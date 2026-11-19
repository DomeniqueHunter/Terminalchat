import math
import random
from dataclasses import dataclass

from ...body import (
    BUILDS, BUST_CC, BUTT_DEFAULT, DEFAULT_ENDOWMENT, ENDOWMENT_SHAPES,
    apply_body_mods, bust_cm, bust_label, fake_amount, muscle_baseline,
)
from ...config import (
    CLINIC_MAGIC_BASE_CHANCE, CLINIC_MAGIC_CHANCE_DROP, CLINIC_MAGIC_FACTOR,
    CLINIC_MAGIC_MIN_CHANCE, CLINIC_PRICES, ENDOWMENT_BONUS_CM, HUNG_GENDERS,
)
from ...models import Message, Player
from ...towns import town_key
from ...races import race_of_town
from .content import CLINIC_TEXTS, ENHANCEMENTS, KEEPERS


@dataclass(frozen=True)
class Part:
    key: str
    command: str
    label: str
    unit: str
    step: int
    price: int
    reference: int
    minimum: int
    hung: bool = False
    enlargeable: bool = False


PARTS = (
    Part("height", "height", "Height", "cm", 5, 150, 170, 30),
    Part("weight", "weight", "Weight", "kg", 5, 60, 65, 10),
    Part("muscle", "muscle", "Muscle", "", 5, 150, 25, 0),
    Part("bust", "bust", "Bust", "cc", 150, 120, 300, 0, enlargeable=True),
    Part("butt", "butt", "Butt", "cm", 5, 100, 95, 60, enlargeable=True),
    Part("endowment", "cock", "Cock length", "cm", 2, 150,
         DEFAULT_ENDOWMENT, 4, hung=True, enlargeable=True),
    Part("girth", "girth", "Girth", "cm", 1, 100, 12, 4, hung=True,
         enlargeable=True),
    Part("balls", "balls", "Balls", "cm", 1, 120, 5, 2, hung=True,
         enlargeable=True),
)


ALIASES = {"taller": "height up", "shorter": "height down",
           "heavier": "weight up", "lighter": "weight down"}


def part_price(part:Part, value:float, magic:bool=False) -> int:
    growth = 1 + max(0.0, value - part.reference) / part.reference
    return round(part.price * growth * (CLINIC_MAGIC_FACTOR if magic else 1))


def magic_chance(part:Part, value:float) -> float:
    octaves = math.log2(max(1.0, value / part.reference))
    chance = CLINIC_MAGIC_BASE_CHANCE - CLINIC_MAGIC_CHANCE_DROP * octaves
    return max(CLINIC_MAGIC_MIN_CHANCE, chance)


def unit_text(part:Part, amount:float) -> str:
    return f"{amount} {part.unit}".strip()


def clinic_options(player:Player) -> list[tuple[str, str, int]]:
    body = player.body
    hung = player.gender in HUNG_GENDERS
    options: list[tuple[str, str, int]] = []
    for part in PARTS:
        if part.hung and not hung:
            continue
        value = body[part.key]
        up_label = (f"{part.label}: {unit_text(part, value)} → "
                    f"{unit_text(part, value + part.step)}")
        options.append((f"{part.command} up",
                        up_label + (" (implant)" if part.enlargeable else ""),
                        part_price(part, value)))
        if part.enlargeable and not race_of_town(town_key(player)).implant_only:
            chance = round(magic_chance(part, value) * 100)
            options.append((f"{part.command} up magic",
                            f"{up_label} (real, magic, {chance}% success)",
                            part_price(part, value, magic=True)))
        if value - part.step >= part.minimum:
            options.append((f"{part.command} down",
                            f"{part.label}: {unit_text(part, value)} → "
                            f"{unit_text(part, value - part.step)}",
                            part_price(part, value)))
    if player.pregnant:
        options.append(("terminate", "Terminate the pregnancy",
                        CLINIC_PRICES["terminate"]))
    for build in BUILDS:
        if build != body["build"]:
            options.append((f"build {build.lower()}", f"Build: {build}",
                            CLINIC_PRICES["build"]))
    if hung:
        for shape in ENDOWMENT_SHAPES:
            if shape != body.get("endowment_shape", "Human"):
                options.append((f"shape {shape.lower()}", f"Shape: {shape}",
                                CLINIC_PRICES["shape"]))
    for enhancement_id, enhancement in ENHANCEMENTS.items():
        if enhancement_id in player.enhancements:
            options.append((f"remove {enhancement_id}",
                            f"Remove: {enhancement['label']}",
                            CLINIC_PRICES["remove"]))
        else:
            options.append((enhancement_id, enhancement["label"],
                            enhancement["price"]))
    return options


def endowment_cm(player:Player) -> int:
    length = player.body.get("endowment", DEFAULT_ENDOWMENT)
    if "endowment" in player.enhancements:
        length += ENDOWMENT_BONUS_CM["clinic"]
    if "penis" in player.buffs:
        length += ENDOWMENT_BONUS_CM["adept"]
    return length


def implant_note(body:dict, key:str, unit:str) -> str:
    fake = fake_amount(body, key)
    return f", {fake} {unit} implants" if fake else ""


