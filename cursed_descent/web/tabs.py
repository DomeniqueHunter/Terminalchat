from typing import Any

from ..body import body_text, effects_text
from ..config import (
    EQUIPMENT_SLOTS, MAX_PARTY_SIZE, SLOT_LABELS, STAT_NAMES, STAT_SHORT,
)
from ..content import ITEMS
from ..controller import GameController, family_lines
from ..family_tree import family_tree
from ..figure import GROUND, HEIGHT, WIDTH, draw_figure
from ..formulas import (
    allure, buff_lines, exp_needed, max_hp, max_mana, set_lines,
    stat_total_text, totals_line,
)
from ..inventory import grouped, sort_inventory
from ..locations.clinic.location import enhancement_lines
from ..locations.shop.location import item_description
from ..models import Player
from ..needs import needs_line
from ..settings import fill
from ..friends import friend_names, pending_names
from ..town_buildings.family import FAMILY_ROLES, entries, pending
from ..towns import TOWNS, town_key
from ..view import Button, Choice, Panel, Row
from ..sweat import condition_line
from ..sheet import sheet_lines
from .svg_canvas import SvgCanvas


CHAT_TOPICS = ("", "work", "town", "self")
SHOWN_TIERS = (("friend", "Friends"), ("acquaintance", "Acquaintances"))


def figure_svg(player:Player) -> str:
    canvas = SvgCanvas(WIDTH, HEIGHT)
    draw_figure(canvas, player)
    return canvas.svg()


SOLO_SCALE = 150 / 170
TALLEST = 185


def figure_sizes(members:list[Player]) -> list[float]:
    tallest = max(member.body["height"] for member in members)
    scale = min(SOLO_SCALE, TALLEST / max(tallest, 1))
    return [member.body["height"] * scale for member in members]


def party_figures(members:list[Player]) -> str:
    sizes = figure_sizes(members)
    canvas = SvgCanvas(WIDTH * len(members), HEIGHT)
    for index, member in enumerate(members):
        cx = WIDTH * index + WIDTH / 2
        draw_figure(canvas, member, sizes[index], cx, WIDTH, False)
        canvas.create_text(cx, GROUND + 10, text=member.name.split()[0][:16],
                           fill="#888888", font=("TkDefaultFont", 8, "bold"))
        canvas.create_text(cx, GROUND + 22,
                           text=f"{member.body['height']} cm",
                           fill="#777777", font=("TkDefaultFont", 7))
    return canvas.svg()


def character_tab(controller:GameController, player:Player) -> dict[str, Any]:
    member = controller.session.member(player.name)
    in_run = member is not None
    shown = member if member is not None else player
    hp = shown.hp if in_run else max_hp(shown)
    mana = shown.mana if in_run else max_mana(shown)
    head = [f"{shown.name} – Lv {shown.level} {shown.title}",
            f"{shown.gender}, {shown.age} | EXP "
            f"{shown.exp}/{exp_needed(shown.level)}",
            f"Gold {shown.gold} | Allure {allure(shown)}",
            f"HP {max(hp, 0)}/{max_hp(shown)} | "
            f"Mana {mana}/{max_mana(shown)}",
            *needs_line(shown.needs).split(" | "),
            *([condition_line(shown)] if in_run else []),
            *buff_lines(shown)]
    body = [fill(line) for line in (
        body_text(player.body), f"→ {effects_text(player.body)}",
        *enhancement_lines(player))]
    stats = [{"text": stat_total_text(player, stat),
              "short": STAT_SHORT[stat].lower()} for stat in STAT_NAMES]
    return {"head": head, "body": body, "stats": stats,
            "free": player.free_points,
            "notes": [totals_line(player), *family_lines(player)],
            "sheet": sheet_lines(player), "figure": figure_svg(player),
            "flist": player.profile.get("flist", "")}


