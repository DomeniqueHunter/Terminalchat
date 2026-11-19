from types import SimpleNamespace
from dataclasses import replace

from ..config import CAFE_LOCK, LOCATION_MARK, PRIVATE_WHERE, REVIVE_PRICE
from ..content import ITEMS, SPELLS
from .. import control, routines
from ..controller import GameController
from ..dungeon import current_biome
from ..formulas import max_hp, max_mana
from ..locations.shop.location import item_description
from ..models import Message, Player
from ..npcs.hire import hire_price, owns_maid
from ..sheet import sheet_lines
from ..town_buildings import registry
from ..towns import TOWNS, town_of
from ..view import Button, Panel
from . import home, run_panels, trade, visit
from .tabs import CHAT_TOPICS


LOG_CLASSES = (
    (("💀", "🌑"), "death"),
    (("🗺",), "biome"),
    ((LOCATION_MARK,), "place"),
)
AMBIENT_PLACES = ("cafe",)
IDLE_BUTTONS = (("Lobby", "!lobby"),)
LOBBY_BUTTONS = (("Join", "!join"), ("Leave", "!leave"), ("Start", "!start"))
PAUSED_BUTTONS = (("Resume run", "!resume"), ("Retire run", "!retire"))
COMBAT_BUTTONS = (("Hit", "!hit"), ("Dodge", "!dodge"), ("Guard", "!guard"),
                  ("Force round", "!force"))
INFO_BUTTONS = (("Status", "!status"), ("Profile", "!profile"),
                ("Inventory", "!inv"), ("Spells", "!spells"),
                ("Body", "!body"), ("Leaderboard", "!top"),
                ("Graveyard", "!graveyard"), ("Help", "!help"))


def log_entries(messages:list[Message]) -> list[dict[str, str]]:
    entries = []
    for message in messages:
        text = message.text
        if message.style == "ambient":
            entries.append({"text": text, "kind": "ambient",
                            "place": message.place})
            continue
        if message.is_private:
            text = f"→ {message.recipient}: {text}"
        for line in text.splitlines() or [""]:
            kind = next((name for marks, name in LOG_CLASSES
                         if line.startswith(marks)), "")
            entries.append({"text": line, "kind": kind})
        entries.append({"text": "", "kind": ""})
    return entries


def echo_entry(sender:str, text:str) -> dict[str, str]:
    return {"text": f"> {sender}: {text}", "kind": "input"}


def stage_text(controller:GameController, viewer:Player | None) -> str:
    session = controller.session
    if session.state in ("combat", "chest", "remains", "event"):
        biome = current_biome(session.stage, session.run_id,
                               session.lobby_town)["name"]
        return f"⚔ Stage {session.stage} · {biome}"
    if session.state == "paused":
        return f"🚉 Run waits at stage {session.stage}"
    if session.state == "lobby":
        return "🕯 Lobby"
    if viewer is not None:
        return f"🏘 {town_of(viewer).name}"
    return "Cursed Descent"


def party_rows(controller:GameController, viewer:str | None) -> list[dict]:
    session = controller.session
    if not viewer or session.member(viewer) is None:
        return []
    if session.state in ("idle", "lobby"):
        return []
    return [{"name": member.name, "hp": max(0, member.hp),
             "max_hp": max_hp(member), "alive": member.alive,
             "npc": bool(member.npc), "you": member.name.casefold() == viewer.casefold(),
             "percent": round(100 * max(0, member.hp)
                              / max(1, max_hp(member)))}
            for member in session.party]


def action_buttons(controller:GameController) -> list[Button]:
    session = controller.session
    state = session.state
    if state == "idle":
        pairs = IDLE_BUTTONS
    elif state == "lobby":
        pairs = LOBBY_BUTTONS
    elif state == "paused":
        pairs = PAUSED_BUTTONS
    elif state == "combat":
        pairs = COMBAT_BUTTONS
    else:
        pairs = tuple((word.capitalize(), f"!{word}")
                      for word in session.available_commands())
    return [Button(label, command) for label, command in pairs]


ENCOUNTER_LABELS = {
    "open": "Open chest", "skip": "Skip chest", "loot": "Loot remains",
    "taste": "Taste stew", "pack": "Pack stew", "sellself": "Sell yourself",
    "offer": "Offer yourself", "sneak": "Sneak in",
    "thrust": "Use the hole",
}
OFFER_LABELS = {"accept": "Become maid", "decline": "Decline"}
PROFILE_BUTTONS = (("Profile", "!profile"), ("Inventory", "!inv"),
                   ("Spells", "!spells"), ("Leaderboard", "!top"),
                   ("Body", "!body"), ("Graveyard", "!graveyard"),
                   ("Help", "!help"))
