PLACE = ("🍰 The Fat Ass Café – Madame Bertha serves tea, cake and ladies "
         "who sit down heavily. Gentlemen are welcome as furniture only.")
OFFER = ("Ladies take a seat or a stool, gentlemen work the floor as "
         "furniture – see the list below.")
OWNER = "Madame Bertha"
CLOSED = "The Fat Ass Café is shut while you are in the dungeon."

SESSION_LINES = {
    "server": [
        "You carry a three-tier cake stand through a forest of skirts.",
        "A lady rests her tea on a stool, then on you. You hold still.",
        "You refill a lady's cup without once looking up. Good boy.",
        "Somebody wants a second slice, and a third. You keep running.",
        "A lady pinches your cheek and tips in cream puffs.",
        "You dodge a swinging hip with a full teapot and no spill.",
    ],
    "trainer": [
        "You break in a nervous new stool with patient, firm words.",
        "You teach a trembling lad how to hold under two hundred kilos.",
        "You test a stool's wobble with your own weight, twice.",
        "You pad a creaking stool and show it how to breathe.",
        "You demonstrate the proper 'welcome' pose to a pale trainee.",
        "You straighten a stool's spine. It thanks you, in gasps.",
    ],
    "baker": [
        "You knead dough for the ladies' favourite triple-cream roll.",
        "You glaze a tray of puffs and sneak exactly one.",
        "You whisk cream until your arms burn and the oven sings.",
        "You pull a perfect cheesecake out of the oven. Bertha sniffs "
        "approvingly.",
        "You stir the secret batter. Bertha says nothing, ever, about it.",
        "You ice a cake in the shape of a very round moon.",
    ],
    "usher": [
        "You guide a lady to her favourite stool with a flourish.",
        "You hold a lady's hand and her bag while she lowers herself.",
        "You rearrange the stools so everyone has a clear view.",
        "You bow, point, and say 'Seat of honour, madame.' It works.",
        "You smooth a way through the crowd for a very wide lady.",
        "You call out the 'next table, please' without a stutter.",
    ],
    "cleaner": [
        "You scrub crumbs and cream from every cushion.",
        "You polish the brass legs of the seat of honour.",
        "You mop the floor under a particularly dramatic sneeze.",
        "You air out the cushion room and open every window.",
        "You wipe down the stools, one by one, with soapy cloths.",
        "You pick a lost shoe out of an enormous armchair.",
    ],
}

SEAT_INTRO = ("You lie back on the cushion bench, head at the edge, ready for "
              "the first lady to sit. Madame Bertha taps the wood with her cane: "
              "'Hold well, dear. [hold] to carry on, [quit] to stand up "
              "– that is your safeword, and it always works.'")
SEAT_NO_SHIFT = ("You are not on a seat shift. [job cafe seat] starts one.")
SEAT_DONE = "The last lady stands up. Bertha counts your tips."
HOME_DONE = ("{name} finally stands, smooths her skirt and pats your cheek. "
             "'Same time next week, dear.' No money changes hands.")
NO_HOME_SAFEWORD = ("There is no safeword in her house: only she decides "
                    "when it is over. Hope for her mercy – lick, kiss, pat "
                    "or struggle.")
SEAT_QUIT = ("You tap out. Bertha waves two stool-boys over: 'Good enough "
             "for today, dear.'")

GUEST_NAMES = (
    "Lady Mabel", "Dame Hortensia", "Countess Pia", "Madame Odette",
    "Baroness Gundula", "Mrs. Fenwick", "Lady Rosalind", "Dame Agatha",
    "Duchess Beatrix", "Miss Cordelia", "Lady Winifred", "Madame Solange",
)

GUEST_INTRO = "{name} arrives ({weight} kg, {butt} cm of rear) and eyes your stool."
LIGHT = "She looks light. This should be easy."
HEAVY = "She looks like a proper load."
CRUSHING = "She looks like a landslide in a skirt. Think hard."

