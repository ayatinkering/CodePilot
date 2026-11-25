from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Budgets(BaseModel):
    """Per-run limits; stricter requests are allowed, exceeding hard caps is not."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    candidates: int = Field(default=3, ge=1, le=3)
    generation_calls: int = Field(default=8, ge=1, le=8)
    tokens: int = Field(default=32000, ge=1, le=64000)
    wall_seconds: int = Field(default=600, ge=1, le=600)
    test_seconds: int = Field(default=120, ge=1, le=120)
    changed_lines: int = Field(default=50, ge=1, le=50)
    production_files: int = Field(default=3, ge=1, le=3)
    indexed_files: int = Field(default=2000, ge=1, le=2000)
    indexed_bytes: int = Field(default=10_000_000, ge=1, le=10_000_000)
    file_bytes: int = Field(default=200_000, ge=1, le=200_000)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CODEPILOT_", env_file=".env", extra="ignore")
    data_dir: Path = Path(".codepilot")
    provider: Literal["gemini", "offline"] = "gemini"
    model: str = ""
