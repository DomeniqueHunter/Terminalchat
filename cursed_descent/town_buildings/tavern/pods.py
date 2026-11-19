from ...config import POD_SELL_FACTOR
from ...content import ITEMS
from ...models import Message, Player
from ...view import Button, Panel


def is_pod(item_id:str) -> bool:
    return bool(ITEMS.get(item_id, {}).get("pod"))


def price_of(item_id:str) -> int:
    return round(ITEMS[item_id]["price"] * POD_SELL_FACTOR)


def pods_of(player:Player) -> list[tuple[int, str]]:
    return [(number, item) for number, item in
            enumerate(player.inventory, 1) if is_pod(item)]


def pod_panel(player:Player) -> Panel | None:
    pods = pods_of(player)
    if not pods:
        return None
    buttons = [Button(f"{ITEMS[item]['name']} – {price_of(item)} g",
                      f"!sellpods {number}") for number, item in pods]
    if len(pods) > 1:
        buttons.append(Button("Sell all pods", "!sellpods all"))
    return Panel("Pods wanted", (
        "The regulars pay gladly, and well, for a fresh pod.",), tuple(buttons))


def sell(player:Player, args:list[str]) -> list[Message]:
    pods = pods_of(player)
    if not pods:
        return [Message("You carry no pods. The tavern pays well for "
                        "them.", player.name)]
    if args and args[0].isdigit():
        chosen = [(number, item) for number, item in pods
                  if number == int(args[0])]
        if not chosen:
            return [Message("That is not a pod.", player.name)]
    elif args and args[0] == "all":
        chosen = pods
    else:
        return [Message("Usage: sellpods <nr|all>", player.name)]
    total = sum(price_of(item) for _, item in chosen)
    names = ", ".join(ITEMS[item]["name"] for _, item in chosen)
    for number, _ in sorted(chosen, reverse=True):
        player.inventory.pop(number - 1)
    player.gold += total
    return [Message(f"🍺 The patrons crowd around. {names} changes hands "
                    f"for {total} gold, and the whole taproom cheers. "
                    f"💰 Gold: {player.gold}", player.name)]
