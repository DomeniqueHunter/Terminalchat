KEY = "tuning_room"
TITLE = "The Tuning Room"
BLURB = ("A velvet-curtained salon with three doors, where five coaches "
         "help you find out what you like.")
HELP = ("The Tuning Room (Last Light): ask a coach by first name for "
        "training: seraphine (straight), ilaria (bi), taren (fag "
        "training for men), ysolde (lesbian training for women), camille "
        "(homo training for the rest, an alternative for men). One "
        "training per game day.")
OFFER = ("'Welcome, darling. Three doors, five coaches, one evening.' "
         "The Tuning Room smells of rosewater and old velvet.")
CLOSED = "The velvet curtains are drawn: no training while you are down below."
TOO_SOON = ("The coaches smile and shake their heads. 'Once a day, darling. "
            "Come back tomorrow.'")
SAME = "'Nothing to change, darling. You already feel that way.'"
ASK_FIRST = "Ask for a coach by first name. Today's offers:"
UNKNOWN = "Nobody here by that name."

COACHES = {
    "seraphine": "Madame Seraphine Delacroix",
    "ilaria": "Ilaria Moonwhisper",
    "taren": "Coach Taren Blackwood",
    "ysolde": "Mother Ysolde Marrow",
    "camille": "Camille Moreau",
}
KIND_LABELS = {"straight": "Straight training", "bi": "Bi training",
               "fag": "Fag training", "lesbian": "Lesbian training",
               "homo": "Homo training"}
LIKES_TEXT = {"penis": "penis", "vagina": "vagina", "both": "both"}
REFUSALS = {
    "seraphine": "Madame Seraphine tilts her head. 'Not my door for you, "
                 "darling.'",
    "ilaria": "Ilaria laughs. 'You have already got the whole hallway, "
              "darling.'",
    "taren": "Taren shakes his head slowly. 'That is not my kind of "
             "teaching, friend.'",
    "ysolde": "Mother Ysolde pats the chair beside her. 'Another door "
              "for you, dear.'",
    "camille": "Camille folds her arms. 'Not for you, sweetheart. Pick "
               "another door.'",
}

SCENES = {
    ("seraphine", "straight"): [
        "Madame Seraphine hums a waltz and takes your hand. The salon is "
        "small, the steps are old-fashioned, and she corrects your posture "
        "twice before the second turn. 'Eyes up, darling. Not there. "
        "There.'",
        "By the last bar you have forgotten what you were nervous about. "
        "When you leave, your gaze goes the way it once did, the oldest "
        "road of all."],
    ("ilaria", "bi"): [
        "Ilaria opens two doors and asks you not to choose. 'Why pick one "
        "when the hallway is so nice?' You walk through both, one after "
        "the other, and every room behind them is warmer than the last.",
        "When you come back she is grinning like a cat that has solved "
        "you. Nothing in the hall looks off-limits any more."],
    ("taren", "fag"): [
        "Taren leads you behind the dark silk screen and sits down "
        "opposite you. For a long while he does not touch you. 'Breathe. "
        "Tell me what you looked at on your way up the stairs.'",
        "He listens, nods, asks again, and the answers you did not know "
        "you had become easy to say. When you step out, you look at the "
        "men in the hall the way you always secretly wanted to."],
    ("ysolde", "lesbian"): [
        "Mother Ysolde pours tea before anything else and watches you over "
        "the rim of her glasses. 'Sit, dear. You did not climb those "
        "stairs by accident.' The truths come out with the tea, one cup "
        "at a time.",
        "When she finally holds up the mirror there is nothing left to be "
        "shy about. When you leave, your eyes find the women in the hall "
        "first and stay there."],
    ("camille", "fag"): [
        "Camille has to duck to follow you behind the screen. She leans on "
        "the wall, looks you up and down, and says, 'Stop apologising. I "
        "have seen everything twice.' She is rough, funny and very "
        "patient.",
        "An hour goes by without you noticing. At the end she tips your "
        "chin up. 'Look at me. Higher. There. One way ticket, darling.' "
        "You walk out with a new sense of what you want."],
    ("camille", "homo"): [
        "Camille ducks through the curtain behind you and drops into the "
        "big chair, which creaks. 'We are made of the same awkward parts, "
        "you and I.' She talks about hers, you talk about yours.",
        "Somewhere in between, the awkwardness turns into something warm "
        "and funny. When she waves you out, what you carry has stopped "
        "being a puzzle and started feeling like yours, and you know "
        "exactly who you want to share it with."],
}
