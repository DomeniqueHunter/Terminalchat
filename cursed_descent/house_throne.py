import random
from typing import Any

from .config import HOME_SEAT_SITS, INTIMACY_BOND, INTIMACY_RELIEF
from .models import Message, Player
from .needs_runtime import satisfy
from .npc_menu import bump
from .partner_detail import partner_line
from .towns.last_light_humans.cafe.guests import (
    endurance, fatigue, pressure, smell_drain,
)
from .towns.last_light_humans.cafe.home_seat import guest_of
from .towns.last_light_humans.cafe.seat import air_change, stats_of


INTRO = ("You made {guest} lie down on the rug. Tonight {guest} is "
         "your seat, and you take your time arranging yourself.")
HOLD = {
    "easy": (
        "{guest} takes your weight with a long breath, hands resting "
        "on your thighs. 'I can hold this all night,' comes the muffled "
        "boast, and you reward it with a slow roll of the hips.",
        "You settle fully and {guest} does not even flinch; only a "
        "low, contented hum rises from under you.",
    ),
    "hard": (
        "{guest} trembles under you, breath coming in short sips, but "
        "holds. You lean forward just to feel {guest} work for it.",
        "You press down and {guest}'s fingers dig into your hips, "
        "asking for mercy without a word. You pretend not to notice.",
    ),
    "bad": (
        "{guest} taps weakly against your thigh, a thin, desperate "
        "sound dying in the dark under you. You lift half an inch – "
        "exactly as long as it takes for one ragged breath – and sit "
        "again.",
        "{guest} bucks once, then goes limp for a moment. You grind "
        "down slowly and let {guest} earn the next breath.",
    ),
}
PASSED_OUT = ("{guest} goes still under you. You rise with a satisfied "
              "sigh and find {guest} breathing, flushed and dazed – out "
              "cold, but alive. It will pass.")


def throne_scene(player:Player, guest:Player, repository:Any,
                 rng:random.Random, called:str="") -> list[Message]:
    sitter = guest_of({
        "name": player.full_name,
        "weight": player.body.get("weight", 80),
        "butt": player.body.get("butt", 110), "cruel": 1,
        "age": player.age, "height": player.body.get("height", 170),
        "gender": player.gender,
        "endowment": player.body.get("endowment", 0)})
    vitality, strength, level = stats_of(guest)
    name = guest.first_name or guest.name
    lines = [INTRO.format(guest=name),
             partner_line("facesitting", "give", player, guest, rng)]
    if called:
        lines.append(called)
    air = 100
    for number in range(HOME_SEAT_SITS):
        weight = pressure(sitter, rng)
        margin = (endurance(vitality, strength, level, rng) - weight
                  - fatigue(number * 2))
        air += air_change(weight, margin) - smell_drain(sitter)
        tier = "easy" if margin >= 4 else "hard" if margin >= 0 else "bad"
        lines.append(rng.choice(HOLD[tier]).format(guest=name))
        if air <= 0:
            lines.append(PASSED_OUT.format(guest=name))
            break
    satisfy(player.needs, INTIMACY_RELIEF)
    note = bump(guest, player, INTIMACY_BOND)
    if note:
        lines.append(note.strip())
    repository.save(player)
    repository.save(guest)
    return [Message("\n".join(lines))]
