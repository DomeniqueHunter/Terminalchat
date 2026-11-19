import random

from .config import (
    FUTA_GENDERS, VINE_BIOME, VINE_FULL_SWEAT, VINE_RISK_SWEAT,
    VINE_SURE_SWEAT,
)
from .models import Enemy, Player


WARNINGS = [
    "{name}, keep your eggs clean. The swamp can smell everything.",
    "A sweet, heavy scent hangs over the water. {name} is dripping, and "
    "somewhere under the mud something notices.",
    "'Hold it together, {name}.' The vines on the nearest tree lean a "
    "little closer, as if listening.",
    "{name} is glistening with sweat. Pale flowers open along the path, "
    "one by one, all turned in {their} direction.",
]
AMBUSH_LINES = [
    "🌿 The scent of {names} rolls across the swamp. The mud splits, and a "
    "Pheromone Bloom rises with its petals wide open.",
    "🌿 Vines slide out of the reeds without a sound, drawn to the sweat on "
    "{names}. Heart-shaped leaves unfold around the party.",
]


def is_futa(player:Player) -> bool:
    return player.gender in FUTA_GENDERS


def sweat_ratio(player:Player) -> float:
    return player.sweat / VINE_FULL_SWEAT


def worst(party:list[Player]) -> tuple[float, list[Player]]:
    futas = [member for member in party if is_futa(member)]
    ratio = max((sweat_ratio(member) for member in futas), default=0.0)
    return ratio, futas


def in_swamp(biome:dict) -> bool:
    return biome["name"] == VINE_BIOME


def warnings(party:list[Player]) -> list[str]:
    lines = []
    for member in party:
        if is_futa(member) and sweat_ratio(member) > VINE_RISK_SWEAT:
            their = "her" if member.gender == "Herm" else "their"
            lines.append("🌿 " + random.choice(WARNINGS).format(
                name=member.name, their=their))
    return lines[:2]


def triggered(party:list[Player], chance:float=0.5) -> bool:
    ratio, _ = worst(party)
    if ratio > VINE_SURE_SWEAT:
        return True
    return ratio > VINE_RISK_SWEAT and random.random() < chance


def only_vines(enemies:list[Enemy]) -> None:
    if any(enemy.template_id == "pheromone_bloom" for enemy in enemies):
        enemies[:] = [enemy for enemy in enemies
                      if enemy.template_id == "pheromone_bloom"]


def ambush(biome:dict, party:list[Player], enemies:list[Enemy],
           make) -> list[str]:
    if not in_swamp(biome) or not enemies:
        return []
    lines = warnings(party)
    if any(enemy.template_id == "pheromone_bloom" for enemy in enemies):
        only_vines(enemies)
        return lines
    if not triggered(party):
        return lines
    _, futas = worst(party)
    sweaty = [member.name for member in futas
              if sweat_ratio(member) > VINE_RISK_SWEAT]
    enemies[:] = [make(enemy.uid) for enemy in enemies]
    lines.append(random.choice(AMBUSH_LINES).format(
        names=" and ".join(sweaty)))
    return lines
