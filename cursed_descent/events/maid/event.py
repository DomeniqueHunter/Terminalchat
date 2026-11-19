import copy
import random
import uuid
from typing import Any

from ...config import (
    COMPANION_NAME,
    MAID_DEATH_PER_HIT, MAID_GENDERS, MAID_HITS, MAID_ROUND_HITS,
    MAID_STR_PER_LEVEL, MAID_VIT_PER_LEVEL,
    MAX_PARTY_SIZE, POINTS_PER_LEVEL, ROUND_TIMEOUT_SECONDS,
)
from ...content import BUFFS, EVENT_TEXTS
from ...formulas import apply_buff, max_hp, set_bonus_text
from ...models import Message, Player
from ...npcs.hire import spend_points
from ...settings import PROTOTYPES, ensure_loaded
from ..common import options_text, their
from .ledger import STOOD, result_word
from .content import (
    BUILD_LINES, FLATTERY, FLATTERY_ANY, NICKNAMES, ROUND_TEXTS, SCREAMS,
    SCREAMS_B,
)


FATE_KEYS = (
    "paddle_shattered",
    "paddle_popped",
    "paddle_busted",
    "paddle_squashed",
    "paddle_decimated",
    "paddle_mangled",
    "paddle_obliterated",
    "paddle_annihilated",
    "paddle_vaporized",
    "paddle_demolished",
    "paddle_wiped_out",
    "paddle_eradicated",
    "paddle_pummeled",
    "paddle_terminated",
    "paddle_shredded",
    "paddle_eviscerated",
    "paddle_exterminated",
    "paddle_disintegrated",
)


def first_hit_death(rng:random.Random, hits:int=MAID_ROUND_HITS) -> int:
    for hit in range(1, hits + 1):
        if rng.random() < MAID_DEATH_PER_HIT:
            return hit
    return 0


def hit_lines(player:Player, step:int, dead_hit:int) -> list[str]:
    cries = random.choice((SCREAMS, SCREAMS_B))[step].split(" — ")
    last = dead_hit or MAID_ROUND_HITS
    return [f"💥 SMACK {step * MAID_ROUND_HITS + number}! "
            f"💬 {player.name}: {cries[(number - 1) % len(cries)]}"
            for number in range(1, last + 1)]


def make_companion(party_level:int) -> Player:
    ensure_loaded()
    record = copy.deepcopy(PROTOTYPES["constance"])
    record.update(name=COMPANION_NAME, first_name=COMPANION_NAME,
                  last_name="Whackshire", npc="mercenary",
                  id=uuid.uuid4().hex)
    player = Player.from_dict(record)
    player.profile = {
        "kind": "mercenary", "blurb": "A wandering maid who swings a "
        "2.5 m paddle", "role": "mercenary",
        "focus": ["strength", "vitality"], "home": ""}
    player.level = max(1, party_level)
    player.free_points = (player.level - 1) * POINTS_PER_LEVEL
    spend_points(player)
    player.stats["vitality"] += player.level * MAID_VIT_PER_LEVEL
    player.stats["strength"] += player.level * MAID_STR_PER_LEVEL
    player.hp = max_hp(player)
    return player


