#!/usr/bin/env python3
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


import cv2
import time
import random
import string
from datetime import datetime

from wopr.config import get_config
from wopr.logging import setup_logging
from wopr.storage import imagefilename

config = get_config()
logger = setup_logging("wopr-camera", config=config)

game_id = "dune_imperium"
subject = "capture"
sequence = 1

# Generate filepath from config
filepath = imagefilename(
  game_id=game_id,
  subject=subject,
  sequence=sequence,
  config=config
)
  
resolution = config.camera.get_resolution(config.camera.default_resolution)
logger.info(f"Capturing {resolution.width}x{resolution.height} to {filepath}")
    
# Initialize camera (0 = default camera)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

# Set resolution (may or may not work depending on camera)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution.width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution.height)

# Capture
ret, frame = cap.read()
if ret:
    print(f"File: {filepath}")
    cv2.imwrite(filepath, frame)

cap.release()
