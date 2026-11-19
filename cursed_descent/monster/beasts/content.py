ENEMIES = {
    "rat": {
        "name": "Giant Rat", "min_stage": 1, "max_stage": 20,
        "hp": 18, "attack": 5, "defense": 0, "agility": 6, "exp": 6,
        "fates": ["eaten"],
        "actions": [("attack", 80), ("attack_weakest", 20)],
    },
    "gorgon": {
        "name": "Gorgon", "min_stage": 28, "max_stage": 0,
        "hp": 70, "attack": 12, "defense": 3, "agility": 12, "exp": 35,
        "fates": ["statue"],
        "actions": [("attack", 60), ("petrify", 40)],
    },
}
