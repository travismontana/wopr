from . import router, logger
from fastapi import APIRouter, HTTPException, status, Response
from pydantic import BaseModel, Field
from app import globals as woprvar
import requests
from app.logging import configure_logging

logger = configure_logging(woprvar.LOGFILE)

router = APIRouter(tags=["stream"])

@router.get("/grab/{camera_id}")
@router.get("/grab/{camera_id}/")
def grab(camera_id: str):
    """
    Grab a stream from a specific camera.
    """
    logger.info(f"Grabbing stream from camera ID {camera_id}")
    CAMURL = woprvar.WOPR_CONFIG['camera']['camDict'][camera_id]['host']
    CAMPORT = woprvar.WOPR_CONFIG['camera']['camDict'][camera_id]['port']
    CAMLCLID = woprvar.WOPR_CONFIG['camera']['camDict'][camera_id]['id']
    URL = f"http://{CAMURL}:{CAMPORT}/grab/{CAMLCLID}"
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        return Response(content=response.content)
    except requests.RequestException as e:
        logger.error(f"Error grabbing stream from WOPR API: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error grabbing stream, error: {e}")
