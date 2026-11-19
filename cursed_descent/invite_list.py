from typing import Any

from .house_regulars import regular_player
from .house_visit import dynamic_of
from .npc_menu import locate
from .party_talk import bonds
from .town_buildings.chat import friendship
from .town_buildings.visits import ask_address


MODE_FOR = {"player": "Submissive", "npc": "Dominant", "": "Plain guest"}


def invite_candidates(app:Any, player:Any, town:Any,
                      present:set[str]) -> list[tuple[str, Any, int]]:
    found: list[tuple[str, Any, int]] = []
    for resident in town.residents:
        if resident.first_name.casefold() not in present:
            npc = locate(player, app.controller.repository,
                         resident.first_name)
            found.append((resident.first_name, npc,
                          friendship(npc, player) if npc else 0))
    store = app.controller.town.regulars_of(player)
    for building in ("cafe", "brothel"):
        for record in store.all(building):
            if ask_address(record) and (
                    record["name"].casefold() not in present):
                found.append((record["name"],
                              regular_player(building, record),
                              record.get("visits", 0)))
    repository = app.controller.repository
    names = [entry[0] for entry in found]
    for name in app.known_players():
        if (name.casefold() == player.name.casefold()
                or name.casefold() in present or name in names):
            continue
        hero = repository.load(name)
        found.append((name, hero, bonds(player).get(
            hero.id, 0) if hero is not None else 0))
    found.sort(key=lambda entry: (-entry[2], entry[0].casefold()))
    return found


def suggested_mode(player:Any, other:Any) -> str:
    if other is None:
        return "Plain guest"
    building = "cafe" if other.id.startswith("reg:cafe") else ""
    return MODE_FOR[dynamic_of(player, other, {"building": building})]
