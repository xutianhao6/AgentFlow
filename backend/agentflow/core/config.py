"""Application configuration (pydantic-settings reads from .env)."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Storage
    database_url: str = "sqlite:///./agentflow.db"
    redis_url: str = "redis://localhost:6379/0"
    storage_dir: str = "./storage"

    # LLM — SiliconFlow (OpenAI-compatible API)
    llm_provider: str = "siliconflow"
    anthropic_api_key: str = ""  # kept for backward compatibility
    siliconflow_api_key: str = ""
    siliconflow_base_url: str = "https://api.siliconflow.cn/v1"
    llm_model: str = "Qwen/Qwen2.5-7B-Instruct"
    embedding_model: str = "BAAI/bge-large-zh-v1.5"

    # CORS
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
