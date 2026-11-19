import json
import re
import uuid
from pathlib import Path
from typing import Any

from .clock import timestamp
from .accounts import AccountStore
from .config import (
    ACCOUNTS_DIR_NAME, GRAVEYARD_DIR_NAME, LEADERBOARD_FILE_NAME,
    LEADERBOARD_SIZE, LOCAL_ACCOUNT_ID, NPC_DIR_NAME, STORY_KINDS,
    TEMP_MONSTER_DIR_NAME,
)
from .inventory import sort_inventory
from .migrations import migrate_player
from .models import Player


def write_json(path:Path, data:Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    tmp_path.replace(path)


def read_json(path:Path, default:Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


MIN_ID_PREFIX = 6


class TempMonsters:
    def __init__(self, data_path:Path, graveyard_dir:Path) -> None:
        self.directory = data_path / TEMP_MONSTER_DIR_NAME
        self.graveyard_dir = graveyard_dir

    def add(self, entry:dict[str, Any]) -> str:
        monster_id = uuid.uuid4().hex[:8]
        write_json(self.directory / f"{monster_id}.json",
                   {**entry, "id": monster_id, "created": timestamp()})
        return monster_id

    def all(self) -> list[dict[str, Any]]:
        if not self.directory.exists():
            return []
        return [read_json(path, {})
                for path in sorted(self.directory.glob("*.json"))]

    def get(self, monster_id:str) -> dict[str, Any] | None:
        return read_json(self.directory / f"{monster_id}.json", None)

    def remove(self, monster_id:str) -> bool:
        path = self.directory / f"{monster_id}.json"
        existed = path.exists()
        path.unlink(missing_ok=True)
        return existed

    def die(self, monster_id:str, reason:str) -> bool:
        entry = self.get(monster_id)
        if entry is None:
            return False
        name = re.sub(r"[^a-z0-9_-]", "_", entry.get("name", "x").lower())
        stamp = re.sub(r"[^0-9]", "", timestamp())
        write_json(self.graveyard_dir / f"monster_{name}_{stamp}_"
                   f"{monster_id}.json",
                   {"reason": reason, "buried": timestamp(),
                    "monster": entry})
        return self.remove(monster_id)


class PlayerRepository:
    def __init__(self, data_path:Path) -> None:
        self.data_path = data_path
        self.accounts_dir = data_path / ACCOUNTS_DIR_NAME
        self.npc_dir = data_path / NPC_DIR_NAME
        self.graveyard_dir = data_path / GRAVEYARD_DIR_NAME
        self.store = AccountStore(data_path)
        self.cache: dict[str, Player] = {}
        self.known: dict[str, tuple] = {}
        self.aliases: dict[str, str] = {}
        self.temp_monsters = TempMonsters(data_path, self.graveyard_dir)
        from .house_store import HouseStore
        from .item_store import ItemStore
        self.items = ItemStore(data_path)
        self.houses = HouseStore(data_path, self)
        self.reconcile_npcs()

    def reconcile_npcs(self) -> None:
        from .settings import PROTOTYPES, ensure_loaded
        ensure_loaded()
        files = sorted(self.npc_dir.glob("*.json")) if (
            self.npc_dir.exists()) else []
        seen = set()
        self.aliases = {}
        for path in files:
            data = read_json(path, {})
            name, char_id = data.get("name", ""), data.get("id", path.stem)
            if not name:
                continue
            seen.add(char_id)
            prototype = PROTOTYPES.get(data.get("npc", ""))
            if prototype and self.key(prototype["name"]) != self.key(name):
                self.aliases[self.key(prototype["name"])] = char_id
            row = self.store.character_by_id(char_id)
            key = self.key(name)
            if row is None or row["key"] != key or row["account_id"]:
                clash = self.store.character_by_key(key)
                if clash is not None and clash["id"] != char_id:
                    continue
                self.store.add_character(char_id, None, name, key, True)
                self.cache.pop(key, None)
        for row in self.store.characters(False):
            if row["id"] not in seen and not row["account_id"]:
                self.store.remove_character(row["id"])

    def reload(self, rows:list, busy:set[str]) -> tuple[int, list[str]]:
        done, skipped = 0, []
        for row in rows:
            if row["handle"] in busy:
                skipped.append(row["handle"])
                continue
            self.cache.pop(row["key"], None)
            self.known.pop(row["id"], None)
            done += 1
        return done, skipped

    @staticmethod
    def key(name:str) -> str:
        return re.sub(r"[^a-z0-9_-]", "_", name.strip().lower())

    def file_for(self, char_id:str, account_id:str | None) -> Path:
        if account_id:
            return self.accounts_dir / account_id / f"{char_id}.json"
        return self.npc_dir / f"{char_id}.json"

    def row_of(self, name:str):
        key = self.key(name)
        row = self.store.character_by_key(key)
        if row is None and key in self.aliases:
            return self.store.character_by_id(self.aliases[key])
        return row

    def path(self, name:str) -> Path:
        row = self.row_of(name)
        if row is None or row["npc"]:
            return self.accounts_dir / "_missing" / f"{self.key(name)}.json"
        return self.file_for(row["id"], row["account_id"])

    def npc_path(self, name:str) -> Path:
        row = self.row_of(name)
        if row is None or not (row["npc"] or not row["account_id"]):
            return self.npc_dir / f"_missing_{self.key(name)}.json"
        return self.file_for(row["id"], row["account_id"])

    def save_path(self, player:Player) -> Path:
        return self.file_for(player.id, self.account_for(player))

    def account_for(self, player:Player) -> str | None:
        if player.account_id:
            return player.account_id
        return None if player.npc else LOCAL_ACCOUNT_ID

    def is_story(self, player:Player) -> bool:
        return bool(player.npc
                    and player.profile.get("kind") in STORY_KINDS)

    def exists(self, name:str) -> bool:
        return self.key(name) in self.cache or self.row_of(name) is not None

    def load(self, name:str) -> Player | None:
        key = self.key(name)
        if key in self.cache:
            return self.cache[key]
        row = self.row_of(name)
        if row is None:
            return None
        key = row["key"]
        if key in self.cache:
            return self.cache[key]
        data = read_json(self.file_for(row["id"], row["account_id"]), None)
        if data is None:
            return None
        migrated, changed = migrate_player(data)
        player = Player.from_dict(migrated)
        player.id = row["id"]
        player.account_id = row["account_id"]
        self.items.pull_player(player)
        sort_inventory(player)
        self.cache[key] = player
        self.known[player.id] = (player.account_id, key, bool(player.npc))
        if changed:
            self.save(player)
        return player

    def names(self) -> list[str]:
        return [row["handle"] for row in self.store.characters(True)]

    def npc_players(self) -> list[Player]:
        players = (self.load(row["handle"])
                   for row in self.store.characters(False))
        return [player for player in players if player is not None]

    def recruitable(self) -> list[Player]:
        return [player for player in self.npc_players()
                if not self.is_story(player)]

    def graduates(self) -> list[Player]:
        return [player for player in self.npc_players()
                if player.npc == "maid" and player.profile.get("graduate")]

    def release(self, player:Player) -> None:
        self.cache.pop(self.key(player.name), None)
        self.known.pop(player.id, None)
        self.save_path(player).unlink(missing_ok=True)
        self.store.remove_character(player.id)

    def bury(self, player:Player, reason:str) -> Path:
        stamp = re.sub(r"[^0-9]", "", timestamp())
        path = self.graveyard_dir / f"{self.key(player.name)}_{stamp}.json"
        count = 1
        while path.exists():
            count += 1
            path = path.with_name(
                f"{self.key(player.name)}_{stamp}_{count}.json")
        write_json(path, {"reason": reason, "buried": timestamp(),
                          "player": player.to_dict()})
        return path

    def convert(self, name:str, npc:str) -> bool:
        player = self.load(name)
        if player is None:
            return False
        player.npc = npc
        self.save(player)
        return True

    def id_map(self) -> dict[str, str]:
        return {row["key"]: row["id"] for row in self.store.characters(True)}

    def load_by_id(self, char_id:str) -> Player | None:
        row = self.store.character_by_id(char_id)
        return self.load(row["handle"]) if row is not None else None

    def copies_of(self, char_id:str) -> list[Player]:
        player = self.load_by_id(char_id)
        return [player] if player is not None else []

    def unique_handle(self, wanted:str) -> str:
        wanted = wanted.strip()
        if not self.exists(wanted):
            return wanted
        number = 2
        while self.exists(f"{wanted}#{number}"):
            number += 1
        return f"{wanted}#{number}"

    def resolve(self, ref:str) -> str:
        ref = ref.strip()
        if self.exists(ref):
            return self.load(ref).name
        if len(ref) >= MIN_ID_PREFIX:
            found = [row["handle"] for row in self.store.db.execute(
                "SELECT handle FROM characters WHERE id LIKE ?",
                (ref.lower() + "%",)).fetchall()]
            if len(found) == 1:
                return found[0]
        return ref

    def add(self, player:Player) -> None:
        self.cache[self.key(player.name)] = player
        self.save(player)

    def register(self, player:Player) -> None:
        key = self.key(player.name)
        account = self.account_for(player)
        player.account_id = player.account_id or account
        now = (player.account_id, key, bool(player.npc))
        if self.known.get(player.id) == now:
            return
        clash = self.store.character_by_key(key)
        if clash is not None and clash["id"] != player.id:
            raise ValueError(f"The name {player.name} is already taken.")
        old = self.known.get(player.id)
        self.store.add_character(player.id, player.account_id,
                                 player.name, key, bool(player.npc))
        if old is not None and old[0] != player.account_id:
            self.file_for(player.id, old[0]).unlink(missing_ok=True)
        self.known[player.id] = now

    def save(self, player:Player) -> None:
        sort_inventory(player)
        self.items.sync_player(player)
        self.register(player)
        write_json(self.save_path(player), player.to_dict())
        self.houses.flush()


class Leaderboard:
    def __init__(self, data_path:Path) -> None:
        self.path = data_path / LEADERBOARD_FILE_NAME

    def entries(self) -> list[dict[str, Any]]:
        return read_json(self.path, [])

    def add_run(self, stage:int, names:list[str]) -> int:
        entries = self.entries()
        entry = {
            "stage": stage,
            "players": names,
            "date": timestamp(),
        }
        entries.append(entry)
        entries.sort(key=lambda item: item["stage"], reverse=True)
        entries = entries[:LEADERBOARD_SIZE]
        write_json(self.path, entries)
        return entries.index(entry) + 1 if entry in entries else 0
