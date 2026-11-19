from ...spawn_rule import SpawnRule


RULES = (
    SpawnRule("farmer", weight=3, order=11, min_stage=6),
    SpawnRule("farm", weight=3, order=12, min_stage=4, slot="location"),
)
