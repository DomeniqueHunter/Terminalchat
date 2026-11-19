ENEMIES = {
    "ogre": {
        "name": "Ogre", "min_stage": 20, "max_stage": 0,
        "hp": 90, "attack": 13, "defense": 3, "agility": 2, "exp": 28,
        "tribe": "ogres", "fates": ["roasted", "eaten", "trophy"],
        "actions": [("attack", 30), ("heavy", 50), ("sweep", 20)],
    },
    "hammer_ogre": {
        "name": "Giant Hammer Ogre", "min_stage": 30, "max_stage": 0,
        "tribe": "ogres",
        "hp": 125, "attack": 16, "defense": 4, "agility": 5, "exp": 72,
        "melee_mult": 0.9,
        "fates": ["flattened", "flattened", "trophy"],
        "actions": [("heavy", 55), ("sweep", 30), ("attack", 15)],
    },
}
