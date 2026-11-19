import random
from typing import Any

from .. import routines
from ..models import Enemy, Message, Player
from ..town_buildings.chat import chat, split_topic
from ..towns import START_TOWN, TOWNS, town_of
from ..locations.wedding.content import GUEST_STAGES
from .places import place_residents
from .store import find_local, residents_of


def town_company(repository:Any, player:Player | None=None
                 ) -> list[Player]:
    npcs = repository.npc_players()
    town = TOWNS[START_TOWN] if player is None else town_of(player)
    locals_ = residents_of(npcs, town.buildings, town.key)
    if player is not None:
        locals_ = [npc for npc in locals_
                   if routines.reachable(player, npc.npc)]
    return locals_ + [npc for npc in npcs if not repository.is_story(npc)]


def place_company(repository:Any, event:dict[str, Any]) -> list[Player]:
    npcs = repository.npc_players()
    found = [find_local(npcs, resident.key)
             for resident in place_residents(event)]
    return [npc for npc in found if npc is not None]


def stage_topics(npc:Player, event:dict[str, Any] | None
                 ) -> dict[str, tuple[str, ...]] | None:
    if not event or event.get("phase") != "wedding":
        return None
    done = len(event.get("used", set()) & {"eat", "congratulate"})
    return GUEST_STAGES.get(npc.npc, {}).get(done)


def talk_to(player:Player, text:str, repository:Any, rng:random.Random,
            in_run:bool, event:dict[str, Any] | None,
            enemies:list[Enemy], party:list[Player]) -> list[Message]:
    name, topic = split_topic(text.split())
    if not name:
        return [Message("Talk to whom? [talk <name> [work|town|self]]",
                        player.name)]
    if not in_run:
        company = town_company(repository, player)
    else:
        company = [member for member in party if member.npc]
        company += place_company(repository, event or {})
    npc = find_local(company, name)
    if npc is not None:
        spot = None if in_run else routines.texts.at_place(npc.npc)
        if spot is not None and not spot.dialogues:
            return [Message(f"{npc.first_name} has nothing to say here yet.",
                            player.name)]
        staged = stage_topics(npc, event) if in_run else None
        original = npc.profile.get("topics")
        if staged:
            npc.profile["topics"] = staged
        messages = chat(player, npc, topic, rng,
                        spot.dialogues if spot else ())
        if staged:
            npc.profile["topics"] = original
        repository.save(npc)
        return messages
    for enemy in enemies:
        foe = find_local(repository.npc_players(), enemy.name)
        if enemy.alive and foe is not None and foe is find_local(
                repository.npc_players(), name):
            quote = rng.choice(foe.profile.get("quotes") or [""])
            return [Message(f"{foe.first_name} doesn't lower the weapon. "
                            f"{quote}", player.name)]
    return [Message(routines.away_message(player, name)
                    or f"Nobody called '{name}' is here to talk to.",
                    player.name)]
