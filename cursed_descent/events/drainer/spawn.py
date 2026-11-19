from ...spawn_rule import SpawnRule
from .config import MIN_STAGE


RULES = (
    SpawnRule("drainer", weight=1, order=27, min_stage=MIN_STAGE,
              once_per_run=True),
)
