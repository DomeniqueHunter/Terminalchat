import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from cursed_descent.web import chat
from cursed_descent.web.app import create_app
from cursed_descent.web.hub import GameHub


def test_parse_commands() -> None:
    assert chat.parse("hello  there") == ("say", "", "hello  there")
    assert chat.parse("!say hi") == ("say", "", "hi")
    assert chat.parse("!w Lyra Dawn: psst") == ("whisper", "Lyra Dawn",
                                                "psst")
    assert chat.parse("!w kerl psst") == ("whisper", "kerl", "psst")
    assert chat.parse("!hit") is None and chat.parse("   ") is None


def test_the_limiter_blocks_a_flood() -> None:
    limiter = chat.Limiter()
    assert all(limiter.allow("a", now=0.0) for _ in range(5))
    assert not limiter.allow("a", now=1.0)
    assert limiter.allow("a", now=60.0)


def test_say_reaches_only_the_same_place(data_path:Path) -> None:
    hub = GameHub(data_path)
    controller = hub.controller
    for name in ("kerl", "galactica", "Gianna Morningwood"):
        player = controller.repository.load(name)
        player.profile["where"] = "home"
        controller.repository.save(player)
    away = controller.repository.load("galactica")
    away.profile["where"] = "shop"
    controller.repository.save(away)
    items = chat.deliver(controller, "kerl", "say", "", "hi <b>")
    names, entry = items[0]
    assert "kerl" in names and "Gianna Morningwood" in names
    assert "galactica" not in names
    assert entry["text"] == "💬 kerl: hi <b>"


def test_whisper_and_errors(data_path:Path) -> None:
    controller = GameHub(data_path).controller
    names, entry = chat.deliver(controller, "kerl", "whisper", "Galactica",
                                "secret")[0]
    assert names == {"kerl", "galactica"} or names == {"kerl", "Galactica"}
    for kind, target, body in (("whisper", "nobody", "x"),
                               ("whisper", "kerl", "x"),
                               ("say", "", ""), ("say", "", "x" * 301)):
        with pytest.raises(chat.ChatError):
            chat.deliver(controller, "kerl", kind, target, body)


def test_plain_text_is_chat_over_the_socket(data_path:Path) -> None:
    with TestClient(create_app(data_path, login=False)) as client:
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            socket.send_text(json.dumps({"action": "cmd", "viewer": "kerl",
                                         "text": "hello <i>world</i>"}))
            page = socket.receive_text()
    assert "kerl: hello &lt;i&gt;world&lt;/i&gt;" in page
    assert 'class="line chat"' in page


def test_a_failed_whisper_shows_the_usage_line(data_path:Path) -> None:
    with TestClient(create_app(data_path, login=False)) as client:
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            socket.send_text(json.dumps({"action": "cmd", "viewer": "kerl",
                                         "text": "!w nobody: hi"}))
            page = socket.receive_text()
    assert "Nobody called" in page and 'class="line usage"' in page
    assert "Usage: !w &lt;name&gt;: &lt;text&gt;" in page


def test_panels_resolve_name_tokens_but_chat_text_stays_literal(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    page = hub.render("log.html", entries=[
        {"text": "<<npc.astrid_last>>", "kind": "chat"}])
    assert "&lt;&lt;npc.astrid_last&gt;&gt;" in page
    from cursed_descent.town_buildings.brewhouse.content import BLURB
    assert "<<" not in hub.render("panels.html", **{
        "viewer": "", "players": [], "stage": BLURB, "main": "",
        "debug": False, "auto_time": True, "status": "", "slots": [],
        "hire": [], "encounter": [], "hits": [], "party_buttons": [],
        "profile_buttons": [], "combat_buttons": [], "debug_buttons": [],
        "targets": [], "visit": None, "sex": None, "visit_label": "",
        "sex_label": "", "free": 0, "character": None, "inventory": None,
        "party": None, "family": None, "contacts": [], "location": [],
        "world": {"day": 0, "elapsed": 0, "length": 3600},
        "account_name": "", "is_admin": False, "run_shop": False})
