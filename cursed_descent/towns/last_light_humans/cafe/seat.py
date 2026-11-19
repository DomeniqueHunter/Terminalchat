import random

from ....config import (
    CAFE_ARRIVAL_SECONDS, CAFE_CRUSH_WEIGHT, CAFE_DEATH_CHANCE, CAFE_DEATH_MARGIN, CAFE_ENGULF_BUTT,
    CAFE_ENGULF_CHANCE, CAFE_ENGULF_WEIGHT, CAFE_REACTION_SECONDS,
    CAFE_FAMILY_CHANCE, CAFE_FAMILY_TIP, CAFE_NPC_ACTION_CHANCE, CAFE_NPC_CRUELTY, CAFE_RIDER_RELIEF,
    CAFE_SWALLOW_CHANCE, CAFE_SWALLOW_RATIO, DREAD_HESITATE_AIR,
    DREAD_HESITATE_CHANCE, DREAD_PAY_CUT, DREAD_ROUND_PENALTY,
    PITY_AIR, PITY_AIR_LIMIT, PITY_EASE_CHANCE, RIDER_RAISE_AIR,
    RIDER_RAISE_COOLDOWN, VAGINA_GENDERS,
)
from ....models import Message, Player
from ....needs import satisfy
from ....town_buildings.work.jobs import Job, Shift, finish, session_pay
from ....town_buildings.bodies import body_line, pref_of
from ....town_buildings.family import SIT_LINES, role_of
from .swallow import grow_guest
from .kin_seat import CLENCH, RISE, ROUND, SIT, WIGGLE, kin_text
from ....npcs.visiting import quirk_line
from ....town_buildings.regular_body import smell_note
from .ambient import family_scene, make_family
from .training import train_cut, training_of
from .content import (
    CLENCH_PLEAS, CRUSH_POPS, HOME_DONE, RIDER_RAISE, RIDER_RAISE_WAIT, CRUSH_SEAT, CRUSH_WARNING, CRUSH_WHIMPER, PITY_EASE,
    COLLAPSE_CRUSHED, COLLAPSE_DRAGGED, COLLAPSE_LEAD, COLLAPSE_RIDER,
    COLLAPSE_RIDER_CRUSHED,
    KILLS_NOTE,
    NPC_CLENCH, NPC_DEMAND, NPC_DEMAND_IGNORED, NPC_WIGGLE,
    CLENCH_MAX, CLENCH_RIDER, CLENCH_SEAT, TORMENT_NONE, WIGGLE_RIDER,
    WIGGLE_SEAT,
    SWALLOW_NONE, SWALLOW_NPC, SWALLOW_TOO_SMALL,
    BERTHA_NAME, BERTHA_PROBE,
    BERTHA_DEATH, COMPLAINTS_DEATH, COMPLAINTS_FAIL, CRUSHING, DESPERATE, DREAD_LINES,
    PANIC_LINES, SAFEWORD_FROZEN,
    GUEST_ARRIVES, GUEST_LEAVES, SEAT_MUTE, SEAT_NO_GUEST,
    WITNESS_DONE, WITNESS_GUEST, WITNESS_GUEST_BIG, WITNESS_QUIT,
    WITNESS_RIDER, WITNESS_SEAT,
    SEAT_WAITING, DESPERATE_RIDER, GUEST_INTRO, HEAVY, HOLD_BAD,
    HOLD_EASY, HOLD_HARD, HOLD_WARN,
    LIGHT, RIDER_GONE, RIDER_HOLD, RIDER_RISE, RIDER_TO_SEAT, RIDER_WELCOME,
    RIDER_LEAN, RIDER_LEAN_MAX, RIDER_STAY, SEAT_REACTION,
    SEAT_DONE, SEAT_INTRO, SEAT_LOCKED, SEAT_STUCK, SEAT_NO_SHIFT, SEAT_QUIT,
)
from .guests import (
    swallow_sound,
    MAX_SQUEEZE, dread_now, fatigue, panic_tier, smell_drain, trait_note,
    Guest, difficulty, endurance, heavy_futa, hung_pay_factor, new_guest,
    click_crush, crush_chance, crush_tier, pity_of, pressure, rider_guest,
)


