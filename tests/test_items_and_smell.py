import json

from cursed_descent.controller import GameController
from cursed_descent.items import (
    Item, as_item, item_from_json, item_state, item_to_json, remove_item,
    restore_item,
)
from cursed_descent.inventory import sort_inventory
from cursed_descent.models import Player
from cursed_descent.remains import RemainsLog
from cursed_descent.scent import scent_tier
from cursed_descent.smell import (
    absorb_gear, foreign_smell, foreign_tier, smell_note,
)
from cursed_descent.locations.shop.location import item_description


def worn_hero(item:str="high_heels") -> Player:
    hero = Player(name="Hero", first_name="Hero", last_name="One")
    hero.equipment["feet"] = item
    return hero


def test_item_behaves_like_its_template_id() -> None:
    item = Item("potion_small", soak=3)
    assert item == "potion_small" and hash(item) == hash("potion_small")
    assert item in {"potion_small"} and f"{item}" == "potion_small"


def test_plain_items_serialize_as_strings() -> None:
    assert item_to_json("potion_small") == "potion_small"
    assert item_to_json(Item("potion_small")) == "potion_small"
    assert type(item_to_json(Item("potion_small"))) is str


def test_state_roundtrips_through_json() -> None:
    item = Item("high_heels", {"a": {"name": "A", "strength": 9}}, 2)
    clone = item_from_json(json.loads(json.dumps(item_to_json(item))))
    assert isinstance(clone, Item)
    assert clone.traces == item.traces and clone.soak == 2


def test_item_state_helpers() -> None:
    item = Item("high_heels", soak=1)
    assert item_state("high_heels") == {}
    restored = restore_item("high_heels", item_state(item))
    assert restored.soak == 1 and restore_item("high_heels", {}) == "high_heels"


def test_remove_item_removes_the_exact_instance() -> None:
    clean, smelly = Item("high_heels"), Item("high_heels", soak=5)
    bag = [clean, smelly]
    remove_item(bag, smelly)
    assert len(bag) == 1 and bag[0] is clean


def test_remove_item_falls_back_to_equality() -> None:
    bag = ["high_heels", "potion_small"]
    remove_item(bag, "high_heels")
    assert bag == ["potion_small"]


def test_gear_absorbs_the_wearers_smell() -> None:
    hero = worn_hero()
    for _ in range(10):
        absorb_gear(hero)
    boots = hero.equipment["feet"]
    assert isinstance(boots, Item)
    assert boots.traces[hero.id]["strength"] == 10
    assert boots.traces[hero.id]["name"] == "Hero One"


def test_sweaty_wearer_soaks_gear_faster() -> None:
    dry, sweaty = worn_hero(), worn_hero()
    sweaty.sweat = 50
    absorb_gear(dry)
    absorb_gear(sweaty)
    assert (sweaty.equipment["feet"].traces[sweaty.id]["strength"]
            > dry.equipment["feet"].traces[dry.id]["strength"])
    assert sweaty.equipment["feet"].soak > 0


def test_smell_is_capped() -> None:
    hero = worn_hero()
    for _ in range(500):
        absorb_gear(hero)
    assert hero.equipment["feet"].traces[hero.id]["strength"] == 60


def test_own_smell_is_not_foreign() -> None:
    hero = worn_hero()
    for _ in range(50):
        absorb_gear(hero)
    assert foreign_smell(hero) == 0 and foreign_tier(hero) == 0


def test_borrowed_gear_changes_the_wearers_scent() -> None:
    owner, borrower = worn_hero(), Player(name="Other")
    for _ in range(45):
        absorb_gear(owner)
    borrower.equipment["feet"] = owner.equipment["feet"]
    assert foreign_tier(borrower) >= 2
    assert scent_tier(borrower) == foreign_tier(borrower)
    assert scent_tier(Player(name="Clean")) == 0


def test_smell_note_names_the_source() -> None:
    hero = worn_hero()
    assert smell_note(hero.equipment["feet"]) == ""
    for _ in range(25):
        absorb_gear(hero)
    assert "Hero One" in smell_note(hero.equipment["feet"])
    assert "Hero One" in item_description(hero.equipment["feet"])
    assert smell_note("high_heels") == ""


def test_player_save_keeps_item_state() -> None:
    hero = worn_hero()
    for _ in range(12):
        absorb_gear(hero)
    hero.inventory.append(Item("potion_small", soak=1))
    clone = Player.from_dict(json.loads(json.dumps(hero.to_dict())))
    assert clone.equipment["feet"].traces[hero.id]["strength"] == 12
    assert clone.inventory[-1].soak == 1


def test_remains_keep_the_state_of_a_dropped_item(empty_data_path) -> None:
    hero = worn_hero()
    for _ in range(12):
        absorb_gear(hero)
    log = RemainsLog(empty_data_path)
    log.add(name="Hero", gender="Male", fate="eaten", stage=3, killer="x",
            tribe="monsters", run_id="r1", char_id=hero.id)
    log.attach_item("Hero", "r1", hero.equipment["feet"], hero.id)
    reloaded = RemainsLog(empty_data_path)
    looted = reloaded.loot(reloaded.entries[0])
    assert isinstance(looted, Item)
    assert looted.traces[hero.id]["strength"] == 12


def test_give_moves_the_item_with_its_smell(
        controller:GameController) -> None:
    giver = controller.repository.load("kerl")
    receiver = controller.repository.load("galactica")
    boots = as_item("high_heels")
    for _ in range(25):
        absorb_gear(_wearing(giver, boots))
    giver.equipment["feet"] = None
    giver.inventory.append(boots)
    sort_inventory(giver)
    number = next(index for index, item in enumerate(giver.inventory, 1)
                  if item is boots)
    before = len(receiver.inventory)
    messages = controller.handle("kerl", f"!give {number} galactica")
    assert "gives" in messages[0].text and "kerl" in messages[0].text
    received = next(item for item in receiver.inventory
                    if getattr(item, "traces", None))
    assert received.traces == boots.traces
    assert len(receiver.inventory) == before + 1


def _wearing(player:Player, item:Item) -> Player:
    player.equipment["feet"] = item
    return player


def test_give_needs_a_valid_target_and_item(
        controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    kerl.inventory.append("potion_small")
    assert "nobody" in controller.handle("kerl", "!give 1 nobody")[0].text
    assert "Usage" in controller.handle("kerl", "!give")[0].text
    assert "No such item" in controller.handle(
        "kerl", "!give 99 galactica")[0].text


def test_give_is_blocked_between_run_and_non_run(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby")
    controller.handle("kerl", "!start", now=0.0)
    controller.repository.load("kerl").inventory.append("potion_small")
    text = controller.handle("kerl", "!give 1 galactica")[0].text
    assert "same situation" in text


def test_clearing_a_stage_soaks_worn_gear(controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    kerl.equipment["feet"] = "high_heels"
    controller.session.open_lobby(kerl)
    controller.session.start("kerl", 0.0)
    controller.session.enemies.clear()
    controller.session.clear_stage(1.0)
    assert kerl.equipment["feet"].traces[kerl.id]["strength"] >= 1
