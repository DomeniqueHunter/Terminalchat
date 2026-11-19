VENUE_TEXTS = {
    "north_pole": {
        "intros": [
            "❄ The corridor ends in a wall of snow, and the snow ends in "
            "a sky full of green and violet light. Ahead, a workshop "
            "village glows under the aurora: crooked red roofs, candy-"
            "cane lamp posts, a sleigh the size of a barn. Everything "
            "smells of cinnamon, pine and hot wax, and somewhere "
            "behind it all a thousand tiny bells are ringing.",
            "❄ A warm wind that does not belong to any dungeon blows "
            "through the passage, and the stone floor turns to packed "
            "snow under your boots. Beyond an arch of frosted holly "
            "lies a snug little village of workshops, stables and "
            "chimneys, all lit from within. A banner over the gate "
            "reads: NORTH POLE – DELIVERIES DAILY.",
        ],
        "options": "Actions: {options} ({seconds} s)",
        "look_outside": "🔎 A snowy workshop village under the aurora.",
        "look": "🔎 The workshop smells of glue, pine and warm "
                "gingerbread. Elves hurry between benches with ribbons "
                "and tape, and along the back wall stand rows of gift-"
                "wrapped parcels, each with a tag. Some of the parcels "
                "are the size of a person, and a few of them move "
                "slightly. The ones that are ready can be taken:",
        "look_gift": "  [{nr}] Wrapped Gift – {name}, stage {stage}",
        "look_none": "🔎 The shelves are bare. A few elves sweep up "
                     "ribbon ends and yawn. Nothing is wrapped and "
                     "waiting at the moment.",
        "enter": "The party walks through the arch. Inside, the cold "
                 "vanishes. Benches, stoves and shelves crowd under a "
                 "low, beamed ceiling, and by the biggest stove sits a "
                 "towering matron in a red velvet bodice with her "
                 "boots up on a stool, stockinged feet toasting by the "
                 "fire. Mrs. Claus waves a mug of cocoa at you. 'Come "
                 "in, come in, dears. Nobody is naughty at the North "
                 "Pole. Not before supper.'",
        "watch_wrap": [
            "👀 Through a window a crew of elves is hard at work. "
            "{name} is laid out on a workbench, snug in a nest of "
            "tissue, while two elves pull a ribbon around the waist "
            "and a third balances on a stool to lay the bow. A tag "
            "goes on last: 'To a good child'. The parcel is sealed with "
            "a tiny stamp and carried off to the shelves.",
            "👀 An elf with a clipboard checks a list, ticks a box, and "
            "waves the next one forward. A parcel the size of a person "
            "slides down a chute on the conveyor, gets a gold bow "
            "slapped on, and is stacked on a shelf with the others. "
            "The tag reads {name}.",
        ],
        "watch_none": "👀 The elves have no new parcels to wrap, so they "
                      "wrap each other instead, giggling, until one "
                      "ends up taped to the ceiling.",
        "watch_depart": [
            "👀 A bell rings and the whole village runs. Reindeer are "
            "hitched with a clatter of harness, a mountain of gift "
            "sacks is lashed onto the sleigh, and Mrs. Claus climbs "
            "up on the bench with a thump that rocks it on its "
            "runners. 'Ho ho ho! Behave, dears!' The sleigh lifts into "
            "the aurora with a jingle and a gust of cinnamon, and "
            "is gone.",
        ],
        "talk": [
            "{name} sits down by the fire. Mrs. Claus pours hot "
            "cocoa, asks about the dungeon, laughs in the right places "
            "and gives {name} a cookie shaped like a boot. 'Everybody "
            "tells me how tiring it is,' she says. 'Nobody asks how my "
            "feet are. You are a good one, dear.' The cocoa warms "
            "everyone to the bones.",
        ],
        "talk_none": "Mrs. Claus has already told you all her stories "
                     "for now. She smiles and hums a carol instead.",
        "boots_1": "👢 'Oh, bless you, would you? My feet are killing me "
                   "after the run.' Mrs. Claus plants one huge boot in "
                   "{name}'s lap. {name} works the laces loose, one slow "
                   "cross at a time, and eases the boot off. Heat rolls "
                   "out of it, leather and warm wool and cinnamon.",
        "boots_2": "👢 'Go on, dear. Properly. Deodorizing is a thorough "
                   "business.' {name} pushes {their} face deep into the "
                   "boot and breathes in. Leather, pine, cinnamon, and a "
                   "long day of sleigh-pulling. {name} breathes in again, "
                   "and {their} head turns heavy and pleasantly warm. "
                   "Above {name}, Mrs. Claus sighs happily and wiggles "
                   "her toes in the red stocking.",
        "boots_3": "👢 'Now the other one.' She does not bother with the "
                   "stool this time. {name} ends up flat on the floor "
                   "with a stockinged foot planted on {their} chest, "
                   "heavy as a sack of flour and warm as bread, {their} "
                   "face buried in the second boot. {name} breathes in "
                   "until there is nothing else left, and comes up dizzy "
                   "and glowing.",
        "boots_win": "'Wonderful. Spotless. I could kiss you, dear.' "
                     "Mrs. Claus squeezes {name} hard enough to creak "
                     "something and presses a parcel into {name}'s "
                     "hands: {item}.",
        "boots_friend": "Mrs. Claus pats the cushion next to her. "
                        "'You and I will be friends, dear. Come back "
                        "next year.'",
        "boots_sloppy": "👢 'You barely breathed, dear. A little "
                        "hasty.' Mrs. Claus licks a pencil and writes in "
                        "a very big book. 'Naughty List. Just a note, "
                        "nothing serious.' A cold gust blows through "
                        "{name}'s pockets, and {name} feels strangely "
                        "tired.",
        "boots_done": "The boots are done. Mrs. Claus wiggles her "
                      "toes happily and does not need anything more.",
        "boots_busy": "Mrs. Claus has her feet up and is not "
                      "interested in anything else right now.",
        "harvest": "🎁 {name} lifts the parcel from the shelf. It is "
                   "heavy, warm, and breathes softly under the paper. "
                   "The tag reads: 'To a good child, from Mrs. Claus.' "
                   "A real gift.",
        "own": "🎁 {name} stops in front of the shelf. The tag on the "
               "parcel reads {name}. The elves look up, a little "
               "embarrassed. Then {name} takes the parcel down anyway.",
        "gone": "That parcel is already taken.",
        "none": "The shelves are empty. Nothing is waiting to be "
                "taken.",
        "full": "{name}'s bag is full.",
        "depart": "The party leaves the village. The arch of holly "
                  "closes behind them, and for a long while the smell "
                  "of cinnamon and boot leather clings to everyone's "
                  "clothes.",
    },
}
GIFT_TEXT = ("A gift wrapped in red paper and gold ribbon, with a tag: "
             "'To a good child, from Mrs. Claus.' Inside is {name}, a "
             "level {level} {build} {gender}, folded snug and breathing "
             "softly through the paper. The elves tied the bow "
             "themselves.")
