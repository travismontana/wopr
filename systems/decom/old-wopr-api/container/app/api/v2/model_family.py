from app import globals as woprvar
from app.lib.crud import CRUDRouter
from app.logging import configure_logging
from app.models.model_family import (
    ModelFamilyCreate,
    ModelFamilyResponse,
    ModelFamilyUpdate,
)

logger = configure_logging(woprvar.LOGFILE)

# Usage
model_family_router = CRUDRouter(
    table_name="model_family",
    response_model=ModelFamilyResponse,
    create_model=ModelFamilyCreate,
    update_model=ModelFamilyUpdate,
    prefix="",
    tags=["model_family"],
).router


# Custom endpoint
@model_family_router.get("/{model_family_id}/stats")
async def get_model_stats(model_family_id: str):
    # Custom logic
    pass


@model_family_router.get("/health")
async def get_health():
    return "healthy"
