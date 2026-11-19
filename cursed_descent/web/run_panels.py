from typing import Callable

from ..config import (
    DAIRY_JOBS, FISHER_ROD_PRICE, GRILL_SPECIAL_PRICE, HUNG_GENDERS,
    PRIVY_ATTEND_PAY, PRIVY_FIXTURE_PAY, PRIVY_TIP, PRIVY_TOLL, PRIVY_URINAL,
)
from ..content import ITEMS
from ..events.common import self_price
from ..locations.brewery.location import fresh_price, self_total
from ..locations.mage_tower import enchantments
from ..locations.mage_tower.content import (
    ENCHANT_BONUS, ENCHANT_PRICE, PART_WORDS, POTION_MARKUP, POTIONS,
    REAL_PRICE, REAL_SEX_PRICE, SLEEP_PRICE, SUPER_BONUS, SUPER_PRICE,
)
from ..locations.mage_tower.location import implant_parts
from ..locations.wedding.npc import WEDDING_GUESTS
from ..locations.shop.location import base_price, buy_price, item_summary
from ..models import Player
from ..settings import fill
from ..town_buildings import shop_ui
from ..towns import town_of
from ..towns.localize import localize_text
from ..view import Button, Panel, Row


VENUE_TITLES = {"butcher_shop": "🔪 <<npc.hamhock_first>>'s Butchery",
                "farm": "🐖 <<npc.old_trotter_first>>'s Farm",
                "brewery": "🍺 <<npc.astrid_last>>'s Taproom",
                "sweatery": "💦 The Sweatery",
                "smokery": "🔥 The Northern Smokery",
                "mage_tower": "🧙 The Mage's Tower",
                "wardrobe": "🚪 The Living Wardrobe",
                "throne": "🪑 The Corruption Throne",
                "glory_hole": "🕳 The Glory Hole",
                "wedding": "💒 A Strange Wedding",
                "fisher": "🎣 <<npc.old_gorm_first>>'s Jetty",
                "grill": "🍗 <<npc.gul_first>>'s Grill",
                "dairy": "🥛 Crone Creamery",
                "privy": "🚽 Public Privy",
                "maid": "🧹 Head Maid <<npc.constance_first>>"}
CARAVAN_TITLE = "🐎 The Caravaneer"
DRAINER_TITLE = "🧪 The Drainer"
SHIFT_WORDS = ("rent", "work", "quit", "sweat", "smoke", "endure", "beg")
EXAMINE = Button("🔍 Examine", "!examine")
DEPART = Button("Leave", "!depart")
OUTSIDE = (Button("Enter", "!enter"), Button("Examine", "!examine"))
DAIRY_LABELS = {"milk": "Milk the herd", "feed": "Feed the herd",
                "cow": "Cow shift", "bull": "Bull shift"}


def gold_line(player:Player) -> str:
    return f"💰 {player.name}: {player.gold} gold"


def stock_panel(title:str, stock:list, player:Player,
                note:Callable[[int], str]=lambda nr: "",
                counts:bool=False) -> Panel:
    rows = []
    for nr, item_id, count in stock:
        price = buy_price(item_id, player)
        stack = f"{count}× " if counts and count > 1 else ""
        rows.append(Row(f"{stack}{item_summary(item_id)}{note(nr)}", (
            Button(f"Buy {price}", f"!buy {nr}", "", player.gold >= price),)))
    return Panel(title, () if rows else ("sold out",), rows=tuple(rows))


def shift_panel(events) -> Panel | None:
    actions = [option for option in events.available()
               if option.split()[0] in SHIFT_WORDS]
    if not actions:
        return None
    return Panel("Work", buttons=tuple(
        Button(option.capitalize(), f"!{option}") for option in actions))


def compact(*parts:Panel | None) -> tuple[Panel, ...]:
    return tuple(part for part in parts if part is not None)


def venue_panel(title:str, player:Player, lines:tuple[str, ...]=(),
                buttons:tuple[Button, ...]=(),
                sections:tuple[Panel, ...]=()) -> Panel:
    return Panel(localize_text(title, town_of(player)),
                 (gold_line(player), *lines), buttons, sections)


