import random
from typing import Any, NamedTuple

from ....control import die, holders, start, witnesses
from ....models import Message, Player
from ....npcs.store import find_local
from ....routines import HIDDEN, PLACES, WINDOWS
from .content import INVITE_KEY

KIND = "leash_slave"
HOLDER = "alexandra"
NPC_SLAVES = ("edric_vane", "tomas_wren")
CAP = 2
ODDS = 0.7
COOLDOWN_HOURS = 24
FOREVER = 10 ** 9
FIRST = ("Corvin", "Lisbet", "Darian", "Mireille", "Aldous", "Sabine",
         "Tobiah", "Ysolde", "Casimir", "Neve", "Orrin", "Wilhelmina",
         "Jasper", "Odette", "Lucan", "Perrin", "Isaure", "Emeric")
GENDERS = ("Male", "Female")
PENDING = "castle_offer_pending"
LATER = "castle_offer_later"

WARN = ("The Duchess keeps {cap} slaves, never more. If she accepts you, "
        "you are hers for two world days: you will follow her, you will "
        "not control your body, and you can only watch. A slave who is "
        "the oldest when a newcomer arrives is drunk dry, even a "
        "player's.{drain} Select the "
        "offer again to go through with it.")
WARN_DRAIN = (" Her household is full, so the oldest, {oldest}, will be "
              "emptied – drunk to the last drop – to make room.")
NOT_RECEIVING = ("Mina Vasek shakes her head. 'The Duchess is not "
                 "receiving. {reason}'")
NO_ROOM = ("Mina Vasek shakes her head. 'The household is full of "
           "guests of the Duchess, and she has nobody to spare. Come back "
           "when one of them has left.'")
REFUSED = [
    "Alexandra lets the silence run until it is uncomfortable. 'No,' she "
    "says at last, almost gently. 'Not tonight. Ask me again when you are "
    "less eager.'",
    "She tilts your chin up with one finger, looks, and lets go. 'You "
    "would break too quickly,' says the Duchess. 'Try again tomorrow.'",
]
ACCEPTED = (
    "Alexandra rises. For the first time a smile reaches her eyes. "
    "'Kneel,' she says, and you are already kneeling. Mina has the collar "
    "ready.")
DRAIN = (
    "{oldest} is led to the middle of the hall. Alexandra takes {oldest} "
    "in her arms like a lover, bends over the throat, and does not stop "
    "until there is nothing left to take. She straightens, flushed and "
    "radiant, stronger than before. Servants carry the body out. By "
    "morning a new face will kneel in the same place.")


DRAIN_PLAYER = (
    "A newcomer kneels, and the Duchess needs room. Alexandra turns to "
    "you, takes you in her arms like a lover, and bends over your throat. "
    "You can only watch as she drinks. The hall grows dim, then dark. "
    "💀 You are dead – drunk dry by Alexandra.")


class Member(NamedTuple):
    since: float
    kind: str
    who: Any


def alive_residents(services:Any) -> list[tuple[int, Any]]:
    npcs = services.repository.npc_players()
    found = []
    for index, key in enumerate(NPC_SLAVES):
        npc = find_local(npcs, key)
        if npc is None:
            continue
        old = npc.profile.pop("slave_gone", 0)
        if (old or npc.profile.get("gone_until")) and not npc.profile.get(
                "dead"):
            npc.profile.update(dead=True, gone_until=FOREVER)
            services.repository.save(npc)
        if not npc.profile.get("dead"):
            found.append((index, npc))
    return found


def new_slave(services:Any) -> Player:
    rng: random.Random = services.rng
    taken = {npc.first_name for npc in services.repository.npc_players()}
    name = rng.choice([n for n in FIRST if n not in taken] or list(FIRST))
    slave = Player(name=services.repository.unique_handle(name),
                   first_name=name, gender=rng.choice(GENDERS), npc="slave")
    slave.profile = {
        "kind": "resident", "town": "dusk_hollow", "building": "castle",
        "control": KIND, "role": "Leash slave of the Duchess",
        "holder": "Alexandra", "since": services.world_hours(),
        "look": f"{name} kneels at the Duchess's heel, collar bright, "
                f"eyes on the floor.",
        "quotes": ["'Please do not make me look up.'"]}
    services.repository.add(slave)
    return slave


