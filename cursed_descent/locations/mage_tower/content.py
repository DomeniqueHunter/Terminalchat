MAGE_ID = "npc-mage-tower"
ENCHANT_BONUS = 10
ENCHANT_PRICE = 10000
SUPER_BONUS = 15
SUPER_PRICE = 15000
MALUS_RANGE = (5, 10)
EFFECTS = ("soul_hunger", "stat_malus", "allure_malus")
SLEEP_PRICE = 300
POTIONS = ("potion_large", "mana_potion", "elixir")
POTION_MARKUP = 3
REAL_PRICE = 4000
REAL_SEX_PRICE = 2000
IMPLANT_SHARE = 0.5
PART_WORDS = {"bust": "breasts", "butt": "ass", "endowment": "cock",
              "balls": "balls"}

VENUE_TEXTS = {
    "mage_tower": {
        "intro": "🧙 A crooked tower in the corridor, humming with old "
                 "magic. An ancient mage waits at the door, his robe "
                 "straining at the front. 'Come in. Everything has a "
                 "price.'",
        "door": "The door stands open. Warm light and a faint smell of "
                "ozone spill out.",
        "enter": "You step inside. The door closes behind you with a "
                 "soft click. 'Welcome. Look around.'",
        "options": "Actions: {options}",
        "examine": "🔎 Shelves of bottled lightning, a bed nobody has "
                   "slept in for a century, and the mage's smile.",
        "depart": "The party leaves the tower. The door closes itself "
                  "behind them.",
        "poor": "'{price} gold, {name}. Not a coin less.'",
        "once": "'One working per visit, {name}. The tower needs its "
                "evening. Come back on the next road.'",
        "empty": "{name} carries nothing the mage would bother with.",
        "enchant": "The mage weaves a slow spell around {item}. It flares and "
                "settles: {new}. 'Handle with care.'",
        "super": "The mage weaves a slow spell around {item}. It flares and "
                 "settles: {new}. 'A fine payment.'",
        "effect_soul_hunger": "The new item hums with hunger. It may keep "
                              "your soul if you fall with it.",
        "effect_stat_malus": "The magic took its share: {stat} -{amount}.",
        "effect_allure_malus": "The magic took its share: allure "
                               "-{amount}.",
        "potion": "{name} buys {item} for {price} gold.",
        "full": "{name}'s bag is full.",
        "sleep": "🛏 The party sleeps in the old bed, one after another. "
                 "Everybody wakes healed and rested.",
        "slept": "The bed is still warm.",
        "offer": "'I could make that real,' he says. 'Same size, living "
                 "flesh. {price} gold. Or...' he smiles, 'less gold, and a "
                 "little time with me.'",
        "real_sex_intro": "'Hold still. This part of the spell needs "
                          "closeness.'",
        "real": "He draws a slow circle in the air over {name}'s {part}. "
                "The implant melts into warmth, flesh now, same size, and "
                "it trembles when touched. 'There. Honest at last.'",
        "real_none": "'Nothing of yours needs that, {name}. Everything "
                     "there is already honest.'",
        "sleep_poor": "'A night costs {price} gold, {name}.'",
    },
}

LIFT = (
    "The mage flicks two fingers and {name} rises off the floor, "
    "weightless, however heavy and big {name} is.",
    "'Stay.' The air closes around {name} like a hand, and the old man "
    "turns {name} to face away from him.",
    "Gear and clothes slide off {name} on their own and fold themselves "
    "onto the chair, while the mage walks a slow circle.",
    "'Up.' {name} is lifted and folded in mid-air, feet behind the "
    "head, a full nelson no muscle can break.",
)
SCENE = (
    "The mage spreads {name}'s cheeks with a thought and rests his huge "
    "head against the tight entrance. He pushes in slowly, inch by inch, "
    "humming. 'There. See? You were made for it.'",
    "A warm slick spell coats {name}'s ass, and the mage sinks in all at "
    "once with a long, satisfied groan. He holds there, balls pressed "
    "against {name}, savoring the stretch. 'Don't clench. You can't "
    "anyway.'",
    "He takes {name} from behind, one hand on the small of the back, the "
    "other still weaving magic. Each thrust is long and unhurried, and "
    "the spell keeps {name} open, wet and wanting more.",
    "The mage lowers {name} onto his lap in mid-air. {name} slides down "
    "his thick shaft, helpless, with the spell setting the rhythm: up, "
    "hold, down. He murmurs in {name}'s ear, 'Good. Take all of it.'",
    "'Let us see how much you can hold.' The mage pushes in deep and "
    "stops, and {name} feels the length twitch and swell inside. Then he "
    "starts to move, slowly at first, then harder, while {name}'s own "
    "body answers against all will.",
    "He folds {name} forward in the air and holds {name} there by the "
    "hips with invisible hands. The mage pounds into {name}'s ass with "
    "the patience of an old man and the stamina of a young god. 'Yes. "
    "Just like that.'",
    "The spell makes every nerve in {name}'s ass sing. The mage fucks "
    "{name} slowly, each stroke dragging along it, and {name} cannot help "
    "moaning. 'Hm. You enjoy it more than you will admit.'",
    "At the end he sinks in to the base and groans, flooding {name} deep "
    "with a long, hot load. He stays buried until the last pulse, then "
    "lowers {name} gently to the floor. 'Very good. A fine payment.'",
    "With a lazy gesture the mage folds {name} in mid-air: arms hooked "
    "behind the neck, legs pulled up and back until {name}'s feet rest "
    "behind {name}'s own head, a full nelson with nowhere to go. Every "
    "hole on display, and the mage steps close. 'Flexible. I like that.'",
    "{name} hangs helpless in the air, folded into a full nelson, "
    "ankles locked behind the head. The mage lines up with {name}'s ass "
    "and pushes in slowly, all the way, while the spell turns {name} "
    "slowly like meat on a spit. 'Hold still. Not that you can.'",
    "The folded body floats at exactly the right height. The mage grips "
    "{name}'s thighs and takes {name} in the full nelson, hard and deep, "
    "each thrust rocking {name} back and forth in the air. 'Look at "
    "that. Made for it.'",
)
AFTER = (
    "'Your gear hums now. It will serve you well.'",
    "'A pleasure. Come again when you have more to offer.'",
)

