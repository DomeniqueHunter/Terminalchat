VARIANTS = {
    "classic": ("Classic Pod", 900,
                "A large, elongated pod, shaped like the one who was in it."),
    "pumpkin": ("Pumpkin Pod", 1300,
                "A small, ridged orange pod, hard as wood. Collectors pay "
                "double for the shape beneath the rind."),
    "tuber": ("Tuber Pod", 800,
              "A bulbous root sac dug out of the mud, still faintly warm."),
    "cocoon": ("Vine Cocoon", 1000,
               "A tall cocoon of muscular vines that still twitches now "
               "and then."),
    "flytrap": ("Flytrap Pod", 1050,
                "A glossy green trap, its toothed lobes locked shut over "
                "a shape that still fills it to the rim."),
    "nectar": ("Nectar Pod", 1100,
               "A flower-like sac, full of sweet, thick nectar."),
    "burrow": ("Root Burrow Pod", 850,
               "A knot of barbed roots around a hollow shaped like a body."),
}
ITEMS = {
    f"pod_{key}": {
        "name": name, "slot": "consumable", "rarity": "epic",
        "price": price, "no_loot": True, "shops": (), "for": "both",
        "pod": True, "seed": "seductress", "sprout": 1, "note": note,
    }
    for key, (name, price, note) in VARIANTS.items()
}
ITEMS["pod_goo"] = {
    "name": "Pod Nectar", "slot": "consumable", "rarity": "rare",
    "price": 160, "no_loot": True, "shops": (), "for": "both",
    "heal": 60, "mana": 30,
    "note": "Sweet, warm goo from a bloomed pod. It tingles all the way "
            "down.",
}
ITEMS["pod_seed"] = {
    "name": "Bloom Seed", "slot": "consumable", "rarity": "rare",
    "price": 120, "no_loot": True, "shops": (), "for": "both",
    "mana": 40,
    "note": "A seed that smells of sweat and flowers. It hums when held.",
}
