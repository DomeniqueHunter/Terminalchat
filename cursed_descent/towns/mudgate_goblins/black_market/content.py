from ....town_buildings.counter import Offer, Special


KEY = "black_market"
TITLE = "Black Market"
BLURB = "Cursed goods nobody asks about."
SPECIAL = Special(
    KEY, TITLE, BLURB, "🕶", "Sniv the Fence",
    "'Never seen you. Never sold you anything. Cash only.'",
    (Offer("Soul Drinker", "item", item="cursed_blade", factor=1.5),
     Offer("Grave Plate", "item", item="cursed_plate", factor=1.5),
     Offer("Whispering Skull", "item", item="cursed_skull", factor=1.5),
     Offer("Gorgon Eye", "item", item="gorgon_eye", factor=1.5)))
