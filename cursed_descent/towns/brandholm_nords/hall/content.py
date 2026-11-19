from ....town_buildings.counter import Offer, Special


KEY = "hall"
TITLE = "The Council Hall"
BLURB = ("The long hall of the Matriarch, where the town is ruled by the "
         "women who carry the most weight.")
GREETING = ("A hall of black timber, warm as a bakery, with a throne at "
            "the far end that is far too big for any normal person. "
            "Sigrunn Brandsdottir looks down from it, 3.3 metres of "
            "grey braids, fur and calm, her bare feet on a bearskin. "
            "'Sit. You are standing in my smoke.'")
OWNER = "Sigrunn Brandsdottir"
PLACE = "🔥 The Council Hall – Sigrunn rules from the throne."
CLOSED = "The Hall is closed to petitioners while you are in the dungeon."
FAVOUR_BUFF = "hall_favour"
FAVOUR_PRICE = 300

AUDIENCE_BASE = [
    "Sigrunn looks down at you for a long moment. 'Speak, small one. "
    "Or do not. I enjoy both.'",
    "Sigrunn shifts her bare feet on the bearskin. 'Brandholm is "
    "simple. The women lead, the men carry, and guests keep their "
    "boots at the door.'",
    "'You may sit,' says Sigrunn, and points with one toe at a bench "
    "that was built for someone much taller than you.",
]
AUDIENCE_FLAGS = (
    ("brandholm_feast",
     "'You were at my table today,' says Sigrunn. 'Good. A fed guest is "
     "a quiet guest.'"),
    ("brandholm_full",
     "Sigrunn glances at your belly and nods. 'Gudlaug has been "
     "generous. Come and ask me while it still shows.'"),
    ("blessing",
     "'You kneel at my feet today,' says Sigrunn. 'Finish what you "
     "began.'"),
    ("sole",
     "Sigrunn wiggles her toes. 'I hear the Sole Hall has you. They "
     "always do.'"),
)

BOOK = [
    "📖 The Town Book of Brandholm",
    "Rule 1: Boots stay at the door. Everyone is equal under the soles.",
    "Rule 2: The women lead. The men carry. Both are honoured.",
    "Rule 3: A guest who is fed is a guest who stays.",
    "🍺 Ember Cask – strong drinks, three to a day.",
    "♨ Steam Hall – masks and sweat. 🦶 Sole Hall – a day of service.",
    "🥩 Smokehouse – short smoke or the wheel. ❄ Snow Ring – bets and fights.",
    "🥛 Cream Room – fill up, then ask the Matriarch for her blessing.",
    "🧺 Carrying House – ride, rest or be carried for hire.",
    "🍖 Feast Hall – one feast a day. Come hungry.",
]

FAVOUR = [
    "You kneel on the bearskin and name your petition. Sigrunn listens "
    "with her chin on her fist, then lifts one foot. 'Kiss the sole and "
    "pay the hall,' she says. You do both. 'The Council has your name. "
    "Walk with my favour.'",
]
HAS_FAVOUR = ("Sigrunn waves you off with one toe. 'You carry my favour "
              "already. Do not be greedy.'")

SPECIAL = Special(
    KEY, TITLE, BLURB, "🔥", OWNER,
    "'Sit. You are standing in my smoke.'",
    (Offer("Ask for an audience", "audience"),
     Offer("Read the Town Book", "book"),
     Offer("Petition the Matriarch (favour until death)", "favour",
           price=FAVOUR_PRICE)))
