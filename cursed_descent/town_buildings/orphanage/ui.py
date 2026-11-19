from ...models import Player
from ...view import Button, Panel
from . import content, rules


def panel(services, player:Player) -> Panel:
    data = rules.record(player)
    points = data["points"]
    lines = (content.TEXTS["points"].format(
        points=points, title=rules.title_of(points)),
        "Gold counts 1 point per 20, food by its worth, milk and cream "
        "2 points, giving on the spot 3.")
    buttons = [Button("Give all food", "!donate all food")]
    if rules.can_give(player, "milk"):
        buttons.append(Button("Give milk", "!donate milk"))
    if rules.can_give(player, "cum"):
        buttons.append(Button("Give cream", "!donate cum"))
    buttons.append(Button("Donate 100 gold", "!donate gold 100"))
    return Panel(f"🏮 {content.TITLE}", lines, tuple(buttons))
