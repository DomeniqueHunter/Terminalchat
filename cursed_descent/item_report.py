from .config import EQUIPMENT_SLOTS, SLOT_LABELS, SMELL_WORDS
from .content import ITEMS
from .items import Item
from .locations.north_pole.location import gift_description
from .locations.shop.location import (
    base_price, item_description, sell_price,
)
from .models import Player


def find_owned(player:Player, reference:str) -> tuple[str, str] | None:
    reference = reference.strip().casefold()
    if not reference:
        return None
    if reference.isdigit():
        index = int(reference) - 1
        if 0 <= index < len(player.inventory):
            return player.inventory[index], f"in your bag (nr {reference})"
        return None
    for slot in EQUIPMENT_SLOTS:
        worn = player.equipment.get(slot)
        if worn and reference in (slot, str(worn),
                                  ITEMS[worn]["name"].casefold()):
            return worn, f"worn ({SLOT_LABELS[slot]})"
    for index, item_id in enumerate(player.inventory, 1):
        if reference in (str(item_id), ITEMS[item_id]["name"].casefold()):
            return item_id, f"in your bag (nr {index})"
    return None


def trace_lines(item:str) -> list[str]:
    if not isinstance(item, Item):
        return []
    lines: list[str] = []
    for trace in sorted(item.traces.values(),
                        key=lambda entry: -entry["strength"]):
        word = next((word for limit, word in SMELL_WORDS
                     if trace["strength"] >= limit), "")
        if word:
            lines.append(f"  {word} {trace['name']}")
    if item.soak:
        lines.append(f"  soaked with sweat (level {item.soak})")
    return lines


def origin_lines(player:Player, item:str, repository) -> list[str]:
    if not isinstance(item, Item) or not item.iid:
        return []
    record = repository.items.get(item.iid) if repository else None
    creator = (record or {}).get("creator") or item.creator or "shop"
    lines = [f"  Made by {creator}"]
    if record and record["owner"] != player.id:
        owner = repository.load_by_id(record["owner"])
        if owner is not None:
            lines[0] += f" | belonged to {owner.name}"
    if item.restriction != "both":
        lines.append(f"  Made for {item.restriction}s only")
    return lines


def item_report(player:Player, reference:str,
                repository=None) -> list[str]:
    found = find_owned(player, reference)
    if found is None:
        return ["No such item. [item <nr|slot|name>] looks at something in "
                "your bag or on your body."]
    item, place = found
    data = ITEMS[item]
    lines = [f"🔎 {gift_description(item) or item_description(item)}",
             f"  Slot: {SLOT_LABELS.get(data['slot'], data['slot'])} | "
             f"{place}",
             f"  Worth {base_price(item)} gold, sells for "
             f"{sell_price(item)} gold"]
    if data.get("made_from"):
        lines.append(f"  Made from {data['made_from']}.")
    lines += origin_lines(player, item, repository)
    traces = trace_lines(item)
    if traces:
        lines.append("  Traces on it:")
        lines += traces
    return lines