def inventory_tab(controller:GameController, player:Player) -> dict[str, Any]:
    in_combat = controller.session.state == "combat"
    equipment = []
    for slot in EQUIPMENT_SLOTS:
        item_id = player.equipment[slot]
        equipment.append({"slot": slot, "label": SLOT_LABELS[slot],
                          "name": ITEMS[item_id]["name"] if item_id else "-",
                          "filled": bool(item_id)})
    sort_inventory(player)
    gear, consumables = grouped(player)
    bag = []
    number = 0
    for title, items in (("Gear", gear), ("Consumables", consumables)):
        rows = []
        for item_id in items:
            number += 1
            consumable = ITEMS[item_id]["slot"] == "consumable"
            rows.append({"number": number, "id": item_id,
                         "consumable": consumable,
                         "text": item_description(item_id)})
        if rows:
            bag.append({"title": title, "rows": rows})
    counts: dict[str, int] = {}
    for item_id in consumables:
        counts[item_id] = counts.get(item_id, 0) + 1
    return {"equipment": equipment, "sets": set_lines(player),
            "potions": [{"id": item_id, "count": count,
                         "text": item_description(item_id)}
                        for item_id, count in counts.items()],
            "bag": bag, "used": len(player.inventory),
            "size": player.bag_size, "combat": in_combat}


def lobby_overlay(controller:GameController,
                  player:Player) -> dict[str, Any]:
    lobbies = controller.lobbies
    mine = lobbies.of(player.name)
    here = town_key(player)
    cards = []
    for bundle in lobbies.open_lobbies():
        session = bundle.session
        leader = session.party[0].name
        own = bundle is mine
        reason = ""
        if not own:
            if mine is not None:
                reason = "Leave your lobby first"
            elif len(session.party) >= MAX_PARTY_SIZE:
                reason = "Full"
            elif here != session.lobby_town:
                reason = f"Gathers in {TOWNS[session.lobby_town].name}"
        mine_leader = own and leader == player.name
        cards.append({
            "own": own, "leader": leader, "reason": reason,
            "town": TOWNS[session.lobby_town].name,
            "count": len(session.party), "max": MAX_PARTY_SIZE,
            "is_leader": mine_leader,
            "members": [{"name": member.name,
                         "offline": not member.npc
                         and not controller.is_online(member.name),
                         "npc": bool(member.npc),
                         "kick": mine_leader and member.name != player.name
                         and not member.npc}
                        for member in session.party]})
    cards.sort(key=lambda card: not card["own"])
    running = (mine is not None and mine.session.state != "lobby")
    return {"cards": cards, "running": running,
            "can_create": mine is None}


def whisper_names(controller:GameController, player:Player) -> list[str]:
    from . import audience
    repository = controller.repository
    found = list(friend_names(player, repository))
    for name in sorted(audience.place_mates(controller, player.name),
                       key=str.casefold):
        if name not in found:
            found.append(name)
    return [name for name in found
            if name != player.name and controller.is_online(name)]


def friend_panels(controller:GameController, player:Player) -> list[Panel]:
    repository = controller.repository
    session = controller.session
    leading = (session.state == "lobby" and session.member(player.name)
               is not None and session.party[0].name == player.name)
    panels = []
    asks = pending_names(player)
    if asks:
        panels.append(Panel("Friend requests", (), (), rows=tuple(
            Row(f"{name} asks to be your friend", (
                Button("Accept", f"!friend accept {name}"),
                Button("Decline", f"!friend decline {name}")))
            for name in asks)))
    rows = []
    for name in friend_names(player, repository):
        online = controller.is_online(name)
        buttons = []
        if leading and online and controller.lobbies.of(name) is None:
            buttons.append(Button("Invite", f"!lobby invite {name}"))
        buttons.append(Button("Remove", f"!friend remove {name}", "danger"))
        rows.append(Row(f"{name} – {'🟢 online' if online else '⚫ offline'}",
                        tuple(buttons)))
    panels.append(Panel("Friends", () if rows else (
        "No friends yet.",), (), rows=tuple(rows)))
    others = tuple((name, name) for name in sorted(
        repository.names(), key=str.casefold)
        if name != player.name and not (
            repository.load(name) or player).npc)
    panels.append(Panel("Add a friend", (
        "The other player has to confirm.",), (
            Button("Ask", "!friend add"),), choices=(
                Choice("friend_char", "Player", others, "select"),)))
    return panels


