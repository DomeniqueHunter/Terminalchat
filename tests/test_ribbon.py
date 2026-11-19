from types import SimpleNamespace

from cursed_descent.content import BIOMES
from cursed_descent.models import Player
from cursed_descent.web.ribbon import LOOKS, biome_ribbon


def fake_session(stage:int, state:str="combat", inside:bool=True):
    return SimpleNamespace(stage=stage, state=state, run_id="r1",
                           lobby_town="",
                           in_run=lambda name: inside)


def test_every_biome_has_a_look() -> None:
    assert {biome["name"] for biome in BIOMES} <= set(LOOKS)


def test_ribbon_in_a_run() -> None:
    ribbon = biome_ribbon(fake_session(1), Player(name="kerl"))
    assert ribbon.name == "Goblin Warrens"
    assert ribbon.stages == "Stages 1–4" and not ribbon.boss
    assert ribbon.intro


def test_ribbon_marks_boss_stages() -> None:
    assert biome_ribbon(fake_session(10), Player(name="kerl")).boss


def test_no_ribbon_outside_runs() -> None:
    assert biome_ribbon(fake_session(3, inside=False),
                        Player(name="kerl")) is None
    assert biome_ribbon(fake_session(3, state="lobby"),
                        Player(name="kerl")) is None
