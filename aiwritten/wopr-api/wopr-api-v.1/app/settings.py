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

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WOPR_", extra="ignore")

    db_url: str = "postgresql+psycopg://wopr:wopr@localhost:5432/wopr_main"
    redis_url: str = "redis://localhost:6379/0"

    # External services
    wopr_cam_base_url: str = "http://wopr-cam:5000"
    wopr_vision_base_url: str = "http://wopr-vision:9000"
    wopr_adjudicator_base_url: str = "http://wopr-adjudicator:9100"

    # Storage root (NFS mounted in pods)
    nfs_root: str = "/mnt/nas/wopr"

    # SSE
    sse_keepalive_seconds: int = 15


settings = Settings()
