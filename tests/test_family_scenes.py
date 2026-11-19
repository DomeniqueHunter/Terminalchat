import random

from cursed_descent.family_scenes import (
    AFTERMATH, OPENERS, family_close, family_open, role_of,
)
from cursed_descent.models import Player
from cursed_descent.town_buildings.family import relations


def make(name:str, gender:str) -> Player:
    player = Player(name=name, id=f"id-{name}", gender=gender, age=40)
    return player


def test_no_relation_means_no_extra_text() -> None:
    mother, son = make("Volena", "Shemale"), make("Karsten", "Male")
    rng = random.Random(1)
    assert family_open(mother, son, rng) == ""
    assert family_close(mother, son, rng) == ""


def test_mother_and_son_get_extra_dialogue() -> None:
    mother, son = make("Volena", "Shemale"), make("Karsten", "Male")
    relations(mother)[son.id] = {"role": "son", "name": son.name}
    rng = random.Random(1)
    assert role_of(mother, son) == "son"
    opener = family_open(mother, son, rng)
    assert "Volena" in opener and "Karsten" in opener
    assert "{" not in opener
    assert "{" not in family_close(mother, son, rng)


def test_every_role_has_both_texts() -> None:
    assert set(OPENERS) == set(AFTERMATH)
