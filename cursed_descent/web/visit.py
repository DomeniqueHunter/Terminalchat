from ..config import SEX_CONTENT_MAX, SEX_HEAT_MAX
from ..controller import GameController
from ..home_scene import bound_text, is_auto, scene_info
from ..house_regulars import is_regular
from ..house_titles import TITLES
from ..house_visit import (
    describe_house, dynamic_of, entry_by_name, person_of, present,
    state_of as visit_state,
)
from ..houses import home_partner
from ..models import Player
from ..preferences import prefs_of
from ..scenes import AMOUNTS, DEFAULTS, POSITIONS, ROLES, WHERE
from ..sex_overlays import LABELS as ACTION_LABELS
from ..sex_sole import OBEYING
from ..town_buildings.brothel.practices import can_do
from ..town_buildings.brothel.practices_content import ACT_LABELS
from ..towns.last_light_humans.cafe.ui import seat_panel
from ..towns import town_of
from ..view import Bar, Button, Choice, Panel, Row
from ..home_practice import other_role


VIEWS = {
    "player": ("Command", "{name} is yours to command. "
                          "★ marks what {name} wishes for."),
    "npc": ("Suggest", "{name} is in charge: you may suggest, {name} "
                       "decides."),
    "": ("Do", ""),
}
NEEDS = ("eat", "sleep", "rest", "relax", "bathe")


def current_visit(controller:GameController,
                  player:Player) -> dict | None:
    if controller.session.in_run(player.name):
        return None
    return visit_state(player)


def offers_panel(player:Player) -> Panel | None:
    offer = player.profile.get("house_offer")
    intimate = player.profile.get("sex_offer")
    sleepy = player.profile.get("sleep_offer")
    if sleepy:
        return Panel("Invitation", (f"{sleepy['from']} wants everyone to "
                                    f"sleep.",), (
            Button("Sleep", "!sleep yes"), Button("Not yet", "!sleep no")))
    if not offer and not intimate:
        return None
    if intimate:
        text = f"{intimate['from']} asks you for something intimate."
    else:
        what = "move into" if offer["kind"] == "movein" else "come over to"
        text = f"{offer['from']} asks you to {what} their house."
    return Panel("Invitation", (text,), (
        Button("Accept", "!home accept"), Button("Decline", "!home decline")))


def scene_choices() -> tuple[Choice, ...]:
    return (Choice("s_position", "Position", tuple(
                (key, key) for key in POSITIONS), "select",
                DEFAULTS["position"]),
            Choice("s_role", "Role", tuple((r, r) for r in ROLES),
                   "select", DEFAULTS["role"]),
            Choice("s_amount", "Amount", tuple((a, a) for a in AMOUNTS),
                   "select", DEFAULTS["amount"]),
            Choice("s_where", "Where", tuple((w, w) for w in WHERE),
                   "select", DEFAULTS["where"]))


def visit_panel(controller:GameController, player:Player,
                state:dict) -> Panel:
    services = controller.town
    repository = controller.repository
    title = f"🏠 Home – {state['host']} – {state['address']}"
    shift = services.shifts.get(player.name)
    if shift is not None and shift.mode == "home":
        return Panel(title, (), (), (seat_panel(services, player, shift),))
    crowd = present(player, repository, state)
    sections = [
        Panel("Examine", (describe_house(state),), (
            Button("🔍 Look around", "!house look"),)),
        Panel("Present", () if crowd else ("Nobody is here.",), (),
              rows=tuple(Row(f"{entry['name']} ({entry['kind']})", (
                  Button("👁", f"!house look {entry['name']}"),))
                  for entry in crowd)),
        Panel("Talk to:", (), tuple(Button(
            entry["name"], f"!house talk {entry['name']}")
            for entry in crowd)),
        Panel("Do:", (), tuple(Button(word.capitalize(), f"!house {word}")
                               for word in NEEDS)),
        Panel("Sex with:", (), tuple(Button(
            entry["name"], f"!house sex {entry['name']}")
            for entry in crowd if entry["kind"] != "family"))]
    owner = any(entry["kind"] == "owner" for entry in crowd)
    if state["building"] == "cafe" and owner:
        sections.append(Panel("Seat session", (), (
            Button("Sit", "!house seat", "danger"),), choices=(
                Choice("intensity", "Intensity", tuple(
                    (v, v) for v in ("gentle", "normal", "hard")),
                    "select", "normal"),
                Choice("length", "Length", (("short", "short"),
                                            ("long", "long")),
                       "select", "long"))))
    return Panel(title, (), (Button("Leave the house", "!house leave"),),
                 tuple(sections))


def can_pair(player:Player, partner, act:str, role:str) -> bool:
    return (can_do(player.gender, act, role, player.body)
            and (partner is None or can_do(
                partner.gender, act, other_role(role), partner.body)))


