import random

from .models import Player
from .town_buildings.family import relations


OPENERS = {
    "son": (
        "{b} hesitates in the doorway. '{a}... Mom... are we really doing "
        "this?' {a} only smiles and pulls {him} closer. 'You are grown, "
        "darling. Nobody here will tell.'",
        "'Don't call me Mom tonight,' {a} murmurs. '{b}, I mean it. Just "
        "{a}.' {b} nods, swallowing, and the door is locked.",
    ),
    "daughter": (
        "{b} blushes to the roots. '{a}, we should not...' 'We should "
        "not,' {a} agrees, and kisses {him} anyway.",
    ),
    "mother": (
        "{b} takes {a}'s hand with a nervous laugh. '{a}, you raised me.' "
        "'And now you are old enough to choose,' {a} answers softly.",
    ),
    "father": (
        "'Is it wrong that I wanted this?' {b} whispers. {a} has no good "
        "answer, only a long breath and an open arm.",
    ),
    "brother": (
        "'Family secrets keep best in the family,' {b} grins. {a} rolls "
        "{their} eyes, but locks the door.",
    ),
    "sister": (
        "'We always shared everything,' {b} says. {a} laughs low. "
        "'Everything.'",
    ),
}
AFTERMATH = {
    "son": (
        "Afterwards {b} rests {their} head on {a}'s chest. 'Mom... "
        "that stays between us.' 'Always, sweetheart.'",
        "{a} strokes {b}'s hair as the candle burns down. 'You were "
        "wonderful. Now sleep.'",
    ),
    "daughter": (
        "{b} curls against {a}, quiet and flushed. 'I will never look "
        "at the dinner table the same way again.'",
    ),
    "mother": (
        "{b} tucks the blanket around {a}, the way {a} once did for {him}.",
    ),
    "father": (
        "{b} pours two cups of tea in the grey light. Neither mentions "
        "what happened, and neither stops smiling.",
    ),
    "brother": (
        "'Not a word at the next family dinner,' {b} says. 'Not one.'",
    ),
    "sister": (
        "They lie side by side, giggling like children who stole cake.",
    ),
}
PRONOUNS = {"Male": ("him", "his"), "Female": ("her", "her")}


def role_of(player:Player, other:Player) -> str:
    role = relations(player).get(other.id, {}).get("role", "")
    return role if role in OPENERS else ""


def fill(text:str, player:Player, other:Player) -> str:
    him, their = PRONOUNS.get(other.gender, ("them", "their"))
    return text.format(a=player.first_name or player.name,
                       b=other.first_name or other.name, him=him,
                       their=their)


def family_open(player:Player, other:Player, rng:random.Random) -> str:
    role = role_of(player, other)
    if not role:
        return ""
    return fill(rng.choice(OPENERS[role]), player, other)


def family_close(player:Player, other:Player, rng:random.Random) -> str:
    role = role_of(player, other)
    if not role:
        return ""
    return fill(rng.choice(AFTERMATH[role]), player, other)
