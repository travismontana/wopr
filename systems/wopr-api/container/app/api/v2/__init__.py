# app/api/v2/__init__.py
import logging
from fastapi import APIRouter
from app import globals as woprvar
from app.logging import configure_logging

router = APIRouter()
logger = logging.getLogger(woprvar.APP_NAME)
