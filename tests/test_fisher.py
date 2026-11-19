import random

import pytest

from cursed_descent.content import FATES, ITEMS
from cursed_descent.controller import GameController
from cursed_descent.locations.fisher.location import (
    gorm_taste, hook_names, taste_tier,
)
from tests.test_enter_buildings import at_location, texts


def enter(controller:GameController, pair:bool=False) -> None:
    if pair:
        controller.handle("kerl", "!lobby", now=0.0)
        controller.handle("galactica", "!join", now=0.5)
        controller.handle("kerl", "!start", now=1.0)
        controller.session.stage = 8
        controller.session.events.offer_location("fisher", 2.0)
    else:
        at_location(controller, "fisher")
    controller.handle("kerl", "!enter", now=3.0)


def kerl(controller:GameController):
    return controller.session.member("kerl")


def test_outside_offers_enter_examine_pass(
        controller:GameController) -> None:
    at_location(controller, "fisher")
    assert controller.session.events.available() == [
        "enter", "examine", "pass"]


def test_inside_has_cast_bait_lie_and_depart(
        controller:GameController) -> None:
    enter(controller)
    options = controller.session.events.available()
    assert "cast" in options and "lie" in options
    assert "bait kerl" in options and "depart" in options


def test_casting_costs_gold_and_is_limited(
        controller:GameController) -> None:
    enter(controller)
    player = kerl(controller)
    player.gold = 1000
    player.inventory.clear()
    for index in range(3):
        controller.handle("kerl", "!cast", now=4.0 + index)
    assert player.gold == 1000 - 90
    reply = texts(controller.handle("kerl", "!cast", now=9.0))
    assert "enough of you" in reply and player.gold == 910


def test_casting_without_gold_is_refused(
        controller:GameController) -> None:
    enter(controller)
    kerl(controller).gold = 5
    assert "can't pay" in texts(controller.handle("kerl", "!cast", now=4.0))


def test_a_cast_can_give_a_fish(controller:GameController) -> None:
    enter(controller)
    player = kerl(controller)
    player.gold = 100000
    player.inventory.clear()
    random.seed(3)
    for index in range(3):
        controller.handle("kerl", "!cast", now=4.0 + index)
    fish = [item for item in player.inventory if str(item).startswith("fish_")]
    assert all(item in ITEMS for item in fish)


def test_bait_needs_a_confirmation(controller:GameController) -> None:
    enter(controller)
    reply = texts(controller.handle("kerl", "!bait kerl", now=4.0))
    assert "Press Bait again" in reply
    assert kerl(controller).alive


@pytest.mark.parametrize("roll,fate", [(0.1, "fished"), (0.7, "fish_food")])
def test_bait_can_kill_the_bait(controller:GameController, monkeypatch,
                                roll:float, fate:str) -> None:
    enter(controller, pair=True)
    controller.handle("kerl", "!bait galactica", now=4.0)
    monkeypatch.setattr(random, "random", lambda: roll)
    controller.handle("kerl", "!bait galactica", now=5.0)
    assert controller.session.remains.entries[-1]["fate"] == fate
    assert not controller.session.member("galactica").alive


def test_bait_can_survive_with_a_buff(controller:GameController,
                                      monkeypatch) -> None:
    enter(controller)
    controller.handle("kerl", "!bait kerl", now=4.0)
    monkeypatch.setattr(random, "random", lambda: 0.99)
    reply = texts(controller.handle("kerl", "!bait kerl", now=5.0))
    assert "alive" in reply
    assert "fish_survivor" in kerl(controller).buffs


def test_bait_only_once_per_visit(controller:GameController,
                                  monkeypatch) -> None:
    enter(controller)
    controller.handle("kerl", "!bait kerl", now=4.0)
    monkeypatch.setattr(random, "random", lambda: 0.99)
    controller.handle("kerl", "!bait kerl", now=5.0)
    assert "bait kerl" not in controller.session.events.available()


def test_the_caught_fish_feeds_the_survivors(
        controller:GameController, monkeypatch) -> None:
    enter(controller, pair=True)
    session = controller.session
    session.member("kerl").inventory.clear()
    controller.handle("kerl", "!bait galactica", now=4.0)
    monkeypatch.setattr(random, "random", lambda: 0.7)
    reply = texts(controller.handle("kerl", "!bait galactica", now=5.0))
    assert "Giant Catch" in reply
    assert "giant_catch" in session.member("kerl").inventory


def test_fish_fates_exist() -> None:
    assert "fished" in FATES and "fish_food" in FATES


def test_lie_with_gorm_gives_a_fish_and_only_once(
        controller:GameController) -> None:
    enter(controller)
    player = kerl(controller)
    player.inventory.clear()
    reply = texts(controller.handle("kerl", "!lie", now=4.0))
    assert "Gorm" in reply
    assert any(str(item).startswith("fish_") for item in player.inventory)
    assert "lie" not in controller.session.events.available()
    again = texts(controller.handle("kerl", "!lie", now=5.0))
    assert "Invalid" in again or "already" in again or "lie" not in again


def test_a_dom_gets_the_dom_scene(controller:GameController) -> None:
    enter(controller)
    kerl(controller).profile["prefs"] = {"role": "dom"}
    reply = texts(controller.handle("kerl", "!lie", now=4.0))
    assert "Gorm" in reply and ("takes the reins" in reply
                                or "pins Gorm" in reply
                                or "shoves the ogre" in reply
                                or "rides him" in reply
                                or "climbs on top" in reply)


def test_gorm_likes_big_real_bodies() -> None:
    from cursed_descent.models import Player
    assert taste_tier(0) == 0 and taste_tier(2) == 1
    assert taste_tier(3) == 2 and taste_tier(4) == 3


def test_taste_counts_height_butt_balls_and_real(
        controller:GameController) -> None:
    enter(controller)
    player = kerl(controller)
    player.gender = "Male"
    player.body.update({"height": 200, "butt": 120, "balls": 9})
    player.body.pop("fake", None)
    assert gorm_taste(player) == 4
    player.body.update({"height": 150, "butt": 80, "balls": 3})
    assert gorm_taste(player) == 1


def test_fake_parts_are_mocked(controller:GameController) -> None:
    enter(controller)
    player = kerl(controller)
    player.gender = "Male"
    player.body.update({"endowment": 20, "fake": {"endowment": 18}})
    reply = texts(controller.handle("kerl", "!lie", now=4.0))
    assert "Silicone" in reply


def test_hooks_show_earlier_baits(controller:GameController) -> None:
    session = controller.session
    controller.handle("kerl", "!lobby", now=0.0)
    session.remains.add(name="Old Bait", gender="Male", fate="fished",
                        stage=5, killer="x", tribe="fish",
                        run_id="other-run", detail="", location=0,
                        victim={}, char_id="x", hoard=None)
    assert hook_names(session.remains, session.run_id) == ["Old Bait"]


def test_gorm_is_a_talkable_figure(controller:GameController) -> None:
    from cursed_descent.npcs.places import PLACE_KEEPERS
    assert PLACE_KEEPERS["fisher"][0].first_name == "Gorm"


def test_gorm_wants_a_child_and_conceives_more_easily(
        controller:GameController, monkeypatch) -> None:
    from cursed_descent.config import GORM_CONCEPTION_FACTOR
    seen = []
    monkeypatch.setattr(
        "cursed_descent.locations.fisher.location.conception",
        lambda giver, carrier, rng, factor: seen.append(factor) or [])
    enter(controller)
    controller.handle("kerl", "!lie", now=4.0)
    assert seen == [GORM_CONCEPTION_FACTOR] and GORM_CONCEPTION_FACTOR > 1
