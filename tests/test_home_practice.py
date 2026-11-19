from cursed_descent.houses import home_of
import random
import sys
from unittest.mock import MagicMock

from cursed_descent.controller import GameController
from cursed_descent.home_practice import parse_practice, partner_text
from cursed_descent.towns import START_TOWN
from tests.test_houses import befriend, hit, rich, texts


from tests.test_houses import accepted  # noqa: E402


def setup_house(controller:GameController, gender:str="Female",
                partner_gender:str="Male") -> None:
    rich(controller)
    controller.handle("kerl", "!home buy hut")
    kerl = controller.repository.load("kerl")
    kerl.gender = gender
    controller.repository.save(kerl)
    hero = controller.repository.load("galactica")
    hero.gender = partner_gender
    controller.repository.save(hero)
    accepted(controller, "kerl", "!home invite galactica")


def test_parse_practice_splits_name_act_role_and_options() -> None:
    name, act, role, options, direction = parse_practice(
        ["Lady", "Volena", "oral", "give", "much", "in"])
    assert name == ["Lady", "Volena"] and act == "oral" and role == "give"
    assert options == {"amount": "much", "where": "in"}
    assert parse_practice(["Hilda", "footsmothering", "receive"])[1] == "foot"


def test_partner_text_replaces_the_client() -> None:
    text = partner_text("The client leans back, and the client's hands "
                        "shake.", "Marta")
    assert text == "Marta leans back, and Marta's hands shake."


def test_practice_texts_and_requirements(
        controller:GameController) -> None:
    setup_house(controller)
    reply = texts(hit(controller, "kerl", "!home practice galactica "
                                            "oral give"))
    assert "💞" in reply and "client" not in reply
    assert "Usage" in texts(hit(controller, "kerl", "!home practice galactica oral"))
    reply = texts(hit(controller, "kerl", "!home practice galactica "
                                            "anal give"))
    assert "cannot" in reply


def test_oral_in_feeds_the_swallower(
        controller:GameController) -> None:
    setup_house(controller)
    kerl = controller.repository.load("kerl")
    kerl.needs["hunger"] = 60
    kerl.needs["thirst"] = 60
    controller.repository.save(kerl)
    reply = texts(hit(controller, "kerl", "!home practice galactica "
                                            "oral give much in"))
    assert "fuller" in reply
    kerl = controller.repository.load("kerl")
    assert kerl.needs["hunger"] < 60 and kerl.needs["thirst"] < 60
    kerl.needs["hunger"] = 60
    controller.repository.save(kerl)
    hit(controller, "kerl", "!home practice galactica oral give much on")
    assert controller.repository.load("kerl").needs["hunger"] == 60


def test_watersports_and_scat_feed_the_receiver(
        controller:GameController) -> None:
    setup_house(controller)
    hero = controller.repository.load("galactica")
    hero.needs["thirst"] = 80
    hero.needs["hunger"] = 80
    controller.repository.save(hero)
    hit(controller, "kerl", "!home practice galactica watersports give "
                              "some in")
    hero = controller.repository.load("galactica")
    assert hero.needs["thirst"] < 80
    hit(controller, "kerl", "!home practice galactica scat give some in")
    assert controller.repository.load("galactica").needs["hunger"] < 80


def test_only_vaginal_and_anal_can_lead_to_pregnancy(
        controller:GameController, monkeypatch) -> None:
    from cursed_descent import intimacy
    monkeypatch.setattr(intimacy, "PARTY_PREGNANCY_CHANCE", 1.0)
    setup_house(controller, gender="Shemale", partner_gender="Female")
    for act in ("oral", "footjob", "pegging"):
        hit(controller, "kerl", f"!home practice galactica {act} give "
                                  f"much in")
        assert not controller.repository.load("galactica").pregnant, act
    reply = texts(hit(controller, "kerl", "!home practice galactica "
                                            "vaginal give much in"))
    assert "👶" in reply
    hero = controller.repository.load("galactica")
    assert hero.pregnant == "party"
    kerl = controller.repository.load("kerl")
    home = home_of(kerl, START_TOWN)
    assert hero.id in home["expecting"]


def test_anal_can_impregnate_a_muscular_man_but_not_with_on(
        controller:GameController, monkeypatch) -> None:
    from cursed_descent import intimacy
    monkeypatch.setattr(intimacy, "PARTY_PREGNANCY_CHANCE", 1.0)
    monkeypatch.setattr(intimacy, "MPREG_FACTOR", 1.0)
    setup_house(controller, gender="Shemale", partner_gender="Male")
    hero = controller.repository.load("galactica")
    hero.body["build"] = "Muscular"
    controller.repository.save(hero)
    hit(controller, "kerl", "!home practice galactica anal give much on")
    assert not controller.repository.load("galactica").pregnant
    hit(controller, "kerl", "!home practice galactica anal give much in")
    assert controller.repository.load("galactica").pregnant == "party"


def test_family_relation_adds_dialogue_to_practice(
        controller:GameController) -> None:
    from cursed_descent.town_buildings.family import relations
    setup_house(controller)
    kerl = controller.repository.load("kerl")
    other = controller.repository.load("galactica")
    relations(kerl)[other.id] = {"role": "son", "name": other.name}
    controller.repository.save(kerl)
    reply = texts(hit(controller, "kerl", "!home practice galactica "
                                    "oral give some in"))
    assert "grown" in reply or "Mom" in reply or "locks" in reply


def test_resident_can_practice_with_a_guest_of_the_host(
        controller:GameController) -> None:
    rich(controller)
    controller.handle("kerl", "!home buy row")
    befriend(controller, "galactica", 30)
    accepted(controller, "kerl", "!home movein galactica")
    reply = texts(hit(controller, "galactica", "!home practice Nobody Known oral give some in"))
    assert "Nobody called" in reply


def test_every_build_of_man_can_carry_but_fertility_differs() -> None:
    from cursed_descent.intimacy import fertility
    from cursed_descent.models import Player
    chances = {}
    for build in ("Thin", "Average", "Curvy", "Muscular"):
        man = Player(name="M", id="m", gender="Male", age=30)
        man.body["build"] = build
        chances[build] = fertility(man)
    assert all(value > 0 for value in chances.values())
    assert chances["Thin"] < chances["Average"] < chances["Curvy"]


def test_practice_reports_why_a_partner_cannot_become_pregnant(
        controller:GameController) -> None:
    setup_house(controller, gender="Shemale", partner_gender="None")
    reply = texts(hit(controller, "kerl", "!home practice galactica anal give some in"))
    assert "No chance of pregnancy" in reply or "cannot" in reply


def test_practice_text_refers_to_the_partners_body(
        controller:GameController) -> None:
    setup_house(controller, gender="Female", partner_gender="Shemale")
    hero = controller.repository.load("galactica")
    hero.body["endowment"] = 38
    controller.repository.save(hero)
    reply = texts(hit(controller, "kerl", "!home practice galactica anal receive some in"))
    assert "shemale" in reply and "38 cm" in reply
