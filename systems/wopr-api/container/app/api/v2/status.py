from . import router, logger
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app import globals as woprvar
import requests
from app.logging import configure_logging

logger = configure_logging(woprvar.LOGFILE)

router = APIRouter(tags=["status"])


@router.get(dict)
def show_status():
  """Get all pieces for a specific game"""
  logger.info(f"Fetching pieces for game ID {game_id} from the directus api")
  URL = f"{woprvar.DIRECTUS_URL}/items/pieces?filter[game_catalog_uuid][_eq]={game_id}"
  
  try:
    response = requests.get(URL, headers=woprvar.DIRECTUS_HEADERS)
    response.raise_for_status()
    data = response.json()
    return data.get('data', [])
  except requests.RequestException as e:
    logger.error(f"Error fetching pieces from Directus: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching pieces, error: {e}")
