#!/usr/bin/env python3
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

"""
WOPR Config Service - Directus API Proxy
"""
from fastapi import APIRouter, HTTPException
import httpx
import os
import logging
import sys
from opentelemetry import trace
from contextlib import nullcontext

logger = logging.getLogger(__name__)
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

router = APIRouter(tags=["session"])

@router.get("/new/{game_id}")
async def getnewsession(game_id: int):
	logger.info(f"Creating new session for game_id: {game_id}")
	
	# Create the record in directus first, then get the uuid, then return that
	URL = f"{woprvar.DIRECTUS_URL}/items/sessiontracker"
	payload = {
		"gameid": game_id
	}

	try:
		response = requests.post(URL, json=payload, headers=woprvar.DIRECTUS_HEADERS)
		response.raise_for_status()
		logger.info("Successfully created new session, response: %s", response.json())
		sessionuuid = response.json().get('data', {}).get('uuid')
		return {"sessionuuid": sessionuuid}
  except requests.RequestException as e:
		logger.error(f"Error creating new session: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating new session, error: {e}")
