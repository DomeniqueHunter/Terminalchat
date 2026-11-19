import random
from typing import Any

from ....config import (
    CAFE_DEATH_CHANCE, CAFE_DEATH_MARGIN, HOME_SEAT_SITS,
    PITY_AIR, PITY_AIR_LIMIT, PITY_EASE_CHANCE,
)
from ....models import Player
from ....town_buildings.regular_body import smell_note
from .content import HOLD_BAD, HOLD_EASY, HOLD_HARD, PITY_EASE
from .guests import (
    Guest, endurance, fatigue, pity_of, pressure, smell_drain,
)
from .seat import air_change, fate_for, record_kill, stats_of
from .vore import outcome_from
from .training import (
    VisitOptions, add_training, train_cut, train_margin, training_of,
)


WARNING = ("⚠ At {place} you are only her seat: {sits} sittings, "
           "no control, no safeword, and she decides when it is over. "
           "You may not survive it. Options: gentle|normal|hard, "
           "short|long. Chosen: {chosen}. No money changes hands. "
           "[{command} {name} confirm] to go anyway.")
NO_CONTROL = ("You cannot move, you cannot call out. Nobody asked "
              "whether you wanted it to stop.")
NO_AIR = ("Your lungs find nothing but {guest} and her smell. The last "
          "breath never comes.")
NO_BREAK = "{name} shifts her weight and settles for the next sitting."


def guest_of(record:dict[str, Any]) -> Guest:
    return Guest(record["name"], record.get("weight", 80),
                 record.get("butt", 110), cruel=record.get("cruel", 1),
                 kills=record.get("kills", 0), age=record.get("age", 30),
                 height=record.get("height", 170),
                 sweat=record.get("sweat", 0), musk=record.get("musk", 0),
                 gender=record.get("gender", "Female"),
                 endowment=record.get("endowment", 0),
                 outcome=outcome_from(record))


def home_sittings(player:Player, record:dict[str, Any],
                  rng:random.Random, regulars=None,
                  options:VisitOptions | None=None
                  ) -> tuple[list[str], int, str]:
    options = options or VisitOptions()
    guest = guest_of(record)
    trained = training_of(player, guest.name)
    vitality, strength, level = stats_of(player)
    lines = [NO_CONTROL]
    note = smell_note(guest.name, guest.sweat, guest.musk)
    if note:
        lines.insert(0, note)
    earned = 0
    air = 100
    for number in range(options.sits):
        done = number * 2
        weight = pressure(guest, rng)
        margin = (endurance(vitality, strength, level, rng)
                  - weight - fatigue(done) + options.margin_mod
                  + train_margin(trained))
        air += air_change(weight, margin) - smell_drain(guest)
        if air < PITY_AIR_LIMIT and rng.random() < (
                PITY_EASE_CHANCE * pity_of(guest)):
            air += PITY_AIR
            lines.append(PITY_EASE.format(guest=guest.name))
        if air <= 0:
            record_kill(guest, regulars)
            lines.append(NO_AIR.format(guest=guest.name))
            return lines, earned, fate_for(player, guest, rng)
        chance = (CAFE_DEATH_CHANCE * (0.75 + 0.25 * guest.cruel)
                  * options.risk * (1 - train_cut(trained)))
        if margin <= -CAFE_DEATH_MARGIN and rng.random() < chance:
            record_kill(guest, regulars)
            lines.append(rng.choice(HOLD_BAD).format(guest=guest.name))
            return lines, earned, fate_for(player, guest, rng)
        if margin >= 4:
            text = rng.choice(HOLD_EASY)
        elif margin >= 0:
            text = rng.choice(HOLD_HARD)
        else:
            text = rng.choice(HOLD_BAD)
        lines.append(text.format(guest=guest.name))
        if number < options.sits - 1:
            lines.append(NO_BREAK.format(name=guest.name))
    return lines, earned, ""
