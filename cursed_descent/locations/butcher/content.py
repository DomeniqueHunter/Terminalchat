MEAT_GRADE_LABELS = {"common": "", "rare": "Prime", "epic": "Marbled Choice"}


HORSE_CUT = "Smoked Horse Sausage"


EXTRA_CUTS = {"ribs": "Spare Ribs", "roast": "Roast Haunch",
              "pate": "Liver Pâté", "brawn": "Brawn"}


SAUSAGE_CUTS = {"Human": "Prime Sausage", "Equine": HORSE_CUT,
                "Canine": "Spiced Hound Sausage",
                "Draconic": "Fire-Cured Dragon Sausage"}


PRIME_CUTS = {
    "b": "Prime Breast Fillets",
    "t": "Prairie Oysters",
    "r": "Rump Roast",
    "h": "Salt-Tanned Skin and Hair",
}


IMPLANT_CUTS = {
    "ib": "Silicone Breast Implants",
    "ir": "Silicone Butt Implants",
    "ie": "Cock Implant",
    "it": "Silicone Testicle Implants",
}


IMPLANT_UNITS = {"ib": "cc", "ir": "cc", "ie": "cm", "it": "cc"}


BUTCHER_CUTS = {
    "sausages": "Sausages",
    "ham": "Smoked Ham",
    "steaks": "Steaks",
    "bacon": "Bacon",
}


EVENT_TEXTS = {
    "butcher": {
        "intro": "🥩 Heavy footsteps, a smell of smoke and salt. A huge "
                 "pigman in a blood-stained apron steps into the light, "
                 "cleaver in hand. 'Fresh stock walking in on its own "
                 "legs!' – <<npc.hamhock_first>> the Butcher attacks!",
        "win": "<<npc.hamhock_first>> crashes into his own meat hooks. {name} helps "
               "themselves to his tools.",
    },
}


VENUE_TEXTS = {
    "butcher_shop": {
        "intro": "🥩 A shop sign shaped like a cleaver: 'HAMHOCK'S – "
                 "Finest Adventurer Cuts'. A huge pigman in a bloody apron "
                 "wipes his hands. 'Customers! Have a look.'",
        "door": "The door stands open. Meat hooks gleam in the dim light "
                "inside.",
        "enter": "🥩 The party steps over the sawdust into the shop.",
        "hanging": "Hanging from the hooks behind the counter: {names}.",
        "stock": "  [{nr}] {item} – {price} gold",
        "empty": "No adventurers on the hooks today – just boar. 'Come "
                 "back after a good hunt,' <<npc.hamhock_first>> grunts, eyeing the party "
                 "a little too long.",
        "own": "{name} recognises {their} own name on a price tag. "
               "<<npc.hamhock_first>> shrugs. 'Nothing personal. Good marbling.'",
        "buy": "{name} buys {item} for {price} gold. <<npc.hamhock_first>> wraps it in "
               "paper. 'Best cooked over an open fire.'",
        "poor": "{name} can't afford {item} ({price} gold, has {gold}).",
        "full": "{name}'s bag is full.",
        "sellself": "{name} climbs onto the butcher's block. <<npc.hamhock_first>> counts "
                    "out {gold} gold, sharpens his cleaver and gets to "
                    "work.",
        "fresh": "Fresh in the window: {item} – {price} gold",
        "yield": "🔪 <<npc.hamhock_first>> sets to work and gets {count} out of {dead}: "
                 "{cuts}.",
        "sausage": "🌭 '...and one {sausage} for the connoisseurs,' <<npc.hamhock_first>> "
                   "adds with a wink, holding it up to the light. 'The "
                   "house specialty.'",
        "prime": "🥩 <<npc.hamhock_first>> sets the prime cuts aside: {cuts}.",
        "implants": "🔧 'Hm, what's this?' <<npc.hamhock_first>> fishes {items} out of "
                    "{dead} and wipes it on his apron. 'Not edible – but "
                    "somebody will pay for the curiosity.'",
        "horse": "🔪 <<npc.hamhock_first>> eyes the carcass and scratches his chin. 'Hm. "
                 "Half horse, half hero. Horse sausage it is – the "
                 "customers pay extra for that.'",
        "options": "Actions: {options} ({seconds} s)",
        "depart": "<<npc.hamhock_first>> waves a sausage after the party. 'Come back "
                  "hungry!'",
    },
}
