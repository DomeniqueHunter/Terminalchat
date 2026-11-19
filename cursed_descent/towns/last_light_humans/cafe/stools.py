import random
from dataclasses import dataclass

from ....config import (
    CAFE_DEATH_CHANCE, MIN_NPC_AGE, CAFE_REACTION_SECONDS, CAFE_RIDE_ROUNDS,
    CAFE_ENGULF_BUTT, CAFE_ENGULF_WEIGHT, CAFE_RIDER_RELIEF, CAFE_SWALLOW_CHANCE,
    CAFE_TICKET,
)
from ....models import Message, Player
from ....needs import satisfy
from ....town_buildings.bodies import DEFAULT_PREF, STOOL_AGES, pick_age
from .content import (
    CLENCH_MAX, CLENCH_RIDER, CLENCH_PLEAS, CRUSH_POPS, CRUSH_WHIMPER, CRUSH_RIDER_STOOL, CRUSH_WARNING, PANIC_LINES, RIDE_COLLAPSE, WIGGLE_RIDER, SWALLOW_STOOL_RANDOM, RIDE_DEATH, RIDE_LEAN, RIDE_OVER,
    STOOL_REACTION,
)
from .guests import (
    swallow_sound,
    MAX_SQUEEZE, SQUEEZE_PRESSURE, Guest, base_pressure, fatigue,
    click_crush, crush_chance, crush_tier, panic_tier,
)
from ....town_buildings.work.jobs import Job, Shift, finish, session_pay


NAMES = ("Tom", "Bastian", "Jonas", "Piet", "Lukas", "Henrik", "Ole",
         "Anselm", "Fritz", "Matteo", "Rolf", "Cedric", "Bruno", "Emil",
         "Karsten", "Dario", "Willem", "Jasper", "Nils", "Torben")
BUILDS = ("Slim", "Average", "Toned", "Muscular", "Heavy")
MOODS = ("nervous", "eager", "resigned", "proud", "dazed")
FREE_COUNTS = (0, 1, 2, 3)
FREE_WEIGHTS = (25, 35, 30, 10)

HEIGHT_WORDS = ((165, "short and compact"), (180, "of average height"),
                (999, "tall and long-limbed"))
BUILD_WORDS = {
    "Slim": "a slim frame with narrow shoulders and a bony, honest back",
    "Average": "an ordinary build, soft in the middle and willing",
    "Toned": "a toned body, lean muscle under warm skin",
    "Muscular": "broad shoulders and a back like a table, thick thighs "
                "braced on the floor",
    "Heavy": "a heavy, solid frame with a wide back and a lot of padding",
}
MOOD_WORDS = {
    "nervous": "He fidgets, swallows, and keeps looking at your hips.",
    "eager": "He is already on all fours, eyes bright, grinning up at you.",
    "resigned": "He sighs, lowers himself, and waits like a man who has "
                "done this before.",
    "proud": "He lifts his chin and presents his back like a throne.",
    "dazed": "He stares at nothing, humming quietly, wholly yours.",
}


@dataclass
class Stool:
    name: str
    age: int
    height: int
    weight: int
    build: str
    muscle: int
    mood: str

    @property
    def stamina(self) -> int:
        return 6 + self.muscle // 6 + self.weight // 20


def new_stool(rng:random.Random, pref:tuple[int, int] = DEFAULT_PREF
              ) -> Stool:
    build = rng.choice(BUILDS)
    weight = {"Slim": 62, "Average": 75, "Toned": 78, "Muscular": 92,
              "Heavy": 112}[build] + rng.randint(-6, 8)
    muscle = {"Slim": 15, "Average": 25, "Toned": 45, "Muscular": 70,
              "Heavy": 35}[build] + rng.randint(-5, 8)
    return Stool(rng.choice(NAMES), pick_age(rng, STOOL_AGES, pref),
                 rng.randint(160, 198), weight, build, muscle,
                 rng.choice(MOODS))


def refresh_stools(rng:random.Random, pref:tuple[int, int] = DEFAULT_PREF
                   ) -> list[Stool]:
    count = rng.choices(FREE_COUNTS, FREE_WEIGHTS)[0]
    return [new_stool(rng, pref) for _ in range(count)]


def height_word(height:int) -> str:
    return next(word for limit, word in HEIGHT_WORDS if height < limit)


def blurb(stool:Stool) -> str:
    return (f"{stool.name} ({stool.age}), {stool.height} cm, "
            f"{stool.weight} kg, {stool.build.lower()}")


def describe(stool:Stool) -> str:
    return (f"{stool.name}, {stool.age}, {height_word(stool.height)} "
            f"({stool.height} cm, {stool.weight} kg) – "
            f"{BUILD_WORDS[stool.build]}. {MOOD_WORDS[stool.mood]}")


def free_list(stools:list[Stool]) -> str:
    if not stools:
        return "No free stool right now – all the lads are already in use."
    lines = ["Free stools ([sit <nr>]):"]
    lines += [f"  {number}. {blurb(stool)}"
              for number, stool in enumerate(stools, 1)]
    return "\n".join(lines)


def pick_stool(stools:list[Stool], text:str) -> Stool | None:
    wanted = text.strip().casefold()
    if wanted.isdigit() and 1 <= int(wanted) <= len(stools):
        return stools[int(wanted) - 1]
    return next((stool for stool in stools
                 if stool.name.casefold() == wanted), None)


@dataclass
class Ride:
    stool: Stool
    squeeze: int = 0
    rounds: int = 0
    due: float = 0.0
    extra: int = 0
    shaken: int = 0
    crush_now: bool = False


def lady_of(rider:Player, extra:int=0) -> Guest:
    return Guest(rider.name, rider.body.get("weight", 65) + extra,
                 rider.body.get("butt", 95))