HOLD_EASY = [
    "{guest} settles in, hums, and your head sits snug between her cheeks. You carry her without trouble.",
    "{guest} wriggles into place, her cheeks closing around your head, and sips her tea. You hold.",
    "{guest} sits with a happy sigh and a little bounce. You stay steady.",
]
HOLD_HARD = [
    "{guest} sinks all the way down, your head swallowed between her cheeks. Your ribs complain, but you hold.",
    "{guest} leans back with a grunt of delight. Stars dance, you endure.",
]
HOLD_BAD = [
    "{guest} shifts and everything goes dark for a heartbeat. You gasp.",
    "{guest} laughs and settles deeper, her cheeks sealing around your head. You barely get a breath in.",
]
HOLD_WARN = "⚠ You are close to blacking out. [hold] if you dare, [quit] to stand up."

RIDER_WELCOME = ("{rider} lowers herself onto {seat} with a satisfied "
                 "sigh. Bertha watches from the counter and nods.")
RIDER_TO_SEAT = ("{rider} ({weight} kg, {butt} cm) sits down on you, your head wedged between her cheeks. "
                 "You cannot get up until she does – [hold] to carry on.")
RIDER_HOLD = [
    "{rider} wriggles comfortably and you hold, snug under her weight.",
    "{rider} sighs and leans back. You hold out, warm and flustered.",
    "{rider} bounces once, softly. You hold, grinning into her soft flesh.",
]
RIDER_RISE = "{rider} rises, smoothing her skirt. {seat} breathes again."
RIDER_GONE = "The stool is gone. {rider} stands, a little disappointed."

WITNESS_SEAT = ("You see {actor} lie back on the cushion bench, waiting for "
                "the first lady to sit.")
WITNESS_GUEST = "You watch {guest} lower {weight} kg onto {{actor}}'s face."
WITNESS_GUEST_BIG = ("You watch {{actor}} disappear under {guest}'s enormous "
                     "rear.")
WITNESS_RIDER = "You see {actor} sit down on {seat}'s face."
WITNESS_DONE = ("You see {actor} get up from the bench, flushed, while "
                "Bertha counts the tips.")
WITNESS_QUIT = ("You see {actor} tap out and get hauled off the bench by two "
                "stool-boys.")
WITNESS_DEATH = {
    "smothered": "💀 You see {actor} go limp under the lady and not wake "
                 "up. Bertha clicks her tongue.",
    "collapsed": "💀 You see the stool break under the lady, and {actor} "
                 "with it.",
    "engulfed": "💀 You watch {actor} disappear beneath the lady's enormous "
                "rear, head and shoulders first, then all the rest.",
    "vored": "💀 You watch {actor} get swallowed whole. The lady pats her "
             "belly.",
    "anal_vored": "💀 You watch {actor} vanish inside the lady, slowly and "
                  "thoroughly.",
}
WITNESS_FURNITURE = ("You see two waiters strap {actor} to a board. From now "
                     "on {actor} is a stool.")
WITNESS_STAND = "You see {actor} stand up from the stool and stretch."
WITNESS_BACK = "You see {actor} blink, shudder and get back on their feet."
DEATH_SMOTHERED = ("{name} blacks out under the lady, and does not wake. "
                   "Bertha clicks her tongue: 'Poor lamb. Waste not.'")
DEATH_COLLAPSED = ("The stool breaks under the lady, and {name} breaks "
                   "with it. Bertha waves two waiters over: 'Not a "
                   "total loss.'")
DEATH_ENGULFED = ("{name} disappears beneath the lady's enormous rear, "
                  "slowly, thoroughly – her tight hole stretches wide, "
                  "swallowing head and shoulders first, then the rest in "
                  "one long, greedy motion.")
SWALLOW_TOO_SMALL = ("You are not built for it: {need} (needs {butt} cm of "
                     "rear and {weight} kg).")
SWALLOW_NONE = "You are not sitting on anybody."
SWALLOW_RIDER = ("You rock your hips and let {seat} slip into your ass: "
                 "first the head, then the shoulders, your hole stretching "
                 "around him until he is gone with a wet, final gulp. "
                 "Bertha raises her teacup to you.")
SWALLOW_SEAT = ("{rider} spreads herself over your face, and the world "
                "turns dark and warm and tight. You are pulled in, deeper, "
                "and the stool goes silent.")

