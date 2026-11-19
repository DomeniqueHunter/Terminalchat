from pathlib import Path

from cursed_descent.config import LOBBY_OFFLINE_SECONDS, MAX_LOBBIES
from cursed_descent.web import tabs
from cursed_descent.web.hub import GameHub


def make(data_path:Path) -> GameHub:
    hub = GameHub(data_path)
    for name in ("kerl", "galactica", "Gianna Morningwood"):
        player = hub.controller.repository.load(name)
        player.profile["town"] = "last_light"
        hub.controller.repository.save(player)
    hub.controller.online = None
    return hub


def names(controller, name:str) -> list[str]:
    bundle = controller.lobbies.of(name)
    return [member.name for member in bundle.session.party]


def test_two_lobbies_run_side_by_side(data_path:Path) -> None:
    controller = make(data_path).controller
    controller.handle("kerl", "!lobby")
    controller.handle("galactica", "!lobby")
    assert names(controller, "kerl") == ["kerl"]
    assert names(controller, "Galactica") == ["Galactica"]
    out = controller.handle("Gianna Morningwood", "!lobbies")
    assert "kerl" in out[0].text and "Galactica" in out[0].text
    controller.handle("Gianna Morningwood", "!join Galactica")
    assert names(controller, "Gianna Morningwood") == [
        "Galactica", "Gianna Morningwood"]
    assert names(controller, "kerl") == ["kerl"]


def test_join_without_a_name_needs_exactly_one_lobby(
        data_path:Path) -> None:
    controller = make(data_path).controller
    controller.handle("kerl", "!lobby")
    controller.handle("galactica", "!lobby")
    out = controller.handle("Gianna Morningwood", "!join")
    assert "Open lobbies" in out[0].text
    controller.handle("galactica", "!leave")
    controller.handle("Gianna Morningwood", "!join")
    assert names(controller, "Gianna Morningwood") == [
        "kerl", "Gianna Morningwood"]


def test_runs_are_independent(data_path:Path) -> None:
    controller = make(data_path).controller
    controller.handle("kerl", "!lobby")
    controller.handle("galactica", "!lobby")
    controller.handle("kerl", "!start", now=0.0)
    assert controller.lobbies.of("kerl").session.in_run("kerl")
    assert controller.lobbies.of("galactica").session.state == "lobby"
    assert not controller.lobbies.of("galactica").session.in_run("galactica")


def test_the_limit_is_ten_runs(data_path:Path) -> None:
    controller = make(data_path).controller
    for _ in range(MAX_LOBBIES):
        assert controller.lobbies.free_bundle() is not None
        controller.lobbies.free_bundle().session.state = "lobby"
    assert controller.lobbies.free_bundle() is None
    out = controller.handle("kerl", "!lobby")
    assert "run slots are busy" in out[0].text


def test_invite_and_kick(data_path:Path) -> None:
    controller = make(data_path).controller
    controller.handle("kerl", "!lobby")
    out = controller.handle("kerl", "!lobby invite Galactica")
    assert any(m.recipient == "Galactica" and "invites you" in m.text
               for m in out)
    assert controller.lobbies.invites["Galactica"] == "kerl"
    panel = tabs.party_tab(controller, controller.repository.load(
        "Galactica"))
    assert panel["invite"] == "kerl"
    controller.handle("Galactica", "!join")
    assert names(controller, "Galactica") == ["kerl", "Galactica"]
    assert "Galactica" not in controller.lobbies.invites
    controller.handle("kerl", "!kick Galactica")
    assert controller.lobbies.of("Galactica") is None


def test_only_the_leader_invites(data_path:Path) -> None:
    controller = make(data_path).controller
    controller.handle("kerl", "!lobby")
    controller.handle("galactica", "!join")
    out = controller.handle("galactica", "!lobby invite Gianna Morningwood")
    assert "Only the one who opened" in out[0].text


def test_offline_members_leave_after_five_minutes(data_path:Path) -> None:
    controller = make(data_path).controller
    controller.handle("kerl", "!lobby")
    controller.handle("galactica", "!join")
    controller.online = lambda: {"Galactica"}
    controller.tick(now=1000.0)
    assert names(controller, "Galactica") == ["kerl", "Galactica"]
    controller.tick(now=1000.0 + LOBBY_OFFLINE_SECONDS - 1)
    assert controller.lobbies.of("kerl") is not None
    controller.tick(now=1000.0 + LOBBY_OFFLINE_SECONDS + 1)
    assert controller.lobbies.of("kerl") is None
    assert names(controller, "Galactica") == ["Galactica"]


def test_the_next_player_leads_when_the_leader_times_out(
        data_path:Path) -> None:
    controller = make(data_path).controller
    controller.handle("kerl", "!lobby")
    controller.handle("galactica", "!join")
    controller.online = lambda: {"Galactica"}
    controller.tick(now=10.0)
    messages = controller.tick(now=10.0 + LOBBY_OFFLINE_SECONDS + 1)
    assert any("leads the party now" in m.text for m in messages)
    assert names(controller, "Galactica")[0] == "Galactica"