def scene_section(controller:GameController, player:Player,
                  name:str) -> Panel | None:
    info = scene_info(player, controller.repository)
    if info is None:
        return None
    bars = [Bar("heat_you", "🔥 You", info["heat"], SEX_HEAT_MAX),
            Bar("heat_mate", f"🔥 {name}", info["mate_heat"], SEX_HEAT_MAX)]
    if info["air"] is not None:
        bars.append(Bar("air", f"🫁 {info['air_owner']}", info["air"], 100))
    overlay = info.get("overlay") or {}
    if overlay and overlay.get("sweat") is not None:
        bars.append(Bar("sweat", "🦶 Foot sweat", overlay["sweat"], 100))
    lines = [f"♥ Contentment {info['content']}/{SEX_CONTENT_MAX}"]
    if overlay and overlay.get("order"):
        lines.append("⚠ Ordered: lick")
    buttons = []
    sections = []
    if overlay:
        side = "you give" if overlay["side"] == "giver" else "you receive"
        actions = []
        for action in overlay["actions"]:
            mark = "● " if overlay["chosen"] == action else ""
            if overlay.get("order") and action in OBEYING:
                mark = f"👅 {mark}"
            actions.append(Button(f"{mark}{ACTION_LABELS[action]}",
                                  f"!home act {action}"))
        sections.append(Panel(
            f"{ACT_LABELS[overlay['act']].capitalize()} – {side}", (),
            tuple(actions)))
    if info["owes"]:
        buttons.append(Button(f"Answer: 'Yes, {info['owes']}.'",
                              "!home answer"))
    return Panel("Scene", tuple(lines), tuple(buttons), tuple(sections),
                 timer=controller.town.timer_text(player), bars=tuple(bars))


def sex_panel_for(controller:GameController, player:Player, partner,
                  state:dict) -> Panel:
    name = state["sex_with"]
    view = state.get("dynamic", "")
    title, hint = VIEWS.get(view, VIEWS[""])
    kind = state.get("kind", "house")
    lines = [hint.format(name=name)] if hint else []
    if view == "npc":
        called = player.profile.get("i_call", {})
        word = next(iter(called.values()), "")
        if partner is not None and partner.id in called:
            word = called[partner.id]
        if word:
            lines.append(f"Call {name}: {word.capitalize()}")
        if state.get("held_by"):
            lines.append(f"📌 Pinned: {state['held_by']} decides when it "
                         f"is over.")
    sections: list[Panel | None] = []
    if view == "player":
        sections.append(Panel("Order to call you", (), (
            Button("Order", f"!{kind} order {name}"),), choices=(
                Choice("title", "Title", tuple((t, t) for t in TITLES),
                       "select", TITLES[0]),)))
    if (kind == "home" and partner is not None
            and not is_regular(partner)):
        sections.append(scene_section(controller, player, name))
    current = prefs_of(player)["role"]
    sections.append(Panel("Your role", (), tuple(
        Button(("● " if role == current else "") + role.capitalize(),
               f"!prefs role {role}") for role in ("dom", "sub", "switch"))))
    liked = prefs_of(partner)["flow"] if partner is not None else {}
    wish = tuple(state.get("wish") or ())
    rows = []
    for act, label in ACT_LABELS.items():
        buttons = tuple(Button(
            f"{'★ ' if wish == (act, role) else ''}{role.capitalize()}",
            f"!{kind} practice {name} {act} {role}", "",
            can_pair(player, partner, act, role))
            for role in ("give", "receive"))
        rows.append(Row(f"{'★ ' if act in liked else ''}"
                        f"{label.capitalize()}", buttons))
    sections.append(Panel(title, rows=tuple(rows)))
    sections.append(Panel("Scene", (
        "role = the one who asks takes (top) or is taken (bottom)",),
        choices=scene_choices()))
    blocked = bool(state.get("held_by") or (
        kind == "home"
        and bound_text(player, controller.repository)))
    return Panel(f"💞 Sex – {name}", tuple(lines), (
        Button("Back to the rooms", f"!{kind} back", "", not blocked),),
        tuple(s for s in sections if s is not None))


def sex_panel(controller:GameController, player:Player) -> Panel | None:
    repository = controller.repository
    regulars = controller.town.regulars_of(player)
    state = current_visit(controller, player)
    if state is None and player.profile.get("home_sex"):
        partner = home_partner(player, town_of(player).key, repository,
                               regulars)
        if partner is None:
            return None
        info = scene_info(player, repository)
        wish = list(info["wish"]) if info and info["wish"] else []
        dynamic = dynamic_of(player, partner, {"building": ""})
        if is_auto(partner) and dynamic == "":
            dynamic = "npc" if prefs_of(partner)["role"] != "sub" else ""
        return sex_panel_for(controller, player, partner, {
            "sex_with": partner.name, "kind": "home", "wish": wish,
            "dynamic": dynamic})
    if state is None or not state.get("sex_with"):
        return None
    name = state["sex_with"]
    entry = entry_by_name(present(player, repository, state), name)
    partner = (person_of(entry, repository, regulars)
               if entry is not None else None)
    if partner is not None:
        state = {**state, "dynamic": dynamic_of(player, partner, state)}
    return sex_panel_for(controller, player, partner, state)
