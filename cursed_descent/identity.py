import uuid
from typing import Any


def new_id() -> str:
    return uuid.uuid4().hex


def character_key(entry:dict[str, Any]) -> str:
    return entry.get("char_id") or entry["name"]


def is_character(entry:dict[str, Any], char_id:str, name:str) -> bool:
    entry_id = entry.get("char_id")
    if entry_id:
        return entry_id == char_id
    return entry["name"] == name


def same_character(first:dict[str, Any], second:dict[str, Any]) -> bool:
    return character_key(first) == character_key(second)