LEVEL_WORDS = {"light": LIGHT, "heavy": HEAVY, "crushing": CRUSHING}
GUEST_GENDERS = ("Female", "Shemale")


def stats_of(player:Player) -> tuple[int, int, int]:
    return (player.stats["vitality"], player.stats["strength"],
            player.level)


SEAT_OPEN = {"examine", "help", "hold", "profile", "sheet", "inv", "needs",
             "item", "spells", "top", "graveyard", "safeword", "quit", "wait", "breath", "pat", "struggle",
             "giveup", "kiss", "lick", "encourage", "regular", "regulars"}

MUTE_COMMANDS = {"talk", "chat", "meet"}


def air_text(air:int) -> str:
    filled = round(air / 10)
    return f"🫁 Air {'█' * filled}{'░' * (10 - filled)} {air} %"


def seat_lock(player:Player, command:str,
              shifts:dict[str, Shift]) -> list[Message]:
    shift = active_seat(player, shifts)
    if shift is None:
        return []
    if command in MUTE_COMMANDS and shift.client is None:
        return []
    if command in SEAT_OPEN:
        return []
    if command in MUTE_COMMANDS:
        return [Message(SEAT_MUTE, player.name)]
    return [Message(SEAT_STUCK.format(
        way="only she can end it" if (
            shift.client is not None and shift.client.rider)
        else "[quit] is your way out"), player.name)]

SIZE_BIG_BUTT = 170


def guest_prompt(shift:Shift, player:Player) -> Message:
    guest = shift.client
    if guest.rider:
        text = RIDER_TO_SEAT.format(rider=guest.name, weight=guest.weight,
                                    butt=guest.butt)
        return Message(text, player.name)
    mood = LEVEL_WORDS[difficulty(guest, *stats_of(player))]
    if guest.butt >= SIZE_BIG_BUTT:
        mood = f"Her rear is enormous. {mood}"
    probe = (BERTHA_PROBE.format(name=player.name) + "\n"
             if guest.name == BERTHA_NAME else "")
    if guest.kills:
        probe += KILLS_NOTE.format(name=guest.name,
                                   kills=kills_word(guest.kills)) + "\n"
    note = smell_note(guest.name, guest.sweat, guest.musk)
    if note:
        probe += note + "\n"
    trait = trait_note(guest)
    if trait:
        probe += trait + "\n"
    quirk = quirk_line(guest.npc, "cafe_arrive", random) if guest.npc else ""
    if quirk:
        probe += quirk + "\n"
    fear = dread_now(guest, stats_of(player)[0], player.level)
    if fear:
        probe += DREAD_LINES[fear] + "\n"
    return Message(probe + GUEST_ARRIVES.format(
        name=guest.name, body=body_line(guest.age, guest.height,
                                        guest.weight),
        butt=guest.butt, mood=mood,
        seconds=CAFE_REACTION_SECONDS) + f" ({shift.left} to go)",
        player.name, witness=(
            WITNESS_GUEST_BIG if guest.butt >= SIZE_BIG_BUTT
            else WITNESS_GUEST).format(guest=guest.name,
                                       weight=guest.weight))


def start_seat(player:Player, job:Job, shifts:dict[str, Shift],
               rng:random.Random, now:float=0.0) -> list[Message]:
    shifts[player.name] = Shift("cafe", job, job.sessions,
                                due=now + CAFE_ARRIVAL_SECONDS)
    return [Message(SEAT_INTRO, player.name, witness=WITNESS_SEAT),
            Message(SEAT_WAITING, player.name)]


def remaining(shift:Shift, now:float) -> int:
    return max(0, round(shift.due - now))


def countdown(shift:Shift, now:float) -> str:
    seconds = remaining(shift, now)
    if shift.client is None:
        return f"Next guest in {seconds} s"
    return f"Next reaction in {seconds} s"


