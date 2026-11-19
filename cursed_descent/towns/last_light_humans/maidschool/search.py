from dataclasses import dataclass, field

from ....config import MAID_SEARCH_FEE, MAID_SEARCH_MAX
from ....models import Message, Player
from ....npcs.generator import make_maid
from ....npcs.hire import hire_price


@dataclass
class Search:
    maids: list[Player] = field(default_factory=list)
    index: int = 0


def taken_names(services, search:Search) -> set[str]:
    names = {npc.name.casefold() for npc in services.repository.npc_players()}
    names |= {name.casefold() for name in services.repository.names()}
    return names | {maid.name.casefold() for maid in search.maids}


def card(search:Search) -> str:
    maid = search.maids[search.index]
    stats = ", ".join(f"{key[:3]} {value}"
                      for key, value in maid.stats.items())
    return (f"🎀 Maid {search.index + 1}/{MAID_SEARCH_MAX}: "
            f"{maid.full_name}, {maid.age}, {maid.gender}, Lv {maid.level}. "
            f"{maid.profile['blurb']} ({maid.personality}) – {stats}. "
            f"Price: {hire_price(maid)} gold.")


def current(services, player:Player) -> Search | None:
    return services.maid_search.get(player.name)


def look(services, player:Player) -> list[Message]:
    search = current(services, player)
    if search is None or not search.maids:
        search = Search()
        search.maids.append(make_maid(services.rng,
                                      taken_names(services, search)))
        services.maid_search[player.name] = search
    return [Message(card(search), player.name)]


def next_maid(services, player:Player) -> list[Message]:
    search = current(services, player)
    if search is None or not search.maids:
        return look(services, player)
    if search.index + 1 < len(search.maids):
        search.index += 1
        return [Message(card(search), player.name)]
    if len(search.maids) >= MAID_SEARCH_MAX:
        return [Message(f"Brunhild shakes her head: that was every maid "
                        f"she has free today ({MAID_SEARCH_MAX}).",
                        player.name)]
    if player.gold < MAID_SEARCH_FEE:
        return [Message(f"Brunhild's clerk wants {MAID_SEARCH_FEE} gold to "
                        f"fetch the next maid.", player.name)]
    player.gold -= MAID_SEARCH_FEE
    search.maids.append(make_maid(services.rng,
                                  taken_names(services, search)))
    search.index = len(search.maids) - 1
    return [Message(f"You pay {MAID_SEARCH_FEE} gold. " + card(search),
                    player.name)]


def previous_maid(services, player:Player) -> list[Message]:
    search = current(services, player)
    if search is None or not search.maids:
        return look(services, player)
    search.index = max(0, search.index - 1)
    return [Message(card(search), player.name)]


def recruit(services, player:Player) -> list[Message]:
    search = current(services, player)
    if search is None or not search.maids:
        return [Message("Look for a maid first.", player.name)]
    maid = search.maids[search.index]
    price = hire_price(maid)
    if player.gold < price:
        return [Message(f"{maid.full_name} costs {price} gold "
                        f"(you have {player.gold}).", player.name)]
    player.gold -= price
    maid.profile["owner"] = player.name
    services.repository.add(maid)
    del search.maids[search.index]
    search.index = max(0, min(search.index, len(search.maids) - 1))
    return [Message(f"{player.name} pays {price} gold. {maid.full_name} "
                    f"signs Brunhild's ledger and is now one of your "
                    f"maids. She joins a party from the lobby, free of "
                    f"charge.", player.name)]
