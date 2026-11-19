NO_REACTION = -1
LEVELS = ("partial", "bare")
PRUDE_WORDS = ("prim", "proper", "stern", "strict", "devout", "pious",
               "respectable", "prudish", "severe", "formal", "gruff")
LOOSE_WORDS = ("flirt", "lewd", "wanton", "playful", "bold", "shameless",
               "ribald", "lusty", "seductive", "cheeky", "charming")
FULL_BODY_WORDS = ("dress", "gown", "robe", "catsuit", "bodysuit", "slip",
                   "uniform", "habit", "pinafore", "overalls", "teddy")
BRA_WORDS = ("bra", "bustier", "corset", "corselet", "teddy", "bodysuit",
             "babydoll", "negligee", "bodystocking", "dessous", "lingerie",
             "set")
REACTIONS = {
    "d4": {
        "partial": [
            "{keeper}'s eyes flick to {name}'s bare skin and away again. "
            "'Please. A little decency, if you would.'",
            "A sharp breath. 'You can't walk in like that,' {keeper} "
            "mutters, and studies the counter very carefully.",
            "{keeper} clears their throat twice and looks pointedly at the "
            "ceiling.",
        ],
        "bare": [
            "{keeper} goes pale, then red. 'Out! Get dressed this "
            "instant!'",
            "'Are you out of your mind?' {keeper} hisses. 'This is a "
            "respectable street!'",
            "{keeper} drops whatever they were holding and stares. 'Cover "
            "yourself. Now.'",
        ],
    },
    "d3": {
        "partial": [
            "{keeper} glances once at {name}, shrugs and goes back to "
            "work.",
            "'Cold in here, is it?' {keeper} says dryly.",
            "{keeper} raises an eyebrow, says nothing and does not stop "
            "counting.",
        ],
        "bare": [
            "'Well. That is certainly a way to shop,' says {keeper} "
            "without looking up.",
            "{keeper} sighs. 'Fine. Show me coin and I won't ask.'",
            "{keeper} gives {name} a long, level look. 'Not my business. "
            "Mind the draft.'",
        ],
    },
    "d2": {
        "partial": [
            "{keeper} adjusts a pair of spectacles and looks a moment too "
            "long.",
            "'Interesting outfit,' {keeper} says with a grin.",
            "{keeper} leans on the counter, plainly enjoying the view.",
        ],
        "bare": [
            "{keeper} chokes, coughs and tries very hard to look "
            "elsewhere. Mostly fails.",
            "'Well! That's a surprise,' says {keeper}, delighted.",
            "{keeper} stares openly, then fans themselves with a ledger.",
        ],
    },
    "d1": {
        "partial": [
            "{keeper} whistles softly. 'Nice. Anything else?'",
            "{keeper} nods approvingly and goes on with the day.",
            "'Brave look,' {keeper} says with a grin.",
        ],
        "bare": [
            "{keeper} laughs out loud. 'Ha! Bold! What can I get you?'",
            "'Nothing I haven't seen,' says {keeper}, 'but not often that "
            "well.'",
            "{keeper} grins and slaps the counter in approval.",
        ],
    },
    "d0": {
        "partial": [
            "{keeper} lifts an eyebrow and smiles. 'Bold. I like it.'",
            "'Now that is how you dress,' says {keeper}, looking {name} "
            "up and down.",
            "{keeper} smiles slowly. 'Do not cover up on my account.'",
        ],
        "bare": [
            "'Magnificent,' says {keeper}, not even pretending to look "
            "elsewhere.",
            "{keeper} circles {name} once, appreciatively. 'Entirely "
            "unbothered. Delightful.'",
            "{keeper} folds their hands and beams. 'The best-dressed "
            "guest we've had all week.'",
        ],
    },
    "brothel": {
        "partial": [
            "{keeper} looks {name} over approvingly. 'Already dressed for "
            "work, darling?'",
            "'Oh, you're a treat already,' purrs {keeper}. 'Come in, come "
            "in.'",
            "{keeper} smiles. 'Half the job done, I see.'",
        ],
        "bare": [
            "{keeper} claps once. 'Straight to the point. I do like that "
            "in a guest.'",
            "'No need for coats here, sweet thing,' says {keeper}.",
            "{keeper} pulls out a chair. 'Sit. You are clearly here for "
            "fun.'",
        ],
    },
    "cafe": {
        "partial": [
            "'You're overdressed, dear, and underseated,' teases "
            "{keeper}.",
            "The regulars notice {name}'s outfit and murmur their approval "
            "over their tea.",
            "{keeper} grins. 'The dress code is flexible here. The seating "
            "is not.'",
        ],
        "bare": [
            "A ripple of delighted gasps runs through the café as {name} "
            "walks in.",
            "{keeper} fans a menu. 'Table for one, and a seat for every "
            "guest who asks.'",
            "The whole café turns, applauds politely and goes back to its "
            "cake.",
        ],
    },
}
