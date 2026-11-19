from ...models import Message


def do_station(services, player, args):
    from ...towns import (
        START_TOWN, TOWNS, destinations, fare_between, town_key,
    )
    from .rail_pass import has_pass, usage as pass_usage
    if services.in_run(player):
        return [Message("The station is far away while you are in the "
                        "dungeon.", player.name)]
    here = town_key(player)
    lines = [f"🚉 {TOWNS[here].name} – trains go to:"]
    for key in destinations(player):
        goal = TOWNS[key]
        lines.append(f"  [travel {goal.name}] {goal.name} "
                     f"({goal.race}) – {fare_between(here, key)} gold")
    if len(destinations(player)) < len(TOWNS) - 1:
        lines.append("  Other lines are still closed. A town opens up "
                     "once you have been there and won over its "
                     "stationmaster.")
    if here != START_TOWN and not has_pass(player, here):
        lines.append("  " + pass_usage(here))
    return [Message("\n".join(lines), player.name)]


def do_travel(services, player, args):
    from ...towns import (
        TOWNS, destinations, fare_between, mark_visited, town_key, town_text,
    )
    from .rail_pass import keeper_name
    if services.in_run(player):
        return [Message("No trains down in the dungeon.", player.name)]
    if services.on_shift(player) or player.name in services.rides:
        return [Message("Not while you are working or sitting.",
                        player.name)]
    wanted = " ".join(args).casefold()
    here = town_key(player)
    goal = next((key for key, town in TOWNS.items()
                 if wanted in (key, town.name.casefold(),
                               town.race.casefold())), "")
    if not goal:
        return do_station(services, player, args)
    if goal == here:
        return [Message(f"You are already in {TOWNS[here].name}.",
                        player.name)]
    if goal not in destinations(player):
        return [Message(f"You hold no rail pass for "
                        f"{TOWNS[goal].name} yet. Go there once and "
                        f"deal with its stationmaster: talk, pay, "
                        f"bribe or sleep with {keeper_name(goal)}.",
                        player.name)]
    fare = fare_between(here, goal)
    if player.gold < fare:
        return [Message(f"The fare is {fare} gold. You have "
                        f"{player.gold}.", player.name)]
    player.gold -= fare
    player.profile["town"] = goal
    mark_visited(player, goal)
    services.regular_stores.pop(player.id, None)
    town = TOWNS[goal]
    text = (f"🚂 You pay {fare} gold and ride to {town.name}.\n"
            + town_text(town, services.rng.choice(town.happenings)))
    return [Message(text, player.name)]


def do_ticket(services, player, args):
    from ...towns import START_TOWN, TOWNS, town_key
    from .rail_pass import HOWS, has_pass, try_pass, usage as pass_usage
    if services.in_run(player):
        return [Message("The station is far away while you are in the "
                        "dungeon.", player.name)]
    key = town_key(player)
    if key == START_TOWN or has_pass(player, key):
        return [Message(f"You already hold a rail pass for "
                        f"{TOWNS[key].name}.", player.name)]
    how = args[0].casefold() if args else ""
    if how not in HOWS:
        return [Message(pass_usage(key), player.name)]
    _, text = try_pass(player, key, how, services.rng)
    return [Message(text, player.name)]


COMMANDS = {"station": do_station, "travel": do_travel,
            "ticket": do_ticket}
