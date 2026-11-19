import random

from cursed_descent.body import DEFAULT_BODY
from cursed_descent.config import GENDERS
from cursed_descent.models import Player
from cursed_descent.town_buildings.brothel.practices import (
    can_do, describe, options_for, parse_choice,
)
from cursed_descent.town_buildings.brothel.practices_content import (
    ACT_LABELS, DOMINANT_ACTS, PRACTICES,
)
from cursed_descent.town_buildings.brothel.practices_extra import (
    EXTRA_LABELS,
)


BODIES = (
    {},
    {"height": 205, "weight": 140, "bust": 900, "butt": 120,
     "muscle": 70, "endowment": 31, "girth": 18, "balls": 11},
    {"height": 150, "weight": 45, "bust": 100, "butt": 80, "muscle": 10,
     "endowment": 6, "girth": 8, "balls": 3},
)


def player(gender:str, changes:dict) -> Player:
    hero = Player(name="Hero", gender=gender)
    hero.body = {**DEFAULT_BODY, **changes}
    return hero


def test_new_acts_are_registered_with_both_roles() -> None:
    assert set(EXTRA_LABELS) <= set(ACT_LABELS) <= set(PRACTICES)
    for act in EXTRA_LABELS:
        assert set(PRACTICES[act]) == {"give", "receive"}
    assert {"pegging", "spanking"} <= set(DOMINANT_ACTS)


def test_every_new_scene_renders_for_every_body() -> None:
    for gender in GENDERS:
        for changes in BODIES:
            hero = player(gender, changes)
            for act, role in options_for(gender, hero.body):
                if act not in EXTRA_LABELS:
                    continue
                for seed in range(20):
                    text = describe(hero, act, role, random.Random(seed))
                    assert text and "{" not in text and "}" not in text


def test_footjob_needs_a_penis_to_receive() -> None:
    for act in ("footjob",):
        assert can_do("Male", act, "receive", DEFAULT_BODY)
        assert not can_do("Female", act, "receive", DEFAULT_BODY)
        assert can_do("Female", act, "give", DEFAULT_BODY)


def test_short_aliases_work() -> None:
    assert parse_choice(["peg", "give"]) == ("pegging", "give")
    assert parse_choice(["spank", "r"]) == ("spanking", "receive")
