VENUE_TEXTS = {
    "wedding": {
        "door": "💒 Music and laughter spill from a pair of tall double "
                "doors hung with black ribbons and white flowers. Somebody "
                "inside is roaring a toast, and a guard at the threshold "
                "waves you closer: 'Strangers are welcome. Strangers bring "
                "luck!'",
        "door_examine": "🔎 Black ribbons and white flowers frame the "
                        "doors. Through the crack you glimpse long tables, "
                        "a crowd and a very tall woman in black leather.",
        "intro": "💒 The corridor opens into a great hall hung with black "
                 "ribbons and white flowers. Long tables groan under "
                 "roasts and beer, and a hundred guests stand to cheer. At "
                 "the head of the hall a giant woman in black leather holds "
                 "the hand of a slim young man in a flower wreath. 'More "
                 "guests! Wonderful!' booms Baroness <<npc.baroness_ottilie_first>>. 'A wedding "
                 "without strangers is just a family dinner. Sit, eat, "
                 "talk to anyone you like.'",
        "options": "Actions: {options} ({seconds} s)",
        "examine": "🔎 Black ribbons, white flowers, long tables. <<npc.baroness_ottilie_first>> "
                   "stands in black leather with a sword at her hip. Her "
                   "boots gleam, a name carved into each heel: Aldric. "
                   "<<npc.emmerich_grimhold_first>> stands beside her in a flower wreath and "
                   "lace, one hand in hers. <<npc.old_brannock_first>> roars at the far "
                   "table, Sister <<npc.sister_merewyn_first>> blesses rings in a corner, and "
                   "a kitchen boy dodges elbows.",
        "sheath": "At her hip, under the skirt, an old sheath of dark leather "
                  "with silver eyelets hugs what she carries. It has been "
                  "oiled for thirty years and was once a husband.",
        "boots_0": "👢 <<npc.baroness_ottilie_first>>'s boots smell of leather and polish, with "
                   "something warm underneath.",
        "boots_1": "👢 The boots have clearly been worn all day. Warm, "
                   "salty, and unmistakably hers.",
        "boots_2": "👢 Sweat, old leather and a hint of the man they were "
                   "made from. Heavy, and impossible to ignore.",
        "emmerich_0": "A slim young man of eighteen in a white shirt and a "
                      "flower wreath. His ears are red, his fingers fidget "
                      "with the lace of his collar, and he keeps glancing "
                      "at his mother's boots, then away. He seems to know "
                      "exactly what tonight is for.",
        "emmerich_1": "<<npc.emmerich_grimhold_first>> has stopped pretending to be calm. Every "
                      "time <<npc.baroness_ottilie_first>> shifts, warm air from her boots drifts "
                      "past him, and his breath catches. He swallows, pulls "
                      "his shirt lower over his hips, and smiles at "
                      "nothing. He walks with small, careful steps, thighs "
                      "pressed together, as if whatever he wears beneath "
                      "his trousers makes every movement a secret. When he "
                      "bends, a strip of white lace shows at his hip. Tonight he will be taken for the "
                      "first time, and the whole hall knows it.",
        "emmerich_2": "<<npc.emmerich_grimhold_first>> is flushed to the collar. The heat and "
                      "scent of the boots hang around him like steam, and "
                      "he leans toward them without noticing. His eyes are "
                      "glassy, his hands tremble, and when <<npc.baroness_ottilie_first>> squeezes "
                      "his shoulder he nearly whimpers. 'Tonight,' he "
                      "whispers to no one. 'Tonight Mom will make me "
                      "hers.' Under the thin white shirt the outline of a "
                      "lace corset is plain to see, and a strip of white "
                      "stocking and garter shows at his hip. A bride, you "
                      "realise, not a groom: wreath, lace, corset and "
                      "stockings, all chosen by the woman who gave birth "
                      "to him, and he wears them like a gift. A flat steel "
                      "cage is outlined under the thin cloth at his hips, "
                      "and when he shifts he winces and blushes: something "
                      "else is seated deep inside him, and it will stay "
                      "there until the one person with the key decides "
                      "otherwise.",
        "eat": "🍖 The party takes a place at the long table. Roast, bread, "
               "beer and a slice of the Baroness's own cake. Everyone "
               "leaves a little warmer than they arrived.",
        "congratulate": "<<npc.baroness_ottilie_first>> crushes {name}'s hand in a handshake that "
                        "rattles bones. 'A toast from strangers! The "
                        "best kind!' <<npc.emmerich_grimhold_first>> blushes and presses a small "
                        "lavender sachet into {name}'s palm. 'For luck. "
                        "Please.'",
        "gift": "The Baroness tosses a purse of {gold} gold across the "
                "table. 'A gift for the guest!'",
        "depart": "The party leaves the hall. Behind them the guests roar "
                  "a toast, and <<npc.baroness_ottilie_first>>'s laughter fills the corridor "
                  "for a long time.",
    },
}


