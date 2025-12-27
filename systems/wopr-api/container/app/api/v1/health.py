from fastapi import APIRouter
router = APIRouter(tags=["status"])

@router.get("/", summary="Health Check", description="Check the health of the WOPR API.")
@router.get("", summary="Health Check", description="Check the health of the WOPR API.")
async def health_check() -> dict:
    return {
        "status": "ok",
        "service": "wopr-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }