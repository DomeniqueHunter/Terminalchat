import random

import pytest

from cursed_descent.controller import GameController
from cursed_descent.formulas import effective_stat


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def at_hole(controller:GameController, gender:str="Male") -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("galactica", "!join", now=0.5)
    controller.handle("kerl", "!start", now=1.0)
    controller.session.stage = 52
    controller.session.member("kerl").gender = gender
    controller.session.events.offer_location("glory_hole", 2.0)


def test_the_hole_has_no_enter_and_offers_thrust_examine_pass(
        controller:GameController) -> None:
    at_hole(controller)
    options = controller.session.events.available()
    assert "enter" not in options and "pass" not in options
    assert options == ["thrust", "examine", "depart"]


def test_nobody_hung_means_only_pass(controller:GameController) -> None:
    at_hole(controller, "Female")
    controller.session.member("galactica").gender = "Female"
    assert controller.session.events.available() == ["examine", "depart"]


def test_relief_gives_a_vitality_buff_until_the_run_ends(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    at_hole(controller)
    kerl = controller.session.member("kerl")
    before = effective_stat(kerl, "vitality")
    monkeypatch.setattr(random, "random", lambda: 0.1)
    reply = texts(controller.handle("kerl", "!thrust", now=3.0))
    assert kerl.buffs == ["glory_relief"]
    assert effective_stat(kerl, "vitality") == before + 2
    assert "until the end of the run" in reply
    assert controller.session.state == "event"


def test_each_figure_may_use_the_hole_once(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    at_hole(controller)
    monkeypatch.setattr(random, "random", lambda: 0.1)
    controller.handle("kerl", "!thrust", now=3.0)
    again = texts(controller.handle("kerl", "!thrust", now=4.0))
    assert "already been here" in again or "That doesn't" in again
    assert len(controller.session.member("kerl").buffs) == 1


def test_the_boon_gives_a_strong_buff_and_an_item(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    at_hole(controller)
    kerl = controller.session.member("kerl")
    kerl.inventory[:] = []
    monkeypatch.setattr(random, "random", lambda: 0.7)
    texts(controller.handle("kerl", "!thrust", now=3.0))
    assert kerl.buffs == ["glory_boon"] and len(kerl.inventory) == 1


def test_the_hole_can_swallow_and_remembers_the_victim(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    at_hole(controller)
    kerl = controller.session.member("kerl")
    monkeypatch.setattr(random, "random", lambda: 0.95)
    texts(controller.handle("kerl", "!thrust", now=3.0))
    entry = controller.session.remains.entries[-1]
    assert not kerl.alive and entry["fate"] == "glory_hole"
    assert entry["name"] == kerl.name


def test_a_later_hole_speaks_with_the_swallowed_voice(
        controller:GameController) -> None:
    at_hole(controller)
    controller.session.remains.add(
        name="Lyra", gender="Female", fate="glory_hole", stage=52,
        killer="the Glory Hole", tribe="corruption", run_id="old-run")
    controller.session.events.offer_location("glory_hole", 5.0)
    assert "Lyra" in texts(controller.handle("kerl", "!examine", now=6.0))


def test_an_anonymous_hole_has_no_name_in_examine(
        controller:GameController) -> None:
    at_hole(controller)
    assert "Scratched" not in texts(
        controller.handle("kerl", "!examine", now=3.0))


def test_the_hole_needs_stage_50(controller:GameController) -> None:
    from cursed_descent.spawns import RULES_BY_KIND
    assert RULES_BY_KIND["glory_hole"].min_stage == 50
