import random

from cursed_descent.content import BUFFS, FATES, ITEMS
from cursed_descent.controller import GameController
from cursed_descent.locations.dairy.location import (
    MENU, can_bull, can_cow, product_id, register_all_dairy,
)
from cursed_descent.spawns import load_rules
from tests.test_enter_buildings import at_location, texts


def entered(controller:GameController) -> None:
    at_location(controller, "dairy")
    controller.handle("kerl", "!enter", now=3.0)


def kerl(controller:GameController):
    return controller.session.member("kerl")


def prep(controller:GameController, gender:str, bust:str="Huge") -> None:
    player = kerl(controller)
    player.gender = gender
    player.body["breasts"] = bust
    player.body["breasts_real"] = bust
    player.age = 25


def test_dairy_is_in_the_location_slot() -> None:
    rule = next(rule for rule in load_rules() if rule.kind == "dairy")
    assert rule.slot == "location"


def test_menu_items_exist() -> None:
    for item_id in MENU:
        assert ITEMS[item_id]["price"] > 0


def test_fates_and_buffs_exist() -> None:
    for fate in ("milked_dry", "bull_stud", "culled"):
        assert fate in FATES
    assert "dairy_stud" in BUFFS


def test_options_list(controller:GameController) -> None:
    entered(controller)
    options = controller.session.events.available()
    for word in ("buy 1", "stint milk", "stint cow", "stint bull", "tour",
                 "sellself", "depart"):
        assert word in options


def test_buying_milk(controller:GameController) -> None:
    entered(controller)
    player = kerl(controller)
    player.gold = 500
    player.inventory.clear()
    reply = texts(controller.handle("kerl", "!buy 1", now=4.0))
    assert "Jug of Fresh Milk" in reply and len(player.inventory) == 1


def test_tour_has_all_steps(controller:GameController) -> None:
    entered(controller)
    first = texts(controller.handle("kerl", "!tour", now=4.0))
    assert "long row" in first
    for index in range(5):
        last = texts(controller.handle("kerl", "!tour", now=5.0 + index))
    assert "That is the tour" in last
    assert "seen the barn" in texts(controller.handle("kerl", "!tour",
                                                      now=12.0))


def test_milk_shift_is_safe_and_pays(controller:GameController) -> None:
    entered(controller)
    player = kerl(controller)
    player.gold = 0
    reply = texts(controller.handle("kerl", "!stint milk", now=4.0))
    assert "finishes the shift" in reply and player.gold > 0
    assert player.alive
    assert "One shift" in texts(controller.handle("kerl", "!stint feed",
                                                  now=5.0))


def test_cow_shift_needs_breasts(controller:GameController) -> None:
    entered(controller)
    prep(controller, "Male", "Flat")
    reply = texts(controller.handle("kerl", "!stint cow", now=4.0))
    assert "no place for you as a cow" in reply
    assert not can_cow(kerl(controller))


def test_bull_shift_needs_penis(controller:GameController) -> None:
    entered(controller)
    prep(controller, "Female")
    reply = texts(controller.handle("kerl", "!stint bull", now=4.0))
    assert "something to offer" in reply
    assert not can_bull(kerl(controller))


def test_cow_shift_ages_a_young_heroine(controller:GameController) -> None:
    random.seed(3)
    entered(controller)
    prep(controller, "Female")
    player = kerl(controller)
    player.stats["vitality"] = 100
    texts(controller.handle("kerl", "!stint cow", now=4.0))
    assert player.age >= 45


def test_cow_collapse_leaves_a_named_product(
        controller:GameController) -> None:
    entered(controller)
    prep(controller, "Female")
    player = kerl(controller)
    player.stats["vitality"] = 1
    player.body["breasts"] = "Huge"
    reply = texts(controller.handle("kerl", "!stint cow", now=4.0))
    entries = [entry for entry in controller.session.remains.entries
               if entry["fate"] == "milked_dry"]
    assert entries and reply
    assert product_id(entries[-1]) in ITEMS


def test_sellself_ineligible_is_refused(controller:GameController) -> None:
    entered(controller)
    prep(controller, "Female", "Small")
    reply = texts(controller.handle("kerl", "!sellself", now=4.0))
    assert "you are a guest" in reply and kerl(controller).alive


def test_sellself_bull_is_a_fate(controller:GameController) -> None:
    entered(controller)
    prep(controller, "Male", "Flat")
    texts(controller.handle("kerl", "!sellself", now=4.0))
    fates = [entry["fate"] for entry in controller.session.remains.entries]
    assert "bull_stud" in fates


def test_named_products_reach_the_shelf(
        controller:GameController) -> None:
    controller.session.remains.add(
        name="Marta", gender="Female", fate="milked_dry", stage=3,
        killer="x", tribe="dairy", run_id="older-run",
        detail="dairy", victim={"level": 12, "build": "Heavy"})
    register_all_dairy(controller.session.remains.entries)
    entered(controller)
    assert "Marta" in texts(controller.handle("kerl", "!examine", now=4.0))
    stock = [ITEMS[item_id]["name"]
             for _, item_id, _ in controller.session.events.venue_stock()]
    assert any("Marta" in name for name in stock)


def test_dairy_is_entered_first(controller:GameController) -> None:
    at_location(controller, "dairy")
    assert controller.session.events.available() == ["enter", "examine",
                                                     "pass"]
    assert "barn" in texts(controller.handle("kerl", "!examine", now=3.0))
    reply = texts(controller.handle("kerl", "!enter", now=3.5))
    assert "Marguerite" in reply
    assert "stint milk" in controller.session.events.available()
