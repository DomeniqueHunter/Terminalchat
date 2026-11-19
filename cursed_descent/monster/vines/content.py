ENEMIES = {
    "pheromone_bloom": {
        "name": "Pheromone Bloom", "min_stage": 16, "max_stage": 0,
        "event_only": True,
        "hp": 75, "attack": 11, "defense": 2, "agility": 7, "exp": 34,
        "tribe": "vines", "melee_mult": 0.8, "magic_mult": 1.2,
        "fates": ["podded", "vined"],
        "actions": [("sweep", 55), ("attack_weakest", 25), ("attack", 20)],
    },
}
