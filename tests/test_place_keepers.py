from unittest.mock import MagicMock

import pytest

from cursed_descent.controller import GameController
from cursed_descent.npcs.places import place_residents


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def start(controller:GameController, kind:str, operator:str="") -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    controller.session.stage = 12
    events = controller.session.events
    events.offer_location(kind, 2.0)
    if operator:
        events.event["data"]["operator"] = operator
    controller.handle("kerl", "!enter", now=3.0)


@pytest.mark.parametrize("name", ["Jorveig", "Snik", "Brokk", "Grash"])
def test_every_smokery_person_can_be_talked_to_by_topic(
        controller:GameController, name:str) -> None:
    start(controller, "smokery")
    for topic in ("work", "town", "self"):
        reply = texts(controller.handle("kerl", f"!talk {name} {topic}",
                                        now=4.0))
        assert name in reply and "'" in reply


def test_the_smokery_people_can_be_examined(
        controller:GameController) -> None:
    start(controller, "smokery")
    assert "Nord" in texts(controller.handle("kerl", "!examine Jorveig",
                                             now=4.0))


@pytest.mark.parametrize("operator,name", [("goblin", "Grizzle"),
                                           ("gnome", "Professor Tinkerwick")])
def test_the_sweatery_foreman_matches_the_operator(
        controller:GameController, operator:str, name:str) -> None:
    start(controller, "sweatery", operator)
    reply = texts(controller.handle("kerl", f"!talk {name} work", now=4.0))
    assert name.split()[-1] in reply
    other = "Grizzle" if operator == "gnome" else "Tinkerwick"
    assert "Nobody called" in texts(controller.handle(
        "kerl", f"!talk {other}", now=5.0))


def test_place_residents_follow_the_event() -> None:
    assert [r.key for r in place_residents({"phase": "smokery"})] == [
        "jorveig", "snik", "brokk", "grash"]
    assert place_residents({"phase": "sweatery",
                            "data": {"operator": "gnome"}})[0].key == (
        "tinkerwick")
    assert place_residents({"phase": "couch"}) == []
    assert place_residents({"phase": "brewery"})[0].key == "astrid"

