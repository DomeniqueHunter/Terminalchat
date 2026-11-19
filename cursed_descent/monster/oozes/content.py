ENEMIES = {
    "green_slime": {
        "mindless": True,
        "name": "Green Slime", "min_stage": 3, "max_stage": 25,
        "hp": 30, "attack": 5, "defense": 0, "agility": 2, "exp": 8,
        "melee_mult": 0.6, "magic_mult": 1.3,
        "fates": ["dissolved"],
        "actions": [("attack", 70), ("drain", 30)],
    },
    "acid_ooze": {
        "mindless": True,
        "name": "Acid Ooze", "min_stage": 12, "max_stage": 0,
        "hp": 55, "attack": 10, "defense": 1, "agility": 3, "exp": 18,
        "melee_mult": 0.5, "magic_mult": 1.3,
        "fates": ["dissolved"],
        "actions": [("attack", 50), ("attack_weakest", 30), ("sweep", 20)],
    },
    "gelatinous_cube": {
        "mindless": True,
        "name": "Gelatinous Cube", "min_stage": 38, "max_stage": 0,
        "hp": 90, "attack": 11, "defense": 2, "agility": 1, "exp": 40,
        "melee_mult": 0.5, "magic_mult": 1.25,
        "fates": ["encased", "dissolved"],
        "actions": [("heavy", 40), ("attack", 40), ("drain", 20)],
    },
    "mimic": {
        "name": "Mimic", "min_stage": 1, "max_stage": 0, "chest_only": True,
        "hp": 55, "attack": 13, "defense": 5, "agility": 5, "exp": 30,
        "fates": ["eaten", "door"],
        "actions": [("attack_weakest", 50), ("heavy", 50)],
    },
}
