import pytest

from cursed_descent.config import AFFINITY_NAMES, EQUIPMENT_SLOTS
from cursed_descent.content import (
    BIOMES, COMBO_TITLES, ENEMIES, FATE_LABELS, FATES, ITEM_SETS, ITEMS,
    RARITY_LABELS, SPELLS, TITLES,
)


BOSS_KEYS = {"name", "hp", "attack", "defense", "agility", "exp", "fates",
             "minions", "actions"}
ENEMY_KEYS = {"name", "min_stage", "max_stage", "hp", "attack", "defense",
              "agility", "exp", "fates", "actions"}


def test_items_have_valid_slot_and_rarity() -> None:
    valid_slots = set(EQUIPMENT_SLOTS) | {"consumable", "furniture"}
    for item_id, item in ITEMS.items():
        assert item["name"], item_id
        assert item["slot"] in valid_slots, item_id
        assert item["rarity"] in RARITY_LABELS, item_id


def test_item_sets_reference_existing_items() -> None:
    members = {item["set"] for item in ITEMS.values() if "set" in item}
    assert members <= set(ITEM_SETS)


@pytest.mark.parametrize("template_id", sorted(ENEMIES))
def test_enemy_template_is_complete(template_id:str) -> None:
    template = ENEMIES[template_id]
    assert ENEMY_KEYS <= set(template), template_id
    assert template["hp"] > 0
    assert template["actions"]
    assert all(weight > 0 for _, weight in template["actions"])
    assert set(template["fates"]) <= set(FATES), template_id


def test_biomes_reference_existing_enemies() -> None:
    for biome in BIOMES:
        assert set(biome["enemies"]) <= set(ENEMIES), biome["name"]
        boss = biome["boss"]
        assert BOSS_KEYS <= set(boss), biome["name"]
        assert set(boss["fates"]) <= set(FATES), biome["name"]
        assert set(boss["minions"]) <= set(ENEMIES), biome["name"]
        assert biome["min_stage"] >= 1, biome["name"]
        assert len(biome["intro"]) > 60, biome["name"]


def test_biome_plan_has_a_start_biome_and_unique_bosses() -> None:
    assert BIOMES[0]["min_stage"] == 1
    assert BIOMES[0]["name"] == "Goblin Warrens"
    bosses = [biome["boss"]["name"] for biome in BIOMES]
    assert len(set(bosses)) == len(BIOMES) == 13


def test_every_fate_has_a_label() -> None:
    assert set(FATES) <= set(FATE_LABELS)


def test_spells_use_known_affinities() -> None:
    for spell_id, spell in SPELLS.items():
        assert spell["affinity"] in AFFINITY_NAMES, spell_id
        assert spell["mana"] >= 0


def test_titles_cover_all_affinities() -> None:
    assert set(TITLES) == set(AFFINITY_NAMES)
    assert all(len(pair) == 2 for pair in COMBO_TITLES)
