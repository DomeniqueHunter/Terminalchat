from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from cursed_descent.web.app import create_app


def register(client:TestClient, name:str="Brain") -> None:
    serial = client.app.state.hub.store.new_serials(1)[0]
    reply = client.post("/register", data={
        "serial": serial, "name": name, "password": "longpassword"},
        follow_redirects=False)
    assert reply.status_code == 303


def test_without_login_the_page_is_the_login_form(tmp_path:Path) -> None:
    with TestClient(create_app(tmp_path)) as client:
        page = client.get("/").text
        assert "Serial key" in page and 'ws-connect="/ws"' not in page
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/ws"):
                pass


def test_register_login_and_logout(tmp_path:Path) -> None:
    with TestClient(create_app(tmp_path)) as client:
        register(client)
        assert 'ws-connect="/ws"' in client.get("/").text
        client.post("/logout")
        assert "Serial key" in client.get("/").text
        bad = client.post("/login", data={"name": "Brain",
                                          "password": "wrong"})
        assert bad.status_code == 401
        good = client.post("/login", data={
            "name": "brain", "password": "longpassword"},
            follow_redirects=False)
        assert good.status_code == 303


def test_a_serial_works_once_and_bad_data_is_refused(tmp_path:Path) -> None:
    with TestClient(create_app(tmp_path)) as client:
        serial = client.app.state.hub.store.new_serials(1)[0]
        data = {"serial": serial, "name": "One", "password": "longpassword"}
        assert client.post("/register", data=data,
                           follow_redirects=False).status_code == 303
        again = {**data, "name": "Two"}
        assert client.post("/register", data=again).status_code == 400
        assert client.post("/register", data={
            "serial": "nope", "name": "Three",
            "password": "longpassword"}).status_code == 400


def test_a_player_sees_only_own_characters_and_is_no_admin(
        data_path:Path) -> None:
    with TestClient(create_app(data_path)) as client:
        register(client)
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            hub = client.app.state.hub
            assert hub.visible(hub.clients[0]) == []
            assert not hub.tools_on(hub.clients[0])


def test_creating_a_character_is_limited_per_account(
        tmp_path:Path) -> None:
    from cursed_descent.config import MAX_CHARS_PER_ACCOUNT
    with TestClient(create_app(tmp_path)) as client:
        register(client)
        hub = client.app.state.hub
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            account = hub.clients[0].account
            for number in range(MAX_CHARS_PER_ACCOUNT):
                assert hub.start_creation(hub.clients[0],
                                          f"Hero{number}") == ""
                from cursed_descent.models import Player
                hub.controller.repository.add(Player(
                    name=f"Hero{number}", account_id=account.id))
            assert "at most" in hub.start_creation(hub.clients[0], "Third")
            assert hub.visible(hub.clients[0]) == ["Hero0", "Hero1"]


def test_temporary_admin_sees_only_own_chars_and_ends_on_restart(
        data_path:Path) -> None:
    with TestClient(create_app(data_path)) as client:
        register(client)
        hub = client.app.state.hub
        hub.store.set_admin("Brain", 3600)
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            assert hub.tools_on(hub.clients[0])
            assert "kerl" not in hub.visible(hub.clients[0])
    with TestClient(create_app(data_path)) as client:
        assert not client.app.state.hub.store.accounts()[0].admin


def test_a_single_character_is_selected_on_connect(tmp_path:Path) -> None:
    from cursed_descent.models import Player
    with TestClient(create_app(tmp_path)) as client:
        register(client)
        hub = client.app.state.hub
        account = hub.store.accounts()[0]
        hub.controller.repository.add(Player(name="Solo",
                                             account_id=account.id))
        with client.websocket_connect("/ws") as socket:
            first = socket.receive_text()
            assert hub.clients[0].viewer == "Solo"
            assert "Solo" in first


def test_the_admin_badge_shows_up_and_goes_away(data_path:Path) -> None:
    import asyncio
    with TestClient(create_app(data_path)) as client:
        register(client)
        hub = client.app.state.hub
        with client.websocket_connect("/ws") as socket:
            assert "ADMIN" not in socket.receive_text()
            hub.store.set_admin("Brain", 3600)
            assert "ADMIN" in hub.panels_for(hub.clients[0])
            hub.store.set_admin("Brain", 0)
            assert "ADMIN" not in hub.panels_for(hub.clients[0])


def test_the_admin_badge_toggles_the_powers(data_path:Path) -> None:
    import asyncio
    with TestClient(create_app(data_path)) as client:
        register(client)
        hub = client.app.state.hub
        hub.store.set_admin("Brain", 3600)
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            admin = hub.clients[0]
            assert hub.tools_on(admin) and "admin-badge on" in (
                hub.panels_for(admin))
            socket.send_text('{"action": "admin_powers"}')
            socket.receive_text()
            assert not hub.tools_on(admin)
            assert not hub.controller.is_admin(admin.viewer)
            assert "kerl" not in hub.visible(admin)
            assert "admin-badge ready" in hub.panels_for(admin)
            socket.send_text('{"action": "admin_powers"}')
            socket.receive_text()
            assert hub.tools_on(admin) and "kerl" not in hub.visible(admin)


def test_non_admins_cannot_toggle_powers(data_path:Path) -> None:
    with TestClient(create_app(data_path)) as client:
        register(client)
        hub = client.app.state.hub
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            socket.send_text('{"action": "admin_powers"}')
            assert hub.clients[0].powers
