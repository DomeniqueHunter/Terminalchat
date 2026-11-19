from dataclasses import dataclass


@dataclass(frozen=True)
class SpawnRule:
    kind: str
    weight: int
    order: int
    min_stage: int = 1
    max_stage: int = 0
    interval: int = 1
    slot: str = "event"
    once_per_run: bool = False
    per_segment: int = 0
    biome: str = ""
    season: str = ""

    def allows(self, stage:int) -> bool:
        if stage < self.min_stage:
            return False
        if self.max_stage and stage > self.max_stage:
            return False
        return (stage - self.min_stage) % max(self.interval, 1) == 0
