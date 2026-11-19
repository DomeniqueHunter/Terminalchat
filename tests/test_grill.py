import random

import pytest

from cursed_descent.content import BUFFS, FATES, ITEMS
from cursed_descent.controller import GameController
from cursed_descent.locations.grill.location import MENU, spit_look
from cursed_descent.spawns import load_rules
from tests.test_enter_buildings import at_location, texts


def kerl(controller:GameController):
    return controller.session.member("kerl")


def add_spit(controller:GameController, name:str, gender:str) -> None:
    controller.session.remains.add(
        name=name, gender=gender, fate="spit_roasted", stage=3,
        killer="x", tribe="grill", run_id="older-run",
        victim={"build": "Muscular"})


def test_grill_is_in_the_location_slot() -> None:
    rule = next(rule for rule in load_rules() if rule.kind == "grill")
    assert rule.slot == "location"


def test_menu_items_exist_and_heal() -> None:
    for item_id in MENU:
        assert ITEMS[item_id]["slot"] == "consumable"
        assert ITEMS[item_id]["heal"] > 0 and ITEMS[item_id]["price"] > 0


def test_options_have_menu_special_ask_complain(
        controller:GameController) -> None:
    at_location(controller, "grill")
    options = controller.session.events.available()
    for word in ("buy 1", "buy 4", "special", "ask", "grumble", "depart"):
        assert word in options


def test_buying_a_kebab_costs_gold(controller:GameController) -> None:
    at_location(controller, "grill")
    player = kerl(controller)
    player.gold = 500
    player.inventory.clear()
    reply = texts(controller.handle("kerl", "!buy 3", now=4.0))
    assert "Kebab in Flatbread" in reply
    assert 470 <= player.gold < 500 and len(player.inventory) == 1


def test_special_with_an_empty_spit_is_plain(
        controller:GameController) -> None:
    at_location(controller, "grill")
    player = kerl(controller)
    player.gold = 1000
    reply = texts(controller.handle("kerl", "!special", now=4.0))
    assert "only a good chicken" in reply and player.gold == 750
    assert "grill_plain" in " ".join(player.buffs)
    assert "one special" in texts(controller.handle("kerl", "!special",
                                                    now=5.0))


def test_special_eats_a_fallen_hero_from_an_earlier_run(
        controller:GameController) -> None:
    at_location(controller, "grill")
    add_spit(controller, "Tobias", "Male")
    player = kerl(controller)
    player.gold = 1000
    assert "Tobias" in texts(controller.handle("kerl", "!examine",
                                               now=3.5))
    reply = texts(controller.handle("kerl", "!special", now=4.0))
    assert "Today's special: Tobias" in reply
    assert "grill_special" in " ".join(player.buffs)
    assert "Tobias" not in texts(controller.handle("kerl", "!examine",
                                                   now=5.0)).split(
        "chalked")[0].split("spit:")[-1]


def test_asking_is_limited_to_once(controller:GameController,
                                   monkeypatch:pytest.MonkeyPatch) -> None:
    at_location(controller, "grill")
    monkeypatch.setattr(random, "random", lambda: 0.1)
    assert texts(controller.handle("kerl", "!ask", now=4.0))
    assert "asked enough" in texts(controller.handle("kerl", "!ask",
                                                     now=5.0))


def test_second_complaint_puts_you_on_the_spit(
        controller:GameController) -> None:
    controller.handle("kerl", "!lobby", now=0.0)
    controller.handle("galactica", "!join", now=0.5)
    controller.handle("kerl", "!start", now=1.0)
    controller.session.stage = 8
    controller.session.events.offer_location("grill", 2.0)
    assert "not hear it again" in texts(controller.handle(
        "kerl", "!grumble", now=4.0))
    assert kerl(controller).alive
    reply = texts(controller.handle("kerl", "!grumble", now=5.0))
    assert "warned you" in reply
    assert not kerl(controller).alive
    entry = controller.session.remains.entries[-1]
    assert entry["fate"] == "spit_roasted"


@pytest.mark.parametrize("gender", ["Male", "Female", "Herm", "Shemale",
                                    "Transgender"])
def test_each_gender_has_its_own_fate_and_spit_text(gender:str) -> None:
    assert FATES["spit_roasted"][gender]
    entry = {"name": "Probe", "gender": gender,
             "victim": {"build": "Heavy"}}
    assert "Probe" in spit_look(entry) and "{" not in spit_look(entry)


def test_buffs_are_registered() -> None:
    assert "grill_special" in BUFFS and "grill_plain" in BUFFS
