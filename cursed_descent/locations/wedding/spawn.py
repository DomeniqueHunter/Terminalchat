from ...spawn_rule import SpawnRule


RULES = (
    SpawnRule("wedding", weight=2, order=20, min_stage=15,
              slot="location", once_per_run=True),
)
