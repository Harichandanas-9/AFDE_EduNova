"""
Centralized application configuration.

All configuration values are loaded from environment variables with
sensible defaults. Never hardcode secrets in source code.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Core ---
    APP_NAME: str = "EduNova AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    API_V1_PREFIX: str = "/api/v1"

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8000)

    # --- Security ---
    SECRET_KEY: str = Field(default="change-me-in-production-please-use-a-strong-key")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # --- CORS ---
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
        ]
    )

    # --- Database ---
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./edunova.db")
    DATABASE_ECHO: bool = False

    # --- LLM Providers ---
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    LLM_PROVIDER: str = Field(default="openai")  # "openai" | "gemini" | "mock"
    LLM_TEMPERATURE: float = 0.4
    LLM_MAX_TOKENS: int = 1500

    # --- DeepEval ---
    DEEPEVAL_ENABLED: bool = True
    DEEPEVAL_THRESHOLD: float = 0.6
    DEEPEVAL_MAX_RETRIES: int = 2

    # --- Rate Limiting ---
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # --- Logging ---
    LOG_LEVEL: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()
