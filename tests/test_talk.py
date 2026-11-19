from pathlib import Path

from cursed_descent.controller import GameController
from tests.npc_factory import add_merc
from cursed_descent.dungeon import build_enemy
from cursed_descent.content import ENEMIES
from cursed_descent.models import Player
from tests.npc_files import npc_file, npc_keys


def say(controller:GameController, name:str, text:str) -> str:
    return "\n".join(m.text for m in controller.handle(name, text))


def make(tmp_path:Path) -> GameController:
    controller = GameController(tmp_path)
    controller.repository.save(Player(name="Hero", gold=1000))
    return controller


def test_talk_reaches_locals_like_chat(tmp_path:Path) -> None:
    controller = make(tmp_path)
    assert "Hilda" in say(controller, "Hero", "!talk hilda")
    assert "Nobody called 'astrid'" in say(controller, "Hero",
                                           "!talk astrid")


def test_talk_reaches_hired_mercenaries_and_maids(tmp_path:Path) -> None:
    controller = make(tmp_path)
    add_merc(controller, "Brom")
    say(controller, "Hero", "!lobby")
    say(controller, "Hero", "!hire brom")
    assert "Brom" in say(controller, "Hero", "!talk brom")


def test_talk_reaches_the_keeper_of_the_current_place(
        tmp_path:Path) -> None:
    controller = make(tmp_path)
    session = controller.session
    session.state = "event"
    session.party = [controller.repository.load("Hero")]
    session.events.event = {"kind": "brewery", "phase": "brewery",
                            "data": {}, "used": set()}
    assert "Astrid" in say(controller, "Hero", "!talk astrid")
    assert "Nobody" in say(controller, "Hero", "!talk hamhock")


def test_figures_only_taunt_in_a_fight(tmp_path:Path) -> None:
    controller = make(tmp_path)
    session = controller.session
    session.state = "combat"
    session.party = [controller.repository.load("Hero")]
    session.enemies = [build_enemy(1, "safari_hunter",
                                   ENEMIES["safari_hunter"], 5)]
    output = say(controller, "Hero", "!talk reginald")
    assert "doesn't lower the weapon" in output
    npc = controller.repository.load("Sir Reginald")
    assert not npc.profile.get("friends")



def test_starch_and_the_null_master_have_story_files(
        tmp_path:Path) -> None:
    controller = make(tmp_path)
    assert {"miss_prudence", "null"} <= npc_keys(tmp_path, True)
    assert "Prudence" in say(controller, "Hero", "!examine starch")


def test_starch_taunts_in_a_fight_and_the_master_talks_in_his_event(
        tmp_path:Path) -> None:
    controller = make(tmp_path)
    session = controller.session
    session.state = "combat"
    session.party = [controller.repository.load("Hero")]
    session.enemies = [build_enemy(1, "school_recruiter",
                                   ENEMIES["school_recruiter"], 5)]
    assert "doesn't lower the weapon" in say(controller, "Hero",
                                             "!talk starch")
    assert "Starch" in say(controller, "Hero", "!examine starch")
    session.enemies = []
    session.state = "event"
    session.events.event = {"kind": "null_master", "phase": "null",
                            "data": {}, "used": set()}
    assert "Null" in say(controller, "Hero", "!talk null")
