import random
from collections import Counter

from ..config import (
    BONUS_DROPS, BOUTIQUE_SELF_BASE, BOUTIQUE_SELF_PER_LEVEL, DEFAULT_GENDER,
    PRONOUNS,
)
from ..models import Player


def their(player:Player) -> str:
    return PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])[2]


def options_text(options:list[str]) -> str:
    return " | ".join(f"[{option}]" for option in options)


def self_price(player:Player) -> int:
    return BOUTIQUE_SELF_BASE + player.level * BOUTIQUE_SELF_PER_LEVEL


def bonus_drop(kind:str) -> str:
    return random.choice(BONUS_DROPS[kind])


def decide(votes:dict[str, str], voters:list[str]) -> tuple[str, bool]:
    counts = Counter(choice for name, choice in votes.items()
                     if name in voters)
    best = max(counts.values())
    tops = [choice for choice, count in counts.items() if count == best]
    return random.choice(tops), len(tops) > 1
