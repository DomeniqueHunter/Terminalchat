KEY = "orphanage"
TITLE = "Orphanage"
BLURB = "Small hands, big appetites and a matron who never says no to help."
GOLD_PER_POINT = 20
KIND_POINTS = {"milk": 2, "cum": 2}
GIVE_POINTS = {"milk": 3, "cum": 3}
KIND_ITEMS = {"milk": "milk_bottle", "cum": "cum_flask"}
MIN_BUST = 150
MIN_ENDOWMENT = 8
MIN_BALLS = 3
LEVELS = (
    (150, "Patron of the Lantern"),
    (50, "Benefactor"),
    (10, "Friend of the House"),
)
BUFF_LEVEL = 2
BUFF = "orphanage_warm"
ORPHANAGE_BUFFS = {
    BUFF: {"label": "Warm Hearts", "bonus": {}, "allure": 2, "text": ""},
}
OFFER = ("Donate gold, food, milk or cream – [donate] shows how. "
         "[donate milk] or [donate cum] gives on the spot.")
HELP = ("The orphanage takes donations and gives reputation. "
        "!donate <bag nr> gives an item, !donate all food gives all food, "
        "!donate gold <amount> gives gold, !donate milk and !donate cum "
        "give on the spot (once per game day each).")
TEXTS = {
    "none": "Nothing in your bag fits that.",
    "closed": "The door is barred while you are down in the dungeon.",
    "gold_small": "The matron smiles kindly. 'Twenty gold at least, dear, "
                  "or the ledger will not notice.'",
    "gold": "The matron counts your {amount} gold twice and tucks it away. "
            "'The little ones will eat well.'",
    "food": "The matron takes your {item} with both hands. 'The little "
            "ones will be glad of this.'",
    "food_all": "A line of small hands carries off {count} things to eat. "
                "'Bless you,' says the matron.",
    "nofood": "You have nothing to eat in your bag.",
    "vial": "The matron takes the {item} carefully. 'Nobody will ask "
            "where it came from.'",
    "milk_no": "The nurse looks you over and shakes her head kindly. "
               "'Not enough there for the little ones, dear.'",
    "cum_no": "The matron glances at you, then politely at the wall. "
              "'I fear that will not do, dear.'",
    "wait": "'Come back tomorrow, dear,' says the nurse. 'You need rest "
            "first.'",
    "milk": "You are led to a quiet back room. A nurse shows you how it "
            "is done, patient and brisk. When you leave, a bottle stands "
            "full and warm on the table.",
    "cum": "A discreet side room, a clean glass, a heavy curtain. The "
           "matron does not look at you when you hand it over, only nods, "
           "grateful.",
    "level": "The matron presses your hand. 'You have a good heart, "
             "{title}. The house will remember it.'",
    "points": "Reputation: {points} ({title}).",
}
