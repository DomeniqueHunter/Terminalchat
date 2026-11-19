import random

from cursed_descent.content import ITEMS, ITEM_SETS
from cursed_descent.exposure import (
    covered_parts, decency_for, exposed_parts, exposure_level,
    reaction_line, shift_for,
)
from cursed_descent.formulas import active_set_bonuses
from cursed_descent.models import Player
from cursed_descent.town_buildings.greeting import greeting_for
from cursed_descent.towns import TOWNS


def building(town:str, key:str):
    return next(found for found in TOWNS[town].building_list()
                if found.key == key)


def dressed(**slots:str) -> Player:
    player = Player(name="Kerl", gender="Female")
    player.profile["town"] = "dusk_hollow"
    player.equipment.update(slots)
    return player


def test_an_undressed_char_is_bare_and_a_dressed_one_is_not() -> None:
    assert exposure_level(dressed()) == "bare"
    full = dressed(chest="evening_gown_with_slit")
    assert covered_parts(full) == {"breasts", "butt", "groin"}
    assert exposure_level(full) == ""


def test_revealing_items_expose_the_named_parts() -> None:
    player = dressed(chest="open_bodice_velvet_dress")
    assert exposed_parts(player) == ["breasts"]
    assert exposure_level(player) == "partial"
    player = dressed(chest="dress_of_open_doors")
    assert exposed_parts(player) == ["breasts", "butt"]
    assert exposed_parts(dressed(chest="backless_velvet_dress")) == ["butt"]


def test_slot_defaults_cover_the_expected_parts() -> None:
    assert exposed_parts(dressed(chest="leather_vest")) == ["butt", "groin"]
    player = dressed(chest="leather_vest", crotch="loincloth")
    assert exposure_level(player) == ""


def test_decency_comes_from_the_town_and_the_building() -> None:
    town = TOWNS["last_light"]
    assert town.decency == 4
    assert decency_for(town, building("last_light", "brothel")) == 0
    assert decency_for(town, building("last_light", "cafe")) == 0
    assert decency_for(town, building("last_light", "clinic")) == -1
    assert decency_for(town, building("last_light", "tavern")) == 2
    assert decency_for(town, building("last_light", "bank")) == 4
    assert decency_for(TOWNS["cogsworth"],
                       building("cogsworth", "tavern")) == 1
    assert decency_for(TOWNS["dusk_hollow"],
                       building("dusk_hollow", "castle")) == 2
    assert decency_for(TOWNS["dusk_hollow"],
                       building("dusk_hollow", "tailor")) == 0
    assert decency_for(TOWNS["mudgate"], building("mudgate", "arena")) == 0


def test_the_keeper_personality_shifts_the_value_by_one() -> None:
    town = TOWNS["ironhold"]
    assert shift_for("stern and proper") == 1
    assert shift_for("bold and flirty") == -1
    assert decency_for(town, None, "stern") == 4
    assert decency_for(town, None, "playful") == 2
    assert decency_for(TOWNS["last_light"], None, "stern") == 4


def test_reactions_exist_for_every_pool_and_level() -> None:
    from cursed_descent.exposure_texts import REACTIONS
    for pool, levels in REACTIONS.items():
        assert set(levels) == {"partial", "bare"}, pool
        assert all(len(lines) >= 3 for lines in levels.values()), pool


def test_a_bare_visitor_gets_a_reaction_and_a_dressed_one_does_not() -> None:
    rng = random.Random(1)
    bare = dressed()
    assert reaction_line(bare, "tailor", "Delphine", "", rng)
    assert "Delphine" in reaction_line(bare, "tailor", "Delphine", "", rng)
    clothed = dressed(chest="evening_gown_with_slit")
    assert reaction_line(clothed, "tailor", "Delphine", "", rng) == ""
    assert reaction_line(bare, "clinic", "Dr. Vane", "", rng) == ""


def test_the_greeting_carries_the_reaction() -> None:
    text = greeting_for(dressed(), "tailor", random.Random(2))
    assert "Delphine" in text and text.count("\n") == 1


def test_the_tailor_sells_sets_with_valid_bonuses() -> None:
    offers = building("dusk_hollow", "tailor").counter.offers
    assert len(offers) >= 20
    for offer in offers:
        assert offer.item in ITEMS and ITEMS[offer.item]["no_loot"]
    sets = {item["set"] for item in ITEMS.values()
            if item.get("set") in ITEM_SETS and item.get("price")}
    assert {"pale_court", "velvet_hours", "revealing_mistress",
            "dagger_lace", "gentleman_hollow"} <= sets


def test_every_tailor_set_can_be_completed_with_distinct_slots() -> None:
    for set_id in ("pale_court", "velvet_hours", "revealing_mistress",
                   "dagger_lace", "gentleman_hollow"):
        slots = [item["slot"] for item in ITEMS.values()
                 if item.get("set") == set_id]
        assert len(slots) == len(set(slots)), set_id
        assert max(ITEM_SETS[set_id]["bonuses"]) <= len(slots), set_id


def test_a_complete_set_gives_its_bonuses() -> None:
    player = Player(name="Kerl", gender="Female")
    player.equipment.update(
        chest="dress_of_open_doors", crotch="satin_hotpants",
        accessory="gilded_bell_chains", lingerie="lace_thong")
    allure = sum(bonus.get("allure", 0)
                 for bonus in active_set_bonuses(player))
    assert allure == 8


def test_tailor_panel_is_sorted_into_tabs_by_group_and_gender() -> None:
    from types import SimpleNamespace
    from cursed_descent.models import Player
    from cursed_descent.towns.dusk_hollow_vampires.tailor import content
    from cursed_descent.towns.dusk_hollow_vampires.tailor.ui import panel
    player = Player(name="kerl", gold=10000)
    services = SimpleNamespace(in_run=lambda who: False)
    wares = panel(services, player).sections[0]
    assert [tab.title for tab in wares.sections] == list(content.GROUPS)
    shown = 0
    for group in wares.sections:
        assert [tab.title for tab in group.sections] == [
            "all", "ladies", "gents"]
        shown += len(group.sections[0].rows)
    assert shown == len(content.SPECIAL.offers)
