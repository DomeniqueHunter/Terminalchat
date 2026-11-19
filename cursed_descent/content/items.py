RARITY_LABELS = {
    "common": "Common", "rare": "Rare",
    "epic": "Epic", "legendary": "Legendary", "cursed": "Cursed",
    "couture": "Couture",
}

ITEM_SETS = {
    "ice_queen": {
        "name": "Ice Queen",
        "bonuses": {
            2: {"bonus": {"intelligence": 3}},
            4: {"armor": 3},
            6: {"crit": 0.1, "allure": 4},
        },
    },
    "hunter": {
        "name": "Big Game Hunter",
        "bonuses": {
            2: {"bonus": {"agility": 2}},
            4: {"crit": 0.08},
            5: {"melee": 0.1, "crit": 0.1},
        },
    },
    "butcher": {
        "name": "Butcher",
        "bonuses": {
            2: {"bonus": {"strength": 2}},
            4: {"melee": 0.1},
            5: {"melee": 0.15, "armor": 4},
        },
    },
    "domina": {
        "name": "Domina",
        "bonuses": {
            2: {"bonus": {"strength": 2}},
            4: {"melee": 0.10, "armor": 3},
            6: {"melee": 0.15, "crit": 0.10, "allure": 5},
        },
    },
}

ITEMS = {
    "domina_whip": {
        "class": "whip", "for": "lady", "shops": ("smith",),
        "name": "Domina's Bullwhip", "slot": "weapon", "rarity": "epic",
        "set": "domina", "damage": 18, "allure": 2,
        "bonus": {"strength": 3, "agility": 2},
        "note": "crack it once and everyone kneels",
    },
    "domina_cap": {
        "for": "lady", "shops": ("velvet",),
        "name": "Domina's Peaked Leather Cap", "slot": "head",
        "rarity": "epic", "set": "domina", "armor": 4, "allure": 2,
        "bonus": {"strength": 1, "vitality": 1},
    },
    "domina_corset": {
        "for": "lady", "shops": ("velvet",),
        "name": "Domina's Steel-Boned Corset", "slot": "chest",
        "rarity": "epic", "set": "domina", "armor": 10, "allure": 4,
        "bonus": {"vitality": 2, "strength": 1},
        "note": "breathing is optional, obedience is not",
    },
    "domina_gloves": {
        "for": "lady", "shops": ("velvet",),
        "name": "Domina's Opera Latex Gloves", "slot": "gloves",
        "rarity": "epic", "set": "domina", "armor": 3, "allure": 2,
        "bonus": {"strength": 2},
    },
    "domina_boots": {
        "for": "lady", "shops": ("velvet",),
        "name": "Domina's Thigh-High Stiletto Boots", "slot": "feet",
        "rarity": "epic", "set": "domina", "damage": 4, "armor": 3,
        "allure": 3, "bonus": {"agility": 1},
        "note": "the heel is a weapon",
    },
    "domina_crop": {
        "for": "lady", "shops": ("velvet",),
        "name": "Domina's Riding Crop", "slot": "accessory",
        "rarity": "epic", "set": "domina", "damage": 3, "allure": 2,
        "bonus": {"strength": 1, "agility": 1},
    },
    "moonshine": {
        "name": "Wanderer's Moonshine", "slot": "consumable",
        "rarity": "common", "heal": 40, "mana": 40, "price": 20,
        "no_loot": True, "note": "a thank-you from a very satisfied wanderer",
    },
    "milk_bottle": {
        "name": "Bottle of Fresh Milk", "slot": "consumable",
        "rarity": "common", "heal": 50, "mana": 20, "price": 15,
        "no_loot": True, "note": "still warm, if you don't ask",
    },
    "fish_pike": {
        "name": "Black-Pond Pike", "slot": "consumable", "rarity": "common",
        "heal": 30, "price": 12, "no_loot": True,
        "note": "long, mean and very fresh",
    },
    "fish_perch": {
        "name": "Striped Perch", "slot": "consumable", "rarity": "common",
        "heal": 25, "mana": 10, "price": 10, "no_loot": True,
        "note": "small, sweet and bony",
    },
    "fish_eel": {
        "name": "Pond Eel", "slot": "consumable", "rarity": "common",
        "heal": 35, "price": 14, "no_loot": True,
        "note": "still wriggling in the bag",
    },
    "fish_goldcarp": {
        "name": "Gold Carp", "slot": "consumable", "rarity": "rare",
        "heal": 60, "price": 90, "no_loot": True,
        "note": "scales like coins, fat as a pillow",
    },
    "fish_blindcat": {
        "name": "Blind Catfish", "slot": "consumable", "rarity": "rare",
        "heal": 70, "price": 80, "no_loot": True,
        "note": "from the deep end, whiskers longer than your arm",
    },
    "fish_moortrout": {
        "name": "Moor Trout", "slot": "consumable", "rarity": "rare",
        "heal": 40, "mana": 70, "price": 85, "no_loot": True,
        "note": "tastes faintly of lightning",
    },
    "fish_sturgeon": {
        "name": "Deep Sturgeon", "slot": "consumable", "rarity": "epic",
        "heal": 160, "price": 220, "no_loot": True,
        "note": "armoured, ancient and rich",
    },
    "fish_siren": {
        "name": "Siren Salmon", "slot": "consumable", "rarity": "epic",
        "heal": 120, "mana": 120, "price": 260, "no_loot": True,
        "note": "hums softly if you hold it to your ear",
    },
    "giant_catch": {
        "name": "Giant Catch", "slot": "consumable", "rarity": "epic",
        "heal": 250, "mana": 120, "price": 400, "no_loot": True,
        "note": "steaks off <<npc.old_gorm_first>>'s biggest fish – bait costs, "
                "but it pays",
    },
    "cum_flask": {
        "name": "Flask of Stud Cream", "slot": "consumable",
        "rarity": "common", "heal": 60, "mana": 30, "price": 30,
        "no_loot": True, "note": "thick, warm and unmistakably musky – "
                                 "<<npc.old_trotter_short>> swears it's good for you",
    },
    "cream_jar": {
        "name": "Jar of Thick Cream", "slot": "consumable",
        "rarity": "rare", "heal": 90, "mana": 30, "price": 40,
        "no_loot": True, "note": "the good stuff",
    },
    "brew_yogurt_drink": {
        "name": "<<npc.astrid_last>> Yogurt Drink", "slot": "consumable",
        "rarity": "common", "heal": 70, "price": 35, "no_loot": True,
        "note": "thick and cold, heavy musk, slightly salty",
    },
    "brew_kefir": {
        "name": "<<npc.astrid_last>> Honey Kefir", "slot": "consumable",
        "rarity": "common", "heal": 20, "mana": 60, "price": 45,
        "no_loot": True, "note": "creamy and faintly fizzy, heavy musk, "
                                 "slightly salty",
    },
    "brew_cream_lassi": {
        "name": "<<npc.astrid_last>> Cream Lassi", "slot": "consumable",
        "rarity": "rare", "heal": 140, "mana": 40, "price": 90,
        "no_loot": True, "note": "rich and a little too warm, heavy musk, slightly salty",
    },
    "brew_house_special": {
        "name": "<<npc.astrid_first>>'s House Special", "slot": "consumable",
        "rarity": "epic", "heal": 250, "mana": 80, "price": 220,
        "no_loot": True,
        "note": "the recipe is a secret – don't ask what's in the keg",
    },
    "stew_jar": {
        "name": "Jar of Adventurer Stew", "slot": "consumable",
        "rarity": "common", "heal": 70, "mana": 10, "price": 20,
        "no_loot": True, "note": "made from a former colleague",
    },
    "bread_loaf": {
        "name": "Hardtack Loaf", "slot": "consumable", "rarity": "common",
        "price": 8, "needs": {"hunger": -35},
    },
    "firewood": {
        "name": "Bundle of Firewood", "slot": "consumable",
        "rarity": "common", "price": 6, "no_loot": True,
        "note": "dry wood with kindling, for one camp fire ([light] at "
                "a camp site)",
    },
    "water_flask": {
        "name": "Water Flask", "slot": "consumable", "rarity": "common",
        "price": 6, "needs": {"thirst": -40},
    },
    "wake_tonic": {
        "name": "Wake-Up Tonic", "slot": "consumable", "rarity": "common",
        "price": 35, "needs": {"sleep": -35},
    },
    "cooling_draught": {
        "name": "Cooling Draught", "slot": "consumable", "rarity": "common",
        "price": 35, "needs": {"arousal": -40},
    },
    "potion_small": {
        "name": "Small Healing Potion", "slot": "consumable",
        "rarity": "common", "heal": 40, "price": 25,
    },
    "potion_large": {
        "name": "Large Healing Potion", "slot": "consumable",
        "rarity": "rare", "heal": 120, "price": 90,
    },
    "mana_potion": {
        "name": "Mana Potion", "slot": "consumable",
        "rarity": "common", "mana": 40, "price": 30,
    },
    "elixir": {
        "name": "Elixir of the Depths", "slot": "consumable",
        "rarity": "epic", "heal": 300, "mana": 100, "price": 300,
    },
    "rusty_sword": {
        "class": "sword", "shops": ("smith",),
        "name": "Rusty Sword", "slot": "weapon",
        "rarity": "common", "damage": 3,
    },
    "oak_staff": {
        "class": "staff", "shops": ("smith",),
        "name": "Oak Staff", "slot": "weapon",
        "rarity": "common", "bonus": {"intelligence": 2},
    },
    "war_axe": {
        "class": "axe", "shops": ("smith",),
        "name": "War Axe", "slot": "weapon",
        "rarity": "rare", "damage": 8, "bonus": {"strength": 2},
    },
    "shadow_dagger": {
        "class": "dagger", "shops": ("smith",), "set": "assassin",
        "name": "Shadow Dagger", "slot": "weapon",
        "rarity": "rare", "damage": 5, "bonus": {"agility": 3},
    },
    "arcane_staff": {
        "class": "staff", "shops": ("smith",), "set": "mage",
        "name": "Arcane Staff", "slot": "weapon",
        "rarity": "rare", "damage": 2, "bonus": {"intelligence": 5},
    },
    "bone_cleaver": {
        "class": "axe", "shops": ("smith",),
        "name": "Bone Cleaver", "slot": "weapon",
        "rarity": "epic", "damage": 15, "bonus": {"strength": 4},
    },
    "cursed_blade": {
        "class": "sword", "for": "gent", "set": "grave",
        "name": "Soul Drinker", "slot": "weapon",
        "rarity": "cursed", "damage": 25, "bonus": {"vitality": -4},
    },
    "leather_vest": {
        "shops": ("smith", "velvet"),
        "name": "Leather Vest", "slot": "chest",
        "rarity": "common", "armor": 3,
    },
    "chainmail": {
        "shops": ("smith",),
        "name": "Chainmail", "slot": "chest",
        "rarity": "rare", "armor": 7, "bonus": {"agility": -1},
    },
    "troll_hide": {
        "shops": ("smith",),
        "name": "Troll Hide", "slot": "chest",
        "rarity": "epic", "armor": 12, "bonus": {"vitality": 3},
    },
    "cursed_plate": {
        "for": "gent", "set": "grave",
        "name": "Grave Plate", "slot": "chest",
        "rarity": "cursed", "armor": 20, "bonus": {"agility": -5},
    },
    "lucky_charm": {
        "shops": ("smith", "velvet"),
        "name": "Lucky Charm", "slot": "accessory",
        "rarity": "common", "bonus": {"agility": 2},
    },
    "ring_of_vigor": {
        "shops": ("smith",),
        "name": "Ring of Vigor", "slot": "accessory",
        "rarity": "rare", "bonus": {"vitality": 3},
    },
    "amulet_of_mind": {
        "shops": ("smith",), "set": "mage",
        "name": "Amulet of the Mind", "slot": "accessory",
        "rarity": "rare", "bonus": {"intelligence": 3},
    },
    "gorgon_eye": {
        "shops": ("smith",),
        "name": "Gorgon Eye", "slot": "accessory",
        "rarity": "epic", "bonus": {"intelligence": 4, "agility": 2},
    },
    "cursed_skull": {
        "for": "gent", "set": "grave",
        "name": "Whispering Skull", "slot": "accessory",
        "rarity": "cursed",
        "bonus": {"strength": 5, "intelligence": 5, "vitality": -3},
    },
    "iron_helmet": {
        "shops": ("smith", "velvet"),
        "name": "Iron Helmet", "slot": "head",
        "rarity": "common", "armor": 2,
    },
    "leather_boots": {
        "shops": ("smith", "velvet"), "set": "assassin",
        "name": "Leather Boots", "slot": "feet",
        "rarity": "common", "armor": 1, "bonus": {"agility": 1},
    },
    "bikini_armor": {
        "for": "lady", "shops": ("velvet",),
        "name": "Bikini Armor", "slot": "chest", "rarity": "rare",
        "armor": 8, "allure": 3, "bonus": {"agility": 1},
        "note": "covers almost nothing, protects almost everything",
    },
    "chainmail_bikini": {
        "for": "lady", "shops": ("velvet",), "set": "valkyrie",
        "name": "Chainmail Bikini", "slot": "chest", "rarity": "epic",
        "armor": 14, "allure": 4, "bonus": {"agility": 2},
        "note": "nobody knows how it works",
    },
    "latex_catsuit": {
        "shops": ("velvet",), "set": "latex",
        "name": "Latex Catsuit", "slot": "chest", "rarity": "rare",
        "armor": 5, "allure": 3, "bonus": {"agility": 3},
        "note": "squeaks when you sneak",
    },
    "cursed_corset": {
        "set": "denial",
        "name": "Corset of Binding", "slot": "chest", "rarity": "cursed",
        "armor": 11, "allure": 5, "bonus": {"vitality": -2},
        "note": "breathing is optional",
    },
    "high_heels": {
        "for": "lady", "shops": ("velvet",), "set": "succubus",
        "name": "High Heel Boots", "slot": "feet", "rarity": "rare",
        "damage": 3, "allure": 3, "bonus": {"agility": -1},
        "note": "stiletto kicks hurt",
    },
    "latex_boots": {
        "shops": ("velvet",), "set": "latex",
        "name": "Thigh-High Latex Boots", "slot": "feet", "rarity": "epic",
        "armor": 2, "allure": 4, "bonus": {"agility": 2},
    },
    "fishnets": {
        "for": "lady", "shops": ("velvet",), "set": "maid",
        "name": "Fishnet Stockings", "slot": "feet", "rarity": "common",
        "allure": 2, "bonus": {"agility": 1},
    },
    "gimp_mask": {
        "shops": ("velvet",), "set": "latex",
        "name": "Gimp Mask", "slot": "head", "rarity": "common",
        "armor": 3, "allure": 2, "bonus": {"vitality": 2, "intelligence": -1},
        "note": "spells come out a little muffled",
    },
    "kitty_ears": {
        "shops": ("velvet",),
        "name": "Kitty Ear Headband", "slot": "head", "rarity": "common",
        "allure": 2, "bonus": {"agility": 1},
    },
    "leather_collar": {
        "for": "lady", "shops": ("velvet",), "set": "succubus",
        "name": "Leather Collar with Bell", "slot": "accessory",
        "rarity": "common", "allure": 2, "bonus": {"vitality": 1},
        "note": "jingles at the worst moments",
    },
    "cock_sleeve": {
        "for": "gent", "shops": ("velvet",),
        "name": "Cock Sleeve", "slot": "crotch", "rarity": "rare",
        "allure": 3, "bonus": {"strength": 2, "vitality": 1},
        "requires": ["Male", "Herm", "Shemale", "Male-Herm", "Transgender"],
        "note": "surprisingly good for morale",
    },
    "loincloth": {
        "shops": ("smith", "velvet"),
        "name": "Loincloth", "slot": "crotch", "rarity": "common",
        "armor": 1, "bonus": {"agility": 1},
    },
    "steel_codpiece": {
        "for": "gent", "shops": ("smith",), "set": "gladiator",
        "name": "Steel Codpiece", "slot": "crotch", "rarity": "rare",
        "armor": 4, "allure": 1, "bonus": {"vitality": 1},
        "requires": ["Male", "Herm", "Shemale", "Male-Herm", "Transgender"],
        "note": "clangs when you run",
    },
    "chastity_belt": {
        "shops": ("velvet",), "set": "denial",
        "name": "Chastity Belt", "slot": "crotch", "rarity": "rare",
        "armor": 5, "allure": 2,
        "note": "key not included",
    },
    "cursed_cage": {
        "for": "gent",
        "name": "Locked Cage of Denial", "slot": "crotch", "rarity": "cursed",
        "armor": 3, "allure": 4, "bonus": {"strength": 4, "intelligence": -2},
        "requires": ["Male", "Herm", "Shemale", "Male-Herm", "Transgender"],
        "note": "nobody remembers where the key went",
    },
    "leather_gloves": {
        "shops": ("smith", "velvet"), "set": "assassin",
        "name": "Leather Gloves", "slot": "gloves", "rarity": "common",
        "armor": 1, "bonus": {"strength": 1},
    },
    "spiked_gauntlets": {
        "shops": ("smith",),
        "name": "Spiked Gauntlets", "slot": "gloves", "rarity": "rare",
        "damage": 4, "armor": 2,
    },
    "opera_gloves": {
        "shops": ("velvet",), "set": "latex",
        "name": "Latex Opera Gloves", "slot": "gloves", "rarity": "rare",
        "allure": 2, "bonus": {"agility": 1, "intelligence": 1},
        "note": "elbow-length elegance",
    },
    "lace_lingerie": {
        "for": "lady", "shops": ("velvet",),
        "name": "Lace Lingerie Set", "slot": "lingerie", "rarity": "common",
        "allure": 2,
    },
    "garter_belt": {
        "for": "lady", "shops": ("velvet",),
        "name": "Silk Garter Belt", "slot": "lingerie", "rarity": "rare",
        "allure": 3, "bonus": {"agility": 1},
    },
    "bodystocking": {
        "shops": ("velvet",),
        "name": "Fishnet Bodystocking", "slot": "lingerie", "rarity": "rare",
        "allure": 3, "bonus": {"agility": 2},
        "note": "leaves very little to the imagination",
    },
    "succubus_lace": {
        "for": "lady", "set": "succubus",
        "name": "Succubus Lace", "slot": "lingerie", "rarity": "cursed",
        "allure": 6, "bonus": {"intelligence": 3, "vitality": -2},
        "note": "it whispers compliments – and suggestions",
    },
    "maid_uniform": {
        "for": "lady", "set": "maid",
        "name": "Maid Uniform", "slot": "chest", "rarity": "rare",
        "armor": 3, "allure": 3, "bonus": {"agility": 1}, "no_loot": True,
        "note": "starched, spotless and impossible to take off with dignity",
    },
    "cow_bikini": {
        "for": "lady", "shops": ("velvet",), "set": "milkmaid",
        "name": "Cow-Print Bikini", "slot": "chest", "rarity": "rare",
        "armor": 6, "allure": 3, "bonus": {"vitality": 1},
        "note": "moo",
    },
    "recruiter_cane": {
        "class": "whip",
        "name": "Miss Starch's Cane", "slot": "weapon", "rarity": "rare",
        "damage": 9, "bonus": {"agility": 1}, "no_loot": True,
        "note": "polite, precise and very, very stern",
    },
    "prefect_badge": {
        "name": "Prefect Badge", "slot": "accessory", "rarity": "rare",
        "allure": 2, "bonus": {"intelligence": 1}, "no_loot": True,
        "note": "grants authority over exactly nobody in the dungeon",
    },
    "pith_helmet": {
        "for": "gent", "set": "hunter",
        "name": "<<npc.reginald_first>>'s Pith Helmet", "slot": "head",
        "rarity": "rare", "armor": 3, "bonus": {"intelligence": 1},
        "no_loot": True, "note": "monocle not included",
    },
    "hunting_blunderbuss": {
        "class": "ranged", "for": "gent", "set": "hunter",
        "name": "Big Game Blunderbuss", "slot": "weapon", "rarity": "epic",
        "damage": 14, "bonus": {"agility": -1},
        "no_loot": True, "note": "loud, inaccurate, magnificent",
    },
    "safari_jacket": {
        "for": "gent", "set": "hunter",
        "name": "Safari Jacket", "slot": "chest", "rarity": "rare",
        "armor": 7, "bonus": {"agility": 2},
        "no_loot": True, "note": "so many pockets",
    },
    "couture_gown": {
        "for": "lady",
        "name": "<<boutique.owner_short>> Couture Gown", "slot": "chest",
        "rarity": "epic",
        "armor": 12, "allure": 8, "bonus": {"agility": 4, "vitality": 3},
        "no_loot": True, "note": "one of a kind – hopefully not made of "
                                 "anyone",
    },
    "aldric_boots": {
        "name": "Aldric Grimhold Leather Boots ★", "slot": "feet",
        "rarity": "epic", "armor": 6, "allure": 9,
        "bonus": {"strength": 8, "vitality": 6}, "no_loot": True,
        "note": "black, polished, a name carved into each heel – handmade "
                "by <<boutique.owner>> from Lord Aldric Grimhold, who never "
                "left his wife's feet",
    },
    "aldric_corset": {
        "name": "Aldric Grimhold Leather Corset ★", "slot": "chest",
        "rarity": "epic", "armor": 8, "allure": 8,
        "bonus": {"vitality": 10}, "no_loot": True,
        "note": "tough leather, handmade by <<boutique.owner>> from Lord "
                "Aldric Grimhold",
    },
    "aldric_gloves": {
        "name": "Aldric Grimhold Leather Gloves ★", "slot": "gloves",
        "rarity": "epic", "armor": 3, "allure": 6,
        "bonus": {"strength": 6}, "no_loot": True,
        "note": "supple leather, handmade by <<boutique.owner>> from Lord "
                "Aldric Grimhold",
    },
    "velvet_gloves": {
        "for": "lady", "set": "ice_queen",
        "name": "<<npc.velvet_first>> Evening Gloves", "slot": "gloves", "rarity": "epic",
        "armor": 4, "allure": 5, "bonus": {"intelligence": 4, "strength": 2},
        "no_loot": True,
    },
    "frost_crown": {
        "for": "lady", "set": "ice_queen",
        "name": "Crown of Black Frost", "slot": "head", "rarity": "cursed",
        "armor": 5, "allure": 4, "bonus": {"intelligence": 4},
        "no_loot": True, "note": "still cold enough to burn",
    },
    "rime_gown": {
        "for": "lady", "set": "ice_queen",
        "name": "<<npc.isolde_first>>'s Rime Gown", "slot": "chest",
        "rarity": "cursed", "armor": 10, "allure": 6,
        "bonus": {"vitality": 2, "agility": 1},
        "no_loot": True, "note": "woven from snowflakes, never melts",
    },
    "soulfrost_scepter": {
        "class": "staff", "for": "lady", "set": "ice_queen",
        "name": "Soulfrost Scepter", "slot": "weapon", "rarity": "cursed",
        "damage": 18, "bonus": {"intelligence": 3},
        "no_loot": True, "note": "whispers marriage proposals at night",
    },
    "butcher_cleaver": {
        "class": "axe", "for": "gent", "set": "butcher",
        "name": "<<npc.hamhock_first>>'s Butcher Cleaver", "slot": "weapon",
        "rarity": "epic", "damage": 20, "bonus": {"strength": 4},
        "no_loot": True, "note": "still smells of smoked ham",
    },
    "butcher_apron": {
        "for": "gent", "set": "butcher",
        "name": "Blood-Stained Leather Apron", "slot": "chest",
        "rarity": "epic", "armor": 9, "bonus": {"vitality": 3},
        "no_loot": True,
    },
    "farmer_pitchfork": {
        "class": "polearm",
        "name": "<<npc.old_trotter_first>>'s Pitchfork", "slot": "weapon",
        "rarity": "epic", "damage": 17, "bonus": {"strength": 2,
                                                  "agility": 2},
        "no_loot": True, "note": "three prongs, all of them sharp",
    },
    "straw_hat": {
        "name": "Farmer's Straw Hat", "slot": "head", "rarity": "rare",
        "armor": 2, "allure": 2, "bonus": {"vitality": 3},
        "no_loot": True,
    },
    "branding_iron": {
        "name": "<<npc.old_trotter_short>> Farm Branding Iron", "slot": "accessory",
        "rarity": "epic", "damage": 6, "bonus": {"strength": 2},
        "allure": 1, "no_loot": True, "note": "leaves a lasting impression",
    },
    "farm_eggs": {
        "name": "Basket of Farm Eggs", "slot": "consumable",
        "rarity": "common", "heal": 60, "price": 25, "no_loot": True,
    },
    "meat_boar": {
        "name": "Boar Ham (raw)", "slot": "consumable", "rarity": "common",
        "heal": 30, "price": 30, "no_loot": True, "raw_meat": True,
        "note": "cook it over a campfire",
    },
    "cooked_boar": {
        "name": "Roast Boar Ham", "slot": "consumable", "rarity": "common",
        "heal": 120, "mana": 20, "price": 45, "no_loot": True,
    },
    "meat_boar_sausage": {
        "name": "Boar Sausages (raw)", "slot": "consumable",
        "rarity": "common", "heal": 25, "price": 20, "no_loot": True,
        "raw_meat": True, "note": "cook it over a campfire",
    },
    "cooked_boar_sausage": {
        "name": "Grilled Boar Sausages", "slot": "consumable",
        "rarity": "common", "heal": 90, "mana": 20, "price": 30,
        "no_loot": True,
    },
    "farm_bread": {
        "name": "Farmhouse Bread", "slot": "consumable", "rarity": "common",
        "heal": 40, "mana": 30, "price": 20, "no_loot": True,
    },
    "masterwork_blade": {
        "class": "sword",
        "name": "<<npc.morgrin_first>>'s Masterwork Blade", "slot": "weapon",
        "rarity": "epic", "damage": 26, "bonus": {"strength": 4},
        "no_loot": True, "smith": True, "price": 1500,
        "note": "forged in green fire",
    },
    "ashen_staff": {
        "class": "staff",
        "name": "Ashen Staff", "slot": "weapon", "rarity": "epic",
        "damage": 10, "bonus": {"intelligence": 8}, "no_loot": True,
        "smith": True, "price": 1500, "note": "warm to the touch, always",
    },
    "infernal_maul": {
        "class": "blunt",
        "name": "Infernal Maul", "slot": "weapon", "rarity": "cursed",
        "damage": 38, "bonus": {"strength": 6, "agility": -2},
        "no_loot": True, "smith": True, "price": 4000, "soul_hunger": True,
        "note": "soul-hungry: it may keep you when you fall",
    },
    "whisperwood_staff": {
        "class": "staff",
        "name": "Whisperwood Staff", "slot": "weapon", "rarity": "cursed",
        "damage": 14, "bonus": {"intelligence": 13, "vitality": 3},
        "no_loot": True, "smith": True, "price": 6000, "soul_hunger": True,
        "note": "soul-hungry – the wood whispers names",
    },
    "soul_eater": {
        "class": "sword",
        "name": "Soul-Eater", "slot": "weapon", "rarity": "cursed",
        "damage": 50, "bonus": {"strength": 8, "agility": 4},
        "no_loot": True, "smith": True, "price": 9000, "soul_hunger": True,
        "note": "soul-hungry – it has eaten many, it is never full",
    },
    "designer_heels": {
        "for": "lady",
        "name": "Red-Soled Designer Heels", "slot": "feet", "rarity": "epic",
        "damage": 8, "armor": 3, "allure": 6,
        "bonus": {"agility": 4, "strength": 1},
        "no_loot": True, "note": "the heels are sharper than they look",
    },
    "frost_slippers": {
        "name": "Frost Slippers", "slot": "feet", "rarity": "cursed",
        "set": "ice_queen", "armor": 4, "allure": 4,
        "bonus": {"intelligence": 4, "vitality": -2}, "for": "lady",
        "shops": (),
    },
    "frost_pendant": {
        "name": "Black Frost Pendant", "slot": "accessory", "rarity": "cursed",
        "set": "ice_queen", "allure": 4,
        "bonus": {"intelligence": 4, "vitality": -2}, "for": "lady",
        "shops": (),
    },
    "hunter_boots": {
        "name": "Hunter Boots", "slot": "feet", "rarity": "epic",
        "set": "hunter", "armor": 4, "bonus": {"agility": 3}, "for": "gent",
        "shops": (),
    },
    "hunter_gloves": {
        "name": "Hunter Gloves", "slot": "gloves", "rarity": "epic",
        "set": "hunter", "armor": 4, "bonus": {"agility": 3}, "for": "gent",
        "shops": (),
    },
    "butcher_cap": {
        "name": "Butcher Cap", "slot": "head", "rarity": "epic",
        "set": "butcher", "armor": 5, "bonus": {"strength": 3}, "for": "gent",
        "shops": (),
    },
    "butcher_gloves": {
        "name": "Butcher Gloves", "slot": "gloves", "rarity": "epic",
        "set": "butcher", "armor": 4, "bonus": {"strength": 3}, "for": "gent",
        "shops": (),
    },
    "butcher_boots": {
        "name": "Butcher Boots", "slot": "feet", "rarity": "epic",
        "set": "butcher", "armor": 4, "bonus": {"strength": 3}, "for": "gent",
        "shops": (),
    },
}