def tick_seat(player:Player, shifts:dict[str, Shift], rng:random.Random,
              now:float, regulars=None, family:bool=False) -> tuple[list[Message], str]:
    shift = active_seat(player, shifts)
    if shift is None or now < shift.due:
        return [], ""
    if shift.mode == "home" and shift.client is None:
        del shifts[player.name]
        return [Message(HOME_DONE.format(name="She"), player.name)], ""
    if shift.client is None and family and (
            rng.random() < CAFE_FAMILY_CHANCE):
        tip = rng.randint(*CAFE_FAMILY_TIP)
        shift.earned += tip
        shift.due = now + CAFE_ARRIVAL_SECONDS
        shift.family = make_family(rng, regulars)
        names = (f"{shift.family.lady.name}, {shift.family.son.name} and "
                 f"{shift.family.girlfriend.name}")
        return [Message(f"{family_scene(rng, shift.family)}\nThey ignore "
                        f"your stool today, but the lady tosses you a tip "
                        f"for holding so still: +{tip} gold. [examine "
                        f"<name>] shows {names}.",
                        player.name)], ""
    if shift.client is None:
        shift.family = None
        shift.client = new_guest(rng, regulars, pref_of(player))
        shift.air = 100
        shift.due = now + CAFE_REACTION_SECONDS
        return [guest_prompt(shift, player)], ""
    return hold(player, shifts, rng, now, regulars=regulars)


def active_seat(player:Player, shifts:dict[str, Shift]) -> Shift | None:
    shift = shifts.get(player.name)
    if shift is not None and shift.building == "cafe" and (
            shift.job.key == "seat"):
        return shift
    return None


def fate_for(player:Player, guest:Guest, rng:random.Random) -> str:
    if guest.outcome:
        return guest.outcome
    if (player.gender == "Male" and guest.butt >= CAFE_ENGULF_BUTT
            and guest.weight >= CAFE_ENGULF_WEIGHT
            and rng.random() < CAFE_ENGULF_CHANCE):
        return "engulfed"
    return "smothered"


def round_pay(player:Player, shift:Shift, margin:int,
              rng:random.Random) -> int:
    pay = session_pay(player, shift.job, rng)
    if margin < 0:
        return pay // 2
    return round(pay * (1 + min(margin, 10) / 20))


def air_change(weight_on_face:int, margin:int) -> int:
    drain = 4 + weight_on_face // 3
    recovery = margin // 4 if margin > 0 else margin * 2
    return recovery - drain


