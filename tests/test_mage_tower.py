import random
from pathlib import Path

import pytest

from cursed_descent.config import (
    BOSS_INTERVAL, CITY_STOP_EVERY, CITY_STOP_FIRST,
)
from cursed_descent.content import ITEMS
from cursed_descent.controller import GameController
from cursed_descent.locations.mage_tower import enchantments as items
from cursed_descent.locations.mage_tower.content import (
    ENCHANT_PRICE, SUPER_PRICE,
)
from cursed_descent.locations.mage_tower.spawn import (
    mage_stage_for, mage_tower_at,
)
from cursed_descent.locations.venues import city_stop_at
from cursed_descent.npcs.places import place_residents


def fits(line:str, reply:str, name:str) -> bool:
    import re
    parts = re.split(r"<<[^>]*>>", line.format(name=name))
    return all(part in reply for part in parts)


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def at_tower(controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    controller.session.stage = 40
    controller.session.events.offer_location("mage_tower", 2.0)
    controller.handle("kerl", "!enter", now=2.5)


def test_one_tower_between_every_two_town_stops() -> None:
    stages = [stage for stage in range(1, 400) if mage_tower_at(stage)]
    assert stages[0] > CITY_STOP_FIRST
    for number, stage in enumerate(stages):
        start = CITY_STOP_FIRST + number * CITY_STOP_EVERY
        assert start < stage < start + CITY_STOP_EVERY
        assert stage % BOSS_INTERVAL and not city_stop_at(stage)
        assert stage == mage_stage_for(number)
    assert len(stages) >= (399 - CITY_STOP_FIRST) // CITY_STOP_EVERY


def test_enchanting_raises_every_value() -> None:
    old = next(item_id for item_id, item in ITEMS.items()
               if item.get("slot") == "weapon" and "damage" in item)
    item, _ = items.build(old, 10, "", random.Random(1))
    assert item["damage"] == ITEMS[old]["damage"] + 10
    for stat in items.STATS:
        assert item["bonus"][stat] == ITEMS[old]["bonus"].get(stat, 0) + 10
    assert ENCHANT_PRICE == 10000 and SUPER_PRICE == 15000
    assert "(Mage's)" in item["name"]


def test_every_effect_changes_the_copy() -> None:
    old = next(item_id for item_id, item in ITEMS.items()
               if item.get("slot") == "weapon")
    rng = random.Random(3)
    soul, _ = items.build(old, 15, "soul_hunger", rng)
    assert soul["soul_hunger"]
    stat, detail = items.build(old, 15, "stat_malus", rng)
    assert stat["bonus"][detail["stat"]] < (
        ITEMS[old]["bonus"].get(detail["stat"], 0) + 15)
    allure, detail = items.build(old, 15, "allure_malus", rng)
    assert allure["allure"] == (
        ITEMS[old].get("allure", 0) + 15 - detail["amount"])


def test_create_replaces_registers_and_persists(tmp_path:Path) -> None:
    class Holder:
        equipment = {"weapon": None}
        inventory = ["dagger"] if "dagger" in ITEMS else []

    old = next(item_id for item_id, item in ITEMS.items()
               if item.get("slot") == "weapon")
    holder = Holder()
    holder.inventory = [old]
    items.setup(tmp_path)
    new_id, _ = items.create(holder, old, 20, "", random.Random(2))
    assert holder.inventory == [new_id] and new_id in ITEMS
    del ITEMS[new_id]
    items.setup(tmp_path)
    assert new_id in ITEMS
    del ITEMS[new_id]
    items.STORE["path"] = None


def test_super_enchanting_costs_gold_and_plays_the_scene(
        controller:GameController) -> None:
    at_tower(controller)
    kerl = controller.session.member("kerl")
    kerl.inventory[:] = [next(item_id for item_id, item in ITEMS.items()
                              if item.get("slot") == "weapon")]
    items.STORE["path"] = None
    kerl.gold = SUPER_PRICE + 7
    options = controller.session.events.available()
    assert "upgrade" in options and "super" in options
    assert "depart" in options
    reply = texts(controller.handle("kerl", "!super 1", now=3.0))
    assert "(Mage's)" in reply and kerl.gold == 7
    assert kerl.inventory[0].startswith("mage_")
    assert "upgrade" in controller.session.events.available()


def test_gold_enchanting_needs_the_gold(
        controller:GameController) -> None:
    at_tower(controller)
    kerl = controller.session.member("kerl")
    weapon = next(item_id for item_id, item in ITEMS.items()
                  if item.get("slot") == "weapon")
    kerl.inventory[:] = [weapon]
    kerl.gold = 10
    assert "gold" in texts(controller.handle("kerl", "!upgrade 1", now=3.0))
    assert kerl.inventory == [weapon]
    kerl.gold = ENCHANT_PRICE + 5
    items.STORE["path"] = None
    reply = texts(controller.handle("kerl", "!upgrade 1", now=4.0))
    assert "(Mage's)" in reply and kerl.gold == 5


def test_potions_and_the_bed(controller:GameController) -> None:
    at_tower(controller)
    kerl = controller.session.member("kerl")
    kerl.gold = 5000
    kerl.inventory.clear()
    texts(controller.handle("kerl", "!potion 1", now=3.0))
    assert kerl.inventory == ["potion_large"]
    kerl.hp = 1
    reply = texts(controller.handle("kerl", "!sleep", now=4.0))
    assert "sleeps" in reply and kerl.hp > 1
    assert "sleep" not in controller.session.events.available()


def test_the_door_comes_first_with_enter_examine_and_pass(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    controller.session.stage = 40
    controller.session.events.offer_location("mage_tower", 2.0)
    events = controller.session.events
    assert events.outside()
    assert events.available() == ["enter", "examine", "pass"]
    assert "bottled lightning" in texts(controller.handle(
        "kerl", "!examine", now=3.0))
    reply = texts(controller.handle("kerl", "!upgrade 1", now=3.5))
    assert "(Mage's)" not in reply
    controller.handle("kerl", "!enter", now=4.0)
    assert not events.outside() and "upgrade" in events.available()


def test_passing_the_door_leaves_the_tower(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    controller.session.stage = 40
    controller.session.events.offer_location("mage_tower", 2.0)
    controller.handle("kerl", "!pass", now=3.0)
    assert controller.session.events.event == {}


def test_an_item_can_be_enchanted_ten_times(
        controller:GameController) -> None:
    at_tower(controller)
    kerl = controller.session.member("kerl")
    weapon = next(item_id for item_id, item in ITEMS.items()
                  if item.get("slot") == "weapon")
    kerl.inventory[:] = [weapon]
    kerl.gold = SUPER_PRICE * 10
    items.STORE["path"] = None
    for step in range(10):
        controller.session.events.event["used"].discard("enchant")
        controller.handle("kerl", "!super 1", now=3.0 + step)
    item = ITEMS[kerl.inventory[0]]
    assert item["mage_level"] == 10 and "(Mage's x10)" in item["name"]
    assert item["name"].count("Mage") == 1
    assert item["bonus"]["strength"] == ITEMS[weapon]["bonus"].get(
        "strength", 0) + 150
    assert kerl.gold == 0


def test_super_enchanting_can_get_the_character_pregnant(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    from cursed_descent.births import add_child
    from cursed_descent.locations.mage_tower.content import MAGE_ID
    from cursed_descent.settings import get
    MAGE_NAME = get("mage_tower")["owner"]
    at_tower(controller)
    kerl = controller.session.member("kerl")
    kerl.gender = "Female"
    kerl.pregnant = ""
    kerl.race = "dwarf"
    kerl.inventory[:] = [next(item_id for item_id, item in ITEMS.items()
                              if item.get("slot") == "weapon")]
    kerl.gold = SUPER_PRICE
    items.STORE["path"] = None
    monkeypatch.setattr(random, "random", lambda: 0.0)
    reply = texts(controller.handle("kerl", "!super 1", now=3.0))
    assert kerl.pregnant == "party" and MAGE_NAME in reply
    assert kerl.profile["pregnant_by_id"] == MAGE_ID
    assert add_child(kerl)["species"] == "human"


def test_a_pregnant_character_is_not_made_pregnant_again(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    at_tower(controller)
    kerl = controller.session.member("kerl")
    kerl.gender = "Female"
    kerl.pregnant = "ogre"
    kerl.inventory[:] = [next(item_id for item_id, item in ITEMS.items()
                              if item.get("slot") == "weapon")]
    kerl.gold = SUPER_PRICE
    items.STORE["path"] = None
    monkeypatch.setattr(random, "random", lambda: 0.0)
    texts(controller.handle("kerl", "!super 1", now=3.0))
    assert kerl.pregnant == "ogre"


def test_plain_enchanting_never_causes_pregnancy(
        controller:GameController, monkeypatch:pytest.MonkeyPatch) -> None:
    at_tower(controller)
    kerl = controller.session.member("kerl")
    kerl.gender = "Female"
    kerl.pregnant = ""
    kerl.inventory[:] = [next(item_id for item_id, item in ITEMS.items()
                              if item.get("slot") == "weapon")]
    kerl.gold = ENCHANT_PRICE
    items.STORE["path"] = None
    monkeypatch.setattr(random, "random", lambda: 0.0)
    texts(controller.handle("kerl", "!upgrade 1", now=3.0))
    assert kerl.pregnant == ""


def test_only_one_enchanting_per_visit(controller:GameController) -> None:
    at_tower(controller)
    kerl = controller.session.member("kerl")
    weapon = next(item_id for item_id, item in ITEMS.items()
                  if item.get("slot") == "weapon")
    kerl.inventory[:] = [weapon]
    kerl.gold = ENCHANT_PRICE * 3
    items.STORE["path"] = None
    texts(controller.handle("kerl", "!upgrade 1", now=3.0))
    gold = kerl.gold
    reply = texts(controller.handle("kerl", "!upgrade 1", now=4.0))
    assert "One working per visit" in reply
    assert kerl.gold == gold
    assert "working per visit" in texts(
        controller.handle("kerl", "!super 1", now=5.0))


def test_the_mage_can_be_examined_and_talked_to(
        controller:GameController) -> None:
    at_tower(controller)
    assert [r.first_name for r in place_residents(
        controller.session.events.event)] == ["Orlen"]
    reply = texts(controller.handle("kerl", "!talk Orlen", now=3.0))
    assert "Orlen" in reply
    reply = texts(controller.handle("kerl", "!examine Orlen", now=4.0))
    assert "robes" in reply


def implanted(controller:GameController, fake:int=600) -> object:
    kerl = controller.session.member("kerl")
    kerl.body["bust"] = 1000
    kerl.body["fake"] = {"bust": fake}
    kerl.gold = 10000
    return kerl


def test_implants_over_half_count(controller:GameController) -> None:
    from cursed_descent.locations.mage_tower.location import implant_parts
    at_tower(controller)
    assert implant_parts(implanted(controller, 600)) == ["bust"]
    assert implant_parts(implanted(controller, 500)) == []


def test_the_mage_mocks_implants_and_offers_real_ones(
        controller:GameController) -> None:
    from cursed_descent.locations.mage_tower.content import MOCK
    at_tower(controller)
    kerl = implanted(controller)
    reply = texts(controller.session.events.enter_mage_tower())
    assert any(fits(line, reply, kerl.name) for line in MOCK["bust"])
    assert "I could make that real" in reply
    assert "real" in controller.session.events.available()


def test_making_implants_real_keeps_the_size(
        controller:GameController) -> None:
    from cursed_descent.body import fake_amount
    at_tower(controller)
    kerl = implanted(controller)
    reply = texts(controller.handle("kerl", "!real bust", now=3.0))
    assert "Honest at last" in reply
    assert kerl.gold == 6000 and kerl.body["bust"] == 1000
    assert fake_amount(kerl.body, "bust") == 0
    assert "Nothing of yours" in texts(
        controller.handle("kerl", "!real bust", now=4.0))


def test_real_implants_the_cheap_way_play_the_scene_with_moans(
        controller:GameController) -> None:
    from cursed_descent.locations.mage_tower.content import (
        MOAN_EARLY, MOAN_MID, MOAN_PEAK,
    )
    at_tower(controller)
    kerl = implanted(controller)
    reply = texts(controller.handle("kerl", "!realsex bust", now=3.0))
    for pool in (MOAN_EARLY, MOAN_MID, MOAN_PEAK):
        assert any(fits(line, reply, kerl.name) for line in pool)
    assert kerl.gold == 8000 and "Honest at last" in reply


def test_making_real_needs_the_gold(controller:GameController) -> None:
    at_tower(controller)
    kerl = implanted(controller)
    kerl.gold = 100
    assert "gold" in texts(controller.handle("kerl", "!real bust", now=3.0))
    assert kerl.body["fake"] == {"bust": 600}
