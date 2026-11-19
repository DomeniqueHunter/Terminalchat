import random

import pytest

from cursed_descent.config import SWEATERY_CYCLES
from cursed_descent.content import ITEMS
from cursed_descent.controller import GameController
from cursed_descent.locations.sweatery.content import SWEATERY_OPERATORS


def texts(messages) -> str:
    return "\n".join(message.text for message in messages)


def at_sweatery(controller:GameController, operator:str="goblin") -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    controller.session.stage = 8
    events = controller.session.events
    events.offer_location("sweatery", 2.0)
    events.event["data"]["operator"] = operator
    controller.handle("kerl", "!enter", now=3.0)


def test_both_operators_have_the_same_text_keys() -> None:
    goblin, gnome = SWEATERY_OPERATORS["goblin"], SWEATERY_OPERATORS["gnome"]
    assert set(goblin) == set(gnome)


def test_outside_offers_enter_examine_and_pass(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    controller.session.events.offer_location("sweatery", 2.0)
    assert controller.session.events.available() == [
        "enter", "examine", "pass"]
    controller.handle("kerl", "!pass", now=3.0)
    assert controller.session.state != "event"


@pytest.mark.parametrize("operator,word", [("goblin", "Grizzle"),
                                           ("gnome", "Tinkerwick")])
def test_operator_decides_the_texts(
        controller:GameController, operator:str, word:str) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    events = controller.session.events
    events.offer_location("sweatery", 2.0)
    events.event["data"]["operator"] = operator
    assert word not in texts(controller.handle("kerl", "!examine", now=2.5))
    assert word in texts(controller.handle("kerl", "!enter", now=3.0))


def test_the_shelf_holds_the_saved_bottles_with_the_adventurers_name(
        controller:GameController) -> None:
    at_sweatery(controller)
    stock = controller.session.events.sweatery_stock()
    assert len(stock) == 12
    item = ITEMS[stock[0]]
    assert "Beverley Morningwood" in item["name"]
    assert "Beverley Morningwood" in item["note"] and "l'" in item["note"]


def test_a_station_shift_takes_five_cycles_and_pays(
        controller:GameController, monkeypatch) -> None:
    at_sweatery(controller)
    kerl = controller.session.member("kerl")
    gold = kerl.gold
    agility = kerl.stats["agility"]
    reply = texts(controller.handle("kerl", "!sweat run", now=4.0))
    assert "cycle 1/5" in reply
    assert "work" in controller.session.events.available()
    assert "depart" not in controller.session.events.available()
    for number in range(2, SWEATERY_CYCLES + 1):
        reply = texts(controller.handle("kerl", "!work", now=5.0))
        assert f"cycle {number}/5" in reply
    assert "The shift is over" in reply and "+1 agility" in reply
    assert kerl.gold > gold and kerl.stats["agility"] == agility + 1
    assert "depart" in controller.session.events.available()
    ledger = controller.session.sweatery_ledger.entries
    assert ledger[-1]["name"] == "kerl" and ledger[-1]["left"] == 5
    assert ledger[-1]["station"] == "run"
    assert ITEMS[f"sweat_{ledger[-1]['id']}"]["name"].startswith("kerl")


def test_quitting_early_pays_half_and_keeps_fewer_bottles(
        controller:GameController) -> None:
    at_sweatery(controller)
    controller.handle("kerl", "!sweat lift", now=4.0)
    controller.handle("kerl", "!work", now=5.0)
    controller.handle("kerl", "!work", now=6.0)
    reply = texts(controller.handle("kerl", "!quit", now=7.0))
    assert "calls it quits" in reply
    assert controller.session.sweatery_ledger.entries[-1]["left"] == 1
    assert "depart" in controller.session.events.available()


def test_cannot_leave_or_restart_during_a_shift(
        controller:GameController) -> None:
    at_sweatery(controller)
    controller.handle("kerl", "!sweat run", now=4.0)
    assert "Finish your shift" in texts(
        controller.handle("kerl", "!depart", now=5.0))
    assert "already sweating" in texts(
        controller.handle("kerl", "!sweat lift", now=6.0))


def test_work_without_a_shift_is_refused(
        controller:GameController) -> None:
    at_sweatery(controller)
    kerl = controller.session.member("kerl")
    assert "not working here" in texts(
        controller.handle("kerl", "!quit", now=4.0))
    assert kerl.alive


def test_heater_hurts_and_can_roast_the_adventurer(
        controller:GameController, monkeypatch) -> None:
    at_sweatery(controller)
    session = controller.session
    kerl = session.member("kerl")
    kerl.hp = 1
    reply = texts(controller.handle("kerl", "!sweat heat", now=4.0))
    assert session.remains.entries[-1]["fate"] == "heated"
    assert "💀" in reply
    assert session.state != "event"
    assert session.remains.entries[-1]["detail"] == "goblin"


def test_heater_squeals_and_costs_hp(controller:GameController,
                                     monkeypatch) -> None:
    at_sweatery(controller, "gnome")
    kerl = controller.session.member("kerl")
    kerl.hp = 10 ** 6
    monkeypatch.setattr(random, "random", lambda: 0.0)
    kerl_before = kerl.hp
    monkeypatch.setattr(
        "cursed_descent.locations.sweatery.location.SWEATERY_ROAST_BASE", 0)
    monkeypatch.setattr(
        "cursed_descent.locations.sweatery.location.SWEATERY_ROAST_STEP", 0)
    reply = texts(controller.handle("kerl", "!sweat heat", now=4.0))
    assert kerl.hp < kerl_before
    assert "squeal" in reply or "yelps" in reply


def test_roasted_adventurers_are_sold_as_meat_at_a_later_sweatery(
        controller:GameController) -> None:
    at_sweatery(controller)
    session = controller.session
    kerl = session.member("kerl")
    kerl.hp = 1
    controller.handle("kerl", "!sweat heat", now=4.0)
    entry = session.remains.entries[-1]
    assert entry["fate"] == "heated" and entry["location"] == 8
    session.run_id = "other-run"
    session.events.reset()
    session.events.offer_location("sweatery", 10.0)
    session.events.event["data"]["operator"] = "goblin"
    session.stage = 8
    stock = session.events.sweatery_stock()
    assert f"roast_{entry['id']}" in stock
    assert ITEMS[f"roast_{entry['id']}"]["name"] == "Roast kerl"


def test_buying_a_bottle_takes_one_from_the_ledger(
        controller:GameController) -> None:
    at_sweatery(controller)
    session = controller.session
    kerl = session.member("kerl")
    kerl.gold = 1000
    kerl.inventory.clear()
    first = session.events.sweatery_stock()[0]
    entry = next(entry for entry in session.sweatery_ledger.entries
                 if f"sweat_{entry['id']}" == first)
    left = entry["left"]
    reply = texts(controller.handle("kerl", "!buy 1", now=4.0))
    assert "buys" in reply and first in kerl.inventory
    assert entry["left"] == left - 1


def test_ledger_survives_a_restart(data_path) -> None:
    game = GameController(data_path)
    game.handle("kerl", "!lobby", now=0.0)
    game.handle("kerl", "!start", now=1.0)
    game.session.stage = 8
    game.session.events.offer_location("sweatery", 2.0)
    game.handle("kerl", "!enter", now=3.0)
    game.handle("kerl", "!sweat run", now=4.0)
    for _ in range(4):
        game.handle("kerl", "!work", now=5.0)
    count = len(game.session.sweatery_ledger.entries)
    again = GameController(data_path)
    assert len(again.session.sweatery_ledger.entries) == count
    assert f"sweat_{again.session.sweatery_ledger.entries[-1]['id']}" in ITEMS


def test_gnomes_roast_less_and_yield_more_than_goblins() -> None:
    from cursed_descent.config import SWEATERY_OPERATORS as RULES
    assert RULES["gnome"]["roast"] < RULES["goblin"]["roast"]
    assert RULES["gnome"]["yield"] > RULES["goblin"]["yield"]


def test_grill_station_burns_harder_and_roasts_more_than_the_heater(
        controller:GameController, monkeypatch) -> None:
    from cursed_descent.config import SWEATERY_STATIONS
    assert SWEATERY_STATIONS["grill"]["damage"] > SWEATERY_STATIONS[
        "heat"]["damage"]
    assert SWEATERY_STATIONS["grill"]["roast"] > SWEATERY_STATIONS[
        "heat"]["roast"]
    at_sweatery(controller)
    kerl = controller.session.member("kerl")
    kerl.hp = 10 ** 6
    monkeypatch.setattr(random, "random", lambda: 0.99)
    reply = texts(controller.handle("kerl", "!sweat grill", now=4.0))
    assert "grates" in reply and kerl.hp < 10 ** 6


def dress(kerl) -> tuple[str, str, str]:
    from cursed_descent.content import ITEMS
    ids = {slot: next(key for key, value in ITEMS.items()
                      if value.get("slot") == slot)
           for slot in ("chest", "feet", "weapon")}
    for slot, item_id in ids.items():
        kerl.equipment[slot] = item_id
    return ids["chest"], ids["feet"], ids["weapon"]


def test_gear_is_really_taken_off_except_the_boots(
        controller:GameController) -> None:
    at_sweatery(controller)
    kerl = controller.session.member("kerl")
    chest, feet, weapon = dress(kerl)
    controller.handle("kerl", "!sweat lift", now=4.0)
    assert kerl.equipment["chest"] is None
    assert kerl.equipment["weapon"] is None
    assert kerl.equipment["feet"] == feet


def test_gear_comes_back_after_the_shift_and_boots_are_decanted(
        controller:GameController) -> None:
    at_sweatery(controller)
    kerl = controller.session.member("kerl")
    chest, feet, weapon = dress(kerl)
    controller.handle("kerl", "!sweat lift", now=4.0)
    for _ in range(SWEATERY_CYCLES - 1):
        reply = texts(controller.handle("kerl", "!work", now=5.0))
    assert kerl.equipment["chest"] == chest
    assert kerl.equipment["weapon"] == weapon
    assert "gets" in reply and "gear back" in reply
    assert "Boot Sweat" in reply and "jar" in reply
    entry = controller.session.sweatery_ledger.entries[-1]
    assert entry["boots"] and entry["left"] == 1


def test_quitting_returns_the_gear(controller:GameController) -> None:
    at_sweatery(controller)
    kerl = controller.session.member("kerl")
    chest, _, _ = dress(kerl)
    controller.handle("kerl", "!sweat run", now=4.0)
    controller.handle("kerl", "!quit", now=5.0)
    assert kerl.equipment["chest"] == chest
    assert "sweatery_locker" not in kerl.profile or not kerl.profile[
        "sweatery_locker"]


def test_a_stale_locker_is_restored_when_entering(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("kerl", "!start", now=1.0)
    kerl = controller.session.member("kerl")
    chest, _, _ = dress(kerl)
    kerl.profile["sweatery_locker"] = {"chest": chest}
    kerl.equipment["chest"] = None
    controller.session.stage = 8
    controller.session.events.offer_location("sweatery", 2.0)
    controller.handle("kerl", "!enter", now=3.0)
    assert kerl.equipment["chest"] == chest


def test_sweat_smells_like_what_the_character_embodies_most() -> None:
    from cursed_descent.locations.sweatery.location import sweat_identity
    from cursed_descent.models import Player
    cases = [
        (Player(name="a", gender="Male",
                body={"endowment_shape": "Equine"}), "animal"),
        (Player(name="b", gender="Male",
                body={"endowment_shape": "Draconic"}), "sulphurous"),
        (Player(name="c", gender="Male",
                body={"endowment_shape": "Canine"}), "wet-fur"),
        (Player(name="d", gender="Female", body={"bust": 1000}), "milky"),
        (Player(name="e", gender="Male", body={"balls": 12}), "musky"),
        (Player(name="f", gender="Female", body={"muscle": 90}), "iron"),
        (Player(name="g", gender="Female"), "warm and salty"),
    ]
    for player, word in cases:
        smell, taste = sweat_identity(player, "run", "goblin")
        assert word in smell, (player.name, smell)
        assert taste.startswith("bright and salty")


def test_fake_bust_does_not_count_for_the_smell() -> None:
    from cursed_descent.locations.sweatery.location import dominant_feature
    from cursed_descent.models import Player
    real = Player(name="r", gender="Female", body={"bust": 900})
    fake = Player(name="s", gender="Female",
                  body={"bust": 900, "fake": {"bust": 900}})
    assert dominant_feature(real) == "breasts"
    assert dominant_feature(fake) == "plain"


def test_option_line_does_not_list_every_bottle(
        controller:GameController) -> None:
    at_sweatery(controller)
    line = controller.session.events.options_line(
        {"options": "Actions: {options} ({seconds} s)"})
    assert "[buy <nr>]" in line and "[buy 2]" not in line
    assert line.count("[buy") == 1