def refill(services:Any) -> None:
    held = len(holders(KIND, services.repository))
    npcs = len(alive_residents(services)) + len(
        [npc for npc in services.repository.npc_players()
         if npc.npc == "slave" and npc.profile.get("control") == KIND])
    for _ in range(max(0, CAP - held - npcs)):
        new_slave(services)


def members(services:Any) -> list[Member]:
    refill(services)
    found = [Member(npc.profile.get("slave_since", index - len(NPC_SLAVES)),
                    "resident", npc)
             for index, npc in alive_residents(services)]
    for npc in services.repository.npc_players():
        if npc.npc == "slave" and npc.profile.get("control") == KIND:
            found.append(Member(npc.profile["since"], "clone", npc))
    for player in holders(KIND, services.repository):
        found.append(Member(player.profile["control"]["since"],
                            "player", player))
    return sorted(found, key=lambda member: member.since)


def reason(services:Any) -> str:
    npc = find_local(services.repository.npc_players(), HOLDER)
    if HOLDER in PLACES:
        return "She is out of the castle tonight."
    if WINDOWS.get(HOLDER) == "sleep":
        return "She is asleep."
    return "" if npc is not None else "She cannot be found."


def drain(services:Any, member:Member) -> str:
    name = member.who.first_name or member.who.name
    if member.kind == "player":
        die(services, member.who, "drained", DRAIN_PLAYER)
        return DRAIN.format(oldest=name)
    services.repository.bury(member.who, "drained by Alexandra")
    if member.kind == "resident":
        member.who.profile["dead"] = True
        member.who.profile["gone_until"] = FOREVER
        services.repository.save(member.who)
        HIDDEN.add(member.who.npc)
    else:
        services.repository.release(member.who)
    return DRAIN.format(oldest=name)


def sate(services:Any) -> None:
    duchess = find_local(services.repository.npc_players(), HOLDER)
    if duchess is not None:
        duchess.level += 1
        services.repository.save(duchess)


def oldest_name(services:Any) -> str:
    found = members(services)
    return (found[0].who.first_name or found[0].who.name) if found else "one"


def offer_self(services:Any, player:Player, offer:Any) -> list[Message]:
    rng: random.Random = services.rng
    if not player.profile.get(INVITE_KEY):
        from .rules import locked
        return [Message(line, player.name)
                for line in locked(player, rng)]
    why = reason(services)
    if why:
        return [Message(NOT_RECEIVING.format(reason=why), player.name)]
    now = services.world_hours()
    if player.profile.get(LATER, 0) > now:
        return [Message("'Not yet,' says Mina Vasek. 'The Duchess "
                        "remembers your face.'", player.name)]
    asked = services.__dict__.setdefault(PENDING, set())
    if player.name not in asked:
        asked.add(player.name)
        full = len(members(services)) >= CAP
        drain_line = (WARN_DRAIN.format(oldest=oldest_name(services))
                      if full else "")
        return [Message(WARN.format(cap=CAP, drain=drain_line),
                        player.name)]
    asked.discard(player.name)
    if rng.random() >= ODDS:
        player.profile[LATER] = now + COOLDOWN_HOURS
        services.repository.save(player)
        return [Message(rng.choice(REFUSED), player.name)]
    lines = [ACCEPTED]
    found = members(services)
    extra: list[Message] = []
    if len(found) >= CAP:
        victim = found[0]
        text = drain(services, victim)
        lines.append(text)
        sate(services)
        skip = victim.who.name if victim.kind == "player" else ""
        extra = [message for message in witnesses(services, player, text)
                 if message.recipient != skip]
        if victim.kind == "player":
            extra.append(Message(DRAIN_PLAYER, victim.who.name))
    messages = [Message("\n".join(lines), player.name)] + extra
    return messages + start(services, player, KIND, "Alexandra",
                            npc=HOLDER)


def household_lines(services:Any, player:Player) -> tuple[str, ...]:
    found = members(services)
    names = ", ".join(
        (member.who.first_name or member.who.name)
        + (" (player)" if member.kind == "player" else "")
        for member in found)
    lines = [f"The Duchess keeps {len(found)} of {CAP} slaves: {names}."]
    if found:
        lines.append(
            f"Next in line: {found[0].who.first_name or found[0].who.name}.")
    return tuple(lines)
