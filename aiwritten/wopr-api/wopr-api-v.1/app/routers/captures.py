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

router = APIRouter(prefix="/api/v1", tags=["captures"])


@router.post("/games/{game_id}/captures", response_model=schemas.CaptureCreateResponse, status_code=202)
def create_capture(game_id: uuid.UUID, payload: schemas.CaptureCreate, db: Session = Depends(get_db)):
    game = db.get(models.Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    cap, jobs = services.create_capture_and_enqueue(db, game=game, device_id=payload.device_id)
    return {"capture": cap, "jobs": jobs}


@router.get("/games/{game_id}/captures", response_model=list[schemas.CaptureOut])
def list_captures(game_id: uuid.UUID, db: Session = Depends(get_db)):
    q = select(models.Capture).where(models.Capture.game_id == game_id).order_by(models.Capture.seq.asc())
    return list(db.execute(q).scalars().all())


@router.get("/captures/{capture_id}", response_model=schemas.CaptureOut)
def get_capture(capture_id: uuid.UUID, db: Session = Depends(get_db)):
    cap = db.get(models.Capture, capture_id)
    if not cap:
        raise HTTPException(status_code=404, detail="Capture not found")
    return cap
