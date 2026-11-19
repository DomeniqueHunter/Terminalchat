from importlib import import_module
from pathlib import Path

from ..settings import PROTOTYPES, ensure_loaded, fill_data, on_bind
from .combat import SPELLS
from .combat import INTENT_TEXTS
from .combat import ACTION_MULTIPLIERS
from ..monster.beasts.content import ENEMIES as ENEMIES_BEASTS
from ..monster.oozes.content import ENEMIES as ENEMIES_OOZES
from ..monster.goblins.content import ENEMIES as ENEMIES_GOBLINS
from ..monster.orcs.content import ENEMIES as ENEMIES_ORCS
from ..monster.ogres.content import ENEMIES as ENEMIES_OGRES
from ..monster.amazons.content import ENEMIES as ENEMIES_AMAZONS
from ..monster.giants.content import ENEMIES as ENEMIES_GIANTS
from ..monster.pigmen.content import ENEMIES as ENEMIES_PIGMEN
from ..monster.undead.content import ENEMIES as ENEMIES_UNDEAD
from ..monster.humans.content import ENEMIES as ENEMIES_HUMANS
from ..monster.constructs.content import ENEMIES as ENEMIES_CONSTRUCTS
from ..monster.drainers.content import ENEMIES as ENEMIES_DRAINERS
from ..monster.vines.content import ENEMIES as ENEMIES_VINES
from ..monster.winter.content import ENEMIES as ENEMIES_WINTER
from ..monster.biomes import BIOMES
from ..monster.order import ENEMY_ORDER
from .fates import FATES as FATES_BASE
from ..locations.lodge.fates import FATES as FATES_LODGE
from ..locations.farm.fates import FATES as FATES_FARM
from ..locations.butcher.fates import FATES as FATES_BUTCHER
from ..locations.brewery.fates import FATES as FATES_BREWERY
from ..locations.boutique.fates import FATES as FATES_BOUTIQUE
from ..locations.couch.fates import FATES as FATES_COUCH
from ..locations.wardrobe.fates import FATES as FATES_WARDROBE
from ..locations.throne.fates import FATES as FATES_THRONE
from ..locations.glory_hole.fates import FATES as FATES_GLORY
from ..locations.fisher.fates import FATES as FATES_FISHER
from ..locations.grill.fates import FATES as FATES_GRILL
from ..locations.dairy.fates import FATES as FATES_DAIRY
from ..locations.privy.fates import FATES as FATES_PRIVY
from ..locations.pod_garden.fates import FATES as FATES_POD
from ..events.maid.fates import FATES as FATES_MAID
from ..locations.citystop.fates import FATES as FATES_STAKED
from ..locations.sweatery.fates import FATES as FATES_SWEATERY
from ..locations.smokery.fates import FATES as FATES_SMOKERY
from ..events.lich.fates import FATES as FATES_LICH
from ..events.mrs_claus.fates import FATES as FATES_CLAUS
from ..locations.displays.fates import FATES as FATES_DISPLAYS
from .fates import FATE_LABELS as FATE_LABELS_BASE
from ..locations.lodge.fates import FATE_LABELS as FATE_LABELS_LODGE
from ..locations.farm.fates import FATE_LABELS as FATE_LABELS_FARM
from ..locations.butcher.fates import FATE_LABELS as FATE_LABELS_BUTCHER
from ..locations.brewery.fates import FATE_LABELS as FATE_LABELS_BREWERY
from ..locations.boutique.fates import FATE_LABELS as FATE_LABELS_BOUTIQUE
from ..locations.couch.fates import FATE_LABELS as FATE_LABELS_COUCH
from ..locations.wardrobe.fates import FATE_LABELS as FATE_LABELS_WARDROBE
from ..locations.throne.fates import FATE_LABELS as FATE_LABELS_THRONE
from ..locations.glory_hole.fates import FATE_LABELS as FATE_LABELS_GLORY
from ..locations.fisher.fates import FATE_LABELS as FATE_LABELS_FISHER
from ..locations.grill.fates import FATE_LABELS as FATE_LABELS_GRILL
from ..locations.dairy.fates import FATE_LABELS as FATE_LABELS_DAIRY
from ..locations.privy.fates import FATE_LABELS as FATE_LABELS_PRIVY
from ..locations.pod_garden.fates import FATE_LABELS as FATE_LABELS_POD
from ..events.maid.fates import FATE_LABELS as FATE_LABELS_MAID
from ..locations.citystop.fates import FATE_LABELS as FATE_LABELS_STAKED
from ..locations.sweatery.fates import FATE_LABELS as FATE_LABELS_SWEATERY
from ..locations.smokery.fates import FATE_LABELS as FATE_LABELS_SMOKERY
from ..events.lich.fates import FATE_LABELS as FATE_LABELS_LICH
from ..events.mrs_claus.fates import FATE_LABELS as FATE_LABELS_CLAUS
from ..locations.displays.fates import FATE_LABELS as FATE_LABELS_DISPLAYS
from ..events.adept.fates import FATE_LABELS as FATE_LABELS_ADEPT
from .fates import DISTRACT_TEXTS
from .remains import REMAINS_TEXTS as REMAINS_TEXTS_BASE
from ..locations.lodge.fates import REMAINS_TEXTS as REMAINS_TEXTS_LODGE
from ..locations.farm.fates import REMAINS_TEXTS as REMAINS_TEXTS_FARM
from ..locations.butcher.fates import REMAINS_TEXTS as REMAINS_TEXTS_BUTCHER
from ..locations.brewery.fates import REMAINS_TEXTS as REMAINS_TEXTS_BREWERY
from ..locations.boutique.fates import REMAINS_TEXTS as REMAINS_TEXTS_BOUTIQUE
from ..locations.couch.fates import REMAINS_TEXTS as REMAINS_TEXTS_COUCH
from ..locations.wardrobe.fates import REMAINS_TEXTS as REMAINS_TEXTS_WARDROBE
from ..locations.throne.fates import REMAINS_TEXTS as REMAINS_TEXTS_THRONE
from ..locations.glory_hole.fates import REMAINS_TEXTS as REMAINS_TEXTS_GLORY
from ..locations.fisher.fates import REMAINS_TEXTS as REMAINS_TEXTS_FISHER
from ..locations.grill.fates import REMAINS_TEXTS as REMAINS_TEXTS_GRILL
from ..locations.dairy.fates import REMAINS_TEXTS as REMAINS_TEXTS_DAIRY
from ..locations.privy.fates import REMAINS_TEXTS as REMAINS_TEXTS_PRIVY
from ..locations.pod_garden.fates import REMAINS_TEXTS as REMAINS_TEXTS_POD
from ..events.maid.fates import REMAINS_TEXTS as REMAINS_TEXTS_MAID
from ..locations.citystop.fates import REMAINS_TEXTS as REMAINS_TEXTS_STAKED
from ..locations.sweatery.fates import REMAINS_TEXTS as REMAINS_TEXTS_SWEATERY
from ..locations.smokery.fates import REMAINS_TEXTS as REMAINS_TEXTS_SMOKERY
from ..events.lich.fates import REMAINS_TEXTS as REMAINS_TEXTS_LICH
from ..events.mrs_claus.fates import REMAINS_TEXTS as REMAINS_TEXTS_CLAUS
from ..locations.displays.fates import REMAINS_TEXTS as REMAINS_TEXTS_DISPLAYS
from ..events.adept.fates import REMAINS_TEXTS as REMAINS_TEXTS_ADEPT
from .offspring import OFFSPRING_NAMES
from .offspring import OFFSPRING_TEXTS
from ..events.wanderer.content import WANDERERS
from ..locations.boutique.content import BOUTIQUE_GARMENTS
from ..locations.boutique.content import BOUTIQUE_FALLBACK
from ..events.adept.content import ADEPT_BUFFS
from .remains import SKELETON_TEXTS
from ..events.adept.content import ADEPT_STATUE_TEXTS
from ..locations.clinic.content import ENHANCEMENTS
from ..locations.clinic.content import CLINIC_TEXTS
from ..events.wanderer.content import WEAR_TEXTS
from ..events.wanderer.content import WANDERER_THANKS
from ..events.adept.content import ADEPT_FLUSTER
from ..events.adept.content import GALLERY_LABELS
from ..locations.lodge.content import HUNTER_HUTS
from ..locations.lodge.content import LODGE_DISPLAYS
from ..locations.farm.content import FARM_JOBS
from ..locations.farm.content import FARM_PRODUCTS
from ..locations.farm.content import FARM_PRODUCT_NOTES
from ..locations.farm.content import FARM_SHIFT_TEXTS
from ..locations.farm.content import FARM_SHIFT_EVENTS
from ..events.sweaty.content import SWEATY_TEXTS
from ..events.sweaty.content import SWEATY_TEASES
from .sweat import SWEAT_LABELS
from .sweat import SWEAT_TEXTS
from ..locations.butcher.content import MEAT_GRADE_LABELS
from ..locations.butcher.content import HORSE_CUT
from ..locations.butcher.content import EXTRA_CUTS
from ..locations.butcher.content import SAUSAGE_CUTS
from ..locations.brewery.content import BREWERY_STYLES
from ..locations.brewery.content import BREWERY_TEXTS
from ..locations.brewery.content import ASTRID_GROWTH
from ..locations.brewery.content import FRESH_TIERS
from ..locations.brewery.content import BREW_GRADE_LABELS
from ..locations.butcher.content import BUTCHER_CUTS
from ..locations.lodge.content import VENUE_TEXTS as VENUE_TEXTS_LODGE
from ..locations.butcher.content import VENUE_TEXTS as VENUE_TEXTS_BUTCHER
from ..locations.farm.content import VENUE_TEXTS as VENUE_TEXTS_FARM
from ..locations.couch.content import VENUE_TEXTS as VENUE_TEXTS_COUCH
from ..locations.bivouac.content import VENUE_TEXTS as VENUE_TEXTS_BIVOUAC
from ..locations.citystop.content import VENUE_TEXTS as VENUE_TEXTS_CITYSTOP
from ..locations.sweatery.content import VENUE_TEXTS as VENUE_TEXTS_SWEATERY
from ..locations.smokery.content import VENUE_TEXTS as VENUE_TEXTS_SMOKERY
from ..locations.mage_tower.content import VENUE_TEXTS as VENUE_TEXTS_MAGE
from ..locations.wardrobe.content import VENUE_TEXTS as VENUE_TEXTS_WARDROBE
from ..locations.throne.content import VENUE_TEXTS as VENUE_TEXTS_THRONE
from ..locations.glory_hole.content import VENUE_TEXTS as VENUE_TEXTS_GLORY
from ..locations.glory_hole.content import GLORY_BUFFS
from ..locations.fisher.content import FISHER_BUFFS
from ..locations.grill.content import GRILL_BUFFS
from ..locations.grill.content import VENUE_TEXTS as VENUE_TEXTS_GRILL
from ..locations.dairy.content import DAIRY_BUFFS
from ..locations.privy.content import PRIVY_BUFFS
from ..towns.dusk_hollow_vampires.blood_bank.content import BLOOD_BUFFS
from ..towns.brandholm_nords.ember_cask.content import BREW_BUFFS
from ..towns.brandholm_nords.buffs import BRANDHOLM_BUFFS
from ..towns.brandholm_nords.fates import FATES as FATES_BRANDHOLM
from ..towns.brandholm_nords.fates import FATE_LABELS as FATE_LABELS_BRANDHOLM
from ..towns.brandholm_nords.fates import REMAINS_TEXTS as REMAINS_TEXTS_BRANDHOLM
from ..towns.dusk_hollow_vampires.castle.content import CASTLE_BUFFS
from ..towns.dusk_hollow_vampires.salon.content import SALON_BUFFS
from ..locations.privy.content import VENUE_TEXTS as VENUE_TEXTS_PRIVY
from ..locations.pod_garden.content import VENUE_TEXTS as VENUE_TEXTS_POD
from ..locations.dairy.content import VENUE_TEXTS as VENUE_TEXTS_DAIRY
from ..locations.fisher.content import VENUE_TEXTS as VENUE_TEXTS_FISHER
from ..locations.wedding.content import VENUE_TEXTS as VENUE_TEXTS_WEDDING
from ..locations.smith.content import SMITH_TEXTS
from ..locations.lodge.fates import LOCATION_NOTES as LOCATION_NOTES_LODGE
from ..locations.farm.fates import LOCATION_NOTES as LOCATION_NOTES_FARM
from ..locations.brewery.fates import LOCATION_NOTES as LOCATION_NOTES_BREWERY
from ..locations.sweatery.fates import LOCATION_NOTES as LOCATION_NOTES_SWEATERY
from ..locations.smokery.fates import LOCATION_NOTES as LOCATION_NOTES_SMOKERY
from ..locations.butcher.fates import LOCATION_NOTES as LOCATION_NOTES_BUTCHER
from .remains import EXAMINE_TEXTS
from .remains import SOUL_HUNGER_TEXTS
from .remains import CONSORT_TEXTS
from .events import EVENT_TEXTS as EVENT_TEXTS_BASE
from ..locations.lodge.content import EVENT_TEXTS as EVENT_TEXTS_LODGE
from ..locations.boutique.content import EVENT_TEXTS as EVENT_TEXTS_BOUTIQUE
from ..locations.butcher.content import EVENT_TEXTS as EVENT_TEXTS_BUTCHER
from ..locations.farm.content import EVENT_TEXTS as EVENT_TEXTS_FARM
from ..events.ogre.content import EVENT_TEXTS as EVENT_TEXTS_OGRE
from ..events.lich.content import EVENT_TEXTS as EVENT_TEXTS_LICH
from ..events.mrs_claus.content import EVENT_TEXTS as EVENT_TEXTS_CLAUS
from ..locations.north_pole.content import VENUE_TEXTS as VENUE_TEXTS_POLE
from ..events.adept.content import EVENT_TEXTS as EVENT_TEXTS_ADEPT
from ..events.maid.content import EVENT_TEXTS as EVENT_TEXTS_MAID
from ..events.maid.content import MAID_BUFFS
from ..events.wanderer.content import EVENT_TEXTS as EVENT_TEXTS_WANDERER
from ..events.recruiter.content import EVENT_TEXTS as EVENT_TEXTS_RECRUITER
from ..events.null_master.content import EVENT_TEXTS as EVENT_TEXTS_NULL
from ..events.caravaneer.content import EVENT_TEXTS as EVENT_TEXTS_CARAVAN
from ..events.drainer.content import EVENT_TEXTS as EVENT_TEXTS_DRAINER
from ..events.drainer.fates import FATES as FATES_DRAINER
from ..events.drainer.fates import FATE_LABELS as FATE_LABELS_DRAINER
from ..events.drainer.fates import REMAINS_TEXTS as REMAINS_TEXTS_DRAINER
from ..events.caravaneer.fates import FATES as FATES_CARAVAN
from ..events.caravaneer.fates import FATE_LABELS as FATE_LABELS_CARAVAN
from ..events.caravaneer.fates import REMAINS_TEXTS as REMAINS_TEXTS_CARAVAN
from ..events.null_master.fates import FATES as FATES_NULL
from ..towns.last_light_humans.cafe.fates import FATES as FATES_CAFE
from ..towns.last_light_humans.cafe.fates import FATE_LABELS as FATE_LABELS_CAFE
from ..towns.last_light_humans.cafe.fates import REMAINS_TEXTS as REMAINS_TEXTS_CAFE
from ..events.null_master.fates import FATE_LABELS as FATE_LABELS_NULL
from ..events.null_master.fates import REMAINS_TEXTS as REMAINS_TEXTS_NULL
from ..events.recruiter.fates import FATES as FATES_RECRUITER
from ..events.recruiter.fates import FATE_LABELS as FATE_LABELS_RECRUITER
from ..events.recruiter.fates import REMAINS_TEXTS as REMAINS_TEXTS_RECRUITER
from .events import CHEST_TEXTS
from ..locations.shop.content import SHOPKEEPER
from .titles import TITLES
from .titles import COMBO_TITLES
from .items import RARITY_LABELS
from .items import ITEM_SETS
from .items import ITEMS
from .merge import merge_ordered
from ..furnishing.buffs import HOME_BUFFS
from ..furnishing.items import ITEMS as FURNITURE_ITEMS
from ..town_buildings.orphanage.content import ORPHANAGE_BUFFS
from ..plants import BUFFS as PLANT_BUFFS, ITEMS as PLANT_ITEMS
from ..town_buildings.dishes import register_dishes
from ..town_buildings.registry import register_items

