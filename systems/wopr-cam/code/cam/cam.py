import logging
import httpx
import torch
import time

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from picamera2 import Picamera2

from lib.helpers import setup_logger

logger = setup_logger()

APP_NAME = "wopr-model"
APP_API_VERSION = "v1"

logger.info(f"Starting {APP_NAME} application")

logger.info(f"Setup variables")

# Allons Ye!
app = FastAPI(
    title=APP_NAME,
)

cam_router = APIRouter()

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

@cam_router.get("/api/capture_preview")
def capture_preview():
    logger.info("Received request for capture preview")
    cam = Picamera2()
    cam.start()
    time.sleep(2)  # Allow camera to warm up
    try:
        preview_image = cam.capture_array("main")
    except Exception as e:
        logger.error(f"Error capturing preview image: {e}")
        raise HTTPException(status_code=500, detail="Failed to capture preview image")
    finally:
        cam.stop()
    
    return preview_image
