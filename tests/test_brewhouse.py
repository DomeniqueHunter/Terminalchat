import random

import pytest

from cursed_descent.controller import GameController
from cursed_descent.town_buildings.brewhouse import rules, sisters
from tests.test_houses import texts


def prepare(controller:GameController, weight:float=70.0):
    kerl = controller.repository.load("kerl")
    kerl.profile["town"] = "last_light"
    kerl.inventory = []
    kerl.body["weight"] = weight
    controller.repository.save(kerl)
    return kerl


def run_rounds(controller:GameController, count:int) -> str:
    reply = ""
    for step in range(1, count + 1):
        reply = texts(controller.handle("kerl", "!round", now=float(step)))
    return reply


@pytest.fixture(autouse=True)
def calm(monkeypatch:pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rules, "VORE_CHANCE", 0.0)
    for cfg in sisters.SISTERS.values():
        monkeypatch.setitem(cfg, "boil_chance", 0.0)
    monkeypatch.setattr(rules, "HOT_HURT_CHANCE", 0.0)


def test_bath_undresses_and_gives_a_named_drink(
        controller:GameController) -> None:
    kerl = prepare(controller)
    kerl.equipment["body"] = "leather_vest"
    controller.repository.save(kerl)
    reply = texts(controller.handle("kerl", "!brewhouse 2", now=0.0))
    assert "vat" in reply
    assert controller.repository.load("kerl").equipment.get("body") is None
    reply = run_rounds(controller, 4)
    assert "Shift over" in reply
    kerl = controller.repository.load("kerl")
    assert kerl.equipment.get("body") == "leather_vest"
    assert any(item.startswith("brew_") and "plain" not in item
               for item in kerl.inventory)


def test_heavy_players_are_refused_by_the_sister(
        controller:GameController) -> None:
    prepare(controller, weight=500.0)
    reply = texts(controller.handle("kerl", "!brewhouse 3", now=0.0))
    assert "Shift" not in reply and "kerl" not in controller.town.shifts


def test_vore_shift_grows_the_sister(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rules, "VORE_DEATH_BASE", 0.0)
    prepare(controller, weight=60.0)
    sister = rules.sister_player(controller.town, "last_light")
    before = sister.body["balls"]
    controller.handle("kerl", "!brewhouse 3", now=0.0)
    controller.handle("kerl", "!vat struggle", now=0.5)
    controller.handle("kerl", "!vat struggle", now=0.6)
    reply = run_rounds(controller, 3)
    assert "Shift over" in reply
    sister = rules.sister_player(controller.town, "last_light")
    assert sister.body["balls"] == before + 2


def test_boil_can_kill_and_locks_the_player(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    prepare(controller)
    before = controller.repository.load("kerl").deaths.get("brewed", 0)
    monkeypatch.setattr(rules, "BOIL_DEATH_CHANCE", 1.0)
    monkeypatch.setitem(sisters.SISTERS["last_light"], "boil_chance", 1.0)
    controller.handle("kerl", "!brewhouse 2", now=0.0)
    run_rounds(controller, 1)
    controller.handle("kerl", "!vat endure", now=2.0)
    kerl = controller.repository.load("kerl")
    assert kerl.last_fate == "brewed" and kerl.deaths["brewed"] == before + 1
    reply = texts(controller.handle("kerl", "!shop", now=3.0))
    assert "brewed" in reply and "kerl" not in controller.town.shifts


def test_boil_survivor_gets_a_reduction(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    prepare(controller)
    monkeypatch.setattr(rules, "BOIL_DEATH_CHANCE", 0.0)
    monkeypatch.setitem(sisters.SISTERS["last_light"], "boil_chance", 1.0)
    controller.handle("kerl", "!brewhouse 2", now=0.0)
    run_rounds(controller, 1)
    controller.handle("kerl", "!vat endure", now=2.0)
    kerl = controller.repository.load("kerl")
    assert kerl.hp == 1 and kerl.inventory


def test_commands_are_blocked_inside_the_vat(
        controller:GameController) -> None:
    prepare(controller)
    controller.handle("kerl", "!brewhouse 2", now=0.0)
    reply = texts(controller.handle("kerl", "!shop", now=0.5))
    assert "in the vat" in reply


def test_plain_brew_still_works(controller:GameController) -> None:
    prepare(controller)
    controller.handle("kerl", "!brewhouse 1", now=0.0)
    reply = run_rounds(controller, 4)
    assert "Shift over" in reply
    assert "brew_last_light_plain" in controller.repository.load(
        "kerl").inventory


def test_old_bath_items_still_exist() -> None:
    from cursed_descent.content import ITEMS
    assert ITEMS["brew_last_light_bath_Equine"]["slot"] == "consumable"


def test_service_only_for_heavy_players_and_no_growth(
        controller:GameController) -> None:
    prepare(controller, weight=60.0)
    reply = texts(controller.handle("kerl", "!brewhouse 4", now=0.0))
    assert "slide right in" in reply and "kerl" not in controller.town.shifts
    prepare(controller, weight=500.0)
    sister = rules.sister_player(controller.town, "last_light")
    before = sister.body["balls"]
    controller.handle("kerl", "!brewhouse 4", now=0.0)
    controller.handle("kerl", "!vat deep", now=0.5)
    reply = run_rounds(controller, 3)
    assert "Shift over" in reply
    kerl = controller.repository.load("kerl")
    assert any("Brewmistress Cream" in item or item.startswith("brew_")
               for item in kerl.inventory)
    sister = rules.sister_player(controller.town, "last_light")
    assert sister.body["balls"] == before


def test_vore_can_end_as_a_load(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rules, "VORE_DEATH_BASE", 2.0)
    monkeypatch.setattr(rules, "VORE_DEATH_MAX", 1.0)
    prepare(controller, weight=60.0)
    controller.handle("kerl", "!brewhouse 3", now=0.0)
    run_rounds(controller, 3)
    kerl = controller.repository.load("kerl")
    assert kerl.last_fate == "cummed" and kerl.deaths["cummed"] == 1
    assert not any(item.startswith("brew_") for item in kerl.inventory)
    reply = texts(controller.handle("kerl", "!shop", now=9.0))
    assert "spent as a load" in reply


def test_vat_actions_follow_the_state() -> None:
    state = rules.BrewState(None, "last_light", "warm", "Big")
    assert rules.vat_actions(state) == []
    state.pending = "offer"
    assert [word for _, word in rules.vat_actions(state)] == ["yes", "no"]
    state.pending = "boil"
    assert [word for _, word in rules.vat_actions(state)] == [
        "escape", "endure"]
    state.pending = ""
    state.kind = "vore"
    assert [word for _, word in rules.vat_actions(state)] == [
        "relax", "struggle", "squirm"]
    state.kind = "service"
    assert [word for _, word in rules.vat_actions(state)] == [
        "gentle", "eager", "deep"]


def test_a_bath_always_brings_one_offer(
        controller:GameController) -> None:
    prepare(controller, weight=60.0)
    controller.handle("kerl", "!brewhouse 2", now=0.0)
    run_rounds(controller, 2)
    state = controller.town.shifts["kerl"].client
    assert state.pending == "offer" and state.offered
