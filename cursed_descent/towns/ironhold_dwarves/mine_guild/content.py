from ....town_buildings.counter import Offer, Special
from ....town_buildings.work.model import Job


KEY = "mine_guild"
TITLE = "Mine Guild"
BLURB = "Haul ore through the deep shafts for coin."
OWNER = "Foreman Ulgrim"
PLACE = "⛏ The Mine Guild – Foreman Ulgrim pays by the ton."
CLOSED = "The Mine Guild is shut while you are in the dungeon."
CUT = 0.25
HURT_ROUND = 0.12
HURT_SHARE = 0.08

JOBS = (
    Job("haul", "Ore Hauler", KEY, 5, 20, "strength",
        "Drag ore carts through the shaft. The ceiling bites."),
)
SESSION_LINES = {
    "haul": [
        "You drag a cart of ore up the shaft, boots sliding on wet stone.",
        "A lamp flickers. You shove the cart on in the dark.",
        "Pick, shovel, cart – the foreman counts the tons out loud.",
        "You wedge a prop under a sagging beam and keep hauling.",
        "Dust in your teeth, a coin in your pocket. Another cart.",
    ],
}
SPECIAL = Special(
    KEY, TITLE, "Take a contract in the deep shafts for coin.", "⛏", OWNER,
    "'The shaft pays by the ton. Mind the ceiling.'",
    (Offer("Haul ore (5 rounds, 25% to the guild)", "job", item="haul"),))
