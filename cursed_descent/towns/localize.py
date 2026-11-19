import re
from dataclasses import replace

from . import START_TOWN, TOWNS, Town, town_key
from ..models import Message
from ..settings import REGISTRY, fill


PATTERNS = (
    ("tavern", r"(?:[Tt]he )?Gilded Tankard", "title"),
    ("tavern", r"{hilda_first} {hilda_last}", "full"),
    ("tavern", r"\b{hilda_first}\b", "name"),
    ("brothel", r"Madame {rose_first}", "madame"),
    ("brothel", r"(?:[Tt]he )?Rose Chamber", "title"),
    ("brothel", r"{rose_first} {rose_last}", "full"),
    ("brothel", r"\b{rose_first}\b", "name"),
    ("shop", r"\b{velvet_first}\b(?! Evening)", "name"),
    ("smith", r"{morgrin_first} the Ashen Smith", "full"),
    ("smith", r"\b{morgrin_first}\b", "name"),
    ("clinic", r"(?:Dr\. {vane_first}'s )?Flesh Atelier", "title"),
    ("clinic", r"Dr\. {vane_first}\b", "name"),
    ("clinic", r"\b{vane_first}\b", "name"),
    ("bank", r"\b{orla_first}\b", "name"),
)
TITLES = ("Madame", "Mistress", "Lady", "Dame")
MALE_FIXES = ((r"\bher\b", "his"), (r"\bshe\b", "he"), (r"\bShe\b", "He"))
CACHE: dict[tuple, re.Pattern] = {}


def alternation() -> re.Pattern:
    names = {key: re.escape(value)
             for key, value in REGISTRY.get("npc", {}).items()}
    snapshot = tuple(sorted(names.items()))
    if snapshot not in CACHE:
        CACHE.clear()
        CACHE[snapshot] = re.compile("|".join(
            f"(?P<g{index}>{pattern.format(**names)})"
            for index, (_, pattern, _) in enumerate(PATTERNS)))
    return CACHE[snapshot]


def operator_of(town:Town, building:str):
    for resident in town.residents:
        if resident.building == building:
            return resident
    return None


def venue_title(town:Town, building:str, matched:str) -> str:
    from ..town_buildings import registry
    found = registry.get(building, town.key)
    if found is None or not found.renamed:
        return matched
    title = found.title
    if not matched.lower().startswith("the "):
        return title
    article = "The" if matched[:1] == "T" else "the"
    if title.startswith("The "):
        return f"{article} {title[4:]}"
    return f"{article} {title}"


def replacement(town:Town, building:str, kind:str, matched:str) -> str:
    resident = operator_of(town, building)
    if kind == "title":
        return venue_title(town, building, matched)
    if resident is None:
        return matched
    if kind == "madame":
        if resident.first_name.split()[0] in TITLES:
            return resident.first_name
        return f"Madame {resident.first_name}"
    if kind == "full":
        return f"{resident.first_name} {resident.last_name}"
    return resident.first_name


def localize_text(text:str, town:Town) -> str:
    text = fill(text)
    if town.key == START_TOWN:
        return text

    def swap(found:re.Match) -> str:
        index = int(found.lastgroup[1:])
        building, _, kind = PATTERNS[index]
        return replacement(town, building, kind, found.group(0))

    changed = alternation().sub(swap, text)
    clinic = operator_of(town, "clinic")
    if changed != text and clinic is not None and clinic.gender == "Male":
        for pattern, word in MALE_FIXES:
            if clinic.first_name in changed:
                changed = re.sub(pattern, word, changed)
    return changed


def localize(messages:list[Message], repository) -> list[Message]:
    towns: dict[str, Town] = {}
    result = []
    for message in messages:
        if message.recipient not in towns:
            player = repository.load(message.recipient)
            towns[message.recipient] = (
                TOWNS[town_key(player)] if player else TOWNS[START_TOWN])
        town = towns[message.recipient]
        if town.key == START_TOWN:
            result.append(message)
        else:
            result.append(replace(message,
                                  text=localize_text(message.text, town)))
    return result
