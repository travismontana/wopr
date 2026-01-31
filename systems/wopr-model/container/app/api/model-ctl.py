from typing import Any
from pathlib import Path
import hashlib
import inspect
import httpx
from fastapi import APIRouter, Request


from lib.helpers import (
    setup_logger,
    update_operations,
    logit,
    check_for_file_in_dir,
    download_file,
    copy_file_to_dist,
    copy_modfam_to_model,
    backup_dist_file,
)

from lib.directus_client import get_one, get_all, post, update
from lib import globals as woprvar

from lib.safe_file import SafeFS

logger = setup_logger()

model_ctl = APIRouter(tags=["models"])

@model_ctl.post(""):
a