from pathlib import Path


GAME_DATA_PATH = Path("game_data")
ACCOUNTS_DIR_NAME = "accounts"
ACCOUNT_DB_NAME = "accounts.db"
NPC_DIR_NAME = "npcs"
LOCAL_ACCOUNT_ID = "00000000-0000-0000-0000-000000000000"
# characters one account may own (int, set here)
MAX_CHARS_PER_ACCOUNT = 2
# a temporary admin loses the rights after this many seconds (and on every restart)
TEMP_ADMIN_SECONDS = 3600
SESSION_DAYS = 30
MIN_PASSWORD_LENGTH = 8
ACCOUNT_NAME_LENGTH = (3, 24)
GRAVEYARD_DIR_NAME = "graveyard"
ITEMS_DIR_NAME = "items"
TRAVEL_FARE_HUB = 30
TRAVEL_FARE_FAR = 60
TEMP_MONSTER_DIR_NAME = "temp_monster"
STORY_KINDS = ("resident", "figure")
LEADERBOARD_FILE_NAME = "leaderboard.json"
SHOPS_DIR_NAME = "shops"
SMITH_STOCK = {"weapons": 10, "armor": 6}
LOOT_STAT_BONUS = 0.25
TROPHY_CHANCE = 0.25
REMAINS_FILE_NAME = "remains.json"
BOUTIQUE_FILE_NAME = "boutique.json"
FARM_FILE_NAME = "farm.json"
SWEATERY_FILE_NAME = "sweatery.json"

COMMAND_PREFIX = "!"
SHOW_ACTION_HINTS = False  # True prints the "Actions: [..]" lines again
MAX_PARTY_SIZE = 4
ROUND_TIMEOUT_SECONDS = 40.0
# Shop-style stops that wait for the party instead of timing out after 40 s.
# Remove a kind from the tuple to give it the normal timer back.
PAUSED_EVENT_KINDS = ("hut", "butcher_shop", "farm", "brewery", "boutique",
                      "sweatery", "smokery", "couch", "bivouac", "citystop",
                      "mage_tower", "wardrobe", "throne", "glory_hole", "wedding", "fisher", "grill", "dairy", "privy", "pod_garden", "north_pole", "buster_maid", "adept", "wanderer", "ogre_feast",
                      "null_master", "caravaneer", "drainer")
# Safety net so a walked-away party can't block the bot forever (0 = never).
PAUSED_IDLE_SECONDS = 1800.0

STAT_NAMES = ("strength", "agility", "vitality", "intelligence")
STAT_ALIASES = {
    "str": "strength", "strength": "strength",
    "agi": "agility", "agility": "agility",
    "vit": "vitality", "vitality": "vitality",
    "int": "intelligence", "intelligence": "intelligence",
}
STAT_SHORT = {
    "strength": "STR", "agility": "AGI",
    "vitality": "VIT", "intelligence": "INT",
}

AFFINITY_NAMES = ("melee", "magic", "dodge", "guard", "heal")
AFFINITY_LABELS = {
    "melee": "Melee", "magic": "Magic", "dodge": "Dodge",
    "guard": "Guard", "heal": "Heal",
}

GENDERS = ("Male", "Female", "Transgender", "Herm", "Shemale",
           "Male-Herm", "Cunt-boy", "None")
DEFAULT_GENDER = "None"
BREEDING_CHANCE = {
    "Female": 0.8,
    "Herm": 0.5,
    "Shemale": 0.5,
    "Male": 0.0,
}
DEFAULT_BREEDING_CHANCE = 0.5
TRIBE_BREEDING_CHANCE = {
    "goblins": {**BREEDING_CHANCE, "Male": 0.05},
    "orcs": {**BREEDING_CHANCE, "Male": 0.10},
    "amazons": {
        "Female": 0.85,
        "Herm": 0.7,
        "Shemale": 0.7,
        "Transgender": 0.7,
        "Cunt-boy": 0.8,
        "Male-Herm": 0.5,
        "Male": 0.0,
    },
}
BREEDING_FALLBACK_FATE = "roasted"
PRONOUNS = {
    "Male": ("he", "him", "his"),
    "Female": ("she", "her", "her"),
    "Transgender": ("she", "her", "her"),
    "Herm": ("she", "her", "her"),
    "Shemale": ("she", "her", "her"),
    "Male-Herm": ("he", "him", "his"),
    "Cunt-boy": ("he", "him", "his"),
    "None": ("they", "them", "their"),
}

START_STAT_VALUE = 5
START_FREE_POINTS = 10
POINTS_PER_LEVEL = 3
INVENTORY_SIZE = 10
BACKPACK_BASE_PRICE = 80
BACKPACK_MAX_EXTRA = 30
BACKPACK_CHEAP_EXTRA = 10
BACKPACK_LUXURY_PRICE = 2000
BACKPACK_LUXURY_FACTOR = 1.5
BANK_SLOTS = 40
MIN_AGE = 18
MAX_AGE = 99
DEFAULT_AGE = 21
PERSONALITY_MAX = 80
FORM_TEXT_MAX = 500
CHAT_MAX_LENGTH = 300
PRIVATE_WHERE = ("brothel", "room")
CHAT_BURST = 5
CHAT_BURST_SECONDS = 10.0
FORM_NAME_MAX = 24
FLIST_PREFIX = "https://www.f-list.net/c/"
CREATE_GENDERS = tuple(g for g in GENDERS if g != "None")
BANK_FILE_NAME = "bank.json"
MAIL_FILE_NAME = "mail.json"
MAIL_DIR_NAME = "mail"
MAIL_READ_DAYS = 14
MAIL_TAKEN_DAYS = 7
MAIL_FEE = 10
MAIL_GOLD_FEE_PERCENT = 5
MAIL_ATTACH_DAYS = 90
MAIL_KEEP_DAYS = 60
MAIL_BOX_SIZE = 50
MAIL_PER_HOUR = 20
MAIL_SUBJECT_MAX = 60
MAIL_BODY_MAX = 1000
MAIL_NPC_REPLY_SECONDS = (60, 300)
SCHOOL_FILE_NAME = "school.json"
BROTHEL_VISIT_PRICE = 40
TAVERN_VISIT_PRICE = 20
WORK_TICK_SECONDS = 20.0
BROTHEL_CUT = 0.3
BROTHEL_KILL_CHANCE = 0.04
BROTHEL_KILL_ACTS = ("facesitting", "trampling")
BROTHEL_WIPE_FACTOR = 1.5       # pay factor for wiping a client's memory (foot)
BROTHEL_DOM_FINISH = 0.08       # chance a dominant client finishes you off (facesitting / foot)
BROTHEL_PURSE = (60, 400)
BROTHEL_HOUSE_GUEST_CHANCE = 0.08   # a resident of town drops in as a client
HOUSE_GUEST_BUILDINGS = ("brothel", "cafe", "tavern", "salon", "castle")
BROTHEL_BELLY_PER_BALL = 0.8
RENT_PRICES = {"classic": 60, "fetish": 110}
COURSE_PRICE = 150
COURSE_DAYS = 3
MAID_PRICE_FACTOR = 2
MAID_SEARCH_FEE = 20
VISIT_ROLL_SECONDS = 240
VISIT_START_CHANCE = 0.4
VISIT_STAY = (360, 900)
VISIT_GUEST_CHANCE = 0.5
NPC_ACTION_SECONDS = (90, 240)
MAID_SEARCH_MAX = 5
MAID_BUYBACK_PRICE = 300
EQUIPMENT_SLOTS = ("weapon", "head", "chest", "gloves", "feet",
                   "accessory", "lingerie", "crotch")
