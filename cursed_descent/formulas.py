import random

from .config import (
    ALLURE_BREEDING, ALLURE_DISTRACT, SWEAT_ALLURE, SWEAT_DODGE,
    CYCLE_BONUS, CYCLE_LENGTH,
    ENEMY_SCALING, INSPECT_BASE_CHANCE, MAX_ALLURE_BREEDING, MAX_DISTRACT,
    INSPECT_INT_CHANCE, INSPECT_MAX_CHANCE, MAX_ENEMIES, MIMIC_BASE_CHANCE,
    MIMIC_MAX_CHANCE, MIMIC_STAGE_CHANCE, OFFSPRING_HP, STAT_SHORT,
)
from .body import body_effect
from .needs import allure_bonus, penalty as need_penalty
from .content import (
    BUFFS, ENHANCEMENTS, ITEM_SETS, ITEMS, SPELLS,
)
from .item_store import allowed_for
from .models import Enemy, Player
from .sweat import sweat_tier


def item_data(item_id:str) -> dict:
    data = ITEMS[item_id]
    stats = getattr(item_id, "stats", None)
    return {**data, **stats} if stats else data


def equipped_items(player:Player) -> list[dict]:
    return [item_data(item_id) for item_id in player.equipment.values()
            if item_id in ITEMS]


def set_counts(player:Player) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in equipped_items(player):
        if item.get("set") in ITEM_SETS:
            counts[item["set"]] = counts.get(item["set"], 0) + 1
    return counts


def set_size(set_id:str) -> int:
    if "size" in ITEM_SETS[set_id]:
        return ITEM_SETS[set_id]["size"]
    return sum(1 for item in ITEMS.values() if item.get("set") == set_id)


def own_bonus_active(player:Player, set_id:str, count:int) -> bool:
    item_set = ITEM_SETS[set_id]
    return (item_set.get("owner") == player.name
            and count >= item_set.get("own_pieces", 99))


def active_set_bonuses(player:Player) -> list[dict]:
    bonuses: list[dict] = []
    for set_id, count in set_counts(player).items():
        for pieces, bonus in sorted(ITEM_SETS[set_id]["bonuses"].items()):
            if count >= pieces:
                bonuses.append(bonus)
        if own_bonus_active(player, set_id, count):
            bonuses.append(ITEM_SETS[set_id]["own_bonus"])
    return bonuses


def gear_sources(player:Player) -> list[dict]:
    buffs = [BUFFS[buff] for buff in player.buffs]
    enhanced = [ENHANCEMENTS[key] for key in player.enhancements
                if key in ENHANCEMENTS]
    return (equipped_items(player) + active_set_bonuses(player) + buffs
            + enhanced)


def apply_buff(player:Player, buff_id:str) -> None:
    buff = BUFFS[buff_id]
    player.buffs.append(buff_id)
    if buff.get("body"):
        if player.body_backup is None:
            player.body_backup = dict(player.body)
        player.body.update(buff["body"])
        if "breasts" in buff["body"]:
            player.body["breasts_real"] = buff["body"]["breasts"]
    player.hp = min(player.hp, max_hp(player))
    player.mana = min(player.mana, max_mana(player))


def clear_buffs(player:Player) -> None:
    player.buffs = []
    if player.body_backup is not None:
        player.body = player.body_backup
        player.body_backup = None


def buff_lines(player:Player) -> list[str]:
    if not player.buffs:
        return []
    parts = [f"{BUFFS[buff]['label']} "
             f"({set_bonus_text(BUFFS[buff])})" for buff in player.buffs]
    return [f"Buffs (until death): {', '.join(parts)}"]


def set_bonus_text(bonus:dict) -> str:
    parts = [f"{value:+d} {STAT_SHORT[stat]}"
             for stat, value in bonus.get("bonus", {}).items()]
    if bonus.get("melee"):
        parts.append(f"+{round(bonus['melee'] * 100)}% melee")
    if bonus.get("crit"):
        parts.append(f"+{round(bonus['crit'] * 100)}% crit")
    if bonus.get("armor"):
        parts.append(f"+{bonus['armor']} armor")
    if bonus.get("allure"):
        parts.append(f"+{bonus['allure']} allure")
    return ", ".join(parts)


def set_lines(player:Player) -> list[str]:
    lines: list[str] = []
    for set_id, count in set_counts(player).items():
        item_set = ITEM_SETS[set_id]
        parts = []
        for pieces, bonus in sorted(item_set["bonuses"].items()):
            mark = "✔" if count >= pieces else "✘"
            parts.append(f"{mark} {pieces}: {set_bonus_text(bonus)}")
        if item_set.get("owner") == player.name:
            mark = "✔" if own_bonus_active(player, set_id, count) else "✘"
            parts.append(f"{mark} wearing yourself "
                         f"({item_set['own_pieces']}+): "
                         f"{set_bonus_text(item_set['own_bonus'])}")
        lines.append(f"Set {item_set['name']} {count}/{set_size(set_id)} – "
                     f"{' | '.join(parts)}")
    return lines


def effective_stat(player:Player, stat:str) -> int:
    bonus = sum(item.get("bonus", {}).get(stat, 0)
                for item in gear_sources(player))
    return max(1, player.stats[stat] + bonus - need_penalty(player.needs,
                                                             stat))


def stat_total_text(player:Player, stat:str) -> str:
    base = player.stats[stat]
    total = effective_stat(player, stat)
    if total == base:
        return f"{STAT_SHORT[stat]} {total}"
    return f"{STAT_SHORT[stat]} {total} ({base} {total - base:+d})"


