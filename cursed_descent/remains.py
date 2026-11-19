import random
import uuid
from pathlib import Path
from typing import Any

from .clock import timestamp
from .config import BOSS_INTERVAL, REMAINS_FILE_NAME, REMAINS_LIMIT
from .content import FATE_LABELS
from .identity import character_key, is_character, same_character
from .items import item_state, restore_item
from .storage import PlayerRepository, read_json, write_json


def unique_names(entries:list[dict[str, Any]]) -> list[dict[str, Any]]:
    newest: dict[str, dict[str, Any]] = {}
    for entry in entries:
        newest[character_key(entry)] = entry
    return list(newest.values())


class RemainsLog:
    def __init__(self, data_path:Path) -> None:
        self.path = data_path / REMAINS_FILE_NAME
        self.entries: list[dict[str, Any]] = read_json(self.path, [])
        for entry in self.entries:
            entry.setdefault("id", uuid.uuid4().hex)

    def backfill_ids(self, ids_by_key:dict[str, str]) -> None:
        changed = False
        for entry in self.entries:
            if entry.get("char_id"):
                continue
            char_id = ids_by_key.get(PlayerRepository.key(entry["name"]))
            if char_id:
                entry["char_id"] = char_id
                changed = True
        if changed:
            self.save()

    def save(self) -> None:
        self.entries = self.entries[-REMAINS_LIMIT:]
        write_json(self.path, self.entries)

    def add(self, name:str, gender:str, fate:str, stage:int, killer:str,
            tribe:str, run_id:str, detail:str="",
            location:int=0, soul:str="",
            victim:dict[str, Any] | None=None,
            char_id:str="",
            hoard:list[dict[str, Any]] | None=None) -> None:
        self.entries.append({
            "id": uuid.uuid4().hex,
            "char_id": char_id,
            "name": name,
            "gender": gender,
            "fate": fate,
            "stage": stage,
            "killer": killer,
            "tribe": tribe,
            "run": run_id,
            "item": None,
            "looted": False,
            "date": timestamp(),
            "detail": detail,
            "location": location,
            "soul": soul,
            "victim": victim or {},
            "hoard": hoard or [],
        })
        self.save()

    def attach_item(self, name:str, run_id:str, item_id:str,
                    char_id:str="") -> bool:
        state = item_state(item_id)
        for entry in reversed(self.entries):
            if (is_character(entry, char_id, name)
                    and entry["run"] == run_id):
                entry["item"] = str(item_id)
                entry["item_state"] = state
                self.save()
                return True
        return False

    def pick(self, stage:int, run_id:str,
             seen:set[str]) -> dict[str, Any] | None:
        block = (stage - 1) // BOSS_INTERVAL
        candidates = [entry for entry in self.entries
                      if entry["run"] != run_id and entry["id"] not in seen
                      and entry["fate"] not in ("consort", "staked", "sacked")
                      and (entry["stage"] - 1) // BOSS_INTERVAL == block]
        exact = [entry for entry in candidates if entry["stage"] == stage]
        pool = exact or candidates
        if not pool:
            return None
        with_items = [entry for entry in pool
                      if entry["item"] and not entry["looted"]]
        return random.choice(with_items or pool)

    def consorts(self, run_id:str) -> list[dict[str, Any]]:
        return unique_names([entry for entry in self.entries
                             if entry["fate"] == "consort"
                             and not entry.get("freed")
                             and entry["run"] != run_id])

    def skeletons(self, run_id:str, fates:tuple) -> list[dict[str, Any]]:
        return unique_names([entry for entry in self.entries
                             if entry["fate"] in fates
                             and not entry.get("laid_to_rest")
                             and entry["run"] != run_id])

    def mark_name(self, entry_id:str, flag:str,
                  fates:tuple) -> dict[str, Any] | None:
        target = next((entry for entry in self.entries
                       if entry["id"] == entry_id), None)
        if target is None:
            return None
        for entry in self.entries:
            if same_character(entry, target) and entry["fate"] in fates:
                entry[flag] = True
        self.save()
        return target

    def lay_to_rest(self, entry_id:str,
                    fates:tuple) -> dict[str, Any] | None:
        return self.mark_name(entry_id, "laid_to_rest", fates)

    def free(self, entry_id:str) -> dict[str, Any] | None:
        return self.mark_name(entry_id, "freed", ("consort",))

    def has_stew(self, entry:dict[str, Any], fates:tuple) -> bool:
        return entry["fate"] in fates and not entry.get("stew_gone")

    def finish_stew(self, entry:dict[str, Any]) -> None:
        entry["stew_gone"] = True
        self.save()

    def has_dairy(self, entry:dict[str, Any]) -> bool:
        return entry["fate"] == "dairy" and not entry.get("dairy_gone")

    def finish_dairy(self, entry:dict[str, Any]) -> None:
        entry["dairy_gone"] = True
        self.save()

    def loot(self, entry:dict[str, Any]) -> str | None:
        if not entry["item"] or entry["looted"]:
            return None
        entry["looted"] = True
        self.save()
        return restore_item(entry["item"], entry.get("item_state"))

    def graveyard(self, count:int=10) -> list[str]:
        lines = ["🪦 The Wall of the Fallen"]
        if not self.entries:
            return lines + ["  No names yet. The dungeon is patient."]
        for entry in reversed(self.entries[-count:]):
            label = FATE_LABELS.get(entry["fate"], entry["fate"])
            detailed = f"{entry['fate']}_{entry.get('detail', '')}"
            label = FATE_LABELS.get(detailed, label)
            if entry.get("freed"):
                label += " (freed)"
            if entry.get("laid_to_rest"):
                label += " (bones laid to rest)"
            lines.append(f"  {entry['name']} – {label} on stage "
                         f"{entry['stage']} by {entry['killer']} "
                         f"({entry['date']})")
        return lines
