DAIRY_BUFFS = {
    "dairy_fresh": {
        "label": "Freshly milked", "bonus": {"vitality": 2}, "text": "",
    },
    "dairy_stud": {
        "label": "Herd-strong", "bonus": {"strength": 3, "vitality": 2},
        "text": "",
    },
    "dairy_heir": {
        "label": "Named heir",
        "bonus": {"vitality": 3, "intelligence": 2}, "text": "",
    },
}


PRODUCTS = {
    "milk": {"name": "{name}'s Milk", "base": "dairy_milk",
             "note": "a jug with a number chalked on the cork – {name}'s "
                     "tag. Warm, sweet, and yours for a few coins."},
    "cream": {"name": "{name}'s Double Cream", "base": "dairy_cream",
              "note": "a pot sealed with red wax and a tag: {name}. "
                      "Odile writes the yield on the lid."},
    "cheese": {"name": "{name}'s Reserve Cheese", "base": "dairy_cheese",
               "note": "a small wheel aged under the barn, branded with "
                       "{name}'s ear tag. The cellar smells of her."},
    "butter": {"name": "{name}'s Butter", "base": "dairy_butter",
               "note": "a hand-churned crock marked {name}. The farm "
                       "says it keeps better than she did."},
    "seed": {"name": "{name}'s Stud Draught", "base": "dairy_tonic",
             "note": "a dark bottle with a nose-ring seal and the name "
                     "{name} burned into the wax."},
    "ham": {"name": "{name}'s Cured Ham", "base": "dairy_cheese",
            "note": "a ham hung in the cellar for the allotted season, "
                    "a tag still tied to the bone: {name}."},
}


BREED_NAMES = {"milked_dry": ("milk", "cream", "cheese", "butter"),
               "bull_stud": ("seed",), "culled": ("ham",)}


SERVE_TEXTS = {
    "milk": {
        "start": "{name} sits down on a three-legged stool beside a "
                 "patient cow in the long barn. A pail is pushed between "
                 "{their} knees. 'Hands warm. Slow rhythm. She tells you "
                 "when she is done,' <<npc.odile_first>> says.",
        "turn": [
            "{name} finds the rhythm and the pail fills with a steady "
            "hiss.",
            "The cow sighs and leans into {name}'s shoulder; the foam "
            "climbs the rim.",
            "{name} wipes {their} hands on the apron and starts on the "
            "next row of stalls.",
        ],
    },
    "feed": {
        "start": "{name} is handed two buckets and a fork. 'Mash for the "
                 "herd, extra for the heavy ones,' <<npc.odile_first>> says. "
                 "'They eat what they are given. Give them plenty.'",
        "turn": [
            "{name} hauls mash along the stalls while huge, heavy women "
            "turn their heads and snuffle for more.",
            "A plump cow with a tag reading 12 grabs {name}'s sleeve and "
            "will not let go until she has been fed by hand.",
            "{name}'s arms tremble under the buckets; the herd chews "
            "on, unhurried.",
        ],
    },
    "cow": {
        "start": "{name} is led to an empty stall at the end of the "
                 "row. A numbered ear tag is clipped on, a brass bell is "
                 "hung round {their} neck, and the machine is wheeled "
                 "over. '{name}. Cow shift. Do not fight the pump,' "
                 "<<npc.odile_first>> says, writing in the ledger.",
        "turn": [
            "The pump pulls, rhythmic and relentless, and {name}'s tag "
            "swings with every breath. Milk runs hot into the glass jar.",
            "The cow beside {name} lows softly. <<npc.odile_first>> "
            "taps the jar with a pencil. 'More. You are doing well.'",
            "{name} sags into the straw, bell chiming, the jar half full "
            "and getting heavier.",
        ],
    },
    "bull": {
        "start": "{name} is walked to the bull pen, a ring set in "
                 "{their} nose, a numbered tag in {their} ear. "
                 "'Stud shift,' <<npc.odile_first>> says. 'The herd is "
                 "waiting, and the herd is patient.'",
        "turn": [
            "{name} is led down the row from stall to stall, each cow "
            "presented in turn, each service logged in the ledger.",
            "The ring in {their} nose is tugged and {name} obeys, sweat "
            "running, the herd shifting restlessly behind the bars.",
            "A tray of jars is carried away, warm and numbered. "
            "<<npc.odile_first>> does not look up from the ledger.",
        ],
    },
}