def size_line(player:Player) -> str:
    body = player.body
    parts: list[str] = []
    if body["bust"] > BUST_CC["Flat"]:
        parts.append(f"bust {bust_cm(body)} cm ({bust_label(body['bust'])}, "
                     f"{round(body['bust'])} cc"
                     f"{implant_note(body, 'bust', 'cc')})")
    parts.append(f"butt {body['butt']} cm"
                 f"{implant_note(body, 'butt', 'cm')}")
    if player.gender in HUNG_GENDERS:
        shape = body.get("endowment_shape", "Human")
        note = "" if shape == "Human" else f" ({shape.lower()})"
        parts.append(f"endowment {endowment_cm(player)} cm{note}, "
                     f"girth {body['girth']} cm, balls {body['balls']} cm"
                     f"{implant_note(body, 'endowment', 'cm')}")
    return f"Measurements: {', '.join(parts)}"


def enhancement_lines(player:Player) -> list[str]:
    lines = [size_line(player)]
    if not player.enhancements:
        return lines
    names = ", ".join(ENHANCEMENTS[key]["label"]
                      for key in player.enhancements if key in ENHANCEMENTS)
    return lines + [f"Enhanced by Dr. <<npc.vane_first>>: {names}"]


def clinic_advice(player:Player, town:str="last_light") -> list[str]:
    body = player.body
    advice = race_of_town(town).advice
    found = []
    if body.get("breasts", "None") != "None":
        found.append("bust")
    if player.gender in HUNG_GENDERS:
        found.append("balls")
        found.append("cock")
    found.append("butt")
    if body.get("build") in ("Thin", "Slim"):
        found.append("build_thin")
    elif body.get("build") in ("Heavy", "Chubby"):
        found.append("build_heavy")
    return [advice[key] for key in found[:2]] or [advice["fine"]]


def clinic_menu(player:Player, town:str="last_light") -> list[Message]:
    keeper, greeting = KEEPERS.get(town, KEEPERS["last_light"])
    advice = " ".join(clinic_advice(player, town))
    lines = [greeting.format(name=player.name),
             f"{keeper}: '{advice}{race_of_town(town).clinic_special}'",
             f"💰 Gold: {player.gold}"]
    for command, label, price in clinic_options(player):
        lines.append(f"  [mod {command}] – {label} ({price} gold)")
    lines += enhancement_lines(player)
    return [Message("\n".join(lines), player.name)]


def find_part(command:str) -> tuple[Part, str] | None:
    words = command.split()
    for part in PARTS:
        if words and words[0] == part.command and len(words) > 1:
            return part, " ".join(words[1:])
    return None


def store(player:Player, **changes) -> None:
    player.body_mods.update(changes)
    apply_body_mods(player.body, player.body_mods)


def change_part(player:Player, part:Part, how:str) -> str:
    body = player.body
    value = body[part.key]
    fake = dict(body.get("fake", {}))
    if how.startswith("up"):
        if how == "up magic":
            if random.random() >= magic_chance(part, value):
                return "failed"
        elif part.enlargeable:
            fake[part.key] = fake.get(part.key, 0) + part.step
        store(player, **{part.key: value + part.step, "fake": fake})
        return part.command
    removed = min(fake.get(part.key, 0), part.step)
    if removed:
        fake[part.key] -= removed
    store(player, **{part.key: value - part.step, "fake": fake})
    return part.command


def change_build(player:Player, build:str) -> str:
    old = player.body["build"]
    shift_muscle = muscle_baseline(build) - muscle_baseline(old)
    shift_butt = BUTT_DEFAULT.get(build, 95) - BUTT_DEFAULT.get(old, 95)
    store(player, build=build,
          muscle=max(0, player.body["muscle"] + shift_muscle),
          butt=max(60, player.body["butt"] + shift_butt))
    return "build"


def apply_mod(player:Player, command:str) -> str:
    command = ALIASES.get(command, command)
    found = find_part(command)
    if found:
        return change_part(player, *found)
    if command == "terminate":
        player.pregnant = ""
        for key in ("pregnant_by", "pregnant_by_id", "pregnant_nights"):
            player.profile.pop(key, None)
        return "terminate"
    if command.startswith("build "):
        return change_build(player, command.split()[1].capitalize())
    if command.startswith("shape "):
        store(player, endowment_shape=command.split()[1].capitalize())
        return "shape"
    if command.startswith("remove "):
        player.enhancements.remove(command.split()[1])
        return "remove"
    player.enhancements.append(command)
    return command


def clinic_mod(player:Player, args:list[str], in_run:bool) -> list[Message]:
    if in_run:
        return [Message(CLINIC_TEXTS["closed"], player.name)]
    command = ALIASES.get(" ".join(args).lower(), " ".join(args).lower())
    options = {option: price for option, _, price in clinic_options(player)}
    if command not in options:
        return clinic_menu(player, town_key(player))
    price = options[command]
    if player.gold < price:
        return [Message(CLINIC_TEXTS["poor"].format(name=player.name,
                                                    price=price,
                                                    gold=player.gold),
                        player.name)]
    player.gold -= price
    key = apply_mod(player, command)
    text = CLINIC_TEXTS["done"].get(key, CLINIC_TEXTS["done"]["generic"])
    return [Message(f"{text.format(name=player.name)}\n"
                    f"💰 Gold: {player.gold}", player.name)]
