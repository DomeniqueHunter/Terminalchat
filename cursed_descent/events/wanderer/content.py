EVENT_TEXTS = {
    "wanderer": {
        "intro": "🔥 By a small campfire sits {wanderer}, {description}. "
                 "'Rough place, this. Sit a while?' {wanderer} looks hungry – "
                 "{gold} gold would go a long way. Or maybe something of "
                 "yours: [give <bag nr|item>] or [give <slot>] for what "
                 "you're wearing.",
        "options": "Actions: {options} ({seconds} s)",
        "sit": "{name} sits down by the fire with {wanderer}. Stories, a "
               "shared pipe, a little laughter. The party heals {percent}% "
               "HP and feels wiser (+{exp} EXP).",
        "give": "{name} hands {wanderer} {gold} gold. With tears in their "
                "eyes they press something into {name}'s hand.",
        "broke": "{name} only has {have} gold – {wanderer} needs {gold}.",
        "no_item": "{name} has no such item – [inv] shows the bag, or name "
                   "a slot like 'feet' for what {name} is wearing.",
        "item_meh": "{name} hands {wanderer} the {item}. {wanderer} turns it "
                    "over, shrugs and pockets it anyway. In return: a small "
                    "token.",
        "item_like": "{name} gives {wanderer} the {item}. {wanderer}'s eyes "
                     "light up. 'Now that's useful.' Something is pressed "
                     "into {name}'s hand.",
        "item_love": "{name} gives {wanderer} the {item}. {wanderer} holds "
                     "it like a holy relic. 'Oh, this is perfect.' They dig "
                     "out their very best treasure for {name}.",
        "worn": "{name} takes the {item} off right there by the fire. "
                "{wanderer} accepts it still warm – and is very, very "
                "grateful.",
        "item_none": "{wanderer} has nothing left to give back.",
        "sleep": "{name} shares {wanderer}'s bedroll by the fire. What "
                 "happens under the blanket stays under the blanket. By "
                 "morning everyone is fully rested.",
        "theft": "… and {wanderer} is gone, along with {stolen} of "
                 "{name}'s gold.",
        "depart": "The party nods at {wanderer} and moves on.",
        "cook": "{name} skewers the raw meat over {wanderer}'s fire. "
                "Fat sizzles, smoke curls up, and soon it smells "
                "unsettlingly delicious. Cooked: {food}.",
        "thirsty": "{wanderer} shakes an empty canteen and stares, very "
                   "hard, at the bustier members of the party. 'Gods, I'm "
                   "parched. Wouldn't happen to have anything… fresh?' "
                   "([milk] or [nurse])",
        "milk": "{wanderer} produces a battered bucket and a stool. {name} "
                "sits back against a rock while {wanderer} milks {them} "
                "with surprisingly practised hands, until the canteen is "
                "full and there is a bottle left over. 'Fresh! Bless you.' "
                "{wanderer} pays {gold} gold.",
        "nurse": "{wanderer} can't wait for a bucket. {name} opens {their} "
                 "top, and {wanderer} drinks straight from the source – long, "
                 "greedy and blissful – until the thirst is gone. They lean "
                 "back, flushed and grateful, and press {gold} gold into "
                 "{name}'s hand.",
        "milk_hung": "{wanderer} eyes {name}, notices just how "
                     "impressively {name} is built, and sets the bucket "
                     "aside. 'There's more than one way to quench a "
                     "thirst.' The two of them disappear behind a boulder "
                     "for a while. {wanderer} comes back very satisfied, "
                     "pays {gold} gold and hands over a bottle of their "
                     "best moonshine as a thank-you.",
        "nurse_hung": "{wanderer} kneels down in front of {name} without a "
                      "word. The rest of the party very pointedly studies "
                      "the campfire for a while. Afterwards {wanderer}'s "
                      "thirst is clearly quenched, and {gold} gold changes "
                      "hands.",
        "dry": "{name} has nothing {wanderer} could drink from. (A Large "
               "bust or bigger – or being very well hung – is needed. Dr. "
               "<<npc.vane_first>>'s [clinic] could help.)",
    },
}


WANDERERS = [
    ("Old Tomas", "a grey-bearded wanderer", ["consumable", "weapon"]),
    ("Sael", "a hooded elven drifter", ["head", "accessory", "allure"]),
    ("Bram", "a travelling tinker", ["weapon", "chest", "gloves"]),
    ("Vesk", "a scarred mercenary", ["weapon", "lingerie", "worn"]),
    ("Mirelle", "a sharp-eyed sellsword", ["feet", "crotch", "worn"]),
    ("Lord Pimsley", "a perfumed collector of curiosities",
     ["worn", "lingerie", "crotch", "feet", "allure"]),
    ("Gorm", "a sunburnt prospector with cracked lips",
     ["weapon", "head", "consumable"], True),
    ("Sister Mab", "a wandering nun with a very empty canteen",
     ["lingerie", "allure", "consumable"], True),
]


