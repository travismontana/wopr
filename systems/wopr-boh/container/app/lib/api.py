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