ENEMIES = {
    "goblin": {
        "name": "Goblin", "min_stage": 1, "max_stage": 30,
        "hp": 24, "attack": 6, "defense": 1, "agility": 10, "exp": 9,
        "tribe": "goblins", "fates": ["breeding", "roasted"],
        "actions": [("attack", 60), ("attack_weakest", 40)],
    },
    "goblin_shaman": {
        "name": "Goblin Shaman", "min_stage": 4, "max_stage": 30,
        "hp": 20, "attack": 8, "defense": 0, "agility": 8, "exp": 12,
        "tribe": "goblins", "fates": ["breeding"],
        "actions": [("attack", 50), ("sweep", 50)],
    },
}
