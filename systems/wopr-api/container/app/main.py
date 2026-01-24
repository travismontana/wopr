from lib.helpers import setup_logging
from lib import globals as worpvar
from fastapi import FastAPI

# Route imports
from routers import config as config_router
from routers import ml_models as ml_model_router
from routers import ml_model_families as ml_model_family_router


logger = setup_logging("wopr-api", "INFO", "/tmp/wopr-api.log")

config = worpvar.WOPR_CONFIG

api = FastAPI(
    title=worpvar.API_TITLE,
    description=worpvar.API_DESCRIPTION,
    version=worpvar.APP_VERSION,
)

API_PREFIX = "/api/v3"

# Include routers
api.include_router(config_router.router, prefix=f"{API_PREFIX}/config", tags=["config"])
api.include_router(
    ml_model_router.router, prefix=f"{API_PREFIX}/ml_models", tags=["ml_models"]
)
api.include_router(
    ml_model_family_router.router,
    prefix=f"{API_PREFIX}/ml_model_families",
    tags=["ml_model_families"],
)

if config:
    api.state.config = config
else:
    logger.error("No configuration loaded!")


# Standard endpoints
@api.get("/health", tags=["health"])
async def health_check():
    """Health Check

    Returns:
        dict: ok
    """
    return {"status": "ok"}


@api.get("/version", tags=["version"])
async def version_check():
    """_summary_

    Returns:
        _type_: _description_
    """
    return {"version": worpvar.APP_VERSION}


@api.get("/status", tags=["status"])
async def status_check():
    """_summary_

    Returns:
        _type_: _description_
    """
    return {
        "status": "running",
        "version": worpvar.APP_VERSION,
        "config_loaded": config is not None,
        "state": api.state.__dict__,
    }
