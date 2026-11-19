import random
from dataclasses import dataclass, field

from .body import muscle_tier, shape_of, size_class
from .config import (
    BREEDING_BODY_BONUS, BREEDING_CHANCE, BREEDING_FALLBACK_FATE, FUTA_GENDERS,
    DAIRY_CHANCE, DAIRY_GEAR_BONUS, DAIRY_TRIBES, MAX_DAIRY_CHANCE,
    DEFAULT_BREEDING_CHANCE, DEFAULT_GENDER, GIANT_SMALL_TROPHY_CHANCE,
    HEAVY_ROAST_CHANCE, LICH_CONSORT_GENDERS, LICH_TRIBE, WINTER_TRIBE,
    MAX_BREEDING_CHANCE, PRONOUNS, SOUL_HUNGER_CHANCE,
    TRIBE_BREEDING_CHANCE,
)
from .content import (
    ACTION_MULTIPLIERS, DISTRACT_TEXTS, FATES, INTENT_TEXTS, ITEMS,
    SOUL_HUNGER_TEXTS, SPELLS,
)
from .formulas import (
    allure_breeding_bonus, armor_value, clear_buffs, crit_chance,
    distract_chance, enemy_dodge_chance, equipped_items, guard_reduction,
    max_hp, max_mana, melee_damage, player_dodge_chance, spell_power,
)
from .items import remove_item
from .models import Action, Enemy, Player
from .scent import scent_fate, scent_weight
from .needs_runtime import change_text, consume
from .sweat import add_sweat


@dataclass
class RoundResult:
    lines: list[str] = field(default_factory=list)
    killed: list[Enemy] = field(default_factory=list)
    fallen: list[Player] = field(default_factory=list)


def armor_multiplier(armor:float) -> float:
    return 50 / (50 + max(armor, 0))


def find_player(party:list[Player], name:str) -> Player | None:
    wanted = name.strip().casefold()
    if not wanted:
        return None
    for player in party:
        if player.name.casefold() == wanted:
            return player
    return None


def find_enemy(enemies:list[Enemy], uid:str) -> Enemy | None:
    for enemy in enemies:
        if str(enemy.uid) == uid.strip():
            return enemy
    return None


def weakest_enemy(enemies:list[Enemy]) -> Enemy | None:
    living = [enemy for enemy in enemies if enemy.alive]
    return min(living, key=lambda enemy: enemy.hp) if living else None


def weakest_ally(party:list[Player]) -> Player | None:
    living = [player for player in party if player.alive]
    if not living:
        return None
    return min(living, key=lambda player: player.hp / max_hp(player))


def enemy_hp_text(enemy:Enemy) -> str:
    return f"{max(enemy.hp, 0)}/{enemy.max_hp} HP"


def player_hp_text(player:Player) -> str:
    return f"{max(player.hp, 0)}/{max_hp(player)} HP"


def choose_intents(enemies:list[Enemy], party:list[Player]) -> list[str]:
    living = [player for player in party if player.alive]
    lines: list[str] = []
    for enemy in enemies:
        if not enemy.alive or not living:
            continue
        names = [name for name, _ in enemy.actions]
        weights = [weight for _, weight in enemy.actions]
        enemy.intent = random.choices(names, weights=weights)[0]
        if enemy.intent == "sweep":
            enemy.intent_target = ""
        elif enemy.intent == "attack_weakest":
            enemy.intent_target = min(living, key=lambda p: p.hp).name
        else:
            scent = [scent_weight(enemy, player) for player in living]
            enemy.intent_target = random.choices(living, weights=scent)[0].name
        lines.append(INTENT_TEXTS[enemy.intent].format(
            enemy=enemy.label, target=enemy.intent_target))
    return lines


def damage_enemy(enemy:Enemy, raw:float, attacker:Player) -> int:
    dealt = max(1, round(raw * armor_multiplier(enemy.defense)))
    was_alive = enemy.alive
    enemy.hp -= dealt
    if was_alive and not enemy.alive:
        enemy.killed_by = attacker.name
    return dealt


def pick_enemy_target(action:Action, enemies:list[Enemy]) -> Enemy | None:
    target = find_enemy(enemies, action.target) if action.target else None
    return target if target else weakest_enemy(enemies)