def generic_panel(events, player:Player, venue:str) -> Panel:
    lines: tuple[str, ...] = ()
    if venue == "smokery" and not events.outside():
        pay = events.smoke_pay()
        lines = (f"Smoking: pays {pay} gold up front (+{round(pay * 2)} if "
                 f"you survive), 5 cycles, about 1 in 10 survives",)
    if venue == "sweatery":
        lines = (*lines, *events.sweat_status())
    if venue == "smokery":
        lines = (*lines, *events.smoke_status())
    buttons = [*(OUTSIDE if events.outside() else ()), DEPART]
    if venue not in ("sweatery", "smokery"):
        buttons.append(Button("Sell yourself", "!sellself"))
    return venue_panel(VENUE_TITLES[venue], player, lines, tuple(buttons),
                       compact(shift_panel(events),
                               stock_panel("For sale", events.venue_stock(),
                                           player)))


def boutique_panel(events, player:Player) -> Panel:
    buttons = (*(OUTSIDE if events.outside() else ()),
               Button("Leave the boutique", "!depart"),
               Button(f"Sell yourself (+{self_price(player)} gold)",
                      "!sellself"))
    return Panel(fill("🧵 <<boutique.shop>>"), (gold_line(player),), buttons,
                 compact(shift_panel(events),
                         stock_panel("Couture for sale",
                                     events.boutique_groups(), player,
                                     counts=True),
                         shop_ui.sell_panel(player)))


def brewery_panel(events, player:Player) -> Panel:
    inside = events.brewery_inside()
    intro = ("Inside: heal and restore mana, sell your items – or sell "
             "yourself. No time limit." if inside else
             "You are standing in front of the door. Nothing happens until "
             "you decide. No time limit.")
    lines = (intro, events.brewery_special_text())
    title = localize_text("🍺 <<npc.astrid_last>>'s Taproom", town_of(player))
    if not inside:
        return Panel(title, (gold_line(player), *lines), (
            Button("Examine", "!examine"), Button("Enter", "!enter"),
            Button("Pass", "!pass")))
    price = fresh_price(player)
    left = events.fresh_left()
    buttons = [Button("Examine", "!examine"),
               Button(localize_text("Talk to <<npc.astrid_first>>",
                                    town_of(player)), "!shop"),
               DEPART,
               Button(f"Sell yourself (+{self_total(player)} gold)",
                      "!sellself"),
               Button(f"Fresh mug from the tap ({price} gold, random, "
                      f"{left} left)", "!fresh", "",
                      player.gold >= price and left > 0)]
    if "tap" in events.available():
        buttons.append(Button("Drink from the tap", "!tap"))
    sections = compact(shift_panel(events),
                       stock_panel("For sale", events.brewery_stock(),
                                   player, events.brewery_note),
                       shop_ui.sell_panel(player))
    return Panel(title, (gold_line(player), *lines), tuple(buttons),
                 sections)


def mage_panel(events, player:Player) -> Panel:
    title = "🧙 The Mage's Tower"
    if events.outside():
        return venue_panel(title, player, (), (*OUTSIDE, Button(
            "Pass", "!pass")))
    spent = "enchant" in events.event["used"]
    lines = (f"Pick one item per visit. Enchant: all values "
             f"+{ENCHANT_BONUS} for {ENCHANT_PRICE} gold, but the magic "
             f"takes a share. Super enchant: all values +{SUPER_BONUS} for "
             f"{SUPER_PRICE} gold and one time with him, no share.",)
    sections = []
    if spent:
        lines += ("The mage has worked his magic for today.",)
    else:
        for number, (where, item_id) in enumerate(
                enchantments.eligible(player), 1):
            sections.append(Panel(f"{ITEMS[item_id]['name']} ({where})",
                                  buttons=(
                Button(f"Enchant +{ENCHANT_BONUS} ({ENCHANT_PRICE} g)",
                       f"!upgrade {number}"),
                Button(f"Super enchant +{SUPER_BONUS} ({SUPER_PRICE} g and "
                       f"sex with him)", f"!super {number}"))))
    parts = implant_parts(player)
    if parts:
        sections.append(Panel("Make implants real", buttons=tuple(
            button for part in parts for button in (
                Button(f"Real {PART_WORDS[part]} ({REAL_PRICE} g)",
                       f"!real {part}"),
                Button(f"Real {PART_WORDS[part]} ({REAL_SEX_PRICE} g and "
                       f"sex with him)", f"!realsex {part}")))))
    shop = [Button(f"{ITEMS[item_id]['name']} "
                   f"({base_price(item_id) * POTION_MARKUP} g)",
                   f"!potion {number}")
            for number, item_id in enumerate(POTIONS, 1)]
    if "sleep" not in events.event["used"]:
        shop.append(Button(f"Sleep in the old bed ({SLEEP_PRICE} g)",
                           "!sleep"))
    sections.append(Panel("Potions and bed", buttons=tuple(shop)))
    return venue_panel(title, player, lines, (DEPART,), tuple(sections))