def totals_line(player:Player) -> str:
    return (f"Weapon {weapon_damage(player)} | "
            f"Armor {round(armor_value(player), 1)} | "
            f"Allure {allure(player)}")


def allure(player:Player) -> int:
    gear = sum(item.get("allure", 0) for item in gear_sources(player))
    sweat = sweat_tier(player) * SWEAT_ALLURE
    return round(gear + sweat + body_effect(player.body, "allure")
                 + allure_bonus(player.needs))


def distract_chance(player:Player) -> float:
    return min(allure(player) * ALLURE_DISTRACT, MAX_DISTRACT)


def allure_breeding_bonus(player:Player) -> float:
    return min(allure(player) * ALLURE_BREEDING, MAX_ALLURE_BREEDING)


def wear_restriction(item_id:str) -> str:
    restriction = getattr(item_id, "restriction", "both")
    if restriction == "both":
        restriction = ITEMS[item_id].get("for", "both")
    return restriction


def can_wear(player:Player, item_id:str) -> bool:
    allowed = ITEMS[item_id].get("requires")
    if allowed and player.gender not in allowed:
        return False
    return allowed_for(wear_restriction(item_id), player.gender)


def wear_refusal(player:Player, item_id:str) -> str:
    name = ITEMS[item_id]["name"]
    allowed = ITEMS[item_id].get("requires")
    if allowed and player.gender not in allowed:
        return (f"The {name} doesn't fit you "
                f"(fits: {', '.join(allowed)}).")
    side = {"gent": "gents", "lady": "ladies"}.get(
        wear_restriction(item_id), "others")
    return (f"The {name} is made for {side}. As a {player.gender} "
            f"you cannot wear it.")


def max_hp(player:Player) -> int:
    base = 50 + effective_stat(player, "vitality") * 10 + player.level * 5
    base += len(player.offspring) * OFFSPRING_HP
    return max(10, round(base + body_effect(player.body, "hp")))


def max_mana(player:Player) -> int:
    return 20 + effective_stat(player, "intelligence") * 5


def exp_needed(level:int) -> int:
    return int(100 * level ** 1.5)


def affinity_bonus(value:int) -> float:
    return min(value * 0.001, 0.25)


def weapon_damage(player:Player) -> int:
    return sum(item.get("damage", 0) for item in equipped_items(player))


def armor_value(player:Player) -> float:
    armor = sum(item.get("armor", 0) for item in gear_sources(player))
    return (armor + effective_stat(player, "vitality") * 0.5
            + body_effect(player.body, "armor"))


def melee_damage(player:Player) -> float:
    base = 5 + effective_stat(player, "strength") * 2 + weapon_damage(player)
    bonus = (1 + affinity_bonus(player.affinity["melee"])
             + body_effect(player.body, "melee")
             + sum(item.get("melee", 0) for item in gear_sources(player)))
    return base * random.uniform(0.85, 1.15) * bonus


def spell_power(player:Player, spell_id:str) -> float:
    spell = SPELLS[spell_id]
    intelligence = effective_stat(player, "intelligence")
    base = spell["base"] + intelligence * spell["scale"]
    bonus = 1 + affinity_bonus(player.affinity[spell["affinity"]])
    return base * random.uniform(0.9, 1.1) * bonus


def crit_chance(player:Player) -> float:
    gear = sum(item.get("crit", 0) for item in gear_sources(player))
    return min(effective_stat(player, "agility") * 0.005 + gear, 0.40)


def player_dodge_chance(player:Player, dodging:bool) -> float:
    chance = min(0.05 + effective_stat(player, "agility") * 0.01, 0.40)
    chance = max(0.0, chance + body_effect(player.body, "dodge"))
    chance += sweat_tier(player) * SWEAT_DODGE
    if dodging:
        chance += 0.40 + affinity_bonus(player.affinity["dodge"])
        chance = min(chance, 0.85)
    return chance


def guard_reduction(guardian:Player) -> float:
    return min(0.5 + affinity_bonus(guardian.affinity["guard"]), 0.75)


def enemy_dodge_chance(enemy:Enemy) -> float:
    return min(enemy.agility * 0.005, 0.25)


def cycle_number(stage:int) -> int:
    return (stage - 1) // CYCLE_LENGTH


def enemy_scale(stage:int) -> float:
    return ENEMY_SCALING ** (stage - 1) * CYCLE_BONUS ** cycle_number(stage)


def mimic_chance(stage:int) -> float:
    return min(MIMIC_BASE_CHANCE + stage * MIMIC_STAGE_CHANCE,
               MIMIC_MAX_CHANCE)


def inspect_chance(player:Player) -> float:
    intelligence = effective_stat(player, "intelligence")
    return min(INSPECT_BASE_CHANCE + intelligence * INSPECT_INT_CHANCE,
               INSPECT_MAX_CHANCE)


def enemy_count(stage:int) -> int:
    return random.randint(1, min(2 + stage // 4, MAX_ENEMIES))


def loot_chance(average_intelligence:float, boss:bool) -> float:
    if boss:
        return 1.0
    return min(0.25 + average_intelligence * 0.005, 0.60)


def knows_spell(player:Player, spell_id:str) -> bool:
    spell = SPELLS[spell_id]
    if player.affinity[spell["affinity"]] >= spell["req_affinity"]:
        return True
    intelligence = effective_stat(player, "intelligence")
    return intelligence >= spell["req_intelligence"] > 0
