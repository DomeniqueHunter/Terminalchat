import random
from typing import Any

from .config import HUNG_GENDERS, SEX_CONTENT_MAX, SEX_HEAT_MAX
from .models import Player
from .preferences import FLOW_OF_ROLE, prefs_of
from .locations.common import pronouns
from .sex_texts import BOTH, CONTENT_LINES, DESTINATIONS, ORGASM


HEAT = {
    "anal": (1, 1), "vaginal": (1, 1), "oral": (0, 1),
    "watersports": (0, 1), "facesitting": (1, 2), "foot": (1, 2),
    "scat": (1, 1), "footjob": (0, 1), "trampling": (0, 1),
    "ballbusting": (0, 1), "pegging": (0, 1), "spanking": (1, 1),
    "titfuck": (2, 1), "bdsm": (1, 1),
}
OUTCOME_DELTA = {"met": 2, "free": 1, "ignored": 0, "dislike_asked": -2,
                 "dislike_free": -1}


def content_of(first:Player, second:Player) -> int:
    return first.profile.get("content", {}).get(second.id, 0)


def shift_content(first:Player, second:Player, delta:int) -> int:
    value = max(0, min(SEX_CONTENT_MAX, content_of(first, second) + delta))
    first.profile.setdefault("content", {})[second.id] = value
    second.profile.setdefault("content", {})[first.id] = value
    return value


def tier_of(value:int) -> str:
    return ("cold" if value <= 6 else "warm" if value <= 13 else "devoted")


def share(first:Player, second:Player) -> float:
    return content_of(first, second) / SEX_CONTENT_MAX


def obedience(first:Player, second:Player) -> float:
    return 0.4 + 0.6 * share(first, second)


def mercy(first:Player, second:Player) -> float:
    return 0.15 + 0.7 * share(first, second)


def wish_chance(first:Player, second:Player) -> float:
    return 0.2 + 0.5 * share(first, second)


def disliked(sub:Player, act:str, sub_role:str) -> bool:
    flow = prefs_of(sub)["flow"]
    return bool(flow) and FLOW_OF_ROLE[sub_role] not in flow.get(act, "")


def outcome_of(wish:dict[str, Any] | None, act:str, bad:bool) -> str:
    if wish is None:
        return "dislike_free" if bad else "free"
    if wish["act"] == act:
        return "met"
    return "dislike_asked" if bad else "ignored"


def rate(dom:Player, sub:Player, wish:dict[str, Any] | None, act:str,
         sub_role:str, rng:random.Random) -> list[str]:
    outcome = outcome_of(wish, act, disliked(sub, act, sub_role))
    value = shift_content(dom, sub, OUTCOME_DELTA[outcome])
    line = rng.choice(CONTENT_LINES[tier_of(value)][outcome]).format(
        dom=dom.name, sub=sub.name)
    sign = f"{OUTCOME_DELTA[outcome]:+d}" if OUTCOME_DELTA[outcome] else "±0"
    return [f"{line} (♥ {value}/{SEX_CONTENT_MAX}, {sign})"]


def heat_of(scene:dict[str, Any], player:Player) -> int:
    return scene.setdefault("heat", {}).get(player.id, 0)


def heat_bar(value:int) -> str:
    return f"{'█' * value}{'░' * (SEX_HEAT_MAX - value)} {value}/{SEX_HEAT_MAX}"


def destination_kind(act:str, giver_comes:bool, where:str) -> str:
    if act in ("anal", "vaginal"):
        return (("pen_in" if where == "in" else "pen_on") if giver_comes
                else "pen_recv")
    table = {"pegging": ("sheets", "pen_recv"),
             "oral": ("sheets", "mouth" if where == "in" else "face"),
             "titfuck": ("chest", "self"), "footjob": ("sheets", "feet"),
             "facesitting": ("face", "self"), "foot": ("face", "self"),
             "ballbusting": ("floor", "floor"),
             "trampling": ("floor", "floor"), "spanking": ("sheets",
                                                          "sheets"),
             "bdsm": ("body", "body"), "scat": ("floor", "floor"),
             "watersports": ("self", "self")}
    pair = table.get(act, ("sheets", "sheets"))
    return pair[0] if giver_comes else pair[1]


def destination_text(act:str, comer:Player, other:Player,
                     giver_comes:bool, where:str,
                     rng:random.Random) -> str:
    kind = destination_kind(act, giver_comes, where)
    own = pronouns(comer.gender)[2]
    phrase = rng.choice(DESTINATIONS[kind]).format(other=other.name,
                                                    own=own)
    verb = "load goes" if comer.gender in HUNG_GENDERS else "release goes"
    return f"{comer.name}'s {verb} {phrase}."


def add_heat(scene:dict[str, Any], act:str, role:str, actor:Player,
             target:Player, rng:random.Random,
             where:str="in") -> list[str]:
    giver_gain, receiver_gain = HEAT.get(act, (0, 0))
    giver, receiver = (actor, target) if role == "give" else (target, actor)
    return bump_heat(scene, giver, receiver, giver_gain, receiver_gain, rng,
                     actor, target, act, where)


def bump_heat(scene:dict[str, Any], giver:Player, receiver:Player,
              giver_gain:int, receiver_gain:int, rng:random.Random,
              actor:Player | None=None,
              target:Player | None=None, act:str="",
              where:str="in") -> list[str]:
    actor, target = actor or giver, target or receiver
    heat = scene.setdefault("heat", {})
    heat[giver.id] = heat.get(giver.id, 0) + giver_gain
    heat[receiver.id] = heat.get(receiver.id, 0) + receiver_gain
    came = [person for person in (giver, receiver)
            if heat[person.id] >= SEX_HEAT_MAX]
    lines: list[str] = []
    for person in came:
        heat[person.id] = 0
        pool = "cum" if person.gender in HUNG_GENDERS else "squirt"
        other = receiver if person is giver else giver
        lines.append("💦 " + rng.choice(ORGASM[pool]).format(
            name=person.name) + " " + destination_text(
                act, person, other, person is giver, where, rng))
    if len(came) == 2:
        lines.append(rng.choice(BOTH))
    lines.append(f"🔥 {actor.name} {heat_bar(heat[actor.id])} · "
                 f"{target.name} {heat_bar(heat[target.id])}")
    return lines
