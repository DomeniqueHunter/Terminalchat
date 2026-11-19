from typing import Any

from ..locations.brewery.npc import ASTRID
from ..locations.fisher.npc import GORM
from ..locations.grill.npc import GUL
from ..locations.dairy.npc import DAIRY_STAFF
from ..events.maid.npc import CONNIE
from ..locations.smokery.npc import SMOKERY_STAFF
from ..locations.wedding.npc import WEDDING_GUESTS
from ..locations.sweatery.npc import SWEATERY_STAFF
from ..towns import Resident
from .figures import (
    ADEPT_BOY, HAMHOCK, ISOLDE, NULL_MASTER, ORLEN, STARCH, TROTTER, VESPER,
)


PLACE_KEEPERS = {
    "brewery": (ASTRID,), "boutique": (VESPER,),
    "butcher_shop": (HAMHOCK,), "farm": (TROTTER,),
    "lich": (ISOLDE,), "null_master": (NULL_MASTER,),
    "smokery": SMOKERY_STAFF, "mage_tower": (ORLEN,),
    "wedding": WEDDING_GUESTS, "fisher": (GORM,), "grill": (GUL,), "dairy": DAIRY_STAFF, "buster_maid": (CONNIE,),
    "adept": (ADEPT_BOY,), "recruiter": (STARCH,),
}


def place_residents(event:dict[str, Any]) -> list[Resident]:
    for key in (event.get("phase", ""), event.get("kind", "")):
        if key == "sweatery":
            operator = event.get("data", {}).get("operator", "goblin")
            return list(SWEATERY_STAFF[operator])
        if key in PLACE_KEEPERS:
            return list(PLACE_KEEPERS[key])
    return []
