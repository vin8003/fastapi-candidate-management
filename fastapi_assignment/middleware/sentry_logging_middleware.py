from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from sentry_sdk import capture_exception
import logging


class SentryLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log the exception to Sentry
            capture_exception(e)
            logging.error(f"Unhandled error: {e}")
            # Return a generic error response
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An internal server error occurred. Our team has "
                    "been notified."
                },
            )
