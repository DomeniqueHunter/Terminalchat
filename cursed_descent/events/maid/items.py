# Gear of Head Maid Constance (never sold, never looted).
from ...config import BUTT_BUSTER_DAMAGE


ITEMS = {
    'constance_butt_buster': {
        'name': 'The Butt Buster', 'slot': 'weapon', 'rarity': 'legendary',
        'class': 'blunt', 'damage': BUTT_BUSTER_DAMAGE, 'for': 'both',
        'shops': (), 'no_loot': True,
        'note': 'A 2.5 m paddle of polished, lacquered wood, 30 cm wide '
                'and 2 cm thick, engraved with intricate patterns and '
                'fitted for a comfortable grip. Indestructible, and '
                'weightless in the hands of Head Maid '
                '<<npc.constance_first>>. Also known as The Mistress Mangler, '
                'The Cheek Crusher, The Glute Gavel and The Derrière '
                'Destroyer. Every mistress submits to it once a day, a '
                'hundred smacks per session. The engraving still reads '
                '"Property of the House of Pemberton".'},
    'constance_lace_cap': {
        'name': "Head Maid's Lace Cap", 'slot': 'head', 'rarity': 'rare',
        'armor': 3, 'allure': 1, 'for': 'both', 'shops': (),
        'no_loot': True,
        'note': 'Starched white lace with a black ribbon, pinned '
                'perfectly straight.'},
    'constance_silk_uniform': {
        'name': 'Silk Head Maid Uniform', 'slot': 'chest',
        'rarity': 'epic', 'armor': 12, 'allure': 2, 'for': 'both',
        'shops': (), 'no_loot': True,
        'note': 'Black silk, cut by a tailor and not a seamstress, with '
                'pearl buttons and a white lace collar. Pressed every '
                'morning, without a crease by evening.'},
    'constance_silk_gloves': {
        'name': 'White Silk Gloves', 'slot': 'gloves', 'rarity': 'rare',
        'armor': 3, 'allure': 1, 'for': 'both', 'shops': (),
        'no_loot': True,
        'note': 'Spotless wrist-length gloves. A lady\'s hands never '
                'touch dust, only paddles.'},
    'constance_hell_boots': {
        'name': 'Hell Boots', 'slot': 'feet', 'rarity': 'epic',
        'armor': 5, 'allure': 3, 'bonus': {'agility': 1}, 'for': 'both',
        'shops': (), 'no_loot': True,
        'note': 'Knee-high black patent boots with tall, slender heels '
                'set with crystals and fine metalwork. Every step rings '
                'on the stone floor like a verdict.'},
    'constance_pearl_collar': {
        'name': 'Pearl Collar', 'slot': 'accessory', 'rarity': 'rare',
        'allure': 3, 'bonus': {'vitality': 1}, 'for': 'both', 'shops': (),
        'no_loot': True,
        'note': 'A jeweled collar of pearls on black velvet, worn with '
                'a straight back and a small, knowing smile. It '
                'symbolizes her submission to the House, and she wears '
                'it as proudly as her paddle.'},
    'constance_shimmer_stockings': {
        'name': 'Shimmer Stockings', 'slot': 'lingerie', 'rarity': 'rare',
        'allure': 2, 'for': 'both', 'shops': (), 'no_loot': True,
        'note': 'Sheer silk stockings with subtle shimmering threads, '
                'so fine one only notices them when she turns.'},
}
