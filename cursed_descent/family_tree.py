from typing import Any

from .births import child_label
from .models import Player
from .town_buildings.family import entries


PARENTS = ("mother", "father")
CHILDREN = ("son", "daughter")
SIBLINGS = ("sister", "brother")


def names_with(player:Player, roles:tuple[str, ...],
               repository:Any=None) -> list[tuple[str, str]]:
    return [(char_id, name) for char_id, name, role
            in entries(player, repository) if role in roles]


def grandparents(player:Player, repository:Any) -> list[str]:
    names = []
    for char_id, _ in names_with(player, PARENTS, repository):
        parent = repository.load_by_id(char_id)
        if parent is None:
            continue
        names += [name for _, name in names_with(parent, PARENTS,
                                                 repository)]
    return names


def others_with_child_of(player:Player, repository:Any) -> list[Player]:
    if repository is None:
        return []
    everyone = [repository.load(name) for name in repository.names()]
    everyone += repository.npc_players()
    return [other for other in everyone
            if other is not None and other.id != player.id
            and any(child.get("parent_id") == player.id
                    or child.get("parent") == player.name
                    for child in other.offspring)]


def family_tree(player:Player, repository:Any=None) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    if repository is not None:
        rows += [(0, f"Grandparent: {name}")
                 for name in grandparents(player, repository)]
    rows += [(1, f"{role.capitalize()}: {name}")
             for _, name, role in entries(player, repository)
             if role in PARENTS]
    rows.append((2, f"{player.name} (you)"))
    rows += [(2, f"Partner: {name}") for _, name, role
             in entries(player, repository) if role == "partner"]
    rows += [(2, f"{role.capitalize()}: {name}")
             for _, name, role in entries(player, repository)
             if role in SIBLINGS]
    rows += [(3, f"{role.capitalize()}: {name}")
             for _, name, role in entries(player, repository)
             if role in CHILDREN]
    rows += [(3, f"Child: {child_label(child)}"
              + (f" – with {child['parent']}" if child.get("parent")
                 else ""))
             for child in player.offspring]
    rows += [(3, f"Child: {child_label(child)} – carried by {other.name}")
             for other in others_with_child_of(player, repository)
             for child in other.offspring
             if child.get("parent_id") == player.id
             or child.get("parent") == player.name]
    rows += [(3, f"Grown up: {entry['name']} ({entry['species']})")
             for entry in player.profile.get("grown_up", [])]
    return rows
