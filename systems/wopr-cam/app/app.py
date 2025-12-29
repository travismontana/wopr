#!/usr/bin/env python3

"""
WOPR - Wargaming Oversight & Position Recognition
Copyright (c) 2025 Bob Bomar <bob@bomar.us>
SPDX-License-Identifier: MIT

wopr-cam -
Camera service for WOPR. Captures images
via USB webcam and saves to a path.
"""

import cv2
from enum import Enum
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from wopr.config import init_config, get_str, get_int
from wopr.logging import setup_logging
from wopr.storage import imagefilename
from pathlib import Path

# get configs
init_config()

logger = setup_logging("wopr-camera")

app = FastAPI(title="wopr-cam", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Subject(str, Enum):
    setup = "setup"
    capture = "capture"
    move = "move"
    thumbnail = "thumbnail"


class CaptureRequest(BaseModel):
    filename: Optional[str] = Field(None, description="Optional filename override")


@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    # Use 400 for invalid input that passes JSON parsing but fails business rules
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_request",
            "message": str(exc),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception):
    # Avoid leaking stack traces to clients; keep them in logs/otel
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Capture failed due to an internal error.",
        },
    )


@app.post("/capture", response_class=PlainTextResponse)
def capture(req: CaptureRequest):
    # Generate filepath from config (may raise ValueError; handled above)
    if req.filename:
        filepath = "/remote/wopr/ml/incoming/" + Path(req.filename).name
    else:
        filepath = imagefilename(req.game_id, req.subject.value)

    resolution = get_str("camera.default_resolution")
    logger.info(f"Res: {resolution}")
    width = get_int(f"camera.resolutions.{resolution}.width")
    height = get_int(f"camera.resolutions.{resolution}.height")
    logger.info(f"Capturing {width}x{height} to {filepath}")

    # Initialize camera (0 = default camera)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        # This will be turned into a 500 JSON by the generic handler
        raise RuntimeError("Camera device could not be opened")

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))

    # Set resolution (may or may not work depending on camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # Capture
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise RuntimeError("Camera capture failed (no frame read)")

    cv2.imwrite(filepath, frame)

    # Return newline so curl doesn't stick your prompt ("%") on the end
    return f"{filepath}\n"

@app.post("/capture_ml", response_class=PlainTextResponse)
def capture_ml(req: CaptureRequest):
    # Generate filepath from config (may raise ValueError; handled above)
    filename = req.filename if req.filename else "noname.jpg"
    base_path = get_str('storage.base_path')
    ml_subdir = "ml" # get_str('storage.ml_subdir')
    ml_dir = Path(base_path) / ml_subdir / 'incoming'
    filepath = ml_dir / f"{filename}"
    ml_dir.mkdir(parents=True, exist_ok=True)

    resolution = get_str("camera.default_resolution")
    logger.info(f"Res: {resolution}")
    width = get_int(f"camera.resolutions.{resolution}.width")
    height = get_int(f"camera.resolutions.{resolution}.height")
    logger.info(f"Capturing {width}x{height} to {filepath}")

    # Initialize camera (0 = default camera)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        # This will be turned into a 500 JSON by the generic handler
        raise RuntimeError("Camera device could not be opened")

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))

    # Set resolution (may or may not work depending on camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # Capture
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise RuntimeError("Camera capture failed (no frame read)")

    cv2.imwrite(filepath, frame)

    # Return newline so curl doesn't stick your prompt ("%") on the end
    return f'{"filename":"{filepath}"}\n'


@app.get("/status")
def status():
    return {"status": "ready"}


@app.get("/images/{game_id}")
def list_images(game_id: str):
    game_dir = WOPR_ROOT / "games" / game_id

    if not game_dir.exists():
        raise HTTPException(status_code=404, detail="Game not found")

    images = sorted(
        p for p in game_dir.rglob("*.jpg")
        if p.is_file()
    )

    # Convert filesystem paths to HTTP paths served by nginx (/wopr/)
    result = [
        f"/wopr/{p.relative_to(WOPR_ROOT)}"
        for p in images
    ]

    return {
        "game_id": game_id,
        "count": len(result),
        "images": result,
    }