OUTCOMES = {
    "cushion": "Bertha hangs the leftovers up to dry and sews them into a "
               "cushion: {item}.",
    "cake": "The kitchen bakes the leftovers into something sweet: {item}.",
    "furniture": "Bertha has the broken frame hauled to the workshop. "
                 "{name} is rebuilt into a stool of the house – padded, "
                 "varnished and still very much {name}. Anyone with the "
                 "gold can buy {name} back.",
    "full": "The lady pats her stomach and sighs, satisfied and "
            "pleasantly full. There is nothing left for the kitchen.",
    "engulfed": "The lady pats her stomach contentedly. What comes of it "
                "will be served in a day or two.",
}
READY_LINE = "Bertha has finished {name}: {item}."

BERTHA_NOTES = [
    "{count} ladies' cases are on Bertha's ledger.",
    "She sits down on the cushion room's oldest cushion, and the whole "
    "room creaks.",
]
MENU_HEADER = "🍰 The Fat Ass Café"
BUY_HINT = "[cafe buy <nr>] – cushions and cakes from the house."
FURNITURE_HEADER = "Stools of the house (ransom with [ransom <name>])"

DESPERATE = [
    "You slap her thigh twice, then drum your fingers in a panic. She "
    "does not rise.",
    "A muffled plea escapes you, but the lady only shifts and keeps "
    "talking about cake.",
    "Your legs shake, your lungs burn, and she settles in for a long "
    "chat. You beg with your hands.",
    "You squirm and wheeze, desperate for her to stand. She pats your "
    "head, for she thinks you are being polite.",
]
DESPERATE_RIDER = [
    "{rider} stays seated, and {seat} starts to quiver, whimpering "
    "into her flesh.",
    "{seat} pleads for air in a thin voice, but {rider} only tightens "
    "her seat.",
]

SEAT_LOCKED = ("{rider} sits on you and does not move. There is no standing "
               "up, no safeword that she would hear – only she can [rise]. "
               "You can [hold], [examine] and [help].")
SEAT_STUCK = ("You are pinned under a lady – {way}. You can "
              "[hold] and [examine] for now.")
RIDER_LOOK = ("{name}: {body}, {butt} cm of rear, planted right on "
              "your face. Your teammate decides now – all you can do is "
              "hope for her mercy.")
GUEST_LOOK = ("{name}: {body}, {butt} cm of rear, a fine hat and a "
              "fork already in hand. She smiles down at your stool.")

SEAT_REACTION = [
    "{seat} stays still, breathing in short sips.",
    "{seat} twitches and whimpers into her flesh.",
    "{seat} taps weakly at her thigh, then goes limp, then shakes.",
    "{seat} gasps and pleads, muffled, entirely in vain.",
]
RIDER_STAY = ("{rider} settles in and stays put, crossing her legs over "
              "{seat}'s trembling shoulders.")
RIDER_RAISE = ("{rider} lifts herself a hand's breadth and hovers over "
               "{seat}'s face. {seat} drags in a long, ragged breath – then "
               "she settles back, exactly where she was.")
RIDER_RAISE_WAIT = "{seat} is still catching breath: wait a moment."
RIDE_RAISE = ("You lift yourself a little. {name} gasps, shakes and breathes "
              "– and you sit down again.")
RIDER_LEAN = [
    "{rider} shifts her weight, slowly, all of it, onto {seat}. The stool "
    "groans.",
    "{rider} leans forward and lets her hips do the talking. {seat} "
    "wheezes.",
    "{rider} rolls her hips and settles heavier. {seat} flails a hand.",
]
RIDER_LEAN_MAX = "{rider} cannot press any harder – {seat} is taking all of it."

SEAT_WAITING = ("Nobody sits on you yet. A lady may take you at any moment "
                "([sit] from her side) – otherwise a guest arrives on her "
                "own in a few seconds.")
SEAT_NO_GUEST = "Nobody sits on you yet. Next guest in about {seconds} s."
GUEST_LEAVES = "{name} stands, smooths her dress and sails off. You breathe."
GUEST_ARRIVES = ("{name} ({body}, {butt} cm of rear) arrives and sits down on you, your head "
                 "between her cheeks. {mood} Next reaction in {seconds} s – [hold] to "
                 "answer now, [quit] to stand up.")