BUFFS = {**ADEPT_BUFFS, **GLORY_BUFFS, **FISHER_BUFFS, **GRILL_BUFFS, **MAID_BUFFS,
         **DAIRY_BUFFS, **PRIVY_BUFFS, **BLOOD_BUFFS, **BREW_BUFFS,
         **BRANDHOLM_BUFFS, **HOME_BUFFS, **PLANT_BUFFS, **ORPHANAGE_BUFFS,
         **SALON_BUFFS, **CASTLE_BUFFS}

for folder in ("locations", "events", "towns"):
    for path in sorted((Path(__file__).parent.parent / folder).glob(
            "*/items.py")):
        store = import_module(f"..{folder}.{path.parent.name}.items",
                              __package__)
        ITEMS.update(getattr(store, "ITEMS", {}))
        ITEM_SETS.update(getattr(store, "ITEM_SETS", {}))

for path in sorted((Path(__file__).parent.parent / "towns").glob(
        "*/*/items.py")):
    store = import_module(f"..towns.{path.parent.parent.name}."
                          f"{path.parent.name}.items", __package__)
    ITEMS.update(getattr(store, "ITEMS", {}))
    ITEM_SETS.update(getattr(store, "ITEM_SETS", {}))

ITEMS.update(FURNITURE_ITEMS)
ITEMS.update(PLANT_ITEMS)
register_dishes(ITEMS)
register_items(ITEMS)


