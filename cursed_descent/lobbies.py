from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field

from .config import MAX_LOBBIES


@dataclass
class Bundle:
    id: str
    session: object
    ready: object
    offline: dict[str, float] = field(default_factory=dict)


class Lobbies:
    def __init__(self, primary:Bundle,
                 factory:Callable[[str], Bundle]) -> None:
        self.primary = primary
        self.factory = factory
        self.extras: list[Bundle] = []
        self.viewless = factory("L0")
        self.forced: list[Bundle] = []
        self.focus_name = ""
        self.invites: dict[str, str] = {}
        self.counter = 0

    def all(self) -> list[Bundle]:
        return [self.primary, *self.extras]

    def get(self, bundle_id:str) -> Bundle | None:
        return next((bundle for bundle in self.all()
                     if bundle.id == bundle_id), None)

    def of(self, name:str) -> Bundle | None:
        return next((bundle for bundle in self.all()
                     if bundle.session.member(name) is not None), None)

    def current(self) -> Bundle:
        if self.forced:
            return self.forced[-1]
        if not self.focus_name:
            return self.primary
        found = self.of(self.focus_name)
        if found is not None:
            return found
        return self.primary if self.primary.session.state == "idle" \
            else self.viewless

    @contextmanager
    def focus(self, name:str) -> Iterator[None]:
        before = self.focus_name
        self.focus_name = name
        try:
            yield
        finally:
            self.focus_name = before

    @contextmanager
    def on(self, bundle:Bundle) -> Iterator[None]:
        self.forced.append(bundle)
        try:
            yield
        finally:
            self.forced.pop()

    def busy(self) -> int:
        return sum(1 for bundle in self.all()
                   if bundle.session.state != "idle")

    def free_bundle(self) -> Bundle | None:
        if self.primary.session.state == "idle":
            return self.primary
        for bundle in self.extras:
            if bundle.session.state == "idle":
                return bundle
        if self.busy() >= MAX_LOBBIES:
            return None
        self.counter += 1
        bundle = self.factory(f"L{self.counter}")
        self.extras.append(bundle)
        return bundle

    def prune(self) -> None:
        self.extras = [bundle for bundle in self.extras
                       if bundle.session.state != "idle"]
        open_leaders = {bundle.session.party[0].name
                        for bundle in self.all()
                        if bundle.session.state == "lobby"
                        and bundle.session.party}
        self.invites = {name: leader for name, leader in self.invites.items()
                        if leader in open_leaders
                        and self.of(name) is None}

    def open_lobbies(self) -> list[Bundle]:
        return [bundle for bundle in self.all()
                if bundle.session.state == "lobby" and bundle.session.party]

    def find(self, word:str) -> Bundle | None:
        wanted = word.casefold()
        for bundle in self.open_lobbies():
            leader = bundle.session.party[0].name.casefold()
            if wanted in (bundle.id.casefold(), leader) or leader.startswith(
                    f"{wanted} "):
                return bundle
        return None
