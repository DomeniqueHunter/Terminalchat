import json
import random
from pathlib import Path

from fastapi.testclient import TestClient

from cursed_descent.web.app import create_app
from tests.test_create_form import form
from tests.test_web_auth import register


HERO = "Lyra Dawn"
STEP_LIMIT = 600


def way_out(options:list[str]) -> str:
    return next((word for word in ("pass", "depart", "leave")
                 if word in options), options[0])


def send(socket, hero:str, text:str) -> str:
    socket.send_text(json.dumps({"action": "cmd", "text": text,
                                 "viewer": hero}))
    return socket.receive_text()


def test_a_new_player_from_registration_to_the_first_run(
        tmp_path:Path) -> None:
    random.seed(11)
    with TestClient(create_app(tmp_path)) as client:
        register(client)
        hub = client.app.state.hub
        with client.websocket_connect("/ws") as socket:
            first = socket.receive_text()
            assert "No character selected" in first or "Lyra" not in first

            socket.send_text(json.dumps({"action": "create_submit",
                                         **form()}))
            assert 'data-done="1"' in socket.receive_text()
            assert hub.clients[0].viewer == HERO

            send(socket, HERO, "!lobby")
            send(socket, HERO, "!start")
            controller = hub.controller
            assert controller.session.in_run(HERO)
            assert controller.session.state in (
                "combat", "chest", "remains", "event")

            steps = 0
            for steps in range(STEP_LIMIT):
                session = controller.session
                if not session.in_run(HERO):
                    break
                if session.state == "event":
                    command = f"!{way_out(session.available_commands())}"
                elif session.state == "combat":
                    command = "!hit"
                else:
                    command = "!open" if session.state == "chest" else (
                        "!leave")
                controller.handle(HERO, command)
            assert steps < STEP_LIMIT - 1, (controller.session.state, controller.session.stage, controller.session.events.event, command)
            hero = controller.repository.load(HERO)
            assert hero.records["runs"] == 1
            assert hero.records["deepest_stage"] >= 1
            assert controller.session.state == "idle"

            panels = hub.panels_for(hub.clients[0])
            assert HERO in panels and "Traceback" not in panels

        client.post("/logout")
        login = client.post("/login", data={
            "name": "Brain", "password": "longpassword"},
            follow_redirects=False)
        assert login.status_code == 303
        with client.websocket_connect("/ws") as socket:
            again = socket.receive_text()
            assert hub.clients[0].viewer == HERO and HERO in again
