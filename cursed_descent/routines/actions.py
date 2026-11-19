import json
import random
from importlib import import_module
from pathlib import Path
from typing import Any, NamedTuple

from ..config import NPC_ACTION_SECONDS
from ..models import Message
from ..needs import satisfy
from ..npcs.store import find_local
from .base import Place
from .board import PLACES, WINDOWS, homes
from .discovery import TOWNS_DIR, routines

FILE = "npc_actions.json"
KIND_DIR = Path(__file__).resolve().parent.parent / "town_buildings"
GUEST = "guest"
SLAVE = "slave"
_CACHE: dict[tuple[str, str], dict[str, "Action"]] = {}


class Action(NamedTuple):
    key: str
    weight: int = 1
    needs: str = ""
    text: str = ""
    text_slave: str = ""
    when: str = ""
    hook: str = ""
    gold: tuple[int, int] = (0, 0)
    satisfy: tuple[tuple[str, int], ...] = ()


def read(path:Path) -> dict[str, Action]:
    if not path.exists():
        return {}
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    found = {}
    for key, value in data.items():
        gold = value.get("gold", [0, 0])
        found[key] = Action(
            key, int(value.get("weight", 1)), value.get("needs", ""),
            value.get("text", ""), value.get("text_slave", ""),
            value.get("when", ""), value.get("hook", ""),
            (int(gold[0]), int(gold[1])),
            tuple(value.get("satisfy", {}).items()))
    return found


def actions_for(town:str, building:str) -> dict[str, Action]:
    from ..towns import TOWNS
    folder = TOWNS[town].folder
    cache_key = (folder, building)
    if cache_key not in _CACHE:
        _CACHE[cache_key] = {
            **read(KIND_DIR / building / FILE),
            **read(TOWNS_DIR / folder / building / FILE)}
    return _CACHE[cache_key]


def reset() -> None:
    _CACHE.clear()


def guests_at(town:str, building:str) -> list[str]:
    here = Place(town, building)
    found = routines()
    return [key for key, place in PLACES.items()
            if place == here and key in found
            and GUEST in found[key].uses]


def roster(services, key:str, place:Place) -> list:
    from .. import control
    from ..towns import town_key
    found = []
    for name in services.repository.names():
        player = services.repository.load(name)
        state = control.state_of(player) if player is not None else None
        if (state and state["data"].get("npc") == key
                and town_key(player) == place.town
                and services.where(player) == place.building):
            found.append(player)
    return found


def workers_at(services, place:Place, key:str="") -> dict[str, list]:
    from ..towns import town_key
    workers: dict[str, list] = {}
    for name, shift in services.shifts.items():
        if shift.building != place.building:
            continue
        player = services.repository.load(name)
        if player is not None and town_key(player) == place.town:
            workers.setdefault(shift.job.key, []).append(player)
    slaves = roster(services, key, place) if key else []
    if slaves:
        workers[SLAVE] = slaves
    return workers


def audience(services, place:Place) -> list:
    from ..towns import town_key
    people = (services.repository.load(name)
              for name in services.repository.names())
    return [player for player in people
            if player is not None and not player.npc
            and town_key(player) == place.town
            and services.where(player) == place.building]


def hook_for(place:Place, name:str):
    from ..towns import TOWNS
    folder = TOWNS[place.town].folder
    for module in (f"towns.{folder}.{place.building}.hooks",
                   f"town_buildings.{place.building}.hooks"):
        try:
            found = import_module(f"cursed_descent.{module}")
        except ModuleNotFoundError:
            continue
        if name in found.HOOKS:
            return found.HOOKS[name]
    raise KeyError(f"{place.building}: no hook called {name}")


def available(action:Action, uses:tuple[str, ...], workers:dict,
              key:str, name:str) -> bool:
    if name not in uses or (action.needs and action.needs not in workers):
        return False
    at_home = key not in PLACES
    if not action.when:
        return not at_home
    if not at_home:
        return False
    window = WINDOWS.get(key, "")
    return any(token == "home" and not window or token == window
               for token in action.when.split(","))


def perform(services, key:str, place:Place, rng:random.Random
            ) -> list[Message]:
    uses = routines()[key].uses
    options = actions_for(place.town, place.building)
    workers = workers_at(services, place, key)
    ready = [action for name, action in options.items()
             if available(action, uses, workers, key, name)]
    npc = find_local(services.repository.npc_players(), key)
    if not ready or npc is None:
        return []
    action = rng.choices(ready, [item.weight for item in ready])[0]
    worker = rng.choice(workers[action.needs]) if action.needs else None
    text = action.text.format(npc=npc.first_name,
                              name=worker.name if worker else "")
    messages: list[Message] = []
    if worker is not None:
        pay = rng.randint(*action.gold)
        if pay:
            worker.gold += pay
            text += f" +{pay} gold"
        if action.satisfy:
            satisfy(worker.needs, dict(action.satisfy))
        services.repository.save(worker)
        own = action.text_slave.format(npc=npc.first_name, name="You") \
            if action.text_slave and action.needs == SLAVE else text
        messages.append(Message(own, worker.name, "ambient",
                                place.building))
    if action.needs != SLAVE or worker is None:
        if worker is None:
            messages += [Message(text, player.name, "ambient",
                                 place.building)
                         for player in audience(services, place)]
    else:
        messages += [Message(text, player.name, "ambient", place.building)
                     for player in audience(services, place)
                     if player.name != worker.name]
    if action.hook:
        messages += hook_for(place, action.hook)(
            services, npc, worker, place)
    return messages


class ActionBoard:
    def __init__(self, rng:random.Random | None=None) -> None:
        self.rng = rng or random.Random()
        self.due: dict[str, float] = {}

    def tick(self, services, now:float) -> list[Message]:
        messages: list[Message] = []
        home = homes()
        for key, routine in routines().items():
            if not routine.uses or key not in home:
                continue
            place = PLACES.get(key, home[key])
            due = self.due.setdefault(
                key, now + self.rng.uniform(*NPC_ACTION_SECONDS))
            if now < due:
                continue
            self.due[key] = now + self.rng.uniform(*NPC_ACTION_SECONDS)
            messages += perform(services, key, place, self.rng)
        return messages


def follow(services) -> None:
    from .. import control
    home = homes()
    for name in services.repository.names():
        player = services.repository.load(name)
        state = control.state_of(player) if player is not None else None
        key = state["data"].get("npc", "") if state else ""
        if key not in home:
            continue
        place = PLACES.get(key, home[key])
        if (player.profile.get("town") != place.town
                or player.profile.get("where") != place.building):
            player.profile["town"] = place.town
            player.profile["where"] = place.building
            services.repository.save(player)
