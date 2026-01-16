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
from fastapi import APIRouter, HTTPException, status
import requests
import logging
from app import globals as woprvar
from opentelemetry import trace
from contextlib import nullcontext
from app.directus_client import get_one, get_all, post, update, delete

logger = logging.getLogger(woprvar.APP_NAME)

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
		session = response.json().get('data', {})
	except requests.RequestException as e:
		logger.error(f"Error creating new session: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating new session, error: {e}")
	return session
	
@router.post("/capture")
async def capture_session(payload: dict):
	logger.info(f"Capturing session data for payload: {payload}")
	camid = payload["camid"]
	filename = payload["filename"]
	sessionuuid = payload["sessionuuid"]
	
	# Use camid from payload instead of hardcoding '0'
	CAMURL = woprvar.WOPR_CONFIG['camera']['camDict'][str(camid)]['host']
	
	camera_payload = {
		"filename": filename
	}
	
	try:
		response = requests.post(f"http://{CAMURL}:5000/capture_ml", json=camera_payload, headers=woprvar.DIRECTUS_HEADERS)
		response.raise_for_status()
		logger.info("Successfully called camera API, response: %s", response.json())
		return response.json()
	except requests.RequestException as e:
		logger.error(f"Error capturing piece image: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error setting filename for piece image, error: {e}")

# GET / - GETS ALL
# POST / - creates a new entry
# UPDATE / - updates entry

@router.get("")
async def get_sessions():
    logger.info("Fetching all sessions")
    return get_all("sessiontracker")

@router.get("/{session_id}")
async def get_session(session_id: str):
    logger.info(f"Fetching session with ID: {session_id}")
    return get_one("sessiontracker", session_id)

@router.post("")
async def create_session(payload: dict):
	logger.info(f"Creating a new session with payload: {payload}")
	return post("sessiontracker", payload)

@router.put("/{session_id}")
async def update_session(session_id: str, payload: dict):
    logger.info(f"Updating session {session_id} with payload: {payload}")
    return update("sessiontracker", session_id, payload)

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    logger.info(f"Deleting session with ID: {session_id}")
    return delete("sessiontracker", session_id)