from typing import Any

from .config import DEFAULT_GENDER, EXAMINE_LIST_MAX, PRONOUNS, TRIBE_NAMES
from .content import EXAMINE_TEXTS, FATE_LABELS, ITEMS
from .identity import same_character
from .locations.shop.location import item_summary


def fate_label(entry:dict[str, Any]) -> str:
    detailed = f"{entry['fate']}_{entry.get('detail', '')}"
    return FATE_LABELS.get(detailed,
                           FATE_LABELS.get(entry["fate"], entry["fate"]))


def hero_line(entry:dict[str, Any], repository:Any) -> str:
    hero = repository.load(entry["name"])
    level = f", level {hero.level}" if hero else ""
    when = f" ({entry['date']})" if entry.get("date") else ""
    return (f"{entry['name']} ({entry['gender']}{level}) – "
            f"{fate_label(entry)}, stage {entry['stage']}, "
            f"by {entry['killer']}{when}")


def history_line(entry:dict[str, Any],
                 entries:list[dict[str, Any]]) -> str:
    earlier = [other for other in entries
               if same_character(other, entry) and other is not entry]
    if not earlier:
        return EXAMINE_TEXTS["first"].format(dead=entry["name"])
    fates: dict[str, int] = {}
    for other in earlier:
        label = fate_label(other)
        fates[label] = fates.get(label, 0) + 1
    common = max(fates, key=lambda label: fates[label])
    count = len(earlier)
    deaths = "earlier death" if count == 1 else "earlier deaths"
    return EXAMINE_TEXTS["history"].format(dead=entry["name"], count=count,
                                           deaths=deaths, fate=common)


def remains_report(entry:dict[str, Any], examiner:str,
                   entries:list[dict[str, Any]], repository:Any) -> list[str]:
    they = PRONOUNS.get(entry["gender"], PRONOUNS[DEFAULT_GENDER])[0]
    tribe = TRIBE_NAMES.get(entry["tribe"], entry["tribe"])
    lines = [EXAMINE_TEXTS["remains"].format(name=examiner),
             f"  • {hero_line(entry, repository)}",
             "  • " + EXAMINE_TEXTS["killer"].format(
                 killer=entry["killer"], tribe=tribe, they=they),
             "  • " + history_line(entry, entries)]
    if entry.get("soul"):
        lines.append("  • " + EXAMINE_TEXTS["soul"].format(
            dead=entry["name"], weapon=entry["soul"]))
    if entry.get("item") and not entry.get("looted"):
        lines.append("  • " + EXAMINE_TEXTS["item"].format(
            item=item_summary(entry["item"])))
    else:
        lines.append("  • " + EXAMINE_TEXTS["no_item"])
    neighbours = [other for other in entries
                  if other["stage"] == entry["stage"]
                  and other["name"] != entry["name"]]
    if neighbours:
        names = ", ".join(dict.fromkeys(other["name"]
                                        for other in neighbours[-5:]))
        lines.append("  • " + EXAMINE_TEXTS["neighbours"].format(
            stage=entry["stage"], names=names))
    return lines


def group_report(title:str, entries:list[dict[str, Any]],
                 repository:Any) -> list[str]:
    if not entries:
        return [EXAMINE_TEXTS["nothing"]]
    lines = [title]
    for entry in entries[-EXAMINE_LIST_MAX:]:
        lines.append(f"  • {hero_line(entry, repository)}")
    if len(entries) > EXAMINE_LIST_MAX:
        lines.append(EXAMINE_TEXTS["more"].format(
            count=len(entries) - EXAMINE_LIST_MAX))
    return lines


def garment_report(stock:list[str], boutique:Any) -> list[str]:
    victims = {entry["id"]: entry.get("victim_data", {})
               for entry in boutique.entries}
    lines = [EXAMINE_TEXTS["boutique"]]
    for item_id in stock:
        data = victims.get(item_id, {})
        stats = data.get("stats", {})
        best = max(stats, key=stats.get) if stats else "?"
        level = data.get("level", "?")
        build = data.get("body", {}).get("build", "?")
        lines.append(f"  • {ITEMS[item_id]['name']} – made from "
                     f"{ITEMS[item_id].get('made_from', '?')} (level {level}, "
                     f"{build}, strongest in {best})")
    return lines
