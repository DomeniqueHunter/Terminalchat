import random

from .models import Message, Player
from .locations.common import pronouns
from .town_buildings.chat import TOPICS, chat, tier_of
from .town_buildings.family import relations


BANTER = {
    "work": (
        "{a}: 'Watch my back on the next stage, {b}.' {b}: 'Always. "
        "Just don't count the loot before we win.'",
        "{a} wipes {their} brow. 'How much longer can we keep this up, "
        "{b}?' {b} shrugs. 'Until the dungeon runs out of floors.'",
        "{a}: 'Split the potions fair this time, {b}.' {b}: 'I always "
        "split fair. You just drink faster.'",
    ),
    "town": (
        "{a}: 'When this run is over I'm buying a very big drink, {b}.' "
        "{b}: 'You'll need it. And I'll watch.'",
        "{a} leans against the wall. 'Remember the taproom, {b}?' {b} "
        "grins. 'The one where <<npc.astrid_first>> looked at us like stew?'",
        "{a}: 'Anyone ever tell you the Café stools are watching us, "
        "{b}?' {b}: 'Only you. Every night.'",
    ),
    "self": (
        "{a}: 'Be honest, {b}. Do I look different since the clinic?' "
        "{b} squints. 'Different. Not bad. Different.'",
        "{a}: 'Sometimes I wonder if we'll ever get out of here, {b}.' "
        "{b} bumps {their} shoulder. 'Not on my watch.'",
        "{a}: 'You're the only one here I'd trust with my boots, {b}.' "
        "{b}: 'Flattery. Keep going.'",
    ),
}


FAMILY_BANTER = {
    "mother": ("{a}: 'Mother, mind your step.' {b}: 'Sweetheart, I "
               "was fighting before you were born.'",
               "{b} fixes {a}'s collar. 'Eat something, dear. You look "
               "pale.'"),
    "father": ("{a}: 'Father, don't overdo it.' {b}: 'Son, I carried "
               "you through worse.'",
               "{b} claps {a} on the shoulder. 'Proud of you. Now move.'"),
    "son": ("{a}: 'Stay close, son.' {b}: 'Mom, I'm not a child "
            "anymore.' {a}: 'You'll always be my little one.'",
            "{b} grumbles as {a} wipes a smudge from {their} cheek."),
    "daughter": ("{a}: 'Stay close, sweetheart.' {b}: 'Mom, I can "
                 "fight!' {a}: 'And you'll still eat your carrots.'",
                 "{b} rolls {their} eyes as {a} fusses with the strap "
                 "of her boots."),
    "sister": ("{a}: 'Sis, you took my last potion again.' {b}: 'It was "
               "mine first.'",
               "{a} and {b} bicker like they did as kids, and then "
               "share the last biscuit."),
    "brother": ("{a}: 'Bro, watch the left side.' {b}: 'I've got it, "
                "I've got it.'",
                "{a} and {b} trade insults, and then fist-bump."),
    "partner": ("{a} brushes {b}'s hand. 'Stay alive. I mean it.' {b}: "
                "'For you, anything.'",
                "{a} and {b} share a quiet look that says more than "
                "any speech."),
}


BOND_TEXT = "({a} and {b} are now: {tier}.)"


def bonds(player:Player) -> dict[str, int]:
    return player.profile.setdefault("party_friends", {})


def banter(player:Player, other:Player, topic:str,
           rng:random.Random) -> list[Message]:
    if other.npc:
        return chat(player, other, topic, rng)
    values = {"a": player.name, "b": other.name,
              "their": pronouns(player.gender)[2]}
    family = relations(player).get(other.id)
    if family and not topic and rng.random() < 0.7:
        line = rng.choice(FAMILY_BANTER.get(family["role"], BANTER["self"]))
    else:
        topic = topic if topic in TOPICS else rng.choice(TOPICS)
        line = rng.choice(BANTER[topic])
    before = tier_of(bonds(player).get(other.id, 0))
    bonds(player)[other.id] = bonds(player).get(other.id, 0) + 1
    after = tier_of(bonds(player)[other.id])
    text = [f"💬 {line.format(**values)}"]
    if after != before:
        text.append(BOND_TEXT.format(tier=after, **values))
    return [Message("\n".join(text))]


def party_chat(player:Player, args:list[str], members:list[Player],
               rng:random.Random) -> list[Message]:
    topic = args[-1].casefold() if args and args[-1].casefold() in TOPICS \
        else ""
    name = " ".join(args[:-1] if topic else args).casefold()
    if not name:
        return [Message("Talk to whom? [banter <name> [work|town|self]]",
                        player.name)]
    for member in members:
        if member is not player and member.name.casefold() == name:
            return banter(player, member, topic, rng)
    return [Message(f"Nobody called '{name}' is in your party.",
                    player.name)]