FATES = merge_ordered(
    (
        "statue",
        "wall",
        "door",
        "eaten",
        "roasted",
        "breeding",
        "swallowed",
        "lodge",
        "fashion",
        "dairy",
        "trophy",
        "dissolved",
        "flattened",
        "iron_maiden",
        "brewed",
        "butchered",
        "farmed",
        "heated",
        "smoked",
        "sweated",
        "hall_smoked",
        "roasted",
        "podded",
        "vined",
        "couch_mimic",
        "wardrobe",
        "throne",
        "glory_hole",
        "fished",
        "fish_food",
        "drained",
        "stud",
        "tapped",
        "sold_brew",
        "brooding",
        "roast",
        "torn",
        "hauled",
        "circus",
        "staked",
        "entombed",
        "ice_statue",
        "consort",
        "sacked",
        "encased",
        "recruited",
        "nulled",
        "caravaned",
        "drained",
        "smothered",
        "milked_dry",
        "bull_stud",
        "culled",
        "fixture",
        "spit_roasted",
        "paddle_shattered",
        "paddle_popped",
        "paddle_busted",
        "paddle_squashed",
        "paddle_decimated",
        "paddle_mangled",
        "paddle_obliterated",
        "paddle_annihilated",
        "paddle_vaporized",
        "paddle_demolished",
        "paddle_wiped_out",
        "paddle_eradicated",
        "paddle_pummeled",
        "paddle_terminated",
        "paddle_shredded",
        "paddle_eviscerated",
        "paddle_exterminated",
        "paddle_disintegrated",
        "paddle_splattered",
        "paddle_pancaked",
        "paddle_launched",
        "paddle_folded",
        "paddle_bounced",
        "paddle_flatpacked",
        "collapsed",
        "engulfed",
        "vored",
        "anal_vored",
    ),
    FATES_BASE,
    FATES_LODGE,
    FATES_FARM,
    FATES_BUTCHER,
    FATES_BREWERY,
    FATES_BOUTIQUE,
    FATES_COUCH,
    FATES_WARDROBE,
    FATES_THRONE,
    FATES_GLORY,
    FATES_FISHER,
    FATES_GRILL,
    FATES_DAIRY,
    FATES_PRIVY,
    FATES_POD,
    FATES_MAID,
    FATES_STAKED,
    FATES_SWEATERY,
    FATES_SMOKERY,
    FATES_BRANDHOLM,
    FATES_LICH,
    FATES_CLAUS,
    FATES_DISPLAYS,
    FATES_RECRUITER,
    FATES_NULL,
    FATES_CARAVAN,
    FATES_DRAINER,
    FATES_CAFE,
)

