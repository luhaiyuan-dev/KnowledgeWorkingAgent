import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import PROJECT_ROOT


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id
        event = getattr(record, "event", None)
        if event:
            payload["event"] = event
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(log_directory: str | Path | None = None) -> None:
    selected_directory = Path(log_directory) if log_directory else PROJECT_ROOT / "logs"
    selected_directory.mkdir(parents=True, exist_ok=True)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()

    formatter = JsonFormatter()
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.FileHandler(selected_directory / "agent.jsonl", encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