def hold(player:Player, shifts:dict[str, Shift], rng:random.Random,
         now:float=0.0, bonus:int=0, pay_factor:float=1.0,
         lead:list[str] | None=None,
         regulars=None) -> tuple[list[Message], str]:
    shift = active_seat(player, shifts)
    if shift is None:
        return [Message(SEAT_NO_SHIFT, player.name)], ""
    guest = shift.client
    if guest is None:
        return [Message(SEAT_NO_GUEST.format(
            seconds=remaining(shift, now)), player.name)], ""
    shift.due = now + CAFE_REACTION_SECONDS
    lines_npc: list[str] = []
    if guest.wants_lick:
        guest.wants_lick = False
        guest.squeeze = min(MAX_SQUEEZE, guest.squeeze + 1)
        lines_npc.append(NPC_DEMAND_IGNORED.format(guest=guest.name))
    vitality, strength, level = stats_of(player)
    done = shift.job.sessions - shift.left
    stamina = endurance(vitality, strength, level, rng)
    weight_on_face = pressure(guest, rng)
    margin = stamina - weight_on_face - fatigue(done)
    fear = dread_now(guest, vitality, level)
    margin += (bonus + shift.bonus - shift.winded * 3
               - fear * DREAD_ROUND_PENALTY)
    shift.winded = 0
    extra, margin_delta = (npc_action(guest, rng, lines_npc)
                           if not guest.rider else (0, 0))
    margin += margin_delta
    shift.air = max(0, min(100, shift.air + air_change(
        weight_on_face, margin) + extra - smell_drain(guest)))
    if (not guest.rider and shift.air < PITY_AIR_LIMIT and guest.squeeze
            and rng.random() < PITY_EASE_CHANCE * pity_of(guest)):
        guest.squeeze -= 1
        shift.air = min(100, shift.air + PITY_AIR)
        lines_npc.append(PITY_EASE.format(guest=guest.name))
    tier = panic_tier(done, shift.job.sessions)
    if guest.rider:
        text = rng.choice(RIDER_HOLD).format(rider=guest.name)
        margin = max(margin, 0)
    elif margin >= 4:
        text = rng.choice(HOLD_EASY).format(guest=guest.name)
    elif margin >= 0:
        text = rng.choice(HOLD_HARD).format(guest=guest.name)
    else:
        text = rng.choice(HOLD_BAD).format(guest=guest.name)
    if (not guest.rider and margin < 4 and can_swallow(guest)
            and player.body.get("weight", 70)
            < guest.weight * CAFE_SWALLOW_RATIO
            and rng.random() < CAFE_SWALLOW_CHANCE):
        del shifts[player.name]
        record_kill(guest, regulars)
        grow_guest(guest, regulars)
        return [Message(SWALLOW_NPC.format(guest=guest.name) + "\n"
                        + swallow_sound(player.name, rng),
                        player.name)], "engulfed"
    crush = crush_chance(guest.butt, guest.weight, guest.squeeze, vitality,
                         player.age)
    if 0 < crush < 1 and not guest.rider:
        crush *= (1 - pity_of(guest)) * (
            1 - train_cut(training_of(player, guest.name)))
    if shift.crush_now or (crush and rng.random() < crush):
        del shifts[player.name]
        if not guest.rider:
            record_kill(guest, regulars)
        return [Message(CRUSH_SEAT.format(
            guest=guest.name, weight=guest.weight, seat=player.name)
            + f" {rng.choice(CRUSH_POPS)}", player.name)], "smothered"
    if shift.air <= 0:
        return collapse(player, shifts, shift, guest, regulars)
    if (not guest.rider and margin <= -CAFE_DEATH_MARGIN
            and rng.random() < CAFE_DEATH_CHANCE * shift.risk * (
                1 - train_cut(training_of(player, guest.name)))):
        del shifts[player.name]
        record_kill(guest, regulars)
        pool = BERTHA_DEATH if guest.name == BERTHA_NAME else COMPLAINTS_DEATH
        complaint = rng.choice(pool).format(guest=guest.name)
        return [Message(text, player.name),
                Message(complaint, player.name)], fate_for(player, guest, rng)
    if guest.npc and rng.random() < 0.6:
        lines_npc.append(quirk_line(guest.npc, "cafe_round", rng))
    lines_npc[:] = [line for line in lines_npc if line]
    guest.held += 1
    pay = round(round_pay(player, shift, margin, rng) * pay_factor
                * (1 - DREAD_PAY_CUT * fear))
    pay = round(pay * hung_pay_factor(guest))
    if guest.rider:
        pay = round(pay * (1 + 0.25 * guest.squeeze))
    home = shift.mode == "home"
    if home:
        pay = 0
    shift.earned += pay
    if not guest.rider:
        shift.left -= 1
    lines = (lead or []) + [text if home else f"{text} +{pay} gold"
                            ] + lines_npc + [air_text(shift.air)]
    if guest.kin and rng.random() < 0.6:
        lines.append(kin_text(ROUND, guest, player.name, rng))
    if guest.rider and guest.held >= 2:
        lines.append(rng.choice(DESPERATE_RIDER).format(
            rider=guest.name, seat=player.name))
    elif not guest.rider and (margin < 0 or guest.held >= 2):
        lines.append(rng.choice(DESPERATE))
    if tier:
        lines.append(rng.choice(PANIC_LINES[tier]).format(name=player.name))
    if not guest.rider and margin < 0:
        lines.append(rng.choice(COMPLAINTS_FAIL).format(guest=guest.name))
        lines.append(HOLD_WARN)
    messages = [Message("\n".join(lines), player.name)]
    if guest.rider:
        reaction = rng.choice(
            PANIC_LINES[tier] if tier else SEAT_REACTION).format(
                seat=player.name, name=player.name)
        messages.append(Message(f"{reaction} (+{pay} gold)", guest.rider))
    if shift.left <= 0 and home:
        del shifts[player.name]
        return messages + [Message(HOME_DONE.format(name=guest.name),
                                   player.name)], ""
    if shift.left <= 0:
        del shifts[player.name]
        released = [Message(RIDER_GONE.format(rider=guest.name),
                            guest.rider)] if guest.rider else []
        return messages + [Message(SEAT_DONE, player.name,
                                witness=WITNESS_DONE)] + finish(
            player, shift) + released, ""
    if not home and not guest.rider and guest.held >= 2 + guest.pleased:
        shift.client = None
        shift.due = now + CAFE_ARRIVAL_SECONDS
        return messages + [Message(GUEST_LEAVES.format(name=guest.name),
                                   player.name)], ""
    return messages, ""


