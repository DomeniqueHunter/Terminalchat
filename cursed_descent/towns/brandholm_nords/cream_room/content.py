from ....town_buildings.counter import Offer, Special
from ....town_buildings.work.model import Job


KEY = "cream_room"
TITLE = "The Cream Room"
BLURB = ("Copper basins, glass jars and a long warm counter. The women of "
         "the hall give here, and the men take a fill and ask for a "
         "blessing.")
OWNER = "Gudlaug Hrafnsdottir"
PLACE = "🥛 The Cream Room – Gudlaug mixes, Eyvind carries the jars."
CLOSED = "The Cream Room is shut while you are in the dungeon."
CUT = 0.25
FILL_KEY = "fill"
FULL_FLAG = "brandholm_full"
BLESS_KEY = "blessing"
FILL_PRICE = 30
FILL_MAX = 4
FULL_AT = 3
HOURS = 24
FEE = 200
BLESS_CHANCE = 0.35
BLOCKED = ("lobby", "join", "start", "force")

JOBS = (
    Job("cream", "Cream Hand", KEY, 4, 20, "intelligence",
        "Fill jars, wipe benches and carry trays."),
)
SESSION_LINES = {
    "cream": [
        "You label jars in Eyvind's careful hand.",
        "You carry a tray of warm jars to the Hall.",
        "You scrub a copper basin until it shines.",
        "Gudlaug hands you a spoon. 'Taste. Tell me if it is ready.'",
    ],
}
FILL = [
    "Gudlaug pours a warm, thick measure of cream into a horn cup and "
    "watches you drink it. 'All of it,' she says. It is sweet, heavy "
    "and a little salty, and it settles in you like a stone.",
    "Eyvind passes you the cup without meeting your eyes. The cream is "
    "thick as custard and warm as skin. Your belly feels round and "
    "very full.",
]
FULL_TEXT = ("You are full now. Properly full. Gudlaug looks at your "
             "belly with open approval. 'Ask the Matriarch,' she says. "
             "'A full belly is a blessing.'")
NOT_FULL = "Gudlaug shakes her head. 'You are not full enough. Take another fill.'"
ALREADY = "The blessing still holds you. {left} left."
SIGNED = ("You kneel before Sigrunn Brandsdottir's footstool and ask. She "
          "looks down for a long time, then nods. 'A day at my feet, "
          "small one. Then you pay the hall for the honour.' The Hall "
          "holds its breath, and you are blessed.")
BABY = ("Something warm settles in you. Gudlaug raises a jar. 'To the "
        "hall, small one. Welcome to the family.'")
FINISHED = ("The day ends. Sigrunn lifts your chin with one toe. 'The "
            "hall thanks you.' Gudlaug takes {fee} gold for the honour, "
            "and you leave with a glow that does not fade.")
BLOCK = ("You are at the Matriarch's feet ({left} left). Finish the day "
         "first.")
IN_RUN = "Not while you are in the dungeon."

SPECIAL = Special(
    KEY, TITLE, BLURB, "🥛", OWNER,
    "'Take a fill. Take two. Come back tomorrow, lighter.'",
    (Offer("Work the jars (4 rounds, 25% cut)", "job", item="cream"),
     Offer("Take a fill (the cream of the hall)", "fill", price=FILL_PRICE),
     Offer(f"Ask the Matriarch's blessing (24 h at her feet, {FEE} gold "
           "at the end)", "bless", show_if=FULL_FLAG)))