class MaidMixin:
    session: Any
    event: dict[str, Any]

    def maid_free(self) -> bool:
        return len(self.session.party) < MAX_PARTY_SIZE

    def maid_taken(self) -> bool:
        return self.session.repository.exists(COMPANION_NAME)

    def offer_maid(self) -> list[str]:
        texts = EVENT_TEXTS["buster_maid"]
        self.event["phase"] = "maid"
        self.event["data"]["inside"] = True
        self.session.buster_ledger.bump("met")
        lines = ["", texts["intro"], random.choice(texts["meet"]).format(
            nick=random.choice(NICKNAMES))]
        if not self.maid_free():
            lines.append(texts["full"])
        else:
            lines.append(random.choice(texts["condition"]))
            lines += self.maid_flattery()
        lines.append(self.strip_timer(texts["options"]).format(
            options=options_text(self.available()),
            seconds=int(ROUND_TIMEOUT_SECONDS)))
        return lines

    def maid_examine(self) -> list[Message]:
        from ...content import ITEMS
        texts = EVENT_TEXTS["buster_maid"]
        ensure_loaded()
        record = PROTOTYPES.get("constance", {})
        look = record.get("profile", {}).get("look", "")
        worn = [ITEMS[item["id"]]["name"]
                for item in record.get("equipment", {}).values()
                if item and item["id"] in ITEMS]
        lines = [texts["examine"], look]
        if worn:
            lines.append("She wears: " + ", ".join(worn) + ".")
        lines.append(texts["examine_buster"])
        ledger = self.session.buster_ledger
        if ledger.total():
            lines.append(texts["examine_ledger"].format(
                summary=ledger.summary()))
        return [Message("\n".join(lines))]

    def maid_history(self, player:Player) -> list[Message]:
        texts = EVENT_TEXTS["buster_maid"]
        ledger = self.session.buster_ledger
        lines = [random.choice(texts["history_intro"])]
        if not ledger.total():
            lines.append(texts["history_none"])
            return self.continue_event(lines)
        lines.append(texts["history_total"].format(
            total=ledger.total(), fallen=ledger.fallen(),
            stood=ledger.stood()))
        best, worst, last = ledger.best(), ledger.worst(), ledger.last()
        lines.append(texts["history_best"].format(
            name=best["name"], hit=best["hit"],
            result=result_word(best["result"])))
        if worst is not None:
            lines.append(texts["history_worst"].format(**worst))
        lines.append(texts["history_last"].format(
            name=last["name"], word=result_word(last["result"])))
        lines.append(texts["history_roll"])
        lines += [f"   {entry['name']}: {result_word(entry['result'])}, "
                  f"hit {entry['hit']}"
                  for entry in ledger.sample(6, random.Random())]
        lines.append(texts["history_roll_end"])
        meta = ledger.meta
        lines.append(texts["history_met"].format(
            met=meta.get("met", 0), joined=meta.get("joined", 0),
            walked=meta.get("walked_on", 0)))
        return self.continue_event(lines)

    def maid_victim(self) -> Player | None:
        name = self.event["data"].get("victim")
        return self.session.member(name) if name else None

    def maid_flattery(self) -> list[str]:
        ladies = [member for member in self.session.living()
                  if member.gender in MAID_GENDERS]
        lines = [random.choice(FLATTERY.get(
            member.body.get("build", ""), FLATTERY_ANY)).format(
            name=member.name) for member in ladies[:2]]
        if lines:
            lines.insert(0, EVENT_TEXTS["buster_maid"]["eyes"])
        return lines

    def maid_options(self) -> list[str]:
        if self.maid_victim() is not None:
            return ["smack"]
        volunteers = self.maid_free() and any(
            member.gender in MAID_GENDERS
            and member.name not in self.event["used"]
            for member in self.session.living())
        return (["history"] + (["volunteer"] if volunteers else [])
                + ["depart"])

    def maid_action(self, player:Player, command:str,
                    now:float) -> list[Message]:
        texts = EVENT_TEXTS["buster_maid"]
        victim = self.maid_victim()
        if victim is not None:
            if command != "smack" or player.name != victim.name:
                return [Message(texts["busy"].format(name=victim.name),
                                player.name)]
            return self.maid_step(victim, now)
        if command == "history":
            return self.maid_history(player)
        if command == "depart":
            self.session.buster_ledger.bump("walked_on")
            self.save_party()
            return self.finish([texts["depart"]], now)
        if command == "smack":
            return [Message(texts["nobody"], player.name)]
        if player.gender not in MAID_GENDERS:
            return [Message(texts["wrong"].format(name=player.name),
                            player.name)]
        if player.name in self.event["used"]:
            return [Message(texts["again"], player.name)]
        if not self.maid_free():
            return [Message(texts["no_room"], player.name)]
        self.event["used"].add(player.name)
        self.event["data"].update(victim=player.name, step=0)
        lines = [texts["volunteer"].format(name=player.name,
                                           their=their(player))]
        record = self.session.buster_ledger.best_hit(player.name)
        if record:
            lines.append(texts["known"].format(name=player.name,
                                               hit=record))
        return self.continue_event(lines + [texts["ready"]])

    def maid_step(self, player:Player, now:float) -> list[Message]:
        texts = EVENT_TEXTS["buster_maid"]
        session = self.session
        step = self.event["data"]["step"]
        dead_hit = first_hit_death(random)
        first = step * MAID_ROUND_HITS
        first_hit = step * MAID_ROUND_HITS + 1
        lines = [f"Hits {first_hit}-{first_hit + MAID_ROUND_HITS - 1}: "
                 + random.choice(ROUND_TEXTS[step]).format(
                     name=player.name, their=their(player))]
        if step == 4:
            lines.append(BUILD_LINES.get(
                player.body.get("build", "Average"), BUILD_LINES["Average"])
                .format(name=player.name))
        lines += hit_lines(player, step, dead_hit)
        if dead_hit:
            lines.append(f"Hit {first + dead_hit}: ...")
            self.event["data"].pop("victim", None)
            return self.maid_death(player, lines, now, first + dead_hit)
        self.event["data"]["step"] = step + 1
        if step + 1 < MAID_HITS // MAID_ROUND_HITS:
            lines.append(texts["next"].format(
                done=(step + 1) * MAID_ROUND_HITS, total=MAID_HITS))
            return self.continue_event(lines)
        self.event["data"].pop("victim", None)
        apply_buff(player, "red_cheeks")
        lines.append(random.choice(texts["survive"]).format(
            name=player.name))
        lines.append(texts["lasts"].format(
            name=player.name, effect=set_bonus_text(BUFFS["red_cheeks"])))
        session.buster_ledger.add(player, STOOD, MAID_HITS, session.run_id,
                                  joined=not self.maid_taken())
        if not self.maid_taken():
            level = max(member.level for member in session.party)
            companion = make_companion(level)
            session.repository.add(companion)
            session.party.append(companion)
            lines.append(texts["join"].format(count=len(session.party),
                                              max=MAX_PARTY_SIZE))
        session.repository.save(player)
        self.save_party()
        return self.finish(lines, now)

    def maid_death(self, player:Player, lines:list[str],
                   now:float, hit:int=0) -> list[Message]:
        from ...combat import fate_text
        texts = EVENT_TEXTS["buster_maid"]
        session = self.session
        fate = random.choice(FATE_KEYS)
        session.buster_ledger.add(player, fate, hit, session.run_id)
        text = fate_text(player, fate, None)
        lines += session.kill_outside(player, fate, text,
                                      "<<npc.constance_first>>'s paddle", "maid")
        lines.append(random.choice(texts["died_after"]).format(
            name=player.name))
        if not session.living():
            self.reset()
            return [Message("\n".join(lines + session.end_run()))]
        self.save_party()
        if "volunteer" not in self.maid_options():
            session.buster_ledger.bump("walked_on")
            lines.append(random.choice(texts["leaves"]))
            return self.finish(lines, now)
        return self.continue_event(lines)
