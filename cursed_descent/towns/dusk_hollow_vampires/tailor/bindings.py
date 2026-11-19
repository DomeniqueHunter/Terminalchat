# Restraint gear sold by the tailor. Pieces use the normal slots, so the
# Kept set fills gloves, feet, head and accessory without a new slot.


def piece(name:str, slot:str, rarity:str, price:int, allure:int,
          note:str, **extra) -> dict:
    return {"name": name, "slot": slot, "rarity": rarity, "allure": allure,
            "for": "both", "price": price, "shops": (), "no_loot": True,
            "note": note, **extra}


BINDINGS = {
    "leather_wrist_cuffs": piece(
        "Leather Wrist Cuffs", "gloves", "common", 40, 1,
        "Soft-lined cuffs with a steel ring on each wrist.", set="kept"),
    "leather_ankle_cuffs": piece(
        "Leather Ankle Cuffs", "feet", "common", 40, 1,
        "Buckled cuffs that make every step a little shorter.", set="kept"),
    "velvet_blindfold": piece(
        "Velvet Blindfold", "head", "common", 40, 1,
        "Thick velvet that shuts out every light.", set="kept"),
    "collar_with_ring": piece(
        "Collar with Ring", "accessory", "rare", 150, 2,
        "A black leather collar with a ring at the throat, made to be "
        "held.", set="kept", bonus={"vitality": 1}),
    "chain_leash": piece(
        "Chain Leash", "accessory", "rare", 150, 2,
        "A fine chain with a leather loop for the hand that holds it."),
    "silk_rope_harness": piece(
        "Silk Rope Harness", "chest", "rare", 150, 2,
        "Black silk rope knotted across the chest. It holds, it shows, "
        "it covers nothing.", reveals=("breasts",)),
    "leather_gag": piece(
        "Leather Gag", "head", "rare", 150, 2,
        "A padded strap with a quiet clasp. Worn by choice, removed by "
        "word."),
    "spreader_bar": piece(
        "Spreader Bar", "accessory", "epic", 500, 3,
        "A polished bar with cuffs at both ends. It keeps things "
        "apart."),
}

KEPT_SET = {
    "name": "Kept",
    "bonuses": {2: {"allure": 2}, 3: {"allure": 2},
                4: {"allure": 4, "bonus": {"vitality": 2}}},
}
