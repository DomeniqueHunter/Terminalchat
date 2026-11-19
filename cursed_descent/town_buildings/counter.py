from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Offer:
    label: str
    kind: str
    price: int = 0
    item: str = ""
    factor: float = 1.0
    hide_if: str = ""
    show_if: str = ""


@dataclass(frozen=True)
class Special:
    key: str
    title: str
    blurb: str
    icon: str
    keeper: str
    quote: str
    offers: tuple[Offer, ...]
    handlers: dict[str, Callable] = field(default_factory=dict)
    starters: dict[str, Callable] = field(default_factory=dict)


def counter_command(key:str) -> Callable:
    def handler(services, player, args):
        from .offers import run
        return run(services, player, key, args)
    return handler


def counter_ui(key:str) -> Callable:
    def panel(services, player):
        from ..view import Button, Panel
        from . import registry
        from .offers import hidden, offer_price
        spec = registry.get(key)
        special = spec.counter
        spec_shift_ui = spec.shift_ui or (lambda *args: None)
        buttons = []
        for number, offer in enumerate(special.offers, 1):
            if hidden(player, offer):
                continue
            price = offer_price(offer)
            label = offer.label + (f" – {price} gold" if price else "")
            buttons.append(Button(label, f"!{key} {number}"))
        from .work.ui import compact, shift_panel
        shift = services.shifts.get(player.name)
        extra = (spec_shift_ui(services, player, shift), shift_panel(
            services, player, shift, key) if spec.jobs else None)
        return Panel(f"{special.icon} {special.title}",
                     (special.blurb, f"💰 {player.name}: {player.gold} gold"),
                     tuple(buttons), compact(*extra))
    return panel
