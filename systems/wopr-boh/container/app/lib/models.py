""" will handle model things"""
import logging

from lib.helpers import debugit, setup_logger
from lib.wopr_api_client import Client
from lib.wopr_api_client.models.model_ import ModelUpdate
from lib.wopr_api_client.api.models import get_all_items_api_v2_models_get
from lib.wopr_api_client.types import Response


logger = setup_logger()


def activate_model(model):
    """Tell model control to activate the given model"""
    logger.info("Activating model: %s", model.get("name", "Unknown"))