def resolve_melee(player:Player, action:Action, enemies:list[Enemy],
                  result:RoundResult) -> None:
    player.add_affinity("melee")
    target = pick_enemy_target(action, enemies)
    if target is None:
        result.lines.append(f"{player.name} swings at nothing.")
        return
    if not target.alive:
        result.lines.append(f"{player.name} only hits the corpse of "
                            f"{target.label} – overkill.")
        return
    if random.random() < enemy_dodge_chance(target):
        result.lines.append(f"{target.label} dodges the attack of "
                            f"{player.name}.")
        return
    raw = melee_damage(player) * target.melee_mult
    crit = random.random() < crit_chance(player)
    if crit:
        raw *= 1.75
    dealt = damage_enemy(target, raw, player)
    crit_text = " CRITICAL!" if crit else ""
    result.lines.append(f"⚔ {player.name} hits {target.label} for "
                        f"{dealt}.{crit_text} ({enemy_hp_text(target)})")


def resolve_damage_spell(player:Player, action:Action, enemies:list[Enemy],
                         result:RoundResult) -> None:
    spell = SPELLS[action.spell]
    if player.mana < spell["mana"]:
        result.lines.append(f"{player.name} lacks the mana and strikes "
                            f"instead.")
        resolve_melee(player, Action("hit", target=action.target), enemies,
                      result)
        return
    player.mana -= spell["mana"]
    player.add_affinity("magic")
    if spell["target"] == "all":
        targets = [enemy for enemy in enemies if enemy.alive]
    else:
        target = pick_enemy_target(action, enemies)
        targets = [target] if target else []
    if not targets:
        result.lines.append(f"✨ {player.name}'s {spell['name']} fizzles.")
        return
    for target in targets:
        if not target.alive:
            result.lines.append(f"✨ {player.name}'s {spell['name']} only "
                                f"hits the corpse of {target.label}.")
            continue
        raw = spell_power(player, action.spell) * target.magic_mult
        dealt = damage_enemy(target, raw, player)
        result.lines.append(f"✨ {player.name}'s {spell['name']} hits "
                            f"{target.label} for {dealt}. "
                            f"({enemy_hp_text(target)})")


def heal_player(target:Player, amount:int) -> int:
    before = target.hp
    target.hp = min(max_hp(target), target.hp + amount)
    return target.hp - before


def restore_mana(target:Player, amount:int) -> int:
    before = target.mana
    target.mana = min(max_mana(target), target.mana + amount)
    return target.mana - before


def resolve_heal_spell(player:Player, action:Action, party:list[Player],
                       result:RoundResult) -> None:
    spell = SPELLS[action.spell]
    if player.mana < spell["mana"]:
        result.lines.append(f"{player.name} lacks the mana for "
                            f"{spell['name']}.")
        return
    player.mana -= spell["mana"]
    player.add_affinity("heal")
    if spell["target"] == "allies":
        targets = [member for member in party if member.alive]
    else:
        target = find_player(party, action.target)
        if target is None or not target.alive:
            target = weakest_ally(party)
        targets = [target] if target else []
    for target in targets:
        healed = heal_player(target, round(spell_power(player, action.spell)))
        result.lines.append(f"💚 {player.name}'s {spell['name']} heals "
                            f"{target.name} for {healed}. "
                            f"({player_hp_text(target)})")


def resolve_item(player:Player, action:Action, party:list[Player],
                 result:RoundResult) -> None:
    if action.item not in player.inventory:
        result.lines.append(f"{player.name} rummages through the bag in vain.")
        return
    item = ITEMS[action.item]
    target = find_player(party, action.target) or player
    if not target.alive:
        target = player
    remove_item(player.inventory, action.item)
    parts: list[str] = []
    if item.get("heal"):
        parts.append(f"+{heal_player(target, item['heal'])} HP")
    if item.get("mana"):
        parts.append(f"+{restore_mana(target, item['mana'])} Mana")
    changes = consume(target, action.item)
    if changes:
        parts.append(change_text(changes))
    result.lines.append(f"🧪 {player.name} uses {item['name']} on "
                        f"{target.name}: {', '.join(parts)}.")


def alluring_item(player:Player) -> str:
    names = [item["name"] for item in equipped_items(player)
             if item.get("allure")]
    return random.choice(names) if names else "curves"