SLOT_LABELS = {
    "weapon": "Weapon", "head": "Head", "chest": "Chest", "gloves": "Gloves",
    "feet": "Feet", "accessory": "Accessory", "lingerie": "Lingerie",
    "crotch": "Crotch",
}
LEGACY_SLOTS = {"armor": "chest"}

ENEMY_SCALING = 1.08
BOSS_INTERVAL = 10
BIOME_SEGMENT = 4
DEBUG_BIOME_SEARCH = 200
BIOME_FAVOR_WEIGHT = 3
TOWN_BIOMES = {
    "last_light": ("Goblin Warrens",
                   ("The Crypt", "Orc Camp", "Orc Stronghold")),
    "mudgate": ("Goblin Warrens",
                ("Orc Camp", "Orc Stronghold", "Rotting Swamp")),
    "ironhold": ("Dripping Caves",
                 ("Ogre Mountain", "Giant's Larder", "Petrified Halls")),
    "cogsworth": ("Dripping Caves",
                  ("Living Walls", "Petrified Halls", "Orc Stronghold")),
    "dusk_hollow": ("Dripping Caves",
                    ("The Crypt", "Rotting Swamp", "Living Walls")),
    "brandholm": ("Dripping Caves",
                  ("Ogre Mountain", "Giant's Larder", "Orc Camp")),
}
CYCLE_LENGTH = 70
MAX_ENEMIES = 8
STRAY_CHANCE = 0.25
STRAY_MIN_STAGE = 3
STRAY_LOOKAHEAD = 30
STRAY_POWER = 1.3
CYCLE_BONUS = 4.0

CHEST_CHANCE = 0.25
CHEST_RARITY_BONUS = 15
MIMIC_BASE_CHANCE = 0.15
MIMIC_STAGE_CHANCE = 0.005
MIMIC_MAX_CHANCE = 0.40
INSPECT_BASE_CHANCE = 0.20
INSPECT_INT_CHANCE = 0.02
INSPECT_MAX_CHANCE = 0.85
STAGE_HP_REGEN = 0.10
STAGE_MANA_REGEN = 0.30
CURSE_ITEM_LOSS_CHANCE = 0.20

START_GOLD = 50
NPC_HIRE_PRICE = 40
NPC_HEAL_HP_RATIO = 0.5
NPC_GUARD_HP_RATIO = 0.25
STAGE_GOLD_BASE = 8
STAGE_GOLD_PER_STAGE = 3
MIMIC_GOLD_FACTOR = 3
SELL_RATIO = 0.4
SHOP_EQUIPMENT_STOCK = 5
SHOP_CONSUMABLES = ("potion_small", "mana_potion", "potion_large",
                    "bread_loaf", "water_flask", "wake_tonic",
                    "cooling_draught", "firewood")
NEEDS = ("hunger", "thirst", "sleep", "arousal")
NEED_RATES = {"hunger": 3, "thirst": 4, "sleep": 2, "arousal": 2}
NEED_LEVELS = (40, 70, 90)
NEED_PENALTIES = {
    "hunger": ("strength", (0, 1, 3, 6)),
    "thirst": ("intelligence", (0, 1, 3, 6)),
    "sleep": ("agility", (0, 1, 3, 6)),
    "arousal": ("intelligence", (0, 0, 2, 4)),
}
NEED_STARVE_DAMAGE = 0.10
NEED_REST_RELIEF = {"sleep": -100}
NEED_RELIEF_INDULGE = {"arousal": -50}
NEED_ITEM_EFFECTS = {
    "milk_bottle": {"thirst": -30, "hunger": -10},
    "cream_jar": {"hunger": -20, "thirst": -10},
    "farm_eggs": {"hunger": -20},
    "cum_flask": {"hunger": -10, "thirst": -20},
    "fish_pike": {"hunger": -25}, "fish_perch": {"hunger": -20},
    "fish_eel": {"hunger": -25}, "fish_goldcarp": {"hunger": -30},
    "fish_blindcat": {"hunger": -30}, "fish_moortrout": {"hunger": -25},
    "fish_sturgeon": {"hunger": -40}, "fish_siren": {"hunger": -30},
    "giant_catch": {"hunger": -60},
    "farm_bread": {"hunger": -30},
    "stew_jar": {"hunger": -30, "thirst": -10},
}
NEED_ITEM_PREFIXES = (
    ("cooked_", {"hunger": -35, "thirst": -5}),
    ("brew_", {"thirst": -30}),
)
RARITY_PRICES = {"common": 40, "rare": 150, "epic": 500, "cursed": 400,
                 "couture": 600, "legendary": 2500}
MAX_DISCOUNT = 0.15
ALLURE_DISCOUNT = 0.01
ALLURE_DISTRACT = 0.02
MAX_DISTRACT = 0.20
ALLURE_BREEDING = 0.02
MAX_ALLURE_BREEDING = 0.15
MAX_BREEDING_CHANCE = 0.95
DAIRY_TRIBES = ("goblins", "orcs", "ogres", "giants", "amazons")
DAIRY_CHANCE = {"Large": 0.10, "Huge": 0.20, "Massive": 0.30}
DAIRY_GEAR_BONUS = {"leather_collar": 0.10, "cow_bikini": 0.15}
MAX_DAIRY_CHANCE = 0.50

