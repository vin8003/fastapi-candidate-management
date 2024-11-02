from pydantic import BaseModel, Field
from typing import Optional


class CandidateCreate(BaseModel):
    name: str
    email: str
    experience: Optional[int] = Field(default=0, ge=0)
    is_verified: Optional[bool] = False
    verification_token: Optional[str] = None


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    experience: Optional[int] = Field(default=None, ge=0)


class CandidateInDB(CandidateCreate):
    id: str
