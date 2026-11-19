import random
from typing import Any

from .config import INTIMACY_BOND, INTIMACY_MIN_AGE
from .house_regulars import is_regular
from .models import Message, Player
from .needs import satisfy
from .npc_menu import bump


ACTIVITIES = {
    "flirt": ((
        "{a} leans against the doorframe and lets the silence do the "
        "talking. {b} laughs first, and the evening gets warmer.",
        "{b} says something a little too bold. {a} answers in kind, and "
        "neither looks away.",
    ), 1, 5),
    "kiss": ((
        "{a} pulls {b} in by the collar and kisses {b} slowly, "
        "unhurried, until the kettle on the stove starts to scream.",
        "A soft, searching kiss in the lamplight. {b} sighs against "
        "{a}'s mouth and does not want it to stop.",
    ), 2, 15),
    "cuddle": ((
        "They share the couch under one blanket, {b}'s head on {a}'s "
        "shoulder, and the whole world shrinks to the sound of "
        "breathing.",
        "{a} wraps both arms around {b}. For a long while nobody says "
        "anything, and nobody needs to.",
    ), 2, 10),
    "massage": ((
        "{a} warms oil between {a}'s palms and works the knots out of "
        "{b}'s shoulders until {b} groans into the cushions.",
        "{b} lies face down on the rug while {a} presses slow circles "
        "into every tired muscle. 'Do not stop,' {b} mumbles.",
    ), 2, 20),
    "bath": ((
        "The tub is barely big enough for two. {a} and {b} spend an hour "
        "in the steam, soaping each other's backs and trading secrets.",
        "Hot water, lavender oil, and {b}'s feet in {a}'s lap. The "
        "bathwater is cold by the time they get out, and nobody minds.",
    ), 3, 25),
    "dance": ((
        "{a} hums a tune and {b} takes the lead. They turn slowly across "
        "the small floor, laughing every time they step on each "
        "other's toes.",
        "No music, only the creak of the boards. {a} and {b} dance "
        "anyway, cheek to cheek, until the candle burns low.",
    ), 1, 10),
}
MORE_TEXTS = {
    "flirt": (
        "{a} refills {b}'s glass without being asked and lets {a}'s "
        "fingers linger on the rim. 'Tell me something you have never "
        "told anyone,' {a} says, and {b} leans close enough to answer "
        "in a whisper. By the time the candle needs trimming, neither of "
        "them has noticed the hour.",
        "A look held a second too long, a hand that finds a knee under "
        "the table. {b} pretends to study the wine while {a} describes, "
        "very seriously, everything {a} would do with a free evening. "
        "{b} laughs, blushes, and does not say no.",
    ),
    "kiss": (
        "{a} cups {b}'s face in both hands. The first kiss is almost "
        "shy, the second is not, and somewhere in the third {b}'s "
        "fingers curl into {a}'s hair. When they finally part, their "
        "foreheads stay pressed together and neither wants to be the "
        "first to speak.",
        "{b} backs {a} slowly against the wall and kisses {a} like a "
        "question that only has one answer. The house is quiet around "
        "them, the stove ticks as it cools, and the world outside the "
        "door might as well not exist.",
    ),
    "cuddle": (
        "The fire has burned down to embers and neither of them has "
        "moved. {a}'s arm is asleep under {b}'s weight, and {a} would "
        "not trade it for anything. 'Stay,' {a} murmurs into {b}'s "
        "hair, and {b} answers by pulling the blanket higher.",
        "They fit together on the narrow couch as if it had been built "
        "for it. {b} traces idle patterns on {a}'s wrist while {a} "
        "tells a long, rambling story that no one is really listening "
        "to. Warmth, lamplight, and slow breathing do the rest.",
    ),
    "massage": (
        "{a} starts at {b}'s neck, thumbs working in slow circles, and "
        "follows the long line of the spine down until {b} stops "
        "pretending to hold a conversation. The oil smells of cedar. "
        "Somewhere between the shoulder blades {b} gives a groan that "
        "{a} files away to bring up again later.",
        "'Lie down,' {a} says, and for once {b} does not argue. Every "
        "knot yields in its own time: the shoulders first, then the "
        "lower back, then the calves, until {b} is a warm, boneless "
        "weight on the rug and {a}'s hands are slick and tired.",
    ),
    "bath": (
        "{a} pours the last kettle into the tub and tests it with an "
        "elbow. {b} sinks in with a long sigh, and {a} climbs in behind, "
        "knees on either side. A sponge, a bar of lavender soap, and "
        "slow, careful hands – the water goes cold long before either "
        "of them thinks about getting out.",
        "Steam fogs the small window. {b} washes {a}'s hair, gently "
        "tipping {a}'s head back to rinse it, and the quiet between "
        "them is the comfortable kind. Later, wrapped in one towel, "
        "they carry each other's warmth back to the bedroom.",
    ),
    "dance": (
        "{b} finds an old record player and, to {a}'s surprise, makes "
        "it work. The first song is slow. {a}'s hand settles at {b}'s "
        "waist, and they turn together between the table and the stove "
        "until the music crackles out and they keep going without it.",
        "'I do not dance,' {a} says, and then does, badly, then better "
        "as {b} counts the steps under {b}'s breath. By the third song "
        "{a} has stopped counting and {b} has stopped correcting, and "
        "the floorboards are the only witnesses.",
    ),
}
ACTIVITIES = {key: (texts + MORE_TEXTS[key], points, relief)
              for key, (texts, points, relief) in ACTIVITIES.items()}
ACTIVITY_WORDS = tuple(ACTIVITIES)


def split_activity(args:list[str]) -> tuple[list[str], str]:
    if len(args) > 1 and args[-1].casefold() in ACTIVITIES:
        return args[:-1], args[-1].casefold()
    return args, ""


def activity(player:Player, other:Player, kind:str, repository:Any,
             rng:random.Random) -> list[Message]:
    if min(player.age, other.age) < INTIMACY_MIN_AGE:
        return [Message(f"{other.name} is not available.", player.name)]
    texts, points, relief = ACTIVITIES[kind]
    line = rng.choice(texts).format(a=player.name, b=other.name)
    lines = [line]
    satisfy(player.needs, {"arousal": -relief})
    if other.npc and not is_regular(other):
        note = bump(other, player, max(1, points * INTIMACY_BOND // 2))
        if note:
            lines.append(note.strip())
    repository.save(player)
    if other.npc and not is_regular(other):
        repository.save(other)
    return [Message("\n".join(lines))]