REMAINS_CHANCE = 0.30
REMAINS_LIMIT = 300
HOARD_TAKE_CHANCE = 0.6
WARDROBE_EAT_CHANCE = 0.6
THRONE_TAKE_CHANCE = 0.4
GLORY_RELIEF_CHANCE = 0.6
GLORY_BOON_CHANCE = 0.2
PASS_SNEAK_CHANCE = 0.4
STAKES_SHOWN = 6
PRAY_HEAL = 0.15
STEW_FATES = ("roasted",)
STEW_HEAL = 0.25
STEW_SPOIL_CHANCE = 0.15
STEW_SPOIL_DAMAGE = 0.10
STEW_ITEM = "stew_jar"
DAIRY_PRODUCTS = {"milk_bottle": 0.7, "cream_jar": 0.3}

EVENT_CHANCE = 0.20
BONUS_DROPS = {
    "hunter": ["pith_helmet", "hunting_blunderbuss", "safari_jacket"],
    "couture": ["couture_gown", "velvet_gloves", "designer_heels"],
    "recruiter": ["recruiter_cane", "prefect_badge", "maid_uniform"],
    "lich": ["frost_crown", "rime_gown", "soulfrost_scepter"],
    "butcher": ["butcher_cleaver", "butcher_apron"],
    "farmer": ["farmer_pitchfork", "straw_hat", "branding_iron"],
    "mrs_claus": ["claus_stockings", "candy_socks", "fur_mittens",
                  "jingle_belt", "bodice_scrap", "antler_headband"],
}
MRS_CLAUS_ESCORTS = {"reindeer": 2, "elf": 3}
WINTER_TRIBE = "winter"
POLE_SHOWN = 8
POLE_BOOT_GIFT_CHANCE = 0.4
POLE_SLOPPY_CHANCE = 0.25
HUT_REST_HEAL = 0.30
HUT_REST_RISK = 0.10
HUT_SLEEP_RISK = 0.35
HUT_SLEEP_AMBUSH_HEAL = 0.25
HUT_SEARCH_RISK = 0.15
HUT_COOK_RISK = 0.15
HUT_EAT_HEAL = 0.20
HUT_EAT_RISK = 0.20
HUT_EAT_RELIEF = {"hunger": -80, "thirst": -40}
HUT_SEARCH_GOLD = 30
HUT_SEARCH_GOLD_STEP = 6
HUT_STAGES = {"lodge": 15, "cabin": 35, "manor": 65}
LOCATION_EVERY = 4
LOCATION_MARK = "📌"
COMPANION_NAME = "Connie"
CITY_STOP_FIRST = 35
CITY_STOP_EVERY = 30
PASS_FEE = 150
PASS_BRIBE_COST = 60
PASS_BRIBE_CHANCE = 0.55
PASS_TALK_CHANCE = 0.35
PASS_TALK_STEP = 0.15
BREWERY_STOCK = ("brew_yogurt_drink", "brew_kefir", "brew_cream_lassi",
                 "brew_house_special")
LEGACY_ITEMS = {"brew_amber_ale": "brew_yogurt_drink",
                "brew_dark_stout": "brew_kefir",
                "brew_cream_stout": "brew_cream_lassi"}
BREW_TAP_FACTOR = 1.5
BREW_HEAL = 120
BREW_MANA = 40
BREW_PRICE = 70
BREW_SWEAT_BONUS = 1
BREWERY_BATCH_MAX = 6
BREWERY_CUM_MAX = 3
FISHER_ROD_PRICE = 30
FISHER_CAST_LIMIT = 3
FISHER_BOOT_CHANCE = 0.15
FISHER_BITE_CHANCE = 0.08
FISHER_BITE_HURT = 0.12
FISHER_FISH_ODDS = {"common": 0.70, "rare": 0.22, "epic": 0.08}
FISHER_BAIT_LOST = 0.50
FISHER_BAIT_CAUGHT = 0.45
GORM_TALL = 180
GORM_BUTT = 110
GORM_BALLS = 8
GORM_CONCEPTION_FACTOR = 2.5
GRILL_SPECIAL_PRICE = 250
DAIRY_JOBS = {
    "milk": {"pay": 12, "rounds": 4, "drain": 0, "buff": "dairy_fresh"},
    "feed": {"pay": 22, "rounds": 4, "drain": 12, "buff": "dairy_fresh"},
    "cow": {"pay": 55, "rounds": 5, "drain": 20, "buff": "dairy_stud"},
    "bull": {"pay": 55, "rounds": 5, "drain": 20, "buff": "dairy_stud"},
}
DAIRY_STAGE_PAY = 0.04
DAIRY_STAMINA_BASE = 60
DAIRY_STAMINA_PER_VIT = 3
DAIRY_STAMINA_SWING = (-4, 6)
DAIRY_PRODUCT_CHANCE = 0.4
PRIVY_TOLL = 5
PRIVY_TIP = 10
PRIVY_URINAL = 3
PRIVY_ATTEND_PAY = 12
PRIVY_FIXTURE_PAY = 45
PRIVY_FIXTURE_SAFE = 2
PRIVY_FIXTURE_CHANCE = 0.4
PRIVY_FATES = ("fixture",)
DAIRY_PRODUCT_JOB = {"milk": "dairy_milk", "feed": "dairy_cheese",
                     "cow": "dairy_cream", "bull": "dairy_tonic"}
