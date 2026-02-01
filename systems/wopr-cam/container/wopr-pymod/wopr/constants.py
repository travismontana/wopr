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

"""Shared constants across WOPR components"""

# These are Python constants that don't change
# Actual configuration values come from the config service

# Game types (IDs)
GAME_TYPE_DUNE = "dune_imperium"
GAME_TYPE_LEGION = "star_wars_legion"

# Game statuses
STATUS_SETUP = "setup"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"
STATUS_ABANDONED = "abandoned"

# Analysis statuses
ANALYSIS_PENDING = "pending"
ANALYSIS_PROCESSING = "processing"
ANALYSIS_COMPLETED = "completed"
ANALYSIS_FAILED = "failed"

# Image subjects
SUBJECT_SETUP = "setup"
SUBJECT_CAPTURE = "capture"
SUBJECT_MOVE = "move"
SUBJECT_THUMBNAIL = "thumbnail"

# Vision models
MODEL_QWEN2VL = "qwen2-vl:7b"
MODEL_OPENCV = "opencv"