FATE_LABELS = merge_ordered(
    (
        "statue",
        "wall",
        "door",
        "eaten",
        "roasted",
        "breeding",
        "swallowed",
        "dairy",
        "lodge",
        "fashion",
        "trophy",
        "dissolved",
        "encased",
        "ice_statue",
        "entombed",
        "flattened",
        "flattened_hammer",
        "flattened_floor",
        "iron_maiden",
        "iron_maiden_spat",
        "butchered",
        "brewed",
        "farmed",
        "heated",
        "smoked",
        "sweated",
        "hall_smoked",
        "roasted",
        "podded",
        "vined",
        "couch_mimic",
        "wardrobe",
        "throne",
        "glory_hole",
        "fished",
        "fish_food",
        "drained",
        "stud",
        "tapped",
        "sold_brew",
        "brooding",
        "roast",
        "torn",
        "hauled",
        "circus",
        "staked",
        "soulbound",
        "adept_statue",
        "adept_statue_breasts",
        "adept_statue_balls",
        "adept_statue_butt",
        "adept_statue_penis",
        "consort",
        "sacked",
        "recruited",
        "nulled",
        "caravaned",
        "drained",
        "smothered",
        "milked_dry",
        "bull_stud",
        "culled",
        "fixture",
        "spit_roasted",
        "paddle_shattered",
        "paddle_popped",
        "paddle_busted",
        "paddle_squashed",
        "paddle_decimated",
        "paddle_mangled",
        "paddle_obliterated",
        "paddle_annihilated",
        "paddle_vaporized",
        "paddle_demolished",
        "paddle_wiped_out",
        "paddle_eradicated",
        "paddle_pummeled",
        "paddle_terminated",
        "paddle_shredded",
        "paddle_eviscerated",
        "paddle_exterminated",
        "paddle_disintegrated",
        "paddle_splattered",
        "paddle_pancaked",
        "paddle_launched",
        "paddle_folded",
        "paddle_bounced",
        "paddle_flatpacked",
        "collapsed",
        "engulfed",
        "vored",
        "anal_vored",
    ),
    FATE_LABELS_BASE,
    FATE_LABELS_LODGE,
    FATE_LABELS_FARM,
    FATE_LABELS_BUTCHER,
    FATE_LABELS_BREWERY,
    FATE_LABELS_BOUTIQUE,
    FATE_LABELS_COUCH,
    FATE_LABELS_WARDROBE,
    FATE_LABELS_THRONE,
    FATE_LABELS_GLORY,
    FATE_LABELS_FISHER,
    FATE_LABELS_GRILL,
    FATE_LABELS_DAIRY,
    FATE_LABELS_PRIVY,
    FATE_LABELS_POD,
    FATE_LABELS_MAID,
    FATE_LABELS_STAKED,
    FATE_LABELS_SWEATERY,
    FATE_LABELS_SMOKERY,
    FATE_LABELS_BRANDHOLM,
    FATE_LABELS_LICH,
    FATE_LABELS_CLAUS,
    FATE_LABELS_DISPLAYS,
    FATE_LABELS_ADEPT,
    FATE_LABELS_RECRUITER,
    FATE_LABELS_NULL,
    FATE_LABELS_CARAVAN,
    FATE_LABELS_DRAINER,
    FATE_LABELS_CAFE,
)

