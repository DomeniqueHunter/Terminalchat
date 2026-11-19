from pathlib import Path

import pytest

from cursed_descent.web import views
from cursed_descent.web.hub import Client, GameHub
from cursed_descent.web.run_panels import VENUE_TITLES


def start_run(hub:GameHub) -> None:
    hub.controller.handle("kerl", "!lobby", now=0.0)
    hub.controller.handle("kerl", "!start", now=1.0)
    hub.controller.session.stage = 8


def open_venue(hub:GameHub, kind:str) -> None:
    start_run(hub)
    hub.controller.session.events.offer_location(kind, 2.0)


def location(hub:GameHub):
    player = hub.controller.repository.load("kerl")
    return views.location_panel(hub.controller, player)


def commands(panel) -> list[str]:
    found = [button.command for button in panel.buttons]
    found += [button.command for row in panel.rows for button in row.buttons]
    for section in panel.sections:
        found += commands(section)
    return found


@pytest.mark.parametrize("kind", sorted(VENUE_TITLES))
def test_every_venue_renders_a_panel_with_leave_or_pass(
        data_path:Path, kind:str) -> None:
    hub = GameHub(data_path)
    open_venue(hub, kind)
    if hub.controller.session.state != "event":
        pytest.skip("venue is not offered at this stage")
    panels = location(hub)
    assert len(panels) == 1
    found = commands(panels[0])
    assert found
    assert any(word in found for word in ("!depart", "!pass")) \
        or kind == "maid"


def test_outside_venue_offers_enter_and_pass(data_path:Path) -> None:
    hub = GameHub(data_path)
    open_venue(hub, "butcher_shop")
    found = commands(location(hub)[0])
    assert "!enter" in found and "!depart" in found
    hub.controller.handle("kerl", "!enter", now=3.0)
    found = commands(location(hub)[0])
    assert any(command.startswith("!buy ") for command in found)


def test_boutique_shows_couture_and_sell_sections(data_path:Path) -> None:
    hub = GameHub(data_path)
    start_run(hub)
    events = hub.controller.session.events
    hub.controller.session.state = "event"
    hub.controller.session.deadline = 2.0
    events.event = {"kind": "boutique", "used": set(), "data": {}}
    events.offer_boutique()
    panel = location(hub)[0]
    titles = [section.title for section in panel.sections]
    assert "Couture for sale" in titles
    assert "!sellself" in commands(panel)


def test_town_panels_return_after_the_run(data_path:Path) -> None:
    hub = GameHub(data_path)
    assert location(hub)
    assert all("Leave" not in p.title for p in location(hub))
