import random

from ...config import WORK_TICK_SECONDS
from ...models import Message, Player
from .. import registry
from ..observers import shift_done
from .content import INCIDENT_CHANCE, INCIDENTS, SESSION_LINES
from .jobs import (
    Job, Shift, barrel_possible, finish, milk_line, milk_word, milk_yield,
    real_share, session_pay,
)
from .moves import moves_for
from .rough import ROUGH_MOVES, roughness_of
from ...towns import town_key
from ..brothel.practices_anatomy import anatomy
from .milk_content import INTROS, NO_BARREL, VARIANTS


TIMED_NOTE = (f"A round takes about {round(WORK_TICK_SECONDS)} s – you can "
              f"let another character act meanwhile.")


def start_timed(player:Player, building:str, job:Job,
                shifts:dict[str, Shift], rng:random.Random, now:float,
                variant:str="") -> list[Message]:
    intro = ""
    if job.key == "milk":
        if variant == "barrel" and not barrel_possible(player):
            return [Message(NO_BARREL, player.name)]
        variant = variant or rng.choice(
            [v for v in VARIANTS if v != "barrel"
             or barrel_possible(player)])
        intro = INTROS[variant] + "\n"
    shifts[player.name] = Shift(building, job, job.sessions,
                                due=now + WORK_TICK_SECONDS, mode=variant)
    return [Message(f"{intro}Your shift as {job.title.lower()} begins: "
                    f"{job.sessions} rounds. {TIMED_NOTE}", player.name)]


def step_timed(player:Player, shift:Shift, shifts:dict[str, Shift],
               rng:random.Random, now:float,
               move:str="") -> list[Message]:
    number = shift.job.sessions - shift.left + 1
    pay = session_pay(player, shift.job, rng)
    dry = shift.job.key == "milk" and real_share(player) == 0
    if shift.job.key == "milk":
        pay = round(pay * milk_yield(player))
    line = (milk_line(player, shift.mode, rng) if shift.job.key == "milk"
            else rng.choice(SESSION_LINES[shift.job.key]))
    if move:
        text, factor = moves_for(shift.job.key, player)[move]
        style = ""
        if move in ROUGH_MOVES:
            harsh, style = roughness_of(town_key(player))
            factor *= harsh
        line = text.format(output=milk_word(player), style=style,
                           **anatomy(player)["words"])
        pay = round(pay * factor)
    lines = [f"{number}/{shift.job.sessions}. {line} +{pay} gold"]
    if dry:
        lines.append("   ✦ All implants: the buckets stay nearly dry, the "
                     "guests only pay for the looks.")
    shift.earned += pay
    if rng.random() < INCIDENT_CHANCE:
        text, bonus = rng.choice(INCIDENTS)
        lines.append(f"   ✦ {text} +{bonus} gold")
        shift.earned += bonus
    spec = registry.get(shift.building)
    if spec is not None and spec.round_hook is not None:
        lines += spec.round_hook(player, shift, rng)
    shift.left -= 1
    shift.due = now + WORK_TICK_SECONDS
    messages = [Message("\n".join(lines), player.name)]
    if shift.left <= 0:
        del shifts[player.name]
        messages += finish(player, shift)
        witness = shift_done(shift.building, shift.job.key)
        if witness:
            messages[-1].witness = witness
    return messages
