import httpx

import streamlit as st


def get_api_client(base_url: str) -> httpx.Client:
    """
    Create and return an HTTPX client configured for the API.

    Args:
        base_url (str): The base URL of the API.
    Returns:
        httpx.Client: Configured HTTPX client.
    """
    client = httpx.Client(base_url=base_url, timeout=10.0)
    return client

def handle_api_error(error: httpx.HTTPError) -> dict:
    """
    Handle API errors and return a structured error response.

    Args:
        error (httpx.HTTPError): The HTTP error encountered.
    Returns:
        dict: Structured error response.
    """
    return {
        "error": True,
        "message": str(error),
        "status_code": error.response.status_code if error.response else None,
    }

def parse_api_response(response: httpx.Response) -> dict:
    """
    Parse the API response and return the JSON content.

    Args:
        response (httpx.Response): The HTTP response from the API.
    Returns:
        dict: Parsed JSON content from the response.
    """
    try:
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        return handle_api_error(e)

def build_api_url(endpoint: str, base_url: str) -> str:
    """
    Build the full API URL for a given endpoint.

    Args:
        endpoint (str): The API endpoint.
        base_url (str): The base URL of the API.
    Returns:
        str: Full API URL.
    """
    return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

def api_get_models() -> dict:
    """
    Fetch the list of ML models from the API.

    Args:
        client (httpx.Client): The HTTPX client configured for the API.
    Returns:
        dict: API response containing the list of models.
    """
    client = get_api_client(st.session_state["api_host"])
    try:
        response = client.get("/api/v3/ml_models")
        return parse_api_response(response)
    except httpx.HTTPError as e:
        return handle_api_error(e)


def api_get_model_families() -> dict:
    """
    Fetch the list of ML model families from the API.

    Args:
        client (httpx.Client): The HTTPX client configured for the API.
    Returns:
        dict: API response containing the list of model families.
    """
    client = get_api_client(st.session_state["api_host"])
    try:
        response = client.get("/api/v3/ml_model_families")
        return parse_api_response(response)
    except httpx.HTTPError as e:
        return handle_api_error(e)


def api_get_model_by_id(model_id: str) -> dict:
    """
    Fetch a specific ML model by its ID from the API.

    Args:
        model_id (str): The ID of the ML model to fetch.
    Returns:
        dict: API response containing the model details.
    """
    client = get_api_client(st.session_state["api_host"])
    try:
        response = client.get(f"/api/v3/ml_models/{model_id}")
        return parse_api_response(response)
    except httpx.HTTPError as e:
        return handle_api_error(e)


def api_create_model(model_data: dict) -> dict:
    """
    Create a new ML model via the API.

    Args:
        model_data (dict): The data for the new ML model.
    Returns:
        dict: API response containing the created model details.
    """
    client = get_api_client(st.session_state["api_host"])
    try:
        response = client.post("/api/v3/ml_models", json=model_data)
        return parse_api_response(response)
    except httpx.HTTPError as e:
        return handle_api_error(e)


def api_update_model(model_id: str, model_data: dict) -> dict:
    """
    Update an existing ML model via the API.

    Args:
        model_id (str): The ID of the ML model to update.
        model_data (dict): The updated data for the ML model.
    Returns:
        dict: API response containing the updated model details.
    """
    client = get_api_client(st.session_state["api_host"])
    try:
        response = client.patch(f"/api/v3/ml_models/{model_id}", json=model_data)
        return parse_api_response(response)
    except httpx.HTTPError as e:
        return handle_api_error(e)


def api_delete_model(model_id: str) -> dict:
    """
    Delete an existing ML model via the API.

    Args:
        model_id (str): The ID of the ML model to delete.
    Returns:
        dict: API response confirming deletion.
    """
    client = get_api_client(st.session_state["api_host"])
    try:
        response = client.delete(f"/api/v3/ml_models/{model_id}")
        return parse_api_response(response)
    except httpx.HTTPError as e:
        return handle_api_error(e)


def api_get_model_family_by_id(family_id: str) -> dict:
    """
    Fetch a specific ML model family by its ID from the API.

    Args:
        family_id (str): The ID of the ML model family to fetch.
    Returns:
        dict: API response containing the model family details.
    """
    client = get_api_client(st.session_state["api_host"])
    try:
        response = client.get(f"/api/v3/ml_model_families/{family_id}")
    except httpx.HTTPError as e:
        return handle_api_error(e)
    return parse_api_response(response)


def api_activate_model(model_id: int) -> dict:
    """
    Fetch the list of ML model families from the API.

    Args:
        client (httpx.Client): The HTTPX client configured for the API.
    Returns:
        dict: API response containing the list of model families.
    """
    client = get_api_client(st.session_state["api_host"])
    try:
        response = client.get(f"/api/v3/ml_models/activate/{model_id}")
        return parse_api_response(response)
    except httpx.HTTPError as e:
        return handle_api_error(e)


def api_new_game_session() -> dict:
    """
    Create a new game session via the API.

    Args:
        note (str): The note for the new game session.
    Returns:
        dict: API response containing the created game session details.
    """
    client = get_api_client(st.session_state["api_host"])
    try:
        response = client.post("/api/v3/game_sessions", json={})
        return parse_api_response(response)
    except httpx.HTTPError as e:
        return handle_api_error(e)


def api_capture_move(filename: str) -> dict:
    """
    Capture a player's move in a game session via the API.

    Args:
        session_id (str): The ID of the game session.
        player_name (str): The name of the player making the move.
        move (str): The move made by the player.
    Returns:
        dict: API response confirming the captured move.
    """
    client = get_api_client(st.session_state["api_host"])
    try:
        response = client.post(
            f"/api/v3/capture",
            json={"filename": filename},
        )
        return parse_api_response(response)
    except httpx.HTTPError as e:
        return handle_api_error(e)