OUTSIDE_BUTTONS = (("Create Lobby", "!lobby"), ("Find Lobby", "!findlobby"),
                   ("Start", "!solo"))
LOBBY_LEADER_BUTTON = ("Start", "!start")
IN_LOBBY_BUTTONS = (("Leave", "!leave"), ("Retire", "!retire"),
                    ("Resume", "!resume"))
DEAD_BUTTONS = (("End run", "!endrun"),
                (f"Resume now {REVIVE_PRICE}", "!endrun pay"))
READY_BUTTONS = (("✔ Ready", "!ready"), ("✘ Decline", "!decline"))
COMBAT_BUTTONS_LEFT = (("Hit", "!hit"), ("Cast", "!cast"),
                       ("Dodge", "!dodge"), ("Guard", "!guard"),
                       ("Use potion", "!potion"), ("Force round", "!force"))
DEBUG_BUTTONS = (("Events", "!events"), ("Enemies", "!enemies"),
                 ("Biomes", "!biomes"), ("Next biome", "!nextbiome"),
                 ("Cities", "!cities"), ("Surrender", "!surrender"))
PARTY_SLOTS = 4


def is_dead(controller:GameController, viewer:str | None) -> bool:
    player = controller.repository.load(viewer) if viewer else None
    return player is not None and bool(player.records.get(CAFE_LOCK))


def party_buttons(controller:GameController, viewer:str) -> tuple:
    if is_dead(controller, viewer):
        return DEAD_BUTTONS
    bundle = controller.lobbies.of(viewer) if viewer else None
    if bundle is None:
        buttons = OUTSIDE_BUTTONS
    else:
        session = bundle.session
        leads = (session.state == "lobby" and session.party
                 and session.party[0].name.casefold() == viewer.casefold())
        buttons = ((LOBBY_LEADER_BUTTON, *IN_LOBBY_BUTTONS) if leads
                   else IN_LOBBY_BUTTONS)
    if controller.ready.waiting_for(viewer):
        return (*READY_BUTTONS, *buttons)
    return buttons


def death_note(controller:GameController, viewer:str | None) -> str:
    if not is_dead(controller, viewer):
        return ""
    player = controller.repository.load(viewer)
    minutes = controller.town.respawn_minutes(player)
    return (f"💀 {viewer} is dead. The world clock brings {viewer} back "
            f"among the living in about {minutes} minutes. [Resume now "
            f"{REVIVE_PRICE}] pays for an earlier return, [End run] shows "
            f"the wait.")


def encounter_buttons(controller:GameController,
                      viewer:str) -> list[Button]:
    session = controller.session
    commands = session.available_commands()
    offer = viewer in session.recruit_offers
    if offer:
        commands = list(OFFER_LABELS) + [
            c for c in commands if c not in OFFER_LABELS]
    buttons = []
    for command in commands:
        label = ENCOUNTER_LABELS.get(command, command.capitalize())
        if offer and command in OFFER_LABELS:
            label = OFFER_LABELS[command]
        buttons.append(Button(label, f"!{command}",
                              "fill" if command == "answer" else ""))
    return buttons


def hit_rows(controller:GameController) -> list[dict]:
    session = controller.session
    if session.state != "combat":
        return []
    return [{"uid": enemy.uid, "name": enemy.name[:7], "hp": enemy.hp,
             "max_hp": enemy.max_hp}
            for enemy in session.enemies if enemy.alive]


def slot_rows(controller:GameController, viewer:str,
              main:str) -> list[dict]:
    session = controller.session
    names = ([member.name for member in session.party]
             or ([viewer] if viewer else []))
    rows = []
    for slot in range(PARTY_SLOTS):
        if slot >= len(names):
            rows.append({"slot": slot + 1, "name": "", "label": f"{slot + 1}: -"})
            continue
        name = names[slot]
        member = session.member(name)
        fallen = " †" if member is not None and not member.alive else ""
        robot = (" 🤖" if member is not None and session.is_auto(member)
                 else "")
        marker = "▶ " if name == viewer else ""
        star = " ★" if name == main else ""
        rows.append({"slot": slot + 1, "name": name,
                     "label": f"{slot + 1}: {marker}{name}{star}"
                              f"{fallen}{robot}"})
    return rows


def status_text(controller:GameController) -> str:
    session = controller.session
    names = ", ".join(member.name for member in session.party) or "-"
    return f"State: {session.state} | Party: {names}"


def encounter_lines(controller:GameController) -> list[str]:
    session = controller.session
    if session.state != "combat":
        return []
    return [line.strip() for line in session.enemy_lines()]