STOOL_REACTION = [
    "{name} stays still, shoulders shaking.",
    "{name} whimpers into the floor.",
    "{name} taps the boards weakly, then stops.",
    "{name} gasps a plea that nobody answers.",
]
RIDE_OVER = "The ticket runs out. {name} is led off, trembling and grateful."
RIDE_COLLAPSE = ("{name} collapses flat under you and is dragged out by two "
                 "stool-boys.")
RIDE_DEATH = ("{name} goes limp under you and does not move again. Bertha "
              "clicks her tongue: 'Waste not.' The stool-boys carry him "
              "off.")
RIDE_RISE = "You rise. {name} breathes again."
RIDE_STAY = "You settle in and stay put on {name}."
RIDE_LEAN = [
    "You shift your weight onto {name}, slowly. The boards groan.",
    "You lean forward and let your hips settle heavier on {name}.",
]

DREAD_LINES = {
    1: "Your eyes go to the size of her and stay there a moment too long.",
    2: "Your mouth goes dry. That rear is far bigger than anything you "
       "wanted to carry today.",
    3: "You freeze. Nothing about this is small – not the weight, not the "
       "rear, not the reputation. Every instinct says to run.",
}
SAFEWORD_FROZEN = ("You open your mouth to say the word, but fear locks "
                   "your throat shut and nothing comes out. Try again.")

PANIC_LINES = {
    "uneasy": [
        "{name} shifts and gulps nervously, starting to wonder when this ends.",
        "{name} clears a dry throat, a little too often.",
    ],
    "strained": [
        "{name} is trembling now, breath coming in short, wet gasps.",
        "{name}'s hands claw at the thighs above, white-knuckled.",
    ],
    "panic": [
        "{name} is in real panic: wild eyes, ragged gasps, muffled "
        "pleading that nobody listens to.",
        "{name} thrashes under the weight, begging for air, for a rest, "
        "for anything.",
    ],
    "frantic": [
        "{name} is beyond words – a hoarse, sobbing, frantic scrabble "
        "against the boards, begging with everything left.",
        "{name} screams into the flesh above, a thin animal sound, legs "
        "kicking, nothing left but terror.",
    ],
}

COMPLAINTS_FAIL = [
    "{guest} frowns down at you: 'Honestly! Hold STILL, boy. I did not "
    "pay for a wobbly stool.'",
    "{guest} slaps the back of your head: 'Such a disgrace. Bertha will "
    "hear of this.'",
    "{guest} sniffs: 'The last one never trembled like that. What a "
    "cheek.'",
]
COMPLAINTS_DEATH = [
    "{guest} stands, brushing her skirt, outraged: 'He broke! Under ME! "
    "What a cheek – Bertha, I want a refund and a fresh stool!'",
    "{guest} looks at what is left and huffs: 'The nerve of him, dying in "
    "the middle of my tea. Bertha! This is the third time.'",
]
BERTHA_DEATH = [
    "{guest} rises, smooths her apron and glances at what is left: 'Well. "
    "Even the sturdy ones give out. Someone fetch a mop, dear.'",
    "{guest} sips her tea over the wreckage: 'Waste not, want not. Bring "
    "me the next one.'",
]
COMPLAINT_OK = ("You march to the counter and complain loudly. Bertha "
                "nods gravely: 'A stool that breaks is the house's fault, "
                "dear. Here is half your ticket back – and I will have "
                "words with the cushion room.' (+{refund} gold)")
COMPLAINT_NONE = "Nothing to complain about right now."

ACT_BREATH = ("You gulp one last breath and hold it, going stiff and "
              "still under her.")
ACT_GIVEUP = ("You stop fighting. Your body goes slack, your hands open, "
              "and you let her weight have you.")
ACT_PAT_OK = ("You pat her rear softly, twice, a polite hint. {guest} "
              "blinks: 'Oh, of course, dear,' and rises.")
ACT_PAT_FAIL = ("You pat her rear softly, but {guest} only hums and settles "
                "deeper: 'Not yet, dear.' She presses a little harder.")
