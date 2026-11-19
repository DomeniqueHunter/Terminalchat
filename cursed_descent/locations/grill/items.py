# Gear worn by the NPCs of the grill (never sold, never looted) and the menu.


ITEMS = {
    'gul_long_carving_knife': {
        'name': 'Long Carving Knife', 'slot': 'weapon', 'rarity': 'epic',
        'class': 'dagger', 'damage': 22, 'for': 'both', 'shops': (),
        'no_loot': True,
        'note': '<<npc.gul_first>>\'s kebab knife: a narrow blade as long as '
                'a forearm, polished by years of thin slices. It has never '
                'slipped, and it cuts what it is pointed at.'},
    'gul_grease_stiff_apron': {
        'name': 'Grease-Stiff Apron', 'slot': 'chest', 'rarity': 'common',
        'armor': 5, 'for': 'both', 'shops': (), 'no_loot': True},
    'gul_gold_tooth_charm': {
        'name': 'Gold Tooth Charm', 'slot': 'accessory', 'rarity': 'epic',
        'allure': 2, 'bonus': {'vitality': 1}, 'for': 'both', 'shops': (),
        'no_loot': True,
        'note': 'A small gold tooth on a thin chain. <<npc.gul_first>> swears '
                'it was a gift. Nobody has asked from whom.'},
    'grill_chicken_half': {
        'name': 'Half Grilled Chicken', 'slot': 'consumable',
        'rarity': 'common', 'heal': 45, 'needs': {'hunger': -30},
        'price': 18, 'no_loot': True,
        'note': 'golden skin, red spice rub, juice that runs down the '
                'wrist – turned on the spit for an hour'},
    'grill_chicken_whole': {
        'name': 'Whole Grilled Chicken', 'slot': 'consumable',
        'rarity': 'rare', 'heal': 90, 'needs': {'hunger': -55},
        'price': 34, 'no_loot': True,
        'note': 'a whole bird, split and flattened, brushed with garlic '
                'oil until the skin crackles'},
    'grill_kebab_wrap': {
        'name': 'Kebab in Flatbread', 'slot': 'consumable',
        'rarity': 'common', 'heal': 55,
        'needs': {'hunger': -35, 'thirst': 5}, 'price': 20,
        'no_loot': True,
        'note': 'thin slices cut from the spit, onions, sharp sauce, '
                'rolled in hot bread'},
    'grill_kebab_plate': {
        'name': 'Kebab Plate with Rice', 'slot': 'consumable',
        'rarity': 'rare', 'heal': 100, 'mana': 20,
        'needs': {'hunger': -60, 'thirst': 5}, 'price': 38,
        'no_loot': True,
        'note': 'a heap of carved meat on buttered rice, grilled '
                'tomato and a bottle of sauce without a label'},
}
