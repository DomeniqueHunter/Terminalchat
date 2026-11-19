from pathlib import Path

from cursed_descent.models import Player
from cursed_descent.web import tabs
from cursed_descent.web.hub import Client, GameHub


def hero(name:str, height:int) -> Player:
    player = Player(name=name)
    player.body["height"] = height
    return player


def test_sizes_are_relative_to_the_body_height() -> None:
    short, tall = tabs.figure_sizes([hero("Pip", 100), hero("Tor", 200)])
    assert abs(tall / short - 2.0) < 1e-9


def test_the_tallest_figure_always_fits() -> None:
    sizes = tabs.figure_sizes([hero("Pip", 100), hero("Giant", 400)])
    assert max(sizes) <= tabs.TALLEST + 1e-9
    assert abs(sizes[1] / sizes[0] - 4.0) < 1e-9


def test_a_lone_hero_keeps_the_normal_scale() -> None:
    assert tabs.figure_sizes([hero("Solo", 170)]) == [150.0]


def test_the_party_tab_shows_one_picture_for_everybody(
        data_path:Path) -> None:
    hub = GameHub(data_path)
    hub.controller.handle("kerl", "!lobby", now=0.0)
    hub.controller.handle("Galactica", "!join", now=1.0)
    page = hub.panels_for(Client(None, "kerl"))
    assert 'class="party-figures"' in page
    assert page.count("kerl</text>") >= 1 and "Galactica</text>" in page
