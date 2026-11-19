from .models import Message, Player


USAGE = ("[friend <name>] asks a player to be your friend; they confirm "
         "with [friend accept <name>] or [friend decline <name>]. "
         "[friend remove <name>] ends it. Also in the Address book tab.")


def book(player:Player) -> dict[str, dict[str, str]]:
    return player.profile.setdefault("friends", {})


def asks(player:Player) -> dict[str, dict[str, str]]:
    return player.profile.setdefault("friend_asks", {})


def find(repository, name:str) -> Player | None:
    return next((repository.load(known) for known in repository.names()
                 if known.casefold() == name.casefold()), None)


def friend_names(player:Player, repository) -> list[str]:
    names = []
    for char_id, entry in book(player).items():
        other = repository.load_by_id(char_id)
        names.append(other.name if other is not None else entry["name"])
    return sorted(names, key=str.casefold)


def pending_names(player:Player) -> list[str]:
    return sorted((entry["name"] for entry in asks(player).values()),
                  key=str.casefold)


def make_friends(first:Player, second:Player) -> None:
    book(first)[second.id] = {"name": second.name}
    book(second)[first.id] = {"name": first.name}


def unfriend(first:Player, second:Player) -> bool:
    removed = book(first).pop(second.id, None)
    book(second).pop(first.id, None)
    return removed is not None


def friend_command(player:Player, args:list[str],
                   repository) -> list[Message]:
    if not args:
        names = friend_names(player, repository)
        lines = [f"  {name}" for name in names]
        lines += [f"  {name} asks to be your friend – [friend accept "
                  f"{name}] / [friend decline {name}]"
                  for name in pending_names(player)]
        if not lines:
            return [Message(f"No friends yet. {USAGE}", player.name)]
        return [Message("Your friends:\n" + "\n".join(lines), player.name)]
    word = args[0].casefold()
    sub = word in ("accept", "decline", "remove")
    other = find(repository, " ".join(args[1:] if sub else args))
    if other is None or other.id == player.id or other.npc:
        return [Message(f"No such other player. {USAGE}", player.name)]
    if word == "remove":
        gone = unfriend(player, other)
        repository.save(other)
        return [Message("Friend removed." if gone
                        else f"{other.name} is not your friend.",
                        player.name)]
    if word in ("accept", "decline"):
        entry = asks(player).pop(other.id, None)
        if entry is None:
            return [Message(f"{other.name} has not asked you.", player.name)]
        if word == "decline":
            return [Message(f"You decline {other.name}.", player.name),
                    Message(f"{player.name} declined your friend request.",
                            other.name)]
        make_friends(player, other)
        repository.save(other)
        return [Message(f"You and {other.name} are friends now.",
                        player.name),
                Message(f"{player.name} accepted: you are friends now.",
                        other.name)]
    if other.id in book(player):
        return [Message(f"{other.name} is already your friend.",
                        player.name)]
    asks(other)[player.id] = {"name": player.name}
    repository.save(other)
    return [Message(f"You ask {other.name} to be your friend.", player.name),
            Message(f"{player.name} asks to be your friend. Accept: "
                    f"[friend accept {player.name}] – or [friend decline "
                    f"{player.name}].", other.name)]
