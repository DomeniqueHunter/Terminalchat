import asyncio
from pathlib import Path

from cursed_descent.models import Message
from cursed_descent.towns import START_TOWN, TOWNS
from cursed_descent.web import audience
from cursed_descent.web.hub import Client, GameHub


class Sink:
    def __init__(self) -> None:
        self.sent: list[str] = []

    async def send_text(self, text:str) -> None:
        self.sent.append(text)


def connect(hub:GameHub, viewer:str) -> Client:
    client = Client(Sink(), viewer)
    hub.clients.append(client)
    return client


def test_private_messages_reach_only_the_recipient(data_path:Path) -> None:
    hub = GameHub(data_path)
    found = audience.audience_of(hub.controller, "kerl",
                                 Message("secret", "Galactica"))
    assert found == {"Galactica"}


def test_run_text_goes_to_the_party_only(data_path:Path) -> None:
    hub = GameHub(data_path)
    controller = hub.controller
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("Galactica", "!join", now=1.0)
    controller.handle("kerl", "!start", now=2.0)
    controller.handle("Galactica", "!ready", now=3.0)
    found = audience.audience_of(controller, "", Message("The fight rages."))
    assert found == {"kerl", "Galactica"}


def test_town_text_reaches_people_in_the_same_town(data_path:Path) -> None:
    hub = GameHub(data_path)
    claudia = hub.controller.repository.load("Galactica")
    claudia.profile["town"] = next(key for key in TOWNS
                                   if key != START_TOWN)
    hub.controller.repository.save(claudia)
    found = audience.audience_of(hub.controller, "kerl", Message("Hello."))
    assert "kerl" in found and "Galactica" not in found


def test_each_client_gets_only_its_own_lines(data_path:Path) -> None:
    hub = GameHub(data_path)
    nick = connect(hub, "kerl")
    bev = connect(hub, "Galactica")
    items = audience.private("kerl", [{"text": "for nick", "kind": ""}])
    items += audience.private("Galactica", [{"text": "for bev", "kind": ""}])
    asyncio.run(hub.broadcast(items))
    assert "for nick" in nick.socket.sent[-1]
    assert "for bev" not in nick.socket.sent[-1]
    assert "for bev" in bev.socket.sent[-1]
    assert "for nick" not in bev.socket.sent[-1]


def test_switching_the_slot_replaces_the_log(data_path:Path) -> None:
    hub = GameHub(data_path)
    client = connect(hub, "kerl")
    asyncio.run(hub.broadcast(audience.private(
        "kerl", [{"text": "kerl line", "kind": ""}])))
    asyncio.run(hub.broadcast(audience.private(
        "Galactica", [{"text": "galactica line", "kind": ""}])))
    asyncio.run(hub.handle(client, '{"action": "select", '
                                   '"viewer": "Galactica"}'))
    replaced = client.socket.sent[-1]
    assert 'hx-swap-oob="innerHTML"' in replaced
    assert "galactica line" in replaced and "kerl line" not in replaced


def test_ambient_text_can_be_switched_off_per_client(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    quiet = connect(hub, "kerl")
    loud = connect(hub, "kerl")
    ambient = {"text": "a fly buzzes", "kind": "ambient", "place": "cafe"}
    asyncio.run(hub.broadcast(audience.private("kerl", [ambient])))
    assert "a fly buzzes" in quiet.socket.sent[-1]
    asyncio.run(hub.handle(quiet, '{"action": "cmd", "viewer": "kerl", '
                                  '"text": "!ambient cafe"}'))
    assert "a fly buzzes" not in quiet.socket.sent[-1]
    asyncio.run(hub.broadcast(audience.private("kerl", [ambient])))
    assert "a fly buzzes" not in quiet.socket.sent[-1]
    assert "a fly buzzes" in loud.socket.sent[-1]
    asyncio.run(hub.handle(quiet, '{"action": "cmd", "viewer": "kerl", '
                                  '"text": "!ambient cafe"}'))
    assert "a fly buzzes" in quiet.socket.sent[-1]


def test_the_cafe_panel_offers_the_ambient_switch(data_path:Path) -> None:
    from cursed_descent.web import views
    hub = GameHub(data_path)
    hub.enter_place("kerl", "!cafe")
    hub.controller.handle("kerl", "!cafe")
    player = hub.controller.repository.load("kerl")
    panel = views.location_panel(hub.controller, player)[0]
    assert "!ambient cafe" in [b.command for b in panel.buttons]
    off = views.location_panel(hub.controller, player, frozenset({"cafe"}))
    assert "🔕" in [b.label for b in off[0].buttons][-3]
