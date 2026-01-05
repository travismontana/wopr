# app/api/v1/__init__.py
import logging
from fastapi import APIRouter
from app import globals as woprvar

router = APIRouter()
logger = logging.getLogger(woprvar.APP_NAME)
