import zlib

from .config import CONDITION_STEPS, HUNG_GENDERS, VAGINA_GENDERS
from .models import Player


LIKES = ("penis", "vagina", "both")
SPREAD = {"Male": (65, 85), "Female": (65, 85)}


def traits_of(gender:str) -> set[str]:
    traits = set()
    if gender in HUNG_GENDERS:
        traits.add("penis")
    if gender in VAGINA_GENDERS:
        traits.add("vagina")
    return traits


def likes_of(player:Player) -> str:
    stored = player.profile.get("orientation")
    if stored in LIKES:
        return stored
    if not player.npc:
        return "both"
    roll = zlib.crc32(player.id.encode()) % 100
    own, other = ("penis", "vagina") if player.gender == "Female" else (
        "vagina", "penis")
    if player.gender in SPREAD:
        first, second = SPREAD[player.gender]
        return own if roll < first else other if roll < second else "both"
    return "both" if roll < 70 else own if roll < 85 else other


def fits(host:Player, guest:Player) -> bool:
    likes = likes_of(host)
    return likes == "both" or likes in traits_of(guest.gender)


def count_of(owner:Player, key:str, other:Player) -> int:
    return owner.profile.get(key, {}).get(other.id, 0)


def raise_count(owner:Player, key:str, other:Player) -> int:
    counts = owner.profile.setdefault(key, {})
    counts[other.id] = counts.get(other.id, 0) + 1
    return counts[other.id]


def reaction(host:Player, guest:Player, host_dominant:bool
             ) -> tuple[list[str], int]:
    name = host.first_name or host.name
    lines: list[str] = []
    delta = 0
    if fits(host, guest):
        delta = 1
        lines.append(f"{name} clearly likes what {guest.name} has.")
    elif count_of(guest, "conditioned", host) >= CONDITION_STEPS:
        lines.append(f"{name} has come around to your body.")
    else:
        delta = -1
        done = raise_count(guest, "conditioned", host)
        if done >= CONDITION_STEPS:
            lines.append(f"{name} stops minding: {guest.name}'s body is "
                         f"welcome now.")
        else:
            lines.append(f"{name} usually prefers {likes_of(host)}, but "
                         f"goes along ({done}/{CONDITION_STEPS}).")
    if host_dominant and not guest.npc and not fits(guest, host):
        done = raise_count(guest, "educated", host)
        if done >= CONDITION_STEPS:
            guest.profile["orientation"] = "both"
            lines.append(f"{name} has taught you to like it. Your "
                         f"orientation is now: both.")
        else:
            lines.append(f"{name} is teaching you to like it "
                         f"({done}/{CONDITION_STEPS}).")
    return lines, delta