DAIRY_CULL_AFTER = 3
DAIRY_CULL_CHANCE = 0.3
DAIRY_HEIR_CHANCE = 0.04
DAIRY_COW_AGE = (45, 52)
DAIRY_SHELF_NAMED = 4
DAIRY_LEVEL_STEP = 10
DAIRY_LEVEL_BONUS = 0.25
DAIRY_FATES = ("milked_dry", "bull_stud", "culled")
BUTT_BUSTER_DAMAGE = 3000
MAID_VIT_PER_LEVEL = 4
MAID_STR_PER_LEVEL = 2
MAID_HITS = 100
MAID_ROUND_HITS = 10
MAID_DEATH_PER_HIT = 0.01
MAID_GENDERS = ("Female", "Herm", "Shemale", "Transgender")
ASTRID_VISIT_CHANCE = 0.3
ASTRID_VISIT_TAKE = 2
ASTRID_VISIT_PRICE = 15
CUM_BREW_FACTOR = 2.0
CUM_BREW_EQUINE = 0.3
BREWERY_FRESH_PRICE = 100
BREWERY_OFFER_TIER = 2     # sweat level from which Astrid makes her offer
BREWERY_FRESH_LIMIT = 4    # fresh mugs per visit, for the whole party
# Talking to Astrid ('!shop' / '!talk') this many times in a row without
# buying anything makes her lose patience (0 = never).
BREWERY_TALK_LIMIT = 6
BREWERY_GEAR_TO_SHOP = True  # False: she keeps the piece for good instead
BREWERY_GEAR_MAX = 4       # pieces of left-behind gear shown at once
# Which worn piece she takes first (never the weapon). Her payment includes
# the shop price of that piece, so buying it back leaves the hero at the
# plain price.
BREWERY_GEAR_PRIORITY = ("feet", "head", "chest", "gloves", "accessory",
                         "lingerie", "crotch")
FRESH_STEP = 20
FRESH_HEAL = (40, 320, 140)     # lowest, highest, most likely
FRESH_MANA = (0, 120, 40)
BREWERY_SELF_FACTOR = 1.25
BREWERY_SWEAT_PRICE = 0.2
EXAMINE_LIST_MAX = 10
NULL_RIDDLE_COUNT = 3
NULL_EXP_BASE = 15
NULL_EXP_PER_STAGE = 6
NULL_RANSOM_PRICE = 400
GIG_TURNS = 3
GIG_KEEP_BASE = 0.018
GIG_KEEP_STEP = 0.018
GIG_STAGE_PAY = 0.05
BREWERY_HAIR_CHANCE = 0.25
TRIBE_NAMES = {
    "amazons": "the futa amazons", "nords": "the Northern Smokery",
    "brewers": "the Creamworth taproom", "constructs": "an animated construct",
    "designers": "the fashion world", "giants": "the giants",
    "goblins": "the goblin tribes", "hunters": "the big-game hunters",
    "lich": "the Lich Queen's court", "winter": "Mrs. Claus' sleigh",
    "monsters": "the dungeon's beasts",
    "ogres": "the ogres", "orcs": "the orc clans", "pigmen": "the pigmen",
    "undead": "the restless dead", "mages": "a well-meaning apprentice",
    "school": "Brunhild's maid school",
    "void": "the Null Master's silence",
}
VENUE_LIST_MAX = 12
MEAT_RAW_PRICE = 60
MEAT_RAW_HEAL = 30
MEAT_COOKED_HEAL = 160
MEAT_COOKED_MANA = 40
MEAT_LEVEL_STEP = 5
MEAT_VIT_STEP = 4
MEAT_BUILD_BONUS = {"Thin": -1, "Toned": 1, "Muscular": 2, "Curvy": 1,
                    "Chubby": 2, "Heavy": 3}
MEAT_GRADES = ((8, "epic", 2.5), (4, "rare", 1.6), (0, "common", 1.0))
MEAT_GRADE_ORDER = ("common", "rare", "epic")
MEAT_SWEAT_BONUS = 1
MEAT_KG_PER_CUT = 20       # one piece per 20 kg of body weight ...
MEAT_MAX_CUTS = 6          # ... up to this many (the sausage comes on top)
MEAT_STOCK_MAX = 12        # pieces hanging in the shop at once
MEAT_SAUSAGE_FACTOR = 1.5  # the extra sausage is worth more than a cut
MEAT_PRIME_FACTOR = 1.5    # breast, testicle and rump cuts are prime cuts
MEAT_PRIME_BUST = 150      # real bust (cc) from which breast fillets exist
MEAT_PRIME_BUTT = 105      # real butt (cm) from which a rump roast exists
MEAT_IMPLANT_PRICE = 25
MEAT_IMPLANT_STEP = 100    # extra price per this much implant size
MEAT_IMPLANT_PARTS = ("bust", "butt", "endowment", "balls")
SWEAT_GAIN = {"hit": 2, "dodge": 2, "guard": 2, "cast": 1, "use": 1}
SWEAT_BUILD_BONUS = {"Chubby": 1, "Heavy": 1}
SWEAT_MUSCLE_BONUS = {"leather": 2, "velvet": 1, "silk": 0}
SWEAT_TIGHT_SLOTS = ("lingerie", "crotch")
SWEAT_ARMOR_LIMIT = 5
SWEAT_MATERIAL_WORDS = ("leather", "wyrmhide", "wolfhide", "fur", "latex",
                        "rubber", "steel", "iron", "plate", "chain")
SWEAT_GEAR_MAX = 4
SWEAT_DODGE = 0.02
SWEAT_AGGRO = 0.5
SWEAT_CURED_TIER = 2
SCENT_PREFERENCES = {
    "orcs": ("Female", "Herm", "Cunt-boy"),
    "amazons": ("Male", "Herm", "Shemale", "Male-Herm", "Transgender"),
    "lich": ("Male", "Herm", "Shemale", "Male-Herm"),
    "gorgon": ("Male", "Male-Herm"),
}
SCENT_PREF_FACTOR = 2.0
SCENT_MUSCLE_LOVERS = ("couturiere",)
SWEAT_MUSK_TIER = 3
BOUTIQUE_SWEAT_PRICE = 0.15
ADEPT_SWEAT_ERROR = 0.05
ADEPT_BOOT_ERROR = 0.05
SCENT_FATES = {"orcs": "breeding", "amazons": "breeding", "ogres": "roasted",
               "giants": "eaten", "gorgon": "statue", "green_slime":
               "dissolved", "acid_ooze": "dissolved",
               "gelatinous_cube": "dissolved"}
SCENT_FATE_CHANCE = 0.08
SCENT_HUNTER_RISK = 0.05
SCENT_FARM_INTEREST = 0.01
SCENT_COUTURE_BONUS = 0.05
SWEATY_WANDERER_TIER = 2
SWEATY_WANDERER_CHANCE = 0.5
SWEATY_TIP_PER_TIER = 0.5
SWEATY_TASTES = (("Female", "Cunt-boy"), ("Male", "Male-Herm"),
                 ("Herm", "Shemale", "Transgender"))
