from ..config import PRIVATE_WHERE
from ..controller import GameController
from ..models import Message
from ..towns import town_key
from . import views


RUN_STATES = ("combat", "chest", "remains", "event", "paused")
Item = tuple[set[str] | None, dict[str, str]]


def canonical(controller:GameController) -> dict[str, str]:
    return {name.casefold(): name for name in views.known_players(controller)}


def town_mates(controller:GameController, town:str) -> set[str]:
    found = set()
    for name in views.known_players(controller):
        player = controller.repository.load(name)
        if player is not None and not player.npc and town_key(player) == town:
            found.add(name)
    return found


def place_of(controller:GameController, name:str) -> tuple[str, str]:
    player = controller.repository.load(name)
    if player is None:
        return "", ""
    if controller.session.in_run(name):
        return "run", ""
    return town_key(player), controller.town.where(player)


def place_mates(controller:GameController, name:str) -> set[str]:
    place = place_of(controller, name)
    if place[0] == "run":
        return {member.name for member in controller.session.party}
    found = {name}
    for other in views.known_players(controller):
        player = controller.repository.load(other)
        if (player is not None and not player.npc
                and place_of(controller, other) == place):
            found.add(other)
    return found


def witnesses(controller:GameController, actor:str,
              message:Message) -> Item | None:
    town, where = place_of(controller, actor)
    player = controller.repository.load(actor)
    if (not message.witness or not actor or town == "run"
            or where in PRIVATE_WHERE or player is None
            or player.profile.get("home_host")
            or player.profile.get("home_session")):
        return None
    seen = place_mates(controller, actor) - {actor}
    if not seen:
        return None
    text = message.witness.replace("{actor}", actor)
    return seen, {"text": text, "kind": "witness", "place": where}


def audience_of(controller:GameController, actor:str,
                message:Message) -> set[str] | None:
    if message.recipient:
        return {message.recipient}
    lobbies = controller.lobbies
    bundle = ((lobbies.get(message.lobby) if message.lobby else None)
              or (lobbies.of(actor) if actor else lobbies.current()))
    session = bundle.session if bundle is not None else None
    party = ({member.name for member in session.party}
             if session is not None else set())
    if session is not None and session.state in RUN_STATES:
        return party | ({actor} if actor else set())
    player = controller.repository.load(actor) if actor else None
    town = (town_key(player) if player is not None
            else session.lobby_town if (
                session is not None and session.state == "lobby") else "")
    if not town:
        return None
    return party | town_mates(controller, town) | ({actor} if actor else set())


def scoped(controller:GameController, actor:str,
           messages:list[Message]) -> list[Item]:
    names = canonical(controller)
    items: list[Item] = []
    for message in messages:
        seen = witnesses(controller, message.recipient, message)
        if seen is not None:
            items.append((
                {names.get(name.casefold(), name) for name in seen[0]},
                seen[1]))
        found = audience_of(controller, actor, message)
        if found is not None:
            found = {names.get(name.casefold(), name) for name in found}
        items += [(found, entry) for entry in views.log_entries([message])]
    return items


def private(name:str, entries:list[dict[str, str]]) -> list[Item]:
    return [({name}, entry) for entry in entries]
