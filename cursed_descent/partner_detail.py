import random

from .config import HUNG_GENDERS, VAGINA_GENDERS
from .models import Player
from .town_buildings.brothel.practices_anatomy import anatomy


FOCUS = {
    ("anal", "give"): ("butt", "cock"),
    ("anal", "receive"): ("cock", "butt"),
    ("vaginal", "give"): ("pussy", "bust"),
    ("vaginal", "receive"): ("cock", "build"),
    ("oral", "give"): ("cock", "pussy"),
    ("oral", "receive"): ("build", "bust"),
    ("titfuck", "give"): ("cock", "build"),
    ("titfuck", "receive"): ("bust", "build"),
    ("facesitting", "give"): ("build", "butt"),
    ("facesitting", "receive"): ("butt", "build"),
    ("spanking", "give"): ("butt", "build"),
    ("spanking", "receive"): ("build", "bust"),
    ("pegging", "give"): ("butt", "build"),
    ("pegging", "receive"): ("cock", "build"),
}
DEFAULT_FOCUS = ("build", "butt")
INTROS = (
    "You take {b} in before anything else: {gender}, {height_word}, "
    "{weight_word}.",
    "{b} stands in the lamplight – {gender}, {height_word}, {weight_word} "
    "– and you let your eyes do their slow, honest work.",
    "Nothing about {b} is an accident: {gender}, {height_word}, "
    "{weight_word}, and entirely at your disposal tonight.",
)
TALLER = (
    "{b} is {cm} cm taller than you, and you feel every one of them when "
    "{b} stands close.",
    "You have to tilt your head back to meet {b}'s eyes – {cm} cm of "
    "difference.",
)
SHORTER = (
    "You look down at {b}, a full {cm} cm shorter than you, and "
    "{b} does not seem to mind at all.",
    "{b} barely reaches your chin – {cm} cm of difference that you use "
    "shamelessly.",
)
LEVEL = (
    "You are nearly the same height, so every glance is eye to eye.",
    "No height between you worth mentioning – {b} fits against you "
    "exactly right.",
)
COCK = {
    "modest": ("{b}'s modest {cm} cm cock twitches under your gaze, easy "
               "and eager.",),
    "solid": ("{b}'s {cm} cm cock is a solid, honest length that fills "
              "the hand and the mind.",),
    "heavy": ("{b}'s {cm} cm cock hangs heavy and thick, the kind you "
              "have to prepare for, and you do.",),
    "huge": ("{b}'s {cm} cm cock is frankly monstrous; you swallow hard "
             "and go very slowly indeed.",),
}
PUSSY = (
    "{b} is already wet, hips shifting restlessly.",
    "{b}'s thighs part with a soft, impatient sigh.",
)
BUTT = (
    "{b}'s {butt_word} rear fills your hands, warm and heavy.",
    "{b} presents {b}'s {butt_word} behind with an unashamed grin.",
)
BUST = (
    "{b}'s {bust} rise and fall with each breath, impossible to ignore.",
    "Your attention keeps drifting to {b}'s {bust}, and {b} knows it.",
)
BUILD = (
    "{b}'s {build} frame moves under your hands, warm and sure.",
    "You feel the {build} weight of {b} settle exactly where you want "
    "it.",
)


def cock_tier(cm:int) -> str:
    return ("modest" if cm < 12 else "solid" if cm < 20
            else "heavy" if cm < 35 else "huge")


def proportion_note(other:Player) -> str:
    share = other.body.get("endowment", 0) / max(other.body.get("height", 170), 1)
    if share >= 0.14:
        return "On such a small frame it looks outrageous."
    if share <= 0.06:
        return "Against that tall frame it looks almost modest."
    return ""


def focus_line(tag:str, other:Player, words:dict, rng:random.Random,
               name:str) -> str:
    cm = other.body.get("endowment", 0)
    if tag == "cock":
        if other.gender not in HUNG_GENDERS or cm <= 0:
            return ""
        line = rng.choice(COCK[cock_tier(cm)]).format(b=name, cm=cm)
        return f"{line} {proportion_note(other)}".strip()
    if tag == "pussy":
        return (rng.choice(PUSSY).format(b=name)
                if other.gender in VAGINA_GENDERS else "")
    if tag == "bust":
        if other.body.get("bust", 0) < 150:
            return ""
        return rng.choice(BUST).format(b=name, bust=words["bust"])
    if tag == "butt":
        return rng.choice(BUTT).format(b=name, butt_word=words["butt"])
    return rng.choice(BUILD).format(b=name, build=words["build"])


def height_line(player:Player, other:Player, name:str,
                rng:random.Random) -> str:
    gap = other.body.get("height", 170) - player.body.get("height", 170)
    if gap >= 12:
        return rng.choice(TALLER).format(b=name, cm=gap)
    if gap <= -12:
        return rng.choice(SHORTER).format(b=name, cm=-gap)
    return rng.choice(LEVEL).format(b=name)


def partner_line(act:str, role:str, player:Player, other:Player,
                 rng:random.Random) -> str:
    words = anatomy(other)["words"]
    name = other.first_name or other.name
    lines = [rng.choice(INTROS).format(
        b=name, gender=other.gender.lower(),
        height_word=words["height_word"],
        weight_word=words["weight_word"])]
    lines.append(height_line(player, other, name, rng))
    for tag in FOCUS.get((act, role), DEFAULT_FOCUS):
        line = focus_line(tag, other, words, rng, name)
        if line:
            lines.append(line)
            break
    return " ".join(lines)
