
from fastapi import APIRouter, HTTPException, status
from lib.safe_file import *
from lib.helpers import *
logger = setup_logger()
WOPR_API_URL = "https://api.wopr.tailandtraillabs.org/api/v2"

config = get_config()
if len(config) == 0:
    logger.info("Configuration is empty or could not be loaded")

logger.info("Setting up projects router")
router = APIRouter(tags=["projects"])
logger.info("Initialized projects router")

# get projects

def get_all_projects():
    #return get_all("projects")
    return project_cheat

@router.get("/{project_id}")
def get_project_status(project_id: str):

    project_name = projects.get('name')
    project_shortname = projects.get('shortname')

    project_path = base_storage_path / project_shortname

    

