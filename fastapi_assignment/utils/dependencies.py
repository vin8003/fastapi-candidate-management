from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorClient

from fastapi_assignment import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")

# Singleton MongoDB client
mongodb_client = AsyncIOMotorClient(config.MONGO_URL)
db = mongodb_client[config.DB_NAME]


# Dependency function to provide the database instance
def get_database():
    return db
