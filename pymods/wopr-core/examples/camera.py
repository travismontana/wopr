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

from wopr.config import init_config, get_str, get_int
from wopr.storage import imagefilename
from wopr.logging import setup_logging

# Initialize config client at startup
init_config()  # Uses WOPR_CONFIG_SERVICE_URL env var

logger = setup_logging("wopr-camera")

def capture(game_id: str, subject: str):
    # Fetch config from service
    resolution_name = get_str('camera.default_resolution')
    width = get_int(f'camera.resolutions.{resolution_name}.width')
    height = get_int(f'camera.resolutions.{resolution_name}.height')
    
    logger.info(f"Config fetched: {resolution_name} = {width}x{height}")
    
    # Generate filepath (also calls config service internally)
    filepath = imagefilename(game_id, subject)
    
    # ... capture code ...
    
    return filepath