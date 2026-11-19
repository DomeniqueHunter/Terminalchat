import random

from cursed_descent.controller import GameController
from cursed_descent.models import Player
from cursed_descent.party_talk import bonds
from cursed_descent.scenes import (
    AMOUNTS, DEFAULTS, POSITIONS, describe, parse_options, roles,
)


def person(name:str, gender:str) -> Player:
    return Player(name=name, gender=gender)


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def test_options_are_parsed_from_the_end() -> None:
    rest, options = parse_options(["mira", "behind", "bottom", "much",
                                   "on"])
    assert rest == ["mira"]
    assert options == {"position": "behind", "role": "bottom",
                       "amount": "much", "where": "on"}


def test_defaults_apply_and_a_name_is_never_swallowed() -> None:
    rest, options = parse_options(["wall"])
    assert rest == ["wall"] and options == DEFAULTS


def test_every_position_and_amount_has_text() -> None:
    assert len(POSITIONS) >= 6 and set(AMOUNTS) == {"little", "some",
                                                    "much"}
    for key in POSITIONS:
        lines, *_ = describe(person("Gus", "Male"), person("Eva", "Female"),
                             {**DEFAULTS, "position": key},
                             random.Random(1))
        assert "Gus" in " ".join(lines) and "{" not in " ".join(lines)


def test_roles_follow_the_choice_if_possible() -> None:
    man, woman = person("Gus", "Male"), person("Eva", "Female")
    assert roles(man, woman, DEFAULTS) == (man, woman)
    assert roles(woman, man, {**DEFAULTS, "role": "bottom"}) == (man,
                                                                 woman)


def test_the_giver_must_have_the_means() -> None:
    man, woman = person("Gus", "Male"), person("Eva", "Female")
    top, bottom = roles(woman, man, DEFAULTS)
    assert top is man and bottom is woman


def test_two_without_means_get_a_scene_but_no_finish() -> None:
    lines, giver, _, factor = describe(person("Eva", "Female"),
                                       person("Mia", "Female"), DEFAULTS,
                                       random.Random(1))
    assert giver is None and factor == 0 and lines


def test_finishing_on_the_partner_never_conceives() -> None:
    _, giver, _, factor = describe(person("Gus", "Male"),
                                   person("Eva", "Female"),
                                   {**DEFAULTS, "where": "on"},
                                   random.Random(1))
    assert giver is not None and factor == 0


def test_the_amount_scales_the_chance() -> None:
    chances = {}
    for amount in AMOUNTS:
        _, _, _, factor = describe(person("Gus", "Male"),
                                   person("Eva", "Female"),
                                   {**DEFAULTS, "amount": amount},
                                   random.Random(1))
        chances[amount] = factor
    assert chances["little"] < chances["some"] < chances["much"]


def two_party(controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.repository.save(person("Mira", "Female"))
    controller.handle("Mira", "!join", now=0.5)


def test_the_chosen_scene_is_remembered_until_consent(
        controller:GameController) -> None:
    two_party(controller)
    ask = texts(controller.handle("kerl", "!intimate Mira rider bottom "
                                          "much on", now=2.0))
    assert "Riding" in ask and "bottom" in ask
    assert controller.session.proposal_options["Mira"]["where"] == "on"
    reply = texts(controller.handle("Mira", "!consent kerl", now=3.0))
    assert "💞" in reply and "Mira" in reply
    assert "Mira" not in controller.session.proposal_options


def test_refusing_drops_the_chosen_scene(
        controller:GameController) -> None:
    two_party(controller)
    controller.handle("kerl", "!intimate Mira spoon", now=2.0)
    controller.handle("Mira", "!refuse kerl", now=3.0)
    assert not controller.session.proposal_options
    kerl = controller.session.member("kerl")
    assert bonds(kerl) == {}


def test_romance_takes_the_same_options(
        controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    hilda = controller.repository.load("hilda")
    hilda.profile.setdefault("friends", {})[kerl.id] = 8
    controller.repository.save(hilda)
    reply = texts(controller.handle("kerl", "!romance hilda wall bottom "
                                            "little in"))
    assert "💞" in reply and "{" not in reply
