import random
import time
from typing import Any

from ...models import Player
from .content import EVENT_TEXTS
from .config import (
    ADULT, CAP, FIRST, GENDERS, KIND, NPC_KIND, RANDOM_GENDERS, START,
)


LOOK = ("{name} stands in the traces, naked but for a leather harness and "
        "hoof boots, arms bound behind the back, a horsehair tail hanging "
        "from a plug.")
ROLE = "Pony of the Caravaneer"


def roster(repository:Any) -> list[Player]:
    found = [npc for npc in repository.npc_players()
             if npc.npc == NPC_KIND]
    return sorted(found, key=lambda npc: npc.profile.get("since", 0.0))


def profile_for(name:str, adventurer:bool, origin:str="") -> dict[str, Any]:
    return {"kind": KIND, "role": ROLE, "since": time.time(),
            "adventurer": adventurer, "origin": origin,
            "look": LOOK.format(name=name),
            "quotes": ["*snorts and shakes the mane*"]}


def is_candidate(player:Player) -> bool:
    return (player.alive and player.gender in GENDERS
            and player.age >= ADULT)


def random_pony(repository:Any, rng:random.Random) -> Player:
    taken = {npc.first_name for npc in repository.npc_players()}
    name = rng.choice([n for n in FIRST if n not in taken] or list(FIRST))
    pony = Player(name=repository.unique_handle(name), first_name=name,
                  gender=rng.choice(RANDOM_GENDERS), npc=NPC_KIND)
    pony.profile = profile_for(name, False)
    repository.add(pony)
    return pony


def pony_from(repository:Any, source:Player) -> Player:
    pony = Player.from_dict(source.to_dict())
    pony.id = Player(name="x").id
    pony.account_id = None
    pony.name = repository.unique_handle(f"{source.name} (pony)")
    pony.npc = NPC_KIND
    if not (pony.first_name or pony.last_name):
        pony.first_name = source.name
    pony.alive = True
    pony.hp = max(1, pony.hp)
    pony.equipment = {slot: None for slot in source.equipment}
    pony.inventory = []
    pony.gold = 0
    pony.records = {key: 0 for key in pony.records}
    pony.profile = profile_for(source.name, True, source.name)
    repository.add(pony)
    return pony


def fill(repository:Any, rng:random.Random) -> list[Player]:
    found = roster(repository)
    for _ in range(max(0, START - len(found))):
        random_pony(repository, rng)
    return roster(repository)


def trim(repository:Any) -> list[str]:
    lines: list[str] = []
    found = roster(repository)
    while len(found) > CAP:
        oldest = found.pop(0)
        repository.bury(oldest, "left the Caravaneer's team")
        repository.release(oldest)
        name = oldest.first_name or oldest.name
        lines.append(EVENT_TEXTS["caravaneer"]["vanished"].format(
            cap=CAP, name=name))
    return lines
