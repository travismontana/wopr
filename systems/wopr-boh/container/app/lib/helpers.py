import logging
import httpx

import streamlit as st

logger = logging.getLogger(__name__)

DEBUG=st.session_state["debug"]

def debugit(message,data):
    """Display debug information if debug set"""
    if DEBUG:
        st.write(f"Message: {message}")
        st.write(data)


def logit(info_message, debug_message):
    logger.info(f"{info_message}")
    logger.debug(f"{debug_message}")


def do_api_things(action, base_url, route, path, payload):
    headers = ""
    result = []
    logger.info(
        f"Doing API things - "
        f"Action: {action}, "
        f"Base URL: {base_url}, "
        f"Route: {route}, "
        f"Path: {path}, "
        f"Headers: {headers}, "
        f"Payload: {payload}"
    )

    action_map = {
        "get": httpx.get,
        "post": httpx.post,
        "put": httpx.put,
        "patch": httpx.patch,
        "delete": httpx.delete,
    }

    method = action_map[action.lower()]
    logger.info(f"Using HTTP method: {method.__name__}")

    timeout = 30.0
    parts = [base_url, route, path]
    url = "/".join(str(p).strip("/") for p in parts if p)
    logger.info(f"Constructed URL: {url}")

    # Build request kwargs based on HTTP method
    kwargs = {"timeout": timeout, "headers": headers}

    if action.lower() in ["post", "put", "patch"] and payload:
        kwargs["json"] = payload
    elif action.lower() == "get" and payload:
        # If payload exists for GET, treat as query params
        kwargs["params"] = payload

    response = method(url, **kwargs)
    response.raise_for_status()
    # for item in response:
    #    result.append(item.json())
    result = response.json()
    logger.info(f"Response status code: {response}")
    logger.info(f"Response result: {result}")
    logger.debug(response.text)

    return result
