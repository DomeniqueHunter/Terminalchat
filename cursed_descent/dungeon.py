import random

from .items import Item
from .config import (
    COMPANION_NAME, MAID_STR_PER_LEVEL, MAID_VIT_PER_LEVEL,
    TEMP_MONSTER_TEMPLATES,
    BIOME_FAVOR_WEIGHT, BIOME_SEGMENT, BOSS_INTERVAL, CHEST_RARITY_BONUS, CURSE_ITEM_LOSS_CHANCE,
    LOOT_STAT_BONUS, POINTS_PER_LEVEL, STAGE_GOLD_BASE, STAGE_GOLD_PER_STAGE,
    STRAY_CHANCE,
    STRAY_LOOKAHEAD, STRAY_MIN_STAGE, STRAY_POWER, TOWN_BIOMES,
    VINE_BIOME, VINE_GROUP_CHANCE,
)
from .content import BIOMES, ENEMIES, ITEMS, RARITY_LABELS
from .formulas import (
    effective_stat, enemy_count, enemy_scale, exp_needed,
    loot_chance, max_hp, max_mana,
)
from .models import Enemy, Player
from .plants import DROPS


def is_boss_stage(stage:int) -> bool:
    return stage % BOSS_INTERVAL == 0


def is_biome_start(stage:int) -> bool:
    return (stage - 1) % BIOME_SEGMENT == 0


def segment_of(stage:int) -> int:
    return (stage - 1) // BIOME_SEGMENT


def biome_named(name:str) -> dict:
    return next(biome for biome in BIOMES if biome["name"] == name)


def current_biome(stage:int, seed:str="", town:str="") -> dict:
    segment = segment_of(stage)
    start, favorites = TOWN_BIOMES.get(town, ("", ()))
    if segment == 0:
        return biome_named(start) if start else BIOMES[0]
    first = segment * BIOME_SEGMENT + 1
    pool = [biome for biome in BIOMES if biome["min_stage"] <= first]
    rng = random.Random(f"{seed}:{segment}")
    if not favorites:
        return rng.choice(pool)
    weights = [BIOME_FAVOR_WEIGHT if biome["name"] in favorites else 1
               for biome in pool]
    return rng.choices(pool, weights)[0]


def build_enemy(uid:int, template_id:str, template:dict, stage:int,
                boss:bool=False) -> Enemy:
    scale = enemy_scale(stage)
    hp = round(template["hp"] * scale)
    return Enemy(
        uid=uid,
        template_id=template_id,
        name=template["name"],
        max_hp=hp,
        hp=hp,
        attack=round(template["attack"] * scale),
        defense=round(template["defense"] * scale),
        agility=template["agility"],
        exp=round(template["exp"] * scale),
        fates=list(template["fates"]),
        actions=list(template["actions"]),
        boss=boss,
        tribe=template.get("tribe", "monsters"),
        melee_mult=template.get("melee_mult", 1.0),
        magic_mult=template.get("magic_mult", 1.0),
        mindless=template.get("mindless", False),
    )


def stray_templates(stage:int, biome:dict) -> list[str]:
    return [
        template_id for template_id, template in ENEMIES.items()
        if not template.get("chest_only")
        and not template.get("event_only")
        and template_id not in biome["enemies"]
        and template["min_stage"] <= stage + STRAY_LOOKAHEAD
        and (template["max_stage"] == 0 or stage <= template["max_stage"])
    ]


def pick_template(stage:int, biome:dict) -> str:
    strays = stray_templates(stage, biome)
    if (strays and stage >= STRAY_MIN_STAGE
            and random.random() < STRAY_CHANCE):
        return random.choice(strays)
    return random.choice(biome["enemies"])


def biome_average(biome:dict, key:str) -> float:
    values = [ENEMIES[template_id][key] for template_id in biome["enemies"]]
    return sum(values) / len(values)


def tame_stray(enemy:Enemy, template:dict, biome:dict) -> None:
    for key, attribute in (("hp", "max_hp"), ("attack", "attack"),
                           ("defense", "defense"), ("exp", "exp")):
        limit = STRAY_POWER * biome_average(biome, key)
        if template[key] <= limit or template[key] == 0:
            continue
        factor = limit / template[key]
        setattr(enemy, attribute, max(1, round(getattr(enemy, attribute)
                                               * factor)))
    enemy.hp = enemy.max_hp


