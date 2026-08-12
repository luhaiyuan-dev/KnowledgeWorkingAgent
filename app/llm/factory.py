import os

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from app.core.config import Settings


def build_chat_model(settings: Settings) -> BaseChatModel | None:
    if settings.app.demo_mode:
        return None

    if settings.llm.provider != "openai":
        raise ValueError(f"当前示例尚未注册 LLM 提供商：{settings.llm.provider}")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("非演示模式必须在 .env 中配置 OPENAI_API_KEY")

    model_arguments: dict[str, object] = {
        "model": settings.llm.model,
        "temperature": settings.llm.temperature,
        "api_key": api_key,
    }
    if settings.llm.base_url:
        model_arguments["base_url"] = settings.llm.base_url

    return ChatOpenAI(**model_arguments)
