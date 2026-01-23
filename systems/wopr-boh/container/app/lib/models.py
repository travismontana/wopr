""" will handle model things"""
import logging

from lib.helpers import debugit


def activate_model(model):
    """Tell model control to activate the given model"""
    logger.info("Activating model: %s", model.get("name", "Unknown"))
