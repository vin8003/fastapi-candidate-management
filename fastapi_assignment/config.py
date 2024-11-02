import os
import re

from dotenv import load_dotenv
from pathlib import Path
from fastapi_mail import ConnectionConfig

# Construct the path to the .env file, one directory up from the current file
env_path = Path(__file__).resolve().parent.parent / ".env"

# Load environment variables from .env file at the start
load_dotenv(dotenv_path=env_path)

# EMAIL config
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "True") == "True"
MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "False") == "True"
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Candidate Management")

MAIL_CONFIG = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
    MAIL_FROM_NAME=MAIL_FROM_NAME,
)

# JWT secret key
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret_key")

# JWT algorithm
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# JWT access token expiration time
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "test_db")
DB_NAME = os.getenv("DB_NAME", "assignment_db")
CELERY_RESULT_COLLECTION = os.getenv("CELERY_RESULT_COLLECTION", "celery_results")

# Redis connection string
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Celery broker URL
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

# Celery result backend URL
CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND", "mongodb://localhost:27017/celery_results"
)

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Sentry
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", "local")
SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", 0.5))
SENTRY_DEBUG = os.getenv("SENTRY_DEBUG", "False") == "True"


# Regular expression patterns for secured paths
SECURE_PATH_PATTERNS = [
    re.compile(r"^/send-report$"),
    re.compile(r"^/all-candidates$"),
    re.compile(r"^/candidate(/[\w-]+)?$"),  # Matches /candidate and /candidate/<id>
    # Add other regex patterns as needed
]
