from fastapi import APIRouter
router = APIRouter(tags=["status"])
@router.get("/health", summary="Health Check", description="Check the health of the WOPR API.")
async def health_check():
    return {"status": "healthy"}