GUEST_STAGES = {
    "baroness_ottilie": {
        1: {"work": ("'Thirty years I led men into fire. Tonight I lead "
                      "one boy to bed. Both take courage.'",
                      "'You fight like someone who wants to live. Good. "
                      "Stay for the cake.'"),
            "town": ("'Another toast! The hall is warm and my boy has not "
                     "stopped smiling. Let them stare.'",
                     "'They talk, of course they talk. I let them talk "
                     "into their beer.'"),
            "self": ("'I brought him into this world. I fed him, I trained "
                     "him, I buried the man who made him. And tonight, in "
                     "front of all of you, I make him mine.'",
                     "'He thinks I do not notice him watching my boots. "
                     "I notice everything.'",
                     "'I put the key on a chain around my neck this "
                     "morning. My boy knows where it is. He looks at it "
                     "every time he thinks I am not watching.'",
                     "'A Grimhold marries her boy the day he turns "
                     "eighteen. Aldric stood where Emmerich stands now. "
                     "Aldric's father never got the chance to stand "
                     "anywhere. He lies much closer to me.' She pats her "
                     "hip, where dark leather creaks.")},
        2: {"work": ("'The contracts are done. The only banner I care for "
                      "now is the one waiting in my bedroom.'",
                      "'Drink up. Tomorrow you can tell everyone you were "
                      "at the best wedding of the age.'"),
            "town": ("'The night is long and I have plans for it. Nobody "
                     "leaves this hall before the first dance is over.'",
                     "'Look at them. All of them staring at my husband. My "
                     "wife. My boy. Let them.'"),
            "self": ("'My boy will be my wife by morning. Do not look so "
                     "shocked. Everyone here knows who is in charge. He "
                     "knows it better than any of you.'",
                     "'He is trembling. Good. I would not want him to be "
                     "calm. Calm is for funerals.'",
                     "'The key stays with me until tonight. Only I will "
                     "unlock him. Only I will take out what is inside "
                     "him. That is what a husband gives his wife on her "
                     "wedding day: everything.'",
                     "'Aldric's father became my sheath, Aldric became my "
                     "boots. What my boy will become, when his time comes, "
                     "I have not decided. Gloves, perhaps. He has such "
                     "lovely hands.' She smiles at the ceiling.")},
    },
    "emmerich_grimhold": {
        1: {"work": ("'Mom laced me in herself this morning. She says a "
                      "groom should stand straight.'",
                      "'I made the sachets last night so my hands would "
                      "stop shaking. They did not.'"),
            "town": ("'Everyone keeps looking at me. I think they can "
                     "tell.'",
                     "'<<npc.old_brannock_first>> winked at me. I am not sure what he "
                     "knows.'"),
            "self": ("'Everyone expects me to be the groom. But tonight I "
                     "will not be the one who takes. Mom will take me. I "
                     "think I have always known.'",
                     "'I am wearing something under this shirt. Mom "
                     "picked it out. Please do not look.'",
                     "'I can still smell her on my lips. I do not mind. I "
                     "think I even like it.'",
                     "'Mom put something on me this morning. A cage. And "
                     "a... plug. She said I had to wear them to the "
                     "feast. She kept the key.'",
                     "'Father was Mom's boy before he was her husband. "
                     "That makes me her son and her grandson. I try not "
                     "to do the sums. Please never call her Grandmother "
                     "in front of her.'")},
        2: {"work": ("'I cannot hold the baskets any more. My hands "
                      "tremble. <<npc.tobin_kitchen_first>> took them.'",
                      "'The lavender was for luck. I think I need all of "
                      "it tonight.'"),
            "town": ("'Everyone is looking. I keep telling myself it is "
                     "only the music.'",
                     "'Sister <<npc.sister_merewyn_first>> blessed me twice. I think she meant "
                     "it as a warning.'"),
            "self": ("'My first time. With her. As the one who is... "
                     "taken. I should be afraid, but I am not. The corset "
                     "helps. It feels like she is already holding me.'",
                     "'She gave me life. Now she gives me this. A new name "
                     "for tonight. Mom says I will be her wife. I think I "
                     "want that.'",
                     "'She smells like the stables back home,' he "
                     "murmurs. 'I could stay here all night, "
                     "Mistress.'",
                     "'I cannot take it off. Only she can. Every step "
                     "reminds me. I... I keep hoping the evening goes "
                     "faster.'")},
    },
    "old_brannock": {
        1: {"work": ("'Mark my words, that boy is nervous as a bride. Well. "
                      "He is the bride. Ha!'",
                      "'I carried her banner for thirty years. Tonight I "
                      "carry her bride's veil. Life is strange.'"),
            "town": ("'Every table has been told to look away at midnight. "
                     "I look at midnight. I always look.'",
                     "'Did you see the lace? At his hip? Do not tell "
                     "her I said.'",
                     "'Aye, I saw how the boy walks. Careful. Like a man "
                     "carrying water in his pants. <<npc.baroness_ottilie_first>> always did "
                     "like a locked door.'"),
            "self": ("'I drink to forget what I saw at the old Lord's "
                     "funeral. It does not work.'",
                     "'He walks taller than he has in years. In heels, "
                     "under the shirt. I saw the stockings.'",
                     "'See that dark leather at her hip? That is the "
                     "first husband. Useless alive, a fine fit dead. Her "
                     "second husband she raised herself, and he went "
                     "into her boots. Do not tell her I told you.'")},
        2: {"work": ("'The banner is hers, the bed is hers, the boy is "
                      "hers. Only the beer is mine.'",
                      "'I have seen men go into that bedroom. I have not "
                      "seen all of them come out walking straight.'",
                      "'Equine, the old Lord used to say, and he said it "
                      "with a prayer. Every wedding night, same prayer.'"),
            "town": ("'A mother, a bride, a son. Only <<npc.baroness_ottilie_first>> could.'",
                     "'By morning the whole camp will have heard. By "
                     "noon, the kingdom.'"),
            "self": ("'I loved her once. Now I toast her happiness and "
                     "pretend not to cry.'",
                     "'If the boy screams tonight, it is a good scream. "
                     "That is what I tell myself.'")},
    },
    "sister_merewyn": {
        1: {"work": ("'The vows are done. What happens after is not mine "
                      "to bless. Or forbid.'",
                      "'I blessed the rings. I did not bless the room.'"),
            "town": ("'The boy asked me for confession. He said he was not "
                     "afraid. I believed him. That is the troubling "
                     "part.'",
                     "'Everyone here knows what tonight is. It is "
                     "strange how loud silence can be.'"),
            "self": ("'I told him it was not too late to refuse. He smiled "
                     "and said he did not want to.'",
                     "'I should leave. I stay. The gods will have a "
                     "word.'",
                     "'He asked me to bless something I will not name. I "
                     "blessed his hands instead. They tremble.'",
                     "'I married her to Aldric, too. Same vows, same "
                     "question, a different boy. The first time she asked "
                     "me nothing. This time she asked me to hurry.'")},
        2: {"work": ("'Pray for him, if you can. Tonight he will need "
                      "more than a blessing.'",
                      "'I will say the prayers for the dead and the "
                      "newly wed together. It saves time.'"),
            "town": ("'A son, a bride, a mother. The gods keep stranger "
                     "books than I do.'",
                     "'The cook is already sending wine upstairs. Do not "
                     "ask me to carry it.'"),
            "self": ("'I envy him a little. He knows exactly who he "
                     "belongs to.'",
                     "'If I were braver, I would stop this. If I were "
                     "honest, I would not.'")},
    },
    "tobin_kitchen": {
        1: {"work": ("'The cook is sending extra wine up to their room. "
                      "Extra. Do not ask me why.'",
                      "'The roast is gone, the beer is going. I am "
                      "sweating through my apron.'"),
            "town": ("'They say the Baroness already picked out the "
                     "bedding. White. Very white.'",
                     "'I heard <<npc.old_brannock_first>> tell three people about the "
                     "lace. Three!'",
                     "'He asked for a cushion for his chair. A cushion! "
                     "He blushed so hard I nearly dropped the tray.'"),
            "self": ("'<<npc.emmerich_grimhold_first>> smiled at me today. He never does. I "
                     "think he is happy. And scared.'",
                     "'I wish somebody loved me like that. Even if it "
                     "was strange.'")},
        2: {"work": ("'They told us to stop serving at midnight. Everyone "
                      "knows why. Nobody says it.'",
                      "'I will be scrubbing the hall until dawn. The "
                      "bedroom is not my problem. Thank the gods.'"),
            "town": ("'The whole kitchen is whispering. Even the cook "
                     "blushes.'",
                     "'There is a bet on how long the bed lasts. I put "
                     "two coins on the morning.'"),
            "self": ("'If anyone asks, I did not see anything. I did not "
                     "hear anything.'",
                     "'I will bring them breakfast tomorrow. I hope he "
                     "is smiling.'")},
    },
}


