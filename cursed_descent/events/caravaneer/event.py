import random
from collections import Counter
from typing import Any

from ...dungeon import give_item, roll_item
from ...locations.common import pronouns
from ...models import Message, Player
from ..common import decide
from .content import EVENT_TEXTS
from .fates import FATES
from .npc import fill, is_candidate, pony_from, roster, trim
from .config import CAP, FATE


EPIC_PER_STAGE = 0.01
EPIC_MAX = 0.6


def rare_item(stage:int) -> str:
    from ...content import ITEMS
    uniques = [item_id for item_id, item in ITEMS.items()
               if item.get("caravan")]
    if uniques:
        return random.choice(uniques)
    rarity = "epic" if random.random() < min(
        EPIC_MAX, stage * EPIC_PER_STAGE) else "rare"
    pool = [item_id for item_id, item in ITEMS.items()
            if not item.get("no_loot") and item["rarity"] == rarity
            and item["slot"] != "consumable"]
    return random.choice(pool) if pool else roll_item(stage)


def ware_text(item_id:str) -> str:
    from ...locations.shop.location import item_summary
    return item_summary(item_id)


def npc_choice(member:Player, candidates:list[Player]) -> str:
    others = [candidate.name for candidate in candidates
              if candidate.name != member.name]
    pool = others or [candidate.name for candidate in candidates]
    return random.choice(pool) if pool else ""


def reward_taker(living:list[Player]) -> Player:
    humans = [member for member in living if not member.npc]
    pool = humans or living
    free = [member for member in pool
            if len(member.inventory) < member.bag_size]
    return random.choice(free or pool)


class CaravaneerMixin:
    session: Any
    event: dict[str, Any]

    def caravan_candidates(self) -> list[Player]:
        return [member for member in self.session.living()
                if is_candidate(member)]

    def caravan_choice_text(self, choice:str) -> str:
        return choice or EVENT_TEXTS["caravaneer"]["choice_refuse"]

    def offer_caravan(self) -> list[str]:
        texts = EVENT_TEXTS["caravaneer"]
        session = self.session
        team = fill(session.repository, random.Random())
        candidates = self.caravan_candidates()
        votes: dict[str, str] = {}
        for member in session.living():
            if member.npc and candidates:
                votes[member.name] = npc_choice(member, candidates)
        self.event["phase"] = "caravan"
        ware = rare_item(session.stage)
        self.event["data"].update(inside=True, votes=votes, ware=ware)
        lines = ["", texts["intro"].format(count=len(team)),
                 texts["ware"].format(item=ware_text(ware))]
        if candidates:
            lines.append(texts["candidates"].format(
                names=", ".join(member.name for member in candidates)))
            lines.append(texts["how"])
        else:
            lines.append(texts["none"])
        return lines

    def caravan_state(self) -> dict[str, Any]:
        data = self.event["data"]
        votes = data["votes"]
        living = [member.name for member in self.session.living()]
        return {"ware": data["ware"],
                "candidates": [member.name
                               for member in self.caravan_candidates()],
                "votes": {name: votes[name] for name in living
                          if name in votes},
                "missing": [name for name in living if name not in votes]}

    def caravan_options(self) -> list[str]:
        if self.caravan_candidates():
            return ["offer", "depart"]
        return ["depart"]

    def caravan_examine(self) -> list[Message]:
        texts = EVENT_TEXTS["caravaneer"]
        lines = [texts["examine"]]
        for pony in roster(self.session.repository):
            origin = (texts["origin"]
                      if pony.profile.get("adventurer") else "")
            lines.append(texts["examine_pony"].format(
                name=pony.full_name, gender=pony.gender, origin=origin))
        lines.append(texts["examine_cap"].format(cap=CAP))
        return [Message("\n".join(lines))]

    def caravan_pick(self, words:list[str]) -> Player | None:
        wanted = " ".join(words).casefold()
        if not wanted:
            return None
        found = [member for member in self.caravan_candidates()
                 if wanted in (member.name.casefold(),
                               member.first_name.casefold())
                 or member.name.casefold().startswith(wanted)]
        return found[0] if len(found) == 1 else None

    def caravan_action(self, player:Player, command:str, args:list[str],
                       now:float) -> list[Message]:
        texts = EVENT_TEXTS["caravaneer"]
        if command == "depart":
            return self.caravan_vote(player, "", now)
        target = self.caravan_pick(args)
        if target is None:
            candidates = self.caravan_candidates()
            key = "unknown" if args else "bad_choice"
            example = candidates[0].name if candidates else "name"
            return [Message(texts[key].format(example=example),
                            player.name)]
        return self.caravan_vote(player, target.name, now)

    def caravan_vote(self, voter:Player, choice:str,
                     now:float) -> list[Message]:
        texts = EVENT_TEXTS["caravaneer"]
        session = self.session
        votes = self.event["data"]["votes"]
        votes[voter.name] = choice
        session.deadline = self.idle_deadline(now)
        voters = [member.name for member in session.living()]
        lines = [texts["vote"].format(
            name=voter.name, choice=self.caravan_choice_text(choice))]
        counts = Counter(value for name, value in votes.items()
                         if name in voters)
        top, best = counts.most_common(1)[0]
        if best >= len(voters) // 2 + 1:
            return self.caravan_resolve(top, lines, now)
        missing = [name for name in voters if name not in votes]
        if not missing:
            top, tie = decide(votes, voters)
            if tie:
                lines.append(texts["tie"])
            return self.caravan_resolve(top, lines, now)
        tally = ", ".join(f"{self.caravan_choice_text(choice)} {count}"
                          for choice, count in counts.most_common())
        lines.append(texts["waiting"].format(
            tally=tally, missing=", ".join(missing)))
        return [Message("\n".join(lines))]

    def caravan_expire(self, now:float) -> list[Message]:
        texts = EVENT_TEXTS["caravaneer"]
        votes = self.event["data"].get("votes", {})
        voters = [member.name for member in self.session.living()]
        humans = [member.name for member in self.session.living()
                  if not member.npc]
        if not any(name in votes for name in humans):
            self.save_party()
            return self.finish([texts["timeout"]], now)
        cast = {name: choice for name, choice in votes.items()
                if name in humans}
        top, tie = decide(cast, voters)
        lines = [texts["tie"]] if tie else []
        return self.caravan_resolve(top, lines, now)

    def caravan_resolve(self, choice:str, lines:list[str],
                        now:float) -> list[Message]:
        texts = EVENT_TEXTS["caravaneer"]
        session = self.session
        victim = session.member(choice) if choice else None
        ware = self.event["data"]["ware"]
        if victim is None:
            self.save_party()
            return self.finish(lines + [texts["refused"]], now)
        they, _, their = pronouns(victim.gender)
        fate = random.choice(FATES[FATE]["any"]).format(
            name=victim.name, they=they, their=their)
        pony_from(session.repository, victim)
        lines.append(texts["deal"])
        lines += session.kill_outside(victim, FATE, fate,
                                      "the Caravaneer", "caravan")
        lines += trim(session.repository)
        living = session.living()
        if not living:
            lines.append(texts["no_reward"])
            self.reset()
            return [Message("\n".join(lines + session.end_run()))]
        finder = reward_taker(living)
        lines.append(texts["reward"].format(finder=finder.name))
        lines.append(give_item(finder, ware))
        self.save_party()
        return self.finish(lines, now)
