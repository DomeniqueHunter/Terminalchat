import random
from typing import Any

from .races import RACES, race_named, race_of
from .config import DEFAULT_GENDER, GROWN_UP_RUNS, PRONOUNS, SPECIES_OF_KIND
from .content import OFFSPRING_NAMES, OFFSPRING_TEXTS
from .locations.citystop.content import STATION_ID
from .locations.mage_tower.content import MAGE_ID
from .towns import TOWNS
from .models import Player


def child_label(child:dict[str, str]) -> str:
    name = f"{child['name']} {child.get('surname', '')}".strip()
    species = child.get("species", SPECIES_OF_KIND.get(child["kind"], "human"))
    runs = child.get("runs", 0)
    return f"{name} ({species}, {runs}/{GROWN_UP_RUNS} runs)"


def add_child(player:Player, rng:random.Random | None=None
              ) -> dict[str, str]:
    rng = rng or random
    kind = player.pregnant
    parent = player.profile.pop("pregnant_by", "")
    player.profile.pop("pregnant_nights", None)
    parent_id = player.profile.pop("pregnant_by_id", "")
    station = (TOWNS[parent_id[len(STATION_ID):]].race_key
               if parent_id.startswith(STATION_ID) else "")
    child = {"name": rng.choice(OFFSPRING_NAMES[kind]), "kind": kind,
             "species": ("human" if parent_id == MAGE_ID
                         else station if station
                         else race_of(player).key if kind == "party"
                         else SPECIES_OF_KIND.get(kind, "human")),
             "surname": player.last_name, "runs": 0,
             **({"parent": parent} if parent else {}),
             **({"parent_id": parent_id} if parent_id else {})}
    player.offspring.append(child)
    player.pregnant = ""
    return child


def give_birth(player:Player, rng:random.Random | None=None) -> str:
    kind = player.pregnant
    child = add_child(player, rng)
    pronouns = PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])
    they, their = pronouns[0], pronouns[2]
    key = "birth_party" if kind == "party" else "birth"
    full = f"{child['name']} {child['surname']}".strip()
    return OFFSPRING_TEXTS[key].format(
        name=player.name, they=they, their=their, kind=child["species"],
        child=full, parent=child.get("parent", ""),
        are="are" if they == "they" else "is")


def age_offspring(player:Player, store:Any=None) -> list[str]:
    lines: list[str] = []
    staying: list[dict[str, str]] = []
    for child in player.offspring:
        child["runs"] = child.get("runs", 0) + 1
        if child["runs"] < GROWN_UP_RUNS:
            staying.append(child)
            continue
        full = f"{child['name']} {child.get('surname', '')}".strip()
        species = child.get("species", "human")
        adventurer = race_named(species).adventurers and (
            species in RACES)
        role = ("an adventurer" if adventurer else f"an {species}"
                if species[0] in "aeiou" else f"a {species}")
        goal = ("sets out to seek fortune and glory"
                if adventurer else "leaves town for the wild")
        entry = {"name": full, "species": species}
        player.profile.setdefault("grown_up", []).append(entry)
        if store is not None:
            store.add({**entry, "role": ("adventurer" if adventurer
                                         else "grown_child"),
                       "parent": player.name, "parent_id": player.id})
        lines.append(f"🌱 {full}, {player.name}'s child, is grown up. "
                     f"As {role}, {full} {goal} and does not come "
                     f"back.")
    player.offspring = staying
    return lines
