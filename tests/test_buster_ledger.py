import json
import re
import random

import pytest

from cursed_descent.controller import GameController
from cursed_descent.events.maid.ledger import BusterLedger
from tests.test_enter_buildings import texts
from tests.test_maid import offer, start_pair


def volunteer_and_die(controller:GameController) -> None:
    controller.handle("galactica", "!volunteer", now=3.0)
    controller.handle("galactica", "!smack", now=4.0)


def test_a_death_is_written_into_the_ledger(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    start_pair(controller)
    offer(controller)
    monkeypatch.setattr(random, "random", lambda: 0.0)
    volunteer_and_die(controller)
    ledger = controller.session.buster_ledger
    assert ledger.total() == 1 and ledger.fallen() == 1
    assert ledger.entries[0]["name"] == "Galactica"
    assert ledger.entries[0]["hit"] == 1
    assert ledger.entries[0]["result"].startswith("paddle_")


def test_standing_the_hundred_is_written_and_marks_joined(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    start_pair(controller)
    offer(controller)
    monkeypatch.setattr(random, "random", lambda: 0.99)
    controller.handle("galactica", "!volunteer", now=3.0)
    for index in range(10):
        controller.handle("galactica", "!smack", now=4.0 + index)
    ledger = controller.session.buster_ledger
    assert ledger.stood() == 1 and ledger.entries[0]["hit"] == 100
    assert ledger.entries[0]["joined"] is True
    assert ledger.meta["joined"] == 1


def test_ledger_persists_in_a_shared_file(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    start_pair(controller)
    offer(controller)
    monkeypatch.setattr(random, "random", lambda: 0.0)
    volunteer_and_die(controller)
    path = controller.session.buster_ledger.path
    assert path.name == "buster_ledger.json" and path.exists()
    again = BusterLedger(path.parent)
    assert again.total() == 1
    assert json.loads(path.read_text())["entries"][0]["name"] == "Galactica"


def test_history_recites_the_paddle_without_using_a_turn(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    start_pair(controller)
    ledger = controller.session.buster_ledger
    lady = controller.session.member("galactica")
    for index in range(20):
        lady.name = f"Lady{index}"
        ledger.add(lady, "paddle_popped" if index % 2 else "stood",
                   index + 1, "r1")
    lady.name = "Galactica"
    offer(controller)
    reply = texts(controller.handle("galactica", "!history", now=3.0))
    assert "20 ladies" in reply and "many more" in reply
    assert "Lady19" in reply or "Lady" in reply
    shown = len(re.findall(r"Lady\d+", reply))
    assert 1 <= shown <= 10
    assert controller.session.events.event["kind"] == "buster_maid"
    assert "volunteer" in controller.session.events.available()


def test_history_without_victims_says_so(
        controller:GameController) -> None:
    start_pair(controller)
    offer(controller)
    reply = texts(controller.handle("galactica", "!history", now=3.0))
    assert "first" in reply


def test_connie_recognizes_a_returning_lady_and_records_persist(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    start_pair(controller)
    controller.session.buster_ledger.add(
        controller.session.member("galactica"), "paddle_popped", 40, "old")
    offer(controller)
    reply = texts(controller.handle("galactica", "!volunteer", now=3.0))
    assert "40" in reply
    assert controller.session.buster_ledger.best_hit("Galactica") == 40


def test_examine_shows_the_tally(controller:GameController) -> None:
    start_pair(controller)
    lady = controller.session.member("galactica")
    controller.session.buster_ledger.add(lady, "stood", 100, "x")
    offer(controller)
    reply = texts(controller.handle("galactica", "!examine", now=3.0))
    assert "1 ladies" in reply or "1 lady" in reply
