import random

from ...config import FLAT_GENDERS, HUNG_GENDERS, VAGINA_GENDERS
from ...models import Message, Player
from ...towns import town_key
from .practices_anatomy import anatomy
from .practices_kicks import KICKS
from .practices_content import (
    ACT_ALIASES, ACT_LABELS, MIN_BUST_CC, NEEDS_BUST, NEEDS_GENITALS,
    NEEDS_PENIS, NEEDS_VAGINA, PRACTICES, ROLE_WORDS, ROLES, TOWN_ACTS,
    TOWN_LABELS,
)


def can_do(gender:str, act:str, role:str,
           body:dict | None=None) -> bool:
    if (act, role) in NEEDS_BUST:
        return gender not in FLAT_GENDERS and (
            body is None or body.get("bust", 0) >= MIN_BUST_CC)
    if (act, role) in NEEDS_PENIS:
        return gender in HUNG_GENDERS
    if (act, role) in NEEDS_VAGINA:
        return gender in VAGINA_GENDERS
    if (act, role) in NEEDS_GENITALS:
        return gender in HUNG_GENDERS or gender in VAGINA_GENDERS
    return True


def acts_in(town:str="") -> dict[str, str]:
    found = dict(ACT_LABELS)
    found.update({act: label for act, label in TOWN_LABELS.items()
                  if town in TOWN_ACTS[act]})
    return found


def options_for(gender:str, body:dict | None=None,
                town:str="") -> list[tuple[str, str]]:
    return [(act, role) for act in acts_in(town) for role in ROLES
            if can_do(gender, act, role, body)]


def parse_direction(args:list[str]) -> str:
    for word in args:
        word = word.casefold()
        if word in ("front", "from_front", "forward"):
            return "front"
        if word in ("back", "behind", "rear"):
            return "back"
    return ""


def parse_choice(args:list[str], town:str="") -> tuple[str, str]:
    words = [word.casefold() for word in args]
    words = [ACT_ALIASES.get(word, word) for word in words]
    labels = acts_in(town)
    act = next((word for word in words if word in labels), "")
    role = next((ROLE_WORDS[word] for word in words if word in ROLE_WORDS),
                "")
    return act, role


def option_text(gender:str, body:dict | None=None, town:str="") -> str:
    return " | ".join(f"{act} {role}"
                      for act, role in options_for(gender, body, town))


def requirement(act:str, role:str) -> str:
    if (act, role) in NEEDS_PENIS:
        return " (needs a penis)"
    if (act, role) in NEEDS_VAGINA:
        return " (needs a vagina)"
    if (act, role) in NEEDS_GENITALS:
        return " (needs a cock or a vagina)"
    if (act, role) in NEEDS_BUST:
        return " (needs breasts)"
    return ""


def describe(player:Player, act:str, role:str,
             rng:random.Random, direction:str="") -> str:
    if act == "ballbusting" and role == "give":
        return rng.choice(KICKS[direction or rng.choice(tuple(KICKS))])
    info = anatomy(player)
    fits = [(tags, text) for tags, text in PRACTICES[act][role]
            if all(info["tags"][tag] for tag in tags)]
    tailored = [entry for entry in fits if entry[0]]
    pool = fits + tailored
    return rng.choice(pool)[1].format(**info["words"])


def practices_text(player:Player, args:list[str]) -> list[Message]:
    town = town_key(player)
    labels = acts_in(town)
    act, _ = parse_choice(args, town)
    rng = random.Random(player.id)
    acts = [act] if act else list(labels)
    lines = ["🌹 Practices at the <<npc.rose_first>> Chamber – every one can be given or "
             "received. [serve <act> give|receive] during a shift."]
    for key in acts:
        lines.append(f"\n{labels[key].upper()}")
        for role in ROLES:
            mark = "✔" if can_do(player.gender, key, role, player.body) else "✘"
            lines.append(f"  {mark} {role}{requirement(key, role)}")
            if act and can_do(player.gender, key, role, player.body):
                lines.append(f"     {describe(player, key, role, rng)}")
    if not act:
        lines.append("\n[practices <act>] shows how each would go for "
                     "your body.")
    return [Message("\n".join(lines), player.name)]
