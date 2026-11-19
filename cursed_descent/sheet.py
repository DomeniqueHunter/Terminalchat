from .body import bust_cm, bust_label
from .config import HOUSE_TYPES, HUNG_GENDERS
from .models import Player


def anatomy_lines(player:Player) -> list[str]:
    body = player.body
    lines = [f"Build: {body['height']} cm, {body['weight']} kg, "
             f"{body['build']}, muscle {body.get('muscle', '-')}, "
             f"butt {body.get('butt', '-')} cm"]
    cc = body.get("bust", 0)
    lines.append(f"Bust: {bust_label(cc)} ({round(cc)} cc, "
                 f"{bust_cm(body)} cm)" if cc > 0 else "Bust: none")
    if player.gender in HUNG_GENDERS:
        lines.append(f"Cock: {body.get('endowment', '-')} cm long, "
                     f"{body.get('girth', '-')} cm around, "
                     f"{body.get('endowment_shape', 'Human')} | "
                     f"Balls: {body.get('balls', '-')} cm")
    else:
        lines.append("Cock: none")
    return lines


def home_lines(player:Player) -> list[str]:
    from .houses import home_of, lodging_of
    lines = []
    for town in player.profile.get("houses", {}):
        house = home_of(player, town)
        if house is not None:
            lines.append(f"Own house in {town}: "
                         f"{HOUSE_TYPES[house['type']][0]} "
                         f"({house['address']}, id {house['id']})")
    for town in player.profile.get("lodging", {}):
        house = lodging_of(player, town)
        if house is not None:
            lines.append(f"Lives at {house['owner_name']}'s "
                         f"{HOUSE_TYPES[house['type']][0]} "
                         f"({house['address']})")
    return lines or ["Home: none"]


def sheet_lines(player:Player) -> list[str]:
    kind = {"maid": "maid NPC"}.get(player.npc, "NPC" if player.npc
                                    else "adventurer")
    return [f"Age: {player.age} | Gender: {player.gender} | {kind}",
            f"Personality: {player.personality or 'not written yet'}",
            *([f"Appearance: {player.profile['look']}"]
              if player.profile.get("look") and not player.npc else []),
            *home_lines(player), *anatomy_lines(player)]
