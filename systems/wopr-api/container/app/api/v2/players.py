#!/usr/bin/env python3
# Copyright 2026 Bob Bomar
# Licensed under the Apache License, Version 2.0

"""
WOPR Players API - Player management endpoints
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging
import sys
from opentelemetry import trace
from typing import Optional
from app.directus_client import get_one, get_all, post, update, delete

logger = logging.getLogger(__name__)
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

router = APIRouter(tags=["players"])

try:
    from app import globals as woprvar
    tracer = trace.get_tracer(woprvar.APP_NAME, woprvar.APP_VERSION)
except Exception:
    tracer = None


class PlayerPayload(BaseModel):
    name: str
    isbot: Optional[bool] = False


# Helper function
async def doesplayerexist(name: str) -> list:
    """Check if player with given name exists"""
    logger.info(f"Checking if player exists: {name}")
    players = get_all("players", filters={"name": {"_eq": name}})
    return players


# GET endpoints
@router.get("")
async def get_players():
    """Get all players (humans and bots)"""
    logger.info("Fetching all players")
    return get_all("players")


@router.get("/{player_id}")
async def get_player(player_id: str):
    """Get specific player by ID"""
    logger.info(f"Fetching player with ID: {player_id}")
    return get_one("players", player_id)


@router.get("/human")
@router.get("/human/")
@router.get("/humans")
@router.get("/humans/")
async def get_humans():
    """Get all human players (isbot=false)"""
    logger.info("Fetching human players")
    return get_all("players", filters={"isbot": {"_eq": False}})


@router.get("/bot")
@router.get("/bot/")
@router.get("/bots")
@router.get("/bots/")
async def get_bots():
    """Get all bot players (isbot=true)"""
    logger.info("Fetching bot players")
    return get_all("players", filters={"isbot": {"_eq": True}})


# POST endpoints
@router.post("")
@router.post("/")
async def create_players(payload: PlayerPayload):
    """Create a new player"""
    logger.info(f"Creating new player: {payload.name}")
    return post("players", payload.model_dump())


@router.post("/human")
@router.post("/human/")
@router.post("/humans")
@router.post("/humans/")
async def post_humans(payload: PlayerPayload):
    """Create a new human player (forces isbot=false)"""
    logger.info(f"Creating human player: {payload.name}")
    
    # Check if exists
    existing = await doesplayerexist(payload.name)
    if len(existing) > 0:
        logger.info(f"Player {payload.name} already exists")
        return existing[0]
    
    # Force isbot=False and create
    payload.isbot = False
    return post("players", payload.model_dump())


@router.post("/bot")
@router.post("/bot/")
@router.post("/bots")
@router.post("/bots/")
async def post_bots(payload: PlayerPayload):
    """Create a new bot player (forces isbot=true)"""
    logger.info(f"Creating bot player: {payload.name}")
    
    # Check if exists
    existing = await doesplayerexist(payload.name)
    if len(existing) > 0:
        logger.info(f"Player {payload.name} already exists")
        return existing[0]
    
    # Force isbot=True and create
    payload.isbot = True
    return post("players", payload.model_dump())


# PATCH/DELETE endpoints
@router.patch("/{player_id}")
async def update_player(player_id: str, payload: dict):
    """Update existing player"""
    logger.info(f"Updating player {player_id}")
    return update("players", player_id, payload)


@router.delete("/{player_id}")
async def delete_player(player_id: str):
    """Delete player"""
    logger.info(f"Deleting player {player_id}")
    return delete("players", player_id)