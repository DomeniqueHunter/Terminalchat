from .rough import ROUGH_MOVES


MOVES = {
    "dancer": {
        "spin": ("You spin in a blur of skirts and sweat; the room claps "
                 "in time.", 1.0),
        "strip": ("You peel off one glove, then the next, and the crowd "
                  "howls for the rest.", 1.3),
        "pole": ("You climb the pole, hang by one knee and slide down "
                 "slowly with your eyes on the biggest spender.", 1.25),
        "lapdance": ("You pick a guest, straddle his lap and move until "
                     "he forgets how to speak.", 1.5),
        "bow": ("You finish with a deep, slow bow and a wink; coins "
                "rain onto the boards.", 0.9),
    },
    "milk": {
        "squeeze": ("You squeeze yourself dry for the crowd and the "
                    "{output} runs into the bucket.", 1.2),
        "pump": ("The pump hums, you gasp, and {output} comes in a "
                 "steady, noisy stream.", 1.3),
        "tease": ("You tease the tap with slow, slick fingers; the patrons "
                  "place bets on how long you last.", 1.4),
        "rest": ("You lean back and let the barrel fill by itself, "
                 "breathing deep.", 0.8),
    },
}


def moves_for(job_key:str, player=None) -> dict[str, tuple[str, float]]:
    moves = dict(MOVES.get(job_key, {}))
    if job_key != "milk":
        return moves
    from ..brothel.practices_anatomy import anatomy
    tags = anatomy(player)["tags"] if player is not None else None
    for name, (need, text, factor) in ROUGH_MOVES.items():
        if tags is None or need == "any" or tags[need]:
            moves[name] = (text, factor)
    return moves
