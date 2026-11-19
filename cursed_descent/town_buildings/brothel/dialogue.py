import random

from ...models import Player
from .dialogue_content import (
    DOMINATED_TEMPER, GREETINGS, MATCH_LINE, PLAYER_LINES, PREFERRED_TONE,
    REACTIONS, TEMPERS, TONE_HINTS, TONES,
)


TONE_BONUS = 1.25


def pick_temper(dominated:bool, rng:random.Random) -> str:
    return DOMINATED_TEMPER if dominated else rng.choice(TEMPERS)


def greeting(temper:str, rng:random.Random) -> str:
    return rng.choice(GREETINGS[temper])


def default_tone(player:Player) -> str:
    text = player.personality.casefold()
    for tone, words in TONE_HINTS.items():
        if any(word in text for word in words):
            return tone
    return "teasing"


def parse_tone(words:list[str]) -> str:
    return next((word.casefold() for word in words
                 if word.casefold() in TONES), "")


def player_line(tone:str, role:str, rng:random.Random) -> str:
    return rng.choice(PLAYER_LINES[tone][role])


def reaction(temper:str, liked:bool, rng:random.Random) -> str:
    return rng.choice(REACTIONS[temper]["liked" if liked else "fine"])


def tone_matches(temper:str, tone:str) -> bool:
    return PREFERRED_TONE[temper] == tone


def match_text(tone:str) -> str:
    return MATCH_LINE.format(tone=tone)


def speaker(name:str) -> str:
    return name[:1].upper() + name[1:]
