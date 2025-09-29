from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")
    TAVILY_API_KEY: str

    # --- MODEL NAME ---
    MODEL: str = "openai:gpt-5-nano-2025-08-07"

    # --- MODEL PROVIDERS ---
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str

    # --- MEMORY CONFIGURATION ---
    MEMORY_SIZE: int = 20

    # --- MCP Servers ---
    MCP_CONFIG: str

    # --- PIXELTABLE SETTINGS ---
    PIXELTABLE_HOME: str
    PIXELTABLE_VERBOSITY: str = "0"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get the application settings."""
    return Settings()
