import random

from ..body import BUST_CC, fake_amount
from ..config import HUNG_GENDERS
from ..models import Player
from ..races import race_named


PARTS = ("bust", "butt", "endowment")
BIG_AT = {"bust": BUST_CC["Large"], "butt": 125, "endowment": 22}
SMALL_AT = {"bust": BUST_CC["Small"], "butt": 95, "endowment": 14}
FAKE_SHARE = 0.25
MATCH_BONUS = 0.15
MISS_MALUS = 0.10
MIN_FACTOR = 0.7
LABELS = {"bust": "chest", "butt": "rear", "endowment": "cock"}

HINTS = {
    ("bust", "big"): (
        "{name}'s gaze keeps sliding to your chest. 'Some people simply "
        "fill a room, don't you think?'",
        "'I never understood the appeal of anything modest up there,' "
        "{name} remarks, eyes on your chest.",
    ),
    ("bust", "small"): (
        "'Neat and dainty,' {name} murmurs, watching your chest. 'That is "
        "what I call elegant.'",
        "{name} sighs. 'Some people overdo it up there. I like a figure "
        "that does not need to shout.'",
    ),
    ("butt", "big"): (
        "{name} lets a long look rest on your rear. 'Plenty to hold on to "
        "– that is the whole point, isn't it?'",
        "'I like it when someone has real weight behind them,' {name} "
        "says, still looking at your rear.",
    ),
    ("butt", "small"): (
        "{name} nods at your rear. 'Tight and trim. Anything more is just "
        "in the way.'",
        "'Give me something lean and firm,' {name} says, eyeing your "
        "rear. 'Bulk is wasted on me.'",
    ),
    ("endowment", "big"): (
        "{name} licks lips and glances below your belt. 'Go big or go "
        "home, I always say.'",
        "'Size matters,' {name} says lightly, and does not hide where "
        "the eyes go.",
    ),
    ("endowment", "small"): (
        "{name} smiles at the front of your hips. 'Something cute and "
        "manageable is my favourite kind.'",
        "'I am not after anything threatening,' {name} says, eyes below "
        "your belt. 'Gentle suits me.'",
    ),
}
REAL_HINTS = {
    "real": (
        "'There is nothing like the genuine article,' {name} says, "
        "stroking a hand along the {part}. 'Soft, warm, a little give.'",
        "{name} wrinkles a nose. 'I can always tell what is natural. "
        "That is what I want.'",
    ),
    "fake": (
        "'Round and firm and perfect,' {name} sighs, watching your "
        "{part}. 'Nature rarely gets it that tidy.'",
        "{name} grins. 'I like a bit of craftsmanship. A well-made "
        "{part} beats a lucky one.'",
    ),
}


def taste_of(name:str, race_key:str="human"
             ) -> dict[str, tuple[str, str]]:
    rng = random.Random(f"taste:{name}")
    focus = rng.sample(PARTS, rng.choice((1, 1, 2)))
    taste = {part: ("any", "any") for part in PARTS}
    for part in focus:
        taste[part] = (rng.choice(("big", "small", "any")),
                       rng.choice(("real", "fake", "any")))
        if taste[part] == ("any", "any"):
            taste[part] = (rng.choice(("big", "small")), "any")
    race = race_named(race_key)
    if race.taste_pull and random.Random(
            f"racetaste:{name}").random() < race.taste_pull:
        part, size, real = race.taste
        taste[part] = (size, real)
    return taste


def player_traits(player:Player) -> dict[str, tuple[str, str]]:
    body = player.body
    traits = {}
    values = {"bust": body.get("bust", 0), "butt": body.get("butt", 0),
              "endowment": body.get("endowment", 0)}
    for part, value in values.items():
        if part == "bust" and body.get("breasts", "None") == "None":
            continue
        if part == "endowment" and player.gender not in HUNG_GENDERS:
            continue
        if not value:
            continue
        size = ("big" if value >= BIG_AT[part]
                else "small" if value <= SMALL_AT[part] else "mid")
        fake = fake_amount(body, part) / value
        traits[part] = (size, "fake" if fake >= FAKE_SHARE else "real")
    return traits


def client_taste(player:Player, name:str) -> dict[str, tuple[str, str]]:
    from ..towns import town_of
    return taste_of(name, town_of(player).race_key)


def tally(player:Player, name:str) -> tuple[list[str], list[str]]:
    traits = player_traits(player)
    hits: list[str] = []
    misses: list[str] = []
    for part, (size, real) in client_taste(player, name).items():
        if part not in traits or (size, real) == ("any", "any"):
            continue
        has_size, has_real = traits[part]
        checks = [(size, has_size), (real, has_real)]
        wanted = [(want, have) for want, have in checks if want != "any"]
        if all(want == have for want, have in wanted):
            hits.append(part)
        elif any(want != have for want, have in wanted):
            misses.append(part)
    return hits, misses


def taste_factor(player:Player, name:str) -> float:
    hits, misses = tally(player, name)
    return max(MIN_FACTOR, 1 + MATCH_BONUS * len(hits)
               - MISS_MALUS * len(misses))


def taste_hints(player:Player, name:str) -> list[str]:
    rng = random.Random(f"hint:{name}")
    lines = []
    for part, (size, real) in client_taste(player, name).items():
        if size != "any":
            lines.append(rng.choice(HINTS[(part, size)]).format(name=name))
        if real != "any":
            lines.append(rng.choice(REAL_HINTS[real]).format(
                name=name, part=LABELS[part]))
    return lines


def taste_reaction(player:Player, name:str) -> str:
    hits, misses = tally(player, name)
    if hits and not misses:
        return (f"{name}'s eyes keep returning to your "
                f"{LABELS[hits[0]]}, plainly pleased.")
    if misses and not hits:
        return (f"{name}'s gaze slides off your {LABELS[misses[0]]} "
                f"with a flicker of disappointment.")
    return ""
