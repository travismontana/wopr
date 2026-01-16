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
from app.directus_client import get_one, get_all, post, update, delete

logger = logging.getLogger(woprvar.APP_NAME)

router = APIRouter(tags=["plays"])

class PlayPayload(BaseModel):
	playerid: int
	gameid: int
	playid: int
	note: str
	filename: str

# GET / - GETS ALL
# POST / - creates a new entry
# UPDATE / - updates entry

@router.get("")
async def get_plays():
    logger.info("Fetching all plays")
    return get_all("playtracker")

@router.get("/{play_id}")
async def get_play(play_id: str):
    logger.info(f"Fetching play with ID: {play_id}")
    return get_one("playtracker", play_id)

@router.post("")
async def create_play(payload: dict):
	logger.info(f"Creating a new play with payload: {payload}")
	return post("playtracker", payload)

@router.put("/{play_id}")
async def update_play(play_id: str, payload: dict):
    logger.info(f"Updating play {play_id} with payload: {payload}")
    return update("playtracker", play_id, payload)

@router.delete("/{play_id}")
async def delete_play(play_id: str):
    logger.info(f"Deleting play with ID: {play_id}")
    return delete("playtracker", play_id)