from fastapi import APIRouter

from lib import globals as woprvar
from lib.helpers import setup_logging, do_api_things
from lib.directus_client import get_one, get_all, post, update, delete

logger = setup_logging("wopr-api", "INFO", "/tmp/wopr-api.log")

router = APIRouter(
    tags=["game_sessions"],
)

@router.get("", response_model=list)
async def get_game_sessions():
    """Get Game Sessions."""
    logger.info("Fetching Game Sessions")
    return get_all("game_sessions") 

@router.patch("/{session_id}", response_model=dict)
async def update_game_session(session_id: str, payload: dict):
    """Update Game Session."""
    logger.info(f"Updating Game Session {session_id}")
    return update("game_sessions", session_id, payload)

@router.post("", response_model=dict)
async def create_game_session(payload: dict):
    """Create new Game Session."""
    logger.info("Creating new Game Session")
    return post("game_sessions", payload)

@router.delete("/{session_id}", status_code=204)
async def delete_game_session(session_id: str):
    """Delete Game Session."""
    logger.info(f"Deleting Game Session {session_id}")
    return delete("game_sessions", session_id)
