import random

from unittest.mock import MagicMock

from cursed_descent.models import Player
from cursed_descent.party_talk import banter, bonds, party_chat


def pair() -> tuple[Player, Player]:
    return Player(name="Ann", gender="Female"), Player(name="Bob",
                                                       gender="Male")


def test_banter_names_both_and_raises_the_bond() -> None:
    ann, bob = pair()
    reply = banter(ann, bob, "work", random.Random(1))
    assert "Ann" in reply[0].text and "Bob" in reply[0].text
    assert bonds(ann)[bob.id] == 1


def test_party_chat_parses_name_and_topic() -> None:
    ann, bob = pair()
    reply = party_chat(ann, ["bob", "town"], [ann, bob], random.Random(2))
    assert "Bob" in reply[0].text and bonds(ann)[bob.id] == 1


def test_party_chat_rejects_unknown_and_empty() -> None:
    ann, bob = pair()
    assert "Nobody" in party_chat(ann, ["zed"], [ann, bob],
                                  random.Random(3))[0].text
    assert "whom" in party_chat(ann, [], [ann, bob],
                                random.Random(3))[0].text


def test_party_chat_cannot_target_oneself() -> None:
    ann, bob = pair()
    assert "Nobody" in party_chat(ann, ["ann"], [ann, bob],
                                  random.Random(4))[0].text


def sys_module(app):
    import sys
    return sys.modules[type(app).__module__]
