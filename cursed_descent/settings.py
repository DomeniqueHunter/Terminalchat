# Names and files per block (config.py); NPC-backed names come from the NPC json.
import importlib.util
import re
from pathlib import Path
from typing import Any, Callable


TOKEN = re.compile(r"<<([a-z_]+)\.([a-z_]+)>>")
SCAN_FOLDERS = ("locations", "events", "towns")
REGISTRY: dict[str, dict[str, str]] = {}
DEFAULTS: dict[str, dict[str, str]] = {}
NPC_TOKENS: dict[str, dict[str, dict[str, str]]] = {}
PROTOTYPES: dict[str, dict[str, Any]] = {}
LISTENERS: list[Callable[[], None]] = []
state = {"loaded": False}


def read_scope_file(path:Path) -> None:
    name = f"cursed_scope_{path.parent.parent.name}_{path.parent.name}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    PROTOTYPES.update(getattr(module, "NPCS", {}))
    scope = getattr(module, "SCOPE", "")
    if not scope:
        return
    values = dict(module.DEFAULTS)
    tokens = dict(getattr(module, "NPC_TOKENS", {}))
    for key, templates in tokens.items():
        record = module.NPCS[key]
        parts = name_parts(record["first_name"], record["last_name"])
        values.update({token: template.format(**parts).strip()
                       for token, template in templates.items()})
    DEFAULTS[scope] = values
    REGISTRY[scope] = dict(values)
    NPC_TOKENS[scope] = tokens


def name_parts(first:str, last:str) -> dict[str, str]:
    return {"first": first, "last": last,
            "short": first.split()[-1] if first else ""}


def ensure_loaded() -> None:
    if state["loaded"]:
        return
    state["loaded"] = True
    for folder in SCAN_FOLDERS:
        for path in sorted((Path(__file__).parent / folder).glob("*/config.py")):
            read_scope_file(path)
    for path in sorted((Path(__file__).parent / "towns").glob("*/*/npcs.py")):
        read_scope_file(path)
    for key, record in PROTOTYPES.items():
        register_prototype(key, record["first_name"], record["last_name"])


def prototype(key:str) -> dict[str, Any]:
    ensure_loaded()
    return PROTOTYPES[key]


def get(scope:str) -> dict[str, str]:
    ensure_loaded()
    return REGISTRY[scope]


def defaults(scope:str) -> dict[str, str]:
    ensure_loaded()
    return DEFAULTS[scope]


def set_names(key:str, first:str, last:str) -> None:
    names = REGISTRY.setdefault("npc", {})
    names[f"{key}_first"] = first
    names[f"{key}_last"] = last
    names[f"{key}_short"] = first.split()[-1] if first else ""


def register_prototype(key:str, first:str, last:str) -> None:
    set_names(key, first, last)
    DEFAULTS.setdefault("npc", {}).update(
        {name: value for name, value in REGISTRY["npc"].items()
         if name.startswith(f"{key}_")})


def on_bind(listener:Callable[[], None]) -> None:
    LISTENERS.append(listener)


def bind_npcs(repository:Any) -> None:
    ensure_loaded()
    npcs = {npc.npc: npc for npc in repository.npc_players()}
    for key, npc in npcs.items():
        if key and key != "maid":
            set_names(key, npc.first_name, npc.last_name)
    for scope, mapping in NPC_TOKENS.items():
        for key, templates in mapping.items():
            npc = npcs.get(key)
            if npc is None:
                continue
            parts = name_parts(npc.first_name, npc.last_name)
            for token, template in templates.items():
                REGISTRY[scope][token] = template.format(**parts).strip()
    for listener in LISTENERS:
        listener()


def replace(match:re.Match) -> str:
    scope, key = match.groups()
    return REGISTRY.get(scope, {}).get(key, match.group(0))


def fill(text:str) -> str:
    if "<<" not in text:
        return text
    ensure_loaded()
    return TOKEN.sub(replace, text)


def fill_data(value:Any) -> Any:
    if isinstance(value, str):
        return fill(value)
    if isinstance(value, dict):
        return {key: fill_data(item) for key, item in value.items()}
    if isinstance(value, list):
        return [fill_data(item) for item in value]
    if isinstance(value, tuple):
        return tuple(fill_data(item) for item in value)
    return value
