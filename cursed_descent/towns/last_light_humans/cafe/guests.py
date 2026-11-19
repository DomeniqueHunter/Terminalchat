import random
from dataclasses import dataclass

from ....config import (
    CRUSH_BASE, CRUSH_BUTT, CRUSH_CLICK, CRUSH_MAX, CRUSH_MIN, CRUSH_OLD_AGE,
    CRUSH_OLD_FACTOR, CRUSH_STEP, CRUSH_VITALITY, CRUSH_WEIGHT,
    CRUSH_YOUNG_AGE, CRUSH_YOUNG_FACTOR,
    HAPPY_DEFAULT,
    CAFE_BERTHA_BUTT, CAFE_BERTHA_CHANCE, CAFE_BERTHA_WEIGHT,
    CAFE_GUEST_BUTT, CAFE_GUEST_WEIGHT, CAFE_NPC_CRUELTY,
    CAFE_NPC_CRUELTY_WEIGHTS, DREAD_BUTT_DIV, DREAD_KILL_POINTS,
    DREAD_RELIEF_DIV, DREAD_TIERS, DREAD_WEIGHT_DIV, HUNG_AIR_DRAIN,
    HUNG_GENDERS,
    HUNG_MIN_ENDOWMENT, HUNG_PAY_BONUS, KIN_HEAVY_BUTT, KIN_HEAVY_WEIGHT,
    PITY_BY_AGE, PITY_OLD_AGE, PITY_YOUNG_AGE, VISIT_GUEST_CHANCE,
    MIN_NPC_AGE, REGULARS_AUTO, SMELL_AIR_MUSK,
    SMELL_AIR_SWEAT,
)
from ....body import bust_label
from ....town_buildings.bodies import DEFAULT_PREF, in_pref, lady_age_height
from ....town_buildings.regular_body import body_values, smell_of
from .content import BERTHA_NAME, GUEST_NAMES, SWALLOW_SOUNDS
from .vore import outcome_from


SQUEEZE_PRESSURE = 4
MAX_SQUEEZE = 3


@dataclass
class Guest:
    name: str
    weight: int
    butt: int
    rider: str = ""
    held: int = 0
    squeeze: int = 0
    pleased: int = 0
    cruel: int = 1
    kills: int = 0
    age: int = 0
    height: int = 0
    wants_lick: bool = False
    kisses: int = 0
    sweat: int = 0
    musk: int = 0
    hesitated: bool = False
    gender: str = "Female"
    bust: int = 0
    endowment: int = 0
    kin: str = ""
    npc: str = ""
    race: str = ""
    happiness: int = HAPPY_DEFAULT
    outcome: str = ""

    def __post_init__(self) -> None:
        self.cruel = max(0, min(len(CAFE_NPC_CRUELTY) - 1, int(self.cruel)))


def guest_butt(weight:int, rng:random.Random) -> int:
    low_w, high_w = CAFE_GUEST_WEIGHT
    low_b, high_b = CAFE_GUEST_BUTT
    share = (weight - low_w) / (high_w - low_w)
    butt = low_b + share * (high_b - low_b) + rng.randint(-12, 12)
    return max(low_b, min(high_b, round(butt)))


def visitor_guest(record:dict) -> Guest:
    guest = Guest(record["name"], record["weight"], record["butt"],
                  cruel=record["cruel"], age=record["age"],
                  height=record["height"], gender=record["gender"],
                  bust=record["bust"], endowment=record["endowment"],
                  npc=record["npc"], race=record.get("race", ""))
    guest.sweat, guest.musk = smell_of("cafe", guest.name)
    guest.outcome = outcome_from(record)
    return guest


def bertha_guest(regulars=None) -> Guest:
    stored = regulars.owner_visit("cafe", BERTHA_NAME) if regulars else None
    if not stored:
        return Guest(BERTHA_NAME, CAFE_BERTHA_WEIGHT, CAFE_BERTHA_BUTT)
    return Guest(BERTHA_NAME, stored["weight"], stored["butt"],
                 kills=stored.get("kills", 0), age=stored.get("age", 0),
                 height=stored.get("height", 0), gender=stored["gender"],
                 bust=stored.get("bust", 0), npc=stored["npc"],
                 race=stored.get("race", ""),
                 happiness=stored.get("happiness", HAPPY_DEFAULT),
                 outcome=outcome_from(stored))


