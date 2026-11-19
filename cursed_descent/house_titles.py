import random
from typing import Any

from .models import Message, Player
from .town_buildings.family import relations


TITLES = ("mistress", "herrin", "goddess", "madam", "mommy", "queen",
          "master", "sir")
ORDERS = (
    "{a} crosses {a}'s arms and fixes {b} with a long, cool look. 'From "
    "now on you call me {title}. Say it.' {b} swallows, eyes lowered. "
    "'Yes, {title}.'",
    "'Kneel,' {a} says, quietly, and waits until {b} obeys. 'You will "
    "address me as {title}, every time, and you will mean it.' {b}'s "
    "voice shakes: 'Yes, {title}.'",
    "{a} tips {b}'s chin up with one finger. 'Tell me what I am to you.' "
    "A pause, then, very softly: '{title}.' 'Good,' {a} smiles. 'Again.'",
)
REMINDERS = (
    "'Thank you, {title},' {b} breathes.",
    "'Yes, {title},' {b} whispers, not daring to look up.",
    "{b} adds, almost reverently: '{title}.'",
    "'As you wish, {title},' {b} says, and means every word.",
)
FORGOT = (
    "{b} slips and uses {a}'s plain name. {a} raises an eyebrow, and "
    "{b} corrects at once: '{title}! Forgive me, {title}.'",
)


KIN_ORDERS = {
    "son": (
        "{a} sits {b} down like she did when {b} was small. 'You are my "
        "son and you will call me {title} now. Say it properly.' {b} "
        "flushes to the ears. 'Yes, {title}.' 'Good boy.'",
        "'Mother is not enough any more, {b}.' {a}'s voice is soft and "
        "absolute. 'It is {title}.' {b} lowers {b}'s gaze: 'Yes, {title}.'",
    ),
    "daughter": (
        "{a} takes {b}'s chin. 'My own daughter will call me {title}. "
        "Say it, darling.' {b} whispers: 'Yes, {title}.' 'Good girl.'",
    ),
    "mother": (
        "{a} turns the old order of the house upside down. 'In here you "
        "call me {title}, {b}. Mother or not.' {b} sighs, then obeys: "
        "'Yes, {title}.'",
    ),
    "father": (
        "{a} holds {b}'s stern look until it breaks. 'It is {title} "
        "in this house, father.' {b}, grudgingly: 'Yes, {title}.'",
    ),
    "sister": (
        "{a} smirks. 'Sisters are equals? Not tonight. {title}.' {b} "
        "rolls {b}'s eyes, then gives in: 'Yes, {title}.'",
    ),
    "brother": (
        "{a} smirks. 'Big brother or not, you call me {title} now.' {b} "
        "grumbles, then: 'Yes, {title}.'",
    ),
    "partner": (
        "{a} leans close. 'My love, you will call me {title} tonight.' "
        "{b} shivers happily. 'Yes, {title}.'",
    ),
}
KIN_REMINDERS = {
    "son": ("'Yes, {title},' {b} mumbles, red to the ears. 'Good boy,' "
            "{a} says.",),
    "daughter": ("'Yes, {title},' {b} says, eyes down. 'Good girl,' {a} "
                 "murmurs.",),
    "mother": ("'Yes, {title},' {b} says, though the word still tastes "
               "odd for a mother.",),
    "father": ("'Yes, {title},' {b} says through {b}'s teeth.",),
}


def kin_of(player:Player, other:Player) -> str:
    return relations(player).get(other.id, {}).get("role", "")


def parse_title(args:list[str]) -> tuple[list[str], str]:
    if len(args) > 1 and args[-1].casefold() in TITLES:
        return args[:-1], args[-1].casefold()
    return args, ""


def titles_of(home:dict[str, Any]) -> dict[str, str]:
    return home.setdefault("titles", {})


def order_title(player:Player, home:dict[str, Any], other:Player,
                title:str, repository:Any,
                rng:random.Random) -> list[Message]:
    if not title:
        return [Message("Order whom to call you what? [home order <name> "
                        + "|".join(TITLES) + "]", player.name)]
    titles_of(home)[other.id] = title.capitalize()
    repository.save(player)
    pool = KIN_ORDERS.get(kin_of(player, other), ()) + ORDERS
    text = rng.choice(pool).format(a=player.name, b=other.name,
                                     title=title.capitalize())
    return [Message(f"👑 {text}")]


GREETINGS = (
    "'Good evening, {title},' {b} says at the door, head slightly bowed.",
    "{b} steps inside and, before anything else, murmurs: '{title}.'",
    "'I came as soon as you called, {title},' {b} says.",
)
FAREWELLS = (
    "'Goodnight, {title},' {b} says at the door, and means it.",
    "{b} bows a little as {b} leaves: 'Until next time, {title}.'",
)
CHATS = (
    "{b} never forgets the title: '{title}, may I say something?'",
    "'Yes, {title},' {b} answers, a little too quickly.",
    "{b} lowers {b}'s voice. 'Whatever you say, {title}.'",
)
ACTIVITIES = (
    "'{title},' {b} whispers, as if the word were part of the "
    "closeness.",
    "{b} adds a soft, obedient 'Thank you, {title}.'",
)
POOLS = {"greet": GREETINGS, "bye": FAREWELLS, "chat": CHATS,
         "act": ACTIVITIES}


def title_for(home:dict[str, Any], player:Player, other:Player,
              kind:str, rng:random.Random) -> str:
    title = titles_of(home).get(other.id)
    if not title:
        return ""
    return rng.choice(POOLS[kind]).format(a=player.name, b=other.name,
                                          title=title)


def title_line(home:dict[str, Any], player:Player, other:Player,
               rng:random.Random) -> str:
    title = titles_of(home).get(other.id)
    if not title:
        return ""
    pool = (KIN_REMINDERS.get(kin_of(player, other), ()) * 2 + REMINDERS
            + (FORGOT if rng.random() < 0.15 else ()))
    return rng.choice(pool).format(a=player.name, b=other.name, title=title)
