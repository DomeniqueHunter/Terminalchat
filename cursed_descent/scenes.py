import random

from .config import HUNG_GENDERS
from .models import Player


POSITIONS = {
    "face": ("Face to face",
             "{top} draws {bottom} close, face to face, close enough to "
             "share every breath."),
    "behind": ("From behind",
               "{bottom} braces against the wall of the camp while {top} "
               "comes up close behind."),
    "rider": ("Riding",
              "{top} lies back and pulls {bottom} on top. {bottom} sets "
              "the rhythm."),
    "spoon": ("Spooning",
              "{top} curls around {bottom} from behind, slow and warm, "
              "wrapped in one blanket."),
    "wall": ("Standing",
             "{top} lifts {bottom} against the wall. Neither of them "
             "makes much sound, and neither can be quiet."),
    "seated": ("Seated",
               "{bottom} settles in {top}'s lap, arms around {top}'s "
               "neck, and the world narrows to the two of them."),
}
AMOUNTS = {"little": ("a little", 0.5), "some": ("a good amount", 1.0),
           "much": ("a great deal", 1.5)}
WHERE = {
    "in": "{top} finishes inside {bottom}, {amount}, and {bottom} "
          "feels the warmth spread.",
    "on": "{top} pulls back at the last moment and finishes on "
          "{bottom}'s skin, {amount}.",
}
AFTER = ("They lie tangled together afterwards, quiet and flushed.",
         "A shared blanket, a shared breath, and the night stays kind.",
         "Neither says anything for a while. Neither needs to.")
ROLES = ("top", "bottom")
DEFAULTS = {"position": "face", "role": "top", "amount": "some",
            "where": "in"}


def parse_options(args:list[str], defaults:dict[str, str] | None=None
                  ) -> tuple[list[str], dict[str, str]]:
    options = dict(defaults or DEFAULTS)
    rest = list(args)
    while len(rest) > 1:
        word = rest[-1].casefold()
        if word in POSITIONS:
            options["position"] = word
        elif word in ROLES:
            options["role"] = word
        elif word in AMOUNTS:
            options["amount"] = word
        elif word in WHERE:
            options["where"] = word
        else:
            break
        rest.pop()
    return rest, options


def roles(first:Player, second:Player,
          options:dict[str, str]) -> tuple[Player | None, Player]:
    top, bottom = ((first, second) if options["role"] == "top"
                   else (second, first))
    if top.gender in HUNG_GENDERS:
        return top, bottom
    if bottom.gender in HUNG_GENDERS:
        return bottom, top
    return None, bottom


def describe(first:Player, second:Player, options:dict[str, str],
             rng:random.Random) -> tuple[list[str], Player | None,
                                          Player, float]:
    top, bottom = roles(first, second, options)
    if top is None:
        top = first
        text = POSITIONS[options["position"]][1]
        values = {"top": top.name, "bottom": bottom.name}
        return [text.format(**values), rng.choice(AFTER)], None, bottom, 0.0
    amount, factor = AMOUNTS[options["amount"]]
    values = {"top": top.name, "bottom": bottom.name, "amount": amount}
    lines = [POSITIONS[options["position"]][1].format(**values),
             WHERE[options["where"]].format(**values), rng.choice(AFTER)]
    return lines, top, bottom, factor if options["where"] == "in" else 0.0
