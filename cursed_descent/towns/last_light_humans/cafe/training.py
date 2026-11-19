import random
from dataclasses import dataclass

from ....config import (
    HOME_SEAT_SITS, INVITE_BASE, INVITE_HAPPY, TRAIN_CUT, TRAIN_CUT_MAX,
    TRAIN_MARGIN_EVERY, TRAIN_MAX,
)
from ....models import Player


INTENSITY = {"gentle": (1, 0.5, 3), "normal": (2, 1.0, 0),
             "hard": (3, 1.6, -3)}
LENGTHS = {"short": 1, "long": HOME_SEAT_SITS}
TRAIN_KEY = "seat_training"


@dataclass
class VisitOptions:
    intensity: str = "normal"
    length: str = "long"

    @property
    def sits(self) -> int:
        return LENGTHS[self.length]

    @property
    def risk(self) -> float:
        return INTENSITY[self.intensity][1]

    @property
    def margin_mod(self) -> int:
        return INTENSITY[self.intensity][2]

    def points(self) -> int:
        return (INTENSITY[self.intensity][0]
                + (1 if self.length == "long" else 0))

    def label(self) -> str:
        return f"{self.intensity}, {self.length}"


def parse_options(words:list[str]) -> tuple[VisitOptions, list[str]]:
    options = VisitOptions()
    rest: list[str] = []
    for word in words:
        low = word.casefold()
        if low in INTENSITY:
            options.intensity = low
        elif low in LENGTHS:
            options.length = low
        else:
            rest.append(word)
    return options, rest


def training_of(player:Player, name:str) -> int:
    return int(player.profile.get(TRAIN_KEY, {}).get(name.casefold(), 0))


def add_training(player:Player, name:str, points:int) -> int:
    table = player.profile.setdefault(TRAIN_KEY, {})
    key = name.casefold()
    table[key] = max(0, min(TRAIN_MAX, table.get(key, 0) + points))
    return table[key]


def train_cut(points:int) -> float:
    return min(TRAIN_CUT_MAX, TRAIN_CUT * points)


def train_margin(points:int) -> int:
    return points // TRAIN_MARGIN_EVERY


def accepts_invite(happiness:int, rng:random.Random) -> bool:
    return rng.random() < INVITE_BASE + INVITE_HAPPY * happiness
