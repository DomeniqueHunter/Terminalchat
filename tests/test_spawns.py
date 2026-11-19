import pytest

from cursed_descent.spawn_rule import SpawnRule
from cursed_descent.spawns import (
    RULES_BY_KIND, SPAWN_RULES, eligible, min_stage,
)


def test_rules_are_loaded_in_declared_order() -> None:
    orders = [rule.order for rule in SPAWN_RULES]
    assert orders == sorted(orders)
    assert len(RULES_BY_KIND) == len(SPAWN_RULES) == 32


def test_min_stage_comes_from_the_block() -> None:
    assert min_stage("lich") == 20
    assert min_stage("wanderer") == 1


def test_eligible_respects_min_stage() -> None:
    assert "lich" not in {rule.kind for rule in eligible(19)}
    assert "lich" in {rule.kind for rule in eligible(20)}


@pytest.mark.parametrize("stage,expected", [
    (4, False), (5, True), (6, False), (7, True), (11, False), (9, True),
    (13, False)])
def test_max_stage_and_interval(stage:int, expected:bool) -> None:
    rule = SpawnRule("x", weight=1, order=1, min_stage=5, max_stage=9,
                     interval=2)
    assert rule.allows(stage) is expected


def test_location_slot_is_separate_from_events() -> None:
    events = {rule.kind for rule in eligible(30)}
    locations = {rule.kind for rule in eligible(30, "location")}
    assert {"hut", "farm", "butcher_shop", "brewery", "sweatery",
            "smokery", "bivouac", "fisher", "grill", "dairy", "privy", "couch", "throne", "wardrobe",
            "wedding", "pod_garden"} == locations
    assert not events & locations
    assert {rule.kind for rule in eligible(4, "location")} == {
        "farm", "butcher_shop", "bivouac", "couch"}
