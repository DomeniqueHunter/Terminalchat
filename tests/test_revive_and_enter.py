from pathlib import Path

from cursed_descent.config import CAFE_LOCK, REVIVE_PRICE
from cursed_descent.town_buildings import registry
from cursed_descent.web import views
from cursed_descent.web.hub import GameHub


def kill(hub:GameHub, name:str, gold:int) -> None:
    player = hub.controller.repository.load(name)
    player.records[CAFE_LOCK] = 1
    player.records["respawn_day"] = 99
    player.gold = gold
    hub.controller.repository.save(player)


def test_paying_ends_the_wait(data_path:Path) -> None:
    hub = GameHub(data_path)
    kill(hub, "kerl", REVIVE_PRICE + 10)
    out = hub.controller.handle("kerl", "!endrun pay")
    player = hub.controller.repository.load("kerl")
    assert "among the living" in out[0].text
    assert not player.records.get(CAFE_LOCK) and player.gold == 10


def test_too_poor_keeps_waiting(data_path:Path) -> None:
    hub = GameHub(data_path)
    kill(hub, "kerl", REVIVE_PRICE - 1)
    out = hub.controller.handle("kerl", "!endrun pay")
    player = hub.controller.repository.load("kerl")
    assert "costs" in out[0].text and player.records.get(CAFE_LOCK)
    assert player.gold == REVIVE_PRICE - 1


def test_endrun_names_the_price(data_path:Path) -> None:
    hub = GameHub(data_path)
    kill(hub, "kerl", 0)
    assert "[endrun pay]" in hub.controller.handle("kerl", "!endrun")[0].text


def test_every_building_sets_the_place() -> None:
    places = registry.place_of()
    for key in ("workshop", "lab", "rune_forge", "mine_guild",
                "black_market", "arena"):
        assert places[key] == key


def test_inside_a_building_only_the_building_shows(data_path:Path) -> None:
    hub = GameHub(data_path)
    player = hub.controller.repository.load("kerl")
    hub.controller.handle("kerl", "!bank")
    player = hub.controller.repository.load("kerl")
    panels = views.location_panel(hub.controller, player)
    assert len(panels) == 1 and "Bank" in panels[0].title
    assert panels[0].buttons[-1].label == "← Town"
    hub.controller.handle("kerl", "!town")
    player = hub.controller.repository.load("kerl")
    assert views.location_panel(hub.controller, player)[0].title.startswith(
        "🏘")


def test_inside_the_home_the_town_menu_is_hidden(data_path:Path) -> None:
    from cursed_descent.web import home
    hub = GameHub(data_path)
    player = hub.controller.repository.load("kerl")
    if not home.explicit_home(hub.controller, player):
        player.profile["where"] = "home"
        hub.controller.repository.save(player)
        player = hub.controller.repository.load("kerl")
    if home.explicit_home(hub.controller, player):
        panels = views.location_panel(hub.controller, player)
        assert not any(p.title.startswith("🏘") for p in panels)
