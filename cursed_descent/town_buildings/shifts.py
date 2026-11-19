import random

from ..config import WORK_TICK_SECONDS
from ..models import Message, Player
from .brothel.shift import start_shift as brothel_shift
from ..towns.last_light_humans.cafe.seat import start_seat
from ..towns.last_light_humans.cafe.stools import trainer_shift
from .work.timed import start_timed
from .work.jobs import (
    Shift, auto_shift, building_menu, closed, find_job, find_variant,
)


BROTHEL_JOBS = {"whore", "escort"}


def mode_of(text:str) -> str:
    words = text.casefold().split()
    if "domina" in words or "dom" in words:
        return "domina"
    if "sub" in words or "submissive" in words:
        return "sub"
    return ""


def work(player:Player, building:str, text:str, in_run:bool,
         shifts:dict[str, Shift], rng:random.Random,
         now:float=0.0, regulars=None,
         timed:bool=False) -> list[Message]:
    if in_run:
        return closed(building, player)
    if player.name in shifts:
        return [Message("Finish your current shift first. "
                        "[serve <act>]", player.name)]
    job = find_job(building, text)
    if job is None:
        return building_menu(building, player)
    if building == "brothel" and job.key in BROTHEL_JOBS:
        messages = brothel_shift(player, job, shifts, rng, regulars,
                                 mode_of(text))
        if timed and player.name in shifts:
            shifts[player.name].due = now + WORK_TICK_SECONDS
            shifts[player.name].endless = job.key == "whore"
        return messages
    if building == "cafe" and player.gender == "Male" and (
            job.key != "seat"):
        return [Message("Madame Bertha taps her cane: 'Men are furniture "
                        "here, dear. [job cafe seat] or nothing.'",
                        player.name)]
    if building == "cafe" and job.key == "trainer":
        return trainer_shift(player, job, rng)
    if building == "cafe" and job.key == "seat":
        return start_seat(player, job, shifts, rng, now)
    if timed:
        messages = start_timed(player, building, job, shifts, rng, now,
                               find_variant(text))
        if building == "brothel":
            from .brothel.shift import rose_visit
            messages = rose_visit(player, rng) + messages
        return messages
    messages = auto_shift(player, building, job, rng, find_variant(text))
    if building == "brothel":
        from .brothel.shift import rose_visit
        messages = rose_visit(player, rng) + messages
    return messages
