from dataclasses import dataclass


@dataclass(frozen=True)
class VisitProfile:
    npc: str
    kinds: tuple[str, ...] = ()
    likes: tuple[tuple[str, int], ...] = (("cafe", 1), ("brothel", 1))
    stance: str = ""
    cruel: int = 1
    quirks: tuple[tuple[str, tuple[str, ...]], ...] = ()