EAT_CHALICE = (
    "While the guests fill their plates, <<npc.baroness_ottilie_first>> lifts a silver chalice "
    "from the table and sets it beneath her skirt. A deep, rough groan "
    "rolls out of her chest, 'Hhhnnh... gods...', and the cup fills with a "
    "steady, audible stream. She hands it to <<npc.emmerich_grimhold_first>> still steaming. "
    "'Drink, my wife. You will need your strength tonight.' He drinks it "
    "down with his eyes lowered. 'Thank you, Mistress.'",
    "'Hold this,' <<npc.baroness_ottilie_first>> says, and passes <<npc.emmerich_grimhold_first>> a goblet beneath the "
    "table's edge. A low, gravelly moan answers from deep in her chest, "
    "'Ahh... fuck, that is good...', and the sound beneath the table is "
    "unmistakable. 'All of it. Do not waste what I give you.' He drinks "
    "without a word, his throat working. 'Thank you, Mistress. It is very "
    "kind.' She strokes his hair as if he were a pet. 'Good boy.'",
    "<<npc.baroness_ottilie_first>> stands, silver cup in hand, and steps behind her chair for a "
    "privacy that nobody believes. A long, growling sigh drifts across the "
    "hall, 'Mmmh... hhhaah...', then she returns and sets the warm cup "
    "before her groom. 'Drink, my wife. Show them what a good bride "
    "does.' <<npc.emmerich_grimhold_first>> lifts it with both hands and drinks, flushed to the "
    "collar. 'Thank you, Mistress,' he says, and licks his lips without "
    "noticing.",
    "'Hungry, my wife?' <<npc.baroness_ottilie_first>> asks, and slips a chalice under her skirt "
    "right there at the table. A heavy, male moan escapes her, 'Ngh... "
    "ahh, yes...', and the guests nearest to her go very quiet. She holds "
    "the cup out to him, steaming. He kneels beside her chair to take it, "
    "drinks it down slowly, and kisses her hand. 'Thank you, Mistress. I "
    "am grateful.' 'I know you are.'",
    "Without a word, <<npc.baroness_ottilie_first>> takes <<npc.emmerich_grimhold_first>>'s own wedding goblet, tucks it "
    "beneath her skirt, and lets out a thick, bass groan, 'Hhhh... fuck, "
    "finally...', that rolls through the table like thunder. When she "
    "gives it back, the goblet is warm and full to the brim. 'Your wine, "
    "wife.' He drinks it with both hands, blushing. 'Thank you, Mistress. "
    "I will not spill a drop.' 'See that you do not.'",
)

