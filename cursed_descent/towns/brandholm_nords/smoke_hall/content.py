from ....town_buildings.counter import Offer, Special
from ....town_buildings.work.model import Job


KEY = "smoke_hall"
TITLE = "The Smokehouse"
BLURB = ("A black brick house with a great wooden box, a little hatch and a "
         "painted wheel on the wall. Short smoke or full smoke.")
OWNER = "Svanhild Brandsdottir"
PLACE = "🔥 The Smokehouse – Svanhild keeps the box and the wheel."
CLOSED = "The Smokehouse is shut while you are in the dungeon."
CUT = 0.25
SHORT_RISK = 0.10
SHORT_PAY = 60
WHEEL = (("feet", 0.7), ("balls", 0.3))
BOX = {"feet": (0.70, "Svanhild's broad bare soles slide through the "
                      "openings and fill the box."),
       "balls": (0.98, "Svanhild stands over the hatch. The haze that "
                       "fills the box is thick, salty and entirely "
                       "hers.")}
FULL_PAY = 400
SHORT_TEXT = ("The lid closes for a few breaths only. The smoke is warm "
              "peat and bare foot, sweet and heavy. Odd opens the lid, "
              "you stagger out grinning, and Svanhild counts out {pay} "
              "gold.")
WHEEL_TEXT = ("Svanhild spins the wheel. It clicks past feet, balls, feet, "
              "feet... and slows to a stop on {pick}. 'The wheel has "
              "spoken,' she says. {scene}")
CURED = ("The lid lifts. You are limp, smelling of peat and skin, but "
         "alive. 'Cured,' says Svanhild, and counts out {pay} gold.")
JOBS = (
    Job("smoke", "Smoke Hand", KEY, 4, 22, "vitality",
        "Stack peat, tend the fire and check the latches."),
)
SESSION_LINES = {
    "smoke": [
        "You stack peat blocks along the wall.",
        "Odd shows you how to set the latch. 'Never forget the latch.'",
        "You sweep ash from under the great box.",
        "You hang planks on the wall, each with a name.",
    ],
}

SPECIAL = Special(
    KEY, TITLE, BLURB, "🔥", OWNER,
    "'Short smoke or full smoke? Choose slowly.'",
    (Offer("Work the fire (4 rounds, 25% cut)", "job", item="smoke"),
     Offer("Short smoke (a few breaths in the box, 10% risk)", "short"),
     Offer("Full box: the wheel decides feet or balls (very dangerous, "
           "400 gold if cured)", "box")))
