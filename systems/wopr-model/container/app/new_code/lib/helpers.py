"""
WOPR Frontend Helpers
Utility functions for Streamlit UI interactions with WOPR API.
Migrated to use wopr_api_client library.
"""

import logging
import sys
from typing import Any

from wopr_api_client import Client
from wopr_api_client.api.models import (
    get_all_items_api_v2_models_get,
    get_item_api_v2_models_item_id_get,
    create_item_api_v2_models_post,
    update_item_api_v2_models_item_id_patch,
    delete_item_api_v2_models_item_id_delete,
)
from wopr_api_client.api.model_family import (
    get_all_items_api_v2_model_family_get,
    get_item_api_v2_model_family_item_id_get,
    create_item_api_v2_model_family_post,
    update_item_api_v2_model_family_item_id_patch,
    delete_item_api_v2_model_family_item_id_delete,
)
from wopr_api_client.api.games import (
    get_games_api_v2_games_get,
    get_game_api_v2_games_game_id_get,
    create_game_api_v2_games_post,
    update_game_api_v2_games_game_id_patch,
    delete_game_api_v2_games_game_id_delete,
)
from wopr_api_client.api.session import (
    get_sessions_api_v2_sessions_get,
    get_session_api_v2_sessions_session_id_get,
    create_session_api_v2_sessions_post,
    update_session_api_v2_sessions_session_id_patch,
    delete_session_api_v2_sessions_session_id_delete,
)
from wopr_api_client.api.plays import (
    get_plays_api_v2_plays_get,
    get_play_api_v2_plays_play_id_get,
    create_play_api_v2_plays_post,
    update_play_api_v2_plays_play_id_patch,
    delete_play_api_v2_plays_play_id_delete,
)
from wopr_api_client.api.pieces import (
    get_pieces_api_v2_pieces_get,
    get_piece_api_v2_pieces_piece_id_get,
    create_piece_api_v2_pieces_post,
    update_piece_api_v2_pieces_piece_id_patch,
    delete_piece_api_v2_pieces_piece_id_delete,
)
from wopr_api_client.api.players import (
    get_players_api_v2_players_get,
    get_player_api_v2_players_player_id_get,
    create_players_api_v2_players_post,
    update_player_api_v2_players_player_id_patch,
    delete_player_api_v2_players_player_id_delete,
)
from wopr_api_client.api.config import get_all_api_v2_config_all_get

API_BASE = "https://api.wopr.tailandtraillabs.org"
client = Client(base_url=API_BASE)


# Flavor text for play submissions
PLAYPHRASES = [
    "My move is made",
    "The feud continues",
    "The next blow is struck",
    "I was friend of Jamis",
    "Fear is the mind killer",
    "There is no escape",
    "You're worm food",
    "Hasta la vista wormy"
]

LOGGER_NAME = "helpers"

project_cheat = {
    "name": "Dune Imperium Uprising Project",
    "shortname": "duneup",
    "id": 6,
    "uuid": "some-unique-uuid"
}

# ------------------------
# Logging Setup
# ------------------------

def setup_logger() -> logging.Logger:
    """
    Configure logging for helper functions.

    Returns:
        Configured logger instance

    Note:
        Only configures once - subsequent calls return existing logger
    """
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger  # Already configured

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    return logger


log = setup_logger()

# ------------------------
# API Endpoint Mappings
# ------------------------

# Maps noun -> (get_all, get_one, create, update, delete) functions
API_ENDPOINTS = {
    "models": (
        get_all_items_api_v2_models_get,
        get_item_api_v2_models_item_id_get,
        create_item_api_v2_models_post,
        update_item_api_v2_models_item_id_patch,
        delete_item_api_v2_models_item_id_delete,
        "item_id",
    ),
    "model_family": (
        get_all_items_api_v2_model_family_get,
        get_item_api_v2_model_family_item_id_get,
        create_item_api_v2_model_family_post,
        update_item_api_v2_model_family_item_id_patch,
        delete_item_api_v2_model_family_item_id_delete,
        "item_id",
    ),
    "games": (
        get_games_api_v2_games_get,
        get_game_api_v2_games_game_id_get,
        create_game_api_v2_games_post,
        update_game_api_v2_games_game_id_patch,
        delete_game_api_v2_games_game_id_delete,
        "game_id",
    ),
    "sessions": (
        get_sessions_api_v2_sessions_get,
        get_session_api_v2_sessions_session_id_get,
        create_session_api_v2_sessions_post,
        update_session_api_v2_sessions_session_id_patch,
        delete_session_api_v2_sessions_session_id_delete,
        "session_id",
    ),
    "plays": (
        get_plays_api_v2_plays_get,
        get_play_api_v2_plays_play_id_get,
        create_play_api_v2_plays_post,
        update_play_api_v2_plays_play_id_patch,
        delete_play_api_v2_plays_play_id_delete,
        "play_id",
    ),
    "pieces": (
        get_pieces_api_v2_pieces_get,
        get_piece_api_v2_pieces_piece_id_get,
        create_piece_api_v2_pieces_post,
        update_piece_api_v2_pieces_piece_id_patch,
        delete_piece_api_v2_pieces_piece_id_delete,
        "piece_id",
    ),
    "players": (
        get_players_api_v2_players_get,
        get_player_api_v2_players_player_id_get,
        create_players_api_v2_players_post,
        update_player_api_v2_players_player_id_patch,
        delete_player_api_v2_players_player_id_delete,
        "player_id",
    ),
}


