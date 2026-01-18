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
    get_all_tasks,
	get_all_active_tasks
)
from app.logging import configure_logging

logger = configure_logging(woprvar.APP_NAME)

router = APIRouter(tags=["tasks"])

# tasks
# /session/{session_id}/archive - archives all images for session
# 
@router.post("/session/{session_id}/archive")
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

@router.get("/session/{task_id}/status")
async def get_session_task_status(task_id: str):
	logger.info(f"Fetching status for task ID: {task_id}")
	try:
		response = get_task_status(task_id)
		logger.info(f"Successfully fetched task status for task ID: {task_id}")
	except Exception as e:
		logger.error(f"Error fetching task status for task ID {task_id}: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching task status for task ID {task_id}, error: {e}")
	return response

@router.post("/session/{task_id}/revoke")
async def revoke_session_task(task_id: str):
	logger.info(f"Revoking task ID: {task_id}")
	try:
		response = revoke_task(task_id, terminate=True)
		logger.info(f"Successfully revoked task ID: {task_id}")
	except Exception as e:
		logger.error(f"Error revoking task ID {task_id}: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error revoking task ID {task_id}, error: {e}")
	return response

@router.post("/session/{task_id}/wait")
async def wait_for_session_task(task_id: str):
	logger.info(f"Waiting for task ID: {task_id} to complete")
	try:
		response = wait_for_task(task_id, timeout=300)  # 5 minute timeout
		logger.info(f"Task ID: {task_id} completed with response: {response}")
	except Exception as e:
		logger.error(f"Error waiting for task ID {task_id}: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error waiting for task ID {task_id}, error: {e}")
	return response

@router.get("/session/{task_id}")
async def get_session_task(task_id: str):
	logger.info(f"Fetching task details for task ID: {task_id}")
	try:
		response = get_task_info(task_id)
		logger.info(f"Successfully fetched task details for task ID: {task_id}")
	except Exception as e:
		logger.error(f"Error fetching task details for task ID {task_id}: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching task details for task ID {task_id}, error: {e}")
	return response

@router.get("/session")
async def get_all_session_tasks():
	logger.info("Fetching all active session tasks")
	return get_all_active_tasks()