def test_friends_need_confirmation_and_show_online(data_path:Path) -> None:
    controller = make(data_path).controller
    controller.handle("kerl", "!friend Galactica")
    assert not controller.repository.load("kerl").profile.get("friends")
    panels = tabs.friend_panels(
        controller, controller.repository.load("Galactica"))
    assert panels[0].title == "Friend requests"
    controller.handle("Galactica", "!friend accept kerl")
    kerl = controller.repository.load("kerl")
    assert kerl.profile["friends"]
    controller.online = lambda: set()
    panels = tabs.friend_panels(controller, kerl)
    friends = next(p for p in panels if p.title == "Friends")
    assert "offline" in friends.rows[0].text
    controller.handle("kerl", "!lobby")
    controller.online = lambda: {"kerl", "Galactica"}
    friends = next(p for p in tabs.friend_panels(controller, kerl)
                   if p.title == "Friends")
    assert any(b.command == "!lobby invite Galactica"
               for b in friends.rows[0].buttons)
    controller.handle("kerl", "!friend remove Galactica")
    assert not controller.repository.load("kerl").profile["friends"]


def test_the_find_button_opens_the_overlay(data_path:Path) -> None:
    import asyncio
    hub = make(data_path)
    hub.controller.handle("kerl", "!lobby")
    sent = []

    class Socket:
        async def send_text(self, text:str) -> None:
            sent.append(text)

    from cursed_descent.web.hub import Client
    client = Client(Socket(), viewer="Galactica")
    hub.clients.append(client)
    asyncio.run(hub.handle(client, '{"action": "cmd", "text": "!findlobby"}'))
    assert client.find_lobbies
    page = "".join(sent)
    assert 'id="lobby-backdrop"' in page and "kerl's lobby" in page
    assert "!join kerl" in page
    sent.clear()
    asyncio.run(hub.handle(
        client, '{"action": "cmd", "text": "!findlobby close"}'))
    assert not client.find_lobbies
    assert "lobby-backdrop" not in "".join(sent)


def test_the_overlay_explains_why_join_is_blocked(data_path:Path) -> None:
    from cursed_descent.web import tabs
    controller = make(data_path).controller
    controller.handle("kerl", "!lobby")
    galactica = controller.repository.load("Galactica")
    galactica.profile["town"] = "cogsworth"
    controller.repository.save(galactica)
    galactica = controller.repository.load("Galactica")
    card = tabs.lobby_overlay(controller, galactica)["cards"][0]
    assert card["reason"].startswith("Gathers in")
    kerl = controller.repository.load("kerl")
    own = tabs.lobby_overlay(controller, kerl)["cards"][0]
    assert own["own"] and own["is_leader"] and not own["reason"]


def test_whisper_names_list_friends_and_place_mates(data_path:Path) -> None:
    from cursed_descent.web import tabs
    controller = make(data_path).controller
    for name in ("kerl", "galactica", "Gianna Morningwood"):
        player = controller.repository.load(name)
        player.profile["where"] = "town"
        controller.repository.save(player)
    controller.handle("kerl", "!friend Galactica")
    controller.handle("Galactica", "!friend accept kerl")
    kerl = controller.repository.load("kerl")
    found = tabs.whisper_names(controller, kerl)
    assert found[0] == "Galactica" and "Gianna Morningwood" in found
    assert "kerl" not in found
    controller.online = lambda: {"kerl"}
    assert tabs.whisper_names(controller, kerl) == []


def test_shop_and_clinic_open_while_waiting_in_a_lobby(
        data_path:Path) -> None:
    from cursed_descent.web import views
    hub = make(data_path)
    controller = hub.controller
    controller.handle("kerl", "!lobby")
    for word in ("shop", "clinic", "smith"):
        hub.enter_place("kerl", f"!{word}")
        controller.handle("kerl", f"!{word}")
        player = controller.repository.load("kerl")
        assert controller.town.where(player) == word
        assert views.location_panel(controller, player)
        controller.handle("kerl", "!town")
    controller.handle("kerl", "!start", now=0.0)
    hub.enter_place("kerl", "!shop")
    assert controller.town.where(controller.repository.load("kerl")) != "shop"


def test_private_requests_show_accept_and_decline(data_path:Path) -> None:
    import asyncio
    from cursed_descent.web import tabs
    from cursed_descent.web.hub import Client
    hub = make(data_path)
    controller = hub.controller
    controller.handle("kerl", "!lobby")
    controller.handle("Galactica", "!join")
    controller.proposals["Galactica"] = "kerl"
    galactica = controller.repository.load("Galactica")
    assert tabs.private_requests(controller, galactica) == ["kerl"]
    kerl = controller.repository.load("kerl")
    assert tabs.party_tab(controller, kerl)["waiting"] == ["Galactica"]
    sent = []

    class Socket:
        async def send_text(self, text:str) -> None:
            sent.append(text)

    client = Client(Socket(), viewer="Galactica")
    hub.clients.append(client)
    asyncio.run(hub.push(client, hub.panels_for(client)))
    page = "".join(sent)
    assert "!consent kerl" in page and "!refuse kerl" in page
    assert 'id="party-badge"' in page and "●" in page
    controller.proposals.clear()
    assert tabs.private_requests(controller, galactica) == []
