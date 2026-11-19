import random

from cursed_descent.config import CAFE_LOCK
from cursed_descent.towns.last_light_humans.cafe.stools import new_stool

from tests.test_cafe import force_death, setup_pair, text


def rich(controller, name:str) -> None:
    player = controller.repository.load(name)
    player.gold = 9000
    controller.repository.save(player)


def test_dead_player_returns_after_one_day(controller) -> None:
    setup_pair(controller)
    force_death(controller, "Kerl", "smothered", "cushion")
    assert controller.repository.load("Kerl").records[CAFE_LOCK]
    controller.town.pass_day()
    kerl = controller.repository.load("Kerl")
    assert not kerl.records[CAFE_LOCK]
    assert "respawn_day" not in kerl.records


def test_sleeping_does_not_move_the_world_clock(controller) -> None:
    setup_pair(controller)
    force_death(controller, "Kerl", "smothered", "cushion")
    rich(controller, "Galactica")
    controller.handle("Galactica", "!room private")
    controller.handle("Galactica", "!room private")
    assert controller.repository.load("Kerl").records[CAFE_LOCK]
    assert controller.town.world.day == 0


def test_endrun_only_reports_the_wait(controller) -> None:
    setup_pair(controller)
    force_death(controller, "Kerl", "smothered", "cushion")
    assert "in about" in text(controller.handle("Kerl", "!endrun"))
    assert controller.repository.load("Kerl").records[CAFE_LOCK]


def test_only_a_collapse_makes_a_stool(controller) -> None:
    setup_pair(controller)
    force_death(controller, "Kerl", "smothered", "cushion")
    assert controller.repository.load("Kerl").npc != "furniture"
    setup_pair(controller)
    force_death(controller, "Kerl", "collapsed", "cushion")
    stool = controller.repository.load("Kerl")
    assert stool.npc == "furniture"
    look = stool.profile["look"]
    assert "kerl" in look.lower() and "hood" not in look and "cm" in look


def test_ransom_hides_no_face(controller) -> None:
    setup_pair(controller)
    force_death(controller, "Kerl", "collapsed", "cushion")
    rich(controller, "Galactica")
    reply = text(controller.handle("Galactica", "!ransom Kerl"))
    assert "hood" not in reply and "free" in reply


def test_ransom_home_makes_a_home_stool(controller) -> None:
    setup_pair(controller)
    force_death(controller, "Kerl", "collapsed", "cushion")
    rich(controller, "Galactica")
    reply = text(controller.handle("Galactica", "!ransom Kerl home"))
    assert "home" in reply
    owner = controller.repository.load("Galactica")
    assert owner.profile["home_stools"] == ["kerl"]
    assert controller.repository.load("Kerl").npc == "furniture"
    assert "kerl" not in text(controller.handle("Galactica", "!ransom")).lower()
    assert "sits down on" in text(controller.handle(
        "Galactica", "!home sit Kerl"))
    assert "free" in text(controller.handle("Galactica", "!home free Kerl"))
    assert controller.repository.load("Kerl").npc == ""


def test_npcs_buy_stools_and_say_where(controller) -> None:
    setup_pair(controller)
    force_death(controller, "Kerl", "collapsed", "cushion")
    sold = controller.repository.load("Kerl")
    sold.profile.pop("kept_gear")
    controller.repository.save(sold)
    controller.town.rng = random.Random(3)
    controller.town.rng.random = lambda: 0.0
    controller.town.pass_day()
    controller.town.pass_day()
    stool = controller.repository.load("Kerl")
    assert stool.profile.get("owner")
    notes = text(controller.town.tick(10.0))
    assert "bought kerl" in notes and "put him in" in notes
    cheap = 45 * stool.level
    assert text(controller.handle("Galactica", "!ransom")).count(
        str(cheap * 2)) == 1


def test_claim_a_ruined_stool(controller) -> None:
    setup_pair(controller)
    controller.town.claims["Galactica"] = new_stool(random.Random(1))
    name = controller.town.claims["Galactica"].name
    rich(controller, "Galactica")
    reply = text(controller.handle("Galactica", "!salvage"))
    assert name in reply
    stool = [npc for npc in controller.repository.npc_players()
             if npc.npc == "furniture"][0]
    assert stool.first_name == name and stool.gender == "Male"
    assert "Nobody" not in text(controller.handle("Galactica", "!ransom"))


def test_own_male_char_becomes_home_stool_with_consent(controller) -> None:
    setup_pair(controller)
    reply = text(controller.handle("Galactica", "!home stool Kerl"))
    assert "asked to kneel" in reply
    assert not controller.repository.load("Kerl").profile.get("stool_of")
    controller.handle("Kerl", "!home yield")
    assert controller.repository.load("Kerl").profile["stool_of"] == (
        "Galactica")
    assert "hold still" in text(controller.handle("Kerl", "!shop"))
    assert "Done being furniture" in text(controller.handle(
        "Kerl", "!safeword"))
    assert not controller.repository.load("Kerl").profile.get("stool_of")
    assert controller.repository.load("Galactica").profile.get(
        "home_stools") == []
