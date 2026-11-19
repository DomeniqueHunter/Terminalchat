import random
from typing import Any

from .config import HOUSE_AIR_DRAIN, HOUSE_AIR_FACTOR, HOUSE_AIR_REF_KG
from .config import HOUSE_CRUSH_KO, SOLE_AIR_SHARE
from .locations.common import pronouns
from .models import Player
from .sex_core import bump_heat, shift_content
from . import sex_sole
from .sex_overlay_texts import DENIED, GRANTED, HOME_CRUSH, LINES


KIND_OF = {"facesitting": "smother", "foot": sex_sole.KIND, "anal": "pen",
           "vaginal": "pen", "pegging": "pen", "ballbusting": "ball",
           "oral": "service", "titfuck": "service", "footjob": "service",
           "bdsm": "bind", "trampling": "trample", "watersports": "pour",
           "scat": "pour", "spanking": "spank"}
DEFAULT_GIVER = {"smother": "stay", "sole": "rest", "pen": "thrust", "ball": "tease",
                 "service": "tease", "bind": "tease", "trample": "step",
                 "pour": "pour", "spank": "spank"}
SIDES = {
    "sole": sex_sole.SIDES,
    "smother": {"giver": ("stay", "lean", "clench", "shift", "raise",
                         "stop"),
                "receiver": ("breath", "lick", "tap", "struggle", "giveup")},
    "pen": {"giver": ("thrust", "spank", "stop"),
            "receiver": ("moan", "more", "mercy")},
    "ball": {"giver": ("kick", "tease", "stop"),
             "receiver": ("beg", "whimper")},
    "service": {"giver": ("tease", "deeper", "stop"),
                "receiver": ("moan", "more", "mercy")},
    "bind": {"giver": ("tighten", "spank", "tease", "stop"),
             "receiver": ("beg", "whimper", "mercy")},
    "trample": {"giver": ("step", "grind", "stop"),
                "receiver": ("whimper", "beg", "mercy")},
    "pour": {"giver": ("pour", "tease", "stop"),
             "receiver": ("swallow", "whimper", "beg")},
    "spank": {"giver": ("spank", "tease", "stop"),
              "receiver": ("moan", "whimper", "mercy")},
}
LABELS = {
    "stay": "Stay", "lean": "Lean in", "clench": "Clench",
    "shift": "Shift weight", "raise": "Raise up", "stop": "Stop",
    "breath": "Gasp for air", "lick": "Lick", "tap": "Tap out",
    "struggle": "Struggle", "giveup": "Give up", "thrust": "Thrust",
    "spank": "Spank", "moan": "Moan", "more": "Beg for more",
    "mercy": "Beg for mercy", "kick": "Kick", "tease": "Tease",
    "beg": "Beg", "whimper": "Whimper", "deeper": "Go deeper",
    "tighten": "Tighten", "step": "Step down", "grind": "Grind down",
    "pour": "Pour", "swallow": "Swallow",
}
FX: dict[str, dict[str, Any]] = {
    "stay": {}, "lean": {"drain": 15, "heat": (1, 0)},
    "clench": {"drain": 20, "heat": (1, 0)},
    "shift": {"air": 10, "heat": (1, 0)},
    "raise": {"air": 30, "safe": True}, "stop": {"end": True},
    "breath": {"air": 20, "safe": True}, "lick": {"heat": (1, 0)},
    "tap": {"plea": "mercy"}, "struggle": {"drain": 10, "heat": (1, 0)},
    "giveup": {"drain": 10, "heat": (1, 1)},
    "thrust": {"heat": (1, 1)}, "spank": {"heat": (0, 1)},
    "moan": {"heat": (1, 0)}, "more": {"plea": "more"},
    "mercy": {"plea": "mercy"}, "kick": {"heat": (0, 1)},
    "tease": {"heat": (1, 0)}, "beg": {"plea": "mercy"},
    "whimper": {"heat": (1, 0)},
    "deeper": {"heat": (1, 1)}, "tighten": {"heat": (1, 1)},
    "step": {"heat": (1, 0)}, "grind": {"heat": (1, 1)},
    "pour": {"heat": (1, 0)}, "swallow": {"heat": (1, 1)},
}
GRANTS = {"more": ("thrust", "spank", "lean", "stay", "kick", "tease")
                + sex_sole.GRANTS["more"],
          "mercy": ("stop", "raise") + sex_sole.GRANTS["mercy"]}
SMOTHERING = ("smother", sex_sole.KIND)
MERCY_ACTION = {"smother": "raise", "sole": "lift"}
AIR_START = 100
LABELS.update(sex_sole.LABELS)
FX.update(sex_sole.FX)


def side_of(overlay:dict[str, Any], player:Player) -> str:
    return "giver" if overlay["giver"] == player.id else "receiver"


def actions_for(overlay:dict[str, Any], player:Player) -> tuple[str, ...]:
    return SIDES[overlay["kind"]][side_of(overlay, player)]