WEAR_TEXTS = {
    "weapon": [
        "{wanderer} gives the {item} a few test swings by the fire and "
        "grins. 'Balanced. Nice.'",
        "{wanderer} straps the {item} across their back at once and "
        "strikes a heroic pose nobody asked for.",
    ],
    "head": [
        "{wanderer} puts on the {item} right away and checks the look in "
        "a puddle. Approved.",
        "{wanderer} tries the {item} on, tilts it to a jaunty angle and "
        "refuses to take it off again.",
    ],
    "chest": [
        "{wanderer} strips off their old shirt right there by the fire and "
        "wriggles into the {item}. It fits suspiciously well.",
        "{wanderer} pulls on the {item}, smooths it down and does a slow "
        "turn in the firelight. 'Well? How do I look?'",
    ],
    "gloves": [
        "{wanderer} slips into the {item} finger by finger, flexes both "
        "hands and sighs happily.",
        "{wanderer} pulls the {item} on and wiggles their fingers at the "
        "party. 'Snug.'",
    ],
    "feet": [
        "{wanderer} kicks off their worn-out shoes and slides into the "
        "{item}, then takes a few wobbly test steps around the fire.",
        "{wanderer} laces up the {item}, stamps twice on the ground and "
        "beams. 'Haven't had decent footwear in years.'",
    ],
    "accessory": [
        "{wanderer} fastens the {item} on at once and keeps glancing down "
        "at it, very pleased.",
    ],
    "lingerie": [
        "{wanderer} turns around, fiddles under their cloak for a moment – "
        "and the {item} is on. They look very satisfied with themselves.",
        "{wanderer} holds the {item} up to the firelight, blushes, and "
        "disappears behind a rock to try it on. The verdict: a thumbs up.",
    ],
    "crotch": [
        "{wanderer} wanders off behind a boulder with the {item}. A few "
        "grunts and adjustments later they return, walking a little "
        "differently – and grinning.",
    ],
    "consumable": [
        "{wanderer} uncorks the {item}, sniffs it and pockets it for a "
        "rainy day.",
    ],
    "couture": [
        "{wanderer} runs a hand over the {item}. 'Huh. {victim}. Met "
        "{victim} once.' A pause. 'Honestly? Makes a far better {label} "
        "than an adventurer.'",
        "{wanderer} reads the little tag: 'from {victim}'. 'Well, {victim} "
        "finally found a calling. Much better {label} than adventurer, "
        "that one.'",
        "'So this is what became of {victim},' {wanderer} murmurs, "
        "admiring the {item}. 'Never could fight. Fits beautifully, "
        "though.'",
    ],
}


WANDERER_THANKS = {
    "gloves": {
        "offer": "{wanderer} flexes their fingers in the new gloves and gives "
                 "{name} a wicked look. 'These deserve a proper test. Bend "
                 "over that log for a spanking – or let me show you just how "
                 "far these gloves can go.'",
        "accept": "{name} bends over the log. What follows is loud, "
                  "rhythmic and leaves {name} glowing – and then the gloves "
                  "go a good deal further than a spanking. The rest happens "
                  "under {wanderer}'s cloak, and {name} sits very carefully "
                  "for the remainder of the night.",
    },
    "feet": {
        "offer": "{wanderer} stretches out a leg and wiggles the new boots. "
                 "'Kneel down and show these some appreciation, and I'll "
                 "show you some in return.'",
        "accept": "{name} kneels by the fire and worships the boots with "
                  "great devotion – leather, laces, heels and all. {wanderer} "
                  "keeps the promise, and what happens after that stays by "
                  "the fire.",
    },
    "lingerie": {
        "offer": "{wanderer} strikes a pose in the new lingerie, firelight "
                 "dancing over the lace. 'Private show? Front-row seat, "
                 "no charge.'",
        "accept": "{name} takes the front-row seat. The show turns into a "
                  "lap dance, the lap dance into something much less "
                  "choreographed – and the lingerie does not stay on for "
                  "long.",
    },
    "crotch": {
        "offer": "{wanderer} adjusts the new piece with a grin and nods at "
                 "the bedroll. 'This needs breaking in. Care to help?'",
        "accept": "{name} helps break it in – thoroughly, enthusiastically "
                  "and more than once. The bedroll will never be the same.",
    },
    "chest": {
        "offer": "{wanderer} twirls in the new outfit, then plucks at the "
                 "laces. 'Getting into it was easy. Want to help me out of "
                 "it again?'",
        "accept": "{name} helps with the laces, slowly, one by one. Neither "
                  "of them is in any hurry to put anything back on.",
    },
    "decline": "{wanderer} shrugs, only a little disappointed. 'Your loss, "
               "{name}.'",
    "reward": "{name} feels thoroughly refreshed – fully healed and a "
              "little wiser (+{exp} EXP).",
    "not_you": "{wanderer} only has eyes for {target} right now.",
}
