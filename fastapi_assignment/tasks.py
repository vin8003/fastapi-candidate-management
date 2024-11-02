import csv
import os
import gzip
import shutil
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi_mail import FastMail, MessageSchema
from fastapi_assignment.celery_config import celery
from fastapi_assignment.utils.email_utils import send_report_email
from fastapi_assignment import config


class ReportGeneratorTask:
    def __init__(self, recipient_email: str):
        self.recipient_email = recipient_email
        self.client = AsyncIOMotorClient(config.MONGO_URL)
        self.db = self.client[config.DB_NAME]

    async def generate_report(self):
        timestamp = datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
        report_basename = f"candidate_report_{timestamp}"
        csv_path = f"/tmp/reports/{report_basename}.csv"
        compressed_csv_path = f"/tmp/reports/{report_basename}.csv.gz"
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        with open(csv_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Name", "Email", "Experience", "Is Verified"])

            async for candidate in self.db["candidates"].find(batch_size=1000):
                writer.writerow(
                    [
                        str(candidate["_id"]),
                        candidate.get("name", ""),
                        candidate.get("email", ""),
                        candidate.get("experience", 0),
                        candidate.get("is_verified", False),
                    ]
                )

        with open(csv_path, "rb") as f_in:
            with gzip.open(compressed_csv_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        await self.send_report(compressed_csv_path)
        self.client.close()
        os.remove(csv_path)

    async def send_report(self, compressed_csv_path: str):
        subject = "Your Compressed Candidate Report"
        body = (
            "<p>Hello,</p><p>Attached is your candidate report in "
            "compressed format.</p>"
        )
        await send_report_email(
            [self.recipient_email], subject, body, compressed_csv_path
        )


@celery.task(
    name="generate_and_send_report",
    auto_retry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def generate_and_send_report_task(recipient_email: str):
    task = ReportGeneratorTask(recipient_email)
    asyncio.run(task.generate_report())


class VerificationEmailTask:
    def __init__(self, recipient_email: str, verification_link: str):
        self.recipient_email = recipient_email
        self.verification_link = verification_link
        self.fm = FastMail(config.MAIL_CONFIG)

    async def send_email(self):
        message = MessageSchema(
            subject="Verify Your Email",
            recipients=[self.recipient_email],
            body="Please click the following link to verify your email: "
            f"<a href='{self.verification_link}'>{self.verification_link}</a>",
            subtype="html",
        )

        try:
            await self.fm.send_message(message)
            print(f"Sent verification email to {self.recipient_email}")
        except Exception as e:
            print(f"Failed to send verification email: {e}")


@celery.task(
    name="send_verification_email_task",
    auto_retry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def send_verification_email_task(recipient_email: str, verification_link: str):
    task = VerificationEmailTask(recipient_email, verification_link)
    asyncio.run(task.send_email())
