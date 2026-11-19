from typing import Any

from .content import VENUE_TEXTS
from .location import (
    implant_names, meat_cuts, prime_names, sausage_cut,
)


def butcher_comment(entry:dict[str, Any]) -> list[str]:
    texts = VENUE_TEXTS["butcher_shop"]
    cuts = meat_cuts(entry)
    count = f"{len(cuts)} cut" + ("s" if len(cuts) > 1 else "")
    lines = [texts["yield"].format(count=count, dead=entry["name"],
                                   cuts=", ".join(cuts))]
    sausage = sausage_cut(entry)
    if sausage:
        lines.append(texts["sausage"].format(sausage=sausage))
    prime = prime_names(entry)
    if prime:
        lines.append(texts["prime"].format(cuts=", ".join(prime)))
    implants = implant_names(entry)
    if implants:
        lines.append(texts["implants"].format(
            items=" and ".join(implants), dead=entry["name"]))
    if entry.get("victim", {}).get("shape") == "Equine":
        lines.append(texts["horse"].format(dead=entry["name"]))
    return lines
