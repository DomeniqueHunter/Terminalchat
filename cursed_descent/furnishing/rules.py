from typing import Any

from ..config import BANK_SLOTS
from ..content import ITEMS
from ..formulas import apply_buff
from ..house_store import current as house_store
from ..items import item_from_json, item_to_json
from ..locations.shop.location import buy_price
from ..models import Message, Player
from .layout import COMFORT_TIERS, KINDS, STARTER, rooms_of, slots_of
from ..plants import PLANTS
from .plants import BLOOM, HUNGRY_AFTER, STAGES, say


def private(text:str, player:Player) -> list[Message]:
    return [Message(text, player.name)]


def name_of(item_id:str) -> str:
    return ITEMS[item_id]["name"]


def starter(house_type:str) -> dict[str, Any]:
    slots = slots_of(house_type)
    placed: dict[str, Any] = {}
    for kind, item_id in STARTER:
        slot = next((key for key, value in slots.items()
                     if value == kind and key not in placed), None)
        if slot:
            placed[slot] = item_id
    return placed


def raw(home:dict[str, Any]) -> dict[str, Any]:
    if "furniture" not in home:
        home["furniture"] = starter(home["type"])
    return home["furniture"]


def furniture_of(home:dict[str, Any]) -> dict[str, str]:
    slots = slots_of(home["type"])
    return {slot: item_from_json(value) for slot, value in raw(home).items()
            if slot in slots}


def plants_of(home:dict[str, Any]) -> dict[str, Any]:
    return home.setdefault("plants", {})


def stage_of(state:dict[str, Any]) -> int:
    need = PLANTS[state["kind"]]["need"]
    return max(number for number, value in enumerate(need)
               if state["growth"] >= value)


def today() -> int:
    return house_store().day()


def neglect_days(state:dict[str, Any]) -> int:
    return today() - state.setdefault("tended", today())


def mood(state:dict[str, Any]) -> str:
    kind = PLANTS[state["kind"]]
    if (state.get("victim") or state.get("pod") or state["wilted"]
            or "neglect" not in kind
            or stage_of(state) < len(STAGES) - 1):
        return ""
    days = neglect_days(state)
    if days >= kind["neglect"]["evil"]:
        return "evil"
    return "warn" if days >= kind["neglect"]["warn"] else ""


def irrigated(home:dict[str, Any]) -> bool:
    return any(ITEMS[item].get("irrigates")
               for item in furniture_of(home).values())


def blooming(home:dict[str, Any]) -> str:
    return next((state["kind"] for state in plants_of(home).values()
                 if not state["wilted"] and stage_of(state) >= BLOOM), "")


def starving(home:dict[str, Any]) -> str:
    return next((state["kind"] for state in plants_of(home).values()
                 if not state["wilted"]
                 and state.get("hungry", 0) >= HUNGRY_AFTER), "")


def comfort_of(home:dict[str, Any]) -> int:
    plants = sum(PLANTS[state["kind"]]["comfort"][stage_of(state)]
                 for state in plants_of(home).values()
                 if not state["wilted"])
    return plants + sum(ITEMS[item].get("comfort", 0)
                        for item in furniture_of(home).values())


def storage_bonus(home:dict[str, Any]) -> int:
    return sum(ITEMS[item].get("storage", 0)
               for item in furniture_of(home).values())


def capacity_of(home:dict[str, Any]) -> int:
    return BANK_SLOTS + storage_bonus(home)


def label(item_id:str) -> str:
    item = ITEMS[item_id]
    parts = []
    if item.get("comfort"):
        parts.append(f"comfort +{item['comfort']}")
    if item.get("storage"):
        parts.append(f"storage +{item['storage']}")
    return f"{item['name']} ({', '.join(parts)})" if parts else item["name"]


def fits(item_id:str, kind:str) -> bool:
    return (ITEMS.get(item_id, {}).get("slot") == "furniture"
            and ITEMS[item_id].get("furniture") == kind)


def candidates(player:Player, kind:str) -> list[tuple[int, str]]:
    return [(number, item) for number, item in
            enumerate(player.inventory, 1) if fits(item, kind)]


def use_of(home:dict[str, Any], slot:str) -> str:
    item = furniture_of(home).get(slot)
    return ITEMS[item].get("use", "") if item else ""


def catalogue() -> list[str]:
    return [key for key, item in ITEMS.items()
            if item.get("slot") == "furniture" and item.get("catalogue")]


