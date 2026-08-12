import runpy
from pathlib import Path

from fastapi.testclient import TestClient
from streamlit.testing.v1 import AppTest

from api.main import app

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_endpoint() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/chat",
            json={"message": "你好", "session_id": "api-test", "mode": "auto"},
        )
    assert response.status_code == 200
    assert response.json()["answer"]


def test_streamlit_entry_can_import_application_package() -> None:
    namespace = runpy.run_path("ui/app.py", run_name="streamlit_import_test")
    assert callable(namespace["main"])


def test_streamlit_application_runs_without_exception() -> None:
    app_test = AppTest.from_file(PROJECT_ROOT / "ui/app.py")
    app_test.run(timeout=15)
    assert not app_test.exception
    assert any(button.label == "＋ 新建对话" for button in app_test.button)
