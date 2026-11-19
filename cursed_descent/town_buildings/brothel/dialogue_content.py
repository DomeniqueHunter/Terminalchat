TONES = ("sweet", "teasing", "stern")
TEMPERS = ("shy", "playful", "romantic", "gruff")
DOMINATED_TEMPER = "needy"
PREFERRED_TONE = {"shy": "sweet", "playful": "teasing",
                  "romantic": "sweet", "gruff": "stern",
                  "needy": "stern"}
TONE_HINTS = {"sweet": ("shy", "gentle", "calm", "kind", "warm", "soft"),
              "stern": ("stern", "strict", "cold", "blunt", "gruff",
                        "sharp", "strong")}

GREETINGS = {
    "shy": ("'Um… hello. I've never done this before. Is it… all right "
            "if I just stand here for a moment?'",
            "'S-sorry, I'm early. I can wait outside if I'm in the "
            "way.'",
            "'They said you were kind. Please be kind.'"),
    "playful": ("'Well, well! Is this the one everybody has been "
                "whispering about? Don't disappoint me, darling.'",
                "'I brought a bottle and a bad joke. Which first?'",
                "'Let's make this memorable – or at least loud.'"),
    "romantic": ("'I've thought about this evening all week. May I "
                 "call you by your name?'",
                 "'You look lovely in the lamplight. Shall we begin "
                 "slowly?'",
                 "'I know it's a business, but pretend with me, just "
                 "for tonight.'"),
    "gruff": ("'Don't talk. Just do what I paid for.'",
              "'Short day. Long evening. Get on with it.'",
              "'I don't do small talk. Do you do anything else?'"),
    "needy": ("'Please, mistress, I've been very bad all week. Do with "
              "me what you will.'",
              "'I kneel when you say, I speak when you say. Tell me "
              "how to serve you.'",
              "'Punish me, please. I need to be told I'm nothing.'"),
}

PLAYER_LINES = {
    "sweet": {
        "give": ("'Relax, darling. Let me look after you tonight.'",
                 "'Close your eyes. I'll be gentle, I promise.'",
                 "'Breathe. You're safe here, and I'm all yours.'"),
        "receive": ("'Take your time with me. I'm yours to hold.'",
                    "'Be as soft or as bold as you like. I'm "
                    "listening.'",
                    "'Come closer. I want to feel you.'"),
    },
    "teasing": {
        "give": ("'Oh, you're going to enjoy this. Try not to beg too "
                 "early.'",
                 "'Let's see how long you can stay quiet for me.'",
                 "'I'll do all the work. You just try to keep up.'"),
        "receive": ("'Go on, show me what you've got. Impress me.'",
                    "'Careful, darling – I bite back.'",
                    "'I hope you've got stamina. I'm just getting "
                    "started.'"),
    },
    "stern": {
        "give": ("'On your knees. Eyes on me. You'll do exactly as "
                 "I say.'",
                 "'Don't move, don't speak. I decide when you're "
                 "done.'",
                 "'You asked for this. Now take it properly.'"),
        "receive": ("'You'll do this properly or not at all. Begin.'",
                    "'Don't stop until I tell you.'",
                    "'Eyes down. Hands where I can see them. Serve me.'"),
    },
}

REACTIONS = {
    "shy": {
        "liked": ("'Oh! That was… thank you. That was perfect.'",
                  "'I didn't know it could feel like that. Can I "
                  "come back tomorrow?'",
                  "'I'm shaking. In a good way, I think.'"),
        "fine": ("'That was nice. Thank you for being patient with "
                 "me.'",
                 "'Um, it was fine. I think I wanted something "
                 "else, but it was fine.'",
                 "'Thank you. I'm sorry I'm so awkward.'"),
    },
    "playful": {
        "liked": ("'Ha! You're good. I'm telling everyone!'",
                  "'That's what I'm talking about. Take a bow, "
                  "darling.'",
                  "'You've ruined all other evenings for me.'"),
        "fine": ("'Not bad. Not bad at all, I'd go for a second "
                 "round.'",
                 "'Decent. You owe me a surprise next time.'",
                 "'Good fun, though I had something else in mind.'"),
    },
    "romantic": {
        "liked": ("'That was… beautiful. I'll remember your name.'",
                  "'For a moment I forgot this was a transaction.'",
                  "'You made me feel seen. Thank you.'"),
        "fine": ("'That was kind. Thank you for the evening.'",
                 "'Pleasant. I'd hoped for a little more tenderness.'",
                 "'Thank you. I'll think of this one fondly.'"),
    },
    "gruff": {
        "liked": ("'Hm. Not bad. Not bad at all.'",
                  "'You do the job. I'll be back.'",
                  "'Better than most. Here, keep the change.'"),
        "fine": ("'Adequate.'",
                 "'I've had worse. I've had better.'",
                 "'It'll do. Don't expect applause.'"),
    },
    "needy": {
        "liked": ("'Oh, thank you, mistress, thank you… I'm "
                  "nothing without you!'",
                  "'That was exactly what I needed. May I kiss "
                  "your hand?'",
                  "'Yes… yes… I'll be good, I promise!'"),
        "fine": ("'Thank you, mistress. I… I hoped for something "
                 "else, but I'm grateful.'",
                 "'I deserved less. Thank you for your mercy.'",
                 "'Forgive me for asking, but could we try something "
                 "different next time?'"),
    },
}

MATCH_LINE = "(A {tone} tone: exactly what they hoped for. Tip +25%.)"