ACT_STRUGGLE_OK = ("You buck, twist, and heave – and {guest} tumbles off "
                   "with a shriek: 'How dare you!'")
ACT_STRUGGLE_FAIL = ("You wriggle and heave with everything you have. "
                     "{guest} just giggles and settles heavier.")
RIDER_PAT = "{seat} slaps your rear twice from below. He wants out."
RIDER_PAT_SELF = ("You slap {rider}'s rear twice. She feels it, smiles, "
                  "and stays where she is.")
RIDER_STRUGGLE = ("{seat} bucks and wriggles beneath you in a hopeless "
                  "attempt to get free.")
RIDER_STRUGGLE_SELF = ("You wriggle and heave, but {rider} sits like a "
                       "mountain. Only she can free you.")

SEAT_MUTE = ("You try to speak, but all that comes out is a muffled hum "
             "under her rear. Nobody can hear you down here.")

ACT_KISS = ("You press your lips to {guest}'s rear and kiss it with devotion. "
            "{guest} purrs: 'Good boy.'")
ACT_FRENCH_KISS = (
    "You kiss {guest}'s rear a third time, and this time your lips part. "
    "Your tongue slides in deep, a slow, wet, open-mouthed kiss against "
    "her. {guest} gasps, grips the stool and rolls her hips down into it: "
    "'Oh, you filthy darling… don't stop.'")
KISS_STREAK = 3
KISS_STREAK_PAY = 1.6
ACT_KISS_EASE = " She shifts her weight off you a little."
RIDER_KISS = "{seat} kisses your rear devotedly from below."
RIDER_KISS_SELF = "You kiss {rider}'s rear. She hums and keeps sitting."

BERTHA_NAME = "Madame Bertha"
BERTHA_PROBE = ("The door slams. Madame Bertha herself stalks over, cane "
                "tapping. 'Let us see what you are worth, {name}. Think of "
                "this as an inspection. I do not like your kind.'")

SWALLOW_NPC = ("{guest} looks down at the small, shaking thing under her and "
               "smiles. 'Oh, you poor little snack.' She rocks back, her "
               "hole gapes wide over your face, and she sucks you in "
               "without effort.")

ACT_LICK = ("You push your tongue against {guest}'s asshole and lick it "
            "slowly, thoroughly. {guest} moans: 'Oh, don't you dare "
            "stop.'")
ACT_PLEASED = " She settles in, in no hurry to get up."
LICK_TASTE = (
    "She smells of soap and warm skin, and tastes clean and faintly salty.",
    "She smells of warm skin and a hint of sweat, and tastes salty and "
    "a little sweet.",
    "A musky, sweaty warmth fills your nose; she tastes salty, earthy and "
    "unmistakably of her.",
    "The smell is thick and heady, sweat and musk together. She tastes "
    "sharp, salty and rich, and it clings to your tongue.",
    "The stench of her hits you like a wall, heavy sweat and ripe musk. "
    "Her taste is overwhelming, bitter-salty and strong enough to make "
    "your eyes water.",
)
RIDER_LICK_TASTE = ("You smell her warm skin and a faint musk, and taste "
                    "salt and something sweet.")
RIDER_LICK = "{seat} licks your asshole from below, slowly and eagerly."
RIDER_LICK_SELF = "You lick {rider}'s asshole. She shivers and stays put."

SWALLOW_STOOL = ("You rock your hips and let {name} slip into your ass: "
                 "first the head, then the shoulders, your hole stretching "
                 "around him until he is gone with a wet, final gulp. "
                 "Bertha raises her teacup to you.")
SWALLOW_STOOL_RANDOM = ("{name} is so small and weak under you that your "
                        "hole simply opens and sucks him in, head first. "
                        "He is gone before he can even whimper. Bertha "
                        "raises her teacup.")

CLENCH_RIDER = ("You clench your cheeks tight around {seat}'s face and hold "
                "them there, grinding down.")
CLENCH_SEAT = ("{rider} clamps her cheeks tight around your face. There is "
               "no air, only her.")
