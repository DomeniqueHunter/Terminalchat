ENEMIES = {
    "mrs_claus": {
        "name": "Mrs. Claus", "min_stage": 1, "max_stage": 0,
        "event_only": True, "tribe": "winter",
        "hp": 230, "attack": 14, "defense": 6, "agility": 8, "exp": 150,
        "melee_mult": 0.8,
        "fates": ["sacked"],
        "actions": [("attack_weakest", 30), ("drain", 20), ("heavy", 30),
                    ("sweep", 20)],
    },
    "reindeer": {
        "name": "Reindeer", "min_stage": 1, "max_stage": 0,
        "event_only": True, "tribe": "winter",
        "hp": 65, "attack": 11, "defense": 3, "agility": 14, "exp": 32,
        "fates": ["sacked"],
        "actions": [("attack", 55), ("heavy", 30), ("attack_weakest", 15)],
    },
    "elf": {
        "name": "Elf", "min_stage": 1, "max_stage": 0,
        "event_only": True, "tribe": "winter",
        "hp": 36, "attack": 8, "defense": 2, "agility": 13, "exp": 18,
        "fates": ["sacked"],
        "actions": [("attack", 50), ("attack_weakest", 35), ("heavy", 15)],
    },
}
