# Gear of the Marsh women (never sold, never looted) and the shelf stock.


ITEMS = {
    'dairy_ledger_stick': {
        'name': 'Ledger Stick', 'slot': 'weapon', 'rarity': 'rare',
        'class': 'staff', 'damage': 12, 'for': 'both', 'shops': (),
        'no_loot': True,
        'note': '<<npc.odile_first>>\'s counting stick, notched with every '
                'cow that ever stood in the barn.'},
    'dairy_milking_apron': {
        'name': 'Milking Apron', 'slot': 'chest', 'rarity': 'common',
        'armor': 4, 'for': 'both', 'shops': (), 'no_loot': True},
    'dairy_lead_cow_bell': {
        'name': 'Lead Cow Bell', 'slot': 'accessory', 'rarity': 'epic',
        'allure': 3, 'bonus': {'vitality': 2}, 'for': 'both', 'shops': (),
        'no_loot': True,
        'note': 'A brass bell on a leather collar, worn smooth by forty '
                'years of <<npc.marguerite_first>>\'s slow, proud walk.'},
    'dairy_milk': {
        'name': 'Jug of Fresh Milk', 'slot': 'consumable',
        'rarity': 'common', 'heal': 40, 'needs': {'hunger': -20,
                                                  'thirst': -25},
        'price': 14, 'no_loot': True,
        'note': 'still warm, thick, a little sweet'},
    'dairy_cream': {
        'name': 'Pot of Double Cream', 'slot': 'consumable',
        'rarity': 'common', 'heal': 55, 'needs': {'hunger': -25},
        'price': 22, 'no_loot': True,
        'note': 'a clay pot with a skin you have to break with a spoon'},
    'dairy_cheese': {
        'name': 'Wheel of Crone Cheese', 'slot': 'consumable',
        'rarity': 'rare', 'heal': 90, 'mana': 15,
        'needs': {'hunger': -50}, 'price': 36, 'no_loot': True,
        'note': 'a small wheel, rind waxed red, aged in the cellar under '
                'the barn'},
    'dairy_butter': {
        'name': 'Crock of Salted Butter', 'slot': 'consumable',
        'rarity': 'common', 'heal': 45, 'needs': {'hunger': -30},
        'price': 18, 'no_loot': True,
        'note': 'hand-churned, a little yellower than butter should be'},
    'dairy_tonic': {
        'name': 'Bull Tonic', 'slot': 'consumable', 'rarity': 'rare',
        'heal': 60, 'mana': 40, 'price': 48, 'no_loot': True,
        'note': 'a dark bottle sold under the counter; the label says '
                '"for vigour" and nothing else'},
}
