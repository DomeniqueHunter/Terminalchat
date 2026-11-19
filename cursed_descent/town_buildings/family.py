from ..models import Message, Player


FAMILY_ROLES = ("mother", "father", "son", "daughter", "sister", "brother",
                "partner")
SIT_LINES = {
    "son": ("'Mom knows best, sweetheart.' {rider} settles onto {seat}'s "
            "face like she did when he was small enough to carry.",
            "'Mom was here first.' {rider} sits down on her own son "
            "{seat} and tells him to behave."),
    "daughter": ("'Come now, darling.' {rider} sits on her daughter "
                 "{seat} as if it were the most natural thing."),
    "brother": ("'Little brother, big favour.' {rider} lowers herself onto "
                "{seat}'s face."),
    "sister": ("'Sisters share, right?' {rider} sits on {seat} with a "
               "grin."),
    "partner": ("'My seat, my rules.' {rider} sits on {seat} like she "
                "owns the stool – and she does."),
    "mother": ("{rider} sits on her own mother's seat and pretends not to "
               "hear the muffled scolding."),
    "father": ("{rider} sits on her father's face and the whole café "
               "politely looks away."),
}
USAGE = (f"[family <name> {'|'.join(FAMILY_ROLES)}] – asks the named "
         f"character to be YOUR mother/father/…; they must confirm with "
         f"[family accept <name>] (or [family decline <name>]) and get the "
         f"matching role back. [family clear <name>] removes a link. "
         f"Also in the Family tab.")


def inverse(role:str, gender:str) -> str:
    if role in ("mother", "father"):
        return "son" if gender == "Male" else "daughter"
    if role in ("son", "daughter"):
        return "father" if gender == "Male" else "mother"
    if role in ("sister", "brother"):
        return "brother" if gender == "Male" else "sister"
    return "partner"


def relations(player:Player) -> dict[str, dict[str, str]]:
    return player.profile.setdefault("family", {})


def upgrade(player:Player, repository) -> None:
    family = relations(player)
    for key, value in list(family.items()):
        if isinstance(value, dict):
            continue
        del family[key]
        other = repository.load(key)
        if other is not None:
            family[other.id] = {"role": value, "name": other.name}


def entries(player:Player, repository=None) -> list[tuple[str, str, str]]:
    result = []
    for char_id, entry in relations(player).items():
        if not isinstance(entry, dict):
            continue
        other = repository.load_by_id(char_id) if repository else None
        if other is not None:
            entry["name"] = other.name
        result.append((char_id, entry.get("name", "?"), entry["role"]))
    return result


def role_of(player:Player, name:str) -> str:
    wanted = name.casefold()
    for _, other, role in entries(player):
        if other.casefold() == wanted:
            return role
    return ""


def link(first:Player, second:Player, role:str) -> None:
    relations(first)[second.id] = {"role": role, "name": second.name}
    relations(second)[first.id] = {"role": inverse(role, first.gender),
                                   "name": first.name}


def unlink(first:Player, second:Player) -> bool:
    removed = relations(first).pop(second.id, None)
    relations(second).pop(first.id, None)
    return removed is not None


def note(player:Player, name:str) -> str:
    role = role_of(player, name)
    return f"{name} is your {role}." if role else ""


def asks_of(player:Player) -> dict[str, dict[str, str]]:
    return player.profile.setdefault("family_asks", {})


def pending(player:Player) -> list[tuple[str, str, str]]:
    return [(char_id, entry["name"], entry["role"])
            for char_id, entry in asks_of(player).items()]


def find(repository, name:str) -> Player | None:
    return next((repository.load(known) for known in repository.names()
                 if known.casefold() == name.casefold()), None)


def answer(player:Player, name:str, accept:bool,
           repository) -> list[Message]:
    asker = find(repository, name)
    entry = None if asker is None else asks_of(player).pop(asker.id, None)
    if asker is None or entry is None:
        return [Message(f"Nobody called '{name}' has asked you. {USAGE}",
                        player.name)]
    if not accept:
        repository.save(player)
        return [Message(f"You decline {asker.name}'s family request.",
                        player.name),
                Message(f"{player.name} declined to be your {entry['role']}.",
                        asker.name)]
    upgrade(asker, repository)
    link(asker, player, entry["role"])
    repository.save(asker)
    repository.save(player)
    back = relations(player)[asker.id]["role"]
    return [Message(f"You are now {asker.name}'s {entry['role']} – and "
                    f"{asker.name} is your {back}.", player.name),
            Message(f"{player.name} accepted: {player.name} is now your "
                    f"{entry['role']}.", asker.name)]


def family_command(player:Player, args:list[str],
                   repository) -> list[Message]:
    upgrade(player, repository)
    if not args:
        known = entries(player, repository)
        lines = [f"  {name}: your {role}" for _, name, role in known]
        lines += [f"  {name} asks to be your {role} – [family accept "
                  f"{name}] / [family decline {name}]"
                  for _, name, role in pending(player)]
        if not lines:
            return [Message(f"No family marked yet. {USAGE}", player.name)]
        return [Message("Your family:\n" + "\n".join(lines), player.name)]
    word = args[0].casefold()
    if word in ("accept", "decline"):
        return answer(player, " ".join(args[1:]), word == "accept",
                      repository)
    clearing = word == "clear"
    words = args[1:] if clearing else args[:-1]
    role = "" if clearing else args[-1].casefold()
    name = " ".join(words)
    other = find(repository, name)
    if other is None or other.id == player.id:
        return [Message(f"No such other character. {USAGE}", player.name)]
    upgrade(other, repository)
    if clearing:
        text = ("Family link removed." if unlink(player, other)
                else f"{other.name} is not marked as family.")
        repository.save(other)
        return [Message(text, player.name)]
    if role not in FAMILY_ROLES:
        return [Message(f"Roles: {', '.join(FAMILY_ROLES)}. {USAGE}",
                        player.name)]
    if other.npc:
        link(player, other, role)
        repository.save(other)
        back = relations(other)[player.id]["role"]
        return [Message(f"{other.name} is now your {role} – and you are "
                        f"{other.name}'s {back}.", player.name)]
    asks_of(other)[player.id] = {"role": role, "name": player.name}
    repository.save(other)
    return [Message(f"You ask {other.name} to be your {role}. They have to "
                    f"confirm.", player.name),
            Message(f"{player.name} asks you to be their {role}. Accept: "
                    f"[family accept {player.name}] – or [family decline "
                    f"{player.name}].", other.name)]
