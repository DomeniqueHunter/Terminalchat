from ....town_buildings.counter import Offer, Special


KEY = "sole_hall"
TITLE = "The Sole Hall"
BLURB = ("A warm hall of pillows and heated footstools, where Ingibjorg "
         "receives and the men kneel. Sign for a day, or take a foot bath.")
OWNER = "Ingibjorg Skuladottir"
PLACE = "🦶 The Sole Hall – Ingibjorg receives, Torben kneels."
CLOSED = "The Sole Hall is shut while you are in the dungeon."
CUT = 0.0
STATE_KEY = "sole"
HOURS = 24
PAY = 300
FREE_PRICE = 150
MAX_SERVES = 6
SERVE_GOLD = (25, 45)
BATH_PRICE = 35
BATH_HEAL = 1.0
BLOCKED = ("lobby", "join", "start", "force")
GLOW = "sole_glow"
REST = "sole_rest"

SIGNED = [
    "Ingibjorg lifts one enormous bare foot and points at the floor. "
    "'Twenty-four hours, small one. You will wash, rub and kneel, and "
    "when the day ends you will be paid for it.' Torben hands you a "
    "cloth. The contract is signed in warm ink.",
    "Ingibjorg glances at you for a long moment, then nods. 'A day at my "
    "feet. Torben will show you where to kneel.' The door closes softly "
    "behind you.",
]
SERVE = [
    "You kneel before Ingibjorg's footstool and rub warm oil into her "
    "soles. Her toes curl, and she hums in approval.",
    "Torben shows you how to wash between the toes. Ingibjorg watches "
    "your face the whole time and smiles a little.",
    "You press your cheek to her instep as she asks. It is warm and "
    "smells of smoke and wool. Nobody speaks for a long time.",
]
SERVE_PAY = "💰 +{gold} gold (serve {count} of {limit})."
NOT_SIGNED = "You have no contract here. Sign one first."
LIMIT = "Ingibjorg shakes her head. 'Enough for today. Rest until it ends.'"
ALREADY = "You are already signed. {left} left."
FINISHED = ("The day ends. Ingibjorg lifts your chin with one toe. 'Well "
            "served.' Torben counts out {pay} gold, and you leave with a "
            "lasting glow.")
BOUGHT_OUT = ("You pay {price} gold and Ingibjorg tears the contract in "
              "half. 'A pity. Come again.'")
CANNOT_PAY = "A buy-out costs {price} gold. You do not have it."
BLOCK = ("You are under the Sole Hall contract ({left} left). Finish the "
         "day first.")
BATH = ("Torben sets a copper basin of warm water under your feet and "
        "washes them gently, while Ingibjorg watches from her throne. "
        "You feel rested down to your toes.")
IN_RUN = "Not while you are in the dungeon."

SPECIAL = Special(
    KEY, TITLE, BLURB, "🦶", OWNER,
    "'Kneel when you enter. The floor is warm for you.'",
    (Offer("Sign the Sole contract (24 h, serve up to 6 times)", "sign"),
     Offer("Serve Ingibjorg's feet (25-45 gold)", "serve"),
     Offer(f"Buy out the contract ({FREE_PRICE} gold)", "free"),
     Offer(f"Warm foot bath ({BATH_PRICE} gold, full heal)", "bath",
           price=BATH_PRICE)))
