ENEMIES = {
    "iron_maiden": {
        "name": "Walking Iron Maiden", "min_stage": 40, "max_stage": 0,
        "tribe": "constructs", "mindless": True,
        "hp": 95, "attack": 13, "defense": 9, "agility": 4, "exp": 55,
        "melee_mult": 0.7, "magic_mult": 1.2,
        "fates": ["iron_maiden"],
        "actions": [("attack_weakest", 50), ("heavy", 30), ("attack", 20)],
    },
    "stone_sentinel": {
        "mindless": True,
        "name": "Stone Sentinel", "min_stage": 30, "max_stage": 0,
        "hp": 130, "attack": 15, "defense": 8, "agility": 1, "exp": 45,
        "fates": ["wall", "statue", "door"],
        "actions": [("heavy", 60), ("sweep", 40)],
    },
    "living_gate": {
        "mindless": True,
        "name": "Living Gate", "min_stage": 30, "max_stage": 0,
        "hp": 110, "attack": 12, "defense": 9, "agility": 1, "exp": 38,
        "fates": ["door"],
        "actions": [("attack", 40), ("heavy", 40), ("attack_weakest", 20)],
    },
    "wall_eater": {
        "mindless": True,
        "name": "Wall Eater", "min_stage": 35, "max_stage": 0,
        "hp": 60, "attack": 11, "defense": 4, "agility": 3, "exp": 20,
        "fates": ["wall", "wall", "door"],
        "actions": [("attack", 60), ("heavy", 40)],
    },
}
