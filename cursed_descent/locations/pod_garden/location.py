import random
from typing import Any

from ...config import POD_FATES, POD_SHOWN
from ...content import ITEMS
from ...dungeon import give_item
from ...items import restore_item
from ...models import Message, Player
from .content import (
    HARVEST_SCENES, KIND_NAMES, MARKERS, POD_LOOKS, VENUE_TEXTS,
)


def pod_variant(text:str) -> str:
    lowered = text.casefold()
    for word, kind in MARKERS:
        if word in lowered:
            return kind
    return "classic"


class PodGardenMixin:
    session: Any
    event: dict[str, Any]

    def pod_entries(self) -> list[dict[str, Any]]:
        found = [entry for entry in self.session.remains.entries
                 if entry["fate"] in POD_FATES
                 and not entry.get("harvested")
                 and entry["run"] != self.session.run_id]
        return list(reversed(found))[:POD_SHOWN]

    def offer_pod_garden(self) -> list[str]:
        texts = VENUE_TEXTS["pod_garden"]
        return ["", random.choice(texts["intros"]),
                self.options_line(texts)]

    def pod_garden_options(self) -> list[str]:
        harvest = [f"harvest {nr}"
                   for nr, _ in enumerate(self.pod_entries(), 1)]
        return harvest + ["depart"]

    def pod_garden_examine(self) -> list[Message]:
        texts = VENUE_TEXTS["pod_garden"]
        entries = self.pod_entries()
        if not entries:
            return [Message(texts["look_none"])]
        lines = [texts["look"]]
        for nr, entry in enumerate(entries, 1):
            kind = entry.get("detail") or "classic"
            lines.append(texts["look_pod"].format(
                nr=nr, kind=KIND_NAMES[kind], name=entry["name"],
                stage=entry["stage"],
                look=POD_LOOKS[kind].format(name=entry["name"])))
        return [Message("\n".join(lines))]

    def pod_garden_action(self, player:Player, command:str,
                          now:float) -> list[Message] | None:
        parts = command.split()
        if parts[0] != "harvest" or len(parts) < 2 or not parts[1].isdigit():
            return None
        texts = VENUE_TEXTS["pod_garden"]
        entries = self.pod_entries()
        number = int(parts[1])
        if not 1 <= number <= len(entries):
            return [Message(texts["gone"], player.name)]
        entry = entries[number - 1]
        if len(player.inventory) >= player.bag_size:
            return [Message(texts["full"].format(name=player.name),
                            player.name)]
        kind = entry.get("detail") or "classic"
        item_id = f"pod_{kind}"
        entry["harvested"] = True
        values = {"name": player.name, "kind": KIND_NAMES[kind],
                  "their": "their"}
        scene = HARVEST_SCENES[kind].format(**values)
        lines = [texts["own"].format(**values) if player.owns(entry)
                 else scene, give_item(player, item_id)]
        if random.random() < 0.5:
            lines.append(texts["bloom"].format(
                name=player.name, item=ITEMS["pod_goo"]["name"]))
            lines.append(give_item(player, "pod_goo"))
        if random.random() < 0.4:
            lines.append(texts["seed"].format(
                name=player.name, item=ITEMS["pod_seed"]["name"]))
            lines.append(give_item(player, "pod_seed"))
        if entry.get("item") and not entry.get("looted"):
            item = restore_item(entry["item"], entry.get("item_state"))
            if len(player.inventory) < player.bag_size:
                player.inventory.append(item)
                entry["looted"] = True
                lines.append(texts["gear"].format(
                    item=ITEMS[str(item)]["name"]))
        self.session.remains.save()
        self.session.repository.save(player)
        return self.continue_venue(lines)
