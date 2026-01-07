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
from datetime import datetime
from pydantic import BaseModel, Field
from .models import GameStatus, CaptureStatus, JobStatus, JobType


class PlayerCreate(BaseModel):
    name: str
    color: str | None = None
    seat: int | None = None
    metadata: dict = Field(default_factory=dict)


class GameCreate(BaseModel):
    game_type: str = Field(min_length=2, max_length=64)
    players: list[PlayerCreate] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class PlayerOut(BaseModel):
    id: uuid.UUID
    name: str
    color: str | None
    seat: int | None
    metadata_json: dict

    class Config:
        from_attributes = True


class GameOut(BaseModel):
    id: uuid.UUID
    game_type: str
    status: GameStatus
    created_at: datetime
    updated_at: datetime
    metadata_json: dict
    players: list[PlayerOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


class GamePatch(BaseModel):
    status: GameStatus | None = None
    metadata: dict | None = None


class CaptureCreate(BaseModel):
    device_id: str | None = None
    mode: str = "overhead"
    idempotency_key: str | None = None


class CaptureOut(BaseModel):
    id: uuid.UUID
    game_id: uuid.UUID
    seq: int
    created_at: datetime
    source_device_id: str | None
    image_path: str | None
    thumb_path: str | None
    sha256: str | None
    status: CaptureStatus
    error: str | None

    class Config:
        from_attributes = True


class JobOut(BaseModel):
    id: uuid.UUID
    game_id: uuid.UUID
    capture_id: uuid.UUID | None
    type: JobType
    status: JobStatus
    queued_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    attempt: int
    error: str | None
    result_json: dict
    cancel_requested: bool

    class Config:
        from_attributes = True


class CaptureCreateResponse(BaseModel):
    capture: CaptureOut
    jobs: list[JobOut]


class EventOut(BaseModel):
    id: uuid.UUID
    game_id: uuid.UUID
    capture_id: uuid.UUID | None
    type: str
    ts: datetime
    actor: str
    payload_json: dict

    class Config:
        from_attributes = True


class StateOut(BaseModel):
    game_id: uuid.UUID
    version: int
    computed_at: datetime
    state_json: dict

    class Config:
        from_attributes = True