def target_choices(controller:GameController) -> list[str]:
    session = controller.session
    return [str(enemy.uid) for enemy in session.enemies if enemy.alive]


def spell_choices(viewer:Player | None) -> list[str]:
    return sorted(SPELLS)


def character_panel(controller:GameController, player:Player) -> Panel:
    stats = ", ".join(f"{name[:3].upper()} {value}"
                      for name, value in player.stats.items())
    gear = tuple(
        f"{slot}: {ITEMS[str(item)]['name']}"
        for slot, item in player.equipment.items() if item)
    bag = tuple(item_description(item_id) for item_id in player.inventory)
    buffs = ", ".join(player.buffs)
    lines = (f"Lv {player.level} · EXP {player.exp} · 💰 {player.gold}",
             f"HP {max(0, player.hp)}/{max_hp(player)} · "
             f"Mana {player.mana}/{max_mana(player)}",
             stats, *(f"Buffs: {buffs}",) * bool(buffs),
             *sheet_lines(player))
    return Panel(player.name, lines, (), (
        Panel("Gear", gear), Panel("Bag", bag)))


def held_here(controller:GameController, town, building:str,
              viewer:Player | None) -> list:
    found = []
    for name in controller.repository.names():
        who = controller.repository.load(name)
        if (who is None or who.npc or (viewer and who.name == viewer.name)
                or not control.kind_of(who)
                or who.profile.get("town") != town.key
                or who.profile.get("where") != building):
            continue
        found.append(SimpleNamespace(
            key=who.name, first_name=who.name, player=True,
            role=f"{control.kind_of(who).title} (player)"))
    return found


def extra_residents(controller:GameController, town, building:str) -> list:
    known = {person.key for each in TOWNS.values()
             for person in each.residents}
    return [SimpleNamespace(
        key=npc.npc, first_name=npc.first_name or npc.name,
        role=npc.profile.get("role", ""))
        for npc in controller.repository.npc_players()
        if npc.profile.get("kind") == "resident" and not npc.profile.get(
            "dead") and npc.npc not in known
        and npc.profile.get("town") == town.key
        and npc.profile.get("building") == building]


def residents_panel(town, building:str, watch:bool=False,
                    controller:GameController | None=None,
                    viewer:Player | None=None) -> Panel | None:
    here = routines.people(town.key, building) if building != "town" else []
    if controller is not None and building != "town":
        here = (here + extra_residents(controller, town, building)
                + held_here(controller, town, building, viewer))
    gone = routines.absent(town.key, building) if building != "town" else []
    if not here and not gone:
        return None
    sections = []
    for resident, note in [(person, "") for person in here] + gone:
        name = resident.first_name
        spot = routines.texts.at_place(resident.key) if not note else None
        talk = not note and (spot is None or bool(spot.dialogues))
        look = not note and (spot is None or bool(spot.examine))
        hints = [note] if note else []
        if spot is not None and not (talk and look):
            hints.append("Not much to see or say here yet.")
        buttons = [Button("🔍 Examine", f"!examine {name}", enabled=look)]
        if not watch and not getattr(resident, "player", False):
            buttons = [Button("Talk", f"!talk {name}", enabled=talk),
                       *buttons,
                       *(Button(topic.capitalize(), f"!chat {name} {topic}",
                                enabled=talk)
                         for topic in CHAT_TOPICS if topic)]
        sections.append(Panel(f"{name} – {resident.role}", tuple(hints),
                              tuple(buttons)))
    return Panel("Locals", (), (), tuple(sections))


def ambient_button(where:str, off:frozenset[str]) -> tuple[Button, ...]:
    buttons = []
    if where in AMBIENT_PLACES:
        label = ("🔕 Ambient text: off" if where in off
                 else "🔔 Ambient text: on")
        buttons.append(Button(label, f"!ambient {where}"))
    if where not in PRIVATE_WHERE and where not in ("", "dungeon"):
        label = ("🙈 Watching others: off" if "witness" in off
                 else "👁 Watching others: on")
        buttons.append(Button(label, "!ambient witness"))
    return tuple(buttons)