EAT_REACTIONS = (
    "<<npc.old_brannock_first>>: 'Drinking like a good wife. <<npc.baroness_ottilie_first>> always did know how to "
    "feed what she owns.'",
    "Sister <<npc.sister_merewyn_first>>: 'I did not see that. I will pray as if I had not "
    "seen that.'",
    "<<npc.tobin_kitchen_first>>: 'The cook says the goblet is going straight to the bin. I did "
    "not ask which goblet.'",
)

DANCES = (
    "The musicians strike up a slow waltz and the hall clears a circle. "
    "<<npc.baroness_ottilie_first>> sweeps <<npc.emmerich_grimhold_first>> into her arms as if he weighed nothing. He "
    "barely reaches her collarbone, so his face ends up pressed between "
    "her heavy breasts, warm and flushed, while his slender hands settle "
    "on the broad swell of her hips and rest on her backside as she steers "
    "him. 'Breathe, my wife,' she murmurs. 'Yes, Mistress,' he whispers "
    "into her skin, 'thank you.' When the last note fades, she kisses the "
    "top of his head. 'Now the night is ours.'",
    "<<npc.baroness_ottilie_first>> does not ask. She takes his hand, pulls him in, and the floor "
    "belongs to her. Every turn, his cheek slides against the cleavage of "
    "her black leather dress, and his hands hold on to her hips as if she "
    "were the only fixed thing in the room. 'Good,' she says, low. 'Stay "
    "close.' 'Yes, Mistress. Thank you for leading me.' The guests clap in "
    "time. Somebody whistles. <<npc.emmerich_grimhold_first>> does not lift his head until the "
    "music stops.",
    "A stately dance, the kind a banner would lead. <<npc.baroness_ottilie_first>> holds him "
    "against her chest, her chin on his hair, her hands splayed on his "
    "back, and his hands rest on her broad rear as she turns him through "
    "every step. 'Look at them,' she says softly. 'Look how they envy "
    "you.' 'Thank you, Mistress,' he breathes. 'Thank you for choosing "
    "me.' Her laugh rumbles through her ribs and through him. 'I always "
    "will.'",
    "He is shaking. She feels it and tightens her hold, pressing his face "
    "deep between her breasts until his breath comes in warm, damp gasps. "
    "His hands slide down her sides and settle on her hips, then, daring, "
    "on the solid curve below. 'Easy,' she murmurs. 'You are doing well.' "
    "'Thank you, Mistress,' he says into her cleavage. 'I will be good "
    "tonight. I promise.' 'I know,' she says. 'That is why I chose you.'",
)

