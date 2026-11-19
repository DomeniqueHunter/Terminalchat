import random

from cursed_descent.config import LOCATION_EVERY
from cursed_descent.dungeon import is_boss_stage
from cursed_descent.locations.venues import fate_location, location_at


def test_locations_appear_every_fourth_non_boss_stage() -> None:
    random.seed(1)
    for stage in range(1, 71):
        kind = location_at(stage)
        expected = (stage % LOCATION_EVERY == 0 and stage >= 4
                    and not is_boss_stage(stage))
        assert bool(kind) == expected, stage


def test_kind_is_random_but_limited_to_eligible_rules() -> None:
    random.seed(2)
    early = {location_at(4) for _ in range(60)}
    assert early == {"farm", "butcher_shop", "bivouac", "couch"}
    late = {location_at(48) for _ in range(200)}
    assert late == {"hut", "farm", "butcher_shop", "brewery", "sweatery",
                    "smokery", "bivouac", "fisher", "grill", "dairy", "privy", "couch", "throne",
                    "wardrobe", "wedding"}


def test_fate_location_is_the_current_cycle_stage() -> None:
    assert fate_location("farmed", "", 24) == 24
    assert fate_location("butchered", "", 94) == 24
    assert fate_location("eaten", "", 24) == 0
