import random
from typing import Any

from ...config import (
    BURDEN_REST, DEFAULT_GENDER, FARM_KEEP_EVENT, FARM_SHIFT_GOLD, FARM_SHIFT_HEAL,
    FARM_SHIFT_HURT, FARM_SHIFT_ITEMS, FARM_SHIFT_SWEAT, PRONOUNS,
)
from ...content import ITEMS
from ...dungeon import give_item
from ...formulas import max_hp
from ...models import Player
from .content import FARM_SHIFT_EVENTS, FARM_SHIFT_TEXTS


def pronoun_values(player:Player) -> dict[str, str]:
    they, them, their = PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])
    return {"name": player.name, "they": they, "them": them, "their": their,
            "Their": their.capitalize()}


class FarmEventsMixin:
    session: Any
    event: dict[str, Any]

    def shift_event(self, player:Player,
                    shift:dict[str, Any]) -> str:
        pool = FARM_SHIFT_EVENTS[shift["job"]] + FARM_SHIFT_EVENTS["any"]
        kind, text = random.choice(pool)
        worker = self.worker_name()
        if kind == "worker" and not worker:
            kind, text = "sweat", FARM_SHIFT_TEXTS["quiet"]
        values = pronoun_values(player)
        if kind == "hurt":
            hp = round(max_hp(player) * FARM_SHIFT_HURT)
            player.hp = max(0, player.hp - hp)
            return text.format(hp=hp, **values)
        if kind == "heal":
            hp = round(max_hp(player) * FARM_SHIFT_HEAL)
            player.hp = min(max_hp(player), player.hp + hp)
            if shift.get("burden"):
                shift["stamina"] += BURDEN_REST
            return text.format(hp=hp, **values)
        if kind == "gold":
            gold = random.randint(*FARM_SHIFT_GOLD)
            shift["earned"] += gold
            return text.format(gold=gold, **values)
        if kind == "item":
            item_id = FARM_SHIFT_ITEMS[shift["job"]]
            line = text.format(item=ITEMS[item_id]["name"], **values)
            return f"{line}\n{give_item(player, item_id)}"
        if kind == "keep":
            shift["interest"] += FARM_KEEP_EVENT
        if kind == "sweat":
            player.sweat += FARM_SHIFT_SWEAT
        return text.format(worker=worker, **values)