def place(player:Player, home:dict[str, Any], slot:str,
          number:int) -> list[Message]:
    slots = slots_of(home["type"])
    if slot not in slots:
        return private("There is no such spot in this house.", player)
    if not 1 <= number <= len(player.inventory):
        return private("You do not carry that.", player)
    item = player.inventory[number - 1]
    if not fits(item, slots[slot]):
        return private(f"That does not fit a {KINDS[slots[slot]][0]} "
                       f"spot.", player)
    placed = raw(home)
    old = placed.get(slot)
    player.inventory.pop(number - 1)
    placed[slot] = item_to_json(item)
    lines = [f"You set the {name_of(item)} in place."]
    if old is not None:
        player.inventory.append(item_from_json(old))
        lines.append(f"The {name_of(item_from_json(old))} goes back into "
                     f"your bag.")
    return private("\n".join(lines), player)


def clear(player:Player, home:dict[str, Any], slot:str) -> list[Message]:
    placed = raw(home)
    if slot not in slots_of(home["type"]) or slot not in placed:
        return private("Nothing stands there.", player)
    if len(player.inventory) >= player.bag_size:
        return private("Your bag is full.", player)
    item = item_from_json(placed.pop(slot))
    player.inventory.append(item)
    return private(f"You take the {name_of(item)} down. It goes into "
                   f"your bag.", player)


def order(player:Player, item_id:str) -> list[Message]:
    if item_id not in catalogue():
        return private("The carpenter has no such piece.", player)
    price = buy_price(item_id, player)
    if player.gold < price:
        return private(f"That costs {price} gold. You only have "
                       f"{player.gold}.", player)
    if len(player.inventory) >= player.bag_size:
        return private("Your bag is full.", player)
    player.gold -= price
    player.inventory.append(item_id)
    return private(f"The carpenter delivers a {name_of(item_id)} for "
                   f"{price} gold.", player)


def look_of(state:dict[str, Any]) -> str:
    kind = PLANTS[state["kind"]]
    victim = state.get("victim")
    if victim:
        return say(state["kind"], "victim_look").format(
            name=victim["name"], left=max(0, victim["until"] - today()))
    if state.get("pod"):
        return say(state["kind"], "pod_look").format(
            name=state["pod"]["name"])
    if state["wilted"]:
        return kind["wilted"]
    feeling = mood(state)
    if feeling:
        return kind["hungry_looks"][0 if feeling == "warn" else 1]
    return kind["looks"][stage_of(state)]


def describe(home:dict[str, Any]) -> str:
    placed = furniture_of(home)
    if not placed:
        return "The rooms are bare."
    names = ", ".join(name_of(item) for item in placed.values())
    text = f"Furnished with: {names}. (comfort {comfort_of(home)})"
    if irrigated(home):
        text += " Copper pipes drip over the garden beds."
    for state in plants_of(home).values():
        text += " " + look_of(state)
    return text


def comfort_buff(player:Player, home:dict[str, Any]) -> str:
    comfort = comfort_of(home)
    wanted = next((key for need, key in COMFORT_TIERS if comfort >= need),
                  "")
    keys = [key for _, key in COMFORT_TIERS]
    lines = []
    if wanted and wanted not in player.buffs:
        player.buffs = [buff for buff in player.buffs if buff not in keys]
        apply_buff(player, wanted)
        lines.append("A well-furnished home leaves its mark on you.")
    hungry = starving(home)
    if hungry and "home_drained" not in player.buffs:
        apply_buff(player, "home_drained")
        lines.append(say(hungry, "drained"))
    bloom = blooming(home)
    if bloom and "home_bloom" not in player.buffs:
        apply_buff(player, "home_bloom")
        lines.append(say(bloom, "bloom_buff"))
    return " ".join(lines)


def bed_line(home:dict[str, Any]) -> str:
    beds = [item for slot, item in furniture_of(home).items()
            if ITEMS[item].get("furniture") == "bed"]
    if not beds:
        return ""
    best = max(beds, key=lambda item: ITEMS[item].get("comfort", 0))
    return f"You sleep in the {name_of(best)}."


def slot_label(home:dict[str, Any], slot:str, kind:str) -> str:
    if kind != "plant":
        return KINDS[kind][0]
    state = plants_of(home).get(slot)
    if state is None:
        return "Garden Bed (empty)"
    plant = PLANTS[state["kind"]]["name"]
    if state.get("victim"):
        return f"{plant} (occupied)"
    if state.get("pod"):
        return f"{plant} (pod)"
    if state.get("wilted"):
        return f"{plant} (wilted)"
    return f"{plant} ({STAGES[stage_of(state)]})"


def rooms_view(home:dict[str, Any]) -> list[dict]:
    placed = furniture_of(home)
    states = plants_of(home)
    view = []
    for item in rooms_of(home["type"]):
        view.append({
            "key": item.key, "name": item.name, "icon": item.icon,
            "col": item.col, "row": item.row, "width": item.width,
            "slots": [{"id": slot, "kind": kind,
                       "label": slot_label(home, slot, kind),
                       "icon": KINDS[kind][1],
                       "item": name_of(placed[slot]) if slot in placed
                       else "",
                       "plant": slot in states}
                      for slot, kind in item.slots()]})
    return view
