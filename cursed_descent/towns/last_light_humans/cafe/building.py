def do_cafe(services, player, args):
    from ....models import Message
    from .content import BUY_HINT, FURNITURE_HEADER
    from ....content import ITEMS, RARITY_LABELS
    from ....town_buildings.work.content import CLOSED as WORK_CLOSED
    from ....town_buildings.work.jobs import building_menu
    from .stools import free_list, refresh_stools
    from .seat import may_sit
    from .stool_trade import where_text
    from ....town_buildings.menu import menu_lines
    from ....town_buildings.bodies import pref_of
    if services.in_run(player):
        return [Message(WORK_CLOSED["cafe"], player.name)]
    if args and args[0].casefold() == "buy":
        return cafe_buy(services, player, args[1:])
    services.cafe_seen[player.name] = services.now
    lines = services.cafe.tick()
    services.stools = refresh_stools(services.rng, pref_of(player))
    messages = building_menu("cafe", player)
    stock = services.cafe.stock()
    extra = menu_lines("cafe") + ([BUY_HINT] if stock else [])
    for number, entry in enumerate(stock, 1):
        item = ITEMS[entry["id"]]
        extra.append(f"  {number}. {item['name']} "
                     f"({RARITY_LABELS[item['rarity']]}) – "
                     f"{item['price']} gold")
    stools = [npc for npc in services.repository.npc_players()
              if npc.npc == "furniture"]
    if stools:
        extra.append(f"{FURNITURE_HEADER}: " + ", ".join(
            f"{npc.full_name} ({where_text(npc)})" for npc in stools))
    if may_sit(player):
        extra.append(free_list(services.stools))
    if services.cafe.digesting():
        extra.append("Something is still being prepared in the back.")
    return [Message("\n".join(lines + [messages[0].text] + extra),
                    player.name)]


def cafe_buy(services, player, args):
    from ....items import Item
    from ....models import Message
    from ....content import ITEMS
    stock = services.cafe.stock()
    if not args or not args[0].isdigit() or not (
            1 <= int(args[0]) <= len(stock)):
        return [Message("[cafe buy <nr>] – see [cafe].", player.name)]
    entry = stock[int(args[0]) - 1]
    item = ITEMS[entry["id"]]
    if player.gold < item["price"]:
        return [Message(f"{item['name']} costs {item['price']} gold.",
                        player.name)]
    if len(player.inventory) >= player.bag_size:
        return [Message("Your bag is full.", player.name)]
    player.gold -= item["price"]
    player.inventory.append(Item(entry["id"], creator="cafe"))
    services.cafe.sell(entry)
    return [Message(f"{player.name} buys {item['name']} for "
                    f"{item['price']} gold.", player.name)]


def do_hold(services, player, args):
    from .seat import hold
    from .service import cafe_death
    messages, fate = hold(player, services.shifts, services.rng, services.now)
    if fate:
        messages += cafe_death(services, player, fate)
    return messages


def seat_action(services, player, action):
    from .actions import act
    from .service import cafe_death
    messages, fate = act(player, services.shifts, services.rng, services.now, action,
                          services.regulars_of(player))
    if fate:
        messages += cafe_death(services, player, fate)
    return messages


def do_wait(services, player, args):
    return seat_action(services, player, "wait")


def do_breath(services, player, args):
    return seat_action(services, player, "breath")


def do_pat(services, player, args):
    return seat_action(services, player, "pat")


def do_struggle(services, player, args):
    return seat_action(services, player, "struggle")


def apply_torment(services, player, kind):
    from ....models import Message
    from .stools import ride_torment
    from ....needs import satisfy
    from .seat import seat_of_rider, torment
    ride = services.rides.get(player.name)
    if ride is not None:
        satisfy(player.needs, {"arousal": -4})
        return [Message(line, player.name)
                for line in ride_torment(ride, kind, player,
                                         services.rng)]
    found = seat_of_rider(player, services.shifts)
    seat = services.repository.load(found[0]) if found else None
    return torment(player, services.shifts, kind, services.rng, seat)


def do_clench(services, player, args):
    return apply_torment(services, player, "clench")


def do_wiggle(services, player, args):
    return apply_torment(services, player, "wiggle")


def do_swallow(services, player, args):
    from ....models import Message
    from ....config import (
        CAFE_ENGULF_BUTT, CAFE_ENGULF_WEIGHT, CAFE_RIDER_RELIEF,
    )
    from .kin_seat import (
        SWALLOW_RIDER as KIN_SWALLOW_RIDER, SWALLOW_SEAT as KIN_SWALLOW_SEAT,
        kin_text,
    )
    from .content import (
        SWALLOW_RIDER, SWALLOW_SEAT, SWALLOW_STOOL, SWALLOW_TOO_SMALL,
    )
    from .seat import can_swallow, seat_of_rider, swallow
    from .swallow import grow_player
    from .stools import lady_of
    from ....needs import satisfy
    from .guests import swallow_sound
    from .service import bertha_takes, cafe_death
    ride = services.rides.get(player.name)
    if ride is not None:
        lady = lady_of(player, ride.extra)
        if not can_swallow(lady):
            return [Message(SWALLOW_TOO_SMALL.format(
                need=f"you are {lady.butt} cm and {lady.weight} kg",
                butt=CAFE_ENGULF_BUTT, weight=CAFE_ENGULF_WEIGHT),
                player.name)]
        del services.rides[player.name]
        bertha_takes(services, "engulfed")
        satisfy(player.needs, {"arousal": -CAFE_RIDER_RELIEF})
        return [Message(SWALLOW_STOOL.format(name=ride.stool.name)
                        + "\n" + swallow_sound(ride.stool.name,
                                               services.rng)
                        + "\n" + grow_player(player, ride.stool.name),
                        player.name)]
    found = seat_of_rider(player, services.shifts)
    guest = found[1].client if found is not None else None
    key, problem = swallow(player, services.shifts)
    if problem:
        return [Message(problem, player.name)]
    seat = services.repository.load(key)
    to_rider = SWALLOW_RIDER.format(seat=key)
    to_seat = SWALLOW_SEAT.format(rider=player.name)
    if guest is not None and guest.kin:
        to_rider = kin_text(KIN_SWALLOW_RIDER, guest, key, services.rng)
        to_seat = kin_text(KIN_SWALLOW_SEAT, guest, key, services.rng)
    messages = [Message(to_rider + "\n"
                        + swallow_sound(key, services.rng) + "\n"
                        + grow_player(player, key), player.name),
                Message(to_seat + "\n"
                        + swallow_sound(key, services.rng), key)]
    return messages + cafe_death(services, seat, "engulfed")


