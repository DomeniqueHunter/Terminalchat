import pytest

from cursed_descent.config import CYCLE_LENGTH
from cursed_descent.content import SPELLS
from cursed_descent.formulas import (
    cycle_number, effective_stat, enemy_scale, exp_needed,
    knows_spell, loot_chance, max_hp, max_mana, mimic_chance,
)
from cursed_descent.models import Player


def test_exp_needed_grows_with_level() -> None:
    values = [exp_needed(level) for level in range(1, 30)]
    assert values == sorted(values) and len(set(values)) == len(values)


def test_max_hp_grows_with_vitality(hero:Player) -> None:
    before = max_hp(hero)
    hero.stats["vitality"] += 10
    assert max_hp(hero) > before


def test_max_mana_grows_with_intelligence(hero:Player) -> None:
    before = max_mana(hero)
    hero.stats["intelligence"] += 10
    assert max_mana(hero) > before


def test_effective_stat_without_gear_is_base(hero:Player) -> None:
    assert effective_stat(hero, "strength") == hero.stats["strength"]


def test_cycle_number_uses_cycle_length() -> None:
    assert cycle_number(CYCLE_LENGTH) == 0
    assert cycle_number(CYCLE_LENGTH + 1) == 1


def test_enemy_scale_is_monotonic() -> None:
    scales = [enemy_scale(stage) for stage in range(1, 120)]
    assert scales == sorted(scales)


@pytest.mark.parametrize("stage", [1, 10, 50, 500])
def test_mimic_chance_is_a_probability(stage:int) -> None:
    assert 0 <= mimic_chance(stage) <= 1


def test_boss_loot_is_guaranteed() -> None:
    assert loot_chance(0, True) == 1.0
    assert loot_chance(1000, False) <= 0.6


def test_fresh_player_knows_starter_spells_only(hero:Player) -> None:
    known = [spell for spell in SPELLS if knows_spell(hero, spell)]
    assert known
    assert len(known) < len(SPELLS)
