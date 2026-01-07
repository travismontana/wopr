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

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    String, DateTime, Enum, Integer, ForeignKey, JSON, Text, Boolean, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.utcnow()


class GameStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"
    ARCHIVED = "ARCHIVED"


class CaptureStatus(str, enum.Enum):
    CREATED = "CREATED"
    STORED = "STORED"
    ANALYZING = "ANALYZING"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"


class JobType(str, enum.Enum):
    VISION = "VISION"
    VALIDATE = "VALIDATE"
    THUMB = "THUMB"
    REPLAY = "REPLAY"


class JobStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class Game(Base):
    __tablename__ = "games"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    game_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[GameStatus] = mapped_column(Enum(GameStatus), nullable=False, default=GameStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    players: Mapped[list["Player"]] = relationship(back_populates="game", cascade="all, delete-orphan")
    captures: Mapped[list["Capture"]] = relationship(back_populates="game", cascade="all, delete-orphan")
    events: Mapped[list["Event"]] = relationship(back_populates="game", cascade="all, delete-orphan")
    snapshot: Mapped["StateSnapshot"] = relationship(back_populates="game", uselist=False, cascade="all, delete-orphan")


class Player(Base):
    __tablename__ = "players"
    __table_args__ = (
        UniqueConstraint("game_id", "seat", name="uq_players_game_seat"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    color: Mapped[str | None] = mapped_column(String(32), nullable=True)
    seat: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    game: Mapped["Game"] = relationship(back_populates="players")


class Capture(Base):
    __tablename__ = "captures"
    __table_args__ = (
        UniqueConstraint("game_id", "seq", name="uq_captures_game_seq"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    source_device_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    image_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumb_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)

    status: Mapped[CaptureStatus] = mapped_column(Enum(CaptureStatus), nullable=False, default=CaptureStatus.CREATED)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    game: Mapped["Game"] = relationship(back_populates="captures")
    jobs: Mapped[list["Job"]] = relationship(back_populates="capture", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    capture_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("captures.id", ondelete="CASCADE"), nullable=True)

    type: Mapped[JobType] = mapped_column(Enum(JobType), nullable=False)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), nullable=False, default=JobStatus.QUEUED)

    queued_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    result_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    cancel_requested: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    capture: Mapped["Capture" | None] = relationship(back_populates="jobs")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    capture_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("captures.id", ondelete="SET NULL"), nullable=True)

    type: Mapped[str] = mapped_column(String(64), nullable=False)
    ts: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    actor: Mapped[str] = mapped_column(String(64), nullable=False, default="system")
    payload_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    game: Mapped["Game"] = relationship(back_populates="events")


class StateSnapshot(Base):
    __tablename__ = "state_snapshots"

    game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    state_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    game: Mapped["Game"] = relationship(back_populates="snapshot")
