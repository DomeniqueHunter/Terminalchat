SWEATERY_OPERATORS = {
    "goblin": {
        "plural": "goblins",
        "boss": "Grizzle",
        "sign": "GRIZZLE'S SWEATERY – Honest Pay for Honest Sweat!",
        "intro": "💦 A steaming tin shed leans against the corridor wall "
                 "under a crooked sign: 'GRIZZLE'S SWEATERY – Honest Pay "
                 "for Honest Sweat!'. Goblins of every age and gender "
                 "swarm around it with buckets, funnels and clipboards, "
                 "cackling happily.",
        "door": "A goblin waves a clipboard at the party. 'New sweaters! "
                "Naked is best, boots are fine!'",
        "enter": "💦 The party ducks into the shed. Warm, salty air, "
                 "rows of treadmills, iron racks and a glowing heater "
                 "bench. <<npc.grizzle_first>>, a squat old goblin with a measuring "
                 "jug on a chain, grins. 'Lockers on the left. Leave the "
                 "armour, keep the boots.'",
        "strip": "{name} takes off everything – weapon, armour, clothes – "
                 "and the goblins lock it in a locker. Only the boots stay "
                 "on.",
        "label": "A goblin labels the bottle in cheerful scrawl: "
                 "'{name} – {station} – {liters} l'.",
        "boots": "A goblin pulls off {name}'s {boots}, upends them over a "
                 "jar and wrings out every last drop. 'Nothing goes to "
                 "waste!'",
        "squeal": ["The goblins nod along to {name}'s squeals. 'Ordinary "
                   "workplace sound,' says <<npc.grizzle_first>>.",
                   "{name} squeals. A goblin hums a matching note and "
                   "writes down the pitch."],
        "roast": "<<npc.grizzle_first>> sniffs the air, shrugs and reaches for a "
                 "skewer. 'Well done, {name}. Literally.'",
        "pass": "The party walks past the shed. 'Come back sweaty!' "
                "<<npc.grizzle_first>> shouts after them.",
        "look_outside": "🔎 A steaming tin shed with a crooked sign. "
                        "Goblins of every age and gender swarm around it "
                        "with funnels and buckets, bottles stacked "
                        "outside, each labelled in messy handwriting.",
        "look_inside": "🔎 Treadmills, iron racks, a glowing heater bench "
                       "and a wall of lockers. Rows of labelled bottles "
                       "line the shelves, and a goblin sniffs one "
                       "thoughtfully.",
    },
    "gnome": {
        "plural": "gnomes",
        "boss": "Professor Tinkerwick",
        "sign": "TINKERWICK'S PERSPIRATORIUM – Precision Sweat Extraction",
        "intro": "💦 A neat brass pavilion hisses with steam under a "
                 "polished sign: 'TINKERWICK'S PERSPIRATORIUM – Precision "
                 "Sweat Extraction'. Gnomes in goggles scribble on "
                 "clipboards and adjust a forest of gauges.",
        "door": "A gnome adjusts her goggles. 'Volunteers? Splendid. "
                "Please remove all metal. Boots are permitted.'",
        "enter": "💦 The party steps into the pavilion. Brass pipes, "
                 "pressure gauges, calibrated treadmills and a heater "
                 "bench with a thermometer. <<npc.tinkerwick_first>> peers "
                 "up through three lenses. 'Lockers on the left. Metal "
                 "interferes with the readings.'",
        "strip": "{name} takes off everything – weapon, armour, clothes – "
                 "and the gnomes weigh it and lock it in a numbered "
                 "locker. Only the boots stay on.",
        "label": "A gnome engraves a brass tag: '{name} · {station} · "
                 "{liters} l'.",
        "boots": "A gnome removes {name}'s {boots} with tweezers and "
                 "decants them into a graduated jar, noting the volume. "
                 "'Footwear fraction: collected.'",
        "squeal": ["The gnomes record {name}'s squeal on a wax cylinder. "
                   "'Within tolerance,' says <<npc.tinkerwick_short>>.",
                   "{name} squeals. A gnome taps a gauge. 'Pitch is "
                   "consistent with the heat. Continue.'"],
        "roast": "<<npc.tinkerwick_short>> taps the thermometer, sighs and fetches the "
                 "carving set. 'Overshot the safety margin. Pity.'",
        "pass": "The party walks past the pavilion. 'Do return with "
                "fresh data,' <<npc.tinkerwick_short>> calls after them.",
        "look_outside": "🔎 A brass pavilion hissing with steam. Gnomes in "
                        "goggles scribble at clipboards among a forest of "
                        "gauges, and neat glass bottles sit in racks, "
                        "each with an engraved tag.",
        "look_inside": "🔎 Calibrated treadmills, weight racks with "
                       "scales, a heater bench with a thermometer and a "
                       "wall of numbered lockers. Brass condensers drip "
                       "into labelled flasks.",
    },
}