DANCE_REACTIONS = (
    "<<npc.old_brannock_first>>: 'Gods. She danced him like a banner in the wind.'",
    "Sister <<npc.sister_merewyn_first>>: 'I have blessed forty dances. I have never seen one "
    "end like that.'",
    "<<npc.tobin_kitchen_first>>: 'He did not step on her feet once. I counted.'",
    "<<npc.old_brannock_first>>: 'Gods. She smells like a battlefield and a stud farm in "
    "one. And the lad looks like he is in heaven.'",
    "<<npc.tobin_kitchen_first>>: 'I stood by the doorway and still caught it. It was... a lot "
    "of horse.'",
    "Sister <<npc.sister_merewyn_first>>: 'I have blessed stables that smelled less like a "
    "stable.'",
    "<<npc.old_brannock_first>>: 'The lad cried the whole dance and never let go. That is "
    "love, or the stench. Hard to tell.'",
)

NIGHTS = (
    "The music thins out as <<npc.baroness_ottilie_first>> lifts the key from her throat. 'Come, "
    "my wife.' The hall falls silent and watches <<npc.emmerich_grimhold_first>> cross it in his "
    "white shirt, one careful step at a time. The door closes behind "
    "them, and for a moment there is nothing but the muffled thud of "
    "<<npc.baroness_ottilie_first>>'s boots. Then comes the first sound: a gasp, soft and "
    "startled, followed by a low, steady rhythm that does not slow. "
    "Through the wall the guests hear everything. His cries climb, break "
    "and climb again, 'Mistress... Mom... please...', and her answer is a "
    "deep, patient growl: 'Hhhnnh... take it. You are mine tonight.' It "
    "goes on for a very long time. By the time the hall resumes its "
    "toasts, nobody looks at the door.",
    "<<npc.baroness_ottilie_first>> opens the cage with the key from her throat, slowly, and "
    "draws out the plug that only she may remove. <<npc.emmerich_grimhold_first>> holds his "
    "breath. 'Thank you, Mom.' 'Mistress, in front of the guests. You "
    "know that.' 'Yes, Mistress.' The door shuts, and what follows comes "
    "through the wall in pieces: the bed frame knocking, his high, "
    "breaking cries, 'Ah! Mistress! Harder, please, thank you, "
    "thank you...', and over it all her heavy bass groans, 'Fuck... "
    "ahh... that is it, my wife... take all of me.' Nobody in the hall "
    "says a word. Nobody leaves either.",
    "'Last time I ask,' <<npc.baroness_ottilie_first>> says at the bedroom door, and lifts "
    "<<npc.emmerich_grimhold_first>>'s chin. 'Do you want this?' 'Yes, Mistress.' A pause, then "
    "softer: 'Yes, Mom.' She carries him in like a bride. Through the "
    "wall the hall hears his first startled gasp, then the rhythm: hard, "
    "relentless, her boots planted on the floor. His voice rises to a "
    "sob of joy, 'Mom! Mistress! Thank you, thank you...', and she "
    "answers with a long, thunderous moan, 'Nnngh... mine... all mine.' "
    "It does not stop until the candles burn low.",
)