MOAN_EARLY = (
    "{name} gasps as he fills {name}, a shaky \"Ah... nngh...\" escaping "
    "through clenched teeth.",
    "A low, helpless \"Oh gods...\" slips out of {name} with every inch.",
    "{name} bites down on a whimper, but it breaks anyway: \"Ah! Too... "
    "too big...\"",
    "\"Hnngh... slow... please slow...\" {name} pants, and the mage does "
    "not slow down.",
)
MOAN_MID = (
    "\"Ah! Ah! Yes... right there...\" {name} cries out, hips jerking "
    "against the spell's grip.",
    "Moans spill out of {name} in time with the thrusts, wet, broken, "
    "louder each time. \"Ohhh... fuck... deeper...\"",
    "{name} arches in the air, whimpering, \"Mmmh... don't stop... don't "
    "you dare stop...\"",
    "\"Nngh! You... bastard...\" {name} moans, and the word turns into a "
    "gasp halfway.",
)
MOAN_PEAK = (
    "{name}'s voice breaks into a long, shuddering cry: \"Aaah! I'm... "
    "I'm going to...\" The spell tightens and {name} comes helplessly.",
    "A scream of pleasure tears out of {name} as the mage hits the "
    "deepest point: \"Yes! Yes! Fill me!\"",
    "{name} sobs his name, \"<<mage_tower.owner_short>>... <<mage_tower.owner_short>>...\", and shakes in the air, "
    "tight and trembling around him.",
    "\"Oh gods, oh gods, ahhh!\" {name} clenches around him, twitching, "
    "and the moan dies into a ragged whisper.",
)
MOCK = {
    "bust": (
        "The mage's eyes drop to {name}'s chest and he laughs softly. "
        "'Silicone. How brave.' His palm lands on one breast with a sharp "
        "clap and the whole thing wobbles. 'Hollow, and you paid for it.'",
        "'Oh, that is not yours, is it?' <<mage_tower.owner_short>> circles {name} slowly, then "
        "smacks both breasts, one after the other. The sound is wet and "
        "tight. 'Firm. Too firm. Nothing real is that polite.'",
        "<<mage_tower.owner_short>> flicks {name}'s nipple with a ringed finger, then slaps the "
        "breast hard enough to leave a red handprint. 'Bought, not grown. "
        "Don't pout, it suits you.'",
    ),
    "butt": (
        "'A shop-made ass,' <<mage_tower.owner_short>> says, and cracks his palm across "
        "{name}'s butt. It barely moves. 'Hard as a saddle. Who sold you "
        "that?'",
        "<<mage_tower.owner_short>> steps behind {name} and spanks one cheek, then the other, "
        "listening. 'No give. Pure filler.' He grins. 'Turn around, let me "
        "see the whole fraud.'",
        "A slap lands on {name}'s ass, loud in the stone room. 'Implants,' "
        "<<mage_tower.owner_short>> sighs, rubbing his palm. 'Such a pretty lie.'",
    ),
    "endowment": (
        "<<mage_tower.owner_short>> glances at {name}'s crotch and arches a brow. 'Added "
        "length. Did they at least give you a receipt?' He slaps it "
        "sideways with two fingers and laughs as it bounces.",
        "'Bolted on,' <<mage_tower.owner_short>> says, weighing {name}'s cock in his palm "
        "before smacking it lightly. 'More engineering than flesh.'",
        "<<mage_tower.owner_short>> flicks {name}'s cock with a fingernail, then slaps it flat "
        "against the thigh. 'Hung by prescription. Adorable.'",
    ),
    "balls": (
        "<<mage_tower.owner_short>> cups {name}'s balls, squeezes and smirks. 'Plastic "
        "marbles.' A quick slap makes {name} flinch. 'Don't worry, they "
        "bounce.'",
        "'Filled, not grown,' <<mage_tower.owner_short>> murmurs, rolling them in his palm, "
        "then smacks them once. 'Heavy, though. I'll give you that.'",
        "<<mage_tower.owner_short>> taps {name}'s balls with two fingers like testing fruit, "
        "then slaps them. 'Hollow ring. How embarrassing for you.'",
    ),
}
