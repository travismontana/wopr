from . import router, logger
from fastapi import APIRouter, HTTPException, status
from app import globals as woprvar
import requests

router = APIRouter(tags=["images"])
logger.info("Images API module loaded")


def oneGet(url: str, headers: dict, params: dict) -> list[dict]:
    req_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        **(headers or {}),
    }

    try:
        response = requests.get(url, headers=req_headers, params=params or {})
        response.raise_for_status()

        payload = response.json()

        data = payload.get("data", [])
        if not isinstance(data, list):
            logger.error(f"Directus returned non-list 'data': {type(data)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Directus response 'data' was not a list",
            )
        return data

    except requests.RequestException as e:
        logger.error(f"Error fetching data from Directus: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching data, error: {e}",
        )


@router.get("/gameid/{game_catalog_id}/", response_model=list[dict])
@router.get("/gameid/{game_catalog_id}", response_model=list[dict])
def get_images_by_game_catalog_id(game_catalog_id: int):
    logger.info(f"Fetching images for game catalog ID {game_catalog_id} from the directus api")
    url = f"{woprvar.DIRECTUS_URL}/items/mlimages"
    params = {
        "filter[game_catalog_id][_eq]": game_catalog_id,
    }
    return oneGet(url, woprvar.DIRECTUS_HEADERS, params)


@router.get("/gameid/names/{game_catalog_id}/", response_model=list[dict])
@router.get("/gameid/names/{game_catalog_id}", response_model=list[dict])
def get_images_by_game_catalog_id_names(game_catalog_id: int): 
    logger.info(f"Fetching images for game catalog ID {game_catalog_id} from the directus api")
    url = f"{woprvar.DIRECTUS_URL}/items/mlimages"

    params = {
        "filter[game_catalog_id][_eq]": game_catalog_id,
        "fields": "*,piece_id.id,piece_id.name,piece_id.game_catalog_uuid.id,piece_id.game_catalog_uuid.name",
    }
    return oneGet(url, woprvar.DIRECTUS_HEADERS, params)


@router.get("/pieceid/{piece_id}/", response_model=list[dict])
@router.get("/pieceid/{piece_id}", response_model=list[dict])
def get_images_by_piece_id(piece_id: int):
    logger.info(f"Fetching images for piece ID {piece_id} from the directus api")
    url = f"{woprvar.DIRECTUS_URL}/items/mlimages"
    params = {
        "filter[piece_id][_eq]": piece_id,
    }
    return oneGet(url, woprvar.DIRECTUS_HEADERS, params)


@router.get("/all/", response_model=list[dict])
@router.get("/all", response_model=list[dict])
def get_all_images():
    logger.info("Fetching all images from the directus api")
    url = f"{woprvar.DIRECTUS_URL}/items/mlimages"
    return oneGet(url, woprvar.DIRECTUS_HEADERS, {})
