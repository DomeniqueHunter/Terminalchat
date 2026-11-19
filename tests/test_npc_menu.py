import random

from cursed_descent.controller import GameController
from cursed_descent.town_buildings.chat import friendship


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def befriend(controller:GameController, name:str, points:int) -> None:
    kerl = controller.repository.load("kerl")
    npc = controller.repository.load(name)
    npc.profile.setdefault("friends", {})[kerl.id] = points
    controller.repository.save(npc)


def test_gift_raises_friendship_and_uses_up_the_item(
        controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    kerl.inventory[:] = ["bread_loaf"]
    controller.repository.save(kerl)
    reply = texts(controller.handle("kerl", "!gift hilda bread_loaf"))
    kerl = controller.repository.load("kerl")
    hilda = controller.repository.load("hilda")
    assert "smiles" in reply and "bread_loaf" not in kerl.inventory
    assert friendship(hilda, kerl) >= 2


def test_barter_pays_gold(controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    kerl.inventory[:] = ["bread_loaf"]
    kerl.gold = 0
    controller.repository.save(kerl)
    reply = texts(controller.handle("kerl", "!barter hilda bread_loaf"))
    assert "for" in reply
    assert controller.repository.load("kerl").gold > 0


def test_coaching_needs_friendship_gold_and_has_a_limit(
        controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    kerl.gold = 10 ** 6
    controller.repository.save(kerl)
    assert "know you" in texts(controller.handle("kerl", "!coach hilda"))
    befriend(controller, "hilda", 3)
    before = controller.repository.load("kerl").stats["vitality"]
    reply = texts(controller.handle("kerl", "!coach hilda"))
    assert "+1 vitality" in reply
    assert controller.repository.load("kerl").stats["vitality"] == before + 1
    controller.handle("kerl", "!coach hilda")
    controller.handle("kerl", "!coach hilda")
    assert "everything" in texts(controller.handle("kerl", "!coach hilda"))


def test_coaching_costs_gold(controller:GameController) -> None:
    befriend(controller, "hilda", 3)
    kerl = controller.repository.load("kerl")
    kerl.gold = 0
    controller.repository.save(kerl)
    assert "gold" in texts(controller.handle("kerl", "!coach hilda"))


def test_romance_needs_a_close_friend(controller:GameController) -> None:
    assert "Not yet" in texts(controller.handle("kerl", "!romance hilda"))
    befriend(controller, "hilda", 8)
    reply = texts(controller.handle("kerl", "!romance hilda"))
    assert "💞" in reply
    assert friendship(controller.repository.load("hilda"),
                      controller.repository.load("kerl")) >= 10


def test_nobody_is_available_in_the_dungeon(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    assert "dungeon" in texts(controller.handle("kerl", "!coach hilda"))


def test_unknown_neighbour(controller:GameController) -> None:
    assert "Nobody called" in texts(controller.handle("kerl",
                                                      "!coach nobody"))
    assert random.Random(1)
