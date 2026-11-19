def confirm(controller, now:float=1.0) -> list:
    messages = []
    for name in sorted(controller.ready.pending):
        messages += controller.handle(name, "!ready", now=now)
    return messages
