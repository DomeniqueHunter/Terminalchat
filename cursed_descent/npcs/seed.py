import copy
import uuid

from ..models import Player
from ..settings import PROTOTYPES, ensure_loaded
from ..storage import PlayerRepository
from ..towns import Resident
from .address import ADDRESS_KEY


GEAR_KEY = "gear"
GEAR_VERSION = 3


def player_of(key:str) -> Player:
    ensure_loaded()
    return Player.from_dict({**copy.deepcopy(PROTOTYPES[key]),
                             "id": uuid.uuid4().hex})


def resident_player(resident:Resident, kind:str="resident",
                    town:str="") -> Player:
    return player_of(resident.key)


def default_npcs() -> list[Player]:
    ensure_loaded()
    return [player_of(key) for key in PROTOTYPES]


def sync_figure_shapes(repository:PlayerRepository,
                       defaults:list[Player]) -> None:
    stored = {npc.npc: npc for npc in repository.npc_players()}
    for fresh in defaults:
        old = stored.get(fresh.npc)
        if old is None or old.profile.get("kind") != "figure":
            continue
        shape = fresh.body.get("endowment_shape", "Human")
        if old.body.get("endowment_shape", "Human") != shape:
            old.body["endowment_shape"] = shape
            repository.save(old)


def sync_addresses(repository:PlayerRepository,
                   defaults:list[Player]) -> None:
    fresh = {npc.npc: npc for npc in defaults}
    for old in repository.npc_players():
        new = fresh.get(old.npc)
        if new is None or old.profile.get(ADDRESS_KEY):
            continue
        old.profile[ADDRESS_KEY] = new.profile[ADDRESS_KEY]
        old.profile["home"] = new.profile["home"]
        repository.save(old)


def sync_prefs(repository:PlayerRepository,
               defaults:list[Player]) -> None:
    fresh = {npc.npc: npc for npc in defaults}
    for old in repository.npc_players():
        new = fresh.get(old.npc)
        if new is None or "prefs" not in new.profile:
            continue
        stored = old.profile.get("prefs")
        if stored is None:
            old.profile["prefs"] = new.profile["prefs"]
        elif (new.profile["prefs"].get("outcomes")
                and not stored.get("outcomes")):
            stored["outcomes"] = new.profile["prefs"]["outcomes"]
        else:
            continue
        repository.save(old)


def sync_gear(repository:PlayerRepository,
              defaults:list[Player]) -> None:
    fresh = {npc.npc: npc for npc in defaults}
    for old in repository.npc_players():
        new = fresh.get(old.npc)
        if new is None or old.profile.get(GEAR_KEY, 0) >= GEAR_VERSION:
            continue
        for slot, item in new.equipment.items():
            if item and old.equipment.get(slot) is None:
                old.equipment[slot] = item
        old.profile[GEAR_KEY] = GEAR_VERSION
        repository.save(old)


def seed_npcs(repository:PlayerRepository) -> None:
    defaults = default_npcs()
    present = {npc.npc for npc in repository.npc_players()}
    for player in defaults:
        if player.npc not in present:
            repository.save(player)
    sync_figure_shapes(repository, defaults)
    sync_addresses(repository, defaults)
    sync_prefs(repository, defaults)
    sync_gear(repository, defaults)