def collapse(player:Player, shifts:dict[str, Shift], shift:Shift,
             guest:Guest, regulars=None) -> tuple[list[Message], str]:
    del shifts[player.name]
    lines = [Message(COLLAPSE_LEAD.format(guest=guest.name), player.name)]
    crushed = guest.weight > CAFE_CRUSH_WEIGHT
    if guest.rider:
        text = (COLLAPSE_RIDER_CRUSHED if crushed else COLLAPSE_RIDER)
        lines.append(Message(text.format(seat=player.name), guest.rider))
    elif crushed:
        record_kill(guest, regulars)
    if crushed:
        lines.append(Message(COLLAPSE_CRUSHED.format(
            guest=guest.name, weight=guest.weight), player.name))
        return lines, "collapsed"
    lines.append(Message(COLLAPSE_DRAGGED.format(guest=guest.name),
                         player.name))
    return lines + finish(player, shift), ""


def safeword(player:Player, shifts:dict[str, Shift],
             rng:random.Random | None=None) -> list[Message]:
    shift = active_seat(player, shifts)
    if shift is None:
        return [Message(SEAT_NO_SHIFT, player.name)]
    guest = shift.client
    if guest is not None and guest.rider:
        return [Message(SEAT_LOCKED.format(rider=guest.name),
                        player.name)]
    if rng is not None and frozen(player, shift, guest, rng):
        guest.hesitated = True
        shift.air = max(0, shift.air - DREAD_HESITATE_AIR)
        return [Message(SAFEWORD_FROZEN, player.name)]
    del shifts[player.name]
    return [Message(SEAT_QUIT, player.name, witness=WITNESS_QUIT)] + finish(
        player, shift)


def frozen(player:Player, shift:Shift, guest:Guest | None,
           rng:random.Random) -> bool:
    if guest is None or guest.hesitated:
        return False
    fear = dread_now(guest, stats_of(player)[0], player.level)
    return fear >= 2 and rng.random() < DREAD_HESITATE_CHANCE * fear


def seat_named(name:str, shifts:dict[str, Shift]) -> tuple[str, Shift] | None:
    wanted = name.strip().casefold()
    for key, shift in shifts.items():
        if (shift.building == "cafe" and shift.job.key == "seat"
                and key.casefold() == wanted):
            return key, shift
    return None


def seat_of_rider(rider:Player,
                  shifts:dict[str, Shift]) -> tuple[str, Shift] | None:
    for key, shift in shifts.items():
        guest = shift.client
        if (shift.building == "cafe" and isinstance(guest, Guest)
                and guest.rider == rider.name):
            return key, shift
    return None


def may_sit(player:Player) -> bool:
    return player.gender in GUEST_GENDERS or (
        player.gender in VAGINA_GENDERS)


NOT_A_LADY = ("Only ladies sit at the Fat Ass Café. Men work the stools "
              "– [job cafe seat].")


