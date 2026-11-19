from . import registry


MENUS = {
    "cafe": {
        "tea": ("Pot of sweet tea", 3, {"thirst": -40}),
        "slice": ("Slice of cheesecake", 6, {"hunger": -30, "thirst": -5}),
        "puff": ("Cream puff", 4, {"hunger": -20}),
        "layer": ("Berry layer cake", 12, {"hunger": -55, "thirst": -10}),
        "feast": ("Bertha's cake tower", 20,
                  {"hunger": -80, "thirst": -20}),
    },
}


def dish_id(building:str, key:str) -> str:
    return f"dish_{building}_{key}"


def register_dishes(items:dict) -> None:
    for building, menu in MENUS.items():
        for key, (name, price, effects) in menu.items():
            items[dish_id(building, key)] = {
                "name": name, "slot": "consumable", "rarity": "common",
                "needs": dict(effects), "price": price, "no_loot": True,
                "note": f"takeaway from the {TITLES[building]}"}


TITLES = {"cafe": "Fat Ass Café"}


DISH_KG = {
    ("cafe", "tea"): 0, ("cafe", "puff"): 1, ("cafe", "slice"): 2,
    ("cafe", "layer"): 3, ("cafe", "feast"): 6,
}
HOUSE_CAKE_KG = 3


for _spec in registry.specs().values():
    if _spec.menu:
        MENUS[_spec.key] = _spec.menu
        TITLES[_spec.key] = _spec.menu_title
        DISH_KG.update({(_spec.key, key): kg
                        for key, kg in _spec.dish_kg.items()})