NIGHT_MORNING = (
    "In the morning <<npc.emmerich_grimhold_first>> walks out in white lace and stockings, "
    "trembling and smiling, one hand in his mother's. He is a bride now, "
    "and he has never looked happier. <<npc.baroness_ottilie_first>> rests her free hand on his "
    "belly. 'The heir,' she says quietly. 'Mine. Ours. It took.' "
    "<<npc.emmerich_grimhold_first>> covers her hand with his and nods, glowing. <<npc.baroness_ottilie_first>> gives "
    "the party breakfast and a purse of {gold} gold. 'For the guests who "
    "stayed. Come back for the first anniversary.'",
)

NIGHT_HINTS = {
    "emmerich_eat": "His lips are shiny, and he keeps licking them. The "
                    "smell of the chalice still clings to his mouth.",
    "emmerich_dance": "His eyes are red and watering, and he keeps "
                      "blinking, but he is smiling. He smells of her, "
                      "leather, sweat and stable.",
}


EAT_SMELLS = (
    "<<npc.old_brannock_first>> sniffs the air. 'I smell wine. Then I smell something else. "
    "Then I stop asking.'",
    "Sister <<npc.sister_merewyn_first>> wrinkles her nose. 'The wine smells... different "
    "tonight. I will not look at the cup.'",
    "<<npc.tobin_kitchen_first>>, carrying a tray past: 'It smells like the kitchen after a long "
    "shift. Warm. Salty. I should not know that.'",
    "<<npc.baroness_ottilie_first>> breathes in, grinning. 'A good vintage. Nobody else gets a "
    "glass.'",
)

DANCE_SMELLS = (
    "Up close she smells of leather, sweat and warm hay, a heavy, animal "
    "musk that rolls off her with every turn.",
    "The heat of the dance has her steaming. The smell is thick and "
    "earthy, almost a stable on a summer evening, and <<npc.emmerich_grimhold_first>> breathes it "
    "in without meaning to.",
    "Her skin smells of horse and iron and warm leather. He closes his "
    "eyes and his knees nearly give.",
    "Between sweat, boots and something far more primal, the air around "
    "her is heady enough to make the nearest guests step back, and "
    "<<npc.emmerich_grimhold_first>> lean in.",
)

DANCE_TEARS = (
    "Her musk is so thick that <<npc.emmerich_grimhold_first>>'s eyes begin to water. He blinks "
    "hard, breathes it in anyway, and presses closer. 'Thank you, "
    "Mistress,' he chokes out, tears on his lashes.",
    "The stable-heat of her skin stings his eyes. They shine wet in the "
    "lamplight, but he does not turn his face away from her chest. 'It "
    "is... a lot, Mistress,' he whispers. 'Thank you for it.'",
    "Each turn, the smell hits him harder, leather, sweat and horse, and "
    "his eyes fill and spill. He keeps dancing, blushing and sniffling. "
    "'Please do not stop, Mistress.'",
)

DANCE_TEARS_OTTILIE = (
    "'Crying already, my wife?' <<npc.baroness_ottilie_first>> tilts his chin up and kisses the "
    "tears away. 'Good. Breathe me in. You will smell me for a week.'"
)
