import random

import pytest

from cursed_descent.config import (
    BIOME_SEGMENT, BOSS_INTERVAL, MAX_ENEMIES, MAX_PARTY_SIZE,
)
from cursed_descent.content import BIOMES
from cursed_descent.controller import GameController
from cursed_descent.dungeon import (
    current_biome, is_biome_start, is_boss_stage, spawn_stage,
)
from cursed_descent.models import Player


def test_boss_and_biome_stage_markers() -> None:
    assert is_boss_stage(BOSS_INTERVAL)
    assert not is_boss_stage(BOSS_INTERVAL + 1)
    assert is_biome_start(1)
    assert is_biome_start(BIOME_SEGMENT + 1)
    assert not is_biome_start(BIOME_SEGMENT)
    assert current_biome(1) is current_biome(BIOME_SEGMENT)


def test_first_segment_is_always_the_start_biome() -> None:
    for seed in ("a", "b", "c"):
        for stage in range(1, BIOME_SEGMENT + 1):
            assert current_biome(stage, seed)["name"] == "Goblin Warrens"


def test_biome_plan_is_stable_per_seed_and_covers_a_segment() -> None:
    for stage in range(5, 120):
        first = current_biome(stage, "x")
        assert first is current_biome(stage, "x")
        segment_start = stage - (stage - 1) % BIOME_SEGMENT
        assert first is current_biome(segment_start, "x")


def test_biomes_respect_min_stage_and_may_repeat() -> None:
    names = []
    for seed in range(40):
        for stage in range(BIOME_SEGMENT + 1, 200, BIOME_SEGMENT):
            biome = current_biome(stage, str(seed))
            assert biome["min_stage"] <= stage
            names.append(biome["name"])
    assert len(set(names)) == len(BIOMES)
    pairs = zip(names, names[1:])
    assert any(left == right for left, right in pairs)


def test_boss_stage_uses_the_boss_of_the_current_biome() -> None:
    random.seed(1)
    biome = current_biome(BOSS_INTERVAL, "boss")
    boss = spawn_stage(BOSS_INTERVAL, "boss")[0]
    assert boss.name == biome["boss"]["name"]


@pytest.mark.parametrize("stage", [1, 5, 10, 25, 40, 80, 150])
def test_spawn_stage_creates_living_enemies(stage:int) -> None:
    random.seed(stage)
    enemies = spawn_stage(stage)
    assert 1 <= len(enemies) <= MAX_ENEMIES
    assert all(enemy.alive for enemy in enemies)
    assert len({enemy.uid for enemy in enemies}) == len(enemies)


def test_boss_stage_contains_a_boss() -> None:
    random.seed(1)
    assert any(enemy.boss for enemy in spawn_stage(BOSS_INTERVAL))


def test_lobby_rules(controller:GameController) -> None:
    session = controller.session
    kerl = controller.repository.load("kerl")
    session.open_lobby(kerl)
    assert session.state == "lobby"
    assert "already in the party" in session.join(kerl)[0].text
    session.leave("kerl")
    assert session.state == "idle"


def test_party_size_is_capped(controller:GameController) -> None:
    session = controller.session
    members = [controller.repository.load(name) for name in
               ("kerl", "galactica", "gianna_morningwood",
                "beverley_morningwood")]
    session.open_lobby(members[0])
    for member in members[1:]:
        session.join(member)
    extra = Player(name="Extra")
    assert len(session.party) == MAX_PARTY_SIZE
    assert "full" in session.join(extra)[0].text


def test_start_requires_lobby_member(controller:GameController) -> None:
    session = controller.session
    session.open_lobby(controller.repository.load("kerl"))
    assert "Only a member" in session.start("galactica", 0.0)[0].text
    assert session.state == "lobby"


def test_run_heals_party_on_start(controller:GameController) -> None:
    kerl = controller.repository.load("kerl")
    controller.session.open_lobby(kerl)
    controller.session.start("kerl", 0.0)
    assert kerl.hp > 0 and kerl.alive and kerl.records["runs"] >= 1


def test_dead_players_cannot_act(controller:GameController) -> None:
    session = controller.session
    kerl = controller.repository.load("kerl")
    session.open_lobby(kerl)
    session.start("kerl", 0.0)
    kerl.alive = False
    assert "dead" in session.submit("kerl", "hit", [], 1.0)[0].text.lower()
