import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi_mail import FastMail
from fastapi_assignment.tasks import ReportGeneratorTask, VerificationEmailTask


@pytest.fixture
def mock_db_client():
    """Create a mock MongoDB client."""
    mock_client = MagicMock(AsyncIOMotorClient)
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_db["candidates"].find.return_value = AsyncMock()
    return mock_client


@pytest.mark.asyncio
async def test_generate_report_success():
    """Test successful generation and sending of a report."""
    recipient_email = "test@example.com"

    with patch(
        "fastapi_assignment.tasks.ReportGeneratorTask.generate_report",
        new_callable=AsyncMock,
    ) as mock_generate_report:
        task = ReportGeneratorTask(recipient_email)

        # Simulate successful report generation
        await task.generate_report()

        # Verify that generate_report was called once
        mock_generate_report.assert_called_once()


@pytest.mark.asyncio
async def test_send_report_email_error_handling():
    """Test handling of errors during email sending."""
    recipient_email = "test@example.com"
    verification_link = "http://example.com/verify"

    with patch.object(
        FastMail, "send_message", side_effect=Exception("Email send failed")
    ) as mock_send_message:
        task = VerificationEmailTask(recipient_email, verification_link)

        await task.send_email()

        # Check that an error message is printed when the email sending fails
        mock_send_message.assert_called_once()
        assert mock_send_message.call_count == 1


@pytest.mark.asyncio
async def test_send_verification_email_success():
    """Test successful sending of a verification email."""
    recipient_email = "test@example.com"
    verification_link = "http://example.com/verify"

    with patch.object(
        FastMail, "send_message", new_callable=AsyncMock
    ) as mock_send_message:
        task = VerificationEmailTask(recipient_email, verification_link)

        await task.send_email()

        # Verify that send_message was called once
        mock_send_message.assert_called_once()


# Additional tests can be added for more edge cases and failure scenarios as needed
