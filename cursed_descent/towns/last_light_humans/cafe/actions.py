import random

from ....config import (
    HAPPY_DEFAULT, HAPPY_MAX, HAPPY_PAY,
    PAT_PUNISH_AIR, PAT_PUNISH_MIDDLE,
    CAFE_ARRIVAL_SECONDS, CAFE_ENCOURAGE_PAY, CAFE_PAT_CHANCE,
    CAFE_PAT_MAX, CAFE_PAT_PLEASED,
)
from ....models import Message, Player
from ....town_buildings.work.jobs import Shift
from .content import (
    ACT_BREATH, ACT_GIVEUP, PAT_PUNISH, ACT_PAT_FAIL, ACT_PAT_OK, ACT_STRUGGLE_FAIL,
    ACT_STRUGGLE_OK, ACT_KISS, ACT_KISS_EASE, RIDER_KISS, RIDER_KISS_SELF,
    ACT_ENCOURAGE, ACT_ENCOURAGE_RIDER, RIDER_ENCOURAGED,
    ACT_FRENCH_KISS, KISS_STREAK, KISS_STREAK_PAY, ACT_LICK, LICK_TASTE, NPC_DEMAND_PAID, ACT_PLEASED, RIDER_LICK_TASTE, RIDER_LICK, RIDER_LICK_SELF, RIDER_PAT, RIDER_PAT_SELF, RIDER_STRUGGLE,
    RIDER_STRUGGLE_SELF, SEAT_NO_GUEST,
)
from ....races import RACES
from ....town_buildings.regular_body import smell_tier
from .guests import MAX_SQUEEZE, SQUEEZE_PRESSURE, base_pressure
from .kin_seat import KISS, LICK, kin_text
from .seat import active_seat, hold, remaining


SEAT_ACTIONS = ("wait", "breath", "pat", "struggle", "giveup", "kiss", "lick",
                "encourage")


def dislodge(shift:Shift, now:float) -> None:
    shift.client = None
    shift.due = now + CAFE_ARRIVAL_SECONDS


def act(player:Player, shifts:dict[str, Shift], rng:random.Random,
        now:float, action:str, regulars=None) -> tuple[list[Message], str]:
    shift = active_seat(player, shifts)
    guest = shift.client if shift is not None else None
    if shift is None or guest is None:
        seconds = remaining(shift, now) if shift is not None else 0
        return [Message(SEAT_NO_GUEST.format(seconds=seconds),
                        player.name)], ""
    if action != "kiss":
        guest.kisses = 0
    if action == "wait":
        return hold(player, shifts, rng, now, regulars=regulars)
    if action == "breath":
        shift.winded = 1
        shift.air = min(100, shift.air + 20)
        return hold(player, shifts, rng, now, regulars=regulars, bonus=5, lead=[ACT_BREATH])
    if action == "giveup":
        return hold(player, shifts, rng, now, regulars=regulars, bonus=6, pay_factor=1.5,
                    lead=[ACT_GIVEUP])
    if action == "encourage":
        if guest.rider:
            return [Message(ACT_ENCOURAGE_RIDER.format(rider=guest.name),
                            player.name),
                    Message(RIDER_ENCOURAGED.format(seat=player.name),
                            guest.rider)], ""
        guest.pleased = min(3, guest.pleased + 1)
        return hold(player, shifts, rng, now, regulars=regulars,
                    pay_factor=CAFE_ENCOURAGE_PAY,
                    lead=[ACT_ENCOURAGE.format(guest=guest.name)])
    if guest.rider:
        return rider_signal(player, guest.name, action), ""
    if action in ("kiss", "lick"):
        licking = action == "lick"
        paid = licking and guest.wants_lick
        guest.wants_lick = False
        lead = (ACT_LICK if licking else ACT_KISS).format(guest=guest.name)
        french = False
        if not licking:
            guest.kisses += 1
            if guest.kisses >= KISS_STREAK:
                guest.kisses = 0
                french = True
                lead = ACT_FRENCH_KISS.format(guest=guest.name)
        if rng.random() < 0.5 and guest.squeeze > 0:
            guest.squeeze -= 1
            lead += ACT_KISS_EASE
        guest.pleased = min(3, guest.pleased + 1)
        guest.happiness = cheer(regulars, guest, 1)
        lead += ACT_PLEASED
        if licking:
            bonus = RACES[guest.race].scent if guest.race in RACES else (0, 0)
            tier = smell_tier(max(guest.sweat + bonus[0],
                                  guest.musk + bonus[1]))
            lead += " " + LICK_TASTE[tier]
            lead += skin_line(guest, True)
        elif guest.race in RACES:
            lead += skin_line(guest, False)
        if guest.kin:
            lead += "\n" + kin_text(LICK if licking else KISS, guest,
                                    player.name, rng)
        if paid:
            lead += NPC_DEMAND_PAID
        factor = (1.4 if licking else 1.3) * (1.5 if paid else 1.0)
        factor *= 1 + HAPPY_PAY * (guest.happiness - HAPPY_DEFAULT)
        if french:
            factor *= KISS_STREAK_PAY
        return hold(player, shifts, rng, now, regulars=regulars,
                    pay_factor=factor, lead=[lead])
    if action == "pat":
        if punishes_pat(guest, rng):
            kind = rng.choice(tuple(PAT_PUNISH))
            return punish_pat(player, shifts, rng, now, shift, guest, kind,
                              regulars)
        if rng.random() < min(CAFE_PAT_MAX,
                              CAFE_PAT_CHANCE + CAFE_PAT_PLEASED * guest.pleased):
            dislodge(shift, now)
            return [Message(ACT_PAT_OK.format(guest=guest.name),
                            player.name)], ""
        guest.squeeze = min(MAX_SQUEEZE, guest.squeeze + 1)
        return hold(player, shifts, rng, now, regulars=regulars,
                    lead=[ACT_PAT_FAIL.format(guest=guest.name)])
    effort = (player.stats["strength"] + player.stats["agility"]
              + rng.randint(0, 8))
    need = base_pressure(guest) + guest.squeeze * SQUEEZE_PRESSURE + 8
    if effort >= need:
        cheer(regulars, guest, -1)
        dislodge(shift, now)
        return [Message(ACT_STRUGGLE_OK.format(guest=guest.name),
                        player.name)], ""
    guest.squeeze = min(MAX_SQUEEZE, guest.squeeze + 1)
    return hold(player, shifts, rng, now, regulars=regulars, bonus=-4,
                lead=[ACT_STRUGGLE_FAIL.format(guest=guest.name)])


