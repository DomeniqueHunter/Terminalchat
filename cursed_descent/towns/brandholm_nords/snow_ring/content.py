from ....town_buildings.counter import Offer, Special
from ....town_buildings.work.model import Job


KEY = "snow_ring"
TITLE = "The Snow Ring"
BLURB = "A round sand ring under open sky, benches of packed snow and loud giantesses."
OWNER = "Ulfhild Sigurdsdottir"
PLACE = "🥊 The Snow Ring – Ulfhild referees, Sven sweeps the sand."
CLOSED = "The Snow Ring is shut while you are in the dungeon."
CUT = 0.25
BET = 50
BET_CHANCE = 0.45
FIGHT_FEE = 20
FIGHT_PAY = 80
FIGHT_BASE = 0.30
FIGHT_PER_STRENGTH = 0.03
FIGHT_MAX = 0.80
FIGHT_LOSS = 0.30
JOBS = (
    Job("sand", "Ring Hand", KEY, 4, 20, "strength",
        "Rake the sand, carry the fallen and patch the winners."),
)
SESSION_LINES = {
    "sand": [
        "You rake the sand smooth between bouts.",
        "Sven passes you a bucket. 'Water for the loser, water for "
        "the winner.'",
        "You carry a fallen fighter off the sand, politely.",
        "You pour fresh sand where the last bout left a crater.",
    ],
}
BET_WIN = ("The giantess in the red corner flattens her rival and the "
           "benches roar. {name} collects {pay} gold.")
BET_LOSE = ("The red corner goes down in a cloud of sand. {price} gold "
            "lost, and Sven shrugs sympathetically.")
FIGHT_WIN = ("You step into the ring and Ulfhild blows her bone whistle. "
             "You hit, you duck, you stand. The crowd roars when your "
             "opponent hits the sand. Ulfhild raises your arm. {pay} "
             "gold, and a bandage from Sven.")
FIGHT_LOSE = ("You step into the ring and Ulfhild blows her bone whistle. "
              "The sand comes up very fast. Sven drags you out by the "
              "arms. 'Next time,' he says kindly. ❤ −{loss} HP.")

SPECIAL = Special(
    KEY, TITLE, BLURB, "🥊", OWNER,
    "'Two in, one standing. Place your coin!'",
    (Offer("Work the sand (4 rounds, 25% cut)", "job", item="sand"),
     Offer("Bet on the red corner", "bet", price=BET),
     Offer("Step into the ring yourself", "fight", price=FIGHT_FEE)))
