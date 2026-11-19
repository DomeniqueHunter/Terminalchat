SISTERS = {
    "last_light": {
        "name": "Ada", "start_balls": 14, "limit": 70, "boil_chance": 0.05,
        "greeting": "Ada wipes her hands on her apron. 'Sit down, love. "
                    "<<npc.astrid_first>> is my big sister, but my yogurt is better. Care "
                    "to go in the vat – or somewhere warmer?'",
        "ask": "Ada pats her apron where it bulges. 'Climb in, love? All "
               "the way?'",
        "boil": "Ada turns the flame up and smiles, almost sad. 'You'd "
                "reduce so nicely, love. Forgive me.'",
        "growth": ("Under her apron Ada's balls hang a little fuller.",
                   "Ada's balls are heavy now, sloshing with every step.",
                   "'Look at them. <<npc.astrid_first>> will be jealous.'"),
    },
    "ironhold": {
        "name": "Gerda", "start_balls": 15, "limit": 80, "boil_chance": 0.06,
        "greeting": "Gerda slams a tankard down. 'Astrid's recipe, my "
                    "stout. Dig deep. Or climb in.'",
        "ask": "Gerda cracks her knuckles. 'Last chance to turn back, "
               "little one.'",
        "boil": "Gerda adds coal with a heavy hand. 'Reducing is an old "
                "craft, lad. Hold still.'",
        "growth": ("Gerda's balls hang like two small kegs.",
                   "Gerda's balls hang like two big kegs now.",
                   "'Soon I need a bigger apron!'"),
    },
    "cogsworth": {
        "name": "Tilly", "start_balls": 11, "limit": 55, "boil_chance": 0.07,
        "greeting": "Tilly pushes her goggles up. 'Fizz test day! Need a "
                    "starter? Hop in. Or in *me*, more pressure.'",
        "ask": "Tilly taps a gauge. 'Valve is ready. Pressure check, yes? "
               "'",
        "boil": "Tilly turns a valve with trembling hands. 'Pressure is "
                "climbing... sorry, sorry, I need the data!'",
        "growth": ("Tilly's balls are round, glistening kegs, pipes and "
                   "all.",
                   "Tilly has fitted a gauge on each of her balls.",
                   "'Next time I add a second boiler.'"),
    },
    "mudgate": {
        "name": "Snizzle", "start_balls": 12, "limit": 60, "boil_chance": 0.09,
        "greeting": "Snizzle grins around her spoon. '<<npc.astrid_first>> is my big "
                    "sister. I made it sourer. Care to ferment?'",
        "ask": "Snizzle points the spoon at {name}. 'Last chance to be "
               "sensible.'",
        "boil": "Snizzle opens the damper wide. 'Don't squeal, it spoils "
                "the taste... actually squeal.'",
        "growth": ("Snizzle's balls are tight and sour-sweet.",
                   "Snizzle's balls are heavy and brimming now.",
                   "'I could start my own brewery.'"),
    },
}
VATS = {
    "last_light": ("Yogurt", "Kefir", "Lassi", "Skyr"),
    "ironhold": ("Stout", "Porter", "Bock", "Dark Mead"),
    "cogsworth": ("Fizz", "Sparkle", "Spritz", "Pop"),
    "mudgate": ("Sour Mash", "Bog Sour", "Gruel", "Stinkbeer"),
}
TEMPS = {
    "cool": (30, 0.8, "It ferments slowly, cool and still."),
    "warm": (45, 1.0, "Warm and inviting, a little steam on top."),
    "hot": (25, 1.3, "Hot and steaming, the surface barely trembles."),
}
UNDRESS = ("{sister}: 'Strip first – everything.' Your gear goes into the "
           "locker (boots may stay). You get it back after the shift.")
VAT_INTRO = ("{sister} points you to the {temp} {vat} vat. {temp_line} Your "
             "shift as {title} begins: {rounds} rounds.{extra}")
TOO_HEAVY = ("{sister} sizes you up and shakes her head. 'Not yet, love. "
             "Come back when I have grown. Or kneel down and use your "
             "mouth instead – ask for the service.'")
