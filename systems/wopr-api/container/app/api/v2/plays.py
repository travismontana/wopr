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
WOPR Plays Service
"""
from fastapi import APIRouter, HTTPException, status
import logging
import httpx
from pydantic import BaseModel
from app import globals as woprvar

logger = logging.getLogger(woprvar.APP_NAME)

router = APIRouter(tags=["plays"])

class PlayPayload(BaseModel):
	playerid: int
	gameid: int
	sessionid: int
	note: str
	filename: str

@router.get("/{game_id}")
@router.get("/{game_id}/")
async def get_play(game_id: int):
	logger.info(f"Getting plays for game_id: {game_id}")
	
	url = f"{woprvar.DIRECTUS_URL}/items/playtracker?filter[gameid][_eq]={game_id}"
	try:
		async with httpx.AsyncClient(timeout=10.0) as client:
			response = await client.get(
				url,
				headers=woprvar.DIRECTUS_HEADERS
			)
		response.raise_for_status()
		data = response.json()
		logger.info(f"Retrieved {data}")
		return data
	except httpx.HTTPStatusError as e:
		logger.error(f"Directus API error: {e.response.status_code} - {e.response.text}")
		raise HTTPException(
			status_code=e.response.status_code,
			detail=f"Directus API error: {e.response.text}"
		)
	except httpx.HTTPError as e:
		logger.error(f"Failed to reach Directus: {str(e)}")
		raise HTTPException(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			detail=f"Failed to communicate with Directus: {str(e)}"
		)

@router.post("")
@router.post("/")
async def post_play(payload: PlayPayload):
	url = f"{woprvar.DIRECTUS_URL}/items/playtracker"
	logger.info(f"Received POST request to /playtracker: {payload}")
	
	try:
		async with httpx.AsyncClient(timeout=10.0) as client:
			response = await client.post(
				url,
				headers=woprvar.DIRECTUS_HEADERS,
				json=payload.model_dump()
			)
		response.raise_for_status()
		data = response.json()
		logger.info(f"Created {data}")
		return data
	except httpx.HTTPStatusError as e:
		logger.error(f"Directus API error: {e.response.status_code} - {e.response.text}")
		raise HTTPException(
			status_code=e.response.status_code,
			detail=f"Directus API error: {e.response.text}"
		)
	except httpx.HTTPError as e:
		logger.error(f"Failed to reach Directus: {str(e)}")
		raise HTTPException(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			detail=f"Failed to communicate with Directus: {str(e)}"
		)