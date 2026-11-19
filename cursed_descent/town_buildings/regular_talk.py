import random
from typing import Any


TALK_LINES = {
    "cafe": (
        "{name} pours you a cup and asks how the stool has been treating "
        "you.",
        "{name} laughs: 'You are the only one who sits still, dear.'",
        "{name} tells a long story about her neighbours and pats your "
        "shoulder twice.",
        "{name} says the afternoons are quiet without a lap to rest on.",
    ),
    "brothel": (
        "{name} grins and asks whether the house still lets you keep your "
        "tips.",
        "{name} complains about the week, then admits you are the highlight "
        "of it.",
        "{name} lowers their voice and swaps a rumour from the street.",
        "{name} says the stairs seem shorter when you are waiting at the "
        "top.",
    ),
}
MARRIED_LINE = "{name} mentions {spouse} with a careful smile."


def regular_talk(record:dict[str, Any], building:str,
                 rng:random.Random) -> str:
    lines = [rng.choice(TALK_LINES[building]).format(name=record["name"])]
    if record.get("married") and record.get("spouse"):
        lines.append(MARRIED_LINE.format(name=record["name"],
                                         spouse=record["spouse"]))
    return " ".join(lines)
