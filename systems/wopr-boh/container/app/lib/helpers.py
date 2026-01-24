"""
Shared helpers for WOPR Streamlit Back of House.

This module centralizes:
- Debug printing helpers
- Exception capture + display (verbose only when debug is enabled)
- API client factory
- httpx event hooks
"""

from __future__ import annotations

import json
import os
import traceback
from typing import Any, Dict

import streamlit as st

from lib.wopr_api_client import Client


def init_session_defaults() -> None:
    """
    Ensure required Streamlit session_state defaults exist.

    This should be called early by the main page.
    """
    if "debug" not in st.session_state:
        st.session_state["debug"] = False

    if "api_host" not in st.session_state:
        api_host = os.getenv("API_URL", "")
        if not api_host:
            st.error("API_URL environment variable is not set.")
            raise SystemExit(1)
        st.session_state["api_host"] = api_host


def debug_enabled() -> bool:
    """Return True if debug output should be shown."""
    return bool(st.session_state.get("debug", False))


def debugit_message(message: str) -> None:
    """
    Conditionally display a debug message to the Streamlit UI.

    Args:
        message: Message to render when debug is enabled.
    """
    if debug_enabled():
        st.write(message)


def debugit_json(json_data: Any) -> None:
    """
    Conditionally display JSON-like data to the Streamlit UI.

    Args:
        json_data: Any JSON-serializable-ish object to render when debug is enabled.
    """
    if debug_enabled():
        st.json(json_data, expanded=False)


def _safe_serialize(obj: Any) -> str:
    """
    Best-effort serialization for debugging.

    Tries JSON first, falls back to repr.

    Args:
        obj: Any object.

    Returns:
        A safe string representation.
    """
    try:
        return json.dumps(obj, default=str)
    except Exception:
        return repr(obj)


def capture_exception(context: str, exc: BaseException) -> None:
    """
    Surface an exception to the user, with full details only when debug is enabled.

    Args:
        context: What we were doing when the exception occurred.
        exc: The caught exception.
    """
    st.error(f"{context}: {type(exc).__name__}")

    if not debug_enabled():
        return

    st.write("**Exception message:**")
    st.code(str(exc))

    st.write("**Traceback:**")
    st.code(traceback.format_exc())

    # Best-effort structured details (works for many httpx / generated-client patterns)
    extra: Dict[str, Any] = {}
    for attr in ("status_code", "response", "body", "content", "detail", "errors"):
        if hasattr(exc, attr):
            try:
                extra[attr] = getattr(exc, attr)
            except Exception:
                extra[attr] = "<unreadable>"

    resp = getattr(exc, "response", None)
    if resp is not None:
        try:
            extra["response_status_code"] = getattr(resp, "status_code", None)
            extra["response_text"] = getattr(resp, "text", None)
            if hasattr(resp, "json"):
                try:
                    extra["response_json"] = resp.json()
                except Exception:
                    pass
        except Exception:
            pass

    if extra:
        st.write("**Exception details (best effort):**")
        debugit_json(extra)


def log_request(request: Any) -> None:
    """
    httpx request hook (debug only).

    Args:
        request: httpx request object from event hook.
    """
    debugit_message(f"Request: {_safe_serialize(request)}")


def log_response(response: Any) -> None:
    """
    httpx response hook (debug only).

    Args:
        response: httpx response object from event hook.
    """
    debugit_message(f"Response: {_safe_serialize(response)}")


def make_client() -> Client:
    """
    Create and configure the WOPR API client.

    Returns:
        Configured `lib.wopr_api_client.Client`.
    """
    return Client(
        base_url=st.session_state["api_host"],
        httpx_args={
            "event_hooks": {"request": [log_request], "response": [log_response]}
        },
        timeout=10.0,
    )


def clear_ui_cache() -> None:
    """
    Clear Streamlit cache and session-cached API payloads.

    Useful when API-side data changed and you want a hard refresh.
    """
    st.cache_data.clear()
    for key in ("models", "model_families", "modelsdf"):
        if key in st.session_state:
            del st.session_state[key]
