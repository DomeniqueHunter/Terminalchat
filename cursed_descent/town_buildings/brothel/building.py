from ...models import Message


def do_brothel(services, player, args):
    return services.place_menu(player, "brothel")


def do_serve(services, player, args):
    from .shift import serve
    return serve(player, " ".join(args), services.shifts, services.rng,
                 services.regulars_of(player), services.now)


def do_practices(services, player, args):
    from .practices import practices_text
    return practices_text(player, args)


def do_book(services, player, args):
    from .shift import rent
    return rent(player, " ".join(args), services.in_run(player))


def examine(services, player, text):
    from ..visits import status_line
    from .clients import describe_client
    shift = services.shifts.get(player.name)
    client = shift.client if shift is not None else None
    if shift is None or shift.building != "brothel" or client is None:
        return []
    wanted = text.strip().casefold()
    if wanted not in ("client", "partner", "him", "her", "them",
                      client.name.casefold()) and (
            wanted not in client.name.casefold().split()):
        return []
    text = describe_client(client)
    stored = services.regulars_of(player).get("brothel", client.name)
    if stored is not None:
        text += f"\nRegular: {status_line(stored)}"
    return [Message(text, player.name)]


COMMANDS = {"brothel": do_brothel, "serve": do_serve,
            "practices": do_practices, "book": do_book}
