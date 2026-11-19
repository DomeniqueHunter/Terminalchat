import random

from ..dungeon import give_item
from ..formulas import max_hp
from ..locations.shop.location import base_price
from ..models import Message, Player
from . import registry
from .counter import Offer, Special


DEFAULT_CLOSED = "The doors are barred while you are down in the dungeon."


def offer_price(offer:Offer) -> int:
    if offer.kind == "item":
        return round(base_price(offer.item) * offer.factor)
    return offer.price


def hidden(player:Player, offer:Offer) -> bool:
    if offer.show_if and not player.profile.get(offer.show_if):
        return True
    return bool(offer.hide_if and player.profile.get(offer.hide_if))


def menu(player:Player, special:Special) -> list[Message]:
    lines = [f"{special.icon} {special.title} – {special.keeper} greets "
             f"{player.name}: {special.quote}",
             f"💰 Gold: {player.gold}"]
    for number, offer in enumerate(special.offers, 1):
        if hidden(player, offer):
            continue
        price = offer_price(offer)
        lines.append(f"  [{special.key} {number}] {offer.label}"
                     f"{f' – {price} gold' if price else ''}")
    return [Message("\n".join(lines), player.name)]


def hurt(player:Player, share:float) -> int:
    loss = min(player.hp - 1, max(1, round(max_hp(player) * share)))
    player.hp -= max(0, loss)
    return max(0, loss)


def take(player:Player, special:Special, number:int,
         rng:random.Random) -> list[Message]:
    offer = special.offers[number - 1]
    price = offer_price(offer)
    if player.gold < price:
        return [Message(f"That costs {price} gold. {player.name} only has "
                        f"{player.gold}.", player.name)]
    player.gold -= price
    if offer.kind == "item":
        if len(player.inventory) >= player.bag_size:
            player.gold += price
            return [Message("The bag is full.", player.name)]
        lines = [f"{player.name} pays {price} gold.",
                 give_item(player, offer.item)]
    else:
        lines = special.handlers[offer.kind](player, offer, price, rng)
    lines.append(f"💰 Gold: {player.gold}")
    return [Message("\n".join(lines), player.name)]


def run(services, player:Player, key:str, args:list[str]) -> list[Message]:
    from .shifts import work
    spec = registry.get(key)
    special = spec.counter
    if services.in_run(player):
        return [Message(spec.closed or DEFAULT_CLOSED, player.name)]
    if not args or not args[0].isdigit() or not (
            1 <= int(args[0]) <= len(special.offers)):
        return menu(player, special)
    offer = special.offers[int(args[0]) - 1]
    if offer.kind == "job":
        return work(player, key, offer.item, False, services.shifts,
                    services.rng, services.now, timed=True)
    if offer.kind in special.starters:
        return special.starters[offer.kind](services, player, offer)
    return take(player, special, int(args[0]), services.rng)
