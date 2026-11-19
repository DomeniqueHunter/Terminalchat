ENEMIES = {
    "drainer": {
        "name": "The Drainer", "min_stage": 1, "max_stage": 0,
        "event_only": True, "tribe": "drainers",
        "hp": 600, "attack": 26, "defense": 12, "agility": 14, "exp": 400,
        "fates": ["drained"],
        "actions": [("heavy", 35), ("sweep", 25), ("attack_weakest", 25),
                    ("attack", 15)],
    },
}
