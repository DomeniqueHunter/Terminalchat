import random
from typing import Any

from .body import DEFAULT_BODY
from .models import Player
from .town_buildings.regular_talk import regular_talk
from .town_buildings.visits import ask_address


PREFIX = "reg:"


def regular_player(building:str, record:dict[str, Any]) -> Player:
    body = dict(DEFAULT_BODY)
    for key in ("bust", "endowment", "weight", "height", "butt"):
        if key in record:
            body[key] = record[key]
    return Player(name=record["name"], id=f"{PREFIX}{building}:"
                  f"{record['name'].casefold()}",
                  first_name=record["name"], npc="regular",
                  gender=record.get("gender", "Female"),
                  age=record.get("age", 30), body=body,
                  profile=({"prefs": record["prefs"]}
                           if "prefs" in record else {}))


def is_regular(player:Player) -> bool:
    return player.id.startswith(PREFIX)


def find_regular(regulars:Any, name:str) -> Player | None:
    if regulars is None or not name.strip():
        return None
    found = regulars.find(name)
    if found is None or not ask_address(found[1]):
        return None
    return regular_player(*found)


def regular_by_id(regulars:Any, entry_id:str) -> Player | None:
    if regulars is None or not entry_id.startswith(PREFIX):
        return None
    building, _, name = entry_id[len(PREFIX):].partition(":")
    record = regulars.get(building, name)
    return regular_player(building, record) if record else None


def regular_chat(other:Player, regulars:Any, rng:random.Random) -> str:
    building, _, name = other.id[len(PREFIX):].partition(":")
    record = regulars.get(building, name) or {"name": other.name}
    return regular_talk(record, building, rng)


class SavingOnly:
    def __init__(self, repository:Any) -> None:
        self.repository = repository

    def save(self, player:Player) -> None:
        if not is_regular(player):
            self.repository.save(player)

    def __getattr__(self, name:str) -> Any:
        return getattr(self.repository, name)
