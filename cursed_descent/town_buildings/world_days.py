import time
from pathlib import Path

from ..config import WEEKDAYS, WORLD_DAY_SECONDS, YEAR_DAYS
from ..storage import read_json, write_json


FILE_NAME = "world.json"


def calendar(day:int) -> tuple[int, int, str]:
    year, in_year = divmod(day, YEAR_DAYS)
    return year + 1, in_year + 1, WEEKDAYS[day % len(WEEKDAYS)]


def date_text(day:int) -> str:
    year, in_year, weekday = calendar(day)
    return f"{weekday}, day {in_year} of year {year}"


class WorldDays:
    def __init__(self, data_path:Path) -> None:
        self.path = data_path / FILE_NAME
        saved = read_json(self.path, {"day": 0})
        self.day: int = saved["day"]
        self.anchor: float = saved.get("anchor", time.time())
        if "anchor" not in saved:
            self.save()

    def save(self) -> None:
        write_json(self.path, {"day": self.day, "anchor": self.anchor})

    def due(self, wall:float | None=None) -> int:
        wall = time.time() if wall is None else wall
        return max(0, int((wall - self.anchor) // WORLD_DAY_SECONDS))

    def advance(self, days:int=1) -> int:
        self.day += days
        self.anchor += days * WORLD_DAY_SECONDS
        self.save()
        return self.day

    def seconds_left(self, wall:float | None=None) -> float:
        wall = time.time() if wall is None else wall
        return max(0.0, self.anchor + WORLD_DAY_SECONDS - wall)

    def elapsed(self, wall:float | None=None) -> float:
        wall = time.time() if wall is None else wall
        return min(float(WORLD_DAY_SECONDS), max(0.0, wall - self.anchor))

    def clock_text(self, wall:float | None=None) -> str:
        wall = time.time() if wall is None else wall
        share = min(1.0, max(0.0, (wall - self.anchor) / WORLD_DAY_SECONDS))
        minutes = int(share * 24 * 60)
        return f"{date_text(self.day)}, {minutes // 60:02d}:{minutes % 60:02d}"
