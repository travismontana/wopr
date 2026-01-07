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

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..db import get_db
from .. import models, schemas, services

router = APIRouter(prefix="/api/v1/games", tags=["games"])


@router.post("", response_model=schemas.GameOut, status_code=201)
def create_game(payload: schemas.GameCreate, db: Session = Depends(get_db)):
    game = services.create_game(
        db,
        game_type=payload.game_type,
        players=[p.model_dump() for p in payload.players],
        metadata=payload.metadata,
    )
    return game


@router.get("/{game_id}", response_model=schemas.GameOut)
def get_game(game_id: uuid.UUID, db: Session = Depends(get_db)):
    game = db.get(models.Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.patch("/{game_id}", response_model=schemas.GameOut)
def patch_game(game_id: uuid.UUID, payload: schemas.GamePatch, db: Session = Depends(get_db)):
    game = db.get(models.Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return services.patch_game(db, game, status=payload.status, metadata=payload.metadata)


@router.get("/{game_id}/state", response_model=schemas.StateOut)
def get_state(game_id: uuid.UUID, db: Session = Depends(get_db)):
    snap = db.get(models.StateSnapshot, game_id)
    if not snap:
        raise HTTPException(status_code=404, detail="State snapshot not found")
    return snap


@router.get("/{game_id}/events", response_model=list[schemas.EventOut])
def list_events(game_id: uuid.UUID, after: uuid.UUID | None = None, limit: int = 200, db: Session = Depends(get_db)):
    q = select(models.Event).where(models.Event.game_id == game_id).order_by(models.Event.ts.asc()).limit(limit)
    if after:
        q = q.where(models.Event.id > after)
    return list(db.execute(q).scalars().all())
