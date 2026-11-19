import random

import pytest

from cursed_descent.content import FATES, ITEMS
from cursed_descent.controller import GameController
from cursed_descent.locations.farm.location import (
    cum_factor, cum_scent, farm_job,
)
from cursed_descent.sweat import sweat_tier
from tests.test_enter_buildings import at_location, texts


def hang(controller:GameController, gender:str="Male", balls:int=5,
         shape:str="Human"):
    if controller.session.member("kerl") is None:
        controller.handle("kerl", "!lobby", now=0.0)
        controller.handle("kerl", "!start", now=1.0)
    player = controller.session.member("kerl")
    player.gender = gender
    player.body["balls"] = balls
    player.body["endowment_shape"] = shape
    return player


def enter_farm(controller:GameController) -> None:
    at_location(controller, "farm")
    controller.handle("kerl", "!enter", now=3.0)


def test_the_cum_cow_is_an_extra_work_button(
        controller:GameController) -> None:
    enter_farm(controller)
    options = controller.session.events.available()
    assert "work cumcow" in options and "work cow" in options


def test_only_hung_genders_can_work_as_cum_cow(
        controller:GameController) -> None:
    enter_farm(controller)
    hang(controller, gender="Female")
    reply = texts(controller.handle("kerl", "!work cumcow", now=4.0))
    assert "Nothing to pump" in reply
    assert "kerl" not in controller.session.events.shifts()


@pytest.mark.parametrize("gender", ["Male", "Herm", "Shemale"])
def test_hung_genders_start_the_cum_cow_shift(
        controller:GameController, gender:str) -> None:
    enter_farm(controller)
    hang(controller, gender=gender)
    reply = texts(controller.handle("kerl", "!work cumcow", now=4.0))
    assert "milking stall" in reply and "bucket" in reply
    assert controller.session.events.shifts()["kerl"]["job"] == "cum"


def test_a_cum_cow_turn_names_the_smell_of_the_stall(
        controller:GameController) -> None:
    enter_farm(controller)
    hang(controller)
    controller.handle("kerl", "!work cumcow", now=4.0)
    reply = texts(controller.handle("kerl", "!work", now=5.0))
    assert "shift turn 1" in reply
    from cursed_descent.locations.farm.content import CUM_SCENTS
    assert any(line.split("{name}")[0] and line.split("{name}")[0] in reply
               or line.split("{name}")[-1][:12] in reply
               for line in CUM_SCENTS[""])


@pytest.mark.parametrize("balls,expected", [
    (2, 0.5), (5, 1.0), (8, 2.0), (12, 3.0), (6.5, 1.5), (10, 2.5)])
def test_the_yield_grows_with_the_balls(
        controller:GameController, balls:float, expected:float) -> None:
    player = hang(controller, balls=balls)
    assert cum_factor(player) == pytest.approx(expected)


def test_equine_gives_one_and_a_half_times_the_yield(
        controller:GameController) -> None:
    human = cum_factor(hang(controller, balls=8))
    equine = cum_factor(hang(controller, balls=8, shape="Equine"))
    assert equine == pytest.approx(human * 1.5)


def test_the_batch_is_scaled_by_the_balls(
        controller:GameController) -> None:
    enter_farm(controller)
    player = hang(controller, balls=12)
    events = controller.session.events
    shift = {"job": "cum", "turn": 3, "turns": 3, "earned": 0}
    lines = events.store_batch(player, shift, 3)
    assert "9×" in "\n".join(lines)
    assert any(entry["job"] == "cum"
               for entry in controller.session.farm_ledger.entries)


def test_an_equine_cum_cow_product_is_worth_more(
        controller:GameController) -> None:
    from cursed_descent.locations.farm.location import register_product
    register_product("t_human", "A", "cum", "shift", {"shape": "Human"})
    register_product("t_equine", "B", "cum", "shift", {"shape": "Equine"})
    assert ITEMS["t_equine"]["price"] > ITEMS["t_human"]["price"]
    assert ITEMS["t_human"]["name"] == "A's Stud Cream"


