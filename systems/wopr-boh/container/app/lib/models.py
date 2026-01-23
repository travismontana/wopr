""" will handle model things"""
import logging

from lib.helpers import debugit, do_api_things


def activate_model(model):
    """Tell model control to activate the given model"""
    logger.info("Activating model: %s", model.get("name", "Unknown"))
    payload = model["id"]
    return do_api_things(action, base_url, route, path, payload)
