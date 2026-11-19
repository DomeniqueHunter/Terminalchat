# Mage tower presets: the mage's own items and set.


ITEMS = {
    "mage_hat": {
        "name": "Mage Hat", "slot": "head", "rarity": "rare", "set": "mage",
        "armor": 3, "bonus": {"intelligence": 2}, "for": "both",
        "shops": ("velvet", "smith"),
    },
    "mage_robe": {
        "name": "Mage Robe", "slot": "chest", "rarity": "rare", "set": "mage",
        "armor": 8, "bonus": {"intelligence": 2}, "for": "both",
        "shops": ("velvet", "smith"),
    },
    "mage_gloves": {
        "name": "Mage Gloves", "slot": "gloves", "rarity": "rare",
        "set": "mage", "armor": 2, "bonus": {"intelligence": 2}, "for": "both",
        "shops": ("velvet", "smith"),
    },
    "mage_slippers": {
        "name": "Mage Slippers", "slot": "feet", "rarity": "rare",
        "set": "mage", "armor": 2, "bonus": {"intelligence": 2}, "for": "both",
        "shops": ("velvet", "smith"),
    },
    "spellbook": {
        "name": "Old Spellbook", "slot": "weapon", "class": "tome",
        "rarity": "rare", "damage": 2, "bonus": {"intelligence": 4},
        "note": "a focus for the mage set", "for": "both", "shops": ("smith",),
    },
    # NPC gear
    'archmage_orlen_midnight_blue_archmage_robes': {'name': 'Midnight-Blue Archmage Robes',
 'slot': 'chest',
 'rarity': 'epic',
 'armor': 6,
 'bonus': {'intelligence': 5},
 'for': 'both',
 'shops': (),
 'no_loot': True,
 'note': 'Heavy robes of midnight-blue wool with silver thread constellations along the hem. They hang with the weight of long study and smell of candle wax, ozone and old paper.'},
    'archmage_orlen_ring_set_of_ten_rings': {'name': 'Ring Set of Ten Rings',
 'slot': 'accessory',
 'rarity': 'epic',
 'mana': 20,
 'bonus': {'intelligence': 4},
 'for': 'both',
 'shops': (),
 'no_loot': True,
 'note': 'Ten slim silver rings, one for each finger, each set with a different dull stone. They hum in sequence when <<npc.archmage_orlen_first>> counts a spell on his fingers.'},
    'archmage_orlen_staff_of_patient_manners': {'name': 'Staff of Patient Manners',
 'slot': 'weapon',
 'rarity': 'epic',
 'class': 'staff',
 'damage': 12,
 'bonus': {'intelligence': 3},
 'for': 'both',
 'shops': (),
 'no_loot': True,
 'note': 'A tall staff of pale ash, topped with a smoky crystal that glows when someone is rude. It is carved with tiny rules of courtesy and rewards the patient.'},
    'archmage_orlen_silver_thread_hood': {'name': 'Silver-Thread Hood',
 'slot': 'head',
 'rarity': 'common',
 'bonus': {'intelligence': 1},
 'for': 'both',
 'shops': (),
 'no_loot': True},
}


ITEM_SETS = {
    "mage": {
        "name": "Mage",
        "bonuses": {
            2: {"bonus": {"intelligence": 3}},
            4: {"armor": 2, "crit": 0.06},
            6: {"bonus": {"intelligence": 3, "vitality": 2}, "crit": 0.08},
        },
    },
}
