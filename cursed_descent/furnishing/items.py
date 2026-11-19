# Furniture for the house slots; ordering is possible for common and rare pieces.


ITEMS = {
    'straw_pallet': {
        "use": "bed",
        "name": 'Straw Pallet', "slot": "furniture", "furniture": 'bed',
        "rarity": 'common', "price": 60, "comfort": 2, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'A sack of straw on a plank frame.'},
    'feather_bed': {
        "use": "bed",
        "name": 'Feather Bed', "slot": "furniture", "furniture": 'bed',
        "rarity": 'rare', "price": 300, "comfort": 6, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'Deep, soft and a little too inviting.'},
    'canopy_bed': {
        "use": "bed",
        "name": 'Canopy Bed', "slot": "furniture", "furniture": 'bed',
        "rarity": 'epic', "price": 900, "comfort": 12, "storage": 0,
        "shops": (), "for": "both", "catalogue": False,
        "note": 'Four carved posts and curtains heavy as velvet.'},
    'three_legged_stool': {
        "name": 'Three-Legged Stool', "slot": "furniture", "furniture": 'seat',
        "rarity": 'common', "price": 40, "comfort": 1, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'It wobbles, but it holds.'},
    'padded_armchair': {
        "name": 'Padded Armchair', "slot": "furniture", "furniture": 'seat',
        "rarity": 'rare', "price": 220, "comfort": 3, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'A wide chair with arms made for sprawling.'},
    'carved_throne_chair': {
        "name": 'Carved Throne Chair', "slot": "furniture", "furniture": 'seat',
        "rarity": 'epic', "price": 800, "comfort": 6, "storage": 0,
        "shops": (), "for": "both", "catalogue": False,
        "note": 'Dark oak, high back, room for a heavy host.'},
    'reed_mat': {
        "name": 'Reed Mat', "slot": "furniture", "furniture": 'rug',
        "rarity": 'common', "price": 40, "comfort": 1, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'Woven reeds, rough but warm enough.'},
    'wool_rug': {
        "name": 'Wool Rug', "slot": "furniture", "furniture": 'rug',
        "rarity": 'rare', "price": 180, "comfort": 3, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'Thick wool in red and ochre.'},
    'bearskin_rug': {
        "name": 'Bearskin Rug', "slot": "furniture", "furniture": 'rug',
        "rarity": 'epic', "price": 700, "comfort": 5, "storage": 0,
        "shops": (), "for": "both", "catalogue": False,
        "note": 'A whole bear, head included, glass eyes watching.'},
    'plank_shelf': {
        "name": 'Plank Shelf', "slot": "furniture", "furniture": 'shelf',
        "rarity": 'common', "price": 50, "comfort": 0, "storage": 2,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'Three boards and a lot of hope.'},
    'oak_bookcase': {
        "name": 'Oak Bookcase', "slot": "furniture", "furniture": 'shelf',
        "rarity": 'rare', "price": 250, "comfort": 1, "storage": 5,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'Floor to ceiling, with a ladder.'},
    'iron_bound_cabinet': {
        "name": 'Iron-Bound Cabinet', "slot": "furniture", "furniture": 'shelf',
        "rarity": 'epic', "price": 700, "comfort": 0, "storage": 9,
        "shops": (), "for": "both", "catalogue": False,
        "note": 'Locked, heavy and surprisingly roomy.'},
    'crate_table': {
        "name": 'Crate Table', "slot": "furniture", "furniture": 'table',
        "rarity": 'common', "price": 45, "comfort": 0, "storage": 1,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'A dungeon crate with a cloth on top.'},
    'oak_table': {
        "name": 'Oak Table', "slot": "furniture", "furniture": 'table',
        "rarity": 'rare', "price": 200, "comfort": 1, "storage": 2,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'Scarred by a hundred dinners.'},
    'marble_table': {
        "name": 'Marble Table', "slot": "furniture", "furniture": 'table',
        "rarity": 'epic', "price": 650, "comfort": 3, "storage": 3,
        "shops": (), "for": "both", "catalogue": False,
        "note": 'Cold, smooth and very expensive.'},
    'tallow_candle': {
        "name": 'Tallow Candle', "slot": "furniture", "furniture": 'lamp',
        "rarity": 'common', "price": 25, "comfort": 1, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'Smoky, but it is yours.'},
    'brass_oil_lamp': {
        "name": 'Brass Oil Lamp', "slot": "furniture", "furniture": 'lamp',
        "rarity": 'rare', "price": 140, "comfort": 2, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'A steady amber glow.'},
    'crystal_chandelier': {
        "name": 'Crystal Chandelier', "slot": "furniture", "furniture": 'lamp',
        "rarity": 'epic', "price": 600, "comfort": 4, "storage": 0,
        "shops": (), "for": "both", "catalogue": False,
        "note": 'Throws rainbows on every wall.'},
    'painted_jug': {
        "name": 'Painted Jug', "slot": "furniture", "furniture": 'decor',
        "rarity": 'common', "price": 50, "comfort": 1, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'Blue flowers on grey clay.'},
    'woven_tapestry': {
        "name": 'Woven Tapestry', "slot": "furniture", "furniture": 'decor',
        "rarity": 'rare', "price": 220, "comfort": 3, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'A hunt scene in faded thread.'},
    'gilt_portrait': {
        "name": 'Gilt Portrait', "slot": "furniture", "furniture": 'decor',
        "rarity": 'epic', "price": 750, "comfort": 5, "storage": 0,
        "shops": (), "for": "both", "catalogue": False,
        "note": 'Somebody important, painted kindly.'},
    'wooden_tub': {
        "use": "bath",
        "name": 'Wooden Tub', "slot": "furniture", "furniture": 'bath',
        "rarity": 'common', "price": 90, "comfort": 2, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'Barrel-built and leaky only a little.'},
    'copper_tub': {
        "use": "bath",
        "name": 'Copper Tub', "slot": "furniture", "furniture": 'bath',
        "rarity": 'rare', "price": 350, "comfort": 5, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'Polished copper with a brass tap.'},
    'marble_bath': {
        "use": "bath",
        "name": 'Marble Bath', "slot": "furniture", "furniture": 'bath',
        "rarity": 'epic', "price": 1000, "comfort": 9, "storage": 0,
        "shops": (), "for": "both", "catalogue": False,
        "note": 'Sunk into the floor, steam rising.'},
    'clay_stove': {
        "name": 'Clay Stove', "slot": "furniture", "furniture": 'stove',
        "rarity": 'common', "price": 80, "comfort": 1, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'Squat, stubby and good for stew.'},
    'iron_range': {
        "name": 'Iron Range', "slot": "furniture", "furniture": 'stove',
        "rarity": 'rare', "price": 320, "comfort": 3, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'Six rings, an oven and a warming rack.'},
    'enchanted_hearth': {
        "name": 'Enchanted Hearth', "slot": "furniture", "furniture": 'stove',
        "rarity": 'epic', "price": 900, "comfort": 6, "storage": 0,
        "shops": (), "for": "both", "catalogue": False,
        "note": 'A fire that never needs wood.'},
    'herb_pot': {
        "name": 'Herb Pot', "slot": "furniture", "furniture": 'plant',
        "rarity": 'common', "price": 30, "comfort": 1, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'Thyme, mint and a stubborn weed.'},
    'flower_bed': {
        "name": 'Flower Bed', "slot": "furniture", "furniture": 'plant',
        "rarity": 'rare', "price": 160, "comfort": 2, "storage": 0,
        "shops": (), "for": "both", "catalogue": True,
        "note": 'A bright patch of cultivated colour.'},
    'garden_fountain': {
        "name": 'Garden Fountain', "slot": "furniture", "furniture": 'plant',
        "rarity": 'epic', "price": 650, "comfort": 5, "storage": 0,
        "shops": (), "for": "both", "catalogue": False,
        "note": 'A little stone fountain that sings.'},
    'foot_smothering_box': {
        "name": 'Foot Smothering Box', "slot": "furniture",
        "furniture": 'kinky', "rarity": 'rare', "price": 650, "comfort": 1,
        "storage": 0, "use": "foot", "shops": (), "for": "both",
        "catalogue": True,
        "note": "A lined wooden box with a hinged lid and two carved "
        "footrests. Whoever lies inside breathes what the feet above "
        "them give."},
    'facesitting_throne': {
        "name": 'Facesitting Throne', "slot": "furniture",
        "furniture": 'kinky', "rarity": 'epic', "price": 1400,
        "comfort": 3, "storage": 0, "use": "facesitting", "shops": (),
        "for": "both", "catalogue": False,
        "note": 'A high-backed throne with a cushioned, open seat and a '
        'padded headrest on the floor below it.'},
    'leather_bench': {
        "name": 'Leather Bench', "slot": "furniture", "furniture": 'kinky',
        "rarity": 'rare', "price": 450, "comfort": 1,
        "storage": 0, "use": "bench", "shops": (), "for": "both",
        "catalogue": True,
        "note": "A padded bench with buckled straps at every leg."},
    'spanking_horse': {
        "name": 'Spanking Horse', "slot": "furniture", "furniture": 'kinky',
        "rarity": 'rare', "price": 520, "comfort": 1,
        "storage": 0, "use": "horse", "shops": (), "for": "both",
        "catalogue": True,
        "note": "A narrow padded ridge on four sturdy legs, built to be straddled face down."},
    'bondage_frame': {
        "name": 'Bondage Frame', "slot": "furniture", "furniture": 'kinky',
        "rarity": 'epic', "price": 1100, "comfort": 2,
        "storage": 0, "use": "frame", "shops": (), "for": "both",
        "catalogue": False,
        "note": "An iron frame with four cuffs on adjustable chains."},
    'cage_bed': {
        "name": 'Cage Bed', "slot": "furniture", "furniture": 'kinky',
        "rarity": 'epic', "price": 1600, "comfort": 5,
        "storage": 0, "use": "cage", "shops": (), "for": "both",
        "catalogue": False,
        "note": "A four-poster bed with a barred cage built into its base."},
    "irrigation_system": {
        "name": "Irrigation System", "slot": "furniture",
        "furniture": "utility", "rarity": "rare", "price": 250,
        "comfort": 0, "storage": 0, "irrigates": True,
        "shops": (), "for": "both", "catalogue": True,
        "note": "Copper pipes and a rain barrel. The garden stays damp "
                "when you are away, but it will not grow by itself."},
}
