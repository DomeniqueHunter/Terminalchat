import random

from ..models import Message, Player
from .chat_content import (
    GENDER_FAREWELLS, GENDER_GREETINGS, GENDER_QUOTES, GENDER_TOPICS,
)

TOPICS = ("work", "town", "self")
TIERS = ((8, "friend"), (3, "acquaintance"), (0, "stranger"))
GREETINGS = {
    "stranger": "{npc} looks you over. 'New face. What do you want?'",
    "acquaintance": "{npc} nods. 'Ah, {name}. Back again.'",
    "friend": "{npc} smiles properly for once. '{name}! Sit, sit.'",
}
FAREWELLS = {
    "friend": "{npc} lingers a moment. 'Come by anytime. I mean it.'",
}


def friendship(npc:Player, player:Player) -> int:
    return npc.profile.get("friends", {}).get(player.id, 0)


def tier_of(points:int) -> str:
    return next(name for limit, name in TIERS if points >= limit)


def split_topic(words:list[str]) -> tuple[str, str]:
    if words and words[-1].casefold() in TOPICS:
        return " ".join(words[:-1]), words[-1].casefold()
    return " ".join(words), ""


def chat(player:Player, npc:Player, topic:str,
         rng:random.Random, pool:tuple[str, ...]=()) -> list[Message]:
    topics = dict(npc.profile.get("topics", {}))
    topics.update(GENDER_TOPICS.get(npc.npc, {}).get(player.gender, {}))
    topic = topic or rng.choice([name for name in TOPICS if name in topics]
                                or ["quote"])
    lines = list(pool) or topics.get(topic) or npc.profile.get("quotes") or [""]
    before = tier_of(friendship(npc, player))
    friends = npc.profile.setdefault("friends", {})
    friends[player.id] = friends.get(player.id, 0) + 1
    after = tier_of(friends[player.id])
    values = {"npc": npc.first_name, "name": player.name}
    greetings = GENDER_GREETINGS.get(npc.npc, {}).get(
        player.gender, GREETINGS)
    farewell = GENDER_FAREWELLS.get(npc.npc, {}).get(player.gender)
    text = [greetings[before].format(**values), rng.choice(lines)]
    if after != before:
        text.append(f"({npc.first_name} now counts you as: {after}.)")
    elif after in FAREWELLS:
        text.append((farewell or FAREWELLS[after]).format(**values))
    return [Message("\n".join(text), player.name)]