REMAINS_TEXTS = merge_ordered(
    (
        "statue",
        "wall",
        "door",
        "eaten",
        "roasted",
        "lodge",
        "fashion",
        "dairy",
        "swallowed",
        "breeding",
        "trophy",
        "dissolved",
        "encased",
        "ice_statue",
        "entombed",
        "flattened",
        "flattened_floor",
        "flattened_hammer",
        "iron_maiden",
        "iron_maiden_spat",
        "butchered",
        "brewed",
        "farmed",
        "couch_mimic",
        "wardrobe",
        "throne",
        "glory_hole",
        "fished",
        "fish_food",
        "drained",
        "stud",
        "tapped",
        "sold_brew",
        "brooding",
        "roast",
        "torn",
        "hauled",
        "circus",
        "staked",
        "soulbound",
        "adept_statue_breasts",
        "adept_statue_balls",
        "adept_statue_butt",
        "adept_statue_penis",
        "adept_statue",
        "consort",
        "sacked",
        "recruited",
        "nulled",
        "caravaned",
        "drained",
        "smothered",
        "milked_dry",
        "bull_stud",
        "culled",
        "fixture",
        "spit_roasted",
        "paddle_shattered",
        "paddle_popped",
        "paddle_busted",
        "paddle_squashed",
        "paddle_decimated",
        "paddle_mangled",
        "paddle_obliterated",
        "paddle_annihilated",
        "paddle_vaporized",
        "paddle_demolished",
        "paddle_wiped_out",
        "paddle_eradicated",
        "paddle_pummeled",
        "paddle_terminated",
        "paddle_shredded",
        "paddle_eviscerated",
        "paddle_exterminated",
        "paddle_disintegrated",
        "paddle_splattered",
        "paddle_pancaked",
        "paddle_launched",
        "paddle_folded",
        "paddle_bounced",
        "paddle_flatpacked",
        "collapsed",
        "engulfed",
        "vored",
        "anal_vored",
        "own",
        "item",
        "no_item",
        "commands",
        "stew",
        "stew_gone",
        "taste",
        "taste_own",
        "taste_spoiled",
        "pack",
        "pack_own",
        "no_stew",
        "dairy_bucket",
        "dairy_gone",
        "dairy_found",
        "dairy_found_own",
        "dairy_full",
        "loot",
        "loot_own",
        "loot_none",
        "pray",
        "pass",
        "heated",
        "smoked",
        "sweated",
        "hall_smoked",
        "roasted",
        "podded",
        "vined",
    ),
    REMAINS_TEXTS_BASE,
    REMAINS_TEXTS_LODGE,
    REMAINS_TEXTS_FARM,
    REMAINS_TEXTS_BUTCHER,
    REMAINS_TEXTS_BREWERY,
    REMAINS_TEXTS_BOUTIQUE,
    REMAINS_TEXTS_COUCH,
    REMAINS_TEXTS_WARDROBE,
    REMAINS_TEXTS_THRONE,
    REMAINS_TEXTS_GLORY,
    REMAINS_TEXTS_FISHER,
    REMAINS_TEXTS_GRILL,
    REMAINS_TEXTS_DAIRY,
    REMAINS_TEXTS_PRIVY,
    REMAINS_TEXTS_POD,
    REMAINS_TEXTS_MAID,
    REMAINS_TEXTS_STAKED,
    REMAINS_TEXTS_SWEATERY,
    REMAINS_TEXTS_SMOKERY,
    REMAINS_TEXTS_BRANDHOLM,
    REMAINS_TEXTS_LICH,
    REMAINS_TEXTS_CLAUS,
    REMAINS_TEXTS_DISPLAYS,
    REMAINS_TEXTS_ADEPT,
    REMAINS_TEXTS_RECRUITER,
    REMAINS_TEXTS_NULL,
    REMAINS_TEXTS_CARAVAN,
    REMAINS_TEXTS_DRAINER,
    REMAINS_TEXTS_CAFE,
)

