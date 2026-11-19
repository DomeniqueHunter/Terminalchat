import random
from typing import Any

from .models import Message, Player
from .scenes import DEFAULTS, POSITIONS
from .town_buildings.brothel.practices_content import (
    ACT_ALIASES, ACT_LABELS,
)


ROLES = ("switch", "dom", "sub")
SCENE_ROLE = {"dom": "top", "sub": "bottom"}
BROTHEL_MODE = {"dom": "domina", "sub": "sub"}
CONSENT_MODES = ("ask", "allow", "deny")
USAGE = ("[prefs role dom|sub|switch] [prefs orientation penis|vagina|both] "
         "[prefs consent ask|allow|deny] "
         "[prefs position <name>] "
         "[prefs practice <name> [g|t|gt]] [prefs clear]")
FLOW_CYCLE = ("", "G", "T", "GT")
FLOW_OF_ROLE = {"give": "G", "receive": "T"}


def prefs_of(player:Player) -> dict[str, Any]:
    stored = player.profile.get("prefs", {})
    flow = dict(stored.get("flow", {}))
    for act in stored.get("practices", []):
        flow.setdefault(act, "GT")
    return {"role": stored.get("role", "switch"),
            "positions": list(stored.get("positions", [])),
            "flow": flow, "practices": list(flow)}


def consent_of(player:Player) -> str:
    mode = player.profile.get("consent", "ask")
    return mode if mode in CONSENT_MODES else "ask"


def flow_label(flow:str) -> str:
    return "/".join(flow)


def next_flow(current:str) -> str:
    return FLOW_CYCLE[(FLOW_CYCLE.index(current) + 1) % len(FLOW_CYCLE)]


def scene_defaults(player:Player) -> dict[str, str]:
    prefs = prefs_of(player)
    options = dict(DEFAULTS)
    if prefs["role"] in SCENE_ROLE:
        options["role"] = SCENE_ROLE[prefs["role"]]
    if prefs["positions"]:
        options["position"] = prefs["positions"][0]
    return options


def brothel_mode(player:Player, mode:str) -> str:
    return mode or BROTHEL_MODE.get(prefs_of(player)["role"], "")


def pick_likes(player:Player, pool:list[tuple[str, str]],
               rng:random.Random) -> tuple[tuple[str, str], ...]:
    flow = prefs_of(player)["flow"]
    chosen = [like for like in pool
              if FLOW_OF_ROLE.get(like[1], "") in flow.get(like[0], "")
              ] or pool
    return tuple(rng.sample(chosen, min(2, len(chosen))))


def describe_prefs(player:Player) -> str:
    prefs = prefs_of(player)
    positions = ", ".join(prefs["positions"]) or "any"
    practices = ", ".join(
        f"{ACT_LABELS[act]} {flow_label(flow)}"
        for act, flow in prefs["flow"].items() if act in ACT_LABELS) or "any"
    return (f"Your preferences – role: {prefs['role']}, positions: "
            f"{positions}, practices: {practices}.\n{USAGE}")


def toggle(values:list[str], word:str) -> list[str]:
    return ([value for value in values if value != word]
            if word in values else values + [word])


def prefs_command(player:Player, args:list[str], repository:Any
                  ) -> list[Message]:
    prefs = prefs_of(player)
    kind = args[0].casefold() if args else ""
    word = args[1].casefold().replace("-", "_") if len(args) > 1 else ""
    if kind == "practice":
        word = ACT_ALIASES.get(word, word)
    if kind == "orientation":
        from .orientation import LIKES
        if word in LIKES:
            player.profile["orientation"] = word
            repository.save(player)
        return [Message(f"Your orientation: "
                        f"{player.profile.get('orientation', 'both')} "
                        f"(penis|vagina|both).", player.name)]
    if kind == "consent":
        if word in CONSENT_MODES:
            player.profile["consent"] = word
            repository.save(player)
        return [Message(f"Intimacy requests from other players: "
                        f"{consent_of(player)} (ask|allow|deny).",
                        player.name)]
    if kind == "clear":
        player.profile.pop("prefs", None)
        repository.save(player)
        return [Message("Preferences cleared.", player.name)]
    if kind == "role" and word in ROLES:
        prefs["role"] = word
    elif kind == "position" and word in POSITIONS:
        prefs["positions"] = toggle(prefs["positions"], word)
    elif kind == "practice" and word in ACT_LABELS:
        wanted = args[2].upper() if len(args) > 2 else ""
        current = prefs["flow"].get(word, "")
        flow = wanted if wanted in FLOW_CYCLE[1:] else next_flow(current)
        if flow:
            prefs["flow"][word] = flow
        else:
            prefs["flow"].pop(word, None)
    else:
        return [Message(describe_prefs(player), player.name)]
    player.profile["prefs"] = {"role": prefs["role"],
                               "positions": prefs["positions"],
                               "flow": prefs["flow"]}
    repository.save(player)
    return [Message(describe_prefs(player), player.name)]