def start(scene:dict[str, Any], act:str, role:str, actor:Player,
          target:Player, where:str="in") -> dict[str, Any] | None:
    kind = KIND_OF.get(act)
    if kind is None:
        scene["overlay"] = None
        return None
    giver, receiver = (actor, target) if role == "give" else (target, actor)
    scene["overlay"] = {"kind": kind, "act": act, "giver": giver.id,
                        "receiver": receiver.id, "plea": "", "where": where}
    scene["acts"] = {}
    scene.pop("order", None)
    scene["sweat"] = (sex_sole.start_value(giver)
                      if kind == sex_sole.KIND else None)
    return scene["overlay"]


def forms(giver:Player, receiver:Player) -> dict[str, str]:
    gs, go, gp = pronouns(giver.gender)
    rs, ro, rp = pronouns(receiver.gender)
    return {"g": giver.name, "r": receiver.name, "gs": gs, "go": go,
            "gp": gp, "rs": rs, "ro": ro, "rp": rp,
            "gself": f"{go}self" if gs != "they" else "themself",
            "rself": f"{ro}self" if rs != "they" else "themself"}


def text_for(overlay:dict[str, Any], action:str, giver:Player,
             receiver:Player, rng:random.Random) -> str:
    for key in ((overlay["act"], action), (overlay["kind"], action),
                ("any", action)):
        if key in LINES:
            return rng.choice(LINES[key]).format(**forms(giver, receiver))
    return ""


def queue(scene:dict[str, Any], player:Player, action:str) -> str:
    overlay = scene.get("overlay")
    if overlay is None:
        return "Nothing is going on that needs an answer."
    if action not in actions_for(overlay, player):
        return "That is not possible right now."
    scene.setdefault("acts", {})[player.id] = action
    return ""


def air_drain(weight:float) -> int:
    low, high = HOUSE_AIR_FACTOR
    factor = max(low, min(high, weight / HOUSE_AIR_REF_KG))
    return round(HOUSE_AIR_DRAIN * factor)


def crush_check(scene:dict[str, Any], giver:Player, receiver:Player,
                rng:random.Random) -> list[str]:
    from .towns.last_light_humans.cafe.content import CRUSH_WHIMPER
    from .towns.last_light_humans.cafe.guests import (
        MAX_SQUEEZE, click_crush, crush_chance, crush_tier,
    )
    chance = crush_chance(giver.body.get("butt", 95),
                          giver.body.get("weight", HOUSE_AIR_REF_KG),
                          MAX_SQUEEZE, receiver.stats.get("vitality", 0),
                          receiver.age)
    if click_crush(chance, rng):
        scene["crushed"] = receiver.id
        scene["air"] = 0
        return [rng.choice(HOME_CRUSH).format(**forms(giver, receiver))]
    tier = crush_tier(chance)
    if not tier:
        return []
    return [rng.choice(CRUSH_WHIMPER[tier]).format(seat=receiver.name)]


def resolve(scene:dict[str, Any], giver:Player, receiver:Player,
            rng:random.Random) -> tuple[list[str], bool]:
    overlay = scene["overlay"]
    acts = scene.get("acts", {})
    scene["acts"] = {}
    given, taken = acts.get(giver.id), acts.get(receiver.id)
    shown = given or DEFAULT_GIVER[overlay["kind"]]
    lines: list[str] = []
    safe, extra, ended = False, 0, False
    for action in (shown, taken):
        if action is None:
            continue
        effect = FX[action]
        lines.append(text_for(overlay, action, giver, receiver, rng))
        if action == "clench":
            lines += crush_check(scene, giver, receiver, rng)
        safe = safe or effect.get("safe", False)
        extra += effect.get("drain", 0)
        ended = ended or effect.get("end", False)
        if "air" in effect and scene["air"] is not None:
            scene["air"] = min(100, scene["air"] + effect["air"])
        if "plea" in effect:
            overlay["plea"] = effect["plea"]
        heat = effect.get("heat")
        if heat is not None:
            side = side_of(overlay, giver if action == shown else receiver)
            gain = heat if side == "giver" else (heat[1], heat[0])
            lines += bump_heat(scene, giver, receiver, gain[0], gain[1],
                               rng, act=overlay["act"],
                               where=overlay.get("where", "in"))
    plea = overlay["plea"]
    if plea and given is not None:
        if given in GRANTS[plea]:
            shift_content(giver, receiver, 2)
            lines.append(rng.choice(GRANTED).format(
                **forms(giver, receiver)))
        else:
            lines.append(rng.choice(DENIED).format(
                **forms(giver, receiver)))
        overlay["plea"] = ""
    if ended:
        scene["overlay"], scene["air"], scene["smothered"] = None, None, ""
        return lines, False
    if overlay["kind"] == sex_sole.KIND:
        more, extra_more = sex_sole.after_beat(
            scene, giver, receiver, shown, taken, rng,
            forms(giver, receiver))
        lines += more
        extra += extra_more
    sitter = giver if scene["smothered"] == receiver.id else receiver
    if scene["air"] is not None and not safe:
        drain = air_drain(sitter.body.get("weight", HOUSE_AIR_REF_KG))
        if overlay["kind"] == sex_sole.KIND:
            drain = round(drain * SOLE_AIR_SHARE)
        scene["air"] = max(0, scene["air"] - drain - extra)
    elif extra and scene["air"] is not None:
        scene["air"] = max(0, scene["air"] - extra)
    return lines, scene["air"] is not None and scene["air"] <= 0