CLENCH_MAX = " You cannot press any harder."
CLENCH_PLEAS = {
    1: ["{seat} whimpers into your flesh, the sound muffled and wet.",
        "{seat} squirms and tries to turn his head away. There is nowhere "
        "to turn it.",
        "{seat} gives a thin, pleading whine and pats weakly at your hip."],
    2: ["{seat} sobs under you, his hands scrabbling desperately at your "
        "thighs.",
        "{seat} bucks and kicks, wailing into you, begging for air with "
        "every muffled sound he can make.",
        "{seat} whines high and broken and claws at the stool beneath him."],
    3: ["{seat} screams into your cheeks, a thin, hopeless sound, and "
        "hammers both fists against your thighs.",
        "{seat} thrashes in a blind panic, sobbing and choking, tapping out "
        "again and again.",
        "{seat} wails like a child, heels drumming, fingers digging at your "
        "hips, begging to be let go."],
}
CRUSH_POPS = ["*POP*", "*squelch… POP!*", "*crk-POP*", "*SPLORCH-pop*"]
WIGGLE_RIDER = ("You wiggle your ass slowly back and forth over {seat}'s "
                "face, smearing yourself over his mouth and nose.")
WIGGLE_SEAT = ("{rider} wiggles her ass over your face, her cheeks sliding "
               "across your nose. You gasp and get nothing.")
TORMENT_NONE = "You are not sitting on anybody."

SWALLOW_SOUNDS = (
    "*Mmmpf! Mmmmph!* – {name}'s muffled cries fade into wet squelching.",
    "*Glrk… hnnnngh…* {name} gurgles, and the sound vanishes with a slurp.",
    "A thin, panicked *'Mmh-mmh-MMH!'* comes from inside, then a wet "
    "gulp, then nothing.",
    "*Squelch… slurp… gulp.* From within, {name}'s last whimpers echo "
    "faintly.",
    "{name} groans somewhere deep in there, a dull, muffled thudding "
    "against warm walls.",
)

NPC_CLENCH = ("{guest} clenches her cheeks tight around your face and grinds "
              "down. 'Oh, that's lovely.'")
NPC_WIGGLE = ("{guest} wiggles her ass over your face, her cheeks sliding "
              "across your nose and mouth. 'Hold still, dear.'")
NPC_DEMAND = ("{guest} purrs and shifts: 'Use that tongue, boy. [lick] – "
              "or I will sit harder.'")
NPC_DEMAND_IGNORED = ("{guest} frowns. 'I asked for your tongue.' She sits "
                      "down harder, punishing.")
NPC_DEMAND_PAID = " 'Good boy. Very good boy.' She tips extra."

KILLS_NOTE = "Word in the café: {name} has {kills} on her ledger."


ACT_ENCOURAGE = ("You wheeze out something warm: 'Stay… please… you are "
                 "so comfortable, {guest}.' She hums, delighted, and "
                 "settles in for longer.")
ACT_ENCOURAGE_RIDER = ("You whisper to {rider} that she should stay. She "
                       "can hear it, and what she does with it is up to her.")
RIDER_ENCOURAGED = "{seat} begs you to stay, voice muffled by your thighs."
COLLAPSE_LEAD = ("The last air leaves you. The room tilts, your arms go "
                 "limp, and you collapse under {guest}.")
COLLAPSE_CRUSHED = ("{guest} feels the stool go limp and shrieks as she "
                    "topples, all {weight} kg of her landing on you. "
                    "There is a wet crunch and nothing moves anymore.")
COLLAPSE_DRAGGED = ("{guest} slides off and lands on top of you with an "
                    "'Oof!' Two waiters grab your ankles and drag you "
                    "through the back door, limp and wheezing. Your shift "
                    "is over.")
COLLAPSE_RIDER = "{seat} collapsed under you and was dragged away."
COLLAPSE_RIDER_CRUSHED = ("{seat} collapsed under you. You landed on "
                          "{seat} with all your weight, and it did not end "
                          "well for {seat}.")

PITY_EASE = ("{guest} notices your trembling, hesitates, and lifts a "
             "little – 'Oh dear, I am sorry, take a breath.'")


CRUSH_SEAT = ("{guest} clamps down with everything she has, all {weight} kg "
              "and every centimetre of her enormous rear. There is a wet, "
              "final crack from under her. When she lifts her hips there is "
              "nothing left of {seat}'s head worth saving.")
