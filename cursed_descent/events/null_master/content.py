EVENT_TEXTS = {
    "null_master": {
        "intro": "⚫ The torchlight simply stops. A tall figure in a smooth "
                 "black hood stands in the corridor, hands folded, utterly "
                 "still. Behind the hood there is only a faint hum. 'I am "
                 "the Null Master,' it says, and every word lands flat and "
                 "empty. 'Three riddles. Answer, and I give. Fail, and I "
                 "empty you.' Beyond it, a row of kneeling, hooded figures "
                 "squats motionless in the dark – drones, hands on knees, "
                 "waiting.",
        "options": "Answer with [answer <word>] (anyone may), or [depart] "
                   "and refuse the game. ({seconds} s)",
        "ask": "🕳 Riddle {nr} of {total}: \"{question}\"",
        "right": "'Yes,' the Null Master hums, and something in the air "
                 "settles. {name} was right: +{exp} EXP, +{gold} gold.",
        "wrong": "'No.' The word has no echo. {name} was wrong.",
        "drone": "The hum rises. {name}'s thoughts slide out one by one "
                 "like water through a sieve, until nothing is left but "
                 "the need to squat. A black hood settles over {their} "
                 "head. The Null Master adds one more figure to its row "
                 "and says, gently: 'Quiet now.'",
        "done": "'Three,' the Null Master says, and for the first time "
                "there is something in the voice – almost respect. 'Take "
                "this and go before I change my mind.'",
        "reward": "A smooth black shard drops into the dust.",
        "depart": "'Refusing is also an answer,' the Null Master hums. "
                  "'A very empty one. Go.' The torchlight returns, and "
                  "so does the draught.",
        "timeout": "The silence stretches until nobody remembers a "
                   "question was asked. The figure is simply gone.",
        "ended": "The last riddle is spent. The Null Master dissolves "
                 "into the dark, and the torchlight stumbles back.",
        "no_riddle": "Nothing is being asked right now.",
    },
}


RIDDLES = [
    ("I speak without a mouth and hear without ears. I have no body, but "
     "come alive with the wind. What am I?", ("echo",)),
    ("The more of me you take, the more you leave behind. What am I?",
     ("footstep", "step", "track")),
    ("What has hands but cannot clap?", ("clock", "watch")),
    ("What gets wetter the more it dries?", ("towel", "cloth")),
    ("I have cities but no houses, mountains but no trees, and water but "
     "no fish. What am I?", ("map", "chart")),
    ("What can you break without ever touching it?",
     ("promise", "silence", "vow")),
    ("What has a neck but no head?", ("bottle", "flask")),
    ("The one who makes me does not need me, the one who buys me does not "
     "use me, and the one who uses me never knows. What am I?",
     ("coffin", "casket")),
    ("What has keys but opens no locks?", ("piano", "keyboard")),
    ("What has one eye but cannot see?", ("needle",)),
    ("What runs but never walks, and has a mouth but never talks?",
     ("river", "stream")),
    ("I am nothing, yet say my name and I vanish. What am I?",
     ("silence", "quiet")),
    ("What can fill a room without taking up any space?",
     ("light", "sound", "air", "smell")),
    ("What belongs to you, yet is used far more by everyone else?",
     ("name",)),
]