def spawn_boss(stage:int, biome:dict) -> list[Enemy]:
    boss = biome["boss"]
    enemies = [build_enemy(1, "boss", boss, stage, boss=True)]
    for _ in range(random.randint(0, 2)):
        minion_id = random.choice(boss["minions"])
        enemies.append(build_enemy(len(enemies) + 1, minion_id,
                                   ENEMIES[minion_id], stage))
    return enemies


def pick_swamp_template(biome:dict, vines:bool) -> str:
    pool = [template_id for template_id in biome["enemies"]
            if (template_id == "pheromone_bloom") == vines]
    return random.choice(pool)


def spawn_stage(stage:int, seed:str="", town:str="") -> list[Enemy]:
    biome = current_biome(stage, seed, town)
    if is_boss_stage(stage):
        return spawn_boss(stage, biome)
    enemies: list[Enemy] = []
    vines = (biome["name"] == VINE_BIOME
             and random.random() < VINE_GROUP_CHANCE)
    for uid in range(1, enemy_count(stage) + 1):
        if biome["name"] == VINE_BIOME:
            template_id = pick_swamp_template(biome, vines)
            enemies.append(build_enemy(uid, template_id,
                                       ENEMIES[template_id], stage))
            continue
        template_id = pick_template(stage, biome)
        template = ENEMIES[template_id]
        enemy = build_enemy(uid, template_id, template, stage)
        if template_id not in biome["enemies"]:
            tame_stray(enemy, template, biome)
        enemies.append(enemy)
    return enemies


def vine_ambush(biome:dict, party:list[Player],
                enemies:list[Enemy], stage:int) -> list[str]:
    from .vine_ambush import ambush

    def make(uid:int) -> Enemy:
        return build_enemy(uid, "pheromone_bloom",
                           ENEMIES["pheromone_bloom"], stage)

    if is_boss_stage(stage):
        return []
    return ambush(biome, party, enemies, make)


def build_consort(uid:int, entry:dict, stage:int) -> Enemy:
    enemy = build_enemy(uid, "lich_consort", ENEMIES["lich_consort"], stage)
    enemy.name = f"{entry['name']}, the Queen's Consort"
    enemy.origin = entry["id"]
    return enemy


def build_skeleton(uid:int, entry:dict, stage:int) -> Enemy:
    enemy = build_enemy(uid, "risen_skeleton", ENEMIES["risen_skeleton"],
                        stage)
    enemy.name = f"{entry['name']}'s Skeleton"
    enemy.origin = entry["id"]
    return enemy


def build_temp_monster(uid:int, entry:dict, stage:int) -> Enemy:
    template_id = TEMP_MONSTER_TEMPLATES.get(entry.get("species", ""), "orc")
    enemy = build_enemy(uid, template_id, ENEMIES[template_id], stage)
    adventurer = entry.get("role") == "adventurer"
    enemy.name = entry["name"] + (" (adventurer)" if adventurer else "")
    enemy.temp_id = entry["id"]
    return enemy


def spawn_mimic(stage:int) -> list[Enemy]:
    return [build_enemy(1, "mimic", ENEMIES["mimic"], stage)]


def stage_exp(enemies:list[Enemy], stage:int) -> int:
    total = sum(enemy.exp for enemy in enemies)
    return total * 2 if is_boss_stage(stage) else total


def stage_gold(stage:int) -> int:
    gold = STAGE_GOLD_BASE + stage * STAGE_GOLD_PER_STAGE
    return gold * 2 if is_boss_stage(stage) else gold


def grant_exp(player:Player, amount:int) -> list[str]:
    lines: list[str] = []
    old_max_hp = max_hp(player)
    start_level = player.level
    player.exp += amount
    while player.exp >= exp_needed(player.level):
        player.exp -= exp_needed(player.level)
        player.level += 1
        player.free_points += POINTS_PER_LEVEL
        lines.append(f"⬆ {player.name} reaches level {player.level}! "
                     f"(+{POINTS_PER_LEVEL} points, [add] to spend them)")
    gained = player.level - start_level
    if (gained and player.npc == "mercenary"
            and player.name == COMPANION_NAME):
        player.stats["vitality"] += gained * MAID_VIT_PER_LEVEL
        player.stats["strength"] += gained * MAID_STR_PER_LEVEL
    player.hp += max_hp(player) - old_max_hp
    return lines