VENUE_TEXTS = merge_ordered(
    (
        "hut",
        "butcher_shop",
        "farm",
        "couch",
        "sweatery",
        "smokery",
        "bivouac",
        "citystop",
        "mage_tower",
        "wardrobe",
        "throne",
        "glory_hole",
        "wedding",
        "fisher",
        "grill",
        "dairy",
        "privy",
        "pod_garden",
        "north_pole",
    ),
    VENUE_TEXTS_LODGE,
    VENUE_TEXTS_BUTCHER,
    VENUE_TEXTS_FARM,
    VENUE_TEXTS_COUCH,
    VENUE_TEXTS_SWEATERY,
    VENUE_TEXTS_SMOKERY,
    VENUE_TEXTS_BIVOUAC,
    VENUE_TEXTS_CITYSTOP,
    VENUE_TEXTS_MAGE,
    VENUE_TEXTS_WARDROBE,
    VENUE_TEXTS_THRONE,
    VENUE_TEXTS_GLORY,
    VENUE_TEXTS_FISHER,
    VENUE_TEXTS_GRILL,
    VENUE_TEXTS_DAIRY,
    VENUE_TEXTS_PRIVY,
    VENUE_TEXTS_POD,
    VENUE_TEXTS_POLE,
    VENUE_TEXTS_WEDDING,
)

