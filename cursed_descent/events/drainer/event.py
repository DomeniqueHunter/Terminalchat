import random
from collections import Counter
from typing import Any

from ...content import ENEMIES
from ...dungeon import build_enemy, give_item
from ...models import Message, Player
from ..common import decide, their
from .config import SHELF_LIMIT
from .content import EVENT_TEXTS
from .ledger import (
    Ledger, bottle_name, drain, item_id_of, next_part,
)


FIGHT = "!fight"


class DrainerMixin:
    session: Any
    event: dict[str, Any]

    def drainer_ledger(self) -> Ledger:
        return Ledger(self.session.repository.data_path)

    def drainer_voters(self) -> list[Player]:
        return [member for member in self.session.living()
                if not member.npc]

    def drainer_candidates(self) -> list[Player]:
        return [member for member in self.drainer_voters()
                if next_part(member)]

    def drainer_recipients(self) -> list[Player]:
        bottle = self.event["data"].get("bottle")
        if bottle is None:
            return []
        return [member for member in self.drainer_voters()
                if len(member.inventory) < member.bag_size]

    def drainer_shelf(self) -> list[str]:
        texts = EVENT_TEXTS["drainer"]
        bottles = self.drainer_ledger().bottles()
        if not bottles:
            return [texts["shelf_empty"]]
        lines = [texts["shelf_head"]]
        for bottle in bottles[:SHELF_LIMIT]:
            lines.append(texts["shelf_line"].format(
                victim=bottle["victim"],
                thing=texts[f"name_{bottle['part']}"]))
        if len(bottles) > SHELF_LIMIT:
            lines.append(texts["shelf_more"].format(
                count=len(bottles) - SHELF_LIMIT))
        return lines

    def offer_drainer(self) -> list[str]:
        texts = EVENT_TEXTS["drainer"]
        self.event["phase"] = "drainer"
        self.event["data"].update(inside=True, mode="offer", votes={})
        lines = ["", texts["intro"]] + self.drainer_shelf()
        candidates = self.drainer_candidates()
        if candidates:
            lines.append(texts["candidates"].format(
                names=", ".join(member.name for member in candidates)))
            lines.append(texts["how"])
        else:
            lines += [texts["none"], texts["how_fight"]]
        return lines

    def offer_restore(self, now:float) -> list[str]:
        session = self.session
        texts = EVENT_TEXTS["drainer"]
        bottle = self.drainer_ledger().take_random()
        if bottle is None:
            return session.begin_stage(now)
        session.state = "event"
        session.deadline = self.idle_deadline(now)
        self.event = {"kind": "drainer", "phase": "drainer", "used": set(),
                      "data": {"inside": True, "mode": "restore",
                               "votes": {}, "bottle": bottle}}
        if not self.drainer_recipients():
            self.drainer_ledger().release(bottle["id"])
            self.reset()
            return [texts["restore_none"]] + session.begin_stage(now)
        return ["", texts["restore_intro"].format(
            bottle=bottle_name(bottle)), texts["restore_how"]]

    def drainer_state(self) -> dict[str, Any]:
        data = self.event["data"]
        votes = data["votes"]
        voters = [member.name for member in self.drainer_voters()]
        restoring = data["mode"] == "restore"
        bottle = data.get("bottle")
        return {
            "mode": data["mode"],
            "shelf": self.drainer_shelf(),
            "bottle": bottle_name(bottle) if bottle else "",
            "targets": [member.name for member in (
                self.drainer_recipients() if restoring
                else self.drainer_candidates())],
            "votes": {name: votes[name] for name in voters
                      if name in votes},
            "missing": [name for name in voters if name not in votes]}

    def drainer_options(self) -> list[str]:
        if self.event["data"]["mode"] == "restore":
            return ["give", "depart"]
        if self.drainer_candidates():
            return ["sacrifice", "challenge"]
        return ["challenge"]

    def drainer_examine(self) -> list[Message]:
        lines = [EVENT_TEXTS["drainer"]["examine"]] + self.drainer_shelf()
        return [Message("\n".join(lines))]

    def drainer_pick(self, words:list[str]) -> Player | None:
        wanted = " ".join(words).casefold()
        if not wanted:
            return None
        pool = (self.drainer_recipients()
                if self.event["data"]["mode"] == "restore"
                else self.drainer_candidates())
        found = [member for member in pool
                 if wanted in (member.name.casefold(),
                               member.first_name.casefold())
                 or member.name.casefold().startswith(wanted)]
        return found[0] if len(found) == 1 else None

    def drainer_action(self, player:Player, command:str, args:list[str],
                       now:float) -> list[Message]:
        texts = EVENT_TEXTS["drainer"]
        if command == "challenge":
            return self.drainer_vote(player, FIGHT, now)
        if command == "depart":
            return self.drainer_vote(player, "", now)
        target = self.drainer_pick(args)
        if target is None:
            pool = (self.drainer_recipients()
                    if self.event["data"]["mode"] == "restore"
                    else self.drainer_candidates())
            key = "unknown" if args else "bad_choice"
            example = pool[0].name if pool else "name"
            return [Message(texts[key].format(example=example),
                            player.name)]
        return self.drainer_vote(player, target.name, now)

    def drainer_vote_text(self, voter:Player, choice:str) -> str:
        texts = EVENT_TEXTS["drainer"]
        restoring = self.event["data"]["mode"] == "restore"
        if choice == FIGHT:
            return texts["vote_fight"].format(name=voter.name)
        if restoring and not choice:
            return texts["vote_leave"].format(name=voter.name)
        key = "vote_give" if restoring else "vote_name"
        return texts[key].format(name=voter.name, choice=choice)

    def drainer_vote(self, voter:Player, choice:str,
                     now:float) -> list[Message]:
        texts = EVENT_TEXTS["drainer"]
        session = self.session
        votes = self.event["data"]["votes"]
        votes[voter.name] = choice
        session.deadline = self.idle_deadline(now)
        voters = [member.name for member in self.drainer_voters()]
        lines = [self.drainer_vote_text(voter, choice)]
        counts = Counter(value for name, value in votes.items()
                         if name in voters)
        top, best = counts.most_common(1)[0]
        if best >= len(voters) // 2 + 1:
            return self.drainer_resolve(top, lines, now)
        missing = [name for name in voters if name not in votes]
        if not missing:
            top, tie = decide(votes, voters)
            if tie:
                lines.append(texts["tie"])
            return self.drainer_resolve(top, lines, now)
        tally = ", ".join(f"{self.drainer_tally_name(value)} {count}"
                          for value, count in counts.most_common())
        lines.append(texts["waiting"].format(
            tally=tally, missing=", ".join(missing)))
        return [Message("\n".join(lines))]

    def drainer_tally_name(self, value:str) -> str:
        if value == FIGHT:
            return "fight"
        return value or "leave it"

    def drainer_expire(self, now:float) -> list[Message]:
        texts = EVENT_TEXTS["drainer"]
        data = self.event["data"]
        voters = [member.name for member in self.drainer_voters()]
        cast = {name: choice for name, choice in data["votes"].items()
                if name in voters}
        if not cast:
            if data["mode"] == "restore":
                self.drainer_ledger().release(data["bottle"]["id"])
            self.save_party()
            return self.finish([texts["timeout"]], now)
        top, tie = decide(cast, voters)
        return self.drainer_resolve(top, [texts["tie"]] if tie else [], now)

    def drainer_resolve(self, choice:str, lines:list[str],
                        now:float) -> list[Message]:
        if self.event["data"]["mode"] == "restore":
            return self.drainer_pour(choice, lines, now)
        if choice == FIGHT:
            return self.drainer_fight(lines, now)
        return self.drainer_sacrifice(choice, lines, now)

    def drainer_fight(self, lines:list[str], now:float) -> list[Message]:
        session = self.session
        self.reset()
        enemy = build_enemy(1, "drainer", ENEMIES["drainer"], session.stage)
        enemy.boss = True
        intro = [""] + lines + [EVENT_TEXTS["drainer"]["fight"]]
        return [Message("\n".join(
            session.start_bonus_fight("drainer", [enemy], intro, now)))]

    def drainer_sacrifice(self, choice:str, lines:list[str],
                          now:float) -> list[Message]:
        texts = EVENT_TEXTS["drainer"]
        victim = self.session.member(choice)
        bottle = drain(victim, self.session.stage) if victim else None
        if victim is None or bottle is None:
            self.save_party()
            return self.finish(lines + [texts["timeout"]], now)
        self.drainer_ledger().add(bottle)
        values = {"name": victim.name, "their": their(victim),
                  "label": bottle["label"]}
        lines += [texts["deal"].format(**values),
                  texts[f"drain_{bottle['part']}"].format(**values),
                  texts["bottled"].format(**values)]
        self.save_party()
        return self.finish(lines, now)

    def drainer_pour(self, choice:str, lines:list[str],
                     now:float) -> list[Message]:
        texts = EVENT_TEXTS["drainer"]
        bottle = self.event["data"]["bottle"]
        receiver = self.session.member(choice) if choice else None
        if receiver is None:
            self.drainer_ledger().release(bottle["id"])
            self.save_party()
            return self.finish(lines + [texts["restore_left"]], now)
        lines.append(texts["restore_given"].format(name=receiver.name))
        lines.append(give_item(receiver, item_id_of(bottle)))
        self.save_party()
        return self.finish(lines, now)

    def drainer_wipe(self) -> list[str]:
        texts = EVENT_TEXTS["drainer"]
        pool = [member for member in self.session.party
                if not member.npc and next_part(member)]
        if not pool:
            return []
        victim = random.choice(pool)
        bottle = drain(victim, self.session.stage)
        self.drainer_ledger().add(bottle)
        return [texts["wipe"].format(name=victim.name),
                EVENT_TEXTS["drainer"][f"drain_{bottle['part']}"].format(
                    name=victim.name, their=their(victim),
                    label=bottle["label"])]
