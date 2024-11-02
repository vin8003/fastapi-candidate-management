from fastapi import APIRouter, Request
from fastapi_assignment.tasks import generate_and_send_report_task

router = APIRouter()


@router.get("/send-report")
async def send_report(request: Request):
    # Retrieve the email from the request state set by the JWT middleware
    email = request.state.email
    generate_and_send_report_task.delay(email)
    return {"message": "Report will be sent to your email once it is generated"}