LOCATION_NOTES = merge_ordered(
    (
        "lodge",
        "farmed",
        "brewed",
        "butchered",
    ),
    LOCATION_NOTES_LODGE,
    LOCATION_NOTES_FARM,
    LOCATION_NOTES_BREWERY,
    LOCATION_NOTES_BUTCHER,
    LOCATION_NOTES_SWEATERY,
    LOCATION_NOTES_SMOKERY,
)

EVENT_TEXTS = merge_ordered(
    (
        "hunter",
        "couture",
        "recruiter",
        "butcher",
        "farmer",
        "ogre_feast",
        "lich",
        "mrs_claus",
        "adept",
        "buster_maid",
        "boutique",
        "wanderer",
        "null_master",
        "caravaneer",
        "drainer",
        "used",
        "invalid",
        "timeout",
    ),
    EVENT_TEXTS_BASE,
    EVENT_TEXTS_LODGE,
    EVENT_TEXTS_BOUTIQUE,
    EVENT_TEXTS_BUTCHER,
    EVENT_TEXTS_FARM,
    EVENT_TEXTS_OGRE,
    EVENT_TEXTS_LICH,
    EVENT_TEXTS_CLAUS,
    EVENT_TEXTS_ADEPT,
    EVENT_TEXTS_MAID,
    EVENT_TEXTS_WANDERER,
    EVENT_TEXTS_RECRUITER,
    EVENT_TEXTS_NULL,
    EVENT_TEXTS_CARAVAN,
    EVENT_TEXTS_DRAINER,
)


