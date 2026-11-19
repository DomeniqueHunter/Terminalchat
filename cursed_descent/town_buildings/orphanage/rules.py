from ...models import Message, Player
from ...needs import item_needs
from . import content


def private(text:str, player:Player) -> list[Message]:
    return [Message(text, player.name)]


def record(player:Player) -> dict:
    return player.profile.setdefault("orphanage", {"points": 0, "given": {}})


def title_of(points:int) -> str:
    return next((name for need, name in content.LEVELS if points >= need),
                "Visitor")


def level_of(points:int) -> int:
    return sum(1 for need, _ in content.LEVELS if points >= need)


def food_points(item_id:str) -> int:
    needs = item_needs(item_id)
    value = -sum(amount for amount in needs.values() if amount < 0)
    return max(1, value // 10)


def is_food(item_id:str) -> bool:
    return any(amount < 0 for amount in item_needs(item_id).values())


def add_points(player:Player, amount:int) -> list[str]:
    data = record(player)
    before = title_of(data["points"])
    data["points"] += amount
    lines = []
    after = title_of(data["points"])
    if after != before:
        lines.append(content.TEXTS["level"].format(title=after))
    if level_of(data["points"]) >= content.BUFF_LEVEL:
        from ...formulas import apply_buff
        if content.BUFF not in player.buffs:
            apply_buff(player, content.BUFF)
    lines.append(content.TEXTS["points"].format(
        points=data["points"], title=title_of(data["points"])))
    return lines


def donate_gold(player:Player, amount:int) -> list[Message]:
    amount = min(amount, player.gold)
    points = amount // content.GOLD_PER_POINT
    if points < 1:
        return private(content.TEXTS["gold_small"], player)
    amount = points * content.GOLD_PER_POINT
    player.gold -= amount
    lines = [content.TEXTS["gold"].format(amount=amount)]
    return private("\n".join(lines + add_points(player, points)), player)


def donate_item(player:Player, reference:str) -> list[Message]:
    from ...content import ITEMS
    from ...locations.shop.location import find_index
    index = find_index(player.inventory, reference)
    if index is None:
        return private(content.TEXTS["none"], player)
    item_id = player.inventory.pop(index)
    name = ITEMS[item_id]["name"]
    if item_id in content.KIND_ITEMS.values():
        points = content.KIND_POINTS["milk" if item_id == "milk_bottle"
                                     else "cum"]
        text = content.TEXTS["vial"].format(item=name)
    elif is_food(item_id):
        points = food_points(item_id)
        text = content.TEXTS["food"].format(item=name)
    else:
        player.inventory.insert(index, item_id)
        return private(content.TEXTS["none"], player)
    return private("\n".join([text] + add_points(player, points)), player)


def donate_all_food(player:Player) -> list[Message]:
    kept, points, count = [], 0, 0
    for item_id in player.inventory:
        if is_food(item_id) and item_id not in content.KIND_ITEMS.values():
            points += food_points(item_id)
            count += 1
        else:
            kept.append(item_id)
    if not count:
        return private(content.TEXTS["nofood"], player)
    player.inventory = kept
    lines = [content.TEXTS["food_all"].format(count=count)]
    return private("\n".join(lines + add_points(player, points)), player)


def can_give(player:Player, kind:str) -> bool:
    body = player.body
    if kind == "milk":
        return body.get("bust", 0) >= content.MIN_BUST
    from ...config import HUNG_GENDERS
    return (player.gender in HUNG_GENDERS
            and body.get("endowment", 15) >= content.MIN_ENDOWMENT
            and body.get("balls", 5) >= content.MIN_BALLS)


def give_on_the_spot(player:Player, kind:str, day:int) -> list[Message]:
    if not can_give(player, kind):
        return private(content.TEXTS[f"{kind}_no"], player)
    given = record(player).setdefault("given", {})
    if given.get(kind) == day:
        return private(content.TEXTS["wait"], player)
    given[kind] = day
    lines = [content.TEXTS[kind]]
    return private("\n".join(lines + add_points(
        player, content.GIVE_POINTS[kind])), player)


def donate(services, player:Player, args:list[str]) -> list[Message]:
    if services.in_run(player):
        return private(content.TEXTS["closed"], player)
    words = [word.lower() for word in args]
    if not words:
        return private(content.HELP, player)
    if words[0] == "gold" and len(words) > 1 and words[1].isdigit():
        found = donate_gold(player, int(words[1]))
    elif words[0] == "all" and words[1:2] == ["food"]:
        found = donate_all_food(player)
    elif words[0] in content.GIVE_POINTS:
        found = give_on_the_spot(player, words[0], services.world.day)
    else:
        found = donate_item(player, " ".join(args))
    services.repository.save(player)
    return found
