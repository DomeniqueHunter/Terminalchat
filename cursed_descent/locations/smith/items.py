# Smith presets: weapons and metal armour that Morgrin's forge sells.


ITEMS = {
    "gladiator_helm": {
        "name": "Gladiator Helm", "slot": "head", "rarity": "rare",
        "set": "gladiator", "armor": 3, "bonus": {"strength": 2},
        "for": "gent", "shops": ("smith",),
    },
    "gladiator_cuirass": {
        "name": "Gladiator Cuirass", "slot": "chest", "rarity": "rare",
        "set": "gladiator", "armor": 8, "bonus": {"strength": 2},
        "for": "gent", "shops": ("smith",),
    },
    "gladiator_bracers": {
        "name": "Gladiator Bracers", "slot": "gloves", "rarity": "rare",
        "set": "gladiator", "armor": 2, "bonus": {"strength": 2},
        "for": "gent", "shops": ("smith",),
    },
    "gladiator_sandals": {
        "name": "Gladiator Sandals", "slot": "feet", "rarity": "rare",
        "set": "gladiator", "armor": 2, "bonus": {"strength": 2},
        "for": "gent", "shops": ("smith",),
    },
    "grave_helm": {
        "name": "Grave Helm", "slot": "head", "rarity": "cursed",
        "set": "grave", "armor": 6, "bonus": {"strength": 4, "vitality": -2},
        "for": "gent", "shops": (),
    },
    "grave_gauntlets": {
        "name": "Grave Gauntlets", "slot": "gloves", "rarity": "cursed",
        "set": "grave", "armor": 4, "bonus": {"strength": 4, "vitality": -2},
        "for": "gent", "shops": (),
    },
    "grave_greaves": {
        "name": "Grave Greaves", "slot": "feet", "rarity": "cursed",
        "set": "grave", "armor": 4, "bonus": {"strength": 4, "vitality": -2},
        "for": "gent", "shops": (),
    },
    "assassin_hood": {
        "name": "Assassin Hood", "slot": "head", "rarity": "rare",
        "set": "assassin", "armor": 3, "bonus": {"agility": 2}, "for": "both",
        "shops": ("velvet", "smith"),
    },
    "assassin_jerkin": {
        "name": "Assassin Jerkin", "slot": "chest", "rarity": "rare",
        "set": "assassin", "armor": 8, "bonus": {"agility": 2}, "for": "both",
        "shops": ("velvet", "smith"),
    },
    "shadow_cloak": {
        "name": "Shadow Cloak", "slot": "accessory", "rarity": "rare",
        "set": "assassin", "bonus": {"agility": 2}, "for": "both",
        "shops": ("velvet", "smith"),
    },
    "iron_sword": {
        "name": "Iron Sword", "slot": "weapon", "class": "sword",
        "rarity": "common", "damage": 5, "note": "plain soldier's blade",
        "for": "both", "shops": ("smith",),
    },
    "longsword": {
        "name": "Longsword", "slot": "weapon", "class": "sword",
        "rarity": "rare", "damage": 9, "bonus": {"strength": 1},
        "note": "balanced all-rounder", "for": "both", "shops": ("smith",),
    },
    "rapier": {
        "name": "Rapier", "slot": "weapon", "class": "sword", "rarity": "rare",
        "damage": 7, "allure": 1, "bonus": {"agility": 3},
        "note": "fast duelist's blade", "for": "lady",
        "shops": ("smith", "velvet"),
    },
    "saber": {
        "name": "Cavalry Saber", "slot": "weapon", "class": "sword",
        "rarity": "rare", "damage": 9, "bonus": {"agility": 1},
        "note": "curved slashing blade", "for": "gent", "shops": ("smith",),
    },
    "greatsword": {
        "name": "Greatsword", "slot": "weapon", "class": "sword",
        "rarity": "epic", "damage": 19,
        "bonus": {"strength": 4, "agility": -1}, "note": "heavy two-hander",
        "for": "gent", "shops": ("smith",),
    },
    "kitchen_knife": {
        "name": "Kitchen Knife", "slot": "weapon", "class": "dagger",
        "rarity": "common", "damage": 3, "note": "better than nothing",
        "for": "both", "shops": ("smith",),
    },
    "stiletto": {
        "name": "Stiletto", "slot": "weapon", "class": "dagger",
        "rarity": "rare", "damage": 6, "allure": 1, "bonus": {"agility": 3},
        "note": "thin and elegant", "for": "lady",
        "shops": ("smith", "velvet"),
    },
    "poison_dagger": {
        "name": "Poisoned Dagger", "slot": "weapon", "class": "dagger",
        "rarity": "epic", "damage": 12, "bonus": {"agility": 4},
        "note": "coated blade", "for": "both", "shops": ("smith",),
    },
    "sacrificial_dagger": {
        "name": "Sacrificial Dagger", "slot": "weapon", "class": "dagger",
        "rarity": "cursed", "damage": 17,
        "bonus": {"vitality": -3, "agility": 3}, "note": "drinks what it cuts",
        "for": "both", "shops": (),
    },
    "hand_axe": {
        "name": "Hand Axe", "slot": "weapon", "class": "axe",
        "rarity": "common", "damage": 5, "bonus": {"strength": 1},
        "note": "wood and bite", "for": "both", "shops": ("smith",),
    },
    "battle_axe": {
        "name": "Battle Axe", "slot": "weapon", "class": "axe",
        "rarity": "rare", "damage": 11, "bonus": {"strength": 3},
        "note": "two-handed chopper", "for": "gent", "shops": ("smith",),
    },
    "double_axe": {
        "name": "Double-Headed Axe", "slot": "weapon", "class": "axe",
        "rarity": "epic", "damage": 21, "bonus": {"strength": 5},
        "note": "two blades, no mercy", "for": "gent", "shops": ("smith",),
    },
    "headsman_axe": {
        "name": "Headsman's Axe", "slot": "weapon", "class": "axe",
        "rarity": "cursed", "damage": 27,
        "bonus": {"strength": 4, "vitality": -3},
        "note": "cold iron, old blood", "for": "both", "shops": (),
    },
    "walking_staff": {
        "name": "Walking Staff", "slot": "weapon", "class": "staff",
        "rarity": "common", "damage": 2, "bonus": {"intelligence": 1},
        "note": "pilgrim's stick", "for": "both", "shops": ("smith",),
    },
    "crystal_staff": {
        "name": "Crystal Staff", "slot": "weapon", "class": "staff",
        "rarity": "rare", "damage": 3, "bonus": {"intelligence": 4},
        "note": "focus crystal on top", "for": "both", "shops": ("smith",),
    },
    "rune_scepter": {
        "name": "Rune Scepter", "slot": "weapon", "class": "staff",
        "rarity": "epic", "damage": 8, "bonus": {"intelligence": 6},
        "note": "carved with old runes", "for": "both", "shops": ("smith",),
    },
    "wand": {
        "name": "Silver Wand", "slot": "weapon", "class": "staff",
        "rarity": "rare", "damage": 2, "allure": 1,
        "bonus": {"intelligence": 3}, "note": "fine and light", "for": "lady",
        "shops": ("smith", "velvet"),
    },
    "riding_crop": {
        "name": "Riding Crop", "slot": "weapon", "class": "whip",
        "rarity": "common", "damage": 3, "allure": 1, "bonus": {"agility": 1},
        "note": "sharp little sting", "for": "both",
        "shops": ("smith", "velvet"),
    },
    "cat_o_nine": {
        "name": "Cat-o'-Nine-Tails", "slot": "weapon", "class": "whip",
        "rarity": "rare", "damage": 8, "allure": 1,
        "bonus": {"strength": 1, "agility": 1},
        "note": "nine tails, nine welts", "for": "both",
        "shops": ("smith", "velvet"),
    },
    "chain_whip": {
        "name": "Chain Whip", "slot": "weapon", "class": "whip",
        "rarity": "epic", "damage": 16, "allure": 2,
        "bonus": {"strength": 3, "agility": 2},
        "note": "chain links in leather", "for": "lady",
        "shops": ("smith", "velvet"),
    },
    "birch_rod": {
        "name": "Birch Rod", "slot": "weapon", "class": "whip",
        "rarity": "rare", "damage": 7, "allure": 1, "bonus": {"agility": 2},
        "note": "schoolmaster's favourite", "for": "both",
        "shops": ("velvet",),
    },
    "club": {
        "name": "Wooden Club", "slot": "weapon", "class": "blunt",
        "rarity": "common", "damage": 5, "bonus": {"strength": 1},
        "note": "simple and heavy", "for": "both", "shops": ("smith",),
    },
    "mace": {
        "name": "Flanged Mace", "slot": "weapon", "class": "blunt",
        "rarity": "rare", "damage": 10, "bonus": {"strength": 2},
        "note": "dents helmets", "for": "gent", "shops": ("smith",),
    },
    "warhammer": {
        "name": "Warhammer", "slot": "weapon", "class": "blunt",
        "rarity": "epic", "damage": 20,
        "bonus": {"strength": 4, "agility": -1}, "note": "crushes plate",
        "for": "gent", "shops": ("smith",),
    },
    "morning_star": {
        "name": "Morning Star", "slot": "weapon", "class": "blunt",
        "rarity": "cursed", "damage": 24,
        "bonus": {"strength": 3, "vitality": -3}, "note": "spiked and cruel",
        "for": "both", "shops": (),
    },
    "spear": {
        "name": "Spear", "slot": "weapon", "class": "polearm",
        "rarity": "common", "damage": 6, "bonus": {"agility": 1},
        "note": "reach is everything", "for": "both", "shops": ("smith",),
    },
    "halberd": {
        "name": "Halberd", "slot": "weapon", "class": "polearm",
        "rarity": "rare", "damage": 12, "bonus": {"strength": 2},
        "note": "axe, spike and hook", "for": "gent", "shops": ("smith",),
    },
    "naginata": {
        "name": "Naginata", "slot": "weapon", "class": "polearm",
        "rarity": "rare", "damage": 11, "allure": 1,
        "bonus": {"agility": 2, "strength": 1},
        "note": "curved blade on a long shaft", "for": "lady",
        "shops": ("smith", "velvet"),
    },
    "glaive": {
        "name": "Glaive", "slot": "weapon", "class": "polearm",
        "rarity": "rare", "damage": 10, "bonus": {"agility": 2},
        "note": "blade on a pole", "for": "both", "shops": ("smith",),
    },
    "sling": {
        "name": "Sling", "slot": "weapon", "class": "ranged",
        "rarity": "common", "damage": 3, "bonus": {"agility": 1},
        "note": "a leather strap", "for": "both", "shops": ("smith",),
    },
    "shortbow": {
        "name": "Shortbow", "slot": "weapon", "class": "ranged",
        "rarity": "common", "damage": 5, "bonus": {"agility": 2},
        "note": "quick and light", "for": "both", "shops": ("smith",),
    },
    "longbow": {
        "name": "Longbow", "slot": "weapon", "class": "ranged",
        "rarity": "rare", "damage": 11, "bonus": {"agility": 3},
        "note": "long reach", "for": "both", "shops": ("smith",),
    },
    "crossbow": {
        "name": "Crossbow", "slot": "weapon", "class": "ranged",
        "rarity": "rare", "damage": 13, "bonus": {"agility": -1},
        "note": "slow, but it hits", "for": "both", "shops": ("smith",),
    },
    "flintlock": {
        "name": "Flintlock Pistol", "slot": "weapon", "class": "ranged",
        "rarity": "epic", "damage": 15, "bonus": {"agility": 1},
        "note": "one loud shot", "for": "both", "shops": ("smith",),
    },
    "fighting_gloves": {
        "name": "Fighting Gloves", "slot": "weapon", "class": "fist",
        "rarity": "rare", "damage": 8, "bonus": {"strength": 2, "agility": 1},
        "note": "knuckles and leather", "for": "both", "shops": ("smith",),
    },
    "cat_claws": {
        "name": "Cat Claws", "slot": "weapon", "class": "fist",
        "rarity": "epic", "damage": 13, "allure": 1, "bonus": {"agility": 4},
        "note": "blades on the fingers", "for": "lady",
        "shops": ("smith", "velvet"),
    },
    "manacles": {
        "name": "Iron Manacles", "slot": "weapon", "class": "chain",
        "rarity": "rare", "damage": 6, "allure": 1,
        "bonus": {"strength": 1, "vitality": 1},
        "note": "for binding, or hitting", "for": "both", "shops": ("velvet",),
    },
    "gladius": {
        "name": "Gladius", "slot": "weapon", "class": "sword",
        "rarity": "rare", "set": "gladiator", "damage": 9,
        "bonus": {"strength": 2}, "for": "gent", "shops": ("smith",),
    },
}


ITEM_SETS = {
    "gladiator": {
        "name": "Gladiator",
        "bonuses": {
            2: {"bonus": {"strength": 2}},
            4: {"armor": 4},
            6: {"melee": 0.12, "armor": 4},
        },
    },
    "grave": {
        "name": "Grave Knight",
        "bonuses": {
            2: {"bonus": {"strength": 3}},
            4: {"melee": 0.12},
            6: {"melee": 0.2, "crit": 0.1},
        },
    },
    "assassin": {
        "name": "Assassin",
        "bonuses": {
            2: {"bonus": {"agility": 2}},
            4: {"crit": 0.08},
            6: {"crit": 0.12, "melee": 0.1},
        },
    },
}