SWEATY_TASTE_BONUS = 1.5
SWEAT_TIERS = ((45, 3), (25, 2), (10, 1))
ITEM_SMELL_STAGE_GAIN = 1
ITEM_SMELL_MAX = 60
SMELL_WORDS = ((40, "reeking of"), (20, "steeped in the scent of"),
               (8, "faintly scented by"))
FOREIGN_SMELL_TIERS = ((40, 3), (20, 2), (8, 1))
SWEAT_ALLURE = 1
RENT_JOBS = {"horse": "plough", "cow": "milk", "cumcow": "cum", "hen": "hen",
             "mule": "mule", "carriage": "carriage"}
FARM_SHIFT_TURNS = (3, 5)
FARM_SHIFT_PAY = {"plough": 25, "milk": 35, "cum": 35, "hen": 15,
                  "mule": 20, "carriage": 40}
FARM_SHIFT_STAGE_PAY = 0.05
FARM_SHIFT_GOLD = (10, 30)
FARM_SHIFT_HURT = 0.12
FARM_SHIFT_HEAL = 0.15
FARM_SHIFT_SWEAT = 6
FARM_SHIFT_ITEMS = {"plough": "farm_bread", "milk": "milk_bottle",
                    "cum": "cum_flask", "hen": "farm_eggs",
                    "mule": "farm_bread", "carriage": "farm_bread"}
CUM_YIELD_BY_BALLS = ((2, 0.5), (5, 1.0), (8, 2.0), (12, 3.0))
CUM_EQUINE_YIELD = 1.5
CUM_COW_MIN_BALLS = 8
BURDEN_MIN_BALLS = 8
BURDEN_BUILDS = ("Muscular", "Heavy", "Toned")
BURDEN_STAMINA_BASE = 8
BURDEN_STAMINA_VIT_STEP = 5
BURDEN_STAMINA_LOSS = {"plough": 2, "carriage": 3}
BURDEN_PAIN = 0.06
BURDEN_PAY = 1.25
BURDEN_REST = 2
CUM_COW_CHANCE = 0.5
FARM_KEEP_BASE = 0.02
FARM_KEEP_STEP = 0.015
FARM_KEEP_EVENT = 0.05
FARM_KEEP_MAX = 0.4
FARM_PRODUCT_FACTOR = {"kept": 1.8, "shift": 1.3}
FARM_PRODUCT_BUST = {"Large": 0.0, "Huge": 0.3, "Massive": 0.6}
FARM_PRODUCT_LEVEL_STEP = 10
FARM_PRODUCT_LEVEL_BONUS = 0.1
FARM_KEEP_JOB = {"plough": 1.2, "milk": 1.5, "cum": 1.5, "hen": 0.8,
                 "mule": 1.0, "carriage": 1.4}
FARM_STOCK = ("milk_bottle", "cream_jar", "farm_eggs", "farm_bread")
BUTCHER_BASIC_STOCK = ("meat_boar", "meat_boar_sausage")
COUCH_MIMIC_CHANCE = 0.5
COUCH_EAT_CHANCE = 0.6
COUCH_HEAL = 0.40
SOUL_HUNGER_CHANCE = 0.5
ENEMY_DISPLAY_MAX = 5
MAIDEN_CAPACITY = 3
MAIDEN_GROWTH = 0.2
BOUTIQUE_STOCK = 4
BOUTIQUE_MAIN_BASE = 3
BOUTIQUE_MAIN_STEP = 4
BOUTIQUE_MAIN_MAX = 10
BOUTIQUE_SECOND_BASE = 2
BOUTIQUE_SECOND_STEP = 8
BOUTIQUE_SECOND_MAX = 6
BOUTIQUE_ARMOR_FACTOR = 2
BOUTIQUE_ARMOR_STEP = 3
BOUTIQUE_DAMAGE_SLOTS = ("feet", "gloves")
BOUTIQUE_DAMAGE_BASE = 2
BOUTIQUE_DAMAGE_STEP = 6
BOUTIQUE_ALLURE_BONUS = 2
BOUTIQUE_PRICE_BASE = 1000
BOUTIQUE_PRICE_PER_LEVEL = 75
BOUTIQUE_HUNTED = {"bonus": (4, 9), "armor": 1.2, "damage": 2, "allure": 2,
                   "price": 1.3}
CLINIC_PRICES = {"build": 300, "remove": 150, "shape": 400,
                 "terminate": 500}
CLINIC_MAGIC_FACTOR = 3
CLINIC_MAGIC_BASE_CHANCE = 0.9
CLINIC_MAGIC_CHANCE_DROP = 0.1
CLINIC_MAGIC_MIN_CHANCE = 0.35
VELOURS_GROWTH = 0.04
VELOURS_GROWTH_MAX = 1.5
VELOURS_PHYSIQUE = ((25, "ripped"), (10, "toned"), (3, "fit"))
VELOURS_STAGE_STEP = 5
VELOURS_SWEAT = ((45, "sweat_dripping"), (25, "sweat_glistening"),
                 (10, "sweat_sheen"))
COLLECTION_SIZE = 4
COLLECTION_OWN_PIECES = 2
BOUTIQUE_SELF_BASE = 150
BOUTIQUE_SELF_PER_LEVEL = 40
BOUTIQUE_MATERIALS = {
    "leather": {"label": "Leather", "armor": 1.5, "allure": -1,
                "note": "tough leather"},
    "velvet": {"label": "Velvet", "armor": 1.0, "allure": 1,
               "note": "plush velvet"},
    "silk": {"label": "Silk", "armor": 0.5, "allure": 3,
             "note": "sheer silk"},
    "stallion": {"label": "Stallion Leather", "armor": 1.7, "allure": 0,
                 "note": "thick stallion leather"},
    "wolfhide": {"label": "Wolfhide", "armor": 1.3, "allure": 1,
                 "note": "shaggy wolfhide"},
    "wyrmhide": {"label": "Wyrmhide", "armor": 1.8, "allure": 0,
                 "note": "scaled wyrmhide"},
}
SHAPE_MATERIALS = {"Equine": "stallion", "Canine": "wolfhide",
                   "Draconic": "wyrmhide"}
CODPIECE_CHANCE = 0.6
CODPIECE_MIN_CM = 30
CODPIECE_CM_STEP = 10
CODPIECE_PREFIX = {"Equine": "Stallion", "Canine": "Wolf",
                   "Draconic": "Dragon", "Human": "Grand"}