def test_smell_lines_get_stronger_with_sweat_and_stronger_for_equine(
        controller:GameController) -> None:
    player = hang(controller)
    seen = set()
    for sweat in (0, 10, 25, 45):
        player.sweat = sweat
        seen.add(cum_scent(player))
    assert len(seen) == 4
    player.body["endowment_shape"] = "Equine"
    player.sweat = 45
    assert sweat_tier(player) == 3
    assert "stallion" in cum_scent(player) or "horse" in cum_scent(player)


def test_big_balls_may_be_put_to_the_cum_cow_when_sold_to_the_farm(
        controller:GameController) -> None:
    player = hang(controller, balls=12)
    random.seed(1)
    jobs = {farm_job(player) for _ in range(40)}
    assert "cum" in jobs
    player.body["balls"] = 5
    assert "cum" not in {farm_job(player) for _ in range(40)}
    player.gender = "Female"
    player.body["balls"] = 12
    assert "cum" not in {farm_job(player) for _ in range(40)}


def test_the_cum_flask_is_a_consumable_with_a_need_effect() -> None:
    from cursed_descent.config import NEED_ITEM_EFFECTS
    assert ITEMS["cum_flask"]["slot"] == "consumable"
    assert "cum_flask" in NEED_ITEM_EFFECTS


def test_a_hen_lays_an_egg_every_turn_and_the_batch_grows(
        controller:GameController) -> None:
    from cursed_descent.locations.farm.content import HEN_LAYING
    enter_farm(controller)
    hang(controller, gender="Female")
    controller.handle("kerl", "!work hen", now=4.0)
    controller.session.events.shifts()["kerl"]["turns"] = 4
    reply = texts(controller.handle("kerl", "!work", now=5.0))
    assert any(line.split("{name}")[-1][:15] in reply
               for line in HEN_LAYING)
    assert controller.session.events.shifts()["kerl"]["eggs"] == 1


def test_the_hen_batch_includes_the_laid_eggs(
        controller:GameController) -> None:
    enter_farm(controller)
    player = hang(controller, gender="Female")
    shift = {"job": "hen", "turn": 4, "turns": 4, "earned": 0, "eggs": 4}
    lines = controller.session.events.store_batch(player, shift, 4)
    assert "6×" in "\n".join(lines)


def fit(controller:GameController, build:str="Muscular", balls:int=9,
        gender:str="Male"):
    player = hang(controller, gender=gender, balls=balls)
    player.body["build"] = build
    return player


def test_big_muscular_hung_characters_are_hitched_by_the_balls(
        controller:GameController) -> None:
    enter_farm(controller)
    fit(controller)
    reply = texts(controller.handle("kerl", "!work horse", now=4.0))
    assert "heavy sack" in reply
    shift = controller.session.events.shifts()["kerl"]
    assert shift["burden"] and shift["stamina"] >= 8


@pytest.mark.parametrize("build,balls,gender", [
    ("Slim", 9, "Male"), ("Muscular", 7, "Male"), ("Muscular", 9, "Female")])
def test_others_are_not_hitched_by_the_balls(
        controller:GameController, build:str, balls:int,
        gender:str) -> None:
    enter_farm(controller)
    fit(controller, build, balls, gender)
    controller.handle("kerl", "!work horse", now=4.0)
    assert "burden" not in controller.session.events.shifts()["kerl"]


def test_the_burden_pays_more_and_allows_the_carriage(
        controller:GameController) -> None:
    enter_farm(controller)
    fit(controller)
    reply = texts(controller.handle("kerl", "!work carriage", now=4.0))
    assert "Beast of burden" in reply
    assert controller.session.events.shifts()["kerl"]["job"] == "carriage"


def test_a_burden_turn_hurts_and_uses_stamina(
        controller:GameController) -> None:
    enter_farm(controller)
    player = fit(controller)
    player.stats["vitality"] = 100
    controller.handle("kerl", "!work horse", now=4.0)
    shift = controller.session.events.shifts()["kerl"]
    shift["turns"] = 9
    start = shift["stamina"]
    hp = player.hp
    reply = texts(controller.handle("kerl", "!work", now=5.0))
    after = controller.session.events.shifts().get("kerl")
    assert "Stamina" in reply
    assert after is None or after["stamina"] < start
    assert player.hp < hp or after is None


