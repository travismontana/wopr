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
import random
import string
from datetime import datetime

from wopr.config import init_config, get_str, get_int
from wopr.logging import setup_logging
from wopr.storage import imagefilename

# get configs
init_config()

logger = setup_logging("wopr-camera")

from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/capture', methods=['POST'])
def capture():
    data = request.json
    game_id = data['game_id']
    subject = data['subject']
    subject_name = data['subject_name']
    sequence = data['sequence']

    # Generate filepath from config
    filepath = imagefilename(game_id, subject)

    resolution = get_str('camera.default_resolution')
    logger.info(f"Res: {resolution}")
    width = get_int(f'camera.resolutions.{resolution}.width')
    height = get_int(f'camera.resolutions.{resolution}.height')
    logger.info(f"Capturing {width}x{height} to {filepath}")
        
    # Initialize camera (0 = default camera)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

    # Set resolution (may or may not work depending on camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # Capture
    ret, frame = cap.read()
    if ret:
        print(f"File: {filepath}")
        cv2.imwrite(filepath, frame)

    cap.release()
    return filepath

@app.route('/captureml', methods=['POST'])
def capture_ml():
    data = request.json
    game_id = data['game_id']
    subject = data['subject']
    subject_name = data['subject_name']
    sequence = data['sequence']

    # Generate filepath from config
    filepath1 = imagefilename(game_id, subject)
    # Build full path
    base_path = get_str('storage.base_path')
    ml_subdir = "ml" # get_str('storage.ml_subdir')
    ml_dir = Path(base_path) / ml_subdir / game_id
    filename = filepath1.split('/')[-1]
    filepath = ml_dir / f"{subject_name}-{filename}"
    ensure_path(ml_dir)

    resolution = get_str('camera.default_resolution')
    logger.info(f"Res: {resolution}")
    width = get_int(f'camera.resolutions.{resolution}.width')
    height = get_int(f'camera.resolutions.{resolution}.height')
    logger.info(f"Capturing {width}x{height} to {filepath}")
        
    # Initialize camera (0 = default camera)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

    # Set resolution (may or may not work depending on camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # Capture
    ret, frame = cap.read()
    if ret:
        print(f"File: {filepath}")
        cv2.imwrite(filepath, frame)

    cap.release()
    return filepath

@app.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'ready'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
