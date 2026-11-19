from ...spawn_rule import SpawnRule
from .config import PER_SEGMENT


RULES = (
    SpawnRule("caravaneer", weight=3, order=26, per_segment=PER_SEGMENT),
)