def roll_rarity(stage:int) -> str:
    weights = {
        "common": 60.0,
        "rare": 28.0 + stage * 0.5,
        "epic": 9.0 + stage * 0.3,
        "cursed": 3.0 + stage * 0.1,
    }
    return random.choices(list(weights), weights=list(weights.values()))[0]


def roll_item(stage:int, equipment_chance:float=0.5) -> str:
    rarity = roll_rarity(stage)
    equipment = random.random() < equipment_chance
    lootable = {item_id: item for item_id, item in ITEMS.items()
                if not item.get("no_loot")}
    candidates = [
        item_id for item_id, item in lootable.items()
        if item["rarity"] == rarity
        and (item["slot"] != "consumable") == equipment
    ]
    if not candidates:
        candidates = [item_id for item_id, item in lootable.items()
                      if item["rarity"] == rarity]
    return random.choice(candidates)


def find_inventory_item(player:Player, reference:str) -> str | None:
    if reference.isdigit():
        index = int(reference) - 1
        if 0 <= index < len(player.inventory):
            return player.inventory[index]
        return None
    wanted = reference.casefold()
    for item_id in player.inventory:
        if wanted in (item_id, ITEMS[item_id]["name"].casefold()):
            return item_id
    return None


def loot_stats(item_id:str) -> dict | None:
    from .item_store import base_stats
    if ITEMS[item_id]["slot"] == "consumable":
        return None

    def grow(value:int) -> int:
        if value <= 0:
            return value
        return max(value, round(value * (1 + random.uniform(
            0, LOOT_STAT_BONUS))))

    stats = base_stats(item_id)
    for key, value in stats.items():
        if isinstance(value, dict):
            stats[key] = {stat: grow(number)
                          for stat, number in value.items()}
        elif key in ("damage", "armor", "allure"):
            stats[key] = grow(value)
    return stats


def give_item(player:Player, item_id:str) -> str:
    item = ITEMS[item_id]
    rarity = RARITY_LABELS[item["rarity"]]
    if len(player.inventory) >= player.bag_size:
        return (f"💎 {player.name} finds {item['name']} ({rarity}), "
                f"but the bag is full. It stays behind.")
    player.inventory.append(Item(item_id, creator="dungeon",
                                 stats=loot_stats(item_id)))
    return f"💎 {player.name} finds {item['name']} ({rarity})!"


def seed_drops(enemies:list[Enemy], party:list[Player]) -> list[str]:
    living = [player for player in party if player.alive]
    lines: list[str] = []
    for drop in DROPS:
        kin = [enemy for enemy in enemies if enemy.tribe == drop["tribe"]]
        if not living or not kin:
            continue
        count = sum(random.random() < drop["chance"] for _ in kin)
        count = min(count, drop["max"])
        if any(enemy.boss for enemy in kin):
            count = drop["boss"]
        for _ in range(count):
            owner = random.choice(living)
            lines.append(drop["text"] + give_item(owner, drop["item"]))
    return lines


def roll_loot(stage:int, party:list[Player]) -> list[str]:
    living = [player for player in party if player.alive]
    if not living:
        return []
    average_int = sum(effective_stat(player, "intelligence")
                      for player in living) / len(living)
    if random.random() > loot_chance(average_int, is_boss_stage(stage)):
        return []
    return [give_item(random.choice(living), roll_item(stage))]


def chest_loot(stage:int, player:Player, gold:int) -> list[str]:
    bonus_stage = stage + CHEST_RARITY_BONUS
    player.gold += gold
    lines = [f"💰 {player.name} pockets {gold} gold."]
    lines.append(give_item(player, roll_item(bonus_stage,
                                             equipment_chance=0.7)))
    if random.random() < 0.5:
        lines.append(give_item(player, roll_item(stage, equipment_chance=0)))
    return lines


def regenerate(party:list[Player], hp_ratio:float, mana_ratio:float) -> None:
    for player in party:
        if not player.alive:
            continue
        player.hp = min(max_hp(player),
                        player.hp + round(max_hp(player) * hp_ratio))
        player.mana = min(max_mana(player),
                          player.mana + round(max_mana(player) * mana_ratio))


def apply_curse(party:list[Player]) -> list[tuple[Player, str]]:
    losses: list[tuple[Player, str]] = []
    for player in party:
        if player.inventory and random.random() < CURSE_ITEM_LOSS_CHANCE:
            index = random.randrange(len(player.inventory))
            losses.append((player, player.inventory.pop(index)))
    return losses
