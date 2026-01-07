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
from sqlalchemy.orm import Session

from .celery_app import celery
from ..db import SessionLocal
from .. import models, repository
from ..sse import hub, SSEMessage


def enqueue_vision_chain(*, vision_job_id: uuid.UUID, validate_job_id: uuid.UUID) -> None:
    from .validate import validate_task
    celery.chain(
        vision_task.s(str(vision_job_id)),
        validate_task.s(str(validate_job_id)),
    ).apply_async()


@celery.task(name="wopr.vision")
def vision_task(vision_job_id: str):
    job_id = uuid.UUID(vision_job_id)

    db: Session = SessionLocal()
    try:
        job = db.get(models.Job, job_id)
        if not job:
            return

        if job.cancel_requested:
            job.status = models.JobStatus.CANCELED
            job.finished_at = datetime.utcnow()
            db.commit()
            return

        job.status = models.JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        job.attempt += 1
        db.commit()

        # TODO: call wopr-cam + wopr-vision for real
        result = {
            "detected_pieces": [],
            "board_delta": {"changed": True},
            "notes": "stubbed vision result",
        }

        job.result_json = result
        job.status = models.JobStatus.SUCCEEDED
        job.finished_at = datetime.utcnow()

        repository.append_event(
            db,
            game_id=job.game_id,
            capture_id=job.capture_id,
            type="VISION_COMPLETE",
            payload={"job_id": str(job.id), "summary": {"pieces": 0}},
        )

        db.commit()

        try:
            import asyncio
            asyncio.run(hub.publish(job.game_id, SSEMessage(event="job", data={"job_id": str(job.id), "status": job.status.value, "type": job.type.value})))
        except RuntimeError:
            pass

    except Exception as e:
        job = db.get(models.Job, job_id)
        if job:
            job.status = models.JobStatus.FAILED
            job.error = str(e)
            job.finished_at = datetime.utcnow()
            repository.append_event(db, game_id=job.game_id, capture_id=job.capture_id, type="VISION_FAILED", payload={"job_id": str(job.id), "error": str(e)})
            db.commit()
        raise
    finally:
        db.close()
