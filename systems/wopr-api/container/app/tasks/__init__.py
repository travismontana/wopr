# Copyright 2026 Bob Bomar
# Licensed under the Apache License, Version 2.0

import logging
from app import globals as woprvar
from app.logging import configure_logging

configure_logging(woprvar.WOPR_CONFIG["LOG_LEVEL"], woprvar.WOPR_CONFIG["LOG_FILE"])
from .session_tasks import *  # noqa

# Export tasks for discovery
__all__ = [
    'archive_session',
]

