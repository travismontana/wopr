import logging
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from lib.helpers import *
logger = setup_logger()
WOPR_API_URL = "https://api.wopr.tailandtraillabs.org/api/v2"

config = get_config()
if len(config) == 0:
    logger.info("Configuration is empty or could not be loaded")

# Load the api's
from app.lib import projects

APP_NAME = "wopr-model"
APP_API_VERSION = "v1"

logger.info(f"Starting {APP_NAME} application")

logger.info(f"Setup variables")
logger.info(f"Config: {config}")

try: 
    base_storage_path = config['storage']['base_path'] or "/remote/wopr"
except:
    base_storage_path = "/remote/wopr"

try:
    project_subdir = config['storage']['project_subdir'] or "projects"
except:
    project_subdir = "projects"

projects = get_all_projects()
global_vars = []

global_vars.append({
    "base_storage_path": base_storage_path,
    "project_subdir": project_subdir,
    "projects": projects
}
)

# Allons Ye!
app = FastAPI(title=APP_NAME)

# Load api's
app.include_router(projects.router, prefix=f"/api/{APP_API_VERSION}/projects", tags=["projects"])

# health page
@app.get("/health")
def get_health():
    return "healthy"

@app.get("/nelson")
def nelson():
    return "haha"

@app.get("/status")
def get_status():
    status = []

    status.append({"variables": global_vars})

    return status

# projects (each game)
# datasets (the stuff)
# models
# tasks

