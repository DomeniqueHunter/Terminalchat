import random
from typing import Any

from ..config import (
    CITY_STOP_EVERY, CITY_STOP_FIRST, LOCATION_MARK,
    PAUSED_EVENT_KINDS, PAUSED_IDLE_SECONDS,
    ROUND_TIMEOUT_SECONDS,
)
from ..content import (
    ENEMIES, EVENT_TEXTS, EXAMINE_TEXTS, FARM_SHIFT_TEXTS, VENUE_TEXTS,
)
from ..dungeon import build_enemy, current_biome, grant_exp
from ..settings import fill
from ..examine import garment_report, group_report
from ..formulas import max_hp, max_mana
from ..locations.boutique.location import BoutiqueMixin
from ..locations.common import cycle_stage, unique_names
from ..locations.gigs import GigMixin
from ..locations.places import PLACE_LOOKS
from ..locations.venues import VENUE_KINDS, VenueMixin, location_at
from ..spawns import RULES_BY_KIND, eligible
from ..models import Message, Player
from ..needs_runtime import rest_needs
from .adept.event import ADEPT_OPTIONS, AdeptMixin
from .caravaneer.event import CaravaneerMixin
from .drainer.event import DrainerMixin
from .maid.event import MaidMixin
from .null_master.event import NULL_OPTIONS, NullMasterMixin
from .common import options_text
from .lich.event import LichMixin
from .mrs_claus.event import MrsClausMixin
from .ogre.event import OGRE_DINNER, OgreMixin
from .sweaty.event import SweatyMixin
from .wanderer.event import THIRSTY_OPTIONS, WANDERER_OPTIONS, WandererMixin


EVENT_COMMANDS = {"accept", "decline", "charm", "eat", "talk", "sleep", "sit",
                  "give", "depart", "volunteer", "sellself", "milk",
                  "nurse", "rest", "inspect", "cook", "examine", "rent",
                  "indulge", "enter", "search", "pass", "fresh", "pay", "bribe",
                  "work", "quit", "tap", "answer", "sweat",
                  "smoke", "endure", "beg", "gather", "light", "upgrade",
                  "super", "potion", "real", "realsex", "open", "claim", "take", "offer", "sneak", "thrust",
                  "congratulate", "dance", "night", "cast", "bait", "lie", "special", "ask", "grumble", "stint", "harvest", "tour", "smack", "history", "stall", "wash", "read", "knock", "tip", "urinal", "sacrifice", "challenge",
                  "watch", "deodorize"}
EXAMINE_FATES = {"hut": "lodge", "butcher_shop": "butchered",
                 "farm": "farmed", "sweatery": "heated", "smokery": "smoked",
                 "adept": "adept_statue"}
VENUE_NAMES = {"hut": "one of <<npc.reginald_first>>'s huts",
               "butcher_shop": "<<npc.hamhock_first>>'s butcher shop",
               "farm": "<<npc.old_trotter_short>> Farm",
               "brewery": "<<npc.astrid_first>> <<npc.astrid_last>>'s taproom",
               "couch": "a very comfortable couch",
               "bivouac": "a camp site",
               "citystop": "a town platform",
               "mage_tower": "the Mage's Tower",
               "wardrobe": "a living wardrobe",
               "throne": "the Corruption Throne",
               "glory_hole": "a glory hole",
               "wedding": "a strange wedding",
               "fisher": "<<npc.old_gorm_first>>'s fishing jetty",
               "grill": "<<npc.gul_first>>'s Grill",
               "dairy": "the Crone Creamery",
               "privy": "the Public Privy",
               "pod_garden": "the Pod Garden",
               "north_pole": "the North Pole",
               "sweatery": "the Sweatery",
               "smokery": "the Amazonian Smokery"}
BONUS_ENEMIES = {"hunter": "safari_hunter", "couture": "couturiere",
                 "butcher": "pigman_butcher", "farmer": "pigman_farmer",
                 "recruiter": "school_recruiter"}