def new_guest(rng:random.Random, regulars=None,
              pref:tuple[int, int]=DEFAULT_PREF) -> Guest:
    if rng.random() < CAFE_BERTHA_CHANCE:
        return bertha_guest(regulars)
    visitors = regulars.visiting("cafe") if regulars is not None else []
    if visitors and rng.random() < VISIT_GUEST_CHANCE:
        record = rng.choice(visitors)
        stored = regulars.visit("cafe", record)
        guest = visitor_guest(record)
        guest.kills = stored.get("kills", 0)
        guest.happiness = stored.get("happiness", HAPPY_DEFAULT)
        return guest
    if regulars is not None:
        known = regulars.pick("cafe", rng)
        if known is not None and not in_pref(
                known.get("age", pref[0]), pref):
            known = None
        if known is not None:
            known = regulars.remember("cafe", known)
            age, height = lady_age_height(rng, pref)
            guest = Guest(
                known["name"],
                known.get("weight", rng.randint(*CAFE_GUEST_WEIGHT)),
                known.get("butt", rng.randint(*CAFE_GUEST_BUTT)),
                cruel=known.get("cruel", 1), kills=known.get("kills", 0),
                age=max(MIN_NPC_AGE, known.get("age", age)),
                height=known.get("height", height),
                sweat=known.get("sweat", 0), musk=known.get("musk", 0),
                gender=known.get("gender", "Female"),
                bust=known.get("bust", 0),
                endowment=known.get("endowment", 0))
            guest.happiness = known.get("happiness", HAPPY_DEFAULT)
            guest.outcome = outcome_from(known)
            regulars.fill("cafe", guest.name, {
                "weight": guest.weight, "butt": guest.butt,
                "age": guest.age, "height": guest.height,
                "cruel": guest.cruel})
            return guest
    weight = rng.randint(*CAFE_GUEST_WEIGHT)
    guest = Guest(rng.choice(GUEST_NAMES), weight,
                  guest_butt(weight, rng),
                  cruel=rng.choices((0, 1, 2), CAFE_NPC_CRUELTY_WEIGHTS)[0])
    guest.age, guest.height = lady_age_height(rng, pref)
    guest.sweat, guest.musk = smell_of("cafe", guest.name)
    traits = body_values("cafe", f"{guest.name}|{guest.age}|{guest.weight}"
                                 f"|{guest.butt}")
    guest.gender, guest.bust = traits["gender"], traits["bust"]
    guest.endowment = traits["endowment"]
    if regulars is not None and REGULARS_AUTO:
        stored = regulars.remember("cafe", {"name": guest.name,
                                            "age": guest.age,
                                            "height": guest.height,
                                            "weight": guest.weight,
                                            "butt": guest.butt,
                                            "cruel": guest.cruel})
        guest.weight, guest.butt = stored["weight"], stored["butt"]
        guest.cruel = stored.get("cruel", 1)
        guest.kills = stored.get("kills", 0)
        guest.age = stored.get("age", guest.age)
        guest.height = stored.get("height", guest.height)
    return guest


def guest_record(guest:Guest) -> dict:
    return {"name": guest.name, "weight": guest.weight,
            "butt": guest.butt, "cruel": guest.cruel, "kills": guest.kills,
            "age": guest.age, "height": guest.height,
            "sweat": guest.sweat, "musk": guest.musk,
            "gender": guest.gender, "bust": guest.bust,
            "endowment": guest.endowment}


def swallow_sound(name:str, rng:random.Random) -> str:
    return rng.choice(SWALLOW_SOUNDS).format(name=name)


def rider_guest(name:str, weight:int, butt:int, age:int=0,
                height:int=0, gender:str="Female",
                endowment:int=0) -> Guest:
    return Guest(name, weight, butt, rider=name, age=age, height=height,
                 gender=gender, endowment=endowment)


def pity_of(guest:Guest) -> float:
    young, middle, old = PITY_BY_AGE
    if not guest.age:
        return 0.0
    if guest.age < PITY_YOUNG_AGE:
        return young
    if guest.age >= PITY_OLD_AGE:
        return old
    return middle


def is_hung(guest:Guest) -> bool:
    return (guest.gender in HUNG_GENDERS
            and guest.endowment >= HUNG_MIN_ENDOWMENT)


