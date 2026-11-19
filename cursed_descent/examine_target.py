from .config import EQUIPMENT_SLOTS, HUNG_GENDERS, SLOT_LABELS, TRIBE_NAMES
from .content import ENEMIES, ITEMS
from .formulas import max_hp
from .models import Enemy, Message, Player
from . import control, routines
from .npcs.store import find_local
from .sheet import sheet_lines
from .towns import START_TOWN, TOWNS


def bulge_word(length_cm:int) -> str:
    if length_cm >= 30:
        return "an enormous"
    if length_cm >= 22:
        return "a heavy"
    if length_cm >= 14:
        return "a noticeable"
    return "a small"


def visible_anatomy(player:Player) -> list[str]:
    lines = sheet_lines(player)
    gear = player.equipment.get("crotch")
    if player.gender not in HUNG_GENDERS or not gear:
        return lines
    name = ITEMS.get(gear, {}).get("name", gear)
    length = player.body.get("endowment", 0)
    bulge = f"Cock: hidden under the {name}, {bulge_word(length)} bulge"
    return [bulge if line.startswith("Cock:") else line for line in lines]


def worn_lines(player:Player) -> list[str]:
    worn = [f"{SLOT_LABELS.get(slot, slot)}: "
            f"{ITEMS.get(player.equipment[slot], {}).get('name', '?')}"
            for slot in EQUIPMENT_SLOTS if player.equipment.get(slot)]
    return ["Wearing: " + (", ".join(worn) if worn else "nothing special")]


def player_report(target:Player) -> list[str]:
    kind = "NPC" if target.npc else "adventurer"
    name = " ".join(part for part in (target.first_name, target.last_name)
                    if part) or target.name
    profile = target.profile
    role = f", {profile['role']}" if profile.get("role") else ""
    state = (f"HP {max(target.hp, 0)}/{max_hp(target)}"
             if target.hp else f"HP {max_hp(target)}")
    lines = [f"🔎 {name} ({target.name}) – level {target.level} "
             f"{kind}{role}"]
    if profile.get("look"):
        lines.append(profile["look"])
    if target.personality and not target.npc:
        lines.append(f"Personality: {target.personality}")
    if profile.get("flist") and not target.npc:
        lines.append(f"F-List: {profile['flist']}")
    lines += [*visible_anatomy(target), *worn_lines(target), state]
    if target.npc and target.records.get("kills"):
        lines.append(f"Kills: {target.records['kills']}")
    if profile.get("quotes"):
        lines.append(profile["quotes"][0])
    return lines


def enemy_report(enemy:Enemy) -> list[str]:
    tribe = TRIBE_NAMES.get(enemy.tribe, enemy.tribe)
    lines = [f"🔎 {enemy.label} – from {tribe}",
             f"HP {max(enemy.hp, 0)}/{enemy.max_hp} | attack {enemy.attack} "
             f"| defense {enemy.defense} | agility {enemy.agility}"]
    traits = []
    if enemy.boss:
        traits.append("a boss")
    if enemy.mindless:
        traits.append("mindless")
    if enemy.melee_mult < 1:
        traits.append("shrugs off melee")
    elif enemy.melee_mult > 1:
        traits.append("weak to melee")
    if enemy.magic_mult < 1:
        traits.append("resists magic")
    elif enemy.magic_mult > 1:
        traits.append("weak to magic")
    if traits:
        lines.append("Notes: " + ", ".join(traits))
    if enemy.intent:
        lines.append(f"It looks like it is about to {enemy.intent}"
                     + (f" {enemy.intent_target}." if enemy.intent_target
                        else "."))
    if enemy.fates:
        lines.append("What it does to the beaten: " + ", ".join(enemy.fates))
    return lines


def find_enemy(enemies:list[Enemy], text:str) -> Enemy | None:
    wanted = text.strip().casefold().lstrip("[").rstrip("]")
    living = [enemy for enemy in enemies if enemy.alive]
    for enemy in living:
        if wanted == str(enemy.uid):
            return enemy
    for enemy in living:
        if wanted and wanted in enemy.name.casefold():
            return enemy
    return None


def find_character(names:list[str], party:list[Player], repository,
                   text:str) -> Player | None:
    wanted = text.strip().casefold()
    for player in party:
        if wanted in (player.name.casefold(), player.first_name.casefold()):
            return player
    for name in names:
        player = repository.load(name)
        if player is not None and wanted in (
                name.casefold(), player.first_name.casefold()):
            return player
    return None


def examine_target(player:Player, text:str, enemies:list[Enemy],
                   party:list[Player], repository, in_run:bool,
                   ) -> list[Message]:
    enemy = find_enemy(enemies, text) if in_run else None
    target = find_character(repository.names(), party, repository, text)
    if target is None:
        target = find_local(repository.npc_players(), text)
        if target is not None and in_run and target.profile.get(
                "building") in TOWNS[START_TOWN].buildings:
            target = None
        if target is not None and not in_run and not routines.reachable(
                player, target.npc):
            target = None
    if enemy is not None:
        lines = enemy_report(enemy)
        key = ENEMIES.get(enemy.template_id, {}).get("npc")
        figure = next((npc for npc in repository.npc_players()
                       if key and npc.npc == key),
                      None) or find_local(repository.npc_players(), enemy.name)
        if figure is not None:
            lines += [figure.profile.get("look", ""),
                      *visible_anatomy(figure), *worn_lines(figure)]
    elif target is not None:
        spot = None if in_run else routines.texts.at_place(target.npc)
        if spot is not None and not spot.examine:
            return [Message(f"{target.first_name} is here, but there is "
                            f"nothing to see yet.", player.name)]
        held = [] if target.npc else [control.examine_line(target)]
        lines = (([spot.examine] if spot else [])
                 + [line for line in held if line] + player_report(target))
    else:
        lines = []
    if not lines:
        return [Message(routines.away_message(player, text)
                        or f"You see nobody called '{text}' to look at.",
                        player.name)]
    return [Message("\n".join(lines), player.name)]
