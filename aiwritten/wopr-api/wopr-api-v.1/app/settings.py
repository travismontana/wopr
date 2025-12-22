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
