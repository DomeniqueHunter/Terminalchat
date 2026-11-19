from ....town_buildings.counter import Offer, Special
from .bindings import BINDINGS
from .items import ITEMS


KEY = "tailor"
GROUPS = {
    "Bottoms": ("crotch",),
    "Lingerie": ("lingerie",),
    "Dresses & tops": ("chest",),
    "Footwear & gloves": ("feet", "gloves"),
    "Headwear & jewelry": ("head", "accessory"),
    "Bindings": (),
}
SIDE_ORDER = {"both": 0, "lady": 1, "gent": 2}


def group_of(item_id:str) -> str:
    if item_id in BINDINGS:
        return "Bindings"
    slot = ITEMS[item_id]["slot"]
    return next(name for name, slots in GROUPS.items() if slot in slots)


def sort_key(ware:tuple[str, str]) -> tuple[int, int, str]:
    group = list(GROUPS).index(group_of(ware[1]))
    return group, SIDE_ORDER[ITEMS[ware[1]].get("for", "both")], ware[0]


TITLE = "Rook & Thread"
BLURB = ("Made-to-order fashion for the Hollow's high society. Mistress "
         "Delphine measures twice and judges once.")
WARES = (
    ("Hollow Wrap Skirt", "hollow_wrap_skirt"),
    ("Pleated Velvet Skirt [ladies]", "pleated_velvet_skirt"),
    ("Slit Silk Skirt", "slit_silk_skirt"),
    ("Tailored Black Trousers", "tailored_black_trousers"),
    ("Satin Hotpants [ladies]", "satin_hotpants"),
    ("Lace Thong [ladies]", "lace_thong"),
    ("Velvet Laced Thong [ladies]", "velvet_laced_thong"),
    ("Silk Pouch Brief [gents]", "silk_pouch_brief"),
    ("Jet-Beaded Garter Set [ladies]", "jet_beaded_garter_set"),
    ("Dagger Garter [ladies]", "dagger_garter"),
    ("Silk Thigh-Highs [ladies]", "silk_thigh_highs"),
    ("Lacquered Ankle Boots", "lacquered_ankle_boots"),
    ("Gentleman's Black Boots [gents]", "gentlemans_black_boots"),
    ("Lace Gloves", "lace_gloves"),
    ("Black Lace Veil [ladies]", "black_lace_veil"),
    ("High-Collared Silk Blouse", "high_collared_silk_blouse"),
    ("Velvet Frock Coat", "velvet_frock_coat"),
    ("Corset Bodice Dress [ladies]", "corset_bodice_dress"),
    ("Evening Gown with Slit [ladies]", "evening_gown_with_slit"),
    ("Backless Velvet Dress [ladies]", "backless_velvet_dress"),
    ("Open-Bodice Velvet Dress [ladies]", "open_bodice_velvet_dress"),
    ("Dress of Open Doors [ladies]", "dress_of_open_doors"),
    ("Ballgown of the Pale Court [ladies]", "ballgown_of_the_pale_court"),
    ("Brass Nipple Chains", "brass_nipple_chains"),
    ("Gilded Bell Chains", "gilded_bell_chains"),
    ("Leather Wrist Cuffs", "leather_wrist_cuffs"),
    ("Leather Ankle Cuffs", "leather_ankle_cuffs"),
    ("Velvet Blindfold", "velvet_blindfold"),
    ("Collar with Ring", "collar_with_ring"),
    ("Chain Leash", "chain_leash"),
    ("Silk Rope Harness", "silk_rope_harness"),
    ("Leather Gag", "leather_gag"),
    ("Spreader Bar", "spreader_bar"),
)
SPECIAL = Special(
    KEY, TITLE, BLURB, "🧵", "Mistress Delphine Rook",
    "'Stand still. I measure twice and I judge once.'",
    tuple(Offer(label, "item", item=item_id)
          for label, item_id in sorted(WARES, key=sort_key)))
