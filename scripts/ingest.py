import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    from app.agent.service import create_service
    from app.observability.logging_config import configure_logging

    configure_logging()
    service = create_service()
    statistics = service.rag.ingest()
    print(
        "知识库索引完成："
        f"{statistics['files']} 个文件，"
        f"{statistics['documents']} 个解析单元，"
        f"{statistics['chunks']} 个检索分块。"
    )


if __name__ == "__main__":
    main()
