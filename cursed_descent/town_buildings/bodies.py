import random

from ..config import MIN_NPC_AGE


DEFAULT_PREF = (MIN_NPC_AGE, 65)
MAX_PREF_AGE = 90
MIN_PREF_WIDTH = 9
LADY_AGES = (max(MIN_NPC_AGE, 24), 64)
CLIENT_AGES = (MIN_NPC_AGE, 65)
STOOL_AGES = (MIN_NPC_AGE, 25)


def build_word(weight:int) -> str:
    if weight < 70:
        return "slim"
    if weight < 95:
        return "average"
    if weight < 125:
        return "curvy"
    return "heavy"


def normalise_pref(low:int, high:int) -> tuple[int, int]:
    low = max(MIN_NPC_AGE, min(int(low), MAX_PREF_AGE - MIN_PREF_WIDTH))
    high = min(MAX_PREF_AGE, max(int(high), low + MIN_PREF_WIDTH))
    return low, high


def pref_of(player) -> tuple[int, int]:
    low, high = player.profile.get("age_pref", DEFAULT_PREF)
    return normalise_pref(low, high)


def in_pref(age:int, pref:tuple[int, int]) -> bool:
    return pref[0] <= age <= pref[1]


def pick_age(rng:random.Random, base:tuple[int, int],
             pref:tuple[int, int]) -> int:
    low, high = max(base[0], pref[0]), min(base[1], pref[1])
    if low > high:
        low, high = pref
    return rng.randint(low, high)


def lady_age_height(rng:random.Random,
                    pref:tuple[int, int]=DEFAULT_PREF) -> tuple[int, int]:
    return pick_age(rng, LADY_AGES, pref), rng.randint(150, 185)


def client_body(rng:random.Random, pref:tuple[int, int]=DEFAULT_PREF
                ) -> tuple[int, int, int]:
    return (pick_age(rng, CLIENT_AGES, pref), rng.randint(160, 198),
            rng.randint(55, 115))


def body_line(age:int, height:int, weight:int) -> str:
    parts = []
    if age:
        parts.append(f"{max(age, MIN_NPC_AGE)} years")
    if height:
        parts.append(f"{height} cm")
    parts.append(f"{weight} kg, {build_word(weight)}")
    return ", ".join(parts)
