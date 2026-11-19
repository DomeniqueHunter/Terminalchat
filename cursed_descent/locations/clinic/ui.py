from ...models import Player
from ...towns import town_of
from ...towns.localize import localize_text
from ...view import Button, Panel, Row
from .location import clinic_options


BODY_COMMANDS = ("bust", "taller", "shorter")


def group_of(command:str) -> str:
    if command == "terminate":
        return "Care"
    if command.startswith("build "):
        return "Build"
    if command.split()[0] in BODY_COMMANDS:
        return "Body"
    return "Enhancements"


def panel(services, player:Player) -> Panel:
    in_run = services.in_run(player)
    groups: dict[str, list[Row]] = {"Care": [], "Body": [], "Build": [],
                                    "Enhancements": []}
    for command, label, price in clinic_options(player):
        groups[group_of(command)].append(Row(label, (Button(
            f"{price} g", f"!mod {command}", "",
            not in_run and player.gold >= price),)))
    title = localize_text("💉 Dr. <<npc.vane_first>>'s Flesh Atelier",
                          town_of(player))
    lines = (f"💰 {player.name}: {player.gold} gold",
             *(("Closed during a run.",) if in_run else ()))
    return Panel(title, lines, (), tuple(
        Panel(name, rows=tuple(rows)) for name, rows in groups.items()
        if rows))
