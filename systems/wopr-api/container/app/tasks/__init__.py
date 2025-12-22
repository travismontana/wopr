#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
Copyright (c) 2025 Bob Bomar <bob@bomar.us>
SPDX-License-Identifier: MIT

WOPR API application package.
"""

__version__ = "0.1.0"
from .tasks import celery_app  # noqa: F401