def simple_buttons(events, player:Player, venue:str) -> tuple[Button, ...]:
    available = events.available()
    if venue == "wardrobe":
        return (Button("Open the doors", "!open"), EXAMINE,
                Button("Pass", "!depart"))
    if venue == "throne":
        take = ((Button("Take what lies at its foot", "!take"),)
                if "take" in available else ())
        return (Button("Sit down", "!claim"), *take, EXAMINE,
                Button("Pass", "!depart"))
    if venue == "glory_hole":
        use = ((Button("Use the hole", "!thrust"),)
               if "thrust" in available else ())
        return (*use, EXAMINE, Button("Pass", "!depart"))
    if venue == "wedding" and not events.outside():
        labels = (("eat", "Eat at the long table"),
                  ("congratulate", "Congratulate the couple"),
                  ("dance", "Watch the first dance"),
                  ("night", "Stay for the night"))
        return (*(Button(label, f"!{word}") for word, label in labels
                  if word in available), EXAMINE, DEPART)
    return ()


def wedding_panel(events, player:Player) -> Panel:
    title = VENUE_TITLES["wedding"]
    if events.outside():
        return venue_panel(title, player, (), (*OUTSIDE, Button(
            "Pass", "!pass")))
    guests = []
    for guest in WEDDING_GUESTS:
        name = guest.first_name
        guests.append(Panel(f"{name} – {guest.role}", (), (
            Button("🔍 Examine", f"!examine {name}"),
            Button("Talk", f"!talk {name}"),
            *(Button(topic.capitalize(), f"!talk {name} {topic}")
              for topic in ("work", "town", "self")))))
    return venue_panel(title, player, (), simple_buttons(
        events, player, "wedding"), (Panel("Guests", (), (), tuple(guests)),))


def fisher_buttons(events, player:Player) -> tuple[Button, ...]:
    available = events.available()
    buttons = []
    if "cast" in available:
        buttons.append(Button(f"Rent a rod ({FISHER_ROD_PRICE} gold)",
                              "!cast"))
    for option in available:
        if option.startswith("bait "):
            name = option.partition(" ")[2]
            buttons.append(Button(f"Bait: {name}", f"!bait {name}"))
    if "lie" in available:
        buttons.append(Button(localize_text("Lie down with "
                                            "<<npc.old_gorm_first>>",
                                            town_of(player)), "!lie"))
    return (*buttons, EXAMINE, DEPART)


def grill_panel(events, player:Player) -> Panel:
    special = player.gold >= GRILL_SPECIAL_PRICE
    return venue_panel(VENUE_TITLES["grill"], player, (), (
        Button(f"Today's special ({GRILL_SPECIAL_PRICE} g)", "!special", "",
               special),
        Button("Ask about the meat", "!ask"),
        Button("Grumble about the food", "!grumble"), EXAMINE, DEPART),
        (stock_panel("Menu", events.venue_stock(), player),))


def privy_panel(events, player:Player) -> Panel:
    title = VENUE_TITLES["privy"]
    if events.outside():
        return venue_panel(title, player, (), (*OUTSIDE, Button(
            "Pass", "!pass")))
    rows = [(f"Use: Stall ({PRIVY_TOLL} g)", "!stall")]
    if player.gender in HUNG_GENDERS:
        rows.append((f"Use: Urinal ({PRIVY_URINAL} g)", "!urinal"))
    rows += [("Use: Basin", "!wash"), ("Read the walls", "!read"),
             ("Knock on stall", "!knock"), ("Chat with Hedwig", "!ask"),
             (f"Tip Hedwig ({PRIVY_TIP} g)", "!tip"),
             (f"Work: Attendant shift ({PRIVY_ATTEND_PAY} g)",
              "!stint attend"),
             (f"Work: Fixture shift ({PRIVY_FIXTURE_PAY} g)",
              "!stint fixture"),
             ("Grumble", "!grumble"), ("🔍 Examine", "!examine")]
    return venue_panel(title, player, (), (
        *(Button(label, command) for label, command in rows), DEPART))


