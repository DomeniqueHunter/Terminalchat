import random

from ...config import BOSS_INTERVAL, CITY_STOP_EVERY, CITY_STOP_FIRST
from ...spawn_rule import SpawnRule


RULES = (
    SpawnRule("mage_tower", weight=0, order=40, slot="location",
              min_stage=CITY_STOP_FIRST + 1),
)


def mage_stage_for(stretch:int) -> int:
    start = CITY_STOP_FIRST + stretch * CITY_STOP_EVERY
    free = [stage for stage in range(start + 1, start + CITY_STOP_EVERY)
            if stage % BOSS_INTERVAL]
    return random.Random(f"mage-tower-{stretch}").choice(free)


def mage_tower_at(stage:int) -> bool:
    if stage <= CITY_STOP_FIRST:
        return False
    stretch = (stage - CITY_STOP_FIRST) // CITY_STOP_EVERY
    return stage == mage_stage_for(stretch)
