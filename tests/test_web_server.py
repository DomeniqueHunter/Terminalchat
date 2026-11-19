from pathlib import Path

from fastapi.testclient import TestClient

from cursed_descent.web.__main__ import DEFAULT_PORT
from cursed_descent.web.app import create_app


def test_health_and_index_answer_and_create_the_game(tmp_path:Path) -> None:
    with TestClient(create_app(tmp_path, login=False)) as client:
        assert client.get("/health").json() == {"status": "ok"}
        page = client.get("/").text
        assert "Cursed Descent" in page and 'ws-connect="/ws"' in page
        assert client.get("/static/htmx.min.js").status_code == 200
        assert client.app.state.controller.repository is not None
    assert any(tmp_path.iterdir())


def test_the_server_listens_on_port_6969() -> None:
    assert DEFAULT_PORT == 6969
    root = Path(__file__).resolve().parent.parent
    assert "6969:6969" in (root / "docker-compose.yml").read_text()
    assert "game_data:/data" in (root / "docker-compose.yml").read_text()


def test_requirements_pull_in_a_websocket_library() -> None:
    root = Path(__file__).resolve().parent.parent
    text = (root / "requirements.txt").read_text()
    assert "websockets" in text and "uvicorn[standard]" in text