def hit_player(enemy:Enemy, target:Player, dodging:set[str],
               guards:dict[str, Player], result:RoundResult) -> None:
    if not enemy.mindless and random.random() < distract_chance(target):
        text = random.choice(DISTRACT_TEXTS).format(
            enemy=enemy.label, name=target.name, item=alluring_item(target))
        result.lines.append(f"💋 {text}")
        return
    if random.random() < player_dodge_chance(target, target.name in dodging):
        result.lines.append(f"💨 {target.name} dodges {enemy.label}.")
        return
    raw = enemy.attack * ACTION_MULTIPLIERS[enemy.intent]
    raw *= random.uniform(0.9, 1.1)
    guardian = guards.get(target.name)
    if guardian:
        raw *= 1 - guard_reduction(guardian)
    dealt = max(1, round(raw * armor_multiplier(armor_value(target))))
    target.hp -= dealt
    target.last_hit_by = enemy
    guard_text = f" (guarded by {guardian.name})" if guardian else ""
    result.lines.append(f"🩸 {enemy.label} hits {target.name} for "
                        f"{dealt}.{guard_text} ({player_hp_text(target)})")
    if enemy.intent == "drain" and enemy.alive:
        enemy.hp = min(enemy.max_hp, enemy.hp + dealt // 2)


def resolve_enemy(enemy:Enemy, party:list[Player], dodging:set[str],
                  guards:dict[str, Player], result:RoundResult) -> None:
    if enemy.intent == "sweep":
        targets = [player for player in party if player.alive]
    else:
        target = find_player(party, enemy.intent_target)
        targets = [target] if target and target.alive else []
    for target in targets:
        hit_player(enemy, target, dodging, guards, result)


def resolve_defense(living:list[Player], party:list[Player],
                    result:RoundResult) -> tuple[set[str], dict[str, Player]]:
    dodging: set[str] = set()
    guards: dict[str, Player] = {}
    for player in living:
        action = player.action
        if action.kind == "dodge":
            dodging.add(player.name)
            player.add_affinity("dodge")
            result.lines.append(f"💨 {player.name} gets ready to "
                                f"dodge.")
        elif action.kind == "guard":
            target = find_player(party, action.target) or player
            if not target.alive:
                target = player
            guards[target.name] = player
            player.add_affinity("guard")
            if target is player:
                result.lines.append(f"🛡 {player.name} takes cover.")
            else:
                result.lines.append(f"🛡 {player.name} guards "
                                    f"{target.name}.")
    return dodging, guards


def body_tags(player:Player) -> list[str]:
    body = player.body
    tags = [f"size:{size_class(body['height'])}", f"build:{body['build']}",
            f"breasts:{body['breasts']}",
            f"muscle:{muscle_tier(player.stats, body)}"]
    if shape_of(player.gender, body):
        tags.append(f"shape:{shape_of(player.gender, body)}")
    tags += [f"gear:{item_id}" for item_id in player.equipment.values()
             if item_id]
    return tags


def breeding_chance(player:Player, killer:Enemy) -> float:
    chances = TRIBE_BREEDING_CHANCE.get(killer.tribe, BREEDING_CHANCE)
    chance = chances.get(player.gender, DEFAULT_BREEDING_CHANCE)
    attractive = (player.body["build"] == "Curvy"
                  or player.body["breasts"] in ("Large", "Huge", "Massive"))
    if chance > 0 and attractive:
        chance += BREEDING_BODY_BONUS
    if chance > 0:
        chance += allure_breeding_bonus(player)
    return min(chance, MAX_BREEDING_CHANCE)


def pick_other_fate(player:Player, fates:list[str]) -> str:
    if not fates:
        return BREEDING_FALLBACK_FATE
    if "podded" in fates:
        pods = [fate for fate in fates if fate != "podded"]
        if player.gender in FUTA_GENDERS:
            return "podded"
        fates = pods or fates
    heavy = player.body["build"] in ("Heavy", "Chubby")
    if heavy and "roasted" in fates and random.random() < HEAVY_ROAST_CHANCE:
        return "roasted"
    return random.choice(fates)


def dairy_chance(player:Player, killer:Enemy) -> float:
    if killer.tribe not in DAIRY_TRIBES:
        return 0.0
    chance = DAIRY_CHANCE.get(
        player.body.get("breasts_real", player.body["breasts"]), 0.0)
    if chance == 0:
        return 0.0
    chance += sum(DAIRY_GEAR_BONUS.get(item_id, 0.0)
                  for item_id in player.equipment.values())
    return min(chance, MAX_DAIRY_CHANCE)


def soul_hungry(player:Player) -> bool:
    weapon = player.equipment.get("weapon")
    return bool(weapon and ITEMS[weapon].get("soul_hunger"))


def choose_fate(player:Player, killer:Enemy | None) -> str:
    if killer is None:
        return "wall"
    if killer.tribe == WINTER_TRIBE:
        return "sacked"
    if killer.tribe == LICH_TRIBE:
        if player.gender in LICH_CONSORT_GENDERS:
            return "consort"
        return "ice_statue"
    nudged = scent_fate(player, killer)
    if nudged:
        return nudged
    small = size_class(player.body["height"]) in ("tiny", "short")
    if ("trophy" in killer.fates and small
            and random.random() < GIANT_SMALL_TROPHY_CHANCE):
        return "trophy"
    if random.random() < dairy_chance(player, killer):
        return "dairy"
    if "breeding" not in killer.fates:
        return pick_other_fate(player, killer.fates)
    if random.random() < breeding_chance(player, killer):
        return "breeding"
    others = [fate for fate in killer.fates if fate != "breeding"]
    return pick_other_fate(player, others)


def fate_text(player:Player, fate:str, killer:Enemy | None) -> str:
    texts = FATES[fate]
    pool = texts["any"] + texts.get(player.gender, [])
    for tag in body_tags(player):
        pool += texts.get(tag, [])
    if killer:
        pool += texts.get(f"tribe:{killer.tribe}", [])
    they, them, their = PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])
    weapon_id = player.equipment.get("weapon")
    weapon = ITEMS[weapon_id]["name"] if weapon_id else "weapon"
    return random.choice(pool).format(
        name=player.name, weapon=weapon,
        killer=killer.name if killer else "the dungeon",
        tribe=killer.tribe if killer else "monsters",
        they=they, them=them, their=their,
        They=they.capitalize(), Their=their.capitalize(),
    )


