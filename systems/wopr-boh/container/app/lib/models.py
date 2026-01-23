""" will handle model things"""
import logging
import streamlit as st
from lib.helpers import logit, do_api_things

def activate_model(model):
    """Tell model control to activate the given model"""
    logit(f"Activating model: {model.get('name', 'Unknown')}", "info")
    payload = {"model_id": model["id"]}
    action = "post"
    base_url = "https://api.wopr.tailandtraillabs.org"
    route = "/api/v2/models"
    path = "activate"
    logit(
        "Calling do_api_things with action={action}, base_url={base_url}, route={route}, path={path}, payload={payload}",
        "",
    )
    try:
        results = do_api_things(action, base_url, route, path, payload)
        logit(f"do_api_things returned: {results}", "info")
        return "Activated"
    except Exception as e:
        return f"Unable to activate: {e}, sent: {payload}"
