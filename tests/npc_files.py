import json
import re
from pathlib import Path

from cursed_descent.config import STORY_KINDS


def npc_records(root:Path) -> list[tuple[Path, dict]]:
    return [(path, json.loads(path.read_text(encoding="utf-8")))
            for path in sorted((root / "npcs").glob("*.json"))]


def npc_file(root:Path, name:str) -> Path:
    for path, data in npc_records(root):
        if data["name"].casefold() == name.casefold():
            return path
    raise FileNotFoundError(name)


def npc_keys(root:Path, story:bool | None=None) -> set[str]:
    keys = set()
    for _, data in npc_records(root):
        is_story = data.get("profile", {}).get("kind") in STORY_KINDS
        if story is None or story == is_story:
            keys.add(re.sub(r"[^a-z0-9_-]", "_", data["name"].lower()))
    return keys
