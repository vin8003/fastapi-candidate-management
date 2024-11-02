import secrets
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi_assignment.models.candidate import (
    CandidateCreate,
    CandidateInDB,
    CandidateUpdate,
)
from fastapi_assignment.utils.dependencies import get_database
from fastapi_assignment.tasks import send_verification_email_task
from fastapi_assignment import config


class CandidateController:
    def __init__(self, db: AsyncIOMotorClient):
        self.collection = db["candidates"]

    async def get_all_candidates(
        self,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 10,
    ) -> List[CandidateInDB]:
        query = {}
        if search:
            query = {
                "$text": {"$search": search}
            }  # Assumes MongoDB text index is set up

        skip = (page - 1) * size
        cursor = self.collection.find(query).skip(skip).limit(size)
        candidates = await cursor.to_list(size)

        return [
            CandidateInDB(id=str(candidate["_id"]), **candidate)
            for candidate in candidates
        ]

    async def create_candidate(self, candidate: CandidateCreate) -> CandidateInDB:
        # Check if a candidate with the same email already exists
        existing_candidate = await self.collection.find_one({"email": candidate.email})
        if existing_candidate:
            raise HTTPException(
                status_code=400, detail="A candidate with this email already exists."
            )

        # Generate a verification token
        verification_token = secrets.token_urlsafe(32)
        candidate_data = candidate.model_dump()
        candidate_data["is_verified"] = False
        candidate_data["verification_token"] = verification_token

        # Insert the new candidate into the database
        result = await self.collection.insert_one(candidate_data)

        # Generate backend verification link
        backend_url = config.BACKEND_URL
        verification_link = f"{backend_url}/verify-email?token={verification_token}"

        # Offload email-sending to Celery for asynchronous handling
        send_verification_email_task.delay(candidate.email, verification_link)

        return CandidateInDB(id=str(result.inserted_id), **candidate_data)

    async def get_candidate(self, id: str) -> CandidateInDB:
        candidate = await self.collection.find_one({"_id": ObjectId(id)})
        if candidate is None:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return CandidateInDB(id=str(candidate["_id"]), **candidate)

    async def update_candidate(
        self, id: str, candidate_update: CandidateUpdate
    ) -> CandidateInDB:
        update_data = {
            k: v for k, v in candidate_update.model_dump().items() if v is not None
        }
        result = await self.collection.update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Candidate not found")
        candidate = await self.collection.find_one({"_id": ObjectId(id)})
        return CandidateInDB(id=str(candidate["_id"]), **candidate)

    async def delete_candidate(self, id: str) -> dict:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return {"message": "Candidate deleted successfully"}


# Create APIRouter instance
router = APIRouter()


# Dependency to initialize the controller
async def get_controller(
    db: AsyncIOMotorClient = Depends(get_database),
) -> CandidateController:
    return CandidateController(db)


@router.get(
    "/all-candidates",
    response_model=List[CandidateInDB],
    summary="List All Candidates",
    description="Retrieve a paginated list of all candidates in the database, "
    "with optional search functionality across candidate fields. Only "
    "accessible to authenticated users.",
)
async def get_all_candidates(
    search: Optional[str] = Query(None, min_length=3, description="Search term"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    controller: CandidateController = Depends(get_controller),
):
    return await controller.get_all_candidates(search=search, page=page, size=size)


@router.post(
    "/candidate",
    response_model=CandidateInDB,
    summary="Create Candidate",
    description="Create a new candidate profile in the database. Requires "
    "details such as name, email, and experience. Only accessible to "
    "authenticated users.",
)
async def create_candidate(
    candidate: CandidateCreate,
    controller: CandidateController = Depends(get_controller),
):
    return await controller.create_candidate(candidate)


@router.get(
    "/candidate/{id}",
    response_model=CandidateInDB,
    summary="Get Candidate by ID",
    description="Retrieve a candidate's information by their unique ID. Only "
    "accessible to authenticated users.",
)
async def get_candidate(
    id: str, controller: CandidateController = Depends(get_controller)
):
    return await controller.get_candidate(id)


@router.put(
    "/candidate/{id}",
    response_model=CandidateInDB,
    summary="Update Candidate by ID",
    description="Update an existing candidate's information by their ID. Only "
    "specified fields will be updated. Requires authentication.",
)
async def update_candidate(
    id: str,
    candidate_update: CandidateUpdate,
    controller: CandidateController = Depends(get_controller),
):
    return await controller.update_candidate(id, candidate_update)


@router.delete(
    "/candidate/{id}",
    summary="Delete Candidate by ID",
    description="Delete a candidate's profile from the database by their unique "
    "ID. Only accessible to authenticated users.",
)
async def delete_candidate(
    id: str, controller: CandidateController = Depends(get_controller)
):
    return await controller.delete_candidate(id)


@router.get(
    "/verify-email",
    summary="Verify Candidate Email",
    description="Verify a candidate's email address using a token.",
)
async def verify_email(
    token: str, controller: CandidateController = Depends(get_controller)
):
    candidate = await controller.collection.find_one(
        {"verification_token": token, "is_verified": False}
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    # Update the candidate to set them as verified
    await controller.collection.update_one(
        {"_id": candidate["_id"]},
        {"$set": {"is_verified": True, "verification_token": None}},
    )

    return {"message": "Email successfully verified"}