def _to_dict(obj: Any) -> Any:
    """Convert response object to dict for backwards compatibility."""
    if obj is None:
        return obj
    if isinstance(obj, list):
        return [_to_dict(item) for item in obj]
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return obj


# ------------------------
# CRUD Operations
# ------------------------

def get_all(noun: str) -> list:
    """
    Fetch all items of a given type from WOPR API.

    Args:
        noun: Resource type (sessions, plays, games, pieces, models, model_family, players)

    Returns:
        List of items, empty list on failure

    Example:
        games = get_all("games")
        sessions = get_all("sessions")
    """
    if noun not in API_ENDPOINTS:
        log.error(f"Unknown resource type: {noun}")
        return []

    get_all_fn = API_ENDPOINTS[noun][0]

    try:
        result = get_all_fn.sync(client=client)
        items = _to_dict(result) or []
        log.info(f"Retrieved {len(items)} items from {noun}")
        return items
    except Exception as e:
        log.error(f"Failed to fetch {noun}: {e}")
        return []


def get_one(noun: str, item_id: str) -> dict:
    """
    Fetch a single item by ID from WOPR API.

    Args:
        noun: Resource type (sessions, plays, games, pieces, models, model_family, players)
        item_id: Unique identifier for the item

    Returns:
        Dict containing item data, empty dict on failure

    Example:
        session = get_one("sessions", "abc-123-def")
    """
    if noun not in API_ENDPOINTS:
        log.error(f"Unknown resource type: {noun}")
        return {}

    get_one_fn = API_ENDPOINTS[noun][1]
    id_param = API_ENDPOINTS[noun][5]

    try:
        result = get_one_fn.sync(client=client, **{id_param: item_id})
        item = _to_dict(result) or {}
        log.info(f"Retrieved item {item_id} from {noun}")
        return item
    except Exception as e:
        log.error(f"Failed to fetch {noun} {item_id}: {e}")
        return {}


def create_new(noun: str, payload: dict) -> dict:
    """
    Create a new item via WOPR API.

    Args:
        noun: Resource type to create
        payload: Dict containing item data

    Returns:
        Created item data, empty dict on failure

    Example:
        new_session = create_new("sessions", {"gameid": 1})
    """
    if noun not in API_ENDPOINTS:
        log.error(f"Unknown resource type: {noun}")
        return {}

    create_fn = API_ENDPOINTS[noun][2]

    try:
        # Use sync_detailed to get the full response
        response = create_fn.sync_detailed(client=client, body=payload)
        if response.parsed:
            item = _to_dict(response.parsed)
            # Handle responses that wrap data in a "data" key
            if isinstance(item, dict) and "data" in item:
                item = item.get("data", {})
            item_id = item.get('id', 'unknown') if isinstance(item, dict) else 'unknown'
            log.info(f"Created new item in {noun} with ID {item_id}")
            return item
        return {}
    except Exception as e:
        log.error(f"Failed to create item in {noun}: {e}")
        return {}


def update_item(noun: str, item_id: str, payload: dict) -> dict:
    """
    Update an existing item via WOPR API.

    Args:
        noun: Resource type
        item_id: ID of item to update
        payload: Dict containing updated fields

    Returns:
        Updated item data, empty dict on failure

    Example:
        updated = update_item("sessions", "abc-123", {"status": "complete"})
    """
    if noun not in API_ENDPOINTS:
        log.error(f"Unknown resource type: {noun}")
        return {}

    update_fn = API_ENDPOINTS[noun][3]
    id_param = API_ENDPOINTS[noun][5]

    try:
        response = update_fn.sync_detailed(client=client, **{id_param: item_id}, body=payload)
        if response.parsed:
            item = _to_dict(response.parsed)
            # Handle responses that wrap data in a "data" key
            if isinstance(item, dict) and "data" in item:
                item = item.get("data", {})
            log.info(f"Updated item {item_id} in {noun}")
            return item
        return {}
    except Exception as e:
        log.error(f"Failed to update {noun} {item_id}: {e}")
        return {}


def delete_item(noun: str, item_id: str) -> bool:
    """
    Delete an item via WOPR API.

    Args:
        noun: Resource type
        item_id: ID of item to delete

    Returns:
        True if successful, False on failure

    Warning:
        Deletion is permanent - no undo available
    """
    if noun not in API_ENDPOINTS:
        log.error(f"Unknown resource type: {noun}")
        return False

    delete_fn = API_ENDPOINTS[noun][4]
    id_param = API_ENDPOINTS[noun][5]

    try:
        delete_fn.sync(client=client, **{id_param: item_id})
        log.info(f"Deleted item {item_id} from {noun}")
        return True
    except Exception as e:
        log.error(f"Failed to delete {noun} {item_id}: {e}")
        return False


def get_config():
    """
    Fetch configuration from WOPR API.

    Returns:
        Configuration dict, or False on failure
    """
    try:
        result = get_all_api_v2_config_all_get.sync(client=client)
        log.info(f"Config item {result}")
        return result
    except Exception as e:
        log.error(f"Failed to get config: {e}")
        return False
