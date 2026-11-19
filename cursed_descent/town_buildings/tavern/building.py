def do_tavern(services, player, args):
    from ...models import Message
    from ..menu import menu_lines
    from .content import ROOM_USAGE
    messages = services.place_menu(player, "tavern")
    if services.in_run(player):
        return messages
    return [Message("\n".join([messages[0].text] + menu_lines("tavern")
                              + [ROOM_USAGE]), player.name)]


def do_room(services, player, args):
    from ...towns.last_light_humans.cafe.service import sitting_on
    from .rooms import sleep_in_room
    busy = (player.name in services.shifts
            or bool(sitting_on(services, player)))
    messages = sleep_in_room(player, " ".join(args), services.in_run(player),
                             busy, services.rng)
    return messages


def do_sellpods(services, player, args):
    from ...models import Message
    from .pods import sell
    if services.in_run(player):
        return [Message("The tavern is far away while you are in the "
                        "dungeon.", player.name)]
    return sell(player, args)


COMMANDS = {"tavern": do_tavern, "room": do_room, "sellpods": do_sellpods}
