#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
Copyright (c) 2025 Bob Bomar <bob@bomar.us>
SPDX-License-Identifier: MIT

Configuration management - integrates wopr-core with environment variables.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

# Import wopr-core for config service integration
# NOTE: In production, install wopr-core package
# For now, assumes wopr-core is in PYTHONPATH or installed
try:
    import wopr
    WOPR_CORE_AVAILABLE = True
except ImportError:
    WOPR_CORE_AVAILABLE = False
    print("WARNING: wopr-core not available, using environment variables only")


class Settings(BaseSettings):
    """Application settings - combines env vars and wopr-config"""
    
    # ===== SECRETS (from environment) =====
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection string"
    )
    JWT_SECRET_KEY: str = Field(
        ...,
        description="Secret key for JWT signing"
    )
    REDIS_URL: str = Field(
        default="redis://wopr-redis.svc:6379/0",
        description="Redis connection URL"
    )
    
    # ===== WOPR CONFIG SERVICE =====
    WOPR_CONFIG_SERVICE_URL: str = Field(
        default="http://wopr-config_service.svc:8080",
        description="WOPR config service URL"
    )
    
    # ===== API SETTINGS =====
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: List[str] = ["*"]
    
    # Auth settings
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    API_KEY_EXPIRY_DAYS: int = 365
    
    # ===== OPENTELEMETRY =====
    OTEL_ENABLED: bool = True
    OTEL_ENDPOINT: str = "http://tempo.studio:4317"
    OTEL_SERVICE_NAME: str = "wopr-api"
    
    # ===== SERVICE URLS =====
    WOPR_VISION_URL: str = "http://wopr-vision.svc:8001"
    WOPR_ADJUDICATOR_URL: str = "http://wopr-adjudicator.svc:8002"
    
    # ===== CELERY =====
    CELERY_BROKER_URL: str | None = None  # Defaults to REDIS_URL
    CELERY_RESULT_BACKEND: str | None = None  # Defaults to REDIS_URL
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize wopr-core if available
        if WOPR_CORE_AVAILABLE:
            wopr.init_config(service_url=self.WOPR_CONFIG_SERVICE_URL)
            self._load_from_wopr_config()
        
        # Set Celery defaults
        if self.CELERY_BROKER_URL is None:
            self.CELERY_BROKER_URL = self.REDIS_URL
        if self.CELERY_RESULT_BACKEND is None:
            self.CELERY_RESULT_BACKEND = self.REDIS_URL
    
    def _load_from_wopr_config(self) -> None:
        """Load settings from wopr-config service"""
        try:
            # API settings
            self.API_HOST = wopr.get_str("api.host", self.API_HOST)
            self.API_PORT = wopr.get_int("api.port", self.API_PORT)
            
            # Auth settings
            self.JWT_ALGORITHM = wopr.get_str("api.jwt_algorithm", self.JWT_ALGORITHM)
            self.JWT_EXPIRY_HOURS = wopr.get_int("api.jwt_expiry_hours", self.JWT_EXPIRY_HOURS)
            self.API_KEY_EXPIRY_DAYS = wopr.get_int("api.api_key_expiry_days", self.API_KEY_EXPIRY_DAYS)
            
            # OTEL settings
            self.OTEL_ENABLED = wopr.get_bool("otel.enabled", self.OTEL_ENABLED)
            self.OTEL_ENDPOINT = wopr.get_str("otel.endpoint", self.OTEL_ENDPOINT)
            self.OTEL_SERVICE_NAME = wopr.get_str("otel.service_name", self.OTEL_SERVICE_NAME)
            
            # Service URLs
            self.WOPR_VISION_URL = wopr.get_str("api.wopr_vision_url", self.WOPR_VISION_URL)
            self.WOPR_ADJUDICATOR_URL = wopr.get_str("api.wopr_adjudicator_url", self.WOPR_ADJUDICATOR_URL)
            
            # Celery
            celery_broker = wopr.get_str("celery.broker_url", None)
            if celery_broker:
                self.CELERY_BROKER_URL = celery_broker
            celery_backend = wopr.get_str("celery.result_backend", None)
            if celery_backend:
                self.CELERY_RESULT_BACKEND = celery_backend
                
        except Exception as e:
            print(f"WARNING: Failed to load some config from wopr-config: {e}")


# Global settings instance
settings = Settings()


def get_wopr_config():
    """
    Get wopr-core config client for direct access to config values.
    
    Returns wopr config client or None if unavailable.
    """
    if WOPR_CORE_AVAILABLE:
        return wopr.get_client()
    return None