def dairy_panel(events, player:Player) -> Panel:
    title = VENUE_TITLES["dairy"]
    if events.outside():
        return venue_panel(title, player, (), (*OUTSIDE, Button(
            "Pass", "!pass")))
    shifts = Panel("Shifts", buttons=tuple(
        Button(f"{label} ({DAIRY_JOBS[job]['pay']} g/round)",
               f"!stint {job}") for job, label in DAIRY_LABELS.items()))
    return venue_panel(title, player, (), (
        Button("Take the tour", "!tour"), Button("Sell yourself",
                                                 "!sellself"),
        EXAMINE, DEPART),
        (stock_panel("Shelf", events.venue_stock(), player), shifts))


def maid_panel(events, player:Player) -> Panel:
    available = events.available()
    buttons = [Button(label, f"!{word}") for word, label in (
        ("volunteer", "Volunteer (100 smacks)"),
        ("smack", "Smack (next 10)"), ("history", "📖 History"))
        if word in available]
    buttons.append(EXAMINE)
    if "depart" in available:
        buttons.append(DEPART)
    return Panel(localize_text(VENUE_TITLES["maid"], town_of(player)),
                 (player.name,), tuple(buttons))


def caravan_panel(events, player:Player) -> Panel:
    state = events.caravan_state()
    mine = state["votes"].get(player.name)
    tally = ", ".join(f"{name}: {choice or 'no trade'}"
                      for name, choice in state["votes"].items())
    lines = [f"🎁 The ware: {item_summary(state['ware'])}",
             "One lady for the team, one rare item for you. Every member "
             "votes, the majority decides."]
    lines.append(f"Votes: {tally}" if tally else "Nobody has voted yet.")
    if state["missing"]:
        lines.append("Still to vote: " + ", ".join(state["missing"]))
    if mine is not None:
        lines.append(f"Your vote: {mine or 'no trade'} (you can change it)")
    buttons = [Button(f"Offer {name}", f"!offer {name}")
               for name in state["candidates"]]
    buttons += [Button("No trade", "!depart"), EXAMINE]
    return Panel(CARAVAN_TITLE, (gold_line(player), *lines),
                 tuple(buttons))


def drainer_panel(events, player:Player) -> Panel:
    state = events.drainer_state()
    restoring = state["mode"] == "restore"
    mine = state["votes"].get(player.name)
    names = {"!fight": "fight", "": "leave it"}
    tally = ", ".join(f"{name}: {names.get(choice, choice)}"
                      for name, choice in state["votes"].items())
    if restoring:
        lines = [f"🍶 A bottle survived: {state['bottle']}. Hand it to "
                 "one of you or leave it. Every member votes; if several "
                 "want it, the dice decide."]
    else:
        lines = ["One of you steps forward and is drained for good "
                 "(chest, then curves, then manhood, then balls: the first "
                 "that is left), or you fight him. Every member votes, the "
                 "majority decides.", *state["shelf"]]
    lines.append(f"Votes: {tally}" if tally else "Nobody has voted yet.")
    if state["missing"]:
        lines.append("Still to vote: " + ", ".join(state["missing"]))
    if mine is not None:
        lines.append(f"Your vote: {names.get(mine, mine)} "
                     "(you can change it)")
    if restoring:
        buttons = [Button(f"Give to {name}", f"!give {name}")
                   for name in state["targets"]]
        buttons += [Button("Leave it", "!depart")]
    else:
        buttons = [Button(f"Sacrifice {name}", f"!sacrifice {name}")
                   for name in state["targets"]]
        buttons += [Button("Fight him", "!challenge")]
    buttons.append(EXAMINE)
    return Panel(DRAINER_TITLE, (gold_line(player), *lines),
                 tuple(buttons))


def run_shop_panel(controller, player:Player) -> Panel | None:
    session = controller.session
    events = session.events
    venue = (events.event.get("phase", "")
             if session.state == "event" else "")
    if venue == "caravan":
        return caravan_panel(events, player)
    if venue == "drainer":
        return drainer_panel(events, player)
    if venue not in VENUE_TITLES:
        return boutique_panel(events, player) if events.boutique_active() \
            else None
    builders = {"brewery": brewery_panel, "mage_tower": mage_panel,
                "grill": grill_panel, "privy": privy_panel,
                "dairy": dairy_panel, "maid": maid_panel}
    if venue in builders:
        return builders[venue](events, player)
    if venue == "fisher":
        return venue_panel(VENUE_TITLES[venue], player, (),
                           fisher_buttons(events, player))
    if venue == "wedding":
        return wedding_panel(events, player)
    simple = simple_buttons(events, player, venue)
    if simple:
        return venue_panel(VENUE_TITLES[venue], player, (), simple)
    return generic_panel(events, player, venue)
