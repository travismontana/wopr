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
from sqlalchemy.orm import Session

from . import models, repository
from .tasks.vision import enqueue_vision_chain


def create_game(db: Session, game_type: str, players: list[dict], metadata: dict) -> models.Game:
    game = models.Game(game_type=game_type, metadata_json=metadata or {})
    db.add(game)
    db.flush()

    for p in players:
        db.add(models.Player(
            game_id=game.id,
            name=p["name"],
            color=p.get("color"),
            seat=p.get("seat"),
            metadata_json=p.get("metadata") or {},
        ))

    snap = models.StateSnapshot(game_id=game.id, version=0, state_json={})
    db.add(snap)

    repository.append_event(db, game_id=game.id, capture_id=None, type="GAME_CREATED", payload={"game_type": game_type})
    db.commit()
    db.refresh(game)
    return game


def patch_game(db: Session, game: models.Game, *, status: models.GameStatus | None, metadata: dict | None) -> models.Game:
    changed = {}
    if status is not None and status != game.status:
        game.status = status
        changed["status"] = status.value
    if metadata is not None:
        game.metadata_json = metadata
        changed["metadata"] = True

    if changed:
        repository.append_event(db, game_id=game.id, capture_id=None, type="GAME_UPDATED", payload=changed)
        db.commit()
        db.refresh(game)
    return game


def create_capture_and_enqueue(db: Session, *, game: models.Game, device_id: str | None) -> tuple[models.Capture, list[models.Job]]:
    seq = repository.next_capture_seq(db, game.id)

    cap = models.Capture(
        game_id=game.id,
        seq=seq,
        source_device_id=device_id,
        status=models.CaptureStatus.CREATED,
    )
    db.add(cap)
    db.flush()

    vision_job = models.Job(game_id=game.id, capture_id=cap.id, type=models.JobType.VISION)
    validate_job = models.Job(game_id=game.id, capture_id=cap.id, type=models.JobType.VALIDATE)
    db.add_all([vision_job, validate_job])

    repository.append_event(db, game_id=game.id, capture_id=cap.id, type="CAPTURE_CREATED", payload={"seq": seq, "device_id": device_id})

    db.commit()
    db.refresh(cap)
    db.refresh(vision_job)
    db.refresh(validate_job)

    enqueue_vision_chain(vision_job_id=vision_job.id, validate_job_id=validate_job.id)

    return cap, [vision_job, validate_job]


def request_job_cancel(db: Session, job: models.Job) -> models.Job:
    if job.status in {models.JobStatus.SUCCEEDED, models.JobStatus.FAILED, models.JobStatus.CANCELED}:
        return job
    job.cancel_requested = True
    repository.append_event(db, game_id=job.game_id, capture_id=job.capture_id, type="JOB_CANCEL_REQUESTED", payload={"job_id": str(job.id)})
    db.commit()
    db.refresh(job)
    return job
