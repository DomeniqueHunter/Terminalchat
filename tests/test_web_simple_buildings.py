from pathlib import Path

from cursed_descent.web import views
from cursed_descent.web.hub import Client, GameHub


def panel(hub:GameHub, name:str, building:str):
    hub.enter_place(name, f"!{building}")
    hub.controller.handle(name, f"!{building}")
    player = hub.controller.repository.load(name)
    return views.location_panel(hub.controller, player)[0]


def test_shop_has_tabbed_wares_sell_and_backpack(data_path:Path) -> None:
    hub = GameHub(data_path)
    shop = panel(hub, "kerl", "shop")
    titles = [section.title for section in shop.sections]
    assert titles[:3] == ["Wares", "Sell from bag", "Pack-maker"]
    wares = shop.sections[0]
    assert wares.tabbed and wares.sections
    page = hub.panels_for(Client(None, "kerl"))
    assert "data-tabs=\"Wares\"" in page and "Buy " in page
    assert "!sell 1" in page or "Sell " in page


def test_smith_is_closed_in_a_run_and_open_otherwise(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    smith = panel(hub, "kerl", "smith")
    assert "Closed during a run." not in smith.lines
    assert smith.sections and smith.sections[0].tabbed


def test_clinic_groups_options_with_price_buttons(data_path:Path) -> None:
    hub = GameHub(data_path)
    clinic = panel(hub, "kerl", "clinic")
    assert clinic.sections
    commands = [b.command for s in clinic.sections for r in s.rows
                for b in r.buttons]
    assert commands and all(c.startswith("!mod ") for c in commands)


def test_station_lists_destinations_with_fares(data_path:Path) -> None:
    hub = GameHub(data_path)
    station = panel(hub, "kerl", "station")
    assert station.buttons
    assert all(b.command.startswith("!travel ") for b in station.buttons
               if b.label != "← Town"
               and not b.command.startswith("!ambient"))


def test_tavern_has_jobs_orders_and_rooms(data_path:Path) -> None:
    hub = GameHub(data_path)
    tavern = panel(hub, "kerl", "tavern")
    names = [section.title for section in tavern.sections]
    assert {"Jobs", "Eat & drink", "Sleep (rooms)"} <= set(names)