ENEMIES = merge_ordered(
    ENEMY_ORDER,
    ENEMIES_BEASTS,
    ENEMIES_OOZES,
    ENEMIES_GOBLINS,
    ENEMIES_ORCS,
    ENEMIES_OGRES,
    ENEMIES_AMAZONS,
    ENEMIES_GIANTS,
    ENEMIES_PIGMEN,
    ENEMIES_UNDEAD,
    ENEMIES_HUMANS,
    ENEMIES_CONSTRUCTS,
    ENEMIES_DRAINERS,
    ENEMIES_VINES,
    ENEMIES_WINTER,
)

__all__ = [
    "SPELLS",
    "INTENT_TEXTS",
    "ACTION_MULTIPLIERS",
    "ENEMIES",
    "BIOMES",
    "FATES",
    "FATE_LABELS",
    "DISTRACT_TEXTS",
    "REMAINS_TEXTS",
    "OFFSPRING_NAMES",
    "OFFSPRING_TEXTS",
    "WANDERERS",
    "BOUTIQUE_GARMENTS",
    "BOUTIQUE_FALLBACK",
    "ADEPT_BUFFS",
    "BUFFS",
    "SKELETON_TEXTS",
    "ADEPT_STATUE_TEXTS",
    "ENHANCEMENTS",
    "CLINIC_TEXTS",
    "WEAR_TEXTS",
    "WANDERER_THANKS",
    "ADEPT_FLUSTER",
    "GALLERY_LABELS",
    "HUNTER_HUTS",
    "LODGE_DISPLAYS",
    "FARM_JOBS",
    "FARM_PRODUCTS",
    "FARM_PRODUCT_NOTES",
    "FARM_SHIFT_TEXTS",
    "FARM_SHIFT_EVENTS",
    "SWEATY_TEXTS",
    "SWEATY_TEASES",
    "SWEAT_LABELS",
    "SWEAT_TEXTS",
    "MEAT_GRADE_LABELS",
    "HORSE_CUT",
    "EXTRA_CUTS",
    "SAUSAGE_CUTS",
    "BREWERY_STYLES",
    "BREWERY_TEXTS",
    "ASTRID_GROWTH",
    "FRESH_TIERS",
    "BREW_GRADE_LABELS",
    "BUTCHER_CUTS",
    "VENUE_TEXTS",
    "SMITH_TEXTS",
    "LOCATION_NOTES",
    "EXAMINE_TEXTS",
    "SOUL_HUNGER_TEXTS",
    "CONSORT_TEXTS",
    "EVENT_TEXTS",
    "CHEST_TEXTS",
    "SHOPKEEPER",
    "TITLES",
    "COMBO_TITLES",
    "RARITY_LABELS",
    "ITEM_SETS",
    "ITEMS",
]


def build_replicas() -> None:
    ensure_loaded()
    for record in PROTOTYPES.values():
        for worn in record["equipment"].values():
            template = ITEMS.get(worn["id"]) if worn else None
            if template is None or template["rarity"] != "epic":
                continue
            replica = dict(template)
            replica.update(name=f"{template['name']} (Replica)",
                           rarity="rare",
                           note=f"{template.get('note', '')} This is a "
                                "careful copy; the original stays with "
                                "its owner.")
            for stat in ("armor", "damage", "allure"):
                if replica.get(stat):
                    replica[stat] = max(1, round(replica[stat] * 0.8))
            ITEMS[f"{worn['id']}_replica"] = replica


build_replicas()

TEMPLATES = {"items": {key: dict(value) for key, value in ITEMS.items()},
             "enemies": {key: dict(value) for key, value in ENEMIES.items()}}


def resolve_names() -> None:
    for key, template in TEMPLATES["items"].items():
        ITEMS[key] = fill_data(template)
    for key, template in TEMPLATES["enemies"].items():
        ENEMIES[key] = fill_data(template)


resolve_names()
on_bind(resolve_names)
