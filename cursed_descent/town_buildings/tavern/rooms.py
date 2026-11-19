import random

from ...models import Message, Player
from ...needs import satisfy
from ...towns.last_light_humans.cafe.swallow import clear_belly
from ..work.jobs import closed
from .content import (
    ROOM_TEXTS, ROOM_USAGE, TAVERN_ROOMS, TAVERN_THEFT_CHANCE,
    TAVERN_THEFT_GOLD, THEFT_TEXT,
)


def sleep_in_room(player:Player, text:str, in_run:bool, busy:bool,
                  rng:random.Random) -> list[Message]:
    if in_run:
        return closed("tavern", player)
    if busy:
        return [Message("Finish what you are doing first.", player.name)]
    kind = text.strip().casefold() or "common"
    if kind not in TAVERN_ROOMS:
        return [Message(ROOM_USAGE, player.name)]
    price = TAVERN_ROOMS[kind]
    if player.gold < price:
        return [Message(f"<<npc.hilda_first>> <<npc.hilda_last>> wants {price} gold for the {kind} "
                        f"room.", player.name)]
    player.gold -= price
    relief = {"sleep": -100}
    if kind == "private":
        relief.update(hunger=-20, thirst=-30)
    satisfy(player.needs, relief)
    lines = [f"{ROOM_TEXTS[kind]} -{price} gold (💰 {player.gold})"]
    belly = clear_belly(player)
    if belly:
        lines.append(belly)
    if (kind == "common" and player.gold > 0
            and rng.random() < TAVERN_THEFT_CHANCE):
        stolen = min(player.gold, rng.randint(*TAVERN_THEFT_GOLD))
        player.gold -= stolen
        lines.append(THEFT_TEXT.format(gold=stolen))
    return [Message("\n".join(lines), player.name)]
