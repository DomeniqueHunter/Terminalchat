from pathlib import Path

from cursed_descent.web import views
from cursed_descent.web.hub import GameHub
from cursed_descent.web.trade import trade_text


def test_town_panel_lists_neighbours_with_actions(data_path:Path) -> None:
    hub = GameHub(data_path)
    player = hub.controller.repository.load("kerl")
    town = views.location_panel(hub.controller, player)[-1]
    neighbours = [s for s in town.sections if s.title == "Neighbours"]
    assert neighbours and neighbours[0].choices[0].name == "trade_item"
    labels = [b.label for b in neighbours[0].sections[0].buttons]
    assert labels == ["Gift", "Barter", "Coach", "Romance"]


def test_gift_and_barter_need_an_item_number() -> None:
    assert trade_text("!gift mara", {"trade_item": "2"}) == "!gift mara 2"
    assert trade_text("!barter mara", {}) == ""
    assert trade_text("!coach mara", {}) == "!coach mara"


def test_romance_uses_scene_fields_or_defaults() -> None:
    assert trade_text("!romance mara", {}) == "!romance mara face top some in"
    data = {"s_position": "back", "s_role": "bottom"}
    assert trade_text("!romance mara", data) == \
        "!romance mara back bottom some in"


def test_hub_builds_the_gift_command(data_path:Path) -> None:
    hub = GameHub(data_path)
    data = {"text": "!gift mara", "trade_item": "1"}
    assert hub.command_text(data) == "!gift mara 1"