SWEATERY_STATION_TEXTS = {
    "run": {
        "name": "Running",
        "start": "{name} steps onto the treadmill and starts to run.",
        "cycle": ["{name} runs and runs, breath ragged, sweat flying. "
                  "+{liters} l.",
                  "{name} sprints on the treadmill while sweat drips "
                  "from every limb. +{liters} l."],
        "gain": "{name} feels faster after the long run. +1 agility.",
    },
    "lift": {
        "name": "Workout",
        "start": "{name} grabs the iron and starts to lift.",
        "cycle": ["{name} grunts under the bar, muscles shining with "
                  "sweat. +{liters} l.",
                  "{name} pumps iron until {their} arms shake and the "
                  "floor is slick. +{liters} l."],
        "gain": "{name} feels stronger after the workout. +1 strength.",
    },
    "heat": {
        "name": "Heater",
        "start": "{name} lies down on the glowing heater bench.",
        "cycle": ["{name} lies on the heated plate, skin red and "
                  "streaming. +{liters} l.",
                  "{name} gasps on the bench while the sweat runs in "
                  "rivers into the gutter. +{liters} l."],
        "gain": "",
    },
    "grill": {
        "name": "Grill",
        "start": "{name} is clamped between two iron grill grates and "
                 "swung out over the fire.",
        "cycle": ["{name} hangs between the glowing grates over the "
                  "flames, sweat sizzling into the pan. +{liters} l.",
                  "The goblins turn {name}'s grate over the coals, and "
                  "the sweat runs in streams. +{liters} l."],
        "hurt": ["{name} yelps as the hot bars press into {their} skin.",
                 "{name} squeals and wriggles between the grates, "
                 "which only presses the bars deeper."],
        "gain": "",
    },
    "labour": {
        "name": "Hard Labour",
        "start": "{name} is handed a pickaxe and a wheelbarrow.",
        "cycle": ["{name} hauls sacks and swings the pick, soaked to "
                  "the skin. +{liters} l.",
                  "{name} pushes a loaded wheelbarrow up the ramp, "
                  "dripping. +{liters} l."],
        "gain": "{name} learns a few tricks of the trade.",
    },
}


SWEATERY_HURT = [
    "{name} yelps as the plate scorches {their} skin.",
    "{name} squeals and tries to roll off the hot plate.",
]


SWEATERY_FEATURES = {
    "Equine": ("intensely animal, the {plural} sniff it twice",
               "with a gamey stable edge"),
    "Canine": ("musky, with a wet-fur edge",
               "with a wild, salty bite"),
    "Draconic": ("smoky and sulphurous, with a hot metal edge",
                 "with a smouldering sulphur finish"),
    "breasts": ("sweet and milky, with a creamy undertone",
                "sweet and creamy"),
    "balls": ("heavy and musky, ripe and masculine",
              "thick, salty-sweet and potent"),
    "endowment": ("rank and virile, unmistakably male",
                  "strong and salty, lingering"),
    "muscle": ("sharp and ironlike, like a well-used locker room",
               "mineral and iron-rich"),
    "butt": ("warm and round, like fresh bread",
             "soft and buttery"),
    "plain": ("warm and salty", ""),
}


SWEATERY_TASTES = {
    "run": "bright and salty, with a citrus snap",
    "lift": "heavy and mineral, like old iron",
    "heat": "roasted and smoky, with a spicy afterglow",
    "grill": "charred and smoky, with a hint of seared skin",
    "labour": "dull, salty and honest",
}


SWEATERY_GEAR_NOTE = ", plus a leathery note from {their} gear"


SWEATERY_PRODUCT_NOTE = "labelled '{name} · {station} · {liters} l'. " \
                        "Smells {smell}; tastes {taste}."


VENUE_TEXTS = {
    "sweatery": {
        "options": "Actions: {options} ({seconds} s)",
        "stock": "  [{nr}] {item} – {price} gold",
        "empty": "The shelves are empty. Nobody has sweated here yet.",
        "buy": "{name} buys {item} for {price} gold.",
        "poor": "{name} can't afford {item} ({price} gold, has {gold}).",
        "full": "{name}'s bag is full.",
        "dress": "{name} gets {their} gear back from the locker.",
        "idle": "{name} is not working here. Pick a station first.",
        "busy": "{name} is already sweating. [work] or [quit].",
        "blocked": "'Finish your shift first,' says {boss}. [work] or "
                   "[quit].",
        "turn": "⏱ {name}: cycle {cycle}/{cycles}",
        "status": "Earned so far: {gold} gold, {liters} l of sweat.",
        "done": "The shift is over. {name} is paid {gold} gold for "
                "{liters} l of sweat.",
        "quit": "{name} calls it quits and is paid {gold} gold for "
                "{liters} l of sweat.",
        "batch": "📦 {count} bottles go on the shelf: {item}.",
        "nobody": "Nobody has been roasted here yet.",
        "roasted": "  • {dead} – served hot, sold by the portion",
        "more": "  … and {count} more on the spit.",
        "own": "{name} spots {their} own name on the roast menu.",
        "depart": "The party leaves, sticky and a little lighter.",
    },
}