def private_requests(controller:GameController,
                     player:Player) -> list[str]:
    session = controller.session
    asker = controller.proposals.get(player.name, "")
    if (asker and session.member(player.name) is not None
            and session.member(asker) is not None):
        return [asker]
    return []


def party_tab(controller:GameController,
              player:Player) -> dict[str, Any]:
    session = controller.session
    in_party = session.member(player.name) is not None
    members = list(session.party) if in_party else [player]
    leader = (in_party and session.state == "lobby"
              and session.party[0].name == player.name)
    rows = []
    for member in members:
        rows.append({"name": member.name, "level": member.level,
                     "height": member.body["height"],
                     "weight": member.body["weight"],
                     "auto": session.is_auto(member),
                     "hp": max(0, member.hp), "max_hp": max_hp(member),
                     "alive": member.alive,
                     "other": member.name != player.name,
                     "offline": not member.npc
                     and not controller.is_online(member.name),
                     "kick": leader and member.name != player.name
                     and not member.npc})
    return {"members": rows, "figures": party_figures(members),
            "invite": controller.lobbies.invites.get(player.name, ""),
            "requests": private_requests(controller, player),
            "waiting": [target for target, asker in
                        controller.proposals.items()
                        if asker == player.name
                        and session.member(target) is not None],
            "in_lobby": in_party and session.state == "lobby",
            "leader": leader,
            "topics": [(topic.capitalize() or "Any", topic)
                                        for topic in CHAT_TOPICS]}


def family_tab(controller:GameController, player:Player) -> dict[str, Any]:
    rows = family_tree(player, controller.repository)
    return {"name": player.name, "rows": rows, "empty": len(rows) <= 1,
            "panels": family_panels(controller, player)}


def family_panels(controller:GameController, player:Player) -> list[Panel]:
    repository = controller.repository
    panels = []
    asks = pending(player)
    if asks:
        panels.append(Panel("Requests", (), (), rows=tuple(
            Row(f"{name} asks to be your {role}", (
                Button("Accept", f"!family accept {name}"),
                Button("Decline", f"!family decline {name}")))
            for _, name, role in asks)))
    linked = entries(player, repository)
    if linked:
        panels.append(Panel("Your family", (), (), rows=tuple(
            Row(f"{name}: your {role}",
                (Button("Remove", f"!family clear {name}", "danger"),))
            for _, name, role in linked)))
    others = tuple((name, name) for name in sorted(
        repository.names(), key=str.casefold) if name != player.name)
    panels.append(Panel("Ask someone to be your …", (
        "The other character has to confirm before the link exists.",), (
            Button("Ask", "!family mark"),), choices=(
                Choice("fam_char", "Character", others, "select"),
                Choice("fam_role", "Is your", tuple(
                    (role, role) for role in FAMILY_ROLES), "select"))))
    return panels


def contacts_tab(controller:GameController, player:Player) -> list[dict]:
    from ..town_buildings.chat import friendship, tier_of
    npcs = controller.repository.npc_players()
    groups: dict[str, list[dict]] = {tier: [] for tier, _ in SHOWN_TIERS}
    for npc in npcs:
        points = friendship(npc, player)
        tier = tier_of(points)
        if tier in groups:
            groups[tier].append({
                "name": npc.full_name, "gender": npc.gender, "age": npc.age,
                "points": points,
                "address": (npc.profile.get("home", "")
                            if tier == "friend" else "")})
    for rows in groups.values():
        rows.sort(key=lambda row: (-row["points"], row["name"]))
    return [{"title": title, "rows": groups[tier]}
            for tier, title in SHOWN_TIERS]


def mail_tab(controller:GameController, player:Player) -> dict[str, Any]:
    from ..town_buildings.post_office.ui import mail_panels
    services = controller.town
    return {"panels": mail_panels(services, player),
            "unread": services.mail.unread(player.id)}
