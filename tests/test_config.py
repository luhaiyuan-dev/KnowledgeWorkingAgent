from app.core.config import load_settings


def test_settings_can_be_loaded() -> None:
    load_settings.cache_clear()
    settings = load_settings()
    assert settings.app.name.startswith("星海智联")
    assert settings.rag.chunk_overlap < settings.rag.chunk_size
