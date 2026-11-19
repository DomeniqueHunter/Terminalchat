BIOMES = [
    {
        "name": "Goblin Warrens",
        "min_stage": 1,
        "intro": "Tunnels reeking of smoke and wet fur. Somewhere in the "
                 "dark, goblins are giggling.",
        "enemies": ["rat", "goblin", "goblin", "goblin_shaman",
                    "green_slime"],
        "boss": {
            "name": "Goblin King Grubnak", "hp": 160, "attack": 10,
            "defense": 3, "agility": 8, "exp": 80, "tribe": "goblins",
            "fates": ["breeding", "roasted"],
            "minions": ["goblin", "goblin_shaman"],
            "actions": [("attack", 40), ("heavy", 30), ("sweep", 30)],
        },
    },
    {
        "name": "The Crypt",
        "min_stage": 8,
        "intro": "Cold stone, open coffins and the sound of something "
                 "chewing in the dark.",
        "enemies": ["ghoul", "ghoul", "rat", "green_slime", "acid_ooze"],
        "boss": {
            "name": "Ghoul Lord Morrow", "hp": 220, "attack": 12,
            "defense": 4, "agility": 6, "exp": 110,
            "fates": ["eaten"], "minions": ["ghoul"],
            "actions": [("attack", 30), ("drain", 40), ("sweep", 30)],
        },
    },
    {
        "name": "Orc Stronghold",
        "min_stage": 20,
        "intro": "War drums echo through crude palisades. A spit turns over "
                 "every fire.",
        "enemies": ["orc", "orc", "orc_berserker", "ogre", "goblin",
                    "pigman_brute"],
        "boss": {
            "name": "Orc Warlord Gorzak", "hp": 300, "attack": 15,
            "defense": 5, "agility": 6, "exp": 160, "tribe": "orcs",
            "fates": ["breeding", "roasted"],
            "minions": ["orc", "orc_berserker"],
            "actions": [("attack", 30), ("heavy", 40), ("sweep", 30)],
        },
    },
    {
        "name": "Amazon Temple",
        "min_stage": 28,
        "intro": "Vine-choked pillars and the smell of incense. Somewhere a "
                 "war horn sounds – the hunt has begun, and you are the prey.",
        "enemies": ["amazon_warrior", "amazon_warrior", "amazon_huntress",
                    "amazon_huntress"],
        "boss": {
            "name": "Amazon Queen Thalassa", "hp": 320, "attack": 16,
            "defense": 5, "agility": 12, "exp": 190, "tribe": "amazons",
            "fates": ["breeding", "swallowed", "swallowed", "roasted"],
            "minions": ["amazon_warrior", "amazon_huntress"],
            "actions": [("attack", 30), ("heavy", 40), ("sweep", 30)],
        },
    },
    {
        "name": "Petrified Halls",
        "min_stage": 30,
        "intro": "Silent halls full of statues. Some of them still wear "
                 "adventurer's gear.",
        "enemies": ["gorgon", "gorgon", "stone_sentinel", "living_gate",
                    "iron_maiden"],
        "boss": {
            "name": "Gorgon Queen Sythra", "hp": 280, "attack": 14,
            "defense": 5, "agility": 14, "exp": 200,
            "fates": ["statue"], "minions": ["gorgon"],
            "actions": [("attack", 30), ("petrify", 40), ("sweep", 30)],
        },
    },
    {
        "name": "Living Walls",
        "min_stage": 35,
        "intro": "The masonry breathes. Doors here have faces, and some of "
                 "them still blink.",
        "enemies": ["wall_eater", "living_gate", "acid_ooze",
                    "gelatinous_cube"],
        "boss": {
            "name": "The Hungry Maw", "mindless": True,
            "hp": 340, "attack": 15,
            "defense": 6, "agility": 2, "exp": 240,
            "fates": ["wall", "eaten", "door"], "minions": ["wall_eater"],
            "actions": [("heavy", 50), ("sweep", 30), ("drain", 20)],
        },
    },
    {
        "name": "Giant's Larder",
        "min_stage": 48,
        "intro": "Bones as big as tree trunks and racks of salted meat. Some "
                 "of it once wore armor.",
        "enemies": ["hill_giant", "hill_giant", "bone_giant", "ogre",
                    "hammer_ogre"],
        "boss": {
            "name": "Giant Chieftain Skullmantle", "hp": 420, "attack": 19,
            "defense": 8, "agility": 3, "exp": 300, "tribe": "giants",
            "fates": ["trophy"], "minions": ["hill_giant", "bone_giant"],
            "actions": [("heavy", 40), ("sweep", 40), ("attack", 20)],
        },
    },
    {
        "name": "Dripping Caves",
        "min_stage": 4,
        "intro": "The tunnels narrow and the walls start to sweat. Water "
                 "drips somewhere ahead, and under the sound of it you hear "
                 "claws scraping on wet stone.",
        "enemies": ["rat", "rat", "green_slime", "goblin", "goblin_shaman"],
        "boss": {
            "name": "Tunnel Warden Skrit", "hp": 140, "attack": 9,
            "defense": 3, "agility": 9, "exp": 70, "tribe": "goblins",
            "fates": ["breeding", "roasted"],
            "minions": ["goblin", "goblin_shaman"],
            "actions": [("attack", 40), ("heavy", 30), ("sweep", 30)],
        },
    },
    {
        "name": "Rotting Swamp",
        "min_stage": 12,
        "intro": "Black water closes over your boots and the air tastes of "
                 "rot. Bubbles rise where something large is breathing "
                 "under the mud.",
        "enemies": ["ghoul", "acid_ooze", "green_slime", "pigman_brute"],
        "boss": {
            "name": "Mire Hag Vessa", "hp": 210, "attack": 12,
            "defense": 4, "agility": 5, "exp": 105,
            "fates": ["eaten"], "minions": ["ghoul", "acid_ooze"],
            "actions": [("attack", 30), ("drain", 40), ("sweep", 30)],
        },
    },
    {
        "name": "Orc Camp",
        "min_stage": 15,
        "intro": "Smoke rises from a ring of crude tents. Bones hang from "
                 "poles, and a very large pot simmers over the central "
                 "fire. Someone is already sharpening a knife.",
        "enemies": ["orc", "orc", "goblin", "goblin_shaman", "pigman_brute"],
        "boss": {
            "name": "Warchief Dragga", "hp": 260, "attack": 14,
            "defense": 5, "agility": 6, "exp": 140, "tribe": "orcs",
            "fates": ["breeding", "roasted"], "minions": ["orc", "goblin"],
            "actions": [("attack", 30), ("heavy", 40), ("sweep", 30)],
        },
    },
    {
        "name": "Ogre Mountain",
        "min_stage": 28,
        "intro": "The path climbs between boulders the size of houses. Cold "
                 "wind carries the thud of heavy feet and the smell of "
                 "roasting meat from somewhere above.",
        "enemies": ["ogre", "ogre", "hammer_ogre", "orc_berserker",
                    "gorgon"],
        "boss": {
            "name": "Peak King Brakk", "hp": 360, "attack": 17,
            "defense": 6, "agility": 4, "exp": 210, "tribe": "ogres",
            "fates": ["flattened", "roasted", "trophy"],
            "minions": ["ogre", "hammer_ogre"],
            "actions": [("heavy", 40), ("sweep", 30), ("attack", 30)],
        },
    },
    {
        "name": "Amazon Jungle",
        "min_stage": 28,
        "intro": "Damp heat, screaming birds and leaves as wide as shields. "
                 "A branch snaps behind you – then another. You are being "
                 "tracked by people who do this for sport.",
        "enemies": ["amazon_warrior", "amazon_warrior", "amazon_huntress",
                    "amazon_huntress", "pigman_brute", "goblin_shaman"],
        "boss": {
            "name": "Huntmistress Kyra", "hp": 290, "attack": 15,
            "defense": 5, "agility": 13, "exp": 175, "tribe": "amazons",
            "fates": ["breeding", "swallowed", "swallowed", "roasted"],
            "minions": ["amazon_warrior", "amazon_huntress"],
            "actions": [("attack", 40), ("heavy", 30), ("sweep", 30)],
        },
    },
    {
        "name": "Vine Swamp",
        "min_stage": 16,
        "intro": "Warm, sweet air hangs over black water. Heart-shaped "
                 "leaves as wide as doors turn slowly toward you, and "
                 "every flower along the path is open.",
        "enemies": ["pheromone_bloom", "pheromone_bloom", "green_slime",
                    "acid_ooze", "ghoul"],
        "boss": {
            "name": "Swamp Seductress Ylvara", "hp": 260, "attack": 14,
            "defense": 4, "agility": 9, "exp": 140, "tribe": "vines",
            "fates": ["podded", "vined"],
            "minions": ["pheromone_bloom"],
            "actions": [("sweep", 40), ("heavy", 30), ("attack", 30)],
        },
    },
]
