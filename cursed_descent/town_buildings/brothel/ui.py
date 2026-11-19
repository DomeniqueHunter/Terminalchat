from ...config import BROTHEL_CUT, RENT_PRICES
from ...models import Player
from ...towns import town_of
from ...towns.localize import localize_text
from ...view import Button, Choice, Panel
from ..work import ui as work_ui
from ..work.content import OWNERS, PLACES
from .clients import wish_text
from .dialogue_content import TONES
from .practices import can_do
from .practices_content import ACT_LABELS, ROLES


FINISHERS = (("swallow", "Anal vore (facesitting)"),
             ("wipe", "Wipe memory (foot)"))


def client_panel(services, player:Player, shift) -> Panel:
    client = shift.client
    title = (f"Client – {shift.served} served, {shift.earned} g earned"
             if shift.endless else
             f"Client – {shift.left} left, {shift.earned} g earned")
    buttons = list(work_ui.examine_buttons((f"Examine {client.name}",
                                            client.name)))
    buttons += [Button("★ Make regular", "!regular"),
                Button("Order their address" if client.dominated
                       else "Ask for their address", "!regular ask"),
                Button("End shift", "!safeword")]
    acts = []
    for act, label in ACT_LABELS.items():
        for role in ROLES:
            acts.append(Button(f"{label.capitalize()}: {role}",
                               f"!serve {act} {role}", "", can_do(
                                   player.gender, act, role, player.body)))
    sections = [Panel("Acts", (), tuple(acts))]
    if shift.mode != "sub" and not client.player:
        sections.append(Panel("Finish", (), tuple(
            Button(label, f"!serve {word}") for word, label in FINISHERS)))
    return Panel(title, (f"{client.name} ({client.gender}) "
                         f"{wish_text(client)}",), tuple(buttons),
                 tuple(sections), timer=services.timer_text(player),
                 bars=(work_ui.round_bar(services, shift),), choices=(
                     Choice("tone", "Tone", (("", "auto"),
                                             *((t, t) for t in TONES))),
                     Choice("kick", "Ballbusting kick",
                            (("", "random"), ("front", "front"),
                             ("back", "back")))))


def panel(services, player:Player) -> Panel:
    town = town_of(player)
    lines = (localize_text(PLACES["brothel"], town),
             localize_text(f"Owner {OWNERS['brothel']} keeps "
                           f"{round(BROTHEL_CUT * 100)}%", town))
    shift = services.shifts.get(player.name)
    if (shift is not None and shift.building == "brothel"
            and shift.job.interactive and shift.client is not None):
        return Panel("🌹 Brothel", lines, (), (
            client_panel(services, player, shift),))
    rent = Panel("For yourself", (), tuple(
        Button(f"{kind.capitalize()} ({price} g)", f"!book {kind}", "",
               player.gold >= price) for kind, price in RENT_PRICES.items()))
    return Panel("🌹 Brothel", lines, (), work_ui.compact(
        work_ui.shift_panel(services, player, shift, "brothel"),
        work_ui.workers_panel(services, player, "brothel"),
        work_ui.jobs_panel("brothel", player), rent))