SERVICE_FIT = ("{sister} laughs. 'You? You would slide right in. Use the "
               "vat, I will take you properly.'")
SERVICE_HELP = "Choose with the buttons in the panel"
SERVICE = {
    "last_light": {
        "start": "Ada lifts her apron and sits on the stool by the vats, "
                 "heavy and patient. 'Kneel down, dear. Take your time.'",
        "gentle": "You lick along her slowly. Ada hums, relaxed.",
        "eager": "You work her hungrily. Ada's breath catches and she "
                 "grips the stool.",
        "deep": "You take as much of her as you can. Ada moans and "
                "strokes your hair.",
        "done": "Ada shudders, thick and warm, and fills a bottle with "
                "what you earned. 'Good worker. Here, a batch for you.'"},
    "ironhold": {
        "start": "Gerda drops her leather apron and plants her boots wide. "
                 "'On your knees. No nonsense.'",
        "gentle": "You lick her slowly. Gerda grunts, approving.",
        "eager": "You go at her eagerly. Gerda's fist thumps the vat rim.",
        "deep": "You take her deep. Gerda curses, grinning.",
        "done": "Gerda finishes with a roar and a full tankard. 'Not bad "
                "for a surface dweller. Take this.'"},
    "cogsworth": {
        "start": "Tilly steps out of her goggles and apron, ears red. "
                 "'Uh. Right. Kneel? Please?'",
        "gentle": "You lick her slowly. Tilly squeaks and taps a pipe.",
        "eager": "You work her eagerly. Tilly's wrench clatters to the "
                 "floor.",
        "deep": "You take her deep. Tilly babbles numbers, then gives up.",
        "done": "Tilly shakes, fills a flask with trembling hands and "
                "presses it into yours. 'Calibrated. Mostly.'"},
    "mudgate": {
        "start": "Snizzle kicks the stool over and grins, wide and "
                 "toothy. 'Down, down. Lick the boss.'",
        "gentle": "You lick her slowly. Snizzle cackles and wiggles.",
        "eager": "You go at her eagerly. Snizzle whoops and slaps the vat.",
        "deep": "You take her deep. Snizzle gurgles, delighted.",
        "done": "Snizzle shudders, bottles the result and tosses it to "
                "you. 'Best brew of the week! Fresh!'"},
}
BOIL_ESCAPE = ("{name} claws out of the vat, scalded and furious. {sister} "
               "shrugs. 'Pity. Next time.'")
BOIL_SURVIVE = ("The steam clears. {name} is still there, red and limp, but "
                "alive. {sister} turns the flame down at the last moment, "
                "grins and bottles a thick reduction. 'You'll live. "
                "Barely.'")
BOIL_DEATH = ("The vat goes quiet. {sister} ladles the thick reduction into "
              "bottles, and {name} is nowhere to be seen. 'Beautiful "
              "batch.'")
DEAD_LOCK = ("You are dead – reduced to a bottle in the Brewhouse. You sit "
             "out until the current dungeon round is over.")
VORE_HELP = "Choose with the buttons in the panel"


VORE_DEATH = {
    "last_light": "Ada groans, her balls pulse, and {name} is gone "
                  "with the surge: nothing left but a warm, creamy spill "
                  "in the bottle she holds under the tip. 'Oh, dear. "
                  "Waste not.'",
    "ironhold": "Gerda grips the bench and bellows. {name} leaves her "
                "the only way a batch can: a thick, hot load into the "
                "waiting tankard. 'Cheers,' she says, hoarse.",
    "cogsworth": "Tilly's gauge spikes, the pipes shudder and {name} is "
                 "spent into the flask in a long, glistening stream. "
                 "'Oh no. Oh no, that was... that was the yield.'",
    "mudgate": "Snizzle whoops, arches, and {name} comes out as one "
               "fat, sticky load across the vat rim. 'Fresh! Fresh "
               "from the boss!'",
}


