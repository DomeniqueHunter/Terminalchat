CONTENT_LINES = {
    "cold": {
        "met": (
            "{sub} asked, {dom} obliged, and for a moment even the chill "
            "between them thins.",
            "{dom} does exactly what {sub} wished for. {sub} blinks, "
            "surprised, and almost smiles.",
            "A rare yes. {sub} files it away carefully.",
        ),
        "free": (
            "{dom} simply takes the lead and {sub} lets it happen, "
            "wary but not unwilling.",
            "Nobody asked, but {sub} does not object either.",
            "{sub} watches {dom} warily and accepts it.",
        ),
        "ignored": (
            "{sub} had wished for something else. {dom} did not care, "
            "and {sub} says nothing.",
            "The wish goes unanswered. {sub}'s jaw tightens.",
            "{dom} brushes the wish aside without a word.",
        ),
        "dislike_asked": (
            "{sub} asked for something else and got this instead: "
            "something {sub} plainly hates. The room goes cold.",
            "{sub} flinches. It was not what {sub} begged for, "
            "and it was not what {sub} wanted at all.",
            "{dom} ignores the wish and picks the one thing {sub} "
            "cannot stand. {sub} stares at the wall.",
        ),
        "dislike_free": (
            "{sub} swallows a protest. This is not to {sub}'s taste.",
            "{sub} goes stiff. {dom} did not ask and {sub} did not "
            "enjoy it.",
            "A small, silent no crosses {sub}'s face.",
        ),
    },
    "warm": {
        "met": (
            "{dom} grants the wish and {sub} sighs with relief and "
            "gratitude.",
            "'Exactly that,' {sub} breathes, and {dom} smiles.",
            "{sub} asked, {dom} listened. It shows in {sub}'s eyes.",
        ),
        "free": (
            "{dom} takes the lead and {sub} settles into it with a "
            "pleased little shiver.",
            "{sub} did not ask for this, but {sub} is glad of it.",
            "{dom} knows what {sub} likes and does not need to be "
            "asked.",
        ),
        "ignored": (
            "{dom} does something else than {sub} wished for. {sub} "
            "shrugs and goes along.",
            "'Not what I asked,' {sub} murmurs, but not unhappily.",
            "The wish is set aside. {sub} lets it go.",
        ),
        "dislike_asked": (
            "{sub} wished for something kinder. {dom} chose this, and "
            "{sub} gives {dom} a hurt look.",
            "'That is not what I asked for,' {sub} says quietly, and "
            "means it.",
            "{sub} bites a lip. The wish was ignored for something "
            "{sub} does not like.",
        ),
        "dislike_free": (
            "{sub} frowns a little. Not {sub}'s favourite.",
            "{dom} misjudged it. {sub} says nothing, but notices.",
            "{sub} endures it with a thin smile.",
        ),
    },
    "devoted": {
        "met": (
            "{dom} grants the wish and {sub} nearly melts: 'Thank you, "
            "thank you.'",
            "{sub} looks up at {dom} with shining eyes. They know each "
            "other well by now.",
            "{sub} asked and {dom} gave: a rhythm they both know by "
            "heart.",
        ),
        "free": (
            "{dom} leads without a word and {sub} follows without "
            "thinking.",
            "{sub} trusts {dom} so far that asking is no longer "
            "necessary.",
            "{dom} takes what is hers, and {sub} gives it happily.",
        ),
        "ignored": (
            "{dom} chose differently from the wish. {sub} trusts "
            "{dom}'s judgement anyway.",
            "{sub} had wished for something else. 'As you like,' "
            "{sub} whispers.",
            "{sub} lets the wish go: {dom} always knows best.",
        ),
        "dislike_asked": (
            "{sub} had asked, and {dom} chose the one thing {sub} "
            "dreads. The trust wavers for a moment.",
            "{sub} looks at {dom} with genuine hurt. It is rare to "
            "see it there.",
            "'Not that,' {sub} whispers. Even after all this time.",
        ),
        "dislike_free": (
            "{sub} goes along, but the old ease is missing.",
            "{dom} should have known better, and {sub}'s sigh says so.",
            "A shadow crosses {sub}'s face and is gone.",
        ),
    },
}
ORGASM = {
    "cum": (
        "{name} shudders, clenches and comes in long, hard pulses, "
        "mouth open, nothing left to say.",
        "{name}'s breath breaks. With a groan that goes through the "
        "whole body {name} spills, shaking.",
        "A loud, helpless cry: {name} comes, spurting, eyes squeezed "
        "shut.",
        "{name} arches, throbs and finishes with a gasp, "
        "hips twitching through every last pulse.",
    ),
    "squirt": (
        "{name} cries out and squirts, thighs trembling, soaking "
        "everything within reach.",
        "{name}'s whole body locks, then lets go in a hot rush "
        "that leaves {name} gasping.",
        "With a high, broken moan {name} comes hard and squirts, "
        "knees giving way.",
        "{name} clenches around nothing, shudders and floods the "
        "sheets with a stifled cry.",
    ),
}
BOTH = (
    "They come together, and for a moment the room holds only their "
    "ragged breathing.",
    "At the same instant, both give in. Neither is able to say who "
    "started it.",
    "It breaks over them at once, and they cling to each other until "
    "it passes.",
)
DESTINATIONS = {
    "pen_in": (
        "deep inside {other}",
        "buried in {other} to the hilt, filling {other} up",
        "right into {other}, hips pressed flush",
    ),
    "pen_on": (
        "all over {other}'s back and backside",
        "in long ropes across {other}'s spine and hips",
        "over {other}'s skin, hot and thick",
    ),
    "pen_recv": (
        "untouched onto the sheets beneath them",
        "over {other}'s hand and the bed",
        "onto the blanket between them",
    ),
    "mouth": (
        "into {other}'s mouth, and {other} swallows it down",
        "down {other}'s throat",
        "onto {other}'s tongue",
    ),
    "face": (
        "over {other}'s face, dripping from lips and chin",
        "across {other}'s cheeks and lashes",
        "in warm streaks over {other}'s face",
    ),
    "chest": (
        "between {other}'s breasts and up over {other}'s throat",
        "all over {other}'s chest",
        "across {other}'s cleavage and chin",
    ),
    "feet": (
        "over {other}'s feet",
        "across {other}'s soles and toes",
        "onto {other}'s ankles",
    ),
    "sheets": (
        "over the sheets",
        "across the bed",
        "onto the blanket",
    ),
    "floor": (
        "onto the floor in helpless spurts",
        "dripping onto the boards",
        "in a thin puddle at {other}'s feet",
    ),
    "self": (
        "over {own} own stomach and chest",
        "across {own} own belly",
        "all over {own} own body",
    ),
    "body": (
        "over the bound, helpless body",
        "across the straps and skin",
        "onto the rope marks",
    ),
}
