from ....combat import fate_text
from ....config import (
    CAFE_AMBIENT_MAX, CAFE_AMBIENT_MIN, CAFE_LOCK, CAFE_PRESENT_SECONDS,
    REGULARS_CALL_CHANCE,
)
from ....content import ITEMS
from ....house_visit import KEY as VISIT_KEY, state_of
from ....houses import home_of
from ....models import Message, Player
from ....needs import satisfy
from ....npcs.store import credit_kill
from ....towns import town_key
from ....town_buildings.bodies import body_line
from ....town_buildings.dishes import DISH_KG, HOUSE_CAKE_KG
from ....town_buildings.family import note as family_note
from ....town_buildings.visits import call_scene, status_line
from .ambient import ambient_line, family_look
from .content import (
    DEATH_COLLAPSED, DEATH_ENGULFED, DEATH_SMOTHERED, GUEST_LOOK, RIDER_LOOK,
    WITNESS_DEATH, WITNESS_FURNITURE,
)
from .furniture import make_furniture
from .kin_seat import LOOK, kin_text
from .ledger import grow_keeper, outcome_text, pick_outcome
from .seat import countdown, seat_of_rider, tick_seat
from .stools import describe as describe_stool, ride_round
from .vore import BAD_END, VORE_FATES


def sitting_on(services, player:Player) -> str:
    ride = services.rides.get(player.name)
    if ride is not None:
        return ride.stool.name
    found = seat_of_rider(player, services.shifts)
    return found[0] if found else ""


def fed(services, player:Player, kilos:int) -> list[Message]:
    if kilos <= 0:
        return []
    ride = services.rides.get(player.name)
    found = seat_of_rider(player, services.shifts)
    if ride is not None:
        ride.extra += kilos
        return [Message(f"You eat while sitting – you press down "
                        f"{kilos} kg heavier on {ride.stool.name} "
                        f"until you rise.", player.name)]
    if found is None:
        return []
    key, shift = found
    shift.client.weight += kilos
    text = (f"{player.name} eats while sitting and settles {kilos} kg "
            f"heavier on {key} – until she rises.")
    return [Message(text, player.name), Message(text, key)]


def fed_item(services, player:Player, item_id:str) -> list[Message]:
    if item_id.startswith("dish_"):
        _, building, key = item_id.split("_", 2)
        return fed(services, player, DISH_KG.get((building, key), 0))
    if ITEMS.get(item_id, {}).get("cafe"):
        return fed(services, player, HOUSE_CAKE_KG)
    return []


def bertha_takes(services, fate:str) -> None:
    keeper = credit_kill(services.repository.npc_players(), fate)
    grow_keeper(keeper, fate)
    if keeper is not None:
        services.repository.save(keeper)


def seat_timer(services, player:Player) -> str:
    shift = services.shifts.get(player.name)
    if (shift is not None and shift.building == "cafe"
            and shift.job.key == "seat"):
        return countdown(shift, services.now)
    ride = services.rides.get(player.name)
    if ride is not None:
        return (f"Next reaction of {ride.stool.name} in "
                f"{max(0, round(ride.due - services.now))} s")
    found = seat_of_rider(player, services.shifts)
    if found is not None:
        return countdown(found[1], services.now)
    return ""


def cafe_active(services, player:Player) -> bool:
    shift = services.shifts.get(player.name)
    return (shift is not None and shift.building == "cafe"
            and shift.job.key == "seat")


def tick_seats(services, now:float) -> list[Message]:
    messages: list[Message] = []
    for name, shift in list(services.shifts.items()):
        if shift.building != "cafe" or shift.job.key != "seat" or (
                now < shift.due):
            continue
        player = services.repository.load(name)
        if player is None:
            del services.shifts[name]
            continue
        added, fate = tick_seat(player, services.shifts, services.rng, now,
                                services.regulars_of(player),
                                services.ambient_on)
        if fate:
            added += cafe_death(services, player, fate)
        added += services.settle_home(player)
        services.repository.save(player)
        messages += added
    return messages


def tick_rides(services, now:float) -> list[Message]:
    messages: list[Message] = []
    for name, ride in list(services.rides.items()):
        if now < ride.due:
            continue
        rider = services.repository.load(name)
        added, status = ride_round(ride, rider, services.rng, now)
        if status:
            del services.rides[name]
        if status == "dead":
            bertha_takes(services, "smothered")
        if status == "swallowed":
            bertha_takes(services, "engulfed")
        if status in ("dead", "collapsed"):
            services.complaints[name] = ride.stool.name
            services.claims[name] = ride.stool
        satisfy(rider.needs, {"arousal": -3})
        services.repository.save(rider)
        messages += added
    return messages


