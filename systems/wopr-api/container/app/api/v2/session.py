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
from app.lib.task_helper import (
    queue_task, 
    get_task_status,
    revoke_task,
    wait_for_task,
    get_task_info
)
from app.logging import configure_logging

logger = configure_logging(woprvar.APP_NAME)

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

@router.patch("/{session_id}")
async def update_session(session_id: str, payload: dict):
    logger.info(f"Updating session {session_id} with payload: {payload}")
    return update("sessiontracker", session_id, payload)

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    logger.info(f"Deleting session with ID: {session_id}")
    return delete("sessiontracker", session_id)

# tasks
# /task/{session_id}/archive - archives all images for session
# 
@router.post("/task/{session_id}/archive")
async def archive_session_tasks(session_id: str):
	logger.info(f"Archiving images for session ID: {session_id}")
	try:
		# Simulate archiving process
		results = queue_task("archive_session_images", {"session_id": session_id})
		logger.info(f"Successfully archived images for session ID: {session_id}")
		return {"status": "success", "message": f"Images for session {session_id} archived successfully."}
	except Exception as e:
		logger.error(f"Error archiving images for session {session_id}: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error archiving images for session {session_id}, error: {e}")

@router.get("/task/{task_id}/status")
async def get_session_task_status(task_id: str):
	logger.info(f"Fetching status for task ID: {task_id}")
	try:
		response = get_task_status(task_id)
		logger.info(f"Successfully fetched task status for task ID: {task_id}")
	except Exception as e:
		logger.error(f"Error fetching task status for task ID {task_id}: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching task status for task ID {task_id}, error: {e}")
	return response

@router.post("/task/{task_id}/revoke")
async def revoke_session_task(task_id: str):
	logger.info(f"Revoking task ID: {task_id}")
	try:
		response = revoke_task(task_id, terminate=True)
		logger.info(f"Successfully revoked task ID: {task_id}")
	except Exception as e:
		logger.error(f"Error revoking task ID {task_id}: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error revoking task ID {task_id}, error: {e}")
	return response

@router.post("/task/{task_id}/wait")
async def wait_for_session_task(task_id: str):
	logger.info(f"Waiting for task ID: {task_id} to complete")
	try:
		response = wait_for_task(task_id, timeout=300)  # 5 minute timeout
		logger.info(f"Task ID: {task_id} completed with response: {response}")
	except Exception as e:
		logger.error(f"Error waiting for task ID {task_id}: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error waiting for task ID {task_id}, error: {e}")
	return response

@router.get("/task/{task_id}")
async def get_session_task(task_id: str):
	logger.info(f"Fetching task details for task ID: {task_id}")
	try:
		response = get_task_info(task_id)
		logger.info(f"Successfully fetched task details for task ID: {task_id}")
	except Exception as e:
		logger.error(f"Error fetching task details for task ID {task_id}: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching task details for task ID {task_id}, error: {e}")
	return response

