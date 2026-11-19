GRILL_BUFFS = {
    "grill_special": {
        "label": "Today's special", "bonus": {"strength": 3, "vitality": 3},
        "text": "",
    },
    "grill_plain": {
        "label": "House special", "bonus": {"vitality": 2}, "text": "",
    },
}


BUILD_WORDS = {
    "Slim": "a slim, tender bird that cooks fast",
    "Average": "an even, well-proportioned roast",
    "Curvy": "a soft, generous roast that drips at every turn",
    "Toned": "lean, firm meat with a dark crust",
    "Muscular": "a heavy, dense cut that needs long, slow heat",
    "Heavy": "a juicy, wide roast that sizzles in its own fat",
}


SPIT_LOOK = {
    "Male": "{name} hangs lengthwise on the spit, arms tied along the "
            "iron, shoulders shining with oil, an apple wedged between "
            "the teeth. {build}.",
    "Female": "{name} is folded onto the spit with the knees drawn up, "
              "the soft curves brushed with herb oil and shining in the "
              "firelight. {build}.",
    "Herm": "{name} is spitted whole, both halves of the body seasoned "
            "evenly and the skin crackling gold. {build}.",
    "Shemale": "{name} turns on the spit, salted everywhere, a little "
               "card pinned to the rope: 'special'. {build}.",
    "Transgender": "{name} is bound to the spit and brushed with garlic "
                   "oil, the skin slowly going golden. {build}.",
    "any": "{name} turns on the spit, bound, glazed and golden. "
           "{build}.",
}


VENUE_TEXTS = {
    "grill": {
        "intro": "🍗 A crooked cart under a patched awning, smoke curling "
                 "up into the dark. A vertical spit of meat turns slowly "
                 "over the coals, half a dozen chickens sizzle on iron "
                 "rods, and a hand-lettered board reads: <<npc.gul_first>>'S "
                 "GRILL – NOBODY LEAVES HUNGRY.",
        "door": "A broad woman with a gold tooth waves a carving knife "
                "at the party. 'Sit, sit! Chicken, kebab, sauce. Good "
                "food, honest price.' The spit turns behind her, much "
                "too large for any animal you can think of.",
        "options": "Actions: {options} ({seconds} s)",
        "stock": "  {nr}. {item} – {price} gold",
        "empty": "The grill is cold. Nothing left on the menu.",
        "poor": "{name} cannot pay {price} gold for {item} (has {gold}). "
                "<<npc.gul_first>> shrugs. 'Hunger is free. Food is not.'",
        "full": "{name}'s bag is full. <<npc.gul_first>> wraps {item} in paper "
                "anyway and keeps it warm for later.",
        "buy": "{name} pays {price} gold. <<npc.gul_first>> carves, wraps and "
               "slides over {item}, still steaming.",
        "look": "🔎 A cart of dented steel on four wheels, a gas-red "
                "grill glowing, tongs hanging on hooks. Behind the cart a "
                "curtain of oilcloth hides the back; the smell is rich, "
                "warm and slightly too sweet. A tray of cut tomatoes, "
                "flatbread, a barrel of sauce.",
        "look_spit": "Behind the curtain a long spit turns over the "
                     "coals:",
        "look_spit_empty": "Behind the curtain: only chickens. Today.",
        "special_poor": "{name} cannot afford the special ({price} gold, "
                        "has {gold}). <<npc.gul_first>> pats the spit. 'It will keep.'",
        "special_used": "<<npc.gul_first>> shakes her head. '{name}, one special per "
                        "guest. Even a big appetite has a limit.'",
        "special_named": "<<npc.gul_first>> carves a thick slice from the spit and "
                         "lays it on a hot plate. 'Today's special: "
                         "{dead}. Eat it while it is warm.'",
        "special_plain": "<<npc.gul_first>> carves a plain slice from the kebab spit. "
                         "'The special is only a good chicken today. "
                         "Come back when the spit is fuller.'",
        "special_eat": "{name} eats. It tastes like someone's best "
                       "effort. {bonus}",
        "special_eaten": "Nothing is left of {dead} on the spit but "
                         "bones and a skewer.",
        "ask_excuse": [
            "'The meat?' <<npc.gul_first>> laughs. 'Mountain goat. Very tough, "
            "very honest goat.' She does not meet your eye.",
            "'Family recipe,' she says, and turns the spit. 'Do not "
            "ask which family.' The joke does not land the way she "
            "intended.",
            "'Chicken. Mostly chicken.' She waves the knife. 'The rest "
            "is the other chicken.'",
        ],
        "ask_smile": "<<npc.gul_first>> smiles and sets down the knife. 'You are "
                      "smart, dear. Smart ones live long.' Her gold tooth "
                      "flashes. 'Today the spit is somebody you might "
                      "have known.'",
        "ask_see": "'Do you want to see?' <<npc.gul_first>> lifts the oilcloth "
                   "curtain without waiting for an answer.",
        "ask_used": "<<npc.gul_first>> looks at {name} for a long moment. 'You "
                    "have asked enough today.'",
        "complain_warn": "<<npc.gul_first>> lowers her knife slowly. 'Too dry, you "
                         "say? Too salty?' A pause. 'I will not hear it "
                         "again, {name}.'",
        "complain_kill": "<<npc.gul_first>> puts down her brush. 'I warned you, "
                         "{name}.'",
        "depart": "<<npc.gul_first>> wraps the last slice in paper and presses it "
                  "into your hand. 'Come back hungry, my dear. Everybody "
                  "does.' The spit turns behind her as the party walks "
                  "on.",
        "hooks": "On the board, chalked in a tidy hand: {names}.",
        "no_hooks": "The board is clean. Nobody has been on the spit "
                    "yet.",
    },
}