def do_lick(services, player, args):
    return seat_action(services, player, "lick")


def do_kiss(services, player, args):
    return seat_action(services, player, "kiss")


def do_encourage(services, player, args):
    return seat_action(services, player, "encourage")


def do_giveup(services, player, args):
    return seat_action(services, player, "giveup")


def do_sit(services, player, args):
    from ....models import Message
    from .seat import NOT_A_LADY, may_sit, sit
    from ....town_buildings.work.content import CLOSED as WORK_CLOSED
    from .service import sitting_on
    from .stools import free_list, pick_stool, start_ride
    if services.in_run(player):
        return [Message(WORK_CLOSED["cafe"], player.name)]
    if not may_sit(player):
        return [Message(NOT_A_LADY, player.name)]
    text = " ".join(args)
    stool = pick_stool(services.stools, text)
    if stool is not None:
        if player.name in services.rides or sitting_on(services, player):
            return [Message("You are already sitting. [rise] first.",
                            player.name)]
        ride, messages = start_ride(player, stool, services.now)
        if ride is not None:
            services.rides[player.name] = ride
            services.stools.remove(stool)
        return messages
    if not text:
        names = [key for key, shift in services.shifts.items()
                 if shift.building == "cafe"
                 and shift.job.key == "seat"]
        return [Message("\n".join([free_list(services.stools)] + (
            [f"Characters on shift: {', '.join(names)} ([sit <name>])"]
            if names else [])), player.name)]
    return sit(player, text, services.shifts, services.rng, services.now)


def do_complain(services, player, args):
    from ....models import Message
    from ....config import CAFE_TICKET
    from .content import COMPLAINT_NONE, COMPLAINT_OK
    if services.complaints.pop(player.name, None) is None:
        return [Message(COMPLAINT_NONE, player.name)]
    refund = CAFE_TICKET // 2
    player.gold += refund
    return [Message(COMPLAINT_OK.format(refund=refund), player.name)]


def do_stay(services, player, args):
    from ....models import Message
    from .content import RIDE_STAY
    from .seat import stay
    ride = services.rides.get(player.name)
    if ride is not None:
        return [Message(RIDE_STAY.format(name=ride.stool.name),
                        player.name)]
    return stay(player, services.shifts)


def do_lean(services, player, args):
    from ....models import Message
    from .seat import lean
    from .stools import ride_lean
    from ....needs import satisfy
    ride = services.rides.get(player.name)
    if ride is not None:
        satisfy(player.needs, {"arousal": -5})
        return [Message(ride_lean(ride, services.rng), player.name)]
    return lean(player, services.shifts, services.rng)


def do_raise(services, player, args):
    from ....config import RIDER_RAISE_COOLDOWN, RIDER_RAISE_PAUSE
    from ....models import Message
    from .content import RIDE_RAISE, RIDER_RAISE_WAIT
    from .seat import raise_up
    ride = services.rides.get(player.name)
    if ride is None:
        return raise_up(player, services.shifts, services.now)
    if services.now < getattr(ride, "raise_due", 0.0):
        return [Message(RIDER_RAISE_WAIT.format(seat=ride.stool.name),
                        player.name)]
    ride.raise_due = services.now + RIDER_RAISE_COOLDOWN
    ride.squeeze = max(0, ride.squeeze - 1)
    ride.due += RIDER_RAISE_PAUSE
    return [Message(RIDE_RAISE.format(name=ride.stool.name), player.name)]


def do_rise(services, player, args):
    from ....models import Message
    from .content import RIDE_RISE
    from .seat import rise
    ride = services.rides.pop(player.name, None)
    if ride is not None:
        return [Message(RIDE_RISE.format(name=ride.stool.name),
                        player.name)]
    return rise(player, services.shifts, services.rng, services.now)


COMMANDS = {"cafe": do_cafe, "hold": do_hold, "wait": do_wait,
            "breath": do_breath, "pat": do_pat, "struggle": do_struggle,
            "clench": do_clench, "wiggle": do_wiggle, "swallow": do_swallow,
            "lick": do_lick, "kiss": do_kiss, "encourage": do_encourage,
            "giveup": do_giveup, "sit": do_sit, "complain": do_complain,
            "stay": do_stay, "lean": do_lean, "rise": do_rise,
            "raise": do_raise}
