ENEMIES = {
    "hill_giant": {
        "name": "Hill Giant", "min_stage": 48, "max_stage": 0,
        "hp": 130, "attack": 16, "defense": 5, "agility": 2, "exp": 55,
        "tribe": "giants", "fates": ["trophy", "trophy", "eaten"],
        "actions": [("heavy", 50), ("sweep", 30), ("attack", 20)],
    },
    "bone_giant": {
        "name": "Bone-Crowned Giant", "min_stage": 52, "max_stage": 0,
        "hp": 150, "attack": 17, "defense": 7, "agility": 3, "exp": 65,
        "tribe": "giants", "fates": ["trophy"],
        "actions": [("heavy", 40), ("sweep", 40), ("attack_weakest", 20)],
    },
}
