import random
from typing import Any

from ..config import VISIT_ASK_VISITS
from ..towns.last_light_humans.cafe.stools import NAMES
from .regular_body import body_line, smell_note


STREETS = ("Rosewater Lane", "Tanner's Row", "Candle Street", "Mill Hill",
           "Old Wharf", "Lanternway", "Cobbler's Court", "Elm Terrace")
VISIT_TEXTS = {
    "cafe": (
        "{name}'s house smells of tea and lavender. She leads you to her "
        "drawing room, settles into her armchair – and onto you, with "
        "everything she has. 'No Bertha watching today, dear.'",
        "{name} opens the door in her house dress, takes your hand and "
        "walks you to the parlour rug. 'Let us see how well you hold "
        "when nobody counts.'",
    ),
    "brothel": (
        "{name} opens the door at {street}, already smiling. The curtains "
        "are drawn, the kettle is on – and the evening is yours alone.",
        "{name} lets you in and locks the door twice. 'Here nobody knows "
        "us. Take your time.'",
    ),
}
SPOUSE_AWAY = "{spouse} is away on business, so nothing disturbs you."
SPOUSE_HOME = ("The door downstairs bangs – {spouse} is home early! You "
               "hide in the pantry for an hour, sweating, and slip out "
               "with your dignity half intact.")


def new_home(rng:random.Random, age:int) -> dict[str, Any]:
    married = rng.random() < (0.45 if age >= 28 else 0.1)
    return {"married": married,
            "spouse": rng.choice(NAMES) if married else "",
            "home": f"No. {rng.randint(2, 60)} {rng.choice(STREETS)}",
            "address_known": False}


def status_line(record:dict[str, Any]) -> str:
    married = ("married to " + record["spouse"]
               if record.get("married") and record.get("spouse")
               else "married" if record.get("married") else "single")
    address = (f"address known ({record['home']})"
               if record.get("address_known") and record.get("home")
               else "address unknown")
    body = body_line(record)
    prefix = f"{body}. " if body else ""
    return f"{prefix}{married[0].upper()}{married[1:]}, {address}."


def ask_address(record:dict[str, Any]) -> bool:
    return record.get("visits", 1) >= VISIT_ASK_VISITS


def visit_scene(record:dict[str, Any], building:str,
                rng:random.Random) -> tuple[str, int]:
    lines = [rng.choice(VISIT_TEXTS[building]).format(
        name=record["name"], street=record["home"])]
    if record.get("married") and record.get("spouse"):
        if rng.random() < 0.25:
            lines.append(SPOUSE_HOME.format(spouse=record["spouse"]))
        else:
            lines.append(SPOUSE_AWAY.format(spouse=record["spouse"]))
    note = smell_note(record["name"], record.get("sweat", 0),
                      record.get("musk", 0))
    if note:
        lines.append(note)
    return "\n".join(lines), 0


INVITE_TEXTS = (
    "{name} arrives at your door with her hat in one hand and an "
    "appetite in the other. 'Your house, your rules, dear – until I sit.'",
    "{name} lets herself in, hangs her coat over your chair and looks "
    "around your place with a critical eye. 'Cosy. Now, the seat.'",
)


def invite_scene(record:dict[str, Any],
                 rng:random.Random) -> tuple[str, int]:
    lines = [rng.choice(INVITE_TEXTS).format(name=record["name"])]
    note = smell_note(record["name"], record.get("sweat", 0),
                      record.get("musk", 0))
    if note:
        lines.append(note)
    return "\n".join(lines), 0


CALL_TEXTS = {
    "cafe": (
        "{name} knocks at your door with a basket of cake. 'I was in the "
        "neighbourhood, dear, and thought of my favourite seat.' She "
        "stays for a cup of tea and a long look.",
        "A note from {name} arrives with flowers: 'Next time I will sit "
        "twice as long.' You smile all day.",
    ),
    "brothel": (
        "{name} waits outside your door with a bottle of wine and a "
        "crooked smile. 'Could not stay away.' You spend a warm hour "
        "together.",
        "{name} sends a boy with a letter: 'Thinking of you. Same time next "
        "week?'",
    ),
}


def call_scene(record:dict[str, Any], building:str,
               rng:random.Random) -> tuple[str, int]:
    text = rng.choice(CALL_TEXTS[building]).format(name=record["name"])
    if record.get("married") and record.get("spouse"):
        text += f" ({record['spouse']} thinks they are at the market.)"
    return text, 0
