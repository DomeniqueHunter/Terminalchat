from dataclasses import dataclass

from ..config import BIOME_SEGMENT, BOSS_INTERVAL
from ..dungeon import current_biome, segment_of
from ..models import Player


LOOKS = {
    "Goblin Warrens": ("🕳", "#7d8f2a"),
    "Dripping Caves": ("💧", "#3f8fb5"),
    "The Crypt": ("⚰", "#6f8499"),
    "Rotting Swamp": ("🐸", "#4f7a3a"),
    "Vine Swamp": ("🌺", "#b0457a"),
    "Orc Camp": ("⛺", "#b5532e"),
    "Orc Stronghold": ("🏰", "#a8402a"),
    "Amazon Temple": ("🏛", "#1f9d6b"),
    "Amazon Jungle": ("🌴", "#2fa05a"),
    "Petrified Halls": ("🗿", "#8a8f94"),
    "Living Walls": ("👁", "#c06a86"),
    "Giant's Larder": ("🍖", "#b59b6a"),
    "Ogre Mountain": ("⛰", "#8a6a4a"),
}
FALLBACK = ("🗺", "#888888")


@dataclass(frozen=True)
class Ribbon:
    icon: str
    name: str
    color: str
    stages: str
    intro: str
    boss: bool


def biome_ribbon(session, viewer:Player) -> Ribbon | None:
    if not session.in_run(viewer.name) or session.state not in (
            "combat", "chest", "remains", "event"):
        return None
    stage = session.stage
    biome = current_biome(stage, session.run_id, session.lobby_town)
    icon, color = LOOKS.get(biome["name"], FALLBACK)
    first = segment_of(stage) * BIOME_SEGMENT + 1
    return Ribbon(icon, biome["name"], color,
                  f"Stages {first}–{first + BIOME_SEGMENT - 1}",
                  biome["intro"], stage % BOSS_INTERVAL == 0)
