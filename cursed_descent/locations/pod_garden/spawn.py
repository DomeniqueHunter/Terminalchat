from ...spawn_rule import SpawnRule


RULES = (
    SpawnRule("pod_garden", weight=20, order=26, min_stage=16,
              slot="location", biome="Vine Swamp"),
)
