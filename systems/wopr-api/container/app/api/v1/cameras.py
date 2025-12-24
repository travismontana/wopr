"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob <bob@example.com>
# See git log for detailed authorship

WOPR API - cameras api.

"""

from wopr import config as woprconfig
from wopr import storage as woprstorage
from wopr import logging as woprlogging
from app import globals as woprvar

import logging
logger = woprlogging.setup_logging(woprvar.APP_NAME)

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()

camera_dict = woprvar.HACK_CAMERA_DICT

@router.get("")
async def listall():
    logger.debug("Listing all cameras")
    """Get list of cameras (stub)"""
    return {"cameras": list(camera_dict.values())}

@router.get("/{camera_id}")
async def get_camera(camera_id: str):
    logger.debug(f"Getting camera {camera_id}")
    """Get camera by ID (stub)"""
    camera = list(camera_dict.values())
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with ID {camera_id} not found"
        )
    return {"camera": camera}

@router.post("/capture")
async def capture_image(
    captureType: str,
    game_id: str,
    subject: str,
    subject_name: str,
    sequence: int
):
    logger.debug(f"Capturing image for game {game_id}, subject {subject}, subject_name {subject_name}, sequence {sequence}")
    """Capture image from camera (stub)"""

    if captureType == "ml_capture":
        const camUrl = "http://wopr-cam.hangar.bpfx.org:5000/api/v1/capture_ml";
    else:
        const camUrl = "http://wopr-cam.hangar.bpfx.org/api/v1/capture";

    try {
        const res = await fetch(camUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                game_id: gameId.trim(),
                subject: subject.trim(),
                subject_name: subjectName.trim(),
                sequence: Number(sequence),
                }),
        });

        const raw = (await res.text()).trim();
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${raw}`);

        const httpPath = raw.startsWith("/remote/wopr/")
            ? `/wopr/${raw.slice("/remote/wopr/".length)}`
            : raw;

        setStatus({ type: "ok", message: "Saved", path: httpPath });

        setSequence((s) => s + 1);
        setShowCaptureDialog(false);
        } catch (e: any) {
        setStatus({ type: "error", message: e?.message ?? String(e) });
        } finally {
        setBusy(false);
        }
        return {"game_id": game_id, "subject": subject, "subject_name": subject_name, "sequence": sequence}