MEAT_EQUINE_BONUS = 1
FARM_STALLION_PAY = 1.3
FARM_STALLION_PRODUCT = 0.2
LICH_TRIBE = "lich"
LICH_CONSORT_GENDERS = ("Male", "Herm", "Shemale", "Male-Herm")
LICH_MAX_ESCORTS = 2
CONSORT_CHANCE = 0.10
CONSORT_MIN_STAGE = 20
ADEPT_STATUE_CHANCE = 0.10
ADEPT_GALLERY_SIZE = 6
SKELETON_FATES = ("eaten", "roasted", "dissolved")
SKELETON_CHANCE = 0.08
TEMP_MONSTER_CHANCE = 0.2
TEMP_MONSTER_MIN_STAGE = 2
TEMP_MONSTER_TEMPLATES = {"ogre": "ogre", "goblin": "goblin",
                         "orc": "orc", "giant": "hill_giant",
                         "human": "orc"}
SKELETON_CRYPT_CHANCE = 0.35
SKELETON_CRYPT = "The Crypt"
SKELETON_MIN_STAGE = 4
BONUS_GOLD_FACTOR = 2
OGRE_FATES = ("roasted", "eaten")
OGRE_EAT_HEAL = 0.30
OGRE_PREGNANCY_CHANCE = 0.05
OFFSPRING_HP = 5
GROWN_UP_RUNS = 20
SPECIES_OF_KIND = {"ogre": "ogre", "party": "human"}
OGRE_TALK_EXP = 6
CHARM_BASE = 0.30
CHARM_PER_ALLURE = 0.04
CHARM_MAX = 0.90
WANDERER_HEAL = 0.20
WANDERER_EXP = 4
WANDERER_GOLD_BASE = 15
WANDERER_GOLD_PER_STAGE = 2
WANDERER_THEFT_CHANCE = 0.20
WANDERER_THEFT_SHARE = 0.25
WANDERER_RARE_BONUS = 5
WANDERER_LOVE_REROLLS = 5
WANDERER_THANKS_EXP = 5
MILK_BUSTS = ("Large", "Huge", "Massive")
FUTA_GENDERS = ("Herm", "Shemale", "Male-Herm")
VINE_BIOME = "Vine Swamp"
VINE_GROUP_CHANCE = 0.5
VINE_FULL_SWEAT = 45
VINE_RISK_SWEAT = 0.30
VINE_SURE_SWEAT = 0.60
POD_SHOWN = 5
POD_SELL_FACTOR = 1.6
POD_FATES = ("podded",)
HUNG_GENDERS = ("Male", "Herm", "Shemale", "Male-Herm", "Transgender")
FLAT_GENDERS = ("Male", "Male-Herm", "Cunt-boy")
VAGINA_GENDERS = ("Female", "Herm", "Male-Herm", "Cunt-boy")
HUNG_TRAITS = ("endowment", "balls", "penis")
ENDOWMENT_BONUS_CM = {"clinic": 8, "adept": 15}
WANDERER_MILK_GOLD = 10
WANDERER_MILK_PER_STAGE = 3
WANDERER_NURSE_HEAL = 0.25
GIANT_SMALL_TROPHY_CHANCE = 0.8
HEAVY_ROAST_CHANCE = 0.7
BREEDING_BODY_BONUS = 0.10
LEADERBOARD_SIZE = 10


CAFE_CUT = 0.25
CAFE_SEAT_SESSIONS = 20
CAFE_DEATH_MARGIN = 6
CAFE_DEATH_CHANCE = 0.45
CAFE_ENGULF_BUTT = 140
CRUSH_BUTT = 160
CRUSH_WEIGHT = 100
CRUSH_CLICK = 0.3               # share of the round crush chance rolled per clench click
CRUSH_BASE = 0.05
CRUSH_STEP = 0.01
CRUSH_MAX = 0.25
CRUSH_VITALITY = 0.005
CRUSH_MIN = 0.02
AMBIENT_ACTION_CHANCE = 0.4
AMBIENT_DEATH_CHANCE = 0.12
CRUSH_YOUNG_AGE = 25
CRUSH_OLD_AGE = 41
CRUSH_YOUNG_FACTOR = 1.5
CRUSH_OLD_FACTOR = 0.75
CAFE_ENGULF_WEIGHT = 95
CAFE_ENGULF_CHANCE = 0.6
CAFE_ENGULF_WAIT = 2
CAFE_FATE_WEIGHTS = {"cushion": 55, "cake": 45}
CAFE_RESPAWN_DAYS = 1
REVIVE_PRICE = 500
MAX_LOBBIES = 10
LOBBY_OFFLINE_SECONDS = 300
WORLD_NEED_STAGES = 5
WORLD_HP_REGEN = 0.25
WORLD_MANA_REGEN = 0.50
WORLD_DAY_SECONDS = 3600
YEAR_DAYS = 365
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday")
WORLD_CATCHUP_DAYS = 3
DEATH_GOLD_LOSS = 0.25
KEPT_GEAR_KEY = "kept_gear"
CAFE_NPC_BUY_CHANCE = 0.5
CAFE_RANSOM_RISE = 2
CAFE_CLAIM_PRICE = 120
CAFE_GROWTH = {"smothered": (2, 1), "engulfed": (5, 2),
               "collapsed": (3, 1)}
