import random
from pathlib import Path
from typing import Any

from ...clock import timestamp
from ...config import MAID_HITS
from ...models import Player
from ...storage import read_json, write_json


LEDGER_FILE_NAME = "buster_ledger.json"
STOOD = "stood"


def result_word(result:str) -> str:
    if result == STOOD:
        return "stood the hundred"
    return "was " + result.removeprefix("paddle_").replace("_", " ")


class BusterLedger:
    def __init__(self, data_path:Path) -> None:
        self.path = data_path / LEDGER_FILE_NAME
        data = read_json(self.path, {})
        self.entries: list[dict[str, Any]] = data.get("entries", [])
        self.meta: dict[str, int] = data.get("meta", {})

    def save(self) -> None:
        write_json(self.path, {"entries": self.entries, "meta": self.meta})

    def add(self, player:Player, result:str, hit:int, run_id:str,
            joined:bool=False) -> None:
        self.entries.append({
            "name": player.name, "gender": player.gender,
            "date": timestamp(), "run": run_id, "result": result,
            "hit": hit, "joined": joined})
        if joined:
            self.bump("joined")
        self.save()

    def bump(self, key:str) -> None:
        self.meta[key] = self.meta.get(key, 0) + 1
        self.save()

    def total(self) -> int:
        return len(self.entries)

    def stood(self) -> int:
        return sum(1 for entry in self.entries if entry["result"] == STOOD)

    def fallen(self) -> int:
        return self.total() - self.stood()

    def best_hit(self, name:str) -> int:
        hits = [entry["hit"] for entry in self.entries
                if entry["name"] == name]
        return max(hits, default=0)

    def best(self) -> dict[str, Any] | None:
        return max(self.entries, key=lambda entry: entry["hit"],
                   default=None)

    def worst(self) -> dict[str, Any] | None:
        fallen = [entry for entry in self.entries
                  if entry["result"] != STOOD]
        return min(fallen, key=lambda entry: entry["hit"], default=None)

    def last(self) -> dict[str, Any] | None:
        return self.entries[-1] if self.entries else None

    def sample(self, count:int, rng:random.Random) -> list[dict[str, Any]]:
        return rng.sample(self.entries, min(count, len(self.entries)))

    def summary(self) -> str:
        return (f"{self.total()} ladies, {self.fallen()} fell, "
                f"{self.stood()} stood the {MAID_HITS}")
