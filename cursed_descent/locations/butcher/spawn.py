from ...spawn_rule import SpawnRule


RULES = (
    SpawnRule("butcher", weight=3, order=9, min_stage=6),
    SpawnRule("butcher_shop", weight=3, order=10, min_stage=4,
              slot="location"),
)
