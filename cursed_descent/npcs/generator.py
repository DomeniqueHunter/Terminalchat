import random
from typing import Any

from ..config import START_STAT_VALUE
from ..models import Player


STATS = ("strength", "agility", "vitality", "intelligence")
MAID_FIRST = (
    "Lotte", "Greta", "Ilse", "Hanne", "Marta", "Elsbeth", "Wilma", "Frieda",
    "Gerda", "Liesl", "Trude", "Resi", "Mina", "Anke", "Hedda", "Imke",
    "Jella", "Katrin", "Luise", "Nelly", "Odile", "Pauline", "Rieke",
    "Sanne", "Thea", "Ulla", "Vroni", "Wanda", "Zita", "Agnes",
)
MAID_LAST = (
    "Brandt", "Holz", "Rauh", "Kessel", "Brunner", "Linde", "Moos",
    "Pfeffer", "Sauer", "Tanner", "Vogel", "Weiss", "Ziegler", "Kraut",
)
MERC_FIRST = (
    "Brom", "Mara", "Vex", "Pip", "Rolf", "Sigrun", "Dag", "Hakon", "Ysolde",
    "Corvin", "Fenna", "Garrick", "Isra", "Joren", "Kestrel", "Lorn",
    "Mirelle", "Nox", "Osric", "Perrin", "Quill", "Rhea", "Sable", "Torvin",
)
MERC_LAST = (
    "Ironhide", "Dawnwhisper", "Nightshade", "Thistlewick", "Ashgrove",
    "Blackwater", "Coldiron", "Duskmantle", "Emberfall", "Flintlock",
    "Greywolf", "Hollowmere", "Stormcrow", "Wyrmbane",
)
MAID_PERSONALITIES = (
    "hard-working, cheerful, stubborn", "polite, graceful, quietly sharp",
    "warm, teasing, endlessly smiling", "shy, careful, never forgets a name",
    "brisk, bossy, secretly soft", "dreamy, clumsy, surprisingly strong",
)
MERC_PERSONALITIES = (
    "gruff, loyal, blunt", "calm, caring, dry humour",
    "sly, restless, flirty", "jumpy, curious, loves explosions",
    "stoic, scarred, speaks rarely", "loud, greedy, fearless",
)
FOCUS_BLURBS = {
    "strength": "hits hard and carries the heavy load",
    "agility": "is quick on the feet and quicker with the hands",
    "vitality": "can take a beating and keeps going",
    "intelligence": "reads the room and casts the spells",
}
MAID_POINTS = (4, 3)
MERC_POINTS = (5, 3)
FREE_POINTS = 3


def roll_name(rng:random.Random, firsts:tuple[str, ...],
              lasts:tuple[str, ...], taken:set[str]) -> tuple[str, str]:
    free = [name for name in firsts if name.casefold() not in taken]
    first = rng.choice(free) if free else (
        f"{rng.choice(firsts)}{rng.randint(2, 99)}")
    return first, rng.choice(lasts)


def roll_stats(rng:random.Random, points:tuple[int, int]
               ) -> tuple[dict[str, int], tuple[str, str]]:
    focus = tuple(rng.sample(STATS, 2))
    values = dict.fromkeys(STATS, 0)
    values[focus[0]] += points[0]
    values[focus[1]] += points[1]
    for _ in range(FREE_POINTS):
        values[rng.choice(STATS)] += 1
    return values, focus


def roll_body(rng:random.Random, gender:str) -> dict[str, Any]:
    build = rng.choice(("Slim", "Average", "Curvy", "Toned", "Muscular"))
    body: dict[str, Any] = {"height": rng.randint(152, 188),
                            "weight": rng.randint(52, 88), "build": build}
    if gender != "Male":
        body["breasts"] = rng.choice(("Small", "Medium", "Large"))
    return body


def make_person(rng:random.Random, taken:set[str], maid:bool,
                gender:str="") -> Player:
    firsts, lasts = ((MAID_FIRST, MAID_LAST) if maid
                     else (MERC_FIRST, MERC_LAST))
    first, last = roll_name(rng, firsts, lasts, taken)
    gender = gender or (rng.choices(("Female", "Herm"), (85, 15))[0] if maid
                        else rng.choice(("Male", "Female", "Herm")))
    values, focus = roll_stats(rng, MAID_POINTS if maid else MERC_POINTS)
    personality = rng.choice(MAID_PERSONALITIES if maid
                             else MERC_PERSONALITIES)
    age = rng.randint(19, 34) if maid else rng.randint(21, 45)
    role = "maid" if maid else "mercenary"
    blurb = (f"A {role} who {FOCUS_BLURBS[focus[0]]}.")
    player = Player(name=first, gender=gender, first_name=first,
                    last_name=last, free_points=0,
                    npc="maid" if maid else "mercenary", age=age,
                    personality=personality, body=roll_body(rng, gender))
    for stat, value in values.items():
        player.stats[stat] = START_STAT_VALUE + value
    if maid:
        player.equipment["chest"] = "maid_uniform"
    player.profile = {"kind": role, "role": blurb, "blurb": blurb,
                      "focus": list(focus),
                      "home": "maid_school" if maid else ""}
    return player


def make_maid(rng:random.Random, taken:set[str]) -> Player:
    return make_person(rng, taken, True)


def make_mercenary(rng:random.Random, taken:set[str],
                   gender:str="") -> Player:
    return make_person(rng, taken, False, gender)
