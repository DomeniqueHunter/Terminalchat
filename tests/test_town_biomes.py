from collections import Counter

from cursed_descent.config import BIOME_SEGMENT, TOWN_BIOMES
from cursed_descent.content import BIOMES
from cursed_descent.dungeon import current_biome
from cursed_descent.towns import TOWNS


def test_every_town_has_valid_biomes() -> None:
    names = {biome["name"] for biome in BIOMES}
    assert set(TOWN_BIOMES) == set(TOWNS)
    for start, favorites in TOWN_BIOMES.values():
        assert start in names and set(favorites) <= names
        low = next(b for b in BIOMES if b["name"] == start)["min_stage"]
        assert low <= 1 + BIOME_SEGMENT


def test_start_biome_follows_the_town() -> None:
    assert current_biome(1, "x", "ironhold")["name"] == "Dripping Caves"
    assert current_biome(1, "x", "mudgate")["name"] == "Goblin Warrens"
    assert current_biome(1, "x")["name"] == "Goblin Warrens"


def test_unknown_town_keeps_the_old_rules() -> None:
    for seed in ("a", "b", "c", "d"):
        assert current_biome(40, seed) is current_biome(40, seed, "nowhere")


def test_favorites_are_drawn_more_often() -> None:
    stage = 14 * BIOME_SEGMENT + 1
    plain = Counter(current_biome(stage, f"s{n}")["name"]
                    for n in range(600))
    ironhold = Counter(current_biome(stage, f"s{n}", "ironhold")["name"]
                       for n in range(600))
    favorites = TOWN_BIOMES["ironhold"][1]
    assert (sum(ironhold[name] for name in favorites)
            > sum(plain[name] for name in favorites))


def test_a_run_is_stable_for_one_seed() -> None:
    first = current_biome(20, "seed", "dusk_hollow")
    assert first is current_biome(20, "seed", "dusk_hollow")
