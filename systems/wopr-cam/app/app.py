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

# OTel imports
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.trace.status import Status, StatusCode

from wopr.config import init_config, get_str, get_int, get_bool
from wopr.logging import setup_logging
from wopr.tracing import create_tracer
from wopr.storage import imagefilename
from globals import globals as woprvar
from pathlib import Path

# Initialize config first
init_config()

logger = setup_logging("wopr-camera")

# Initialize tracer using centralized setup
tracer = create_tracer(
    tracer_name="wopr-cam",
    tracer_version="0.1.0",
    tracer_enabled=get_bool("otel.tracing.enabled", True),
    tracer_endpoint=get_str("otel.tracing.endpoint", "http://tempo:4318/v1/traces"),
    service_namespace=get_str("otel.service_namespace", "wopr"),
    deployment_env=get_str("environment", "production"),
)

# Metrics provider setup (keeping this separate as your tracing.py only handles traces)
resource = Resource(attributes={
    SERVICE_NAME: "wopr-cam",
    SERVICE_VERSION: "0.1.0",
})

metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(
        endpoint=get_str("otel.metrics.endpoint", "http://tempo:4318/v1/metrics"),
    )
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__)

# Custom metrics
capture_counter = meter.create_counter(
    "wopr.camera.captures.total",
    description="Total number of camera captures attempted",
    unit="1",
)
capture_duration = meter.create_histogram(
    "wopr.camera.capture.duration",
    description="Camera capture duration in milliseconds",
    unit="ms",
)
capture_errors = meter.create_counter(
    "wopr.camera.errors.total",
    description="Total number of camera capture errors",
    unit="1",
)

app = FastAPI(title="wopr-cam", version="0.1.0")

# Instrument FastAPI automatically (only if tracer is enabled)
if tracer:
    FastAPIInstrumentor.instrument_app(app)

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
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_request",
            "message": str(exc),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception):
    logger.exception("Unhandled exception")
    capture_errors.add(1, {"error_type": "unhandled"})
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Capture failed due to an internal error.",
        },
    )


@app.post("/capture", response_class=PlainTextResponse)
def capture(req: CaptureRequest):
    if not tracer:
        # Tracing disabled, run without spans
        return _do_capture(req)
    
    with tracer.start_as_current_span("camera.capture") as span:
        import time
        start_time = time.time()
        
        try:
            # Generate filepath
            if req.filename:
                filepath = "/remote/wopr/ml/incoming/" + Path(req.filename).name
            else:
                filepath = imagefilename(req.game_id, req.subject.value)

            span.set_attribute("camera.filepath", str(filepath))
            span.set_attribute("camera.filename_override", bool(req.filename))

            resolution = get_str("camera.default_resolution")
            width = get_int(f"camera.resolutions.{resolution}.width")
            height = get_int(f"camera.resolutions.{resolution}.height")
            
            span.set_attribute("camera.resolution", resolution)
            span.set_attribute("camera.width", width)
            span.set_attribute("camera.height", height)
            
            logger.info(f"Capturing {width}x{height} to {filepath}")

            # Camera initialization and capture
            with tracer.start_as_current_span("camera.device_init"):
                cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
                if not cap.isOpened():
                    raise RuntimeError("Camera device could not be opened")

                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            with tracer.start_as_current_span("camera.frame_capture"):
                ret, frame = cap.read()
                cap.release()

                if not ret:
                    raise RuntimeError("Camera capture failed (no frame read)")

            with tracer.start_as_current_span("camera.image_write"):
                cv2.imwrite(filepath, frame)

            duration_ms = (time.time() - start_time) * 1000
            capture_duration.record(duration_ms, {"endpoint": "capture"})
            capture_counter.add(1, {"endpoint": "capture", "status": "success"})
            
            span.set_status(Status(StatusCode.OK))
            return f"{filepath}\n"
            
        except Exception as e:
            capture_errors.add(1, {"error_type": type(e).__name__, "endpoint": "capture"})
            capture_counter.add(1, {"endpoint": "capture", "status": "error"})
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


@app.post("/capture_ml", response_class=PlainTextResponse)
def capture_ml(req: CaptureRequest):
    if not tracer:
        # Tracing disabled, run without spans
        return _do_capture_ml(req)
    
    with tracer.start_as_current_span("camera.capture_ml") as span:
        import time
        start_time = time.time()
        
        try:
            # Generate filepath
            filename = req.filename if req.filename else "noname.jpg"
            base_path = get_str('storage.base_path')
            ml_subdir = "ml"
            ml_dir = Path(base_path) / ml_subdir / 'incoming'
            filepath = ml_dir / f"{filename}"
            ml_dir.mkdir(parents=True, exist_ok=True)

            span.set_attribute("camera.filepath", str(filepath))
            span.set_attribute("camera.ml_mode", True)

            resolution = get_str("camera.default_resolution")
            width = get_int(f"camera.resolutions.{resolution}.width")
            height = get_int(f"camera.resolutions.{resolution}.height")
            
            span.set_attribute("camera.resolution", resolution)
            span.set_attribute("camera.width", width)
            span.set_attribute("camera.height", height)
            
            logger.info(f"Capturing {width}x{height} to {filepath}")

            # Camera initialization and capture
            with tracer.start_as_current_span("camera.device_init"):
                cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
                if not cap.isOpened():
                    raise RuntimeError("Camera device could not be opened")

                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            with tracer.start_as_current_span("camera.frame_capture"):
                ret, frame = cap.read()
                cap.release()

                if not ret:
                    raise RuntimeError("Camera capture failed (no frame read)")

            with tracer.start_as_current_span("camera.image_write"):
                cv2.imwrite(str(filepath), frame)

            duration_ms = (time.time() - start_time) * 1000
            capture_duration.record(duration_ms, {"endpoint": "capture_ml"})
            capture_counter.add(1, {"endpoint": "capture_ml", "status": "success"})
            
            logger.info(f"Captured image to {filepath}")
            span.set_status(Status(StatusCode.OK))
            return JSONResponse({"filename": str(filepath)})
            
        except Exception as e:
            capture_errors.add(1, {"error_type": type(e).__name__, "endpoint": "capture_ml"})
            capture_counter.add(1, {"endpoint": "capture_ml", "status": "error"})
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


@app.get("/status")
def status():
    if tracer:
        with tracer.start_as_current_span("camera.status"):
            return {"status": "ready"}
    return {"status": "ready"}


@app.get("/images/{game_id}")
def list_images(game_id: str):
    if not tracer:
        return _do_list_images(game_id)
    
    with tracer.start_as_current_span("camera.list_images") as span:
        span.set_attribute("game.id", game_id)
        
        game_dir = WOPR_ROOT / "games" / game_id

        if not game_dir.exists():
            span.set_status(Status(StatusCode.ERROR, "Game not found"))
            raise HTTPException(status_code=404, detail="Game not found")

        images = sorted(
            p for p in game_dir.rglob("*.jpg")
            if p.is_file()
        )

        result = [
            f"/wopr/{p.relative_to(WOPR_ROOT)}"
            for p in images
        ]

        span.set_attribute("images.count", len(result))
        span.set_status(Status(StatusCode.OK))
        
        return {
            "game_id": game_id,
            "count": len(result),
            "images": result,
        }