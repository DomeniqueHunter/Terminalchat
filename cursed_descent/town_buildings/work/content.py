from .. import registry
from ..registry import Layered


OWNERS = {}

PLACES = {}

INCIDENT_CHANCE = 0.2
INCIDENTS = (
    ("A rich patron presses a purse into your hand and winks.", 25),
    ("The bard writes a verse about you and passes the hat.", 15),
    ("A tipsy noblewoman insists you take her ring as a tip – it's "
     "paste, but the pawnbroker gives you something.", 10),
    ("A guard captain pays your whole table 'for peace and quiet'.", 20),
    ("An old regular remembers your name and tips like a king.", 18),
)

SESSION_LINES = {
    "waiter": ["A regular slides a coin under his mug 'for the smile'.",
               "You balance a tower of plates and a toddler's dare.",
               "You weave between tables with six mugs and no spills.",
               "A drunk grabs your sleeve; you smile and keep walking.",
               "You carry a roast through a brawl without losing a bite.",
               "Somebody sings badly. You tip the singer into a bench."],
    "milk": ["A tourist asks for a photograph; you charge for it.",
             "The barrel hums a little tune. Maybe that's you.",
             "You are hooked up to the barrel and the barrel is very "
             "pleased.", "The barrel fills while a crowd cheers the gauge.",
             "A cheerful tap is opened – the room toasts you.",
             "You drift off while the barrel gurgles contentedly."],
    "dancer": ["A drunk baron throws a coin and misses; the coin rolls "
               "back to you anyway.",
               "You dance the lantern dance and the whole room claps "
               "along.",
               "You take the little stage and the room goes quiet.",
               "Coins ring on the boards as you spin.",
               "A slow number; every eye follows your hips.",
               "You finish on a bow and a roaring cheer."],
}

SESSION_LINES.update(registry.session_lines())

MILK_OUTPUT = {"hung": "cum", "other": "milk", "both": "milk and cum"}

CLOSED = {}


OWNERS = Layered(OWNERS, "owner")
PLACES = Layered(PLACES, "place")
CLOSED = Layered(CLOSED, "closed")
