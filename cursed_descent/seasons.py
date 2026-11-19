from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Season:
    name: str
    start: tuple[int, int]
    end: tuple[int, int]

    def contains(self, today:date) -> bool:
        return self.start <= (today.month, today.day) <= self.end


SEASONS = {
    "winter": Season("winter", (12, 1), (12, 24)),
}
_ALL_YEAR = {"flag": False}


def set_all_year(flag:bool) -> None:
    _ALL_YEAR["flag"] = flag


def active(name:str, today:date | None=None) -> bool:
    if not name:
        return True
    if _ALL_YEAR["flag"]:
        return True
    return SEASONS[name].contains(today or date.today())


def active_names(today:date | None=None) -> list[str]:
    return [name for name in SEASONS if active(name, today)]
