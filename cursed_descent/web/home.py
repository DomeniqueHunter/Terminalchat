from typing import Any

from ..commands import command as cmd
from ..config import BANK_SLOTS, HOUSE_BEDS_PER_ROOM, HOUSE_TYPES
from ..controller import GameController
from ..invite_list import invite_candidates, suggested_mode
from ..houses import (
    PLACE_TEXT, catalogue, chest_of, home_of, hosted_by, lodging_lines,
    shared_host, status_lines,
)
from ..locations.shop.location import item_description
from ..models import Player
from ..towns import town_of
from ..view import Button, Choice, Panel, Row
from . import stash, trade


INVITE_ROLES = {
    "Plain guest": ("", "A normal visit, nobody is in charge."),
    "Dominant": ("sub", "The guest is dominant: the guest decides, you "
                        "obey."),
    "Submissive": ("domina", "The guest is submissive: you decide, the "
                             "guest obeys."),
}


class Shim:
    def __init__(self, controller:GameController) -> None:
        self.controller = controller

    def known_players(self) -> list[str]:
        return sorted(self.controller.repository.names(),
                      key=str.casefold)


def explicit_home(controller:GameController, player:Player) -> bool:
    return (player.profile.get("where") == "home"
            and not controller.session.in_run(player.name))


def current_home(controller:GameController, player:Player) -> dict:
    town = town_of(player)
    repository = controller.repository
    away = hosted_by(player, town.key, repository)
    home = None if away is not None else home_of(player, town.key)
    owned = home is not None
    host = None
    if home is None:
        host = away or shared_host(player, town.key, repository)
        home = home_of(host, town.key) if host is not None else None
    lodger = (home is not None and not owned and any(
        entry["id"] == player.id for entry in home["residents"]))
    return {"town": town, "away": away, "home": home, "owned": owned,
            "lodger": lodger, "host": host}


def toolbar(info:dict) -> tuple[Button, ...]:
    buttons = [Button("👁 Examine", "!home look"),
               Button("🛋 Furnishing", "!house open"),
               Button("Leave", "!houseleave")]
    if info["owned"] or info["home"] is not None:
        buttons += [Button("🛏 Sleep", "!home sleep"),
                    Button("🍳 Cook", "!home cook"),
                    Button("🍽 Eat", "!home eat")]
    if info["lodger"]:
        buttons.append(Button("📦 Move out", "!home moveout"))
    return tuple(buttons)


def place_of_entry(controller:GameController, entry:dict) -> str:
    for hero in controller.repository.cache.values():
        if hero.id == entry["id"] and not hero.npc:
            return controller.town.where(hero) or "home"
    return "home"


def guests_panel(controller:GameController, player:Player, home:dict,
                 owner:Player | None) -> Panel:
    people = []
    if owner is not None:
        place = controller.town.where(owner)
        note = ("owner" if place == "home"
                else f"owner, away: {PLACE_TEXT.get(place, place)}")
        people.append(({"id": owner.id, "name": owner.full_name}, note))
    people += [(entry, "lives here") for entry in home["residents"]]
    people += [(entry, "guest") for entry in home["guests"]]
    people = [(entry, role) for entry, role in people
              if entry["id"] != player.id]
    if not people:
        return Panel("Guests", ("Nobody else is here.",))
    rows = []
    for entry, role in people:
        name = entry["name"]
        place = place_of_entry(controller, entry)
        here = place == "home"
        if not here:
            role = f"{role}, away: {PLACE_TEXT.get(place, place)}"
        rows.append(Row(f"{name} ({role})", (
            Button("👁", f"!home look {name}", "", here),
            Button("Sex", f"!home sex {name}", "", here),
            Button("Talk", f"!home talk {name}", "", here),
            *trade.guest_trade_row(name, here),
            Button("✕", f"!home leave {name}"))))
    return Panel("Guests", rows=tuple(rows),
                 choices=(trade.item_choice(player),))


def invite_panel(controller:GameController, player:Player,
                 home:dict, town) -> Panel:
    present = {entry["name"].casefold() for entry in
               home["residents"] + home["guests"]}
    present |= {word for name in present for word in name.split()[:1]}
    found = invite_candidates(Shim(controller), player, town, present)
    names = [(entry[0], entry[0]) for entry in found]
    suggestion = (INVITE_ROLES[suggested_mode(player, found[0][1])][0]
                  if found else "")
    return Panel("Invite", tuple(
        f"{label}: {text}" for label, (_, text) in INVITE_ROLES.items()),
        (Button("Invite", "!home invite"), Button("Move in", "!home movein"),
         Button("Invite everyone (as many as fit)", "!home invite all")),
        choices=(Choice("guest", "Guest", tuple(names), "select"),
                 Choice("mode", "Mode", tuple(
                     (code, label) for label, (code, _) in
                     INVITE_ROLES.items()), "select", suggestion)))


def chest_panel(controller:GameController, player:Player) -> Panel | None:
    account = chest_of(player, town_of(player).key)
    if account is None:
        return None
    return stash.summary_panel("📦 Chest", account, "home")


def lodging_panel(controller:GameController, player:Player,
                  town) -> Panel | None:
    lines = lodging_lines(player, town.key, controller.repository)
    if not lines:
        return None
    return Panel("You live here", tuple(lines), (
        Button("🛏 Sleep here", "!home sleep"),
        Button("📦 Move out", "!home moveout")))


def offers_panel(player:Player, town) -> Panel:
    sections = []
    for key, name, price, rooms in catalogue(town.key):
        sections.append(Panel(name, (
            HOUSE_TYPES[key][3], f"{rooms} room(s), "
            f"{rooms * HOUSE_BEDS_PER_ROOM} beds – {price} gold"), (
                Button(f"Buy ({price} g)", f"!home buy {key}", "",
                       player.gold >= price),)))
    return Panel("You own no house here. Pick one:", (), (),
                 tuple(sections))


def home_panel(controller:GameController, player:Player) -> Panel:
    info = current_home(controller, player)
    town, home = info["town"], info["home"]
    sections: list[Panel | None] = []
    lines: tuple[str, ...] = ()
    if info["away"] is not None:
        lines = (f"You are at {info['away'].name}'s house.",)
    repository = controller.repository
    if info["owned"] and shared_host(player, town.key, repository):
        sections.append(lodging_panel(controller, player, town))
    if home is None:
        sections += [lodging_panel(controller, player, town),
                     offers_panel(player, town)]
        return Panel("🏠 Home", lines, toolbar(info), tuple(
            s for s in sections if s is not None))
    if info["owned"]:
        lines += tuple(status_lines(player, town.key)[:2])
    else:
        lines += (f"🏠 {home['owner_name']}'s "
                  f"{HOUSE_TYPES[home['type']][0]}",
                  HOUSE_TYPES[home["type"]][3])
    owner = None if info["owned"] else repository.load_by_id(home["owner"])
    sections.append(guests_panel(controller, player, home, owner))
    if info["owned"] or info["lodger"]:
        sections.append(invite_panel(controller, player, home, town))
    if info["away"] is None:
        sections.append(chest_panel(controller, player))
    return Panel("🏠 Home", lines, toolbar(info), tuple(
        s for s in sections if s is not None))
