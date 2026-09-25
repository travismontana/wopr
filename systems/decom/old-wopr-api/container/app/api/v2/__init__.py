# app/api/v2/__init__.py
import logging

from app import globals as woprvar
from app.logging import configure_logging
from fastapi import APIRouter

router = APIRouter()
logger = logging.getLogger(woprvar.LOGFILE)