CAFE_BERTHA_MAX = (260, 260)
CAFE_RANSOM_PRICE = 45
CAFE_HOLD_BONUS = 1.5
CAFE_RIDER_RELIEF = 35
CAFE_GUEST_WEIGHT = (70, 150)
CAFE_GUEST_BUTT = (105, 190)
CAFE_STOCK = 6
CAFE_TICKET = 15
CAFE_REACTION_SECONDS = 20
CAFE_ARRIVAL_SECONDS = 12
CAFE_RIDE_ROUNDS = 20
CAFE_PAT_CHANCE = 0.35
CAFE_PAT_PLEASED = 0.12
CAFE_PAT_MAX = 0.9
TRAIN_MAX = 10
TRAIN_CUT = 0.04
TRAIN_CUT_MAX = 0.4
TRAIN_MARGIN_EVERY = 3
INVITE_BASE = 0.4
INVITE_HAPPY = 0.06
CALL_HAPPY = 7
CALL_CHANCE = 0.08
HAPPY_DEFAULT = 5
HAPPY_MAX = 10
HAPPY_PAY = 0.04
HAPPY_WORDS = ("cold", "reserved", "content", "fond", "devoted")
PAT_PUNISH_MIDDLE = 0.25
PAT_PUNISH_AIR = 25
CAFE_BERTHA_CHANCE = 0.04
CAFE_BERTHA_WEIGHT = 165
CAFE_BERTHA_BUTT = 205
CAFE_CRUSH_WEIGHT = 100
CAFE_ENCOURAGE_PAY = 1.15
CAFE_SWALLOW_CHANCE = 0.2
CAFE_SWALLOW_RATIO = 0.7
REGULARS_DIR_NAME = "regulars"
REGULARS_CAP = 40
REGULARS_CHANCE = 0.35
REGULARS_CALL_CHANCE = 0.2
REGULAR_GENDER_WEIGHTS = {
    "cafe": {"Female": 80, "Herm": 8, "Shemale": 12},
    "brothel": {"Male": 45, "Female": 35, "Herm": 6, "Shemale": 5,
                "Male-Herm": 3, "Cunt-boy": 2},
}
REGULAR_BANNED_GENDERS = {"cafe": ("Cunt-boy",)}
REGULAR_BUST_RANGE = {"cafe": (150, 1200), "brothel": (50, 800)}
REGULAR_FLAT_BUST_RANGE = (0, 50)
REGULAR_SMELL_MAX = 10
DREAD_BUTT_DIV = 25
DREAD_WEIGHT_DIV = 30
DREAD_KILL_POINTS = 2
DREAD_RELIEF_DIV = 4
DREAD_TIERS = (7, 10, 13)
DREAD_ROUND_PENALTY = 2
DREAD_PAY_CUT = 0.08
DREAD_HESITATE_CHANCE = 0.2
DREAD_HESITATE_AIR = 10
SMELL_AIR_MUSK = 1.0
SMELL_AIR_SWEAT = 0.5
REGULAR_SMELL_START = (0, 6)
REGULAR_SMELL_WORDS = ("fresh", "faint", "noticeable", "strong", "heavy",
                       "overwhelming")
REGULAR_ENDOWMENT_RANGE = (9, 26)
CAFE_NPC_ACTION_CHANCE = 0.3
CAFE_NPC_CRUELTY = (0.5, 1.0, 1.7)
CAFE_NPC_CRUELTY_WEIGHTS = (30, 45, 25)
REGULARS_AUTO = False
MIN_NPC_AGE = 18
CAFE_AMBIENT_MIN = 6.0
CAFE_AMBIENT_MAX = 14.0
CAFE_PRESENT_SECONDS = 180.0
VISIT_ASK_VISITS = 3
CAFE_FAMILY_CHANCE = 0.12
CAFE_FAMILY_TIP = (6, 14)


SWEATERY_CYCLES = 5
SWEATERY_BOTTLE_LITERS = 0.3
SWEATERY_STAGE_PAY = 0.05
SWEATERY_MUSCLE_BONUS = {"leather": 0.3, "velvet": 0.15, "silk": 0.0}
SWEATERY_TIER_BONUS = 0.1
SWEATERY_HEAT_DAMAGE = 0.12
SWEATERY_ROAST_BASE = 0.04
SWEATERY_ROAST_STEP = 0.04
SWEATERY_SQUEAL_CHANCE = 0.25
SWEATERY_LABOUR_EXP = 10
SWEATERY_PRODUCT_TIER = 0.25
SWEATERY_ROAST_HEAL = 120
SWEATERY_OPERATORS = {
    "goblin": {"pay": 14, "roast": 1.0, "yield": 1.0},
    "gnome": {"pay": 11, "roast": 0.5, "yield": 1.25},
}
SWEATERY_STATIONS = {
    "run": {"liters": 0.5, "stat": "agility", "base": "mana_potion",
            "damage": 0.0, "roast": 0.0},
    "lift": {"liters": 0.6, "stat": "strength", "base": "potion_small",
             "damage": 0.0, "roast": 0.0},
    "heat": {"liters": 1.0, "stat": "", "base": "potion_large",
             "damage": 1.0, "roast": 1.0},
    "grill": {"liters": 1.4, "stat": "", "base": "potion_large",
              "damage": 1.4, "roast": 2.0},
    "labour": {"liters": 0.7, "stat": "", "base": "potion_small",
               "damage": 0.0, "roast": 0.0},
}
SWEATERY_FEATURE_LIMITS = {
    "breasts": (500, 1200), "muscle": (60, 100), "butt": (115, 140),
    "balls": (8, 12), "endowment": (25, 40),
}

SMOKERY_CYCLES = 5
SMOKERY_PAY = 80
SMOKERY_STAGE_PAY = 0.05
SMOKERY_SURVIVOR_BONUS = 2.0
SMOKERY_SURVIVE = 0.631        # per cycle: 0.631 ** 5 is about 10 %
SMOKERY_VIT_STEP = 0.004
SMOKERY_SURVIVE_MAX = 0.8
SMOKERY_RELEASE = 0.3
SMOKERY_GRADE_BONUS = 2
SMOKERY_SMOKED_FACTOR = 0.9
SMOKERY_VIT_GAIN = 2
SMOKERY_MAX_CURE = 5
SMOKERY_DEFAULT_CURE = 3
SMOKERY_CURE_STAGES = ((5, "dried", 1.1, 1.5), (3, "cured", 1.0, 1.0),
                       (1, "fresh", 0.8, 0.8))   # level, label, heal, price
MEAT_RAW_HUNGER = -10
MEAT_COOKED_HUNGER = -40
SMOKERY_HUNGER = {"fresh": -30, "cured": -40, "dried": -50}
CAMP_GATHER_CHANCE = 0.8
CAMP_GATHER_MAX = 2
CAMP_GATHER_HURT = 0.15
CAMP_GATHER_LOSS = 0.10
CAMP_LIGHT_BASE = 0.35
CAMP_LIGHT_STEP = 0.02
CAMP_LIGHT_MAX = 0.95
CAMP_REST_HEAL_FIRE = 0.6
CAMP_REST_HEAL_COLD = 0.2
CAMP_SLEEP_COLD = -40
CAMP_AMBUSH_FIRE = 0.05
CAMP_AMBUSH_COLD = 0.30
PARTY_PREGNANCY_CHANCE = 0.15
HOME_BIRTH_NIGHTS = 3
MPREG_FACTOR = 0.4
MPREG_BUILD_SCALE = {"Toned": 1.0, "Muscular": 1.0, "Heavy": 1.0,
                    "Curvy": 1.0, "Chubby": 1.0, "Average": 0.6,
                    "Slim": 0.4, "Thin": 0.4}
