import random

from .body import muscle_tier
from .config import (
    SCENT_FATE_CHANCE, SCENT_FATES, SCENT_MUSCLE_LOVERS, SCENT_PREF_FACTOR,
    SCENT_PREFERENCES, SWEAT_AGGRO,
)
from .models import Enemy, Player
from .smell import foreign_tier
from .sweat import sweat_tier


def scent_key(enemy:Enemy, table:dict) -> str:
    if enemy.template_id in table:
        return enemy.template_id
    return enemy.tribe if enemy.tribe in table else ""


def prefers(enemy:Enemy, player:Player) -> bool:
    if enemy.template_id in SCENT_MUSCLE_LOVERS:
        return muscle_tier(player.stats, player.body) == "leather"
    key = scent_key(enemy, SCENT_PREFERENCES)
    return bool(key) and player.gender in SCENT_PREFERENCES[key]


def scent_tier(player:Player) -> int:
    return max(sweat_tier(player), foreign_tier(player))


def scent_weight(enemy:Enemy, player:Player) -> float:
    tier = scent_tier(player)
    if not tier:
        return 1.0
    weight = 1 + tier * SWEAT_AGGRO
    return weight * SCENT_PREF_FACTOR if prefers(enemy, player) else weight


def scent_fate(player:Player, killer:Enemy) -> str:
    tier = scent_tier(player)
    key = scent_key(killer, SCENT_FATES)
    if not tier or not key:
        return ""
    fate = SCENT_FATES[key]
    if fate not in killer.fates:
        return ""
    if scent_key(killer, SCENT_PREFERENCES) and not prefers(killer, player):
        return ""
    return fate if random.random() < tier * SCENT_FATE_CHANCE else ""


def party_scent(party:list[Player]) -> int:
    return max((scent_tier(player) for player in party if player.alive),
               default=0)
