import random
from typing import Any

from .config import (
    BARTER_RATIO, COACH_LIMIT, COACH_PRICE, COACH_STATS, COACH_TIER_POINTS,
    GIFT_MAX, GIFT_STEP, INTIMACY_BOND, INTIMACY_MIN_AGE, INTIMACY_RELIEF,
    ROMANCE_POINTS,
)
from .content import ITEMS
from .dungeon import find_inventory_item
from .intimacy import conception
from .preferences import scene_defaults
from .scenes import DEFAULTS, describe, parse_options
from .items import remove_item
from .locations.shop.location import base_price
from .models import Message, Player
from .needs import satisfy
from .npcs.talk import town_company
from .npcs.store import find_local
from .town_buildings.chat import friendship, tier_of


def private(text:str, player:Player) -> list[Message]:
    return [Message(text, player.name)]


def locate(player:Player, repository:Any, name:str) -> Player | None:
    return find_local(town_company(repository, player), name)


def bump(npc:Player, player:Player, points:int) -> str:
    before = tier_of(friendship(npc, player))
    friends = npc.profile.setdefault("friends", {})
    friends[player.id] = friends.get(player.id, 0) + points
    after = tier_of(friends[player.id])
    if after == before:
        return ""
    return f" ({npc.first_name} now counts you as: {after}.)"


def gift_points(item_id:str) -> int:
    item = ITEMS[item_id]
    liked = 1 if item.get("needs") else 0
    return min(GIFT_MAX, 1 + liked + base_price(item_id) // GIFT_STEP)


def gift(player:Player, npc:Player, reference:str,
         repository:Any) -> list[Message]:
    item_id = find_inventory_item(player, reference)
    if item_id is None:
        return private("No such item in your bag.", player)
    remove_item(player.inventory, item_id)
    note = bump(npc, player, gift_points(item_id))
    repository.save(player)
    repository.save(npc)
    return [Message(f"🎁 {player.name} gives {npc.first_name} "
                    f"{ITEMS[item_id]['name']}. {npc.first_name} "
                    f"smiles.{note}")]


def barter(player:Player, npc:Player, reference:str,
           repository:Any) -> list[Message]:
    item_id = find_inventory_item(player, reference)
    if item_id is None:
        return private("No such item in your bag.", player)
    price = max(1, round(base_price(item_id) * BARTER_RATIO))
    remove_item(player.inventory, item_id)
    player.gold += price
    repository.save(player)
    return [Message(f"🤝 {npc.first_name} takes {ITEMS[item_id]['name']} "
                    f"for {price} gold. 💰 {player.gold}", player.name)]


def coach(player:Player, npc:Player, repository:Any) -> list[Message]:
    stat = COACH_STATS.get(npc.profile.get("building", ""))
    if stat is None:
        return private(f"{npc.first_name} has nothing to teach.", player)
    if friendship(npc, player) < COACH_TIER_POINTS:
        return private(f"{npc.first_name} doesn't know you well enough "
                       f"to train you. Talk a little first.", player)
    taught = player.profile.setdefault("coached", {})
    if taught.get(npc.id, 0) >= COACH_LIMIT:
        return private(f"{npc.first_name} has taught you everything "
                       f"{npc.first_name} can.", player)
    price = COACH_PRICE * player.stats[stat]
    if player.gold < price:
        return private(f"{npc.first_name} charges {price} gold for a "
                       f"lesson ({stat}). You have {player.gold}.", player)
    player.gold -= price
    player.stats[stat] += 1
    taught[npc.id] = taught.get(npc.id, 0) + 1
    repository.save(player)
    return [Message(f"🏋 {npc.first_name} drills {player.name} for hours. "
                    f"+1 {stat} for {price} gold. "
                    f"({taught[npc.id]}/{COACH_LIMIT}) 💰 {player.gold}",
                    player.name)]


def romance_scene(player:Player, npc:Player, repository:Any,
                  rng:random.Random,
                  options:dict[str, str] | None=None) -> list[Message]:
    story, giver, carrier, factor = describe(
        player, npc, options or DEFAULTS, rng)
    lines = [f"💞 {' '.join(story)}"]
    satisfy(player.needs, INTIMACY_RELIEF)
    note = bump(npc, player, INTIMACY_BOND)
    if note:
        lines.append(note.strip())
    if giver is not None:
        lines += conception(giver, carrier, rng, factor)
    repository.save(player)
    repository.save(npc)
    return [Message("\n".join(lines))]


def romance(player:Player, npc:Player, repository:Any,
            rng:random.Random,
            options:dict[str, str] | None=None) -> list[Message]:
    if min(player.age, npc.age) < INTIMACY_MIN_AGE:
        return private(f"{npc.first_name} is not available.", player)
    if friendship(npc, player) < ROMANCE_POINTS:
        return private(f"{npc.first_name} smiles politely. 'Not yet, "
                       f"{player.name}. Give it time.'", player)
    return romance_scene(player, npc, repository, rng, options)


def npc_command(command:str, args:list[str], player:Player,
                repository:Any, in_run:bool, on_shift:bool,
                rng:random.Random) -> list[Message]:
    if in_run:
        return private("The neighbours are far away while you are in the "
                       "dungeon.", player)
    if on_shift:
        return private("Not during a shift.", player)
    if not args:
        return private(f"Usage: {command} <neighbour>"
                       + (" <item>" if command in ("gift", "barter")
                          else ""), player)
    needs_item = command in ("gift", "barter")
    options = scene_defaults(player)
    if command == "romance":
        args, options = parse_options(args, options)
    name = args[0] if needs_item else " ".join(args)
    npc = locate(player, repository, name)
    if npc is None:
        return private(f"Nobody called '{name}' is around.", player)
    if needs_item:
        reference = " ".join(args[1:])
        return (gift if command == "gift" else barter)(
            player, npc, reference, repository)
    if command == "coach":
        return coach(player, npc, repository)
    return romance(player, npc, repository, rng, options)
