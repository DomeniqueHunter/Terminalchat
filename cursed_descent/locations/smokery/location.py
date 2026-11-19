import random
from typing import Any

from ...config import (
    SMOKERY_CYCLES, SMOKERY_PAY, SMOKERY_RELEASE, SMOKERY_STAGE_PAY,
    SMOKERY_SURVIVOR_BONUS,
    SMOKERY_SURVIVE, SMOKERY_SURVIVE_MAX, SMOKERY_VIT_GAIN,
    SMOKERY_VIT_STEP,
)
from ...content import ITEMS
from ...models import Message, Player
from ..butcher.location import meat_cuts, meat_unsold, prime_names, \
    register_meat
from ...curing import cure_stage, ripen
from ..common import listing, pronouns, unique_names
from .content import SMOKERY_TRAITS, VENUE_TEXTS


def smoke_chance(player:Player) -> float:
    chance = SMOKERY_SURVIVE + (player.stats["vitality"] - 10
                                ) * SMOKERY_VIT_STEP
    return min(chance, SMOKERY_SURVIVE_MAX)


class SmokeryMixin:
    session: Any
    event: dict[str, Any]

    def smoke_boxes(self) -> dict[str, int]:
        return self.event.setdefault("data", {}).setdefault("smoke", {})

    def smokery_look(self) -> dict[str, str]:
        texts = VENUE_TEXTS["smokery"]
        return {"owner": "", "outside": texts["look_outside"],
                "inside": texts["look_inside"]}

    def smoke_pay(self) -> int:
        return round(SMOKERY_PAY * (1 + self.session.stage
                                    * SMOKERY_STAGE_PAY))

    def smokery_options(self) -> list[str]:
        boxes = self.smoke_boxes()
        free = [member for member in self.session.living()
                if member.name not in boxes]
        buys = [f"buy {nr}" for nr, _, _ in self.venue_stock()]
        if boxes:
            return (["smoke"] if free else []) + ["endure", "beg"] + buys
        return ["smoke"] + buys + ["depart"]

    def smokery_stock(self) -> list[str]:
        pieces = [item_id for entry in self.located("smoked")
                  for item_id in meat_unsold(entry)]
        return [item_id for item_id in pieces
                if item_id in ITEMS and item_id not in self.event["used"]]

    def smokery_bought(self, item_id:str) -> None:
        self.event["used"].add(item_id)
        for entry in self.located("smoked"):
            if item_id in meat_unsold(entry):
                entry.setdefault("meat_sold_ids", []).append(item_id)
        self.session.remains.save()

    def smoke_status(self) -> list[str]:
        return [f"{name}: in the box, cycle {cycle}/{SMOKERY_CYCLES}"
                for name, cycle in self.smoke_boxes().items()]

    def offer_smokery(self) -> list[str]:
        texts = VENUE_TEXTS["smokery"]
        self.event["data"]["inside"] = False
        return ["", texts["intro"], texts["door"], self.options_line(texts)]

    def enter_smokery(self) -> list[Message]:
        texts = VENUE_TEXTS["smokery"]
        self.event["data"]["inside"] = True
        entries = self.located("smoked")
        unique = unique_names(entries)
        lines = [texts["enter"]]
        lines += self.ripen_racks(entries)
        if not unique:
            lines.append(texts["nobody"])
        lines += listing(unique, texts["hanging"], texts["more"])
        lines += self.own_lines(unique, texts["own"])
        return self.continue_venue(lines)

    def ripen_racks(self, entries:list[dict[str, Any]]) -> list[str]:
        texts = VENUE_TEXTS["smokery"]
        changed = [entry for entry in entries if ripen(entry)]
        for entry in changed:
            register_meat(entry)
        if entries:
            self.session.remains.save()
        counts: dict[str, int] = {}
        for entry in entries:
            label = cure_stage(entry)[0]
            counts[label] = counts.get(label, 0) + 1
        if not counts:
            return []
        summary = ", ".join(f"{count} {label}"
                            for label, count in counts.items())
        lines = [texts["racks"].format(summary=summary)]
        if changed:
            lines.append(texts["ripen"].format(count=len(changed)))
        return lines

    def smokery_action(self, player:Player, command:str,
                       now:float) -> list[Message] | None:
        word = command.split()[0]
        texts = VENUE_TEXTS["smokery"]
        boxes = self.smoke_boxes()
        values = {"name": player.name}
        if word == "depart" and boxes:
            return [Message(texts["blocked"].format(**values), player.name)]
        if word == "smoke":
            if player.name in boxes:
                return [Message(texts["busy"].format(**values),
                                player.name)]
            return self.smoke_start(player)
        if word in ("endure", "beg"):
            if player.name not in boxes:
                return [Message(texts["idle"].format(**values),
                                player.name)]
            lines = (self.smoke_beg(player) if word == "beg"
                     else self.smoke_cycle(player))
            return self.smoke_after(player, lines)
        return None

    def smoke_after(self, player:Player, lines:list[str]) -> list[Message]:
        self.session.repository.save(player)
        if not self.session.living():
            self.reset()
            return [Message("\n".join(lines + self.session.end_run()))]
        return self.continue_venue(lines)

    def smoke_start(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["smokery"]
        pay = self.smoke_pay()
        player.gold += pay
        self.smoke_boxes()[player.name] = 0
        lines = [texts["pay"].format(pay=pay),
                 texts["start"].format(name=player.name, pay=pay)]
        return self.smoke_after(player, lines + self.smoke_cycle(player))

    def smoke_beg(self, player:Player) -> list[str]:
        texts = VENUE_TEXTS["smokery"]
        if random.random() < SMOKERY_RELEASE:
            del self.smoke_boxes()[player.name]
            return [texts["beg_ok"].format(name=player.name)]
        return [texts["beg_no"].format(name=player.name)]

    def smoke_cycle(self, player:Player) -> list[str]:
        texts = VENUE_TEXTS["smokery"]
        boxes = self.smoke_boxes()
        boxes[player.name] += 1
        cycle = boxes[player.name]
        lines = [texts["cycles"][cycle - 1].format(
            name=player.name, their=pronouns(player.gender)[2]),
                 texts["turn"].format(name=player.name, cycle=cycle,
                                      cycles=SMOKERY_CYCLES)]
        if random.random() > smoke_chance(player):
            return lines + self.smoke_kill(player)
        if cycle >= SMOKERY_CYCLES:
            return lines + self.smoke_survive(player)
        return lines

    def smoke_survive(self, player:Player) -> list[str]:
        del self.smoke_boxes()[player.name]
        player.stats["vitality"] += SMOKERY_VIT_GAIN
        player.profile["smoked"] = player.profile.get("smoked", 0) + 1
        bonus = round(self.smoke_pay() * SMOKERY_SURVIVOR_BONUS)
        player.gold += bonus
        return [VENUE_TEXTS["smokery"]["survive"].format(
            name=player.name, bonus=bonus),
                random.choice(SMOKERY_TRAITS).format(name=player.name),
                f"{player.name} gains +{SMOKERY_VIT_GAIN} vitality."]

    def smoke_kill(self, player:Player) -> list[str]:
        from ...combat import fate_text
        texts = VENUE_TEXTS["smokery"]
        boxes_cycle = self.smoke_boxes().pop(player.name)
        text = fate_text(player, "smoked", None)
        player.last_fate = "smoked"
        player.last_fate_text = text
        cycle = min(max(boxes_cycle, 1), SMOKERY_CYCLES)
        dying = texts["dying"][cycle - 1].format(
            name=player.name, their=pronouns(player.gender)[2],
            them=pronouns(player.gender)[1])
        lines = [f"🦶 {dying}"] + self.session.kill_outside(
            player, "smoked", text, "Jorveig", "nords")
        entry = self.session.remains.entries[-1]
        entry["cure"] = max(boxes_cycle, 1)
        self.session.remains.save()
        register_meat(entry)
        cuts = meat_cuts(entry)
        lines.append(texts["carve"].format(dead=player.name,
                                           cuts=", ".join(cuts)))
        lines.append(texts["hang"][cure_stage(entry)[0]].format(
            dead=player.name))
        prime = prime_names(entry)
        if prime:
            lines.append(texts["prime"].format(cuts=", ".join(prime)))
        return lines

    def finish_smoke_boxes(self) -> list[str]:
        lines: list[str] = []
        for name in list(self.smoke_boxes()):
            player = self.session.member(name)
            while player and name in self.smoke_boxes() and player.alive:
                lines += self.smoke_cycle(player)
        return lines
