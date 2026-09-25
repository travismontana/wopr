from app import globals as woprvar
from app.lib.crud import CRUDRouter
from app.lib.helpers import do_api_things
from app.logging import configure_logging
from app.models.models import ModelCreate, ModelResponse, ModelUpdate
from fastapi import Request

logger = configure_logging(woprvar.LOGFILE)

# Usage
models_router = CRUDRouter(
    table_name="models",
    response_model=ModelResponse,
    create_model=ModelCreate,
    update_model=ModelUpdate,
    prefix="",
    tags=["models"],
).router


# Custom endpoint
@models_router.get("/{model_id}/stats")
async def get_model_stats(model_id: str):
    """Get statistics for a specific model"""
    # Custom logic


@models_router.get("/health")
async def get_health():
    """Return healthy"""
    return "healthy"


@models_router.post("/status")
async def update_model_status(data: dict, request=Request):
    """Update the status of a model"""
    logger.info("Updating model status")
    logger.debug(f"Update data: {data}")
    model_id = data.get("model")
    models_url = woprvar.WOPR_CONFIG["api"]["models_url"]
    mod_id = model_id
    action = "post"
    base_url = models_url
    route = "/api/v2/models"
    path = "model_status"
    payload = {"model_id": mod_id}
    results = do_api_things(action, base_url, route, path, payload)
    return results


@models_router.post("/activate")
async def activate_model(model_id: dict, request=Request):
    """Activate a model"""
    logger.info("Activating model")
    logger.debug(f"Activation data: {model_id}")
    models_url = woprvar.WOPR_CONFIG["api"]["models_url"]
    mod_id = model_id.get("model_id")
    action = "post"
    base_url = models_url
    route = "/api/v2/models"
    path = "activate"
    payload = {"model_id": mod_id}
    results = do_api_things(action, base_url, route, path, payload)
    return results
