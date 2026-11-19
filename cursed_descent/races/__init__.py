from dataclasses import dataclass, field


DEFAULT_RACE = "human"


@dataclass(frozen=True)
class Race:
    key: str
    name: str
    plural: str
    height: tuple[int, int]
    weight: tuple[int, int]
    roughness: float
    roughness_style: str
    advice: dict[str, str]
    clinic_special: str
    implant_only: bool = False
    taste: tuple[str, str, str] = ("bust", "any", "any")
    taste_pull: float = 0.0
    offers: dict[str, str] = field(default_factory=dict)
    drop_in_working: tuple[str, ...] = ()
    drop_in_sub: tuple[str, ...] = ()
    adventurers: bool = True
    playable: bool = False
    member: tuple[int, int, int] = (15, 12, 5)
    member_shape: str = "Human"
    scent: tuple[int, int] = (0, 0)
    skin: tuple[str, str] = ("warm skin", "salt")

    def fits(self, height:float, weight:float) -> bool:
        return (self.height[0] <= height <= self.height[1]
                and self.weight[0] <= weight <= self.weight[1])


def load_races() -> dict[str, Race]:
    from .dwarf import RACE as dwarf
    from .gnome import RACE as gnome
    from .goblin import RACE as goblin
    from .human import RACE as human
    from .nord import RACE as nord
    from .vampire import RACE as vampire
    return {race.key: race for race in (human, dwarf, gnome, goblin,
                                        vampire, nord)}


RACES = load_races()


def race_named(key:str) -> Race:
    return RACES.get(key, RACES[DEFAULT_RACE])


def race_of(player) -> Race:
    if player.race in RACES:
        return RACES[player.race]
    if player.profile.get("kind") == "resident":
        from ..towns import TOWNS
        town = TOWNS.get(player.profile.get("town", ""))
        if town is not None:
            return race_named(town.race_key)
    return RACES[DEFAULT_RACE]


def race_of_town(town_key:str) -> Race:
    from ..towns import TOWNS
    town = TOWNS.get(town_key)
    return race_named(town.race_key) if town else RACES[DEFAULT_RACE]
