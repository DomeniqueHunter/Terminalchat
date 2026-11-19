import random
from typing import Any

from ...config import (
    DEFAULT_GENDER, POLE_BOOT_GIFT_CHANCE, POLE_SHOWN, POLE_SLOPPY_CHANCE,
    PRONOUNS,
)
from ...content import ITEMS, RARITY_LABELS
from ...dungeon import give_item
from ...events.mrs_claus.event import pick_gift
from ...items import Item
from ...models import Message, Player
from ...formulas import max_hp
from .content import GIFT_TEXT, VENUE_TEXTS


def gift_creator(entry:dict[str, Any]) -> str:
    victim = entry.get("victim") or {}
    return "|".join(["gift", entry["name"], entry["gender"],
                     str(victim.get("level", 1)),
                     str(victim.get("build", "Average"))])


def gift_description(item:str) -> str:
    creator = getattr(item, "creator", "")
    if not creator.startswith("gift|"):
        return ""
    _, name, gender, level, build = creator.split("|")
    return GIFT_TEXT.format(name=name, gender=gender.lower(), level=level,
                            build=build.lower())


class NorthPoleMixin:
    session: Any
    event: dict[str, Any]

    def pole_entries(self) -> list[dict[str, Any]]:
        found = [entry for entry in self.session.remains.entries
                 if entry["fate"] == "sacked"
                 and not entry.get("harvested")
                 and entry["run"] != self.session.run_id]
        return list(reversed(found))[:POLE_SHOWN]

    def offer_north_pole(self) -> list[str]:
        texts = VENUE_TEXTS["north_pole"]
        self.event["data"] = {"inside": False, "boots": 0}
        return ["", random.choice(texts["intros"]),
                self.options_line(texts)]

    def north_pole_options(self) -> list[str]:
        used = self.event["used"]
        if not self.event["data"].get("inside"):
            return ["watch", "enter", "depart"]
        harvest = [f"harvest {nr}"
                   for nr, _ in enumerate(self.pole_entries(), 1)]
        talk = [option for option in ("talk", "deodorize")
                if option not in used]
        return talk + harvest + ["watch", "depart"]

    def north_pole_examine(self) -> list[Message]:
        texts = VENUE_TEXTS["north_pole"]
        if not self.event["data"].get("inside"):
            return [Message(texts["look_outside"])]
        entries = self.pole_entries()
        if not entries:
            return [Message(texts["look_none"])]
        lines = [texts["look"]]
        for nr, entry in enumerate(entries, 1):
            lines.append(texts["look_gift"].format(
                nr=nr, name=entry["name"], stage=entry["stage"]))
        return [Message("\n".join(lines))]

    def north_pole_action(self, player:Player, command:str,
                          now:float) -> list[Message] | None:
        parts = command.split()
        data = self.event["data"]
        inside = bool(data.get("inside"))
        if parts[0] == "enter" and not inside:
            data["inside"] = True
            return self.continue_venue([
                VENUE_TEXTS["north_pole"]["enter"]])
        if parts[0] == "watch":
            return self.pole_watch()
        if not inside:
            return None
        if parts[0] == "talk":
            return self.pole_talk(player)
        if parts[0] == "deodorize":
            return self.pole_boots(player)
        if parts[0] == "harvest" and len(parts) > 1 and parts[1].isdigit():
            return self.pole_harvest(player, int(parts[1]))
        return None

    def pole_watch(self) -> list[Message]:
        texts = VENUE_TEXTS["north_pole"]
        entries = self.pole_entries()
        roll = random.random()
        if roll < 0.3:
            line = random.choice(texts["watch_depart"])
        elif entries:
            entry = random.choice(entries)
            line = random.choice(texts["watch_wrap"]).format(
                name=entry["name"])
        else:
            line = texts["watch_none"]
        return self.continue_venue([line])

    def pole_talk(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["north_pole"]
        self.event["used"].add("talk")
        self.event["data"]["friendly"] = True
        self.heal_party(0.2)
        line = random.choice(texts["talk"]).format(name=player.name)
        return self.continue_venue([line])

    def pole_boots(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["north_pole"]
        data = self.event["data"]
        step = data.get("boots", 0) + 1
        data["boots"] = step
        their = PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])[2]
        lines = [texts[f"boots_{step}"].format(name=player.name,
                                               their=their)]
        if step < 3:
            return self.continue_venue(lines)
        self.event["used"].add("deodorize")
        friendly = bool(data.get("friendly"))
        sloppy = 0.0 if friendly else POLE_SLOPPY_CHANCE
        if random.random() < sloppy:
            lines.append(texts["boots_sloppy"].format(name=player.name))
            player.hp = max(1, player.hp - round(max_hp(player) * 0.15))
        else:
            if random.random() < POLE_BOOT_GIFT_CHANCE + (
                    0.2 if friendly else 0.0):
                item_id = pick_gift()
                lines.append(texts["boots_win"].format(
                    name=player.name, item=ITEMS[item_id]["name"]))
                lines.append(give_item(player, item_id))
            else:
                lines.append(texts["boots_friend"])
        self.session.repository.save(player)
        return self.continue_venue(lines)

    def pole_harvest(self, player:Player, number:int) -> list[Message]:
        texts = VENUE_TEXTS["north_pole"]
        entries = self.pole_entries()
        if not 1 <= number <= len(entries):
            return [Message(texts["gone"], player.name)]
        if len(player.inventory) >= player.bag_size:
            return [Message(texts["full"].format(name=player.name),
                            player.name)]
        entry = entries[number - 1]
        entry["harvested"] = True
        key = "own" if player.owns(entry) else "harvest"
        rarity = RARITY_LABELS[ITEMS["wrapped_gift"]["rarity"]]
        player.inventory.append(Item("wrapped_gift",
                                     creator=gift_creator(entry)))
        lines = [texts[key].format(name=player.name),
                 f"💎 {player.name} takes a Wrapped Gift ({rarity}) "
                 f"with {entry['name']} inside!"]
        self.session.remains.save()
        self.session.repository.save(player)
        return self.continue_venue(lines)
