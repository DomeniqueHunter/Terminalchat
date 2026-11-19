from typing import Any

from ....config import (
    CAFE_CLAIM_PRICE, CAFE_NPC_BUY_CHANCE, CAFE_RANSOM_PRICE,
    CAFE_RANSOM_RISE, CAFE_RIDER_RELIEF,
)
from ....captivity import free as free_captive, is_captive
from ....models import Message, Player
from ....needs import satisfy
from .furniture import FURNITURE_QUOTES
from .stools import Stool, describe


STOOL_OPEN = {"help", "profile", "sheet", "inv", "needs", "spells", "top",
              "graveyard", "examine", "status", "town", "talk", "chat",
              "meet", "rumors", "safeword"}


def stool_price(npc:Player) -> int:
    base = CAFE_RANSOM_PRICE * npc.level
    return base * npc.profile.get("ransom_mult", 1)


def owner_of(npc:Player) -> str:
    return npc.profile.get("owner", "")


def claim_stool(stool:Stool, repository:Any, day:int) -> Player:
    name = stool.name
    while repository.exists(name):
        name += "x"
    npc = Player(name=name, gender="Male", first_name=stool.name,
                 free_points=0, npc="furniture", age=stool.age,
                 body={"height": stool.height, "weight": stool.weight,
                       "build": stool.build})
    npc.profile = {
        "kind": "furniture", "role": "Stool of the Fat Ass Café",
        "look": describe(stool), "quotes": list(FURNITURE_QUOTES),
        "kept": {"kind": "mercenary", "role": "a former café stool"},
        "restore_npc": "mercenary", "since": day}
    repository.save(npc)
    return npc


def residents(repository:Any) -> list[Player]:
    return [npc for npc in repository.npc_players()
            if npc.profile.get("kind") == "resident"]


def npc_buys(services:Any, day:int) -> list[Message]:
    buyers = residents(services.repository)
    messages: list[Message] = []
    if not buyers:
        return messages
    for npc in services.repository.npc_players():
        if (npc.npc != "furniture" or owner_of(npc)
                or day - npc.profile.get("since", day) < 1
                or services.rng.random() >= CAFE_NPC_BUY_CHANCE):
            continue
        buyer = services.rng.choice(buyers)
        place = buyer.profile.get("building", "") or "town"
        npc.profile["owner"] = buyer.full_name
        npc.profile["place"] = place.replace("_", " ")
        npc.profile["ransom_mult"] = CAFE_RANSOM_RISE
        services.repository.save(npc)
        text = (f"{buyer.full_name} bought {npc.full_name} from the Fat "
                f"Ass Café and put him in the {npc.profile['place']} as a "
                f"stool. Ransoming him costs more now.")
        messages += [Message(text, name)
                     for name in services.repository.names()]
    return messages


def where_text(npc:Player) -> str:
    owner = owner_of(npc)
    if not owner:
        return "in the café"
    return f"at {owner}'s, {npc.profile.get('place', 'somewhere')}"


def ransom_home(services:Any, player:Player, npc:Player) -> list[Message]:
    price = stool_price(npc)
    if player.gold < price:
        return [Message(f"{npc.full_name} costs {price} gold.",
                        player.name)]
    player.gold -= price
    npc.profile["owner"] = player.name
    npc.profile["place"] = "home"
    npc.profile.pop("ransom_mult", None)
    services.repository.save(npc)
    player.profile.setdefault("home_stools", [])
    if npc.name not in player.profile["home_stools"]:
        player.profile["home_stools"].append(npc.name)
    services.repository.save(player)
    return [Message(f"{player.name} pays {price} gold and has "
                    f"{npc.full_name} carried home: a stool for the "
                    f"living room now. [home sit {npc.first_name}] to use "
                    f"him, [home free {npc.first_name}] to let him go.",
                    player.name)]


def claim(services:Any, player:Player) -> list[Message]:
    stool = services.claims.get(player.name)
    if stool is None:
        return [Message("There is nobody to claim. A stool must have been "
                        "ruined under you first.", player.name)]
    if player.gold < CAFE_CLAIM_PRICE:
        return [Message(f"Bertha wants {CAFE_CLAIM_PRICE} gold for what is "
                        f"left of {stool.name}.", player.name)]
    player.gold -= CAFE_CLAIM_PRICE
    del services.claims[player.name]
    npc = claim_stool(stool, services.repository, services.world.day)
    return [Message(f"{player.name} pays {CAFE_CLAIM_PRICE} gold. Bertha "
                    f"has {npc.full_name} fitted into a padded frame and "
                    f"set among the stools of the house. [ransom "
                    f"{npc.first_name} home] takes him with you.",
                    player.name)]


def home_stools(services:Any, player:Player) -> list[Player]:
    found = []
    for name in player.profile.get("home_stools", []):
        other = services.repository.load(name)
        if other is not None:
            found.append(other)
    return found


def own_target(services:Any, player:Player, text:str) -> Player | None:
    wanted = text.strip().casefold()
    if not wanted:
        return None
    for other in services.repository.npc_players() + [
            services.repository.load(name)
            for name in services.repository.names()]:
        if (other is not None and other.name != player.name
                and wanted in (other.name.casefold(),
                               other.first_name.casefold(),
                               other.full_name.casefold())):
            return other
    return None


