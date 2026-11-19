from ....town_buildings.counter import Offer, Special


KEY = "lab"
TITLE = "Experiment Lab"
BLURB = "Volunteers wanted for the gnomes' latest experiments."
EXPERIMENT_EXP_PER_LEVEL = 5
EXPERIMENT_HURT_SHARE = 0.15
SPECIAL = Special(
    KEY, TITLE, BLURB, "⚗", "Dr. Quill Fizzlebolt",
    "'Hold still. This is probably safe. Probably.'",
    (Offer("Join an experiment", "experiment", price=100),))