def kill_player(player:Player, result:RoundResult) -> None:
    player.hp = 0
    player.alive = False
    killer = player.last_hit_by
    fate = choose_fate(player, killer)
    player.last_fate = fate
    player.deaths[fate] = player.deaths.get(fate, 0) + 1
    player.last_fate_text = fate_text(player, fate, killer)
    player.soul_weapon = ""
    result.lines.append(f"💀 {player.last_fate_text}")
    if soul_hungry(player) and random.random() < SOUL_HUNGER_CHANCE:
        player.soul_weapon = ITEMS[player.equipment["weapon"]]["name"]
        player.deaths["soulbound"] = player.deaths.get("soulbound", 0) + 1
        result.lines.append(random.choice(SOUL_HUNGER_TEXTS).format(
            name=player.name, weapon=player.soul_weapon))
    clear_buffs(player)
    result.fallen.append(player)


def ambush(enemy:Enemy, target:Player) -> RoundResult:
    result = RoundResult()
    enemy.intent = "heavy"
    hit_player(enemy, target, set(), {}, result)
    if target.hp <= 0:
        kill_player(target, result)
    return result


def resolve_deaths(living:list[Player], active:list[Enemy],
                   result:RoundResult) -> None:
    for enemy in active:
        if not enemy.alive:
            result.killed.append(enemy)
            result.lines.append(f"☠ {enemy.label} falls. "
                                f"(Killing blow: {enemy.killed_by})")
    for player in living:
        if player.hp <= 0:
            kill_player(player, result)


def resolve_round(party:list[Player], enemies:list[Enemy]) -> RoundResult:
    result = RoundResult()
    living = [player for player in party if player.alive]
    active = [enemy for enemy in enemies if enemy.alive]
    for player in living:
        if player.action is None:
            player.action = Action("hit")
    dodging, guards = resolve_defense(living, party, result)
    for player in living:
        action = player.action
        if action.kind == "cast" and SPELLS[action.spell]["kind"] == "heal":
            resolve_heal_spell(player, action, party, result)
        elif action.kind == "use":
            resolve_item(player, action, party, result)
    for player in living:
        action = player.action
        if action.kind == "hit":
            resolve_melee(player, action, enemies, result)
        elif (action.kind == "cast"
              and SPELLS[action.spell]["kind"] == "damage"):
            resolve_damage_spell(player, action, enemies, result)
    for enemy in active:
        resolve_enemy(enemy, party, dodging, guards, result)
    resolve_deaths(living, active, result)
    for player in living:
        if player.alive:
            note = add_sweat(player, player.action.kind)
            if note:
                result.lines.append(note)
    for player in party:
        player.action = None
    return result
