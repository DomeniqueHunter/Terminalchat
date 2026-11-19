from ...config import (
    BROTHEL_VISIT_PRICE, TAVERN_VISIT_PRICE, WORK_TICK_SECONDS,
)
from ...models import Player
from ...view import Bar, Button, Panel
from ..dishes import MENUS
from ..brothel.visitors import USABLE
from ..services import ransom_price
from .jobs import jobs_for
from .moves import moves_for


def job_choices(building:str, job) -> list[tuple[str, str]]:
    if job.key == "milk":
        return [("Milk: barrel", "milk barrel"),
                ("Milk: counter", "milk counter")]
    if building == "brothel" and job.key == "whore":
        return [("Whore (mixed)", "whore"), ("Whore: domina", "whore domina"),
                ("Whore: sub", "whore sub")]
    return [(job.title, job.key)]


def jobs_panel(building:str, player:Player) -> Panel:
    jobs = jobs_for(building, player)
    lines = tuple(f"{job.title}: {job.sessions}× ~{job.base}+ g. {job.blurb}"
                  for job in jobs)
    buttons = tuple(Button(label, f"!job {building} {words}")
                    for job in jobs for label, words in
                    job_choices(building, job))
    return Panel("Jobs", lines, buttons)


def orders_panel(building:str, player:Player) -> Panel:
    buttons = []
    for number, (name, price, _) in enumerate(MENUS[building].values(), 1):
        enough = player.gold >= price
        buttons.append(Button(f"Eat {name} ({price} g)",
                              f"!order {building} {number}", "", enough))
        buttons.append(Button("Take", f"!order {building} {number} take",
                              "", enough))
    return Panel("Eat & drink", (), tuple(buttons))


def round_bar(services, shift) -> Bar:
    left = WORK_TICK_SECONDS - min(
        WORK_TICK_SECONDS, max(0.0, shift.due - services.now))
    return Bar("round", "Round", left, WORK_TICK_SECONDS)


def workers_panel(services, player:Player, building:str) -> Panel | None:
    workers = [name for name, other in services.shifts.items()
               if other.building == building and other.job.key in USABLE
               and name != player.name]
    if not workers:
        return None
    price = (BROTHEL_VISIT_PRICE if building == "brothel"
             else TAVERN_VISIT_PRICE)
    return Panel("Workers on shift", (), tuple(
        Button(f"Visit {name} – {services.shifts[name].job.title} "
               f"({price} g)", f"!visit {name}", "", player.gold >= price)
        for name in workers))


def shift_panel(services, player:Player, shift, building:str) -> Panel | None:
    if (shift is None or shift.building != building
            or shift.job.interactive):
        return None
    buttons = [Button(name.capitalize(), f"!move {name}")
               for name in moves_for(shift.job.key, player)]
    buttons += [Button("Work now (next round)", "!round"),
                Button("Leave shift early", "!quit")]
    return Panel(f"On shift: {shift.job.title}", (), tuple(buttons),
                 timer=services.timer_text(player), bars=(
                     round_bar(services, shift),
                     Bar("shift", "Shift", shift.job.sessions - shift.left,
                         shift.job.sessions)))


def ransom_panel(services, player:Player, kind:str,
                 title:str) -> Panel | None:
    held = [npc for npc in services.repository.npc_players()
            if npc.npc == kind]
    if not held:
        return None
    return Panel(f"{title} – ransom", (), tuple(
        Button(f"Ransom {npc.full_name} (Lv {npc.level}) – "
               f"{ransom_price(npc)} g", f"!ransom {npc.name}", "",
               player.gold >= ransom_price(npc)) for npc in held))


def examine_buttons(*pairs:tuple[str, str]) -> tuple[Button, ...]:
    return tuple(Button(f"🔍 {label}", f"!examine {target}")
                 for label, target in pairs)


def compact(*panels:Panel | None) -> tuple[Panel, ...]:
    return tuple(panel for panel in panels if panel is not None)
