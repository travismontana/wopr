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
import time
import logging
import sys
from enum import Enum
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from picamera2 import Picamera2

# OTel imports
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.trace.status import Status, StatusCode

#from wopr.config import init_config, get_str, get_int, get_bool
from wopr.logging import setup_logging
from wopr.tracing import create_tracer
from wopr.storage import imagefilename

# Import globals module for constants
import globals as g

# Initialize config first
WOPR_API_URL = "https://api.wopr.tailandtraillabs.org/api/v2/config"
#init_config(service_url=WOPR_API_URL)

logger = setup_logging("wopr-cam", log_file="/var/log/wopr-cam.log")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logger.info(f"Starting {g.APP_TITLE} v{g.APP_VERSION}")
logger.info(f"WOPR API URL: {g.WOPR_API_URL}")
# Initialize tracer using centralized setup with globals
tracer = create_tracer(
    tracer_name=g.APP_NAME,
    tracer_version=g.APP_VERSION,
    tracer_enabled=False,
    tracer_endpoint=g.APP_OTEL_URL+"/v1/traces"
)

# Metrics provider setup
resource = Resource(attributes={
    SERVICE_NAME: g.APP_NAME,
    SERVICE_VERSION: g.APP_VERSION,
})

metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(
        endpoint=f"{g.APP_OTEL_URL}/v1/metrics",
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

app = FastAPI(title=g.APP_TITLE, version=g.APP_VERSION)

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


def _trace_if_enabled(span_name: str):
    """Context manager that creates a span if tracing is enabled, otherwise does nothing."""
    if tracer:
        return tracer.start_as_current_span(span_name)
    else:
        from contextlib import nullcontext
        return nullcontext()


@app.post("/capture", response_class=PlainTextResponse)
def capture(req: CaptureRequest):
    with _trace_if_enabled("camera.capture") as span:
        start_time = time.time()
        
        try:
            # Generate filepath
            if req.filename:
                filepath = "/remote/wopr/ml/incoming/" + Path(req.filename).name
            else:
                filepath = imagefilename(req.game_id, req.subject.value)

            if span:
                span.set_attribute("camera.filepath", str(filepath))
                span.set_attribute("camera.filename_override", bool(req.filename))

            resolution = "4k"
            width = "4056"
            height = "3040"
            
            if span:
                span.set_attribute("camera.resolution", resolution)
                span.set_attribute("camera.width", width)
                span.set_attribute("camera.height", height)
            
            logger.info(f"Capturing {width}x{height} to {filepath}")

            # Camera initialization and capture
            with _trace_if_enabled("camera.device_init"):
                cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
                if not cap.isOpened():
                    raise RuntimeError("Camera device could not be opened")

                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            with _trace_if_enabled("camera.frame_capture"):
                ret, frame = cap.read()
                cap.release()

                if not ret:
                    raise RuntimeError("Camera capture failed (no frame read)")

            with _trace_if_enabled("camera.image_write"):
                cv2.imwrite(filepath, frame)

            duration_ms = (time.time() - start_time) * 1000
            capture_duration.record(duration_ms, {"endpoint": "capture"})
            capture_counter.add(1, {"endpoint": "capture", "status": "success"})
            
            if span:
                span.set_status(Status(StatusCode.OK))
            return f"{filepath}\n"
            
        except Exception as e:
            capture_errors.add(1, {"error_type": type(e).__name__, "endpoint": "capture"})
            capture_counter.add(1, {"endpoint": "capture", "status": "error"})
            if span:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
            raise


@app.post("/capture_ml", response_class=PlainTextResponse)
def capture_ml(req: CaptureRequest):
    with _trace_if_enabled("camera.capture_ml") as span:
        start_time = time.time()
        
        try:
            # Generate filepath
            filename = req.filename if req.filename else "noname.jpg"
            base_path = "/remote/wopr"
            ml_subdir = "ml"
            ml_dir = Path(base_path) / ml_subdir / 'incoming'
            filepath = ml_dir / f"{filename}"
            ml_dir.mkdir(parents=True, exist_ok=True)

            if span:
                span.set_attribute("camera.filepath", str(filepath))
                span.set_attribute("camera.ml_mode", True)

            resolution = "4k"
            width = 4056
            height = 3040
            if span:
                span.set_attribute("camera.resolution", resolution)
                span.set_attribute("camera.width", width)
                span.set_attribute("camera.height", height)
            
            logger.info(f"Capturing {width}x{height} to {filepath}")

            # Camera initialization and capture
            with _trace_if_enabled("camera.device_init"):
                cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
                if not cap.isOpened():
                    raise RuntimeError("Camera device could not be opened")

                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            with _trace_if_enabled("camera.frame_capture"):
                ret, frame = cap.read()
                cap.release()

                if not ret:
                    raise RuntimeError("Camera capture failed (no frame read)")

            with _trace_if_enabled("camera.image_write"):
                cv2.imwrite(str(filepath), frame)

            duration_ms = (time.time() - start_time) * 1000
            capture_duration.record(duration_ms, {"endpoint": "capture_ml"})
            capture_counter.add(1, {"endpoint": "capture_ml", "status": "success"})
            
            logger.info(f"Captured image to {filepath}")
            if span:
                span.set_status(Status(StatusCode.OK))
            return JSONResponse({"filename": str(filepath)})
            
        except Exception as e:
            capture_errors.add(1, {"error_type": type(e).__name__, "endpoint": "capture_ml"})
            capture_counter.add(1, {"endpoint": "capture_ml", "status": "error"})
            if span:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
            raise


@app.get("/status")
def status():
    with _trace_if_enabled("camera.status"):
        return {"status": "ready"}

@app.get("/grab/{camera_id}")
@app.get("/grab/{camera_id}/")
def grab_camera(camera_id: int):
    with _trace_if_enabled("camera.grab") as span:
        if span:
            span.set_attribute("camera.id", camera_id)
    camType = g.WOPR_CONFIG["camera"]["camDict"][str(camera_id)]["type"]
    if camType == "blank":
        return "no id"
    width = g.WOPR_CONFIG["camera"]["camDict"][str(camera_id)]["width"]
    height = g.WOPR_CONFIG["camera"]["camDict"][str(camera_id)]["height"]
    if camType == "imx477":
        picam2 = Picamera2()
        picam2.stop()
        picam2.close()
        camera_config = picam2.create_preview_configuration()
        camera_config["main"]["size"] = (width, height)
        camera_config["main"]["format"] = "RGB888"
        picam2.configure(camera_config)
        picam2.start()
        time.sleep(2)
        image_array = picam2.capture_array("main")
        picam2.stop()
        return image_array
    else:
        try:
            cap = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
            if not cap.isOpened():
                raise RuntimeError("Camera device could not be opened")

            ret, frame = cap.read()
            cap.release()

            if not ret:
                raise RuntimeError("Camera capture failed (no frame read)")

            _, img_encoded = cv2.imencode('.jpg', frame)
            if span:
                span.set_status(Status(StatusCode.OK))
            return PlainTextResponse(content=img_encoded.tobytes(), media_type="image/jpeg")
        
        except Exception as e:
            if span:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
            raise HTTPException(status_code=500, detail="Camera stream failed")
