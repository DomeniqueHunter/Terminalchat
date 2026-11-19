from ...spawn_rule import SpawnRule


RULES = (
    SpawnRule("hunter", weight=3, order=2, min_stage=5),
    SpawnRule("hut", weight=3, order=8, min_stage=8, slot="location"),
)
