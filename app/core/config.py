import os
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class AppConfig(BaseModel):
    name: str
    environment: str = "development"
    demo_mode: bool = True
    max_input_chars: int = 6000


class LlmConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-5.4-mini"
    temperature: float = 0.1
    max_iterations: int = 6
    base_url: str | None = None


class EmbeddingConfig(BaseModel):
    provider: str = "hash"
    model: str = "BAAI/bge-small-zh-v1.5"
    dimensions: int = 384


class RagConfig(BaseModel):
    knowledge_base_dir: str
    vector_store_path: str
    chunk_size: int = 800
    chunk_overlap: int = 120
    retrieval_top_k: int = 8
    rerank_top_n: int = 4
    minimum_score: float = 0.05


class MemoryConfig(BaseModel):
    max_messages: int = 12
    max_characters: int = 12000


class SecurityConfig(BaseModel):
    mask_pii_in_logs: bool = True
    block_prompt_injection: bool = False
    require_confirmation_for_high_risk_tools: bool = True


class WebSearchConfig(BaseModel):
    provider: str = "tavily"
    timeout_seconds: int = 15


class Settings(BaseModel):
    app: AppConfig
    llm: LlmConfig
    embedding: EmbeddingConfig
    rag: RagConfig
    memory: MemoryConfig
    security: SecurityConfig
    web_search: WebSearchConfig

    def project_path(self, relative_path: str) -> Path:
        return (PROJECT_ROOT / relative_path).resolve()


@lru_cache(maxsize=1)
def load_settings(config_path: str | Path | None = None) -> Settings:
    load_dotenv(PROJECT_ROOT / ".env")
    selected_path = Path(config_path) if config_path else PROJECT_ROOT / "configs/settings.yaml"
    with selected_path.open("r", encoding="utf-8") as config_file:
        raw_settings = yaml.safe_load(config_file)

    demo_mode_value = os.getenv("DEMO_MODE")
    if demo_mode_value is not None:
        raw_settings["app"]["demo_mode"] = demo_mode_value.lower() in {"1", "true", "yes"}

    environment_value = os.getenv("APP_ENV")
    if environment_value:
        raw_settings["app"]["environment"] = environment_value

    base_url_value = os.getenv("OPENAI_BASE_URL")
    if base_url_value:
        raw_settings["llm"]["base_url"] = base_url_value

    return Settings.model_validate(raw_settings)
