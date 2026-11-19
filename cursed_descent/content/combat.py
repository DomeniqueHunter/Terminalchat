SPELLS = {
    "fireball": {
        "name": "Fireball", "kind": "damage", "target": "single",
        "mana": 8, "base": 12, "scale": 3.0, "affinity": "magic",
        "req_affinity": 0, "req_intelligence": 0,
    },
    "frostnova": {
        "name": "Frost Nova", "kind": "damage", "target": "all",
        "mana": 15, "base": 6, "scale": 1.5, "affinity": "magic",
        "req_affinity": 50, "req_intelligence": 14,
    },
    "lightning": {
        "name": "Chain Lightning", "kind": "damage", "target": "single",
        "mana": 22, "base": 25, "scale": 4.5, "affinity": "magic",
        "req_affinity": 120, "req_intelligence": 22,
    },
    "heal": {
        "name": "Heal", "kind": "heal", "target": "ally",
        "mana": 10, "base": 15, "scale": 2.5, "affinity": "heal",
        "req_affinity": 0, "req_intelligence": 0,
    },
    "healcircle": {
        "name": "Healing Circle", "kind": "heal", "target": "allies",
        "mana": 25, "base": 10, "scale": 1.8, "affinity": "heal",
        "req_affinity": 100, "req_intelligence": 18,
    },
}

INTENT_TEXTS = {
    "attack": "{enemy} attacks {target}.",
    "attack_weakest": "{enemy} locks onto the weakest prey: {target}.",
    "heavy": "{enemy} winds up for a crushing blow against {target}!",
    "sweep": "{enemy} prepares a sweeping strike against everyone!",
    "petrify": "The eyes of {enemy} begin to glow – its gaze falls on "
               "{target}!",
    "drain": "{enemy} reaches its claws toward {target} to drain their "
             "life force.",
}

ACTION_MULTIPLIERS = {
    "attack": 1.0, "attack_weakest": 1.0, "heavy": 1.8,
    "sweep": 0.6, "petrify": 2.5, "drain": 1.0,
}
