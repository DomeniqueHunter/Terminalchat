from ....town_buildings.counter import Offer, Special
from ....town_buildings.work.model import Job


KEY = "steam_hall"
TITLE = "The Steam Hall"
BLURB = ("Hot stone, wet linen and a long bench of women who sweat for the "
         "town. A tube leads from every chamber to a mask on the wall.")
OWNER = "Ragnhild Eldsdottir"
PLACE = "♨ The Steam Hall – Ragnhild sweats, Ketil buckles the masks."
CLOSED = "The Steam Hall is shut while you are in the dungeon."
CUT = 0.25
FEAST_FLAG = "brandholm_feast"
SIT_PAY = 40
SIT_COST = 0.25

JOBS = (
    Job("steam", "Steam Hand", KEY, 4, 22, "vitality",
        "Wipe benches, fetch water and keep the stones hot."),
)
SESSION_LINES = {
    "steam": [
        "You ladle water over the stones and the hall hisses.",
        "You wipe a bench while a woman watches from above.",
        "Ketil hands you a brush. 'Tubes. All of them.'",
        "You carry a bucket of cold water past a very warm giantess.",
    ],
}

# id: (label, price, death risk, heal share, buff, text)
CHAMBERS = {
    "young": ("Mask – young women's chamber", 15, 0.03, 0.3, "steam_young",
              "Ketil buckles the mask over your nose and mouth. The air "
              "that comes through the tube is sweet, warm and faintly "
              "like hay and milk. A young woman breathes hard on the other "
              "side of the wall, and every breath is yours."),
    "hall": ("Mask – hall women's chamber", 30, 0.12, 0.45, "steam_hall",
             "The mask clamps down. The air through the tube is heavy "
             "with smoke, salt and leather. Behind the wall a council "
             "woman shifts on the bench, and her scent seeps into every "
             "breath, deeper than you expected."),
    "herrin": ("Mask – Herrin's chamber", 60, 0.30, 0.7, "steam_herrin",
               "Ketil does not speak as he straps you in. The air is "
               "peat smoke, amber and musk with a cold edge, like snow on "
               "a hot stone. The whole hall holds its breath."),
}
SIT = ("You take the hot bench yourself. Ragnhild watches while the "
       "steam draws the sweat out of you and a bottle fills beside you. "
       "'Good sweat,' she says. You get {pay} gold and a sheen that "
       "lingers.")
SURVIVED = "Ketil unbuckles you, towels your face and steadies you. 'Breathe.'"
NO_FEAST = "Ragnhild shakes her head. 'That chamber is only lit at the feast.'"

SPECIAL = Special(
    KEY, TITLE, BLURB, "♨", OWNER,
    "'Breathe slowly, small one. It is easier that way.'",
    (Offer("Work the stones (4 rounds, 25% cut)", "job", item="steam"),
     *(Offer(label, "mask", price=price, item=key,
             show_if=FEAST_FLAG if key == "herrin" else "")
       for key, (label, price, *_rest) in CHAMBERS.items()),
     Offer(f"Sit in a chamber yourself (+{SIT_PAY} gold, costs 25% HP)",
           "sit")))