def location_panel(controller:GameController, player:Player,
                   ambient_off:frozenset[str]=frozenset()) -> list[Panel]:
    session = controller.session
    if session.in_run(player.name):
        shop = run_panels.run_shop_panel(controller, player)
        return [] if shop is None else [shop]
    leash = control_panel(player, controller)
    if leash is not None:
        return [leash]
    town = town_of(player)
    where = controller.town.where(player)
    owned = (home_of_player(controller, player) is not None)
    invitation = visit.offers_panel(player)
    neighbours = trade.neighbours_panel(town, player)
    panels = [Panel(f"🏘 {town.name}", (town.blurb,), (
        *(Button(building.button, f"!{building.command}")
          for building in town.building_list()),
        Button("🏠 Home" if owned else "🏠 House offers", "!home")),
        (neighbours,) if neighbours is not None else ())]
    if invitation is not None:
        panels.insert(0, invitation)
    if home.explicit_home(controller, player):
        inside = home.home_panel(controller, player)
        return [inside] if invitation is None else [invitation, inside]
    building = registry.panel_for(where, controller.town, player)
    if building is not None:
        sections = building.sections
        if where == "station" and (controller.debug
                                   or controller.is_admin(player.name)):
            sections = (*sections, Panel("⚡ Admin teleport", (
                "Instant trip, no fare, no rail pass needed.",), tuple(
                    Button(goal.name, f"!teleport {goal.name}")
                    for key, goal in TOWNS.items() if key != town.key)))
        locals_panel = residents_panel(town, where, False, controller, player)
        info = registry.info_lines(where, controller.town, player)
        if info:
            sections = (*sections, Panel("ℹ Household", info))
        if locals_panel is not None:
            sections = (*sections, locals_panel)
        inside = replace(
            building, buttons=(*building.buttons,
                               *ambient_button(where, ambient_off),
                               Button("← Town", "!town")),
            sections=sections)
        local = registry.get(where, town.key)
        if local is not None and local.label and local.renamed:
            mark = f"{local.icon} " if local.icon else ""
            inside = replace(inside, title=f"{mark}{local.title}")
        return [inside] if invitation is None else [invitation, inside]
    return panels


def around_panel(controller:GameController, player:Player) -> Panel:
    town = town_of(player)
    where = controller.town.where(player)
    spec = registry.get(where, town.key)
    title = spec.title if spec is not None else "the town"
    locals_panel = residents_panel(town, where, True, controller, player)
    lines = registry.info_lines(where, controller.town, player)
    return Panel(f"👁 Around you – {title}", (
        "You can only look. Examine shows who is here and what they do.",
        *lines), (), (locals_panel,) if locals_panel is not None else ())


def control_panel(player:Player, controller:GameController
                  ) -> Panel | None:
    kind = control.kind_of(player)
    if kind is None:
        return None
    holder = control.holder_of(player)
    buttons = [Button("Status", "!slave")]
    if kind.safeword:
        buttons.append(Button("Safeword", "!slave release"))
    if kind.can_end and control.state_of(player)["data"].get("end_ask"):
        buttons += [Button("Yes, end this character", "!slave end confirm"),
                    Button("No, go back", "!slave cancel")]
    elif kind.can_end:
        buttons.append(Button("End character", "!slave end"))
    return Panel(f"⛓ {kind.title}", (
        kind.watch_text.format(holder=holder, name=player.name),),
        tuple(buttons), (around_panel(controller, player),))


def home_of_player(controller:GameController, player:Player):
    from ..houses import home_of, shared_host
    town = town_of(player)
    return (home_of(player, town.key)
            or shared_host(player, town.key, controller.repository))


def live_parts(panel:Panel) -> list[Panel]:
    found = [panel] if panel.timer or panel.bars else []
    for section in panel.sections:
        found += live_parts(section)
    return found


def live_panels(controller:GameController, viewer:Player) -> list[Panel]:
    panels = location_panel(controller, viewer)
    state = visit.current_visit(controller, viewer)
    if state is not None:
        panels.append(visit.visit_panel(controller, viewer, state))
    sex = visit.sex_panel(controller, viewer)
    if sex is not None:
        panels.append(sex)
    return [part for panel in panels for part in live_parts(panel)]


def known_players(controller:GameController) -> list[str]:
    return sorted(controller.repository.names(), key=str.casefold)


def hire_options(controller:GameController, viewer:str,
                 own:list[str]) -> list[tuple[str, str]]:
    session, repository = controller.session, controller.repository
    options = [(name, name) for name in own]
    taken = {name for name, _ in options}
    me = repository.load(viewer)
    for npc in repository.npc_players():
        if npc.name in taken:
            continue
        in_party = session.member(npc.name) is not None
        if in_party and session.is_companion(npc):
            note = "in party"
        elif (npc.npc == "maid" and me is not None
              and owns_maid(repository, me, npc)):
            note = f"your maid, Lv {npc.level}, free"
        elif npc.npc == "mercenary" and not repository.is_story(npc):
            note = f"mercenary, Lv {npc.level}, {hire_price(npc)} gold"
        elif npc.npc == "maid" and npc.profile.get("graduate"):
            note = f"maid graduate, Lv {npc.level}, {hire_price(npc)} gold"
        else:
            continue
        options.append((npc.name, f"{npc.full_name} ({note})"))
    return options
