from ...view import Button, Panel
from .rules import BrewState, vat_actions
from .sisters import SISTERS


def vat_panel(shift) -> Panel | None:
    state = shift.client if shift is not None else None
    if not isinstance(state, BrewState):
        return None
    cfg = SISTERS[state.town]
    titles = {"vore": f"Inside {cfg['name']}",
              "service": f"Serving {cfg['name']}"}
    title = titles.get(state.kind, f"{cfg['name']}'s {state.vat} vat")
    heat = f"Temperature: {state.temp}. " if state.kind == "bath" else ""
    lines = [f"{heat}Rounds left: {shift.left}."]
    if state.pending == "boil":
        lines.append("The flame is rising!")
    actions = vat_actions(state)
    if not actions:
        lines.append("Nothing to answer right now. The sister may make you "
                     "an offer at the end of a round.")
    return Panel(title, tuple(lines), tuple(
        Button(label, f"!vat {word}") for label, word in actions))
