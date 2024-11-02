from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    summary="Health Check",
    description="Check the health status of the API. Returns a simple JSON "
    "object indicating if the API is running.",
)
async def health_check():
    return {"status": "healthy"}
