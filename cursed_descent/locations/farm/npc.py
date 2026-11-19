import random
from typing import Any


class FarmNpcMixin:
    session: Any
    event: dict[str, Any]

    def worker_name(self) -> str:
        names = [entry["name"] for entry in self.located("farmed")]
        return random.choice(names) if names else ""
