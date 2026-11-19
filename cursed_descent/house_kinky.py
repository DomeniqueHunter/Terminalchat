import random
from typing import Any

from .config import (
    HOME_SEAT_SITS, INTIMACY_BOND, INTIMACY_MIN_AGE, INTIMACY_RELIEF,
)
from .content import ITEMS
from .formulas import apply_buff
from .furnishing import rules as furnishing
from .furnishing.scenes import ACTS, AIR_USES, SCENES
from .house_regulars import is_regular
from .models import Message, Player
from .needs_runtime import satisfy
from .npc_menu import bump
from .partner_detail import partner_line
from .preferences import prefs_of
from .towns.last_light_humans.cafe.guests import (
    endurance, fatigue, pressure, smell_drain,
)
from .towns.last_light_humans.cafe.home_seat import guest_of
from .towns.last_light_humans.cafe.seat import air_change, stats_of


YIELD_CHANCE = 0.5
BATH_TEXT = ("You lower yourself into the {item} and let the water take "
             "the day off your skin. By the time you climb out, nothing "
             "of the dungeon clings to you.")
NOT_FOR = "{guest} looks at the {item} and shakes {their} head. 'Not my thing.'"
CLASH = ("Two strong wills: neither of you wants the bottom spot. "
         "[home use {slot} {name} top] asks {name} to yield and kneel, "
         "[home use {slot} {name} bottom] makes you take the {item} "
         "yourself.")
CLASH_SUBS = ("Neither of you wants to lead. [home use {slot} {name} top] "
              "makes you lead anyway, [home use {slot} {name} bottom] "
              "puts you on the {item}.")
YIELDS = "{guest} bites {their} lip, then lowers {their} eyes. 'Fine. You lead.'"
REFUSES = ("{guest} laughs. 'Not tonight. Not under you.' {guest} steps "
           "away from the {item}.")


def bath_use(player:Player, home:dict[str, Any], slot:str,
             repository:Any) -> list[Message]:
    item = furnishing.furniture_of(home)[slot]
    player.sweat = 0
    if "home_bathed" not in player.buffs:
        apply_buff(player, "home_bathed")
    repository.save(player)
    return [Message(BATH_TEXT.format(item=ITEMS[item]["name"]),
                    player.name)]


def first_name(player:Player) -> str:
    return player.first_name or player.name


def possessive(player:Player) -> str:
    return "his" if player.gender == "Male" else "her"


def accepts(guest:Player, act:str, place:str="bottom") -> bool:
    if guest.npc == "" and not is_regular(guest):
        return True
    wanted = "T" if place == "bottom" else "G"
    return wanted in prefs_of(guest)["flow"].get(act, "")


def default_place(host:Player, guest:Player) -> str:
    mine = prefs_of(host)["role"]
    theirs = prefs_of(guest)["role"]
    if mine == theirs and mine != "switch":
        return ""
    if mine == "dom" or theirs == "sub":
        return "top"
    if mine == "sub" or theirs == "dom":
        return "bottom"
    return "top"


def role_fits(guest:Player, place:str) -> bool:
    role = prefs_of(guest)["role"]
    return role != ("dom" if place == "top" else "sub")


def settle(host:Player, guest:Player, place:str, slot:str, item:str,
           rng:random.Random) -> tuple[str, list[str]]:
    name = first_name(guest)
    texts = {"name": guest.first_name or guest.name, "slot": slot,
             "item": ITEMS[item]["name"]}
    if not place:
        place = default_place(host, guest)
        if not place:
            clash = CLASH if prefs_of(host)["role"] == "dom" else CLASH_SUBS
            return "", [clash.format(**texts)]
    guest_place = "bottom" if place == "top" else "top"
    if guest.npc == "" and not is_regular(guest):
        return place, []
    if role_fits(guest, guest_place):
        return place, []
    their = possessive(guest)
    if rng.random() < YIELD_CHANCE:
        return place, [YIELDS.format(guest=name, their=their)]
    return "", [REFUSES.format(guest=name, item=ITEMS[item]["name"])]


def air_scene(host:Player, guest:Player, use:str, place:str,
              rng:random.Random) -> list[str]:
    top, bottom = (host, guest) if place == "top" else (guest, host)
    scene = SCENES[use]
    texts = {"top": first_name(top), "bottom": first_name(bottom)}
    sitter = guest_of({
        "name": top.full_name, "weight": top.body.get("weight", 80),
        "butt": top.body.get("butt", 110), "cruel": 1, "age": top.age,
        "height": top.body.get("height", 170), "gender": top.gender,
        "endowment": top.body.get("endowment", 0)})
    vitality, strength, level = stats_of(bottom)
    lines = [scene["you_top" if place == "top" else "you_bottom"]
             .format(**texts),
             partner_line(ACTS[use], "give" if place == "top"
                          else "receive", host, guest, rng)]
    air = 100
    for number in range(HOME_SEAT_SITS):
        weight = pressure(sitter, rng)
        if use == "foot":
            weight //= 2
        margin = (endurance(vitality, strength, level, rng) - weight
                  - fatigue(number * 2))
        air += air_change(weight, margin) - smell_drain(sitter)
        tier = "easy" if margin >= 4 else "hard" if margin >= 0 else "bad"
        lines.append(scene[tier].format(**texts))
        if air <= 0:
            lines.append(scene["passed"].format(**texts))
            break
    return lines


def bound_scene(host:Player, guest:Player, use:str,
                place:str) -> list[str]:
    top, bottom = (host, guest) if place == "top" else (guest, host)
    texts = {"top": first_name(top), "bottom": first_name(bottom)}
    return [line.format(**texts)
            for line in SCENES[use]["you_top" if place == "top"
                                   else "you_bottom"]]


def kinky_use(player:Player, guest:Player, home:dict[str, Any],
              slot:str, repository:Any, rng:random.Random,
              called:str="", place:str="") -> list[Message]:
    use = furnishing.use_of(home, slot)
    item = furnishing.furniture_of(home)[slot]
    if use not in ACTS:
        return [Message("That piece cannot be used with a guest.",
                        player.name)]
    if min(player.age, guest.age) < INTIMACY_MIN_AGE:
        return [Message(f"{guest.name} is not available.", player.name)]
    place, notes = settle(player, guest, place, slot, item, rng)
    if not place:
        return [Message("\n".join(notes), player.name)]
    guest_place = "bottom" if place == "top" else "top"
    if not accepts(guest, ACTS[use], guest_place):
        return [Message(NOT_FOR.format(
            guest=first_name(guest), item=ITEMS[item]["name"],
            their=possessive(guest)), player.name)]
    if use in AIR_USES:
        lines = air_scene(player, guest, use, place, rng)
    else:
        lines = bound_scene(player, guest, use, place)
    lines = notes + lines
    if called and place == "top":
        lines.append(called)
    satisfy(player.needs, INTIMACY_RELIEF)
    note = bump(guest, player, INTIMACY_BOND)
    if note:
        lines.append(note.strip())
    if "home_afterglow" not in player.buffs:
        apply_buff(player, "home_afterglow")
    repository.save(player)
    repository.save(guest)
    return [Message("\n".join(lines))]
