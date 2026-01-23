""" will handle model things"""
import logging
import streamlit as st
from lib.helpers import logit, do_api_things

def activate_model(model):
    """Tell model control to activate the given model"""
    logit("Activating model: %s", model.get("name", "Unknown"))
    payload = model["id"]
    action = "post"
    base_url = "https://api.wopr.tailandtraillabs.org"
    route = "/api/v2/models"
    path = "activate"
    return do_api_things(action, base_url, route, path, payload)
