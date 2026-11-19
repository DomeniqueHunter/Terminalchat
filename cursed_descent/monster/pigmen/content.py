ENEMIES = {
    "pigman_brute": {
        "name": "Pigman Brute", "min_stage": 12, "max_stage": 0,
        "tribe": "pigmen",
        "hp": 60, "attack": 11, "defense": 3, "agility": 7, "exp": 34,
        "fates": ["flattened", "roasted"],
        "actions": [("attack", 40), ("heavy", 45), ("attack_weakest", 15)],
    },
    "pigman_butcher": {
        "name": "<<npc.hamhock_first>> the Pigman Butcher", "npc": "hamhock",
        "min_stage": 1,
        "max_stage": 0, "event_only": True, "tribe": "pigmen",
        "hp": 95, "attack": 12, "defense": 3, "agility": 8, "exp": 50,
        "fates": ["butchered"],
        "actions": [("heavy", 45), ("attack_weakest", 35), ("attack", 20)],
    },
    "pigman_farmer": {
        "name": "<<npc.old_trotter_first>> the Pigman Farmer",
        "npc": "old_trotter", "min_stage": 1,
        "max_stage": 0, "event_only": True, "tribe": "pigmen",
        "hp": 90, "attack": 10, "defense": 4, "agility": 9, "exp": 48,
        "fates": ["farmed"],
        "actions": [("sweep", 35), ("attack", 40), ("attack_weakest", 25)],
    },
}
