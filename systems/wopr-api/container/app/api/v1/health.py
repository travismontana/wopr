# Copyright 2026 Bob Bomar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import sys
from datetime import datetime, timezone
from app import globals as woprvar
logger = logging.getLogger(woprvar.APP_NAME)
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

from fastapi import APIRouter
router = APIRouter(tags=["status"])

@router.get("/", summary="Health Check", description="Check the health of the WOPR API.")
@router.get("", summary="Health Check", description="Check the health of the WOPR API.")
async def health_check() -> dict:
    logger.debug("Performing health check at %s", datetime.now(timezone.utc).isoformat())
    return {
        "status": "ok",
        "service": "wopr-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }