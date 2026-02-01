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

"""WOPR Core Library - Tactical Wargaming Adjudication Tracker"""

from wopr.config import (
    init_config,
    get_setting,
    get_str,
    get_int,
    get_float,
    get_bool,
    get_list,
    get_dict,
    get_section,
    reload_config,
    ConfigError
)
from wopr.storage import (
    imagefilename,
    thumbnailfilename,
    ensure_path,
    get_game_directory,
    list_game_images,
    StorageError
)
from wopr.logging import setup_logging, get_logger

__version__ = "0.1.0"
__all__ = [
    # Config
    'init_config',
    'get_setting',
    'get_str',
    'get_int',
    'get_float',
    'get_bool',
    'get_list',
    'get_dict',
    'get_section',
    'reload_config',
    'ConfigError',
    # Storage
    'imagefilename',
    'thumbnailfilename',
    'ensure_path',
    'get_game_directory',
    'list_game_images',
    'StorageError',
    # Logging
    'setup_logging',
    'get_logger',
]
