import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from . import models


def next_capture_seq(db: Session, game_id: uuid.UUID) -> int:
    q = select(func.coalesce(func.max(models.Capture.seq), 0) + 1).where(models.Capture.game_id == game_id)
    return int(db.execute(q).scalar_one())


def get_game(db: Session, game_id: uuid.UUID) -> models.Game | None:
    return db.get(models.Game, game_id)


def get_capture(db: Session, capture_id: uuid.UUID) -> models.Capture | None:
    return db.get(models.Capture, capture_id)


def get_job(db: Session, job_id: uuid.UUID) -> models.Job | None:
    return db.get(models.Job, job_id)


def append_event(
    db: Session,
    *,
    game_id: uuid.UUID,
    capture_id: uuid.UUID | None,
    type: str,
    actor: str = "system",
    payload: dict | None = None,
) -> models.Event:
    ev = models.Event(
        game_id=game_id,
        capture_id=capture_id,
        type=type,
        actor=actor,
        payload_json=payload or {},
    )
    db.add(ev)
    return ev
