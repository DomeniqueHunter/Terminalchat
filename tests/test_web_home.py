from pathlib import Path

from cursed_descent.web import home, views
from cursed_descent.web.hub import Client, GameHub


def test_the_town_panel_offers_the_house(data_path:Path) -> None:
    hub = GameHub(data_path)
    player = hub.controller.repository.load("kerl")
    town = views.location_panel(hub.controller, player)[-1]
    assert any(b.command == "!home" for b in town.buttons)


def test_home_panel_shows_house_offers_when_nothing_is_owned(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    hub.controller.handle("kerl", "!home")
    player = hub.controller.repository.load("kerl")
    assert home.explicit_home(hub.controller, player)
    panel = views.location_panel(hub.controller, player)[0]
    assert panel.title == "🏠 Home"
    page = hub.panels_for(Client(None, "kerl"))
    assert "Pick one" in page or "Guests" in page


def test_buying_a_house_unlocks_guests_invite_and_chest(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    player = hub.controller.repository.load("kerl")
    player.gold = 10 ** 7
    hub.controller.repository.save(player)
    hub.controller.handle("kerl", "!home")
    key = next(b.command for s in views.location_panel(
        hub.controller, player)[0].sections for ss in s.sections
        for b in ss.buttons if b.command.startswith("!home buy"))
    hub.controller.handle("kerl", key)
    player = hub.controller.repository.load("kerl")
    panel = views.location_panel(hub.controller, player)[0]
    titles = [section.title for section in panel.sections]
    assert "Guests" in titles and "Invite" in titles
    assert any(t.startswith("📦 Chest") for t in titles)
    assert [b.label for b in panel.buttons][:3] == ["👁 Examine", "🛋 Furnishing",
                                          "Leave"]


def test_home_form_fields_become_commands(data_path:Path) -> None:
    hub = GameHub(data_path)
    send = hub.command_text
    assert send({"text": "!home invite", "guest": "Rose Valmont",
                 "mode": "sub"}) == "!home invite Rose Valmont sub"
    assert send({"text": "!home movein", "guest": "Kai",
                 "mode": "sub"}) == "!home movein Kai"
    assert send({"text": "!home invite", "guest": ""}) == ""
    assert send({"text": "!home invite all",
                 "mode": "domina"}) == "!home invite all domina"
    assert send({"text": "!home store gold", "amount": "50"}
                ) == "!home store gold 50"
    assert send({"text": "!home take gold", "amount": "abc"}) == ""
    assert send({"text": "!home sleep"}) == "!home sleep"


def test_leaving_the_house_returns_to_town(data_path:Path) -> None:
    hub = GameHub(data_path)
    hub.controller.handle("kerl", "!home")
    assert hub.leave_house("kerl") == "!town"
    hub.controller.handle("kerl", "!town")
    player = hub.controller.repository.load("kerl")
    assert not home.explicit_home(hub.controller, player)
