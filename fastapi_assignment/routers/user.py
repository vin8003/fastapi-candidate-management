from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi_assignment.utils.jwt_utils import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from fastapi_assignment.models.user import UserCreate, Token
from fastapi_assignment.utils.dependencies import get_database

router = APIRouter()


class UserService:
    def __init__(self, db: AsyncIOMotorClient):
        self.collection = db["user"]

    async def register_user(self, user: UserCreate) -> dict:
        # Check if user already exists
        existing_user = await self.collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash password and insert new user
        hashed_password = get_password_hash(user.password)
        user_data = {"email": user.email, "hashed_password": hashed_password}
        result = await self.collection.insert_one(user_data)

        # Create JWT token for the user
        data_for_token = {"id": str(result.inserted_id), "email": user.email}
        access_token = create_access_token(data=data_for_token)
        return {"access_token": access_token, "token_type": "bearer"}

    async def login_user(self, user: UserCreate) -> dict:
        db_user = await self.collection.find_one({"email": user.email})
        if not db_user or not verify_password(
            user.password, db_user["hashed_password"]
        ):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        # Create JWT token for the user
        data_for_token = {"id": str(db_user["_id"]), "email": user.email}
        access_token = create_access_token(data=data_for_token)
        return {"access_token": access_token, "token_type": "bearer"}


# Dependency to initialize the service
async def get_user_service(
    db: AsyncIOMotorClient = Depends(get_database),
) -> UserService:
    return UserService(db)


@router.post(
    "/user/register",
    response_model=Token,
    summary="User Registration",
    description="Register a new user with secure password handling. "
    "This endpoint hashes the password before saving the user details to "
    "the database and returns a JWT token upon successful registration.",
)
async def register_user_endpoint(
    user: UserCreate, user_service: UserService = Depends(get_user_service)
):
    return await user_service.register_user(user)


@router.post(
    "/user/login",
    response_model=Token,
    summary="User Login",
    description="Login for existing users. Validates the provided email and "
    "password, and returns a JWT token if authentication is successful.",
)
async def login_user_endpoint(
    user: UserCreate, user_service: UserService = Depends(get_user_service)
):
    return await user_service.login_user(user)