MPREG_DEFAULT_SCALE = 0.6
INTIMACY_BOND = 2
INTIMACY_RELIEF = {"arousal": -60}
INTIMACY_MIN_AGE = 18
INTIMACY_NPC_TIER = "friend"
COACH_PRICE = 150
COACH_LIMIT = 3
COACH_TIER_POINTS = 3
COACH_STATS = {"smith": "strength", "tavern": "vitality", "cafe": "vitality",
               "clinic": "intelligence", "bank": "intelligence",
               "brothel": "agility", "maidschool": "agility",
               "shop": "agility"}
GIFT_STEP = 40
GIFT_MAX = 3
BARTER_RATIO = 0.5
ROMANCE_POINTS = 8
HOUSE_TYPES = {
    "hut": ("Fixer-Upper Hut", 800, 1,
            "Leaky roof, one bed, a stove that mostly works."),
    "row": ("Row House", 2500, 2,
            "Narrow and tidy, squeezed between two neighbours."),
    "townhouse": ("Townhouse", 6000, 4,
                  "Three floors, a cellar and a proper kitchen."),
    "manor": ("Manor Tower", 15000, 6,
              "A tall stone tower with a library and a view of the "
              "corridor."),
}
HOUSE_TOWN_FACTOR = {"last_light": 1.0}
HOUSE_BEDS_PER_ROOM = 2
HOUSE_MATE_POINTS = 3
HOUSE_INVITE_POINTS = 8
HOME_SEAT_SITS = 3
HOME_SEAT_PAY = 25


PITY_YOUNG_AGE = 35
PITY_OLD_AGE = 55
PITY_BY_AGE = (0.5, 0.25, 0.0)
PITY_EASE_CHANCE = 0.5
PITY_AIR_LIMIT = 40
PITY_AIR = 12
HUNG_MIN_ENDOWMENT = 30
HUNG_AIR_DRAIN = 4
HUNG_PAY_BONUS = 0.15
KIN_HEAVY_BUTT = 120
KIN_HEAVY_WEIGHT = 100

SWALLOW_GROWTH = (2, 1)
SWALLOW_BELLY = 4
CAFE_LOCK = "cafe_lock"


HOUSE_OWNER_HOME = 0.7        # chance the host is at home on arrival
HOUSE_FAMILY_CHANCE = 0.5     # chance a spouse is at home (if married)
HOUSE_GUEST_CHANCE = 0.3      # chance another local is visiting too
HOUSE_ACTIONS = {
    "eat": {"hunger": -45, "thirst": -20},
    "sleep": {"sleep": -70},
    "rest": {"sleep": -25},
    "relax": {"sleep": -10, "arousal": -8},
    "bathe": {"sleep": -5},
}
RIDER_RAISE_AIR = 35           # air the seat regains when the rider raises
RIDER_RAISE_COOLDOWN = 25      # seconds between two raises
RIDER_RAISE_PAUSE = 10         # seconds the stool's next reaction is delayed
HOUSE_HOLD_ACTS = ("facesitting", "foot")
HOUSE_RELEASE_BASE = 0.3       # chance the host lets a pinned visitor go
HOUSE_RELEASE_STEP = 0.15      # added per further attempt
HOUSE_HOLD_SECONDS = (40, 90)  # how long a host keeps a visitor pinned
HOUSE_GUEST_IDLE = 600          # seconds until an idle NPC guest heads home
POD_SCAN_SECONDS = 30            # seconds between checks for pods in house gardens
HOUSE_PIN_SCAN = 2              # seconds between checks for pinned players
CONDITION_STEPS = 3             # sessions until a host warms to a body
SLEEP_VOTE_SECONDS = 120        # how long a group sleep request stays open
HOUSE_SCENE_PULSE = 10          # seconds between registered scene actions
HOUSE_AIR_DRAIN = 25            # breath lost per pulse at the reference weight
HOUSE_AIR_REF_KG = 80           # partner weight that drains exactly HOUSE_AIR_DRAIN
HOUSE_AIR_FACTOR = (0.5, 2.5)   # lowest and highest weight factor
HOUSE_KO_SECONDS = 180          # how long a smothered sub stays out cold
SOLE_AIR_SHARE = 0.5            # share of the facesitting air drain a foot causes
SOLE_SWEAT_TIERS = (25, 50, 75)  # foot sweat values where the smell steps up
SOLE_SWEAT_START = 15           # starting foot sweat per sweat tier of the giver
SOLE_DIZZY = (0, 0, 5, 10)      # extra air drain per smell tier
SOLE_GAG = (0, 0, 8, 15)        # extra air drain when an ordered lick is obeyed
HOUSE_CRUSH_KO = 3              # a crushed sub stays out cold this many times longer (never deadly at home)
SEX_HEAT_MAX = 10               # arousal per session, a full bar comes
SEX_CONTENT_MAX = 20            # contentment per pair, never below 0
HOUSE_AUTO_BEATS = 6            # beats before an autopilot dom may end the scene
HOUSE_AUTO_END = 0.3            # chance per beat after that
HOUSE_CONSENT_SECONDS = 1800    # how long a hero's yes to intimacy holds
HOUSE_HOLD_PULSE = 10          # seconds between updates while pinned
VORE_CHANCE = 0.2            # per house sex session with a vore-minded host

ITEM_GENDER_CLASSES = {
    "gent": ("Male", "Male-Herm", "Herm", "Cunt-boy", "Transgender", "None"),
    "lady": ("Female", "Shemale", "Herm", "Transgender", "None"),
}
ITEM_STAT_KEYS = ("damage", "armor", "allure", "bonus", "mana", "heal",
                  "soul_hunger")
ITEM_UNIQUE_SLOTS_EXCLUDED = ("consumable",)

CLOSE_UNAUTHORIZED = 4401

TUNING_PRICE = 300
TUNING_DAY_KEY = "tuning_day"