def hung_drain(guest:Guest) -> int:
    return HUNG_AIR_DRAIN if is_hung(guest) else 0


def hung_pay_factor(guest:Guest) -> float:
    return 1 + HUNG_PAY_BONUS if is_hung(guest) else 1.0


def heavy_futa(guest:Guest) -> bool:
    return (guest.gender in HUNG_GENDERS and guest.butt >= KIN_HEAVY_BUTT
            and guest.weight >= KIN_HEAVY_WEIGHT)


def base_pressure(guest:Guest) -> int:
    return guest.weight // 12 + guest.butt // 14


def dread_tier(guest:Guest, vitality:int, level:int) -> int:
    score = (guest.butt // DREAD_BUTT_DIV + guest.weight // DREAD_WEIGHT_DIV
             + guest.kills * DREAD_KILL_POINTS
             - (vitality + level) // DREAD_RELIEF_DIV)
    return sum(score >= limit for limit in DREAD_TIERS)


def dread_now(guest:Guest, vitality:int, level:int) -> int:
    if guest.rider:
        return 0
    return max(0, dread_tier(guest, vitality, level) - guest.held)


def trait_note(guest:Guest) -> str:
    if guest.gender == "Female":
        return ""
    parts = [guest.gender]
    if guest.bust > 0:
        parts.append(f"{bust_label(guest.bust)} bust")
    if guest.endowment > 0:
        parts.append(f"{guest.endowment} cm of cock")
    return f"({guest.name}: {', '.join(parts)})"


def smell_drain(guest:Guest) -> int:
    return (round(guest.musk * SMELL_AIR_MUSK
                  + guest.sweat * SMELL_AIR_SWEAT) + hung_drain(guest))


def pressure(guest:Guest, rng:random.Random) -> int:
    return (base_pressure(guest) + rng.randint(0, 8)
            + guest.squeeze * SQUEEZE_PRESSURE)


def endurance(vitality:int, strength:int, level:int,
              rng:random.Random) -> int:
    return vitality * 2 + strength + level + rng.randint(0, 8)


def difficulty(guest:Guest, vitality:int, strength:int, level:int) -> str:
    gap = base_pressure(guest) + 4 - (vitality * 2 + strength + level + 4)
    if gap <= -3:
        return "light"
    if gap <= 4:
        return "heavy"
    return "crushing"


PANIC_STEPS = ((0.95, "frantic"), (0.7, "panic"), (0.4, "strained"),
               (0.15, "uneasy"))


def panic_tier(done:int, total:int) -> str:
    share = done / max(total, 1)
    return next((tier for limit, tier in PANIC_STEPS if share >= limit), "")


def fatigue(done:int) -> int:
    return done // 4


def age_factor(age:int) -> float:
    if age <= 0:
        return 1.0
    if age <= CRUSH_YOUNG_AGE:
        return CRUSH_YOUNG_FACTOR
    if age >= CRUSH_OLD_AGE:
        return CRUSH_OLD_FACTOR
    return 1.0


DEADLY = {"on": False}


def deadly_toggle() -> str:
    DEADLY["on"] = not DEADLY["on"]
    state = "ON: every cafe lady crushes for sure" if DEADLY["on"] else "OFF"
    return f"Deadly dame {state}."


def click_crush(chance:float, rng:random.Random | None) -> bool:
    return bool(chance and rng is not None
                and rng.random() < min(1.0, chance * CRUSH_CLICK))


def crush_tier(chance:float) -> int:
    if chance <= 0:
        return 0
    return 1 if chance < 0.1 else 2 if chance < 0.2 else 3


def crush_chance(butt:int, weight:int, squeeze:int, vitality:int=0,
                 age:int=0) -> float:
    if DEADLY["on"]:
        return 1.0
    if squeeze < MAX_SQUEEZE or (butt < CRUSH_BUTT and weight < CRUSH_WEIGHT):
        return 0.0
    over = (max(0, butt - CRUSH_BUTT) // 10
            + max(0, weight - CRUSH_WEIGHT) // 10)
    chance = CRUSH_BASE + CRUSH_STEP * over - CRUSH_VITALITY * vitality
    chance *= age_factor(age)
    return max(CRUSH_MIN, min(CRUSH_MAX, chance))
