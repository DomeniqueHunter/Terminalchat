ENEMIES = {
    "safari_hunter": {
        "name": "<<npc.reginald_first>> <<npc.reginald_last>>",
        "npc": "reginald", "min_stage": 1, "max_stage": 0,
        "event_only": True, "tribe": "hunters",
        "hp": 90, "attack": 11, "defense": 3, "agility": 12, "exp": 45,
        "fates": ["lodge"],
        "actions": [("attack_weakest", 50), ("heavy", 30), ("attack", 20)],
    },
    "couturiere": {
        "name": "<<npc.vesper_first>> <<npc.vesper_last>>", "npc": "vesper",
        "min_stage": 1, "max_stage": 0,
        "event_only": True, "tribe": "designers",
        "hp": 85, "attack": 10, "defense": 2, "agility": 14, "exp": 45,
        "fates": ["fashion"],
        "actions": [("sweep", 40), ("attack_weakest", 40), ("attack", 20)],
    },
    "school_recruiter": {
        "name": "<<npc.starch_first>> <<npc.starch_last>>", "npc": "starch",
        "min_stage": 1, "max_stage": 0,
        "event_only": True, "tribe": "school",
        "hp": 88, "attack": 10, "defense": 3, "agility": 13, "exp": 45,
        "fates": ["recruited"],
        "actions": [("attack_weakest", 45), ("heavy", 25), ("attack", 30)],
    },
}
