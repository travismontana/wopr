#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob <bob@example.com>
# See git log for detailed authorship

WOPR API application package.

"""

# app/api/v1/__init__.py
import logging
from fastapi import APIRouter
from app import globals as woprvar
from app.logging import configure_logging

router = APIRouter()
logger = logging.getLogger(woprvar.APP_NAME)