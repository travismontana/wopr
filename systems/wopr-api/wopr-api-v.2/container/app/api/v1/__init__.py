#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
Copyright (c) 2025 Bob Bomar <bob@bomar.us>
SPDX-License-Identifier: MIT

API v1 routes.
"""

from app.api.v1 import health, auth, cameras

__all__ = ["health", "auth", "cameras"]