def cheer(regulars, guest, delta:int) -> int:
    if regulars is not None and guest.name:
        return regulars.mood("cafe", guest.name, delta)
    return max(0, min(HAPPY_MAX, guest.happiness + delta))


def skin_line(guest, licking:bool) -> str:
    smell, taste = RACES[guest.race].skin if guest.race in RACES else ("", "")
    if not smell:
        return ""
    if licking:
        return f" Her skin smells of {smell} and tastes of {taste}."
    return f" A trace of {smell} stays on your lips."


def punishes_pat(guest, rng:random.Random) -> bool:
    if guest.cruel >= 2:
        return True
    return guest.cruel == 1 and rng.random() < PAT_PUNISH_MIDDLE


def punish_pat(player:Player, shifts:dict[str, Shift], rng:random.Random,
               now:float, shift:Shift, guest, kind:str,
               regulars) -> tuple[list[Message], str]:
    guest.pleased = 0
    factor = 1.0
    if kind == "clamp":
        guest.squeeze = min(MAX_SQUEEZE, guest.squeeze + 2)
    elif kind == "air":
        shift.air = max(0, shift.air - PAT_PUNISH_AIR)
    elif kind == "apology":
        guest.wants_lick = True
    else:
        shift.winded = min(2, shift.winded + 2)
        factor = 0.7
    return hold(player, shifts, rng, now, regulars=regulars,
                pay_factor=factor,
                lead=[PAT_PUNISH[kind].format(guest=guest.name)])


def rider_signal(player:Player, rider:str, action:str) -> list[Message]:
    if action == "lick":
        return [Message(RIDER_LICK_SELF.format(rider=rider) + " "
                        + RIDER_LICK_TASTE, player.name),
                Message(RIDER_LICK.format(seat=player.name), rider)]
    if action == "kiss":
        return [Message(RIDER_KISS_SELF.format(rider=rider), player.name),
                Message(RIDER_KISS.format(seat=player.name), rider)]
    if action == "pat":
        return [Message(RIDER_PAT_SELF.format(rider=rider), player.name),
                Message(RIDER_PAT.format(seat=player.name), rider)]
    return [Message(RIDER_STRUGGLE_SELF.format(rider=rider), player.name),
            Message(RIDER_STRUGGLE.format(seat=player.name), rider)]
