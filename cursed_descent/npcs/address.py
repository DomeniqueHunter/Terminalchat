from ..models import Player
from ..town_buildings import registry
from ..towns import TOWNS


ADDRESS_KEY = "address"
EVENT_KEYS = {"lich court": "lich_court"}
TOWN_BUILDINGS = {"school": "maidschool"}
PLAIN_BUILDINGS = ("shop",)
EVENT_PLACES = {
    "adept": "Chalk circle (Adept)", "boutique": "<<boutique.atelier>>",
    "brewery": "Creamworth taproom", "butcher": "Butcher shop",
    "farm": "Trotter Farm", "fisher": "Black pond", "grill": "Güls Grill", "dairy": "Crone Creamery", "buster_maid": "The road (Connie)",
    "lich_court": "Frozen court", "lodge": "Hunting lodge",
    "mage_tower": "Mage's Tower", "smokery": "Northern Smokery",
    "sweatery": "Perspiratorium", "void": "The Void",
    "wedding": "Wedding of the Grimholds",
}


def building_title(key:str) -> str:
    spec = registry.specs().get(key)
    return spec.title if spec is not None else key.replace("_", " ").title()


def display_of(address:str) -> str:
    parts = address.split(":")
    if parts[0] == "town" and len(parts) == 4:
        return f"{building_title(parts[2])}, {TOWNS[parts[1]].name}"
    if parts[0] == "event" and len(parts) == 3:
        return EVENT_PLACES.get(parts[1], parts[1].replace("_", " ").title())
    return ""


def valid_address(address:str) -> bool:
    parts = address.split(":")
    if parts[0] == "town" and len(parts) == 4:
        return (parts[1] in TOWNS and parts[3].isdigit()
                and (parts[2] in registry.specs()
                     or parts[2] in TOWN_BUILDINGS.values()
                     or parts[2] in PLAIN_BUILDINGS))
    if parts[0] == "event" and len(parts) == 3:
        return parts[1] in EVENT_PLACES and parts[2].isdigit()
    return False


def assign_addresses(players:list[Player]) -> None:
    counts: dict[tuple[str, str, str], int] = {}
    for player in players:
        profile = player.profile
        place = profile.get("building", "")
        place = TOWN_BUILDINGS.get(place, place)
        if profile.get("kind") == "resident" or place == "maidschool":
            scope = ("town", profile.get("town", "last_light"), place)
        else:
            scope = ("event", EVENT_KEYS.get(place, place), "")
        counts[scope] = counts.get(scope, 0) + 1
        number = counts[scope]
        address = (f"town:{scope[1]}:{scope[2]}:{number}"
                   if scope[0] == "town" else f"event:{scope[1]}:{number}")
        profile[ADDRESS_KEY] = address
        profile["home"] = display_of(address)
