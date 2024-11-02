import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from contextlib import asynccontextmanager
from fastapi_assignment.routers import health, user, candidate, report
from fastapi_assignment.middleware.auth_middleware import JWTAuthenticationMiddleware
from fastapi_assignment import config
from fastapi_assignment.middleware.sentry_logging_middleware import (
    SentryLoggingMiddleware,
)

# Initialize Sentry
sentry_sdk.init(
    dsn=config.SENTRY_DSN,
    traces_sample_rate=config.SENTRY_TRACES_SAMPLE_RATE,
    environment=config.SENTRY_ENVIRONMENT,
    debug=config.SENTRY_DEBUG,
)


# Define lifespan to initialize resources (no need to close MongoDB here)
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # Only yield as we already manage MongoDB client in the dependency
    # MongoDB client close is not needed here, as it’s a singleton


# Create FastAPI app with metadata
app = FastAPI(
    lifespan=lifespan,
    title="Candidate Management API",
    description="API for managing candidates, with error monitoring.",
    version="1.0.0",
    contact={
        "name": "Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)
app.add_middleware(SentryAsgiMiddleware)
app.add_middleware(JWTAuthenticationMiddleware)
app.add_middleware(SentryLoggingMiddleware)

# Register routers
app.include_router(health.router)
app.include_router(user.router)
app.include_router(candidate.router)
app.include_router(report.router)


# Endpoint to test Sentry error capture
@app.get("/trigger-error")
async def trigger_error():
    sentry_sdk.capture_message("Testing Sentry error capture!")
    raise Exception("Test error for Sentry integration")