def test_zero_stamina_collapses_and_keeps_the_worker(
        controller:GameController) -> None:
    enter_farm(controller)
    player = fit(controller)
    controller.handle("kerl", "!work carriage", now=4.0)
    shift = controller.session.events.shifts()["kerl"]
    shift.update({"stamina": 1, "turns": 9, "interest": 0.0})
    reply = texts(controller.handle("kerl", "!work", now=5.0))
    assert "kerl" not in controller.session.events.shifts()
    assert "farmed" in (player.last_fate, "farmed") and (
        "legs give out" in reply or "collapses" in reply)


def deliver_batch(controller:GameController, count:int=2,
                  shape:str="Human") -> str:
    player = hang(controller, balls=9, shape=shape)
    return controller.session.farm_ledger.add(
        player, "cum", 8, count, {"shape": shape, "level": 1})


def at_astrid(controller:GameController) -> None:
    at_location(controller, "brewery")
    controller.handle("kerl", "!enter", now=3.0)


def test_astrid_sells_the_trotter_batch_under_the_characters_name(
        controller:GameController) -> None:
    deliver_batch(controller)
    at_astrid(controller)
    events = controller.session.events
    names = [ITEMS[item_id]["name"] for _, item_id, _ in
             events.brewery_offers()]
    assert "kerl's Stud Brew" in names


def test_the_delivery_is_announced_when_entering_the_brewery(
        controller:GameController) -> None:
    deliver_batch(controller)
    at_location(controller, "brewery")
    reply = texts(controller.handle("kerl", "!enter", now=3.0))
    assert "Trotter" in reply and "kerl" in reply


def test_no_delivery_without_a_cum_batch(
        controller:GameController) -> None:
    hang(controller)
    at_astrid(controller)
    assert not any(key.startswith("cumbrew_") for key, _, _ in
                   controller.session.events.brewery_offers())


def test_buying_the_stud_brew_uses_up_the_batch(
        controller:GameController) -> None:
    deliver_batch(controller, count=1)
    player = hang(controller)
    player.gold = 10000
    player.inventory.clear()
    at_astrid(controller)
    offers = controller.session.events.brewery_offers()
    nr = next(index for index, (key, _, _) in enumerate(offers, 1)
              if key.startswith("cumbrew_"))
    controller.handle("kerl", f"!buy {nr}", now=4.0)
    assert "astrid_cum_" in str(player.inventory)
    assert not [entry for entry in controller.session.farm_ledger.entries
                if entry["job"] == "cum" and entry["left"] > 0]


def test_equine_stud_brew_is_stronger(
        controller:GameController) -> None:
    from cursed_descent.locations.brewery.location import register_cum_brew
    register_cum_brew({"id": "h", "name": "A", "victim": {}})
    register_cum_brew({"id": "e", "name": "B", "victim": {
        "shape": "Equine"}})
    assert (ITEMS["astrid_cum_e"]["heal"] > ITEMS["astrid_cum_h"]["heal"])


def test_trotter_gives_the_hen_a_pill_or_a_suppository(
        controller:GameController) -> None:
    from cursed_descent.locations.farm.content import HEN_AIDS
    seen = set()
    for seed in range(30):
        random.seed(seed)
        controller.session.events.event = {
            "kind": "farm", "phase": "farm", "used": set(),
            "data": {"rented": set(), "shifts": {}, "inside": True}}
        hang(controller, gender="Female")
        player = controller.session.member("kerl")
        lines = controller.session.events.rent(player, "hen")
        aid = controller.session.events.shifts()["kerl"]["aid"]
        seen.add(aid)
        assert any(text.split("{name}")[0][:20] in "\n".join(lines)
                   for text in HEN_AIDS[aid])
    assert seen == {"pill", "suppository"}


def test_only_hens_get_the_egg_aid(controller:GameController) -> None:
    enter_farm(controller)
    hang(controller, gender="Female")
    controller.handle("kerl", "!work cow", now=4.0)
    assert "aid" not in controller.session.events.shifts().get("kerl", {})


