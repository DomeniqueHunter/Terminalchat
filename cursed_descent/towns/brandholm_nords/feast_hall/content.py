from ....town_buildings.counter import Offer, Special
from ....town_buildings.work.model import Job


KEY = "feast_hall"
TITLE = "The Feast Hall"
BLURB = ("A long hall of tables, a great fire and a painted wheel beside "
         "the spit. Join the feast to open the casks of the Herrin and "
         "the wheel.")
OWNER = "Gunhild Arnsdottir"
PLACE = "🍖 The Feast Hall – Gunhild feeds the hall, Thorgrim turns the spit."
CLOSED = "The Feast Hall is shut while you are in the dungeon."
CUT = 0.25
FEAST_FLAG = "brandholm_feast"
FEAST_DAY = "brandholm_feast_day"
FEAST_PRICE = 60
SPIT_RISK = 0.35
SPIT_PAY = 300
MERCY_PAY = 100
WHEEL = (("spit", 0.6), ("mercy", 0.4))

JOBS = (
    Job("feast", "Feast Hand", KEY, 4, 22, "vitality",
        "Carry trays, turn the spit and clear the tables."),
)
SESSION_LINES = {
    "feast": [
        "You carry a platter of smoked meat to the long table.",
        "Thorgrim lets you turn the spit for a while. 'Slow. Even.'",
        "You pour mead into tankards the size of buckets.",
        "You sweep the rushes under the benches.",
    ],
}
JOIN = ("Gunhild bellows your name and the hall cheers. You are seated "
        "between two giantesses at the long table, fed until you cannot "
        "move, and the casks of the Herrin are opened for the night. "
        "Everyone is looking at you with a very warm interest.")
NO_FEAST = "Gunhild shakes her head. 'Join the feast first, small one.'"
WHEEL_INTRO = ("The painted wheel is rolled to the middle of the hall. "
               "The drum starts, slow and heavy. Gunhild spins it. It "
               "clicks past spit, mercy, spit, spit... and slows to a "
               "stop on {pick}.")
SPIT = ("The hall roars. Two women step forward and lift you onto the "
        "spit between them, slowly, warmly, with a great deal of "
        "ceremony.")
SURVIVED = ("Hours later you are lifted down, limp, glowing and very "
            "much alive. The hall applauds and Gunhild counts out "
            "{pay} gold. 'Roast and returned!'")
MERCY = ("The wheel rests on mercy. The hall sighs, a little "
         "disappointed, and Gunhild hands you a tankard and {pay} gold. "
         "'The wheel is kind tonight.'")

SPECIAL = Special(
    KEY, TITLE, BLURB, "🍖", OWNER,
    "'Sit, eat, drink. The wheel is for later.'",
    (Offer("Work the feast (4 rounds, 25% cut)", "job", item="feast"),
     Offer("Join the feast (opens the Herrin's casks for today)", "join",
           price=FEAST_PRICE),
     Offer("Spin the wheel (spit or mercy, risky)", "wheel",
           show_if=FEAST_FLAG)))
