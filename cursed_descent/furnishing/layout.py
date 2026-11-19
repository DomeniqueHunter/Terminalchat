from dataclasses import dataclass


KINDS = {
    "bed": ("Bed", "🛏"), "seat": ("Seat", "🪑"), "rug": ("Rug", "🟫"),
    "shelf": ("Shelf", "📚"), "table": ("Table", "🍽"),
    "lamp": ("Lamp", "🕯"), "decor": ("Decor", "🖼"),
    "bath": ("Bath", "🛁"), "stove": ("Stove", "🔥"),
    "plant": ("Plant", "🌱"), "utility": ("Utility", "🔧"),
    "kinky": ("Kinky", "⛓"),
}
COMFORT_TIERS = ((16, "home_luxury"), (6, "home_rested"))


@dataclass(frozen=True)
class Room:
    key: str
    name: str
    icon: str
    kinds: tuple[str, ...]
    col: int
    row: int
    width: int = 1
    height: int = 1

    def slots(self) -> tuple[tuple[str, str], ...]:
        return tuple((f"{self.key}:{number}", kind)
                     for number, kind in enumerate(self.kinds))


def room(key:str, name:str, icon:str, kinds:str, col:int, row:int,
         width:int=1, height:int=1) -> Room:
    return Room(key, name, icon, tuple(kinds.split()), col, row, width,
                height)


LIVING = "bed seat rug table shelf lamp"
GARDEN = "plant plant plant seat utility"
LAYOUTS = {
    "hut": (
        room("living", "Living room", "🏠", LIVING, 1, 1, 3),
        room("garden", "Garden", "🌳", "plant plant seat utility", 1, 2, 3),
    ),
    "row": (
        room("living", "Living room", "🏠",
             "seat seat rug table shelf lamp decor", 1, 1, 2),
        room("bedroom", "Bedroom", "🛏", "bed bed rug lamp decor kinky", 3, 1),
        room("garden", "Garden", "🌳", GARDEN, 1, 2, 3),
    ),
    "townhouse": (
        room("living", "Living room", "🏠",
             "seat seat rug table shelf lamp decor", 1, 1, 2),
        room("kitchen", "Kitchen", "🍳", "stove table shelf lamp", 3, 1),
        room("bedroom", "Bedroom", "🛏", "bed bed rug lamp shelf decor kinky",
             1, 2, 2),
        room("bath", "Bath", "🛁", "bath rug shelf lamp", 3, 2),
        room("garden", "Garden", "🌳", GARDEN, 1, 3, 3),
    ),
    "manor": (
        room("living", "Living room", "🏠",
             "seat seat rug table shelf lamp decor", 1, 1, 2),
        room("kitchen", "Kitchen", "🍳", "stove table shelf lamp", 3, 1),
        room("bedroom", "Bedroom", "🛏", "bed bed rug lamp shelf decor kinky",
             1, 2, 2),
        room("bath", "Bath", "🛁", "bath rug shelf lamp", 3, 2),
        room("library", "Library", "📖",
             "shelf shelf shelf seat seat table rug lamp decor", 1, 3, 2),
        room("tower", "Tower room", "🗼", "bed seat lamp decor shelf kinky",
             3, 3),
        room("playroom", "Playroom", "⛓", "kinky kinky kinky kinky rug lamp decor",
             1, 4, 3),
        room("garden", "Garden", "🌳", GARDEN, 1, 5, 3),
    ),
}
STARTER = (("bed", "straw_pallet"), ("seat", "three_legged_stool"),
           ("lamp", "tallow_candle"))


def rooms_of(house_type:str) -> tuple[Room, ...]:
    return LAYOUTS.get(house_type, LAYOUTS["hut"])


def slots_of(house_type:str) -> dict[str, str]:
    return {slot: kind for item in rooms_of(house_type)
            for slot, kind in item.slots()}