CRUSH_RIDER_STOOL = ("You clench with all your weight and your enormous "
                     "rear. Something gives way with a wet crack, and "
                     "{name} goes still. Bertha clicks her tongue: 'Waste "
                     "not.'")
CRUSH_WARNING = (" Your rear is big enough to crush a skull now – another "
                 "round like this could be the end of {seat}.")
CRUSH_WHIMPER = {
    1: (" {seat} whimpers, thin and breathless: something creaks.",
        " {seat} lets out a small, frightened whimper under the weight."),
    2: (" {seat} whimpers 'please, please' and goes stiff. His skull "
        "creaks audibly.",
        " {seat} whines through his teeth, a sound that says the end is "
        "near."),
    3: (" {seat} whimpers a last, tiny, hopeless sound. Something is "
        "about to give.",
        " {seat} goes limp and whimpers, 'it's cracking...'. You can feel "
        "it, too."),
}


PAT_PUNISH = {
    "clamp": ("{guest} catches your hand mid-slap and wrenches it away. "
              "'Did I say you may touch?' She clamps her cheeks around "
              "your face until your ears ring."),
    "air": ("{guest} slaps your hand off her rear with a crack. 'Hands "
            "off. You breathe when I allow it.' She seals your nose and "
            "mouth and holds there, unmoving, far too long."),
    "apology": ("{guest} knocks your hand away and grinds down. 'Rude. "
                "You will apologise with that tongue, and you will "
                "mean it.'"),
    "winded": ("{guest} pins your wrist under her thigh and bounces "
               "once, hard, driving every drop of air out of you. "
               "'Next time it will be both hands.'"),
}