def stool_command(services:Any, player:Player, args:list[str]
                  ) -> list[Message]:
    word = args[0].casefold() if args else ""
    rest = " ".join(args[1:])
    if word == "yield":
        return agree(services, player)
    mine = home_stools(services, player)
    if word == "sit":
        return sit(services, player, mine, rest)
    if word == "free":
        return free(services, player, mine, rest)
    if word == "stool" and rest:
        return add(services, player, rest)
    lines = [f"{who.full_name} – {who.profile.get('look', 'a stool')}"
             for who in mine]
    return [Message("\n".join(["Your home stools:"] + lines) if lines
                    else "You have no home stools. [home stool <name>] "
                    "or [ransom <name> home].", player.name)]


def find_mine(mine:list[Player], text:str) -> Player | None:
    wanted = text.strip().casefold()
    if not wanted and len(mine) == 1:
        return mine[0]
    return next((who for who in mine
                 if wanted in (who.name.casefold(),
                               who.first_name.casefold(),
                               who.full_name.casefold())), None)


def sit(services:Any, player:Player, mine:list[Player], text:str
        ) -> list[Message]:
    who = find_mine(mine, text)
    if who is None:
        return [Message("Sit on whom? [home sit <name>]", player.name)]
    satisfy(player.needs, {"arousal": -CAFE_RIDER_RELIEF})
    services.repository.save(player)
    return [Message(f"{player.name} sits down on {who.full_name}. "
                    f"{who.profile.get('look', '')}", player.name)]


def release(services:Any, owner:Player, who:Player) -> None:
    owner.profile["home_stools"] = [
        name for name in owner.profile.get("home_stools", [])
        if name != who.name]
    who.profile.pop("owner", None)
    who.profile.pop("place", None)
    who.profile.pop("stool_of", None)
    if is_captive(who):
        free_captive(who, services.repository)
    elif who.npc == "furniture":
        restore = who.profile.get("restore_npc", "")
        who.profile = dict(who.profile.get("kept", {}))
        services.repository.convert(who.name, restore)
    else:
        services.repository.save(who)
    services.repository.save(owner)


def free(services:Any, player:Player, mine:list[Player], text:str
         ) -> list[Message]:
    who = find_mine(mine, text)
    if who is None:
        return [Message("Free whom? [home free <name>]", player.name)]
    release(services, player, who)
    return [Message(f"{player.name} lets {who.full_name} up. He stretches, "
                    f"rubs his knees and is his own man again.",
                    player.name),
            Message(f"{player.name} lets you up. You are free again.",
                    who.name)]


def add(services:Any, player:Player, text:str) -> list[Message]:
    if services.in_run(player):
        return [Message("Not from the dungeon.", player.name)]
    who = own_target(services, player, text)
    if who is None or who.gender != "Male" or who.npc == "furniture":
        return [Message("Only a man of your own can be a home stool: "
                        "[home stool <name>].", player.name)]
    if who.profile.get("stool_of") or who.name in player.profile.get(
            "home_stools", []):
        return [Message(f"{who.full_name} is already a stool.",
                        player.name)]
    if services.in_run(who) or who.name in services.shifts:
        return [Message(f"{who.full_name} is busy.", player.name)]
    if who.npc:
        place(player, who)
        services.repository.save(who)
        services.repository.save(player)
        return [Message(f"{who.full_name} kneels in your living room and "
                        f"takes the board on his back. [home sit "
                        f"{who.first_name}]", player.name)]
    who.profile["stool_offer"] = player.name
    services.repository.save(who)
    return [Message(f"{who.name} is asked to kneel for you. [home yield] "
                    f"from {who.name} makes it so.", player.name),
            Message(f"{player.name} wants you as a home stool. [home "
                    f"yield] agrees; anything else ignores it.", who.name)]


def place(owner:Player, who:Player) -> None:
    who.profile["stool_of"] = owner.name
    owner.profile.setdefault("home_stools", []).append(who.name)


def agree(services:Any, player:Player) -> list[Message]:
    owner_name = player.profile.pop("stool_offer", "")
    owner = services.repository.load(owner_name) if owner_name else None
    if owner is None:
        return [Message("Nobody has asked you to be a stool.",
                        player.name)]
    if services.in_run(player) or player.name in services.shifts:
        return [Message("Not right now.", player.name)]
    place(owner, player)
    services.repository.save(owner)
    services.repository.save(player)
    return [Message(f"You kneel under {owner.name}'s board and hold "
                    f"still. [safeword] gets you up any time.",
                    player.name),
            Message(f"{player.name} kneels in your living room as a "
                    f"stool. [home sit {player.name}]", owner.name)]


def stool_lock(player:Player, command:str) -> list[Message]:
    owner = player.profile.get("stool_of")
    if not owner or command in STOOL_OPEN:
        return []
    return [Message(f"You are {owner}'s stool and hold still. [safeword] "
                    f"gets you up.", player.name)]


def stand_up(services:Any, player:Player) -> list[Message]:
    owner = services.repository.load(player.profile.get("stool_of", ""))
    if owner is None:
        player.profile.pop("stool_of", None)
        services.repository.save(player)
    else:
        release(services, owner, player)
    return [Message("You stand up and stretch. Done being furniture.",
                    player.name)]
