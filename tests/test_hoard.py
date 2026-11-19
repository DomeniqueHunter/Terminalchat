import random

import pytest

from cursed_descent.content import ITEMS
from cursed_descent.controller import GameController
from cursed_descent.hoard import confiscate


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def at_place(controller:GameController, kind:str, stage:int=12) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("galactica", "!join", now=0.5)
    controller.handle("kerl", "!start", now=1.0)
    controller.session.stage = stage
    controller.session.events.offer_location(kind, 2.0)


def weapon() -> str:
    return next(item_id for item_id, item in ITEMS.items()
                if item.get("slot") == "weapon")


def left_behind(controller:GameController, fate:str) -> None:
    controller.session.remains.add(
        name="Lyra", gender="Female", fate=fate, stage=12, killer="x",
        tribe="y", run_id="old-run", hoard=[{"item": weapon(), "state": {}}])


def test_confiscate_moves_items_by_chance(
        controller:GameController) -> None:
    at_place(controller, "wardrobe")
    kerl = controller.session.member("kerl")
    kerl.inventory[:] = [weapon(), weapon()]
    assert confiscate(kerl, 0.0) == [] and len(kerl.inventory) == 2
    taken = confiscate(kerl, 1.0)
    assert [piece["item"] for piece in taken] == [weapon(), weapon()]
    assert kerl.inventory == []


def test_the_wardrobe_can_eat_and_keeps_the_items(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    at_place(controller, "wardrobe")
    kerl = controller.session.member("kerl")
    kerl.inventory[:] = [weapon()]
    monkeypatch.setattr(random, "random", lambda: 0.0)
    reply = texts(controller.handle("kerl", "!open", now=3.0))
    entry = controller.session.remains.entries[-1]
    assert entry["fate"] == "wardrobe" and entry["name"] == kerl.name
    assert [piece["item"] for piece in entry["hoard"]] == [weapon()]
    assert kerl.inventory == [] and "wardrobe" in reply
    assert "keeps" in reply and ITEMS[weapon()]["name"] in reply


def test_the_wardrobe_gives_loot_and_the_earlier_victims_things(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    at_place(controller, "wardrobe")
    left_behind(controller, "wardrobe")
    kerl = controller.session.member("kerl")
    kerl.inventory[:] = []
    monkeypatch.setattr(random, "random", lambda: 0.99)
    reply = texts(controller.handle("kerl", "!open", now=3.0))
    assert "Lyra" in reply and weapon() in kerl.inventory
    assert controller.session.remains.entries[-1]["hoard"] == []


def test_the_wardrobe_examine_hints_at_a_hoard(
        controller:GameController) -> None:
    at_place(controller, "wardrobe")
    assert "left behind" not in texts(
        controller.handle("kerl", "!examine", now=3.0))
    left_behind(controller, "wardrobe")
    assert "Lyra" in texts(controller.handle("kerl", "!examine", now=4.0))


def test_the_throne_gives_a_buff_or_takes_the_sitter(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    at_place(controller, "throne")
    kerl = controller.session.member("kerl")
    monkeypatch.setattr(random, "random", lambda: 0.99)
    reply = texts(controller.handle("kerl", "!claim", now=3.0))
    assert kerl.buffs and "until death" in reply


def test_the_throne_eats_and_leaves_the_things_at_its_foot(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    at_place(controller, "throne")
    kerl = controller.session.member("kerl")
    kerl.inventory[:] = [weapon()]
    monkeypatch.setattr(random, "random", lambda: 0.0)
    texts(controller.handle("kerl", "!claim", now=3.0))
    entry = controller.session.remains.entries[-1]
    assert entry["fate"] == "throne" and entry["hoard"]
    assert kerl.inventory == []


def test_the_throne_lets_you_take_what_lies_at_its_foot(
        controller:GameController) -> None:
    at_place(controller, "throne")
    assert "take" not in controller.session.events.available()
    left_behind(controller, "throne")
    assert "take" in controller.session.events.available()
    kerl = controller.session.member("kerl")
    kerl.inventory[:] = []
    reply = texts(controller.handle("kerl", "!take", now=3.0))
    assert "Lyra" in reply and weapon() in kerl.inventory
    assert "take" not in controller.session.events.available()


def test_a_mimic_couch_keeps_the_victims_items(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    at_place(controller, "couch")
    controller.session.events.event["data"]["mimic"] = True
    kerl = controller.session.member("kerl")
    kerl.inventory[:] = [weapon()]
    monkeypatch.setattr(random, "random", lambda: 0.0)
    texts(controller.handle("kerl", "!rest", now=3.0))
    entry = controller.session.remains.entries[-1]
    assert entry["fate"] == "couch_mimic"
    assert [piece["item"] for piece in entry["hoard"]] == [weapon()]


def test_a_defeated_mimic_gives_the_hoards_of_the_eaten(
        controller:GameController) -> None:
    from cursed_descent.hoard import take_hoards
    at_place(controller, "wardrobe")
    left_behind(controller, "couch_mimic")
    kerl = controller.session.member("kerl")
    kerl.inventory[:] = []
    lines = take_hoards(controller.session.remains, ("couch_mimic",),
                        controller.session.run_id, kerl)
    assert "Lyra" in lines[0] and weapon() in kerl.inventory