HELP = """🍰 Fat Ass Café
Madame Bertha's café: only ladies (Female, Shemale) are guests, men and
everybody else work as furniture. She keeps 25% of your pay.
  cafe                      – list the jobs, cakes and cushions, stools
  job cafe <job>            – seat, server, trainer, baker, usher, cleaner
  order cafe <nr|name> [take] – tea and cake; eaten at once, or with 'take'
                              into your bag as a consumable
  job cafe seat             – you are the stool: guests sit, you [hold]
                              round after round. [quit] is your safeword.
                              Heavier guests need more VIT and STR; if it
                              goes badly you can black out for good.
  regular [remove]          – (café seat / brothel shift) make the guest or client
                              with you a regular: stored with fixed age, height
                              and body, and they come back (35 %).
  (all jobs) – a shift runs in a 20 s beat: one round per 20 s, others can act meanwhile.
                              In the brothel the house picks a random act for you if you
                              do not choose in time (domina: only give, sub: only receive).
                              [quit] leaves a shift early with the pay so far.
  move [name]               – (dancer / milk barrel shift) put on a move: spin, strip, pole,
                              lapdance, bow / squeeze, pump, tease, rest. Each move is a
                              round with a pay factor; if you do nothing the round runs by itself.
  visit <name>              – also: use a working character – a whore, the dancer or the
                              milk barrel – for 20/40 gold (tavern/brothel). The worker
                              gets the money and sees what happens.
  job brothel whore domina|sub – choose your role: as a domina only dominated
                              clients come and you give; as a sub only
                              dominant clients come and you receive.
  room common|private       – sleep in the Gilded Tankard (8 / 25 gold): sleep need to 0;
                              the private room also gives breakfast (hunger/thirst down);
                              in the common room a neighbour may rob you (15 %). GUI: Tavern tab.
  agepref [min max]         – set the age range of clients, café guests and stools
                              you meet (default 18-65, min 18, 10 years wide).
  family [<name> <role>|clear <name>] – mark another character as YOUR mother, father,
                              son, daughter, sister, brother or partner; they get the
                              matching role back. Mother on her son's stool: family
                              scene ('Mom knows best.'). Shown in examine. Stored by
                              character ID; also settable in the Character tab (Family).
                              Regulars with a known address call on you now and then
                              while you hang around the café (tip). A regular's JSON may
                              hold "son" and "girlfriend" names for the family visit.
  prefs                     – your preferences; [prefs role dom|sub|switch],
                              [prefs position <name>] and [prefs practice <name>]
                              toggle, [prefs clear] resets. Role and position
                              set the scene defaults, dom/sub the brothel mode,
                              practices narrow what clients wish for.
  regulars drop <name>      – ditch a regular (asks for [confirm] first)
  regulars look <name>      – examine a regular in detail (also the 🔍 button)
  regulars                  – list your regulars: age, visits, married or single,
                              address known/unknown.
  regular ask               – (as a domina, with a client who wants to be dominated: you
                              simply order the address, no visits needed, and he becomes a regular)
  regular ask               – ask the guest/client with you for their address
                              (needs 3 visits as a regular).
  visit <name>              – call on a regular whose address you know: a
                              private evening, no money changes hands. Married ones may have
                              a spouse who comes home early. A café regular
                              uses you as her seat: warning first, then
                              [visit <name> confirm] – no control, no
                              safeword, you may not survive it. Options:
                              gentle|normal|hard, short|long – every
                              survived visit trains your seat against this
                              lady (capped, never invulnerable).
  invite <name>             – the same at your own home; a café regular may
                              decline (mood decides).
  endrun                    – after dying in town (café etc.) you are locked until
                              the round ends; [endrun] ends it for you now.
  clench, wiggle            – (sitting on a man) clench your cheeks around his
                              face (more pressure) or wiggle your ass over it
                              (he loses air and is weaker next round).
  swallow                   – (sitting on a man, rear >= 140 cm and >= 95 kg) pull
                              him into your ass: anal vore, he is gone for the
                              round and Bertha digests him (a day or two).
  encourage                 – (pinned seat) beg her to stay: she sits longer, +15 % pay.
                              At 0 % air you collapse: a lady over 100 kg falls
                              on you and crushes you, a lighter one lands on you
                              and the waiters drag you out (shift over).
  wait, breath, pat, struggle, kiss, lick, giveup – what a pinned seat can do each round:
                              endure, hold his breath (+5 now, -3 next round),
                              slap her rear (35 % she gets up, else she
                              presses harder), struggle free (strength+agility
                              vs her weight; failing costs -4 and she presses),
                              kiss/lick her (30/40 % more pay, she stays
                              seated longer, pat works less, may ease her
                              pressure), give up (+6 and 50 % more pay, but you let her).
                              Under a lady of your own party pat/struggle only
                              signal her; only she can [rise].
  hold / quit               – answer the current guest at once, or stand up.
                              TIME: the shift starts waiting; a lady can [sit]
                              first, otherwise an NPC guest arrives after a
                              few seconds. Every 20 s a reaction/round happens
                              by itself (counter in the GUI) – he may break
                              down or die if it is too heavy. Ladies who stay
                              keep him pinned.
                              (ends the shift).
                              Men may ONLY work the seat. While a shift runs
                              you are pinned: only [examine], [help], [hold]
                              (and [quit]) work. If a lady character sits
                              on you, you cannot quit until she [rise]s.
  sit <nr>                  – sit on a free NPC stool (15 gold, shown in [cafe]
                              and [sit]; sometimes there is none)
  job cafe trainer          – break in new stools: every one is described
  order while sitting       – eating on top of him makes you heavier for the
                              rest of the sitting (a few kg per dish, also
                              via [consume])
  complain                  – after a stool collapsed or died under you, give
                              Bertha a piece of your mind (half the ticket back)
  stay / lean               – while sitting: stay put, or shift your weight
                              (more pressure, more pay, he suffers more;
                              [rise] spares him). He is pinned either way
  sit <name> / rise         – a lady (Female/Shemale) sits on a character
                              who works a seat shift, and stands up again.
                              Between your own characters it never kills.
  cafe buy <nr>             – buy a cushion or cake of the house
Deaths there ('smothered', and for men under a very large lady sometimes
'engulfed') are never wasted: Bertha turns the victim into a Seat Cushion
(gear), a Cream Cake (food) or – rarely – a stool of the house that stays
as an NPC and can be bought free with [ransom <name>]. Engulfed victims
are served a day or two later. Bertha gets bigger with every case.
Only in town, not while you are in the dungeon."""