FULL_COMMAND_KINDS = ("boutique", "butcher_shop", "farm", "sweatery",
                      "smokery", "mage_tower", "wardrobe", "throne",
                      "glory_hole", "wedding", "fisher", "grill", "dairy", "privy",
                      "pod_garden", "north_pole")


class EventHandler(VenueMixin, BoutiqueMixin, AdeptMixin, NullMasterMixin,
                   OgreMixin, WandererMixin, SweatyMixin, LichMixin, MrsClausMixin,
                   GigMixin, MaidMixin, CaravaneerMixin, DrainerMixin):
    def __init__(self, session:Any) -> None:
        self.session = session
        self.event: dict[str, Any] = {}
        self.once_run = ""
        self.once_seen: set[str] = set()
        self.segment_seen: dict[tuple[str, int], int] = {}

    def reset(self) -> None:
        self.event = {}

    def pick_kind(self, stage:int) -> tuple[str, dict[str, Any] | None]:
        victim = self.ogre_victim()
        self.sync_once()
        rules = [rule for rule in eligible(stage)
                 if rule.kind not in self.once_seen
                 and not self.segment_full(rule, stage)]
        if not rules:
            return "", None
        weights = [rule.weight for rule in rules]
        rule = random.choices(rules, weights=weights)[0]
        if rule.once_per_run:
            self.once_seen.add(rule.kind)
        return rule.kind, victim

    def sync_once(self) -> None:
        if self.once_run != self.session.run_id:
            self.once_run = self.session.run_id
            self.once_seen = set()
            self.segment_seen = {}

    @staticmethod
    def segment_of(stage:int) -> int:
        return (stage - CITY_STOP_FIRST) // CITY_STOP_EVERY

    def segment_full(self, rule:Any, stage:int) -> bool:
        return bool(rule.per_segment) and self.segment_seen.get(
            (rule.kind, self.segment_of(stage)), 0) >= rule.per_segment

    def note_segment(self, kind:str) -> None:
        self.sync_once()
        key = (kind, self.segment_of(self.session.stage))
        self.segment_seen[key] = self.segment_seen.get(key, 0) + 1

    def location_for(self, stage:int) -> str:
        self.sync_once()
        biome = current_biome(stage, self.session.run_id,
                              self.session.lobby_town)["name"]
        kind = location_at(stage, self.once_seen, biome)
        rule = RULES_BY_KIND.get(kind)
        if rule is not None and rule.once_per_run:
            self.once_seen.add(kind)
        return kind

    def paused(self) -> bool:
        return self.event.get("kind") in PAUSED_EVENT_KINDS

    def idle_deadline(self, now:float) -> float:
        if PAUSED_IDLE_SECONDS <= 0:
            return float("inf")
        return now + PAUSED_IDLE_SECONDS

    def offer_location(self, kind:str, now:float) -> list[str]:
        session = self.session
        session.state = "event"
        session.deadline = now + ROUND_TIMEOUT_SECONDS
        self.event = {"kind": kind, "used": set(), "data": {}}
        if self.paused():
            session.deadline = self.idle_deadline(now)
        return self.marked_venue(kind)

    def marked_venue(self, kind:str) -> list[str]:
        lines = self.offer_venue(kind)
        for index, line in enumerate(lines):
            if line.strip():
                lines[index] = f"{LOCATION_MARK} {line.lstrip()}"
                break
        return lines

    def offer(self, now:float) -> list[str]:
        session = self.session
        kind, victim = self.pick_kind(session.stage)
        if not kind:
            return session.begin_stage(now)
        return self.start_kind(kind, victim, now)

    def trigger(self, kind:str, now:float) -> list[str] | None:
        rule = RULES_BY_KIND.get(kind)
        if kind in ("citystop", "mage_tower"):
            return self.offer_location(kind, now)
        if rule is None:
            return None
        if rule.slot == "location":
            return self.offer_location(kind, now)
        return self.start_kind(kind, self.ogre_victim(), now, force=True)

    def start_kind(self, kind:str, victim:dict[str, Any] | None,
                   now:float, force:bool=False) -> list[str]:
        session = self.session
        if kind == "lich":
            return self.offer_lich(now)
        if kind == "mrs_claus":
            return self.offer_mrs_claus(now)
        if kind in BONUS_ENEMIES:
            template_id = BONUS_ENEMIES[kind]
            enemy = build_enemy(1, template_id, ENEMIES[template_id],
                                session.stage)
            intro = ["", EVENT_TEXTS[kind]["intro"]]
            if kind == "couture":
                intro += self.velours_growth(enemy)
            return session.start_bonus_fight(kind, [enemy], intro, now)
        session.state = "event"
        session.deadline = now + ROUND_TIMEOUT_SECONDS
        self.event = {"kind": kind, "used": set(), "data": {}}
        if self.paused():
            session.deadline = self.idle_deadline(now)
        if kind in VENUE_KINDS:
            return self.marked_venue(kind)
        if kind == "ogre_feast":
            return self.offer_ogre(victim)
        if kind == "boutique":
            return self.offer_boutique()
        if kind == "adept":
            return self.offer_adept()
        if kind == "buster_maid":
            if self.maid_taken() and not force:
                return session.begin_stage(now)
            return self.offer_maid()
        if kind == "null_master":
            return self.offer_null()
        if kind == "caravaneer":
            if not self.caravan_candidates() and not force:
                return session.begin_stage(now)
            self.note_segment(kind)
            return self.offer_caravan()
        if kind == "drainer":
            return self.offer_drainer()
        return self.offer_wanderer()

    def available(self) -> list[str]:
        options = self.base_options()
        if self.examinable() and options and "examine" not in options:
            options.insert(len(options) - 1, "examine")
        gigs = self.gig_options()
        if gigs and options:
            options[-1:-1] = gigs
        return options

    def examinable(self) -> bool:
        phase = self.event.get("phase", "")
        return phase in EXAMINE_FATES or phase in (
            "boutique", "couch", "bivouac", "mage_tower", "wardrobe",
            "throne", "glory_hole", "wedding", "fisher", "grill", "dairy",
            "privy", "pod_garden", "north_pole", "maid", "caravan",
            "drainer")

    def guest_examine(self, player:Player,
                      name:str) -> list[Message] | None:
        return self.wedding_guest_examine(player, name)

    def examine(self, player:Player) -> list[Message]:
        phase = self.event["phase"]
        session = self.session
        session.deadline += ROUND_TIMEOUT_SECONDS / 4
        if phase == "wardrobe":
            return self.wardrobe_examine()
        if phase == "throne":
            return self.throne_examine()
        if phase == "glory_hole":
            return self.glory_hole_examine()
        if phase == "wedding":
            return self.wedding_examine()
        if phase == "fisher":
            return self.fisher_examine()
        if phase == "grill":
            return self.grill_examine()
        if phase == "dairy":
            return self.dairy_examine()
        if phase == "privy":
            return self.privy_examine()
        if phase == "pod_garden":
            return self.pod_garden_examine()
        if phase == "north_pole":
            return self.north_pole_examine()
        if phase == "maid":
            return self.maid_examine()
        if phase == "caravan":
            return self.caravan_examine()
        if phase == "drainer":
            return self.drainer_examine()
        if phase in ("couch", "bivouac", "mage_tower"):
            return [Message(VENUE_TEXTS[phase]["examine"])]
        place = self.place_lines(phase)
        if phase == "boutique" and not self.outside():
            stock = [item_id for _, item_id, _ in self.boutique_groups()]
            lines = place + garment_report(stock, session.boutique)
        elif phase == "boutique":
            lines = place
        else:
            fate = EXAMINE_FATES[phase]
            if phase == "adept":
                current = cycle_stage(session.stage)
                entries = [entry for entry in self.venue_entries(fate)
                           if cycle_stage(entry["stage"]) == current]
            else:
                entries = self.located(fate)
            if phase == "farm":
                entries = unique_names(entries)
            key = "statues" if phase == "adept" else "venue"
            report = group_report(EXAMINE_TEXTS[key], entries,
                                  session.repository)
            lines = place + ([] if place and not entries else report)
        return [Message("\n".join(lines))]

    def place_lines(self, phase:str) -> list[str]:
        look = (self.sweatery_look() if phase == "sweatery"
                else self.smokery_look() if phase == "smokery"
                else PLACE_LOOKS.get(phase))
        if look is None:
            return []
        inside = bool(self.event["data"].get("inside")) or not self.outside()
        lines = [look["inside" if inside else "outside"]]
        owner = self.session.repository.load(look["owner"]) if look[
            "owner"] else None
        if owner is not None and owner.profile.get("look"):
            lines.append(f"{owner.full_name}: {owner.profile['look']}")
        return lines

    def base_options(self) -> list[str]:
        if not self.event:
            return []
        phase = self.event["phase"]
        if self.outside():
            return ["enter", "pass"]
        if phase == "invite":
            return ["accept", "decline"]
        if phase == "adept":
            return list(ADEPT_OPTIONS)
        if phase == "maid":
            return self.maid_options()
        if phase == "caravan":
            return self.caravan_options()
        if phase == "drainer":
            return self.drainer_options()
        if phase == "null":
            return list(NULL_OPTIONS)
        if phase in VENUE_KINDS:
            return self.venue_options()
        if phase == "boutique":
            return [f"buy {nr}" for nr, _, _ in self.boutique_groups()
                    ] + ["sellself", "depart"]
        if "offer" in self.event["data"]:
            return ["accept", "decline"]
        base = OGRE_DINNER if phase == "dinner" else WANDERER_OPTIONS
        if phase == "camp" and self.event["data"].get("thirsty"):
            base = THIRSTY_OPTIONS + tuple(base)
        if phase == "camp" and self.event["data"].get("sweaty"):
            base = ("indulge",) + tuple(base)
        if phase == "camp" and self.party_has_raw_meat():
            base = tuple(base) + ("cook",)
        return [option for option in base
                if option not in self.event["used"]]

    def status(self) -> str:
        kind = self.event.get("kind", "")
        who = ("an ogre's dinner invitation" if kind == "ogre_feast"
               else fill("<<boutique.owner>>'s boutique") if kind == "boutique"
               else "a young mage adept" if kind == "adept"
               else "a wandering maid with a paddle"
               if kind == "buster_maid"
               else "the Null Master" if kind == "null_master"
               else "a caravaneer with a pony wagon"
               if kind == "caravaneer"
               else "the Drainer" if kind == "drainer"
               else VENUE_NAMES.get(kind, "")
               if kind in VENUE_KINDS
               else self.event.get("data", {}).get("wanderer", "someone"))
        return (f"Before stage {self.session.stage}: {who} – "
                f"{options_text(self.available())}")

    def action(self, name:str, command:str, now:float,
               args:list[str] | None=None) -> list[Message]:
        command = " ".join([command] + (args or [])).lower()
        session = self.session
        player = session.member(name)
        if session.state != "event" or player is None:
            return [Message("Nobody here wants anything from you.", name)]
        if not player.alive:
            return [Message("The dead don't get invitations.", name)]
        if self.paused():
            session.deadline = self.idle_deadline(now)
        gig = self.gig_action(player, command, now)
        if gig is not None:
            return gig
        if self.event["kind"] == "brewery":
            parts = command.split()
            return self.brewery_action(player, parts[0], parts[1:], now)
        if self.event["kind"] == "sweatery" and not self.outside():
            handled = self.sweatery_action(player, command, now)
            if handled is not None:
                return handled
        if self.event["kind"] == "smokery" and not self.outside():
            handled = self.smokery_action(player, command, now)
            if handled is not None:
                return handled
        if self.event["kind"] == "mage_tower":
            handled = self.mage_tower_action(player, command, now)
            if handled is not None:
                return handled
        options = self.available()
        base = command.split()[0]
        if base == "examine" and self.examinable():
            return self.examine(player)
        if self.event["kind"] == "farm" and command.startswith("rent "):
            command = "work " + command.split(" ", 1)[1]
        if self.event["kind"] not in FULL_COMMAND_KINDS:
            command, args = base, (args or [])
        if self.event["kind"] in FULL_COMMAND_KINDS:
            exact = {option.casefold(): option for option in options}
            command = exact.get(command.casefold(), command)
        if command == "depart" and self.outside():
            command = "pass"
        if command in self.event["used"]:
            return [Message(EVENT_TEXTS["used"], name)]
        if command in ("work", "quit") and command not in options and any(
                option.startswith("work ") for option in options):
            return [Message(FARM_SHIFT_TEXTS["idle"].format(name=name),
                            name)]
        if command not in options:
            return [Message(EVENT_TEXTS["invalid"].format(
                options=options_text(options)), name)]
        if command == "enter" and self.outside():
            return self.enter_place()
        if command == "pass":
            command = "depart"
        if self.event["kind"] == "ogre_feast":
            return self.ogre_action(player, command, now)
        if self.event["kind"] == "boutique":
            return self.boutique_action(player, command, now)
        if self.event["kind"] == "adept":
            return self.adept_action(player, command, now)
        if self.event["kind"] == "buster_maid":
            return self.maid_action(player, command, now)
        if self.event["kind"] == "null_master":
            return self.null_action(player, command, args or [], now)
        if self.event["kind"] == "caravaneer":
            return self.caravan_action(player, command, args or [], now)
        if self.event["kind"] == "drainer":
            return self.drainer_action(player, command, args or [], now)
        if self.event["kind"] in VENUE_KINDS:
            return self.venue_action(player, command, now)
        if command == "cook":
            return self.cook_action(player)
        if command == "give" and args:
            return self.give_item(player, " ".join(args))
        if command in ("accept", "decline"):
            return self.thanks_action(player, command)
        if command in THIRSTY_OPTIONS:
            return self.thirst_action(player, command)
        if command == "indulge":
            return self.indulge_action(player)
        return self.wanderer_action(player, command, now)

    def expire(self, now:float) -> list[Message]:
        if self.event.get("kind") == "caravaneer" and self.session.living():
            return self.caravan_expire(now)
        if self.event.get("kind") == "drainer" and self.session.living():
            return self.drainer_expire(now)
        lines = (self.finish_shifts() + self.finish_sweat_shifts()
                 + self.finish_smoke_boxes() if self.event else [])
        if not self.session.living():
            self.reset()
            return [Message("\n".join(lines + self.session.end_run()))]
        self.save_party()
        return self.finish(lines + [EVENT_TEXTS["timeout"]], now)

    def finish(self, lines:list[str], now:float) -> list[Message]:
        city = self.event.get("kind") == "citystop"
        self.reset()
        if city:
            return [Message("\n".join(lines + self.session.next_stage(now)))]
        return [Message("\n".join(lines + self.session.begin_stage(now)))]

    def heal_party(self, ratio:float) -> None:
        for member in self.session.living():
            member.hp = min(max_hp(member),
                            member.hp + round(max_hp(member) * ratio))

    def rest_party(self) -> None:
        for member in self.session.living():
            member.hp = max_hp(member)
            member.mana = max_mana(member)
            member.sweat = 0
            rest_needs(member)

    def grant_party_exp(self, amount:int) -> list[str]:
        lines: list[str] = []
        for member in self.session.living():
            lines += grant_exp(member, amount)
        return lines

    def save_party(self) -> None:
        for member in self.session.party:
            self.session.repository.save(member)

    def continue_event(self, lines:list[str]) -> list[Message]:
        self.session.deadline += ROUND_TIMEOUT_SECONDS / 2
        texts = EVENT_TEXTS[self.event["kind"]]
        key = "dinner" if self.event["kind"] == "ogre_feast" else "options"
        lines.append(self.strip_timer(texts[key]).format(
            options=options_text(self.available()),
            seconds=int(ROUND_TIMEOUT_SECONDS)))
        return [Message("\n".join(lines))]