def sit(rider:Player, name:str, shifts:dict[str, Shift],
        rng:random.Random, now:float=0.0) -> list[Message]:
    if not may_sit(rider):
        return [Message(NOT_A_LADY, rider.name)]
    if seat_of_rider(rider, shifts) is not None:
        return [Message("You are already sitting. [rise] first.",
                        rider.name)]
    found = seat_named(name, shifts)
    if found is None:
        names = ", ".join(key for key, shift in shifts.items()
                          if shift.building == "cafe"
                          and shift.job.key == "seat") or "nobody"
        return [Message(f"No such seat on shift. On the stools now: "
                        f"{names}. [sit <name>]", rider.name)]
    key, shift = found
    if shift.client is not None:
        return [Message(f"{key} is already taken by {shift.client.name}.",
                        rider.name)]
    shift.due = now + CAFE_REACTION_SECONDS
    shift.client = rider_guest(rider.name, rider.body.get("weight", 65),
                               rider.body.get("butt", 95), rider.age,
                               rider.body.get("height", 0), rider.gender,
                               rider.body.get("endowment", 0))
    shift.client.kills = rider.profile.get("swallows", 0)
    satisfy(rider.needs, {"arousal": -CAFE_RIDER_RELIEF})
    kin = role_of(rider, key)
    if kin in ("son", "daughter") and heavy_futa(shift.client):
        shift.client.kin = kin
    scene = ([Message(rng.choice(SIT_LINES[kin]).format(
        rider=rider.name, seat=key), rider.name),
        Message(f"Your {kin_back(kin)} {rider.name} sits down on you.",
                key)] if kin in SIT_LINES else [])
    if shift.client.kin:
        text = kin_text(SIT, shift.client, key, rng)
        scene.append(Message(text, rider.name))
        scene.append(Message(text, key))
    return [Message(RIDER_WELCOME.format(rider=rider.name, seat=key),
                    rider.name,
                    witness=WITNESS_RIDER.format(actor="{actor}", seat=key)),
            Message(RIDER_TO_SEAT.format(
                rider=rider.name, weight=shift.client.weight,
                butt=shift.client.butt), key)] + scene


def kin_back(role:str) -> str:
    return {"son": "mother", "daughter": "mother", "mother": "child",
            "father": "child", "brother": "sibling",
            "sister": "sibling"}.get(role, "partner")


def torment(rider:Player, shifts:dict[str, Shift], kind:str,
            rng:random.Random | None=None,
            seat:Player | None=None) -> list[Message]:
    found = seat_of_rider(rider, shifts)
    if found is None:
        return [Message(TORMENT_NONE, rider.name)]
    key, shift = found
    guest = shift.client
    if kind == "clench":
        maxed = guest.squeeze >= MAX_SQUEEZE
        guest.squeeze = min(MAX_SQUEEZE, guest.squeeze + 1)
        shift.air = max(0, shift.air - 10)
        extra = (kin_text(CLENCH, guest, key, rng)
                 if guest.kin and rng else "")
        vitality = seat.stats["vitality"] if seat is not None else 0
        age = seat.age if seat is not None else 0
        chance = crush_chance(guest.butt, guest.weight, guest.squeeze,
                              vitality, age)
        if maxed and click_crush(chance, rng):
            shift.crush_now, shift.due = True, 0.0
        tier = crush_tier(chance)
        warn = (rng.choice(CRUSH_WHIMPER[tier]).format(seat=key)
                if tier and rng else "")
        plea = (" " + rng.choice(CLENCH_PLEAS[guest.squeeze]).format(
            seat=key) if rng else "")
        return [Message(CLENCH_RIDER.format(seat=key)
                        + (CLENCH_MAX if maxed else "") + plea + warn,
                        rider.name),
                Message(CLENCH_SEAT.format(rider=rider.name)
                        + (f"\n{extra}" if extra else ""), key)]
    shift.air = max(0, shift.air - 15)
    shift.winded = min(2, shift.winded + 1)
    extra = (kin_text(WIGGLE, guest, key, rng)
             if guest.kin and rng else "")
    return [Message(WIGGLE_RIDER.format(seat=key), rider.name),
            Message(WIGGLE_SEAT.format(rider=rider.name)
                    + (f"\n{extra}" if extra else ""), key)]


