from typing import Any

from .config import DEFAULT_AGE, LEGACY_ITEMS, LEGACY_SLOTS
from .identity import new_id


SCHEMA_VERSION = 6


def upgrade_to_2(data:dict[str, Any]) -> None:
    data["equipment"] = {LEGACY_SLOTS.get(slot, slot): item_id
                         for slot, item_id in data.get("equipment",
                                                       {}).items()}
    data["inventory"] = [LEGACY_ITEMS.get(item_id, item_id)
                         for item_id in data.get("inventory", [])]
    deaths = dict(data.get("deaths", {}))
    if "goblins" in deaths:
        deaths["breeding"] = deaths.get("breeding", 0) + deaths.pop("goblins")
    data["deaths"] = deaths
    data.setdefault("id", new_id())
    data.setdefault("first_name", "")
    data.setdefault("last_name", "")


def upgrade_to_3(data:dict[str, Any]) -> None:
    data.setdefault("needs", {})


def upgrade_to_4(data:dict[str, Any]) -> None:
    data.setdefault("age", DEFAULT_AGE)
    data.setdefault("personality", "")


def upgrade_to_5(data:dict[str, Any]) -> None:
    data.setdefault("profile", {})


def upgrade_to_6(data:dict[str, Any]) -> None:
    data.setdefault("bag_extra", 0)


UPGRADES = {2: upgrade_to_2, 3: upgrade_to_3, 4: upgrade_to_4,
            5: upgrade_to_5, 6: upgrade_to_6}


def migrate_player(data:dict[str, Any]) -> tuple[dict[str, Any], bool]:
    version = data.get("schema_version", 1)
    if version >= SCHEMA_VERSION:
        return data, False
    migrated = dict(data)
    for target in range(version + 1, SCHEMA_VERSION + 1):
        UPGRADES[target](migrated)
    migrated["schema_version"] = SCHEMA_VERSION
    return migrated, True