def test_astrid_visits_the_farm_and_buys_cum_and_milk_batches(
        controller:GameController, monkeypatch) -> None:
    monkeypatch.setattr(
        "cursed_descent.locations.farm.location.ASTRID_VISIT_CHANCE", 1.0)
    player = hang(controller)
    batch = controller.session.farm_ledger.add(
        player, "cum", 8, 5, {"shape": "Human", "level": 1})
    controller.session.farm_ledger.entries[-1]["name"] = "Old Hero"
    gold = player.gold
    at_location(controller, "farm")
    reply = texts(controller.handle("kerl", "!enter", now=3.0))
    assert "Astrid" in reply and "Old Hero" in reply
    assert player.gold == gold + 2 * 15
    left = [entry["left"] for entry in controller.session.farm_ledger.entries
            if entry["job"] == "cum"]
    assert left == [3] and batch


def test_astrid_does_not_come_without_a_batch(
        controller:GameController, monkeypatch) -> None:
    monkeypatch.setattr(
        "cursed_descent.locations.farm.location.ASTRID_VISIT_CHANCE", 1.0)
    hang(controller)
    at_location(controller, "farm")
    assert "Astrid" not in texts(controller.handle("kerl", "!enter",
                                                   now=3.0))


def test_astrid_leaves_the_current_partys_own_batches_alone(
        controller:GameController, monkeypatch) -> None:
    monkeypatch.setattr(
        "cursed_descent.locations.farm.location.ASTRID_VISIT_CHANCE", 1.0)
    deliver_batch(controller, count=5)
    at_location(controller, "farm")
    assert "Astrid" not in texts(controller.handle("kerl", "!enter",
                                                   now=3.0))
    left = {entry["left"] for entry in controller.session.farm_ledger.entries
            if entry["name"] == "kerl"}
    assert left == {5}


NEW_ENDS = ("drained", "stud", "tapped", "sold_brew", "brooding", "roast",
            "torn", "hauled", "circus")


def test_all_nine_farm_bad_ends_have_texts_labels_and_remains() -> None:
    from cursed_descent.content import FATE_LABELS, REMAINS_TEXTS
    for fate in NEW_ENDS:
        assert FATES[fate]["any"] and FATE_LABELS[fate]
        assert "{dead}" in REMAINS_TEXTS[fate]


def test_end_choice_by_role_and_trigger() -> None:
    from cursed_descent.locations.farm.location import farm_end
    random.seed(1)
    assert {farm_end("cum", "kept", False) for _ in range(60)} == {
        "stud", "tapped", "sold_brew"}
    assert farm_end("cum", "collapse", False) == "drained"
    assert farm_end("hen", "kept", False) == "brooding"
    assert farm_end("hen", "collapse", False) == "roast"
    assert farm_end("plough", "collapse", True) == "torn"
    assert {farm_end("carriage", "burden_collapse", True)
            for _ in range(60)} == {"hauled", "farmed"}
    assert {farm_end("plough", "kept", True)
            for _ in range(60)} == {"circus", "farmed"}
    assert farm_end("milk", "kept", False) == "farmed"
    assert farm_end("mule", "collapse", False) == "farmed"


@pytest.mark.parametrize("job,key,burden,fate", [
    ("cum", "collapse", False, "drained"),
    ("hen", "collapse", False, "roast"),
    ("plough", "collapse", True, "torn"),
])
def test_a_shift_can_end_in_the_new_bad_ends(
        controller:GameController, job:str, key:str, burden:bool,
        fate:str) -> None:
    enter_farm(controller)
    player = hang(controller, gender="Male", balls=9)
    controller.session.events.shifts()["kerl"] = {
        "job": job, "turns": 3, "turn": 1, "pay": 10, "earned": 0}
    lines = controller.session.events.kept_on_farm(player, job, key, burden)
    assert any("💀" in line for line in lines)
    assert controller.session.remains.entries[-1]["fate"] == fate


def test_custody_ends_leave_a_batch_for_the_taproom(
        controller:GameController, monkeypatch) -> None:
    enter_farm(controller)
    player = hang(controller, gender="Male", balls=9)
    monkeypatch.setattr(random, "choice", lambda options: options[-1])
    controller.session.events.shifts()["kerl"] = {
        "job": "cum", "turns": 3, "turn": 1, "pay": 10, "earned": 0}
    controller.session.events.kept_on_farm(player, "cum", "kept")
    assert controller.session.remains.entries[-1]["fate"] == "sold_brew"
    assert any(entry["name"] == "kerl" and entry["job"] == "cum"
               and entry["left"] == 6
               for entry in controller.session.farm_ledger.entries)