def npc_action(guest:Guest, rng:random.Random,
               lines:list[str]) -> tuple[int, int]:
    chance = (CAFE_NPC_ACTION_CHANCE * CAFE_NPC_CRUELTY[guest.cruel]
              * (1 - pity_of(guest)))
    if rng.random() >= chance:
        return 0, 0
    kind = rng.choices(("clench", "wiggle", "demand"), (3, 3, 1))[0]
    if kind == "clench":
        guest.squeeze = min(MAX_SQUEEZE, guest.squeeze + 1)
        lines.append(NPC_CLENCH.format(guest=guest.name))
        return -10, 0
    if kind == "wiggle":
        lines.append(NPC_WIGGLE.format(guest=guest.name))
        return -15, -3
    guest.wants_lick = True
    lines.append(NPC_DEMAND.format(guest=guest.name))
    return 0, 0


def kills_word(kills:int) -> str:
    return f"{kills} kill{'s' if kills != 1 else ''}"


def record_kill(guest:Guest, regulars) -> None:
    guest.kills += 1
    if regulars is not None:
        regulars.bump("cafe", guest.name, "kills")
        if guest.npc and regulars.credit:
            regulars.credit(guest.npc)


def can_swallow(guest:Guest) -> bool:
    return (guest.butt >= CAFE_ENGULF_BUTT
            and guest.weight >= CAFE_ENGULF_WEIGHT)


def swallow(rider:Player, shifts:dict[str, Shift]) -> tuple[str, str]:
    found = seat_of_rider(rider, shifts)
    if found is None:
        return "", SWALLOW_NONE
    key, shift = found
    if not can_swallow(shift.client):
        return "", SWALLOW_TOO_SMALL.format(
            need=f"you are {shift.client.butt} cm and {shift.client.weight} kg",
            butt=CAFE_ENGULF_BUTT, weight=CAFE_ENGULF_WEIGHT)
    del shifts[key]
    return key, ""


def rise(rider:Player, shifts:dict[str, Shift],
         rng:random.Random, now:float=0.0) -> list[Message]:
    found = seat_of_rider(rider, shifts)
    if found is None:
        return [Message("You are not sitting on anybody.", rider.name)]
    key, shift = found
    parting = (kin_text(RISE, shift.client, key, rng)
               if shift.client.kin else "")
    shift.client = None
    shift.due = now + CAFE_ARRIVAL_SECONDS
    text = RIDER_RISE.format(rider=rider.name, seat=key)
    if parting:
        text += f"\n{parting}"
    return [Message(text, rider.name), Message(text, key)]


def stay(rider:Player, shifts:dict[str, Shift]) -> list[Message]:
    found = seat_of_rider(rider, shifts)
    if found is None:
        return [Message("You are not sitting on anybody.", rider.name)]
    key, _ = found
    text = RIDER_STAY.format(rider=rider.name, seat=key)
    return [Message(text, rider.name), Message(text, key)]


def raise_up(rider:Player, shifts:dict[str, Shift],
             now:float) -> list[Message]:
    found = seat_of_rider(rider, shifts)
    if found is None:
        return [Message("You are not sitting on anybody.", rider.name)]
    key, shift = found
    if now < getattr(shift, "raise_due", 0.0):
        return [Message(RIDER_RAISE_WAIT.format(seat=key), rider.name)]
    shift.raise_due = now + RIDER_RAISE_COOLDOWN
    shift.air = min(100, shift.air + RIDER_RAISE_AIR)
    shift.client.squeeze = max(0, shift.client.squeeze - 1)
    text = RIDER_RAISE.format(rider=rider.name, seat=key)
    return [Message(text, rider.name), Message(text, key)]


def lean(rider:Player, shifts:dict[str, Shift],
         rng:random.Random) -> list[Message]:
    found = seat_of_rider(rider, shifts)
    if found is None:
        return [Message("You are not sitting on anybody.", rider.name)]
    key, shift = found
    guest = shift.client
    if guest.squeeze >= MAX_SQUEEZE:
        text = RIDER_LEAN_MAX.format(rider=rider.name, seat=key)
    else:
        guest.squeeze += 1
        text = rng.choice(RIDER_LEAN).format(rider=rider.name, seat=key)
        satisfy(rider.needs, {"arousal": -5})
    return [Message(text, rider.name), Message(text, key)]