def ambient(services, now:float) -> list[Message]:
    if not services.ambient_on:
        return []
    present = {name for name, shift in services.shifts.items()
               if shift.building == "cafe"}
    present |= set(services.rides)
    present |= {name for name, seen in services.cafe_seen.items()
                if now - seen <= CAFE_PRESENT_SECONDS}
    lines = []
    for name in sorted(present):
        if services.session is not None and services.session.in_run(name):
            continue
        visitor = services.repository.load(name)
        if visitor is not None and state_of(visitor) is not None:
            continue
        due = services.ambient_due.setdefault(
            name, now + services.rng.uniform(CAFE_AMBIENT_MIN,
                                             CAFE_AMBIENT_MAX))
        if now < due:
            continue
        services.ambient_due[name] = now + services.rng.uniform(
            CAFE_AMBIENT_MIN, CAFE_AMBIENT_MAX)
        call = regular_call(services, name)
        lines.append(call or Message(ambient_line(services.rng), name,
                                     "ambient", "cafe"))
    return lines


def is_player_char(services, name:str) -> bool:
    other = services.repository.load(name)
    return other is not None and not other.npc


def regular_call(services, name:str) -> Message | None:
    player = services.repository.load(name)
    if (player is None or player.name in services.shifts
            or player.name in services.rides):
        return None
    if home_of(player, town_key(player)) is None:
        return None
    if services.rng.random() >= REGULARS_CALL_CHANCE:
        return None
    store = services.regulars_of(player)
    callers = [(building, record) for building in ("cafe", "brothel")
               for record in store.all(building)
               if record.get("address_known")
               and not is_player_char(services, record["name"])]
    if not callers:
        return None
    building, record = services.rng.choice(callers)
    text, _ = call_scene(record, building, services.rng)
    store.set(building, record["name"], {
        "visits": record.get("visits", 1) + 1})
    return Message(text, name)


def cafe_examine(services, player:Player, text:str) -> list[Message]:
    wanted = text.strip().casefold()
    stools = list(services.stools)
    ride = services.rides.get(player.name)
    if ride is not None:
        stools.append(ride.stool)
    for stool in stools:
        if wanted and wanted in stool.name.casefold().split() or (
                wanted == stool.name.casefold()):
            return [Message(describe_stool(stool), player.name)]
    shift = services.shifts.get(player.name)
    family = getattr(shift, "family", None) if shift else None
    if family is not None:
        seen = family_look(family, wanted)
        if seen:
            return [Message(seen, player.name)]
    guest = (shift.client if shift is not None
             and shift.building == "cafe" else None)
    if guest is None or not (
            wanted in ("guest", "lady", "her")
            or wanted == guest.name.casefold()
            or wanted in guest.name.casefold().replace(".", "").split()):
        return []
    look = RIDER_LOOK if guest.rider else GUEST_LOOK
    if guest.kills:
        look += f" Kills on her ledger: {guest.kills}."
    stored = services.regulars_of(player).get("cafe", guest.name)
    if stored is not None:
        look += f"\nRegular: {status_line(stored)}"
    if guest.rider:
        look += "\n" + family_note(player, guest.name)
        if guest.kin:
            look += "\n" + kin_text(LOOK, guest, player.name, services.rng)
    return [Message(look.format(
        name=guest.name, butt=guest.butt,
        body=body_line(guest.age, guest.height, guest.weight)),
        player.name)]


def vore_death(services, player:Player, fate:str) -> list[Message]:
    text = fate_text(player, fate, None)
    player.deaths[fate] = player.deaths.get(fate, 0) + 1
    player.last_fate = fate
    player.records[CAFE_LOCK] = 1
    player.last_fate_text = text
    bertha_takes(services, fate)
    return [Message("\n".join([text, BAD_END.format(name=player.name)]),
                    player.name,
                    witness=WITNESS_DEATH.get(fate, WITNESS_DEATH["vored"]))]


def cafe_death(services, player:Player, fate:str) -> list[Message]:
    player.profile.pop("home_session", None)
    player.profile.pop(VISIT_KEY, None)
    if fate in VORE_FATES:
        return vore_death(services, player, fate)
    text = fate_text(player, fate, None)
    player.deaths[fate] = player.deaths.get(fate, 0) + 1
    player.last_fate = fate
    player.records[CAFE_LOCK] = 1
    player.last_fate_text = text
    outcome = pick_outcome({}, services.rng)
    if fate == "engulfed":
        outcome = "full"
    elif fate == "collapsed":
        outcome = "furniture"
    entry = services.cafe.add(player, fate, outcome)
    bertha_takes(services, fate)
    intro = {"engulfed": DEATH_ENGULFED,
             "collapsed": DEATH_COLLAPSED}.get(
                 fate, DEATH_SMOTHERED).format(name=player.name)
    lines = [f"💀 {intro}", text, outcome_text(entry, player)]
    if outcome == "furniture":
        make_furniture(player, services.repository, services.world.day)
        player.profile["since"] = services.world.day
        services.repository.save(player)
    witness = WITNESS_DEATH.get(fate, WITNESS_DEATH["smothered"])
    if outcome == "furniture":
        witness += "\n" + WITNESS_FURNITURE
    return [Message("\n".join(lines), player.name, witness=witness)]
