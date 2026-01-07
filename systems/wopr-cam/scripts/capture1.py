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

now = datetime.now()
timestamp = now.strftime("%Y%m%d-%H%M%S")

# Initialize camera (0 = default camera)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
woprdir = "/remote/wopr"
woprimagedir = f"{woprdir}/images"
woprimagedirimport = f"{woprimagedir}/import"
project = "testproj1"
subject = "round1"

for i in range(3):
  sixrand = ''.join(random.sample(string.ascii_lowercase, 8))

imagefile = f"{timestamp}-{sixrand}-{project}-{subject}.jpg"
imagefullpath = f"{woprimagedirimport}/{imagefile}"

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

# Set resolution (may or may not work depending on camera)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(3, 3840)
cap.set(4, 2160)

# Capture
ret, frame = cap.read()
if ret:
    print(f"File: {imagefullpath}")
    cv2.imwrite(imagefullpath, frame)

cap.release()
