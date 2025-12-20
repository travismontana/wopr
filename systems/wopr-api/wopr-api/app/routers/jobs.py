import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas, services

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=schemas.JobOut)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = db.get(models.Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/cancel", response_model=schemas.JobOut)
def cancel_job(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = db.get(models.Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return services.request_job_cancel(db, job)
