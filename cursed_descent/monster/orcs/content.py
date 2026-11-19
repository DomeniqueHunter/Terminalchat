ENEMIES = {
    "orc": {
        "name": "Orc Raider", "min_stage": 15, "max_stage": 45,
        "hp": 50, "attack": 10, "defense": 3, "agility": 5, "exp": 18,
        "tribe": "orcs", "fates": ["breeding", "roasted"],
        "actions": [("attack", 60), ("attack_weakest", 20), ("heavy", 20)],
    },
    "orc_berserker": {
        "name": "Orc Berserker", "min_stage": 20, "max_stage": 0,
        "hp": 75, "attack": 14, "defense": 2, "agility": 7, "exp": 26,
        "tribe": "orcs", "fates": ["breeding", "roasted"],
        "actions": [("attack", 40), ("heavy", 40), ("sweep", 20)],
    },
}
