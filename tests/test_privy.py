import pytest

from cursed_descent.config import PRIVY_TIP, PRIVY_TOLL
from cursed_descent.controller import GameController
from tests.test_enter_buildings import texts
from tests.test_maid import start_pair


def open_privy(controller:GameController, inside:bool=True):
    start_pair(controller)
    session = controller.session
    session.events.offer_location("privy", 1.0)
    if inside:
        controller.handle("kerl", "!enter", now=2.0)
    return session


def test_the_outside_offers_enter_examine_pass(
        controller:GameController) -> None:
    session = open_privy(controller, inside=False)
    assert session.events.available() == ["enter", "examine", "pass"]
    assert "chalkboard" in texts(controller.handle("kerl", "!examine",
                                                   now=2.0))


def test_inside_the_options_are_the_privy_actions(
        controller:GameController) -> None:
    session = open_privy(controller)
    options = session.events.available()
    for word in ("stall", "wash", "read", "knock", "ask", "tip", "depart",
                 "stint attend", "stint fixture", "grumble"):
        assert word in options


def test_a_stall_costs_the_toll_and_gives_the_buff_once(
        controller:GameController) -> None:
    session = open_privy(controller)
    kerl = session.member("kerl")
    kerl.gold = 100
    reply = texts(controller.handle("kerl", "!stall", now=3.0))
    assert "+2 VIT" in reply
    assert kerl.gold == 100 - PRIVY_TOLL
    again = texts(controller.handle("kerl", "!stall", now=4.0))
    assert "One stall per customer" in again
    assert kerl.gold == 100 - PRIVY_TOLL


def test_a_poor_customer_gets_a_towel_instead(
        controller:GameController) -> None:
    session = open_privy(controller)
    session.member("kerl").gold = 1
    reply = texts(controller.handle("kerl", "!stall", now=3.0))
    assert "towel" in reply and session.member("kerl").gold == 1


def test_washing_resets_sweat_once(controller:GameController) -> None:
    session = open_privy(controller)
    kerl = session.member("kerl")
    kerl.sweat = 80
    controller.handle("kerl", "!wash", now=3.0)
    assert kerl.sweat == 0
    assert "enough" in texts(controller.handle("kerl", "!wash", now=4.0))


def test_tipping_pays_and_tells_a_secret(
        controller:GameController) -> None:
    session = open_privy(controller)
    kerl = session.member("kerl")
    kerl.gold = 50
    reply = texts(controller.handle("kerl", "!tip", now=3.0))
    assert kerl.gold == 50 - PRIVY_TIP and "Hedwig" in reply
    assert "already tipped" in texts(controller.handle("kerl", "!tip",
                                                       now=4.0))


@pytest.mark.parametrize("word", ["read", "knock", "ask"])
def test_reading_knocking_and_asking_keep_the_scene_open(
        controller:GameController, word:str) -> None:
    session = open_privy(controller)
    controller.handle("kerl", f"!{word}", now=3.0)
    assert session.events.event["kind"] == "privy"
    assert "depart" in session.events.available()


def test_the_urinal_is_only_for_hung_genders(
        controller:GameController) -> None:
    from cursed_descent.config import HUNG_GENDERS, PRIVY_URINAL
    session = open_privy(controller)
    kerl = session.member("kerl")
    kerl.gold = 50
    kerl.gender = "Male"
    reply = texts(controller.handle("kerl", "!urinal", now=3.0))
    assert kerl.gold == 50 - PRIVY_URINAL and "Male" in HUNG_GENDERS
    assert "have done that" in texts(controller.handle("kerl", "!urinal",
                                                       now=4.0))
    galactica = session.member("galactica")
    galactica.gender = "Female"
    assert "not for you" in texts(controller.handle("galactica", "!urinal",
                                                    now=5.0))


def test_the_attendant_shift_pays_once(
        controller:GameController) -> None:
    from cursed_descent.config import PRIVY_ATTEND_PAY
    session = open_privy(controller)
    kerl = session.member("kerl")
    kerl.gold = 0
    controller.handle("kerl", "!stint attend", now=3.0)
    assert kerl.gold == PRIVY_ATTEND_PAY
    assert "One shift each" in texts(controller.handle(
        "kerl", "!stint attend", now=4.0))


def test_a_risky_fixture_shift_can_end_in_the_wall(
        controller:GameController,
        monkeypatch:pytest.MonkeyPatch) -> None:
    import random
    session = open_privy(controller)
    monkeypatch.setattr(random, "random", lambda: 0.0)
    for index in range(3):
        controller.handle("kerl", "!stint fixture", now=3.0 + index)
        if not session.member("kerl").alive:
            break
    kerl = session.member("kerl")
    assert not kerl.alive and kerl.last_fate == "fixture"
    assert any(entry["fate"] == "fixture" and entry["name"] == "kerl"
               for entry in session.remains.entries)


def test_grumbling_twice_makes_a_fixture(
        controller:GameController) -> None:
    session = open_privy(controller)
    controller.handle("kerl", "!grumble", now=3.0)
    assert session.member("kerl").alive
    controller.handle("kerl", "!grumble", now=4.0)
    assert session.member("kerl").last_fate == "fixture"


def test_later_visitors_see_the_fixtures_in_examine(
        controller:GameController) -> None:
    session = open_privy(controller)
    controller.handle("kerl", "!grumble", now=3.0)
    controller.handle("kerl", "!grumble", now=4.0)
    reply = texts(controller.handle("galactica", "!examine", now=5.0))
    assert "kerl" in reply
