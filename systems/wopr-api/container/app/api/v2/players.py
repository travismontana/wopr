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
WOPR Vision Service - Label Studio API Integration
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import httpx
import os
import logging
import sys
from opentelemetry import trace
from contextlib import nullcontext
from typing import Optional, List, Dict, Any
from app.directus_client import get_one, get_all, post, update, delete


logger = logging.getLogger(__name__)
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

router = APIRouter(tags=["players"])

class PlayerPayload(BaseModel):
	name: str
	isbot: Optional[bool] = False

# /players - GET / - get list of all players, human and rivals
# /players - POST - add a player (1 per call)
# /players/human - GET / - get list of all isbot != true players
# /players/human - POST - add a player (1 per call) (will force isbot == false)
# /players/bot - GET / - get list of all isbot == true
# /players/bot - POST - add a player (1 per call) (will force isbot == true)

try:
		from app import globals as woprvar
		tracer = trace.get_tracer(woprvar.APP_NAME, woprvar.APP_VERSION)
except Exception:
		tracer = None

@router.get("")
async def get_players():
    logger.info("Fetching all players")
    return get_all("players")	

@router.get("/human")
@router.get("/human/")
@router.get("/humans")
@router.get("/humans/")
async def get_humans():
	url = f"{woprvar.DIRECTUS_URL}/items/players?filter[isbot][_eq]=false"
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

@router.get("/bot")
@router.get("/bot/")
@router.get("/bots")
@router.get("/bots/")
async def get_bots():
	url = f"{woprvar.DIRECTUS_URL}/items/players?filter[isbot][_eq]=true"
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

# --------------------
# Posts
#

async def doesplayerexist(name: str) -> list:
	url = f"{woprvar.DIRECTUS_URL}/items/players?filter[name][_eq]={name}"
	try:
		async with httpx.AsyncClient(timeout=10.0) as client:
			response = await client.get(
			url,
			headers=woprvar.DIRECTUS_HEADERS
		)
		response.raise_for_status()
		data = response.json()
		players = data.get('data', [])
		logger.info(f"Retrieved {len(players)} players")
		return players
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
async def create_players(payload: PlayerPayload):
	logger.info(f"Creating a new player with payload: {payload}")
	return post("players", payload)

@router.post("/human")
@router.post("/human/")
@router.post("/humans")
@router.post("/humans/")
async def post_humans(payload: PlayerPayload):
	url = f"{woprvar.DIRECTUS_URL}/items/players"
	logger.info(f"Received POST request to /players: {payload}")
	name = payload.name
	existplayerinfo = await doesplayerexist(name)
	if len(existplayerinfo) == 0:
		try:
			payload.isbot = False
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
	else:
		logger.info(f"Player with name {name} already exists")
		return existplayerinfo[0]

@router.post("/bot")
@router.post("/bot/")
@router.post("/bots")
@router.post("/bot/")
async def post_bots(payload: PlayerPayload):
	url = f"{woprvar.DIRECTUS_URL}/items/players"
	logger.info(f"Received POST request to /players: {payload}")
	name = payload.name
	existplayerinfo = await doesplayerexist(name)
	if len(existplayerinfo) == 0:
		try:
			payload.isbot = True
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
	else:
		logger.info(f"Player with name {name} already exists")
		return existplayerinfo[0]


@router.patch("/{player_id}")
async def update_player(player_id: str, payload: dict):
    logger.info(f"Updating player {player_id} with payload: {payload}")
    return update("players", player_id, payload)

@router.delete("/{player_id}")
async def delete_player(player_id: str):
    logger.info(f"Deleting player with ID: {player_id}")
    return delete("players", player_id)

@router.get("/{player_id}")
async def get_player(player_id: str):
    logger.info(f"Fetching player with ID: {player_id}")
    return get_one("players", player_id)