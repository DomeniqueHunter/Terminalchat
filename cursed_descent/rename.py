from typing import Any

from .storage import PlayerRepository, read_json, write_json


def replace_text(value:Any, old:str, new:str) -> Any:
    if isinstance(value, str):
        return new if value == old else value
    if isinstance(value, list):
        return [replace_text(entry, old, new) for entry in value]
    if isinstance(value, dict):
        return {key: replace_text(entry, old, new)
                for key, entry in value.items()}
    return value


def fix_files(repository:PlayerRepository, skip:str, old:str,
              new:str) -> int:
    paths = list(repository.accounts_dir.glob("*/*.json"))
    paths += list(repository.npc_dir.glob("*.json"))
    changed = 0
    for path in paths:
        if path.stem == skip:
            continue
        data = read_json(path, {})
        fixed = replace_text(data, old, new)
        if fixed != data:
            write_json(path, fixed)
            changed += 1
            row = repository.store.character_by_id(path.stem)
            if row is not None:
                repository.cache.pop(row["key"], None)
                repository.known.pop(row["id"], None)
    return changed


def fix_houses(repository:PlayerRepository, old:str, new:str) -> None:
    store = repository.houses
    for house_id, house in list(store.houses.items()):
        store.houses[house_id] = replace_text(house, old, new)
    store.flush()


def fix_mail(ledger:Any, old:str, new:str) -> None:
    for box in ledger.boxes.values():
        box.inbox = replace_text(box.inbox, old, new)
        box.sent = replace_text(box.sent, old, new)
    ledger.pending = replace_text(ledger.pending, old, new)
    ledger.save()


def rename_character(repository:PlayerRepository, ledger:Any, old:str,
                     new:str) -> str:
    new = " ".join(new.split())
    player = repository.load(old)
    if player is None:
        return f"There is no character called {old}."
    if not new or not repository.key(new).strip("_"):
        return "The new name is not usable."
    clash = repository.row_of(new)
    if clash is not None and clash["id"] != player.id:
        return f"The name {new} is already taken."
    old_name = player.name
    old_key = repository.key(old_name)
    repository.cache.pop(old_key, None)
    player.name = new
    repository.add(player)
    fix_files(repository, player.id, old_name, new)
    fix_houses(repository, old_name, new)
    if ledger is not None:
        fix_mail(ledger, old_name, new)
    return f"✎ {old_name} is now called {new}."
