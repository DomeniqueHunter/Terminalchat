import random

from ..plants import PLANTS

# Engine settings and default texts. The plants themselves live in plants/.

STAGES = ("Seedling", "Vine", "Bud", "Bloom", "Overgrown")
BLOOM = 3
WILT_AFTER = 3
HUNGRY_AFTER = 2

TEXTS = {
    "planted": "You press the {seed} into the soil of the {spot}. The "
               "earth around it turns warm.",
    "no_seed": "That is not something you can plant.",
    "taken": "Something already grows there.",
    "no_spot": "Seeds go into a garden spot.",
    "nothing": "Nothing grows there.",
    "water": "You water the {plant}. The leaves unfurl a little.",
    "watered": "The {plant} has been watered already.",
    "revive": "You water the {plant} until it stirs again.",
    "not_ready": "The {plant} is not in bloom yet ({stage}).",
    "wilted": "A wilted plant gives nothing. Water it first.",
    "harvest": "You harvest the plant. It starts again from the root.",
    "seed": "A seed drops from the plant.",
    "full": "Your bag is full.",
    "uproot": "You pull the {plant} out by its roots. It was a shame.",
    "feed_wilted": "The plant is too limp to drink. Water it first.",
    "feed_done": "The plant has drunk from you already this run.",
    "feed_no_body": "The plant has nothing to take from you.",
    "feed_small": "You are not big enough for the plant.",
    "feed_dry": "You are too dry. The plant wants sweat.",
    "feed": "The plant drinks from you.",
    "feed_store": "The plant stores something up.",
    "held": "The plant holds on to you and will not let go. Pull free.",
    "held_block": "The plant still holds you. Pull free first.",
    "pull": "You pull against the plant.",
    "freed": "You tear yourself free.",
    "not_held": "Nothing holds you.",
    "occupied": "Someone is inside the blossom. That has to be dealt with "
                "first.",
    "offer_no": "The plant is not big enough to take you.",
    "nobody": "Nobody is trapped there.",
    "no_self_rescue": "You cannot free yourself from the inside.",
    "drained": "The starving plant drains you as you walk in.",
    "drained_off": "The plant has had its fill. The weakness fades.",
    "bloom_buff": "The scent of the blooming plant clings to you.",
}


def say(kind:str, key:str) -> str:
    text = PLANTS[kind].get("texts", {}).get(key) or TEXTS[key]
    return random.choice(text) if isinstance(text, (list, tuple)) else text
