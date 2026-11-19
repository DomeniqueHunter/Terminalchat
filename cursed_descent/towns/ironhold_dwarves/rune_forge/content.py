from ....town_buildings.counter import Offer, Special
from ....town_buildings.work.model import Job


KEY = "rune_forge"
TITLE = "Rune Forge"
BLURB = "Dwarven runes cut into rings and charms."
OWNER = "Rurik Runecarver"
PLACE = ("🔥 The Rune Forge – Rurik Runecarver counts every rune twice.")
CLOSED = "The Rune Forge is cold while you are in the dungeon."
CUT = 0.2

JOBS = (
    Job("carve", "Rune Carver", KEY, 4, 24, "intelligence",
        "Cut runes into rings and charms."),
)
SESSION_LINES = {
    "carve": [
        "You cut a rune into a ring, slowly, one stroke at a time.",
        "Rurik taps your chisel. 'Deeper. A rune is not a scratch.'",
        "The forge glows while you etch a charm line by line.",
        "A rune flares blue and settles. The charm is done.",
        "You quench a freshly carved amulet and it hisses back.",
    ],
}
SPECIAL = Special(
    KEY, TITLE, BLURB, "🔥", OWNER,
    "'Every rune takes a week to carve. Do not haggle.'",
    (Offer("Lucky Charm", "item", item="lucky_charm", factor=1.3),
     Offer("Ring of Vigor", "item", item="ring_of_vigor", factor=1.3),
     Offer("Amulet of the Mind", "item", item="amulet_of_mind", factor=1.3),
     Offer("Carve runes (4 rounds, 20% to the forge)", "job",
           item="carve")))
