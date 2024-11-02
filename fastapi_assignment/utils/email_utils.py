from fastapi_mail import FastMail, MessageSchema
import fastapi_assignment.config as config

conf = config.MAIL_CONFIG


async def send_verification_email(recipient_email: str, verification_link: str):
    message = MessageSchema(
        subject="Verify Your Email",
        recipients=[recipient_email],
        body="Please click the following link to verify your email: "
        f"<a href='{verification_link}'>{verification_link}</a>",
        subtype="html",
    )
    fm = FastMail(conf)
    await fm.send_message(message)


async def send_report_email(
    recipients: list[str], subject: str, body: str, attachment_path: str
):
    with open(attachment_path, "rb") as _:
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype="html",
            attachments=[attachment_path],
        )
    fm = FastMail(conf)
    await fm.send_message(message)
