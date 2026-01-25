import streamlit as st
import pandas as pd
import numpy as np

from lib.helpers import debug_log, debug_json

from lib.api import (
    api_get_models,
    api_get_model_families,
    api_create_model,
    api_update_model,
)

def render_models_editor():
    """
    Render the ML Models Editor display.
    """
    if "models" not in st.session_state:
        models_response = api_get_models()
        if "error" in models_response:
            st.error(f"Error fetching models: {models_response['message']}")
            return {"status": "error", "message": models_response['message']}
        st.session_state["models"] = models_response
        debug_json(models_response)

    if "model_families" not in st.session_state:
        families_response = api_get_model_families()
        if "error" in families_response:
            st.error(f"Error fetching model families: {families_response['message']}")
            return {"status": "error", "message": families_response["message"]}
        st.session_state["model_families"] = families_response
        debug_json(families_response)
    models_data = st.session_state.get("models", [])

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

    models_df = pd.DataFrame(models_data)
    models_df = models_df[DISPLAY_COLUMNS]
    st.session_state["models_df"] = models_df
    # st.dataframe(models_df)

    edited_models_df = st.data_editor(
        models_df,
        num_rows="dynamic",
        width="stretch",
        key="models_data_editor",
        column_config={
            "id": st.column_config.NumberColumn(
                "ID",
                help="Unique identifier for the model",
                disabled=True,
            ),
            "name": st.column_config.TextColumn(
                "Name",
                help="Name of the model",
            ),
            "shortname": st.column_config.TextColumn(
                "Short Name",
                help="Abbreviated name for the model",
            ),
            "version": st.column_config.NumberColumn(
                "Version",
                help="Version of the model",
            ),
            "familyid": st.column_config.SelectboxColumn(
                "Family ID",
                help="Identifier for the model family",
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
            "description": st.column_config.TextColumn(
                "Description",
                help="Detailed description of the model",
            ),
            "note": st.column_config.TextColumn(
                "Note",
                help="Additional notes about the model",
            ),
            "date_updated": st.column_config.DatetimeColumn(
                "Date Updated",
                help="Last updated timestamp",
                disabled=True,
            ),
        },
    )

    if edited_models_df.equals(models_df):
        st.info("No changes made to the models.")
        return {"status": "Models editor rendered"}

    st.session_state["edited_models_df"] = edited_models_df
    debug_log("Models DataFrame edited:")
    debug_json(edited_models_df)

    edited_norm = edited_models_df.replace({np.nan: None})
    original_norm = models_df.replace({np.nan: None})

    debug_log("Normalized Edited DataFrame:")
    debug_json(edited_norm)
    debug_log("Normalized Original DataFrame:")
    debug_json(original_norm)
    changes = []

    new_rows = edited_norm[edited_norm["id"].isna()]
    updated_rows = edited_norm[edited_norm["id"].notna()]

    debug_log("New Rows:")
    debug_json(new_rows)
    debug_log("Updated Rows:")
    debug_json(updated_rows)

    if not new_rows.empty:
        for _, row in new_rows.iterrows():
            model_data = {
                k: v
                for k, v in row.to_dict().items()
                if k not in ("id", "date_updated", "date_created", "model_state")
                and v is not None
            }
            model_data = {k: v for k, v in model_data.items() if pd.notna(v)}

            try:
                changes.append({"action": "create", "data": model_data})
                debug_log("Prepared create action for model:")
                debug_json(model_data)
                results = api_create_model(model_data)
            except Exception as e:
                st.error(f"Error creating model: {e}")
                return {"status": "error", "message": str(e)}
    if not updated_rows.empty:
        for _, row in updated_rows.iterrows():
            model_id = row["id"]
            original_row = original_norm[original_norm["id"] == model_id].iloc[0]
            diff_data = {
                k: v
                for k, v in row.to_dict().items()
                if k not in ("id", "date_updated", "date_created", "model_state")
                and v != original_row[k]
            }
            diff_data = {k: v for k, v in diff_data.items() if pd.notna(v)}

            if diff_data:
                try:
                    changes.append(
                        {"action": "update", "id": model_id, "data": diff_data}
                    )
                    debug_log(f"Prepared update action for model {model_id}:")
                    debug_json(diff_data)
                    results = api_update_model(model_id, diff_data)
                except Exception as e:
                    st.error(f"Error updating model {model_id}: {e}")
                    return {"status": "error", "message": str(e)}
