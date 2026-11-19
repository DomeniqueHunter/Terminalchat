from ....config import (
    CAFE_CUT, CAFE_TICKET, STAT_NAMES, STAT_SHORT,
)
from ....content import ITEMS
from ....formulas import effective_stat, max_hp, max_mana
from ....models import Player
from ... import town_of
from ...localize import localize_text
from ....view import Bar, Button, Panel
from ....town_buildings.work.content import OWNERS, PLACES
from ....town_buildings.work import ui as work_ui
from .seat import may_sit
from .stools import blurb as blurb_stool
from .service import sitting_on


SEAT_ACTIONS = (("Wait / endure", "wait"), ("Hold breath", "breath"),
                ("Pat her rear", "pat"), ("Struggle free", "struggle"),
                ("Kiss her rear", "kiss"), ("Lick her ass", "lick"),
                ("Encourage", "encourage"), ("Give up", "giveup"))
RIDER_ACTIONS = (("Stay seated", "stay"),
                 ("Shift weight (more pressure)", "lean"),
                 ("Raise for a moment (seat recovers)", "raise"),
                 ("Rise (spare him)", "rise"),
                 ("Clench cheeks (torment)", "clench"),
                 ("Wiggle ass (torment)", "wiggle"),
                 ("Swallow him whole (anal vore)", "swallow"))


def seat_stats_line(player:Player) -> str:
    parts = [f"{STAT_SHORT[stat]} {effective_stat(player, stat)}"
             for stat in STAT_NAMES]
    return (" | ".join(parts) + f" | Lv {player.level} | HP "
            f"{max_hp(player)} | Mana {max_mana(player)}")


def seat_panel(services, player:Player, shift) -> Panel:
    guest = shift.client
    if guest is None:
        guest_line = "Nobody sits on you yet."
    else:
        guest_line = (f"{guest.name}: {guest.weight} kg, {guest.butt} cm of "
                      f"rear" + (" – a lady of your party!" if guest.rider
                                 else ""))
    buttons = []
    bars = ()
    if guest is not None:
        bars = (Bar("air", "🫁 Air", shift.air, 100),)
        buttons += work_ui.examine_buttons((f"Examine {guest.name}",
                                            guest.name))
        if not guest.rider:
            buttons += [Button("★ Make regular", "!regular"),
                        Button("Ask for her address", "!regular ask")]
    buttons += work_ui.examine_buttons(("Examine Madame Bertha", "bertha"))
    buttons += [Button(label, f"!{word}") for label, word in SEAT_ACTIONS]
    buttons.append(Button("Hold (answer now)", "!hold", "",
                          guest is not None))
    buttons.append(Button("Quit (safeword)", "!safeword", "",
                          not (guest is not None and (
                              guest.rider or shift.mode == "home"))))
    return Panel(f"Seat – {shift.left} left, {shift.earned} g earned",
                 (seat_stats_line(player), guest_line), tuple(buttons),
                 timer=services.timer_text(player), bars=bars)


def rider_panel(services, player:Player, seat:str) -> Panel:
    buttons = list(work_ui.examine_buttons((f"Examine {seat}", seat)))
    buttons += [Button(label, f"!{word}") for label, word in RIDER_ACTIONS]
    return Panel(f"Sitting on {seat}", (), tuple(buttons),
                 timer=services.timer_text(player),
                 sections=(work_ui.orders_panel("cafe", player),))


def ladies_panel(services, player:Player) -> Panel:
    buttons = []
    lines = []
    for name, other in services.shifts.items():
        if other.building == "cafe" and other.job.key == "seat":
            buttons.append(Button(f"Sit on {name} (your character)",
                                  f"!sit {name}", "",
                                  other.client is None))
    for number, stool in enumerate(services.stools, 1):
        lines.append(f"{number}. {blurb_stool(stool)}")
        buttons.append(Button(f"🔍 {stool.name}", f"!examine {stool.name}"))
        buttons.append(Button(f"Sit {number} ({CAFE_TICKET} g)",
                              f"!sit {number}", "",
                              player.gold >= CAFE_TICKET))
    if player.name in services.complaints:
        buttons.append(Button("Complain to Bertha (refund)", "!complain"))
    if player.name in services.claims:
        buttons.append(Button("Salvage the ruined stool", "!salvage"))
    buttons.append(Button("Look around (new faces)", "!cafe"))
    return Panel("Take a seat", tuple(lines), tuple(buttons))


def house_panel(services, player:Player) -> Panel:
    buttons = []
    for number, entry in enumerate(services.cafe.stock(), 1):
        item = ITEMS[entry["id"]]
        buttons.append(Button(f"{item['name']} ({item['price']} g)",
                              f"!cafe buy {number}", "",
                              player.gold >= item["price"]))
    return Panel("From the house", (), tuple(buttons))


def panel(services, player:Player) -> Panel:
    town = town_of(player)
    lines = (localize_text(PLACES["cafe"], town),
             localize_text(f"Owner {OWNERS['cafe']} keeps "
                           f"{round(CAFE_CUT * 100)}%", town))
    shift = services.shifts.get(player.name)
    if (shift is not None and shift.building == "cafe"
            and shift.job.key == "seat"):
        return Panel("🍰 Café", lines, (), (seat_panel(services, player,
                                                       shift),))
    on_shift = work_ui.shift_panel(services, player, shift, "cafe")
    seat = sitting_on(services, player)
    if seat:
        return Panel("🍰 Café", lines, (), work_ui.compact(
            on_shift, rider_panel(services, player, seat)))
    look = Panel("Look at", (), work_ui.examine_buttons(
        ("Examine Madame Bertha", "bertha"),
        *((f"Examine {npc.full_name}", npc.name)
          for npc in services.repository.npc_players()
          if npc.npc == "furniture")))
    return Panel("🍰 Café", lines, (), work_ui.compact(
        on_shift, look,
        work_ui.ransom_panel(services, player, "furniture",
                             "Stools of the house"),
        work_ui.jobs_panel("cafe", player),
        work_ui.orders_panel("cafe", player),
        ladies_panel(services, player) if may_sit(player) else None,
        house_panel(services, player)))
