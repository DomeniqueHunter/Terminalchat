from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    key: str
    title: str
    building: str
    sessions: int
    base: int
    stat: str
    blurb: str
    interactive: bool = False


@dataclass
class Shift:
    building: str
    job: Job
    left: int
    earned: int = 0
    client: object = None
    due: float = 0.0
    winded: int = 0
    air: int = 100
    mode: str = ""
    family: object = None
    endless: bool = False
    served: int = 0
    bonus: int = 0
    risk: float = 1.0
    raise_due: float = 0.0
    crush_now: bool = False
