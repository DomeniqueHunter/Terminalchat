import random
import uuid
from pathlib import Path
from typing import Any

from ...body import apply_body_mods, fake_amount
from ...config import HUNG_GENDERS
from ...models import Player
from ...storage import read_json, write_json
from .config import (
    BOTTLE_PREFIX, FILE_NAME, MIN_BUTT, MIN_ENDOWMENT, MIN_GIRTH, PARTS,
    PRICES,
)
from .content import EVENT_TEXTS


def labels() -> dict[str, str]:
    return {key.removeprefix("label_"): text
            for key, text in EVENT_TEXTS["drainer"].items()
            if key.startswith("label_")}


def label_of(part:str, gender:str) -> str:
    names = labels()
    if part == "bust":
        return names["boy_chest" if gender == "Female" else "flat_tire"]
    return names[{"butt": "flat_ass", "penis": "fail_male",
                  "balls": "silicone"}[part]]


def has_part(player:Player, part:str) -> bool:
    body = player.body
    if part == "bust":
        return body.get("bust", 0) > 0
    if part == "butt":
        return body.get("butt", MIN_BUTT) > MIN_BUTT
    if player.gender not in HUNG_GENDERS:
        return False
    if part == "penis":
        return (body.get("endowment", MIN_ENDOWMENT) > MIN_ENDOWMENT
                or body.get("girth", MIN_GIRTH) > MIN_GIRTH)
    return body.get("balls", 0) > fake_amount(body, "balls")


def next_part(player:Player) -> str:
    return next((part for part in PARTS if has_part(player, part)), "")


def drain(player:Player, stage:int) -> dict[str, Any] | None:
    part = next_part(player)
    if not part:
        return None
    body = player.body
    label = label_of(part, player.gender)
    if part == "bust":
        values = {"bust": body["bust"],
                  "fake": body.get("fake", {}).get("bust", 0)}
        mods: dict[str, Any] = {"bust": 0}
    elif part == "butt":
        values = {"butt": body["butt"]}
        mods = {"butt": MIN_BUTT}
    elif part == "penis":
        values = {"endowment": body["endowment"], "girth": body["girth"]}
        mods = {"endowment": MIN_ENDOWMENT, "girth": MIN_GIRTH}
    else:
        values = {"balls": body["balls"]}
        mods = {"fake": {**body.get("fake", {}), "balls": body["balls"]}}
    marks = dict(body.get("drained", {}))
    marks[part] = label
    mods["drained"] = marks
    apply_body_mods(body, mods)
    return {"victim": player.name, "gender": player.gender, "part": part,
            "values": values, "label": label, "stage": stage}


def can_receive(player:Player, bottle:dict[str, Any]) -> bool:
    if bottle["part"] in ("penis", "balls"):
        return player.gender in HUNG_GENDERS
    return True


def restore(player:Player, bottle:dict[str, Any]) -> None:
    body = player.body
    part = bottle["part"]
    values = bottle["values"]
    fake = dict(body.get("fake", {}))
    mods: dict[str, Any] = {}
    if part == "bust":
        mods["bust"] = max(body.get("bust", 0), values["bust"])
        if values.get("fake"):
            fake["bust"] = values["fake"]
    elif part == "butt":
        mods["butt"] = max(body.get("butt", MIN_BUTT), values["butt"])
    elif part == "penis":
        mods["endowment"] = max(body.get("endowment", 0),
                                values["endowment"])
        mods["girth"] = max(body.get("girth", 0), values["girth"])
    else:
        fake.pop("balls", None)
        mods["balls"] = max(body.get("balls", 0), values["balls"])
    mods["fake"] = fake
    marks = {key: text for key, text in body.get("drained", {}).items()
             if key != part}
    mods["drained"] = marks
    apply_body_mods(body, mods)


def thing_text(bottle:dict[str, Any]) -> str:
    return EVENT_TEXTS["drainer"][f"thing_{bottle['part']}"].format(
        victim=bottle["victim"])


def bottle_name(bottle:dict[str, Any]) -> str:
    texts = EVENT_TEXTS["drainer"]
    size = texts[f"size_{bottle['part']}"].format(**bottle["values"])
    return texts["bottle_name"].format(
        victim=bottle["victim"], size=size,
        thing=texts[f"name_{bottle['part']}"])


def item_id_of(bottle:dict[str, Any]) -> str:
    return f"{BOTTLE_PREFIX}{bottle['id']}"


def register_bottle(bottle:dict[str, Any]) -> None:
    from ...content import ITEMS
    ITEMS[item_id_of(bottle)] = {
        "name": bottle_name(bottle), "slot": "consumable",
        "rarity": "epic", "price": PRICES[bottle["part"]],
        "no_loot": True, "bottle": bottle["id"],
        "note": EVENT_TEXTS["drainer"]["bottle_note"].format(
            victim=bottle["victim"])}


class Ledger:
    def __init__(self, data_path:Path) -> None:
        self.path = data_path / FILE_NAME

    def entries(self) -> list[dict[str, Any]]:
        entries = read_json(self.path, [])
        for entry in entries:
            entry.setdefault("id", uuid.uuid4().hex[:8])
            entry.setdefault("held", False)
        return entries

    def save(self, entries:list[dict[str, Any]]) -> None:
        write_json(self.path, entries)

    def bottles(self) -> list[dict[str, Any]]:
        return [entry for entry in self.entries() if not entry["held"]]

    def get(self, bottle_id:str) -> dict[str, Any] | None:
        return next((entry for entry in self.entries()
                     if entry["id"] == bottle_id), None)

    def add(self, bottle:dict[str, Any]) -> None:
        bottle["id"] = uuid.uuid4().hex[:8]
        bottle["held"] = False
        self.save(self.entries() + [bottle])
        register_bottle(bottle)

    def take_random(self) -> dict[str, Any] | None:
        entries = self.entries()
        shelf = [entry for entry in entries if not entry["held"]]
        if not shelf:
            return None
        bottle = random.choice(shelf)
        bottle["held"] = True
        self.save(entries)
        return bottle

    def release(self, bottle_id:str) -> None:
        entries = self.entries()
        for entry in entries:
            if entry["id"] == bottle_id:
                entry["held"] = False
        self.save(entries)

    def remove(self, bottle_id:str) -> None:
        self.save([entry for entry in self.entries()
                   if entry["id"] != bottle_id])

    def register_all(self) -> None:
        for entry in self.entries():
            register_bottle(entry)
