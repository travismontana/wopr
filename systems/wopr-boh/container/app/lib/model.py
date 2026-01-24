"""
WOPR ML Model handling for Back of House.

Contains:
- API interactions (list/create/update)
- DataEditor UI for models
- Change detection and patch/create logic
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import streamlit as st

import httpx,os

from lib.wopr_api_client import Client
from lib.wopr_api_client.models.model_create import ModelCreate
from lib.wopr_api_client.models.model_family_create import ModelFamilyCreate
from lib.wopr_api_client.models.model_update import ModelUpdate
from lib.wopr_api_client.api.models import get_all_items_api_v2_models_get
from lib.wopr_api_client.api.model_family import get_all_items_api_v2_model_family_get
from lib.wopr_api_client.api.models import update_item_api_v2_models_item_id_patch
from lib.wopr_api_client.api.models import create_item_api_v2_models_post
from lib.wopr_api_client.types import Response

from lib.helpers import (
    capture_exception,
    debugit_message,
    debugit_json,
    make_client,
)

UPDATABLE_FIELDS = {
    "name",
    "familyid",
    "description",
    "shortname",
    "note",
    "model_status",
    "version",
    "operations",
    "date_updated",
}


def load_models_into_session() -> None:
    """
    Load models from API into session_state if not already present.
    """
    if "models" in st.session_state:
        debugit_message("Loading models from session state")
        return

    debugit_message("Fetching models from API")
    try:
        with make_client() as c:
            models: Response[ModelCreate] = get_all_items_api_v2_models_get.sync(
                client=c
            )
        st.session_state["models"] = [m.to_dict() for m in models]
        debugit_message(f"Retrieved {len(st.session_state['models'])} models")
    except Exception as exc:
        capture_exception("Failed to load models", exc)
        st.session_state["models"] = []


def load_model_families_into_session() -> None:
    """
    Load model families from API into session_state if not already present.
    """
    if "model_families" in st.session_state:
        debugit_message("Loading model families from session state")
        return

    debugit_message("Fetching model families from API")
    try:
        with make_client() as c:
            model_families: Response[ModelFamilyCreate] = (
                get_all_items_api_v2_model_family_get.sync(client=c)
            )
        st.session_state["model_families"] = [mf.to_dict() for mf in model_families]
        debugit_message(
            f"Retrieved {len(st.session_state['model_families'])} model families"
        )
    except Exception as exc:
        capture_exception("Failed to load model families", exc)
        st.session_state["model_families"] = []


def build_models_df() -> pd.DataFrame:
    """
    Build the models dataframe from session_state.

    Returns:
        DataFrame of models.
    """
    modelsdf = pd.DataFrame(st.session_state.get("models", []))
    st.session_state["modelsdf"] = modelsdf
    return modelsdf


def update_model_info(item_id: int, row_dict: dict) -> Any:
    """
    Update an existing model record in the API.

    Only fields listed in `UPDATABLE_FIELDS` are included.
    Drops None values to avoid unintentionally nulling fields.

    Args:
        item_id: Model ID.
        row_dict: Row dict from the edited dataframe.

    Returns:
        API response object for the updated model.
    """
    payload = {k: row_dict.get(k) for k in UPDATABLE_FIELDS if k in row_dict}
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        model_update = ModelUpdate(**payload)
    except Exception as exc:
        capture_exception("Failed to build ModelUpdate payload", exc)
        raise

    try:
        with make_client() as c:
            return update_item_api_v2_models_item_id_patch.sync(
                client=c,
                item_id=str(item_id),
                body=model_update,
            )
    except Exception as exc:
        capture_exception(f"API update failed for model id={item_id}", exc)
        raise


def create_new_model(row_dict: dict) -> Any:
    """
    Create a new model record in the API.

    Only fields listed in `UPDATABLE_FIELDS` are included.
    Drops None values to avoid writing nulls.

    Args:
        row_dict: Row dict for the new model.

    Returns:
        API response object for the created model.
    """
    payload = {k: row_dict.get(k) for k in UPDATABLE_FIELDS if k in row_dict}
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        model_create = ModelCreate(**payload)
    except Exception as exc:
        capture_exception("Failed to build ModelCreate payload", exc)
        raise

    try:
        with make_client() as c:
            return create_item_api_v2_models_post.sync(
                client=c,
                body=model_create,
            )
    except Exception as exc:
        capture_exception("API create failed for new model", exc)
        raise


def _rows_changed(before: Optional[dict], after: dict) -> bool:
    """
    Determine if a model row has meaningful changes for update.

    Args:
        before: Original row dict (or None if not found).
        after: Edited row dict.

    Returns:
        True if relevant fields differ, else False.
    """
    if before is None:
        return True
    for k in UPDATABLE_FIELDS:
        if k in after and before.get(k) != after.get(k):
            return True
    return False


def render_models_editor() -> dict:
    """
    Render the models editor UI and perform create/update operations.

    Returns:
        Dict with keys:
          - created: list of created payload dicts
          - updated: list of API responses for updates
    """
    if st.button("Reload Models from API"):
        load_models_into_session()
        modelsdf = build_models_df()
        st.toast("Models reloaded from API", icon="🔄")

    if st.button("Refresh page"):
        st.rerun()

    results: Dict[str, List[Any]] = {"created": [], "updated": []}

    load_models_into_session()
    load_model_families_into_session()

    modelsdf = build_models_df()

    DISPLAY_COLUMNS = [
        "id",
        "name",
        "shortname",
        "version",
        "familyid",
        "description",
        "note",
        "date_updated",
    ]

    modelsdf = modelsdf[DISPLAY_COLUMNS]

    edited_modelsdf = st.data_editor(
        modelsdf,
        column_config={
            "id": st.column_config.NumberColumn(disabled=True),
            "name": st.column_config.TextColumn(
                "Name",
                validate=r"^[a-zA-Z0-9_ -]+$",
                max_chars=63,
                required=True,
                help="Name of the model to be created.",
            ),
            "description": st.column_config.TextColumn("Description"),
            "familyid": st.column_config.SelectboxColumn(
                "Model Family",
                required=True,
                options=[f["id"] for f in st.session_state.get("model_families", [])],
                format_func=lambda x: next(
                    (
                        f["name"]
                        for f in st.session_state.get("model_families", [])
                        if f["id"] == x
                    ),
                    "",
                ),
            ),
            "shortname": st.column_config.TextColumn("Short Name"),
            "note": st.column_config.TextColumn("Note"),
        },
        column_order=(
            "id",
            "name",
            "version",
            "description",
            "familyid",
            "shortname",
            "note",
            "date_updated",
            "model_state",
            "model_status",
            "date_created",
        ),
    )

    # No changes
    if edited_modelsdf.equals(modelsdf):
        return results

    debugit_message("Models dataframe has been edited.")

    # Normalize NaNs -> None so we don't do dumb comparisons / payloads
    edited_norm = edited_modelsdf.replace({np.nan: None})
    original_norm = modelsdf.replace({np.nan: None})

    # Split new/existing rows
    if "id" not in edited_norm.columns:
        st.warning("No 'id' column found; cannot determine create vs update.")
        return results

    new_rows = edited_norm[edited_norm["id"].isna()]
    existing_rows = edited_norm[edited_norm["id"].notna()]

    debugit_message(f"New rows: {len(new_rows)}")
    debugit_message(f"Existing rows: {len(existing_rows)}")

    # Create new models
    if not new_rows.empty:
        for _, row in new_rows.iterrows():
            model_data = {
                k: v
                for k, v in row.to_dict().items()
                if k not in ("id", "date_created", "date_updated", "model_state")
            }
            model_data = {k: v for k, v in model_data.items() if v is not None}

            try:
                created = create_new_model(model_data)
                results["created"].append(model_data)
                debugit_json({"created_result": str(created)})
            except Exception:
                # create_new_model already displayed details when debug is enabled
                continue

    # Update existing models (only if changed)
    original_by_id = {
        r.get("id"): r
        for r in original_norm.to_dict(orient="records")
        if r.get("id") is not None
    }

    for row in existing_rows.to_dict(orient="records"):
        item_id = row.get("id")
        if item_id is None:
            continue

        if not _rows_changed(original_by_id.get(item_id), row):
            continue

        try:
            updated = update_model_info(int(item_id), row)
            results["updated"].append(updated)
        except Exception:
            continue

    return results


def force_reload_models() -> None:
    """Hard reload models into session_state."""
    try:
        with make_client() as c:
            models: Response[ModelCreate] = get_all_items_api_v2_models_get.sync(
                client=c
            )
        st.session_state["models"] = [m.to_dict() for m in models]
        
    except Exception as exc:
        capture_exception("Failed to reload models", exc)
        st.session_state["models"] = []
API_BASE = os.environ.get("API_URL", "http://localhost:8000")
API_VERSION = "v2"
def talk_to_model_ctl(action, data):
    """router for talking to model ctl directly"""
    url = st.session_state["api_host"]
    API_VERSION = "v2"
    match action:
        case "status":
            # thing = do_api_things("post", url, "models", "model_status", data)
            return create_new("models/status", data)
        case "download":
            thing = do_api_things("post", url, "models", "download", data)
            return thing
        case _:
            return False


def create_new(noun: str, payload: dict) -> dict:
    url = f"{API_BASE}/api/v2/{noun}"
    response = do_api_things("post", API_BASE, noun, "", payload)
    return response.get("data", {})


def do_api_things(action, base_url, route, path, payload):
    headers = ""
    result = []

    action_map = {
        "get": httpx.get,
        "post": httpx.post,
        "put": httpx.put,
        "patch": httpx.patch,
        "delete": httpx.delete
    }
    
    method = action_map[action.lower()]
    
    timeout = 30.0
    base_url = f"{API_BASE}"
    debugit_message(f"API call: {action.upper()} {base_url}/api/{API_VERSION}/{route}/{path}")
    parts = [base_url, "api", API_VERSION, route, path]
    url = "/".join(str(p).strip('/') for p in parts if p)
    
    # Build request kwargs based on HTTP method
    kwargs = {"timeout": timeout, "headers": headers}
    
    if action.lower() in ["post", "put", "patch"] and payload:
        kwargs["json"] = payload
    elif action.lower() == "get" and payload:
        # If payload exists for GET, treat as query params
        kwargs["params"] = payload
    
    response = method(url, **kwargs)
    response.raise_for_status()
    #for item in response:
    #    result.append(item.json())
    result = response.json()
    
    return result

def get_status_from_external_source(model_id: int) -> str:
    """
    Placeholder for fetching model status from an external source if not in API.

    Args:
        model_id: ID of the model.

    Returns:
        Status string.
    """
    data = {
        "model": model_id,
        "backedup": False,
        "checksum": None,
        "downloaded": False,
        "filename": None
    }

    results = talk_to_model_ctl("status", data)
    return results

def render_model_status() -> None:
    st.subheader("Model Status")

    # Ensure models exist
    load_models_into_session()
    models = st.session_state.get("models", [])

    if not models:
        st.info("No models loaded.")
        return

    status_df = build_model_status_table(models)

    # Debug: proves what you actually have (delete later)
    #st.caption(f"status_df shape={status_df.shape} cols={list(status_df.columns)}")

    st.dataframe(
        status_df,
        hide_index=True,
        width=True,
        column_config={
            "id": st.column_config.NumberColumn("ID"),
            "name": st.column_config.TextColumn("Name"),
            "shortname": st.column_config.TextColumn("Short"),
            "status": st.column_config.TextColumn("Status"),
        },
    )

def build_model_status_table(models: List[dict]) -> pd.DataFrame:
    """
    Build a DataFrame showing model statuses.

    Args:
        models: List of model dicts.

    Returns:
        DataFrame with model status information.
    """
    status_records = []

    for model in models:
        model_id = model.get("id")
        model_name = model.get("name")
        model_shortname = model.get("shortname")

        # Placeholder logic for status retrieval
        status = get_status_from_external_source(model_id)

        status_records.append({
            "id": model_id,
            "name": model_name,
            "shortname": model_shortname,
            "status": status,
        })

    status_df = pd.DataFrame(status_records)
    return status_df
