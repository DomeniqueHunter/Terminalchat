from ...spawn_rule import SpawnRule


RULES = (
    SpawnRule("buster_maid", weight=3, order=23, min_stage=4,
              once_per_run=True),
)
