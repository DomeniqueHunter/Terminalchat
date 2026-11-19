from ...config import PASS_BRIBE_COST, PASS_FEE
from ...models import Player
from ...towns import START_TOWN, TOWNS, destinations, fare_between, town_of
from ...view import Button, Panel
from .rail_pass import has_pass, keeper_name


def panel(services, player:Player) -> Panel:
    here = town_of(player)
    buttons = []
    for key in destinations(player):
        goal = TOWNS[key]
        fare = fare_between(here.key, key)
        buttons.append(Button(f"{goal.name} ({goal.race}) – {fare} gold",
                              f"!travel {goal.name}"))
    sections = ()
    if here.key != START_TOWN and not has_pass(player, here.key):
        keeper = keeper_name(here.key)
        sections = (Panel("Rail pass", (
            f"No rail pass for {here.name} yet. Win over {keeper} to open "
            f"the line from anywhere.",), (
                Button(f"Talk to {keeper}", "!ticket talk"),
                Button(f"Pay ({PASS_FEE} gold)", "!ticket pay"),
                Button(f"Bribe ({PASS_BRIBE_COST} gold)", "!ticket bribe"),
                Button(f"Sleep with {keeper}", "!ticket sleep"))),)
    return Panel(f"🚉 {here.name} station", (
        "Pick a destination. The fare is paid in gold; the trip costs no "
        "dungeon round.",), tuple(buttons), sections)
