from ....town_buildings.counter import Offer, Special


KEY = "arena"
TITLE = "Arena"
BLURB = "Bet on the pit fights – or cheer on your own luck."
BET_WIN_CHANCE = 0.45
SPECIAL = Special(
    KEY, TITLE, BLURB, "🥊", "Bruiser Grakka",
    "'Two enter, one gets carried out. Place your bets!'",
    (Offer("Bet 100 gold on the red corner", "bet", price=100),))
