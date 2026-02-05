import logging
import httpx
import time

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from picamera2 import Picamera2
from libcamera import Transform


from .lib.helpers import setup_logger

logger = setup_logger()

APP_NAME = "wopr-model"
APP_API_VERSION = "v1"

logger.info(f"Starting {APP_NAME} application")

logger.info(f"Setup variables")

# Allons Ye!
app = FastAPI(
    title=APP_NAME,
)

# health page
@app.get("/health")
def get_health():
    return "healthy"


@app.get("/nelson")
def nelson():
    return "haha"


@app.get("/status")
def get_status():
    status = []

    return status


@app.get("/api/capture_preview")
def capture_preview():
    logger.info("Received request for capture preview")
    # 4k
    width = 3840
    height = 2160
    cam = Picamera2()
    camera_config = cam.create_preview_configuration(
        main={"size": (width, height), "format": "RGB888"},
        transform=Transform(hflip=1, vflip=1),
    )
    cam.configure(camera_config)
    cam.start()
    time.sleep(2)  # Allow camera to warm up
    try:
        preview_image = cam.capture_images("main")
    except Exception as e:
        logger.error(f"Error capturing preview image: {e}")
        raise HTTPException(status_code=500, detail="Failed to capture preview image")
    finally:
        cam.stop()

    return preview_image