VENUE_TEXTS = {
    "dairy": {
        "intro": "🥛 A long, low barn of black timber and whitewashed "
                 "stone, the sign above the door painted in neat red "
                 "letters: CRONE CREAMERY – MILK, CREAM, CHEESE. Behind "
                 "the open doors, rows of stalls, rows of ear tags, and "
                 "the steady chime of brass bells.",
        "door": "A young woman with a long brown braid sets down a pail. "
                "'Welcome. I am <<npc.odile_first>> Marsh. I keep the books. "
                "My mother keeps the barn.' Behind her, a vast silver-"
                "haired woman on a mound of straw lifts a hand without "
                "getting up.",
        "options": "Actions: {options} ({seconds} s)",
        "stock": "  {nr}. {item} – {price} gold",
        "empty": "The shelves are bare. The cellar is being restocked.",
        "poor": "{name} cannot pay {price} gold for {item} (has {gold}). "
                "<<npc.odile_first>> writes the amount in the ledger. 'Next "
                "time.'",
        "full": "{name}'s bag is full. <<npc.odile_first>> sets {item} aside "
                "with a tag marked '{name}'.",
        "buy": "{name} pays {price} gold. <<npc.odile_first>> wraps {item} "
               "in a clean cloth. 'Fresh today. Always fresh.'",
        "enter": "The party steps through the wide doors into the cool, "
                 "clean barn. Bells chime softly down the long row, and "
                 "<<npc.odile_first>> nods without looking up from her ledger.",
        "look_outside": "🔎 A long barn of black timber and whitewashed "
                        "stone, doors wide open. Milk churns line the "
                        "wall, a cart of wax-sealed cheeses waits by the "
                        "gate, and somewhere inside a brass bell rings "
                        "once, slowly.",
        "look": "🔎 The barn is clean and cold. Rows of numbered stalls "
                "run down both sides, each with a hook for a bell. A "
                "wall of copper pumps, glass jars and brass taps hums "
                "quietly. A cellar hatch in the floor lets out the smell "
                "of old cheese and wax.",
        "look_herd": "In the nearest stalls, women in ear tags and bells "
                     "stand or kneel in straw, aged between forty-five "
                     "and seventy-five, each one calm, heavy and fed:",
        "look_empty": "The stalls are empty today. Only the bells "
                      "hanging on their hooks.",
        "look_cow": "  – No. {nr}: {name}, {desc}.",
        "look_bull": "  – Pen {nr}: {name}, ring in nose, bell on the "
                     "gate.",
        "look_cull": "  – On a hook in the cellar: a tag marked {name}, "
                     "hung with the season's hams.",
        "mother": "On the best straw in the barn sits <<npc.marguerite_first>> "
                  "Marsh, sixty-three, tag number 1, a huge silver-haired "
                  "woman with a brass lead bell. She smiles at everyone as "
                  "if they were new calves.",
        "tour_start": "<<npc.odile_first>> picks up her ledger. 'Follow me. Do not "
                      "touch the bells.'",
        "tour": [
            "'This is the long row. Forty-one stalls. Cows give from "
            "forty-five, because older women give richer. The younger "
            "ones are kept in the loft until it is time.'",
            "'The pumps are copper, the jars are glass, the tags are "
            "numbered. A cow has a number, a yield and a mood. That is the "
            "whole farm.'",
            "'Over there, the bull pens. Rings, bells, jars. A bull is "
            "only the other half of the ledger.'",
            "'The cellar is where it ends for most. We keep the cheeses "
            "longest. Some of them have names on them. I write the names "
            "down so they are not forgotten.'",
            "'My mother was the first cow. I will be the second. My "
            "daughter will keep the book. It is not a threat. It is only "
            "the order of things.'",
        ],
        "tour_end": "<<npc.odile_first>> closes the ledger gently. 'That is "
                    "the tour. You may stay, you may work, or you may "
                    "go. The herd is patient.'",
        "tour_used": "<<npc.odile_first>> shakes her head. 'You have seen the "
                     "barn, {name}.'",
        "serve_busy": "{name} has already worked a shift today. "
                      "<<npc.odile_first>> checks the ledger. 'One shift per "
                      "hand, per day.'",
        "serve_no_cow": "<<npc.odile_first>> looks {name} over, then at the "
                        "ledger. 'The herd has no place for you as a cow. "
                        "You are welcome to milk or feed.'",
        "serve_no_bull": "<<npc.odile_first>> glances down the pens and back. "
                         "'We keep bulls with something to offer. You are "
                         "welcome to milk or feed.'",
        "aging": "'You are far too young for the long row,' <<npc.odile_first>> "
                 "says, and hands {name} a cup of something warm and "
                 "sweet. By the time it is finished, {name}'s hair is "
                 "streaked with grey, the skin loosened, the figure "
                 "heavier. Age {age}. 'Now you may stand in the row.'",
        "round": "{name} works round {turn} of {turns} (stamina "
                 "{stamina}/{maximum}, {gold} gold earned).",
        "faint": "{name} sinks into the straw, breath gone. "
                 "<<npc.marguerite_first>> rolls {them} onto a blanket with "
                 "one big hand. 'Sleep, dear. The cows are not going "
                 "anywhere.'",
        "done": "{name} finishes the shift. <<npc.odile_first>> counts the "
                "coins into {their} hand. 'Fair work. Fair pay.' {bonus}",
        "product": "<<npc.odile_first>> adds something from the shelf. 'For the "
                   "road.'",
        "cull": "<<npc.odile_first>> does not look up. 'Three shifts, {name}. "
                "The ledger says it is time.'",
        "heir": "<<npc.marguerite_first>> lifts her hand and <<npc.odile_first>> stops "
                "writing. 'Mother has chosen,' she says quietly. "
                "'{name} is to be the next lead cow. Not today. But "
                "the bell has a name on it now.' A new tag is "
                "clipped on. {bonus}",
        "sellself": "{name} walks into the barn and tells <<npc.odile_first>> "
                    "to put {them} on the books. She counts {gold} gold "
                    "into {their} hand without a flicker.",
        "sellself_no": "<<npc.odile_first>> shakes her head. 'The herd takes "
                       "cows with a full bust and bulls with a full "
                       "yard. Neither, {name}? Then you are a guest.'",
        "depart": "<<npc.odile_first>> hands over a cloth-wrapped parcel. 'For the "
                  "walk.' Behind her, <<npc.marguerite_first>> rings her bell "
                  "once, softly, as the party leaves.",
    },
}
