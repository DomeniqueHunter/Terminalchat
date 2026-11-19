from ....town_buildings.counter import Offer, Special
from ....town_buildings.work.model import Job


KEY = "ember_cask"
TITLE = "The Ember Cask"
BLURB = ("Smoke, malt and warm honey. Everything in the casks was made by "
         "the women of the hall.")
OWNER = "Hjordis Valdisdottir"
PLACE = "🍺 The Ember Cask – Hjordis brews what the hall gives her."
CLOSED = "The Ember Cask is shut while you are in the dungeon."
CUT = 0.25
DAY_KEY = "ember_day"
COUNT_KEY = "ember_count"
HALL_LIMIT = 3
FEAST_FLAG = "brandholm_feast"

JOBS = (
    Job("brew", "Brewer's Hand", KEY, 4, 20, "vitality",
        "Roll casks, stir the mash and carry what is handed to you."),
)
SESSION_LINES = {
    "brew": [
        "You roll a cask across the warm malt-floor and stack it.",
        "Gunnar hands you a paddle. 'Stir slow. Smoke does the rest.'",
        "You skim the vat while Hjordis tastes it with a long spoon.",
        "You carry a tray of tankards to the hall, eyes politely lowered.",
    ],
}

# id: (label, price, heal share, buff, tier, pregnancy chance, text)
DRINKS = {
    "smoke_ale": ("Smoke Ale", 25, 0.3, "ember_smoke", "common", 0.0,
                  "The ale tastes of peat fire and warm bread. Your chest "
                  "feels broad and slow."),
    "hall_mead": ("Hall Mead", 30, 0.5, "", "common", 0.0,
                  "Honey, heather and a clean burn. The mead settles in "
                  "your stomach like a warm hand."),
    "ice_bock": ("Ice Bock", 35, 0.3, "ember_bock", "common", 0.0,
                 "The bock was frozen and thawed three times. It is dark, "
                 "strong, and hits like a shoulder."),
    "trampled_wine": ("Trampled Wine", 40, 0.2, "ember_wine", "common", 0.0,
                      "Berries trodden by bare giant feet, Hjordis says. "
                      "It is sweet, a little salty, and you feel "
                      "strangely looked at."),
    "sweat_stout": ("Sweat Stout", 35, 0.3, "ember_stout", "common", 0.0,
                    "Dark, thick, with a salty edge from the hall's "
                    "steam. You feel light on your feet."),
    "hall_gold": ("Hall Gold", 20, 0.25, "", "common", 0.0,
                  "A clear golden lager, lightly hopped. The young women "
                  "of the hall brew it for the guests, Hjordis says with "
                  "a perfectly straight face."),
    "young_cream": ("Young Cream", 45, 0.3, "ember_cream", "common", 0.0,
                    "Milk, honey and smoke salt, thick as custard. "
                    "Sweet, warm, and it smells of hay and summer skin."),
    "council_gold": ("Council Gold", 40, 0.4, "", "hall", 0.0,
                     "A deep amber lager with a smoky edge. 'The council "
                     "women's cask,' Hjordis says. 'Only a few a day.'"),
    "hall_cream": ("Hall Cream", 70, 0.4, "ember_cream_hall", "hall", 0.0,
                   "Smoke, salt, leather and warm wood. It coats your "
                   "tongue and warms you down to your toes."),
    "matriarch_cream": ("Matriarch's Cream", 90, 0.5, "ember_matriarch",
                        "hall", 0.03,
                        "Thick, rich, salty-sweet, and unmistakably "
                        "meant. The sign over the tap says: the only "
                        "drink in Brandholm that can get you pregnant."),
    "herrin_gold": ("Herrin's Gold", 80, 0.6, "", "feast", 0.0,
                    "Peat smoke, amber and cold snow on hot stone. The "
                    "whole hall goes quiet as you drink it."),
    "herrin_cream": ("Herrin's Cream", 150, 0.8, "ember_blessed", "feast",
                     0.06,
                     "Peat smoke, amber, musk and a cold edge like snow "
                     "on a hot stone. The hall rises and raises its "
                     "tankards. You are Blessed of the Hall."),
}
LABELS = {
    "common": "", "hall": " (limited, a few a day)",
    "feast": " (only at the feast)"}

SPECIAL = Special(
    KEY, TITLE, BLURB, "🍺", OWNER,
    "'Sit. Drink. Ask nothing about what is in the casks.'",
    (Offer("Work the casks (4 rounds, 25% cut)", "job", item="brew"),
     *(Offer(f"{label}{LABELS[tier]}", "drink", price=price, item=key,
             show_if=FEAST_FLAG if tier == "feast" else "")
       for key, (label, price, _, _, tier, _, _) in DRINKS.items())))

BREW_BUFFS = {
    "ember_smoke": {"label": "Smoke-warmed", "bonus": {"vitality": 1},
                    "text": ""},
    "ember_bock": {"label": "Bock-hardened", "bonus": {"strength": 1},
                   "text": ""},
    "ember_wine": {"label": "Trampled-wine glow", "bonus": {}, "allure": 2,
                   "text": ""},
    "ember_stout": {"label": "Sweat-stout lightness",
                    "bonus": {"agility": 1}, "text": ""},
    "ember_cream": {"label": "Cream-warmed", "bonus": {}, "allure": 1,
                    "text": ""},
    "ember_cream_hall": {"label": "Hall-cream glow",
                         "bonus": {"vitality": 1}, "allure": 1, "text": ""},
    "ember_matriarch": {"label": "Matriarch's blush",
                        "bonus": {"vitality": 1}, "allure": 2, "text": ""},
    "ember_blessed": {"label": "Blessed of the Hall",
                      "bonus": {"vitality": 1, "strength": 1}, "allure": 3,
                      "text": ""},
}

SOLD_OUT = ("Hjordis shakes her head. 'That is all the hall gave me for "
            "today. Come back tomorrow, small one.'")
NO_FEAST = "Hjordis smiles. 'That cask is not tapped. Not today.'"
PAID = "{name} pays {price} gold."
EXPECTING = ("The sign said so. {name} puts a hand on {their} belly and "
             "Hjordis raises a tankard. 'To the hall, small one. Welcome "
             "to the family.'")
