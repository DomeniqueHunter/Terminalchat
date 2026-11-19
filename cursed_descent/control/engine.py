from typing import Any

from ..config import CAFE_LOCK, CAFE_RESPAWN_DAYS
from ..models import Message, Player
from ..towns import START_TOWN
from .base import ALWAYS_OPEN, ControlKind
from .discovery import kinds

KEY = "control"
FATE = "enslaved"


def state_of(player:Player) -> dict[str, Any] | None:
    return player.profile.get(KEY) or None


def kind_of(player:Player) -> ControlKind | None:
    state = state_of(player)
    return kinds().get(state["kind"]) if state else None


def holder_of(player:Player) -> str:
    state = state_of(player)
    return state["holder"] if state else ""


def holders(key:str, repository:Any) -> list[Player]:
    found = [player for player in (repository.load(name)
                                   for name in repository.names())
             if player is not None and not player.npc
             and (state_of(player) or {}).get("kind") == key]
    return sorted(found, key=lambda who: state_of(who)["since"])


def texts(player:Player, holder:str, line:str) -> str:
    return line.format(holder=holder, name=player.name)


def witnesses(services:Any, player:Player, line:str) -> list[Message]:
    where = player.profile.get("where", "")
    found = []
    for name in services.repository.names():
        other = services.repository.load(name)
        if (other is None or other.npc or other.name == player.name
                or other.profile.get("town") != player.profile.get("town")
                or other.profile.get("where") != where):
            continue
        found.append(Message(line, other.name, "ambient", where))
    return found


def examine_line(player:Player) -> str:
    kind = kind_of(player)
    if kind is None:
        return ""
    return kind.examine_text.format(name=player.name,
                                    holder=holder_of(player))


def start(services:Any, player:Player, key:str, holder:str,
          **data:Any) -> list[Message]:
    kind = kinds()[key]
    if state_of(player) or services.in_run(player):
        return []
    now = services.world_hours()
    player.profile[KEY] = {
        "kind": key, "holder": holder, "since": now,
        "until": now + kind.hours if kind.hours else 0, "data": data}
    services.repository.save(player)
    public = kind.public_start.format(name=player.name, holder=holder)
    return ([Message(texts(player, holder, kind.start_text), player.name)]
            + witnesses(services, player, public))


def lock(services:Any, player:Player, command:str) -> list[Message]:
    kind = kind_of(player)
    if kind is None or command in ALWAYS_OPEN | kind.open_commands:
        return []
    return [Message(texts(player, holder_of(player), kind.locked_text),
                    player.name)]


def stop(services:Any, player:Player, line:str) -> list[Message]:
    kind = kind_of(player)
    holder = holder_of(player)
    player.profile.pop(KEY, None)
    services.repository.save(player)
    return [Message(texts(player, holder, line), player.name)]


def release(services:Any, player:Player) -> list[Message]:
    kind = kind_of(player)
    if kind is None:
        return [Message("Nobody holds you.", player.name)]
    if not kind.safeword:
        return [Message("There is no safeword here. Only "
                        f"{holder_of(player)} decides.", player.name)]
    return stop(services, player, kind.release_text)


def end(services:Any, player:Player, confirmed:bool) -> list[Message]:
    kind = kind_of(player)
    if kind is None:
        return [Message("Nobody holds you.", player.name)]
    holder = holder_of(player)
    if not kind.can_end:
        return [Message("You cannot end this.", player.name)]
    if not confirmed:
        state_of(player)["data"]["end_ask"] = True
        services.repository.save(player)
        return [Message(texts(player, holder, kind.end_ask),
                        player.name)]
    state = dict(state_of(player))
    slave = make_slave(services, player, kind, state)
    player.profile.pop(KEY, None)
    player.profile.update(town=START_TOWN, where="town")
    player.deaths[FATE] = player.deaths.get(FATE, 0) + 1
    player.last_fate = FATE
    player.records[CAFE_LOCK] = 1
    player.records["respawn_day"] = services.world.day + CAFE_RESPAWN_DAYS
    services.repository.save(player)
    line = texts(slave, holder, kind.end_text)
    public = kind.public_end.format(name=player.name, holder=holder)
    return ([Message(line, player.name)]
            + witnesses(services, player, public))


def make_slave(services:Any, player:Player, kind:ControlKind,
               state:dict[str, Any]) -> Player:
    clone = Player.from_dict(player.to_dict())
    clone.id = Player(name="x").id
    clone.account_id = None
    clone.name = services.repository.unique_handle(f"{player.name} (slave)")
    clone.npc = "slave"
    if not (clone.first_name or clone.last_name):
        clone.first_name = player.name
    clone.equipment = {slot: None for slot in player.equipment}
    clone.inventory = []
    clone.gold = 0
    clone.records = {key: 0 for key in clone.records}
    clone.profile = {"kind": "resident" if kind.home_building else "slave",
                     "town": kind.home_town, "building": kind.home_building,
                     "role": f"Slave of {state['holder']}",
                     "holder": state["holder"], "since": state["since"],
                     "control": kind.key}
    services.repository.add(clone)
    return clone


def die(services:Any, player:Player, fate:str, text:str) -> list[Message]:
    player.profile.pop(KEY, None)
    player.profile.update(town=START_TOWN, where="town")
    player.deaths[fate] = player.deaths.get(fate, 0) + 1
    player.last_fate = fate
    player.last_fate_text = text
    player.records[CAFE_LOCK] = 1
    player.records["respawn_day"] = services.world.day + CAFE_RESPAWN_DAYS
    services.repository.save(player)
    return [Message(text, player.name)]


def tick(services:Any) -> list[Message]:
    messages: list[Message] = []
    now = services.world_hours()
    for name in services.repository.names():
        player = services.repository.load(name)
        state = state_of(player) if player is not None else None
        if state and state["until"] and now >= state["until"]:
            kind = kind_of(player)
            messages += stop(services, player, kind.expire_text)
    return messages


def status(player:Player, services:Any) -> list[Message]:
    kind = kind_of(player)
    if kind is None:
        return [Message("Nobody holds you.", player.name)]
    state = state_of(player)
    holder = state["holder"]
    lines = [texts(player, holder, kind.watch_text)]
    if state["until"]:
        left = max(0.0, state["until"] - services.world_hours())
        lines.append(f"{holder} keeps you for about {left:.0f} more "
                     f"world hours.")
    lines.append("The safeword button frees you." if kind.safeword
                 else "There is no safeword.")
    return [Message("\n".join(lines), player.name)]


def command(services:Any, player:Player,
            args:list[str]) -> list[Message]:
    word = args[0].casefold() if args else ""
    if word in ("release", "safeword"):
        return release(services, player)
    if word == "end":
        return end(services, player, "confirm" in args[1:])
    if word == "cancel" and state_of(player):
        state_of(player)["data"].pop("end_ask", None)
        services.repository.save(player)
    return status(player, services)
