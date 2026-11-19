import random

from cursed_descent.config import INTIMACY_BOND
from cursed_descent.controller import GameController
from cursed_descent.intimacy import (
    fertility, pregnancy_pair, pregnancy_roll,
)
from cursed_descent.models import Player
from cursed_descent.party_talk import bonds

from tests.ready import confirm


def person(name:str, gender:str, build:str="Average") -> Player:
    player = Player(name=name, gender=gender)
    player.body["build"] = build
    return player


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def two_party(controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    other = person("Mira", "Female")
    controller.repository.save(other)
    controller.handle("Mira", "!join", now=0.5)


def test_fertility_by_gender_and_build() -> None:
    assert fertility(person("a", "Female")) > fertility(person("b", "Herm"))
    assert 0 < fertility(person("c", "Male")) < fertility(
        person("d", "Male", "Muscular"))
    assert fertility(person("d", "Male", "Muscular")) > 0
    assert fertility(person("e", "None")) == 0
    carrying = person("f", "Female")
    carrying.pregnant = "party"
    assert fertility(carrying) == 0


def test_a_futa_and_a_man_can_make_a_man_pregnant() -> None:
    futa = person("Fay", "Shemale")
    futa.pregnant = "party"
    man = person("Max", "Male", "Muscular")
    giver, carrier = pregnancy_pair(futa, man, random.Random(1))
    assert giver is futa and carrier is man


def test_two_men_can_conceive_and_one_carries() -> None:
    pair = pregnancy_pair(person("a", "Male"), person("b", "Male"),
                          random.Random(1))
    assert pair is not None and pair[0] is not pair[1]


def test_pregnancy_roll_sets_the_parent(monkeypatch) -> None:
    giver, carrier = person("Gus", "Male"), person("Eva", "Female")
    rng = random.Random(1)
    monkeypatch.setattr(rng, "random", lambda: 0.0)
    pregnancy_roll(giver, carrier, rng)
    assert carrier.pregnant == "party"
    assert carrier.profile["pregnant_by"] == "Gus"


def test_intimacy_is_refused_in_the_dungeon(
        controller:GameController) -> None:
    two_party(controller)
    controller.handle("kerl", "!start", now=1.0)
    confirm(controller, 1.0)
    reply = texts(controller.handle("kerl", "!intimate Mira", now=2.0))
    assert "Not now" in reply


def test_player_must_consent_and_bond_grows(
        controller:GameController) -> None:
    two_party(controller)
    session = controller.session
    ask = texts(controller.handle("kerl", "!intimate Mira", now=2.0))
    assert "consent" in ask and controller.proposals["Mira"] == "kerl"
    reply = texts(controller.handle("Mira", "!consent kerl", now=3.0))
    assert "💞" in reply and "Mira" not in controller.proposals
    kerl, mira = session.member("kerl"), session.member("Mira")
    assert bonds(kerl)[mira.id] == INTIMACY_BOND
    assert bonds(mira)[kerl.id] == INTIMACY_BOND


def test_refusing_clears_the_request(controller:GameController) -> None:
    two_party(controller)
    controller.handle("kerl", "!intimate Mira", now=2.0)
    reply = texts(controller.handle("Mira", "!refuse kerl", now=3.0))
    assert "declines" in reply and not controller.proposals


def test_nobody_asked_means_no_consent(
        controller:GameController) -> None:
    two_party(controller)
    reply = texts(controller.handle("Mira", "!consent kerl", now=3.0))
    assert "not asked" in reply


def test_minors_are_never_available(controller:GameController) -> None:
    two_party(controller)
    controller.session.member("Mira").age = 17
    reply = texts(controller.handle("kerl", "!intimate Mira", now=2.0))
    assert "not available" in reply and not controller.proposals
