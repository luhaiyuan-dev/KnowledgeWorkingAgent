from app.core.config import load_settings
from app.rag.loader import EnterpriseDocumentLoader


def test_loader_supports_all_sample_formats() -> None:
    settings = load_settings()
    loader = EnterpriseDocumentLoader(settings.project_path(settings.rag.knowledge_base_dir))
    documents = loader.load_directory()
    loaded_types = {document.metadata["file_type"] for document in documents}
    assert {"pdf", "docx", "xlsx", "txt", "md"}.issubset(loaded_types)
    assert all(document.page_content.strip() for document in documents)


def test_loader_blocks_path_traversal(tmp_path) -> None:
    allowed_root = tmp_path / "knowledge"
    allowed_root.mkdir()
    outside_file = tmp_path / "secret.txt"
    outside_file.write_text("secret", encoding="utf-8")
    loader = EnterpriseDocumentLoader(allowed_root)

    try:
        loader.load_file(outside_file)
    except PermissionError:
        pass
    else:
        raise AssertionError("路径穿越请求应被拒绝")