VORE = {
    "last_light": {
        "swallow": "Ada lifts her apron and sits you on the stool. 'Easy, "
                   "dear.' She guides you onto the tip, warm and patient, "
                   "and you slide in, inch after inch, until the thick "
                   "base closes behind you. The shaft squeezes you down "
                   "and down into the dark, towards her heavy balls. 'Off "
                   "you go. My balls do the rest.'",
        "inside": {
            "relax": "You sink into her balls. The heat loosens you, "
                     "softens you, and you feel yourself thinning into "
                     "something thick and creamy. Ada hums.",
            "struggle": "You thrash inside the sac. Her balls clench "
                        "around you and Ada gasps. 'Shh. The more you "
                        "wriggle, the faster you turn.'",
            "squirm": "You squirm in the heat. Ada laughs and presses a "
                      "hand to her swell. 'Ooh. Do that again.'",
        },
        "release": "Her balls grow tight. At the last moment Ada breathes "
                   "out and pushes: you come back out of the tip in one "
                   "slow rush, slick, shaking, half dissolved but whole. "
                   "'Beautiful. Here, your bottle.'",
    },
    "ironhold": {
        "swallow": "Gerda lifts you with one hand, thick shaft in the "
                   "other. 'Open up the door!' She forces you onto her "
                   "tip and works you in, inch by thick inch, until the "
                   "shaft swallows your feet and she slaps her belly. "
                   "'Down to the kegs with you. Don't touch the walls.'",
        "inside": {
            "relax": "You sink into her balls and the heat takes your "
                     "edges. You thin out, dark and thick. 'Good lad,' "
                     "Gerda rumbles.",
            "struggle": "You kick against the sac. Her balls jump and "
                        "Gerda roars. 'Go on! Makes the stout sweeter.'",
            "squirm": "You squirm in the heat. Gerda laughs and slaps "
                      "her belly. 'Ha! Still stirring!'",
        },
        "release": "Gerda grunts, clenches, and shoves: out you come, "
                   "dripping and half melted, but still a man. She throws "
                   "a towel. 'Drinkable. Take your coin.'",
    },
    "cogsworth": {
        "swallow": "Tilly hops onto a barrel and guides you onto her tip "
                   "with quick, practiced hands. You are fed in, fast and "
                   "tidy, through the pipe of her shaft and into the "
                   "pressure chamber of her balls. She taps her belly "
                   "with a spanner. 'Pressure rising! Do not panic, "
                   "panic makes foam.'",
        "inside": {
            "relax": "You sink into her balls. The heat turns you to "
                     "foam, then to cream, bit by bit. 'Perfect! Fizz "
                     "rate is lovely.'",
            "struggle": "You thrash. Her balls jerk and Tilly yelps. "
                        "'Careful! That causes foam!' She giggles.",
            "squirm": "You squirm and Tilly taps a gauge on her belly. "
                      "'Reading: tickles.'",
        },
        "release": "Tilly twists a valve and you are blown back out, "
                   "sticky, dizzy and covered in bubbles, half dissolved "
                   "but whole. 'Grade A! Look: a bottle with your name "
                   "on it!'",
    },
    "mudgate": {
        "swallow": "Snizzle laughs, grabs you and eases you onto her long "
                   "tip. You slide in, messy and quick, with Snizzle "
                   "giggling the whole way, down the shaft and into the "
                   "sour dark of her balls. 'Mmm. Already sour. "
                   "Perfect.'",
        "inside": {
            "relax": "You sink into her balls. The sour heat melts you "
                     "into a thick, sticky mash. 'Good. Fermenting "
                     "nicely.'",
            "struggle": "You thrash. Snizzle squeals. 'Squeal if you "
                        "like! It goes into the flavour.'",
            "squirm": "You squirm and Snizzle shakes her balls like a "
                      "tambourine. 'Again, again!'",
        },
        "release": "Snizzle sits up with a grin, clenches and out you "
                   "pop, sour-smelling, slimy and half dissolved. 'Sour "
                   "as sin. Come back.'",
    },
}
