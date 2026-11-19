ENEMIES = {
    "ghoul": {
        "name": "Ghoul", "min_stage": 8, "max_stage": 45,
        "hp": 45, "attack": 9, "defense": 2, "agility": 6, "exp": 16,
        "fates": ["eaten"],
        "actions": [("attack", 60), ("drain", 40)],
    },
    "risen_skeleton": {
        "name": "Risen Skeleton", "min_stage": 1, "max_stage": 0,
        "event_only": True, "tribe": "undead",
        "hp": 50, "attack": 10, "defense": 4, "agility": 9, "exp": 35,
        "melee_mult": 0.8,
        "fates": ["entombed"],
        "actions": [("attack", 50), ("attack_weakest", 30), ("heavy", 20)],
    },
    "lich_queen": {
        "name": "<<npc.isolde_first>> <<npc.isolde_last>>", "npc": "isolde",
        "min_stage": 1, "max_stage": 0, "event_only": True, "tribe": "lich",
        "hp": 260, "attack": 16, "defense": 6, "agility": 12, "exp": 160,
        "melee_mult": 0.7,
        "fates": ["ice_statue", "consort"],
        "actions": [("sweep", 35), ("drain", 25), ("heavy", 25),
                    ("attack_weakest", 15)],
    },
    "lich_consort": {
        "name": "Frozen Consort", "min_stage": 1, "max_stage": 0,
        "event_only": True, "tribe": "lich",
        "hp": 75, "attack": 12, "defense": 5, "agility": 9, "exp": 45,
        "fates": ["ice_statue", "consort"],
        "actions": [("attack", 45), ("heavy", 35), ("attack_weakest", 20)],
    },
}
