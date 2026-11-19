from ..controller import GameController
from ..content import ITEMS
from ..furnishing import garden, rules
from ..plants import PLANTS
from ..furnishing.layout import slots_of
from ..locations.shop.location import buy_price
from ..models import Player
from .home import current_home, explicit_home


def available(controller:GameController, player:Player) -> bool:
    if not explicit_home(controller, player):
        return False
    return current_home(controller, player)["home"] is not None


def selected_view(player:Player, home:dict, slot:str,
                  editable:bool) -> dict | None:
    kinds = slots_of(home["type"])
    if slot not in kinds:
        return None
    placed = rules.furniture_of(home)
    item = placed.get(slot)
    from ..furnishing.layout import KINDS
    icon = KINDS[kinds[slot]][1]
    view = {"id": slot, "label": rules.slot_label(home, slot, kinds[slot]),
            "icon": icon, "editable": editable,
            "item": rules.label(item) if item else "",
            "remove": f"!home clear {slot}" if item and editable else "",
            "candidates": [], "uses": uses_view(home, slot, editable)}
    view["plant"] = plant_view(player, home, slot, editable)
    if editable:
        view["candidates"] = [
            {"label": rules.label(found),
             "command": f"!home place {slot} {number}"}
            for number, found in rules.candidates(player, kinds[slot])]
    return view


def plant_view(player:Player, home:dict, slot:str,
               editable:bool) -> dict | None:
    state = rules.plants_of(home).get(slot)
    if home and slots_of(home["type"]).get(slot) != "plant":
        return None
    view = {"text": (f"{garden.state_text(state)}. {rules.look_of(state)}"
                     if state else ""),
            "progress": garden.progress_text(state) if state else "",
            "actions": [], "seeds": []}
    if player.profile.get("vine_held"):
        view["actions"].append({"label": "Pull free",
                                "command": "!home pull"})
    if state and state.get("victim"):
        if state["victim"]["id"] != player.id:
            view["actions"].append({"label": "Rescue",
                                    "command": f"!home rescue {slot}"})
        return view
    if (state and garden.can_swallow(state)
            and not player.profile.get("pod")):
        asked = player.profile.get("offer_ask") == slot
        view["actions"].append(
            {"label": "Confirm offer" if asked else "Offer yourself",
             "command": f"!home offer {slot}" + (" confirm" if asked
                                                  else "")})
    if state and garden.feed_open(player, state):
        view["actions"].append(
            {"label": PLANTS[state["kind"]]["feed"]["label"],
             "command": f"!home feed {slot}"})
    if not editable:
        return view
    if state:
        view["actions"] += [
            {"label": "Water", "command": f"!home water {slot}"},
            {"label": "Harvest", "command": f"!home harvest {slot}"},
            {"label": "Uproot", "command": f"!home uproot {slot}"}]
    else:
        view["seeds"] = [
            {"label": f"Plant {ITEMS[item]['name']}",
             "command": f"!home plant {slot} {number}"}
            for number, item in garden.seeds(player)]
    return view


def uses_view(home:dict, slot:str, editable:bool) -> list[dict]:
    what = rules.use_of(home, slot)
    if not editable or not what:
        return []
    if what == "bath":
        return [{"label": "Take a bath", "command": f"!home use {slot}"}]
    rows = []
    for entry in home["residents"] + home["guests"]:
        command = f"!home use {slot} {entry['name']}"
        rows.append({"label": f"Use with {entry['name']}",
                     "command": command})
        if what != "bed":
            rows.append({"label": f"{entry['name']} on top",
                         "command": f"{command} bottom"})
    return rows


def catalogue_view(player:Player, editable:bool,
                   kind:str="") -> list[dict]:
    if not editable:
        return []
    rows = []
    for item_id in rules.catalogue():
        if kind and not rules.fits(item_id, kind):
            continue
        price = buy_price(item_id, player)
        rows.append({"label": rules.label(item_id), "price": price,
                     "command": f"!home carpenter {item_id}",
                     "enabled": player.gold >= price
                     and len(player.inventory) < player.bag_size})
    return rows


def overlay(controller:GameController, player:Player,
            slot:str) -> dict | None:
    if not available(controller, player):
        return None
    info = current_home(controller, player)
    home = info["home"]
    editable = info["owned"] and info["away"] is None
    rooms = rules.rooms_view(home)
    for room in rooms:
        for entry in room["slots"]:
            entry["command"] = f"!house slot {entry['id']}"
            entry["selected"] = entry["id"] == slot
    return {
        "title": "🛋 Furnishing", "editable": editable, "rooms": rooms,
        "comfort": rules.comfort_of(home),
        "storage": rules.storage_bonus(home),
        "selected": selected_view(player, home, slot, editable),
        "catalogue": catalogue_view(player, editable,
                                    slots_of(home["type"]).get(slot, "")),
        "gold": player.gold,
    }