def start_ride(rider:Player, stool:Stool,
               now:float) -> tuple[Ride | None, list[Message]]:
    if rider.gold < CAFE_TICKET:
        return None, [Message(f"A free stool costs {CAFE_TICKET} gold.",
                              rider.name)]
    rider.gold -= CAFE_TICKET
    satisfy(rider.needs, {"arousal": -CAFE_RIDER_RELIEF})
    ride = Ride(stool, due=now + CAFE_REACTION_SECONDS)
    return ride, [Message(
        f"You pay {CAFE_TICKET} gold and take {stool.name}.\n"
        f"{describe(stool)}\nNext reaction in {CAFE_REACTION_SECONDS} s – "
        f"[stay], [lean] (more weight, more suffering) or [rise] to "
        f"spare him.", rider.name)]


def ride_lean(ride:Ride, rng:random.Random) -> str:
    if ride.squeeze >= MAX_SQUEEZE:
        return f"You cannot press any harder – {ride.stool.name} is " \
               f"taking all of it."
    ride.squeeze += 1
    return rng.choice(RIDE_LEAN).format(name=ride.stool.name)


def ride_torment(ride:Ride, kind:str, rider:Player,
                 rng:random.Random | None=None) -> list[str]:
    name = ride.stool.name
    if kind == "clench":
        maxed = ride.squeeze >= MAX_SQUEEZE
        ride.squeeze = min(MAX_SQUEEZE, ride.squeeze + 1)
        lady = lady_of(rider, ride.extra)
        chance = crush_chance(lady.butt, lady.weight, ride.squeeze, 0,
                              ride.stool.age)
        if maxed and click_crush(chance, rng):
            ride.crush_now, ride.due = True, 0.0
        tier = crush_tier(chance)
        warn = (rng.choice(CRUSH_WHIMPER[tier]).format(seat=name)
                if tier and rng else "")
        plea = (" " + rng.choice(CLENCH_PLEAS[ride.squeeze]).format(
            seat=name) if rng else "")
        return [CLENCH_RIDER.format(seat=name)
                + (CLENCH_MAX if maxed else "") + plea + warn]
    ride.shaken = min(2, ride.shaken + 1)
    return [WIGGLE_RIDER.format(seat=name)]


def ride_round(ride:Ride, rider:Player, rng:random.Random,
               now:float) -> tuple[list[Message], str]:
    stool = ride.stool
    margin = (stool.stamina - base_pressure(lady_of(rider, ride.extra))
              - ride.squeeze * SQUEEZE_PRESSURE - fatigue(ride.rounds)
              - rng.randint(0, 6) - ride.shaken * 3)
    ride.shaken = 0
    ride.rounds += 1
    ride.due = now + CAFE_REACTION_SECONDS
    lady = lady_of(rider, ride.extra)
    crush = crush_chance(lady.butt, lady.weight, ride.squeeze, 0,
                         stool.age)
    if ride.crush_now or (crush and rng.random() < crush):
        return [Message(CRUSH_RIDER_STOOL.format(name=stool.name)
                        + f" {rng.choice(CRUSH_POPS)}", rider.name)], "dead"
    if (margin < 0 and lady.butt >= CAFE_ENGULF_BUTT
            and lady.weight >= CAFE_ENGULF_WEIGHT
            and rng.random() < CAFE_SWALLOW_CHANCE):
        return [Message(SWALLOW_STOOL_RANDOM.format(name=stool.name)
                        + "\n" + swallow_sound(stool.name, rng),
                        rider.name)], "swallowed"
    if margin >= 0:
        line = f"{stool.name} holds, flushed and steady."
        tier = panic_tier(ride.rounds, CAFE_RIDE_ROUNDS)
        if tier in ("panic", "frantic"):
            line = rng.choice(PANIC_LINES[tier]).format(name=stool.name)
    elif margin >= -6:
        line = rng.choice(STOOL_REACTION).format(name=stool.name)
        tier = panic_tier(ride.rounds, CAFE_RIDE_ROUNDS)
        if tier:
            line = rng.choice(PANIC_LINES[tier]).format(name=stool.name)
    elif rng.random() < CAFE_DEATH_CHANCE:
        return [Message(RIDE_DEATH.format(name=stool.name), rider.name)
                ], "dead"
    else:
        return [Message(RIDE_COLLAPSE.format(name=stool.name),
                        rider.name)], "collapsed"
    if ride.rounds >= CAFE_RIDE_ROUNDS:
        return [Message(f"{line}\n{RIDE_OVER.format(name=stool.name)}",
                        rider.name)], "over"
    return [Message(f"{line} (round {ride.rounds}/{CAFE_RIDE_ROUNDS}, next "
                    f"in {CAFE_REACTION_SECONDS} s)", rider.name)], ""


TRAIN_LINES = (
    "You break him in slowly, until he stops trembling.",
    "You show him the proper posture, then sit to test it.",
    "You hold the weight a little longer each minute, teaching him to "
    "breathe under you.",
    "You correct his back with a firm palm and settle down again.",
)


def trainer_shift(player:Player, job:Job,
                  rng:random.Random) -> list[Message]:
    shift = Shift("cafe", job, job.sessions)
    lines = ["Bertha hands you a list of new stools to break in."]
    for number in range(1, job.sessions + 1):
        stool = new_stool(rng)
        pay = session_pay(player, job, rng)
        lines.append(f"{number}. {describe(stool)}\n   "
                     f"{rng.choice(TRAIN_LINES)} +{pay} gold")
        shift.earned += pay
    return [Message("\n".join(lines), player.name)] + finish(player, shift)
