from typing import Any

from ...config import ENEMY_DISPLAY_MAX, MAIDEN_CAPACITY, MAIDEN_GROWTH
from ...models import Enemy
from .content import DISPLAY_TEXTS, ENEMY_DISPLAYS, MAIDEN_TEXTS


def enemy_displays(enemies:list[Enemy], entries:list[dict[str, Any]],
                   run_id:str) -> list[str]:
    lines: list[str] = []
    shown: set[str] = set()
    for enemy in enemies:
        if enemy.template_id not in ENEMY_DISPLAYS or enemy.name in shown:
            continue
        fate, detail, key = ENEMY_DISPLAYS[enemy.template_id]
        names = [entry["name"] for entry in entries
                 if entry["fate"] == fate and entry["killer"] == enemy.name
                 and entry["run"] != run_id and entry.get("detail") != "spat"
                 and (not detail or entry.get("detail") == detail)]
        unique = list(dict.fromkeys(reversed(names)))[:ENEMY_DISPLAY_MAX]
        if unique:
            shown.add(enemy.name)
            lines.append(DISPLAY_TEXTS[key].format(enemy=enemy.name,
                                                   names=", ".join(unique)))
    return lines


def maiden_occupants(entries:list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [entry for entry in entries
            if entry["fate"] == "iron_maiden"
            and entry.get("detail") != "spat"]


def maiden_buff(enemies:list[Enemy],
                entries:list[dict[str, Any]]) -> list[str]:
    count = min(len(maiden_occupants(entries)), MAIDEN_CAPACITY)
    maidens = [enemy for enemy in enemies
               if enemy.template_id == "iron_maiden"]
    if not count or not maidens:
        return []
    factor = 1 + count * MAIDEN_GROWTH
    for enemy in maidens:
        for attribute in ("max_hp", "attack", "defense", "exp"):
            setattr(enemy, attribute,
                    round(getattr(enemy, attribute) * factor))
        enemy.hp = enemy.max_hp
    return [MAIDEN_TEXTS["buff"].format(
        enemy=maidens[0].name, count=count,
        occupants="occupant" if count == 1 else "occupants")]


def maiden_squeeze(remains:Any, entry:dict[str, Any],
                   stage:int) -> list[str]:
    occupants = maiden_occupants(remains.entries)
    others = [other["name"] for other in occupants
              if other is not entry and other["name"] != entry["name"]]
    lines: list[str] = []
    if others:
        names = ", ".join(list(dict.fromkeys(reversed(others)))[:3])
        lines.append(MAIDEN_TEXTS["squeeze"].format(name=entry["name"],
                                                    names=names))
    if len(occupants) > MAIDEN_CAPACITY:
        oldest = occupants[0]
        oldest["detail"] = "spat"
        oldest["stage"] = stage
        remains.save()
        lines.append(MAIDEN_TEXTS["spat"].format(old=oldest["name"],
                                                 stage=stage))
    return lines
