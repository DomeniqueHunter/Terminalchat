from ....town_buildings.counter import Offer, Special


KEY = "workshop"
TITLE = "Gadget Workshop"
BLURB = "Clockwork tonics and tools, mostly working."
SPECIAL = Special(
    KEY, TITLE, BLURB, "⚙", "Sprocket Ironwhistle",
    "'Everything here has been tested. By somebody.'",
    (Offer("Mana Potion", "item", item="mana_potion", factor=0.9),
     Offer("Wake-Up Tonic", "item", item="wake_tonic", factor=0.9),
     Offer("Cooling Draught", "item", item="cooling_draught", factor=0.9),
     Offer("Elixir of the Depths", "item", item="elixir", factor=0.9)))
