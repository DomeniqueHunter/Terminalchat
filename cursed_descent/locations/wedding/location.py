import random
from typing import Any

from ...dungeon import give_item, roll_item, stage_gold
from ...content import SWEAT_TEXTS
from ...models import Message, Player
from ...sweat import condition_line, sweat_tier
from .content import (
    DANCES, DANCE_REACTIONS, DANCE_SMELLS, DANCE_TEARS,
    DANCE_TEARS_OTTILIE, EAT_CHALICE, EAT_REACTIONS, EAT_SMELLS,
    NIGHT_HINTS, NIGHT_MORNING, NIGHTS, VENUE_TEXTS,
)


SWEAT_GAINS = {"eat": 8, "congratulate": 6, "dance": 16, "night": 20}


class WeddingMixin:
    session: Any
    event: dict[str, Any]

    def ottilie(self) -> Player | None:
        npc = next((npc for npc in self.session.repository.npc_players()
                    if npc.npc == "baroness_ottilie"), None)
        if npc is not None:
            npc.sweat = npc.profile.get("sweat", 0)
        return npc

    def save_ottilie(self, ottilie:Player) -> None:
        ottilie.profile["sweat"] = ottilie.sweat
        self.session.repository.save(ottilie)

    def ottilie_sweats(self, step:str) -> list[str]:
        ottilie = self.ottilie()
        if ottilie is None:
            return []
        before = sweat_tier(ottilie)
        ottilie.sweat += SWEAT_GAINS[step]
        self.save_ottilie(ottilie)
        after = sweat_tier(ottilie)
        if after == before:
            return []
        return [SWEAT_TEXTS[after].format(name=ottilie.name)]

    def offer_wedding(self) -> list[str]:
        texts = VENUE_TEXTS["wedding"]
        ottilie = self.ottilie()
        if ottilie is not None:
            ottilie.sweat = 0
            self.save_ottilie(ottilie)
        self.event["data"]["inside"] = False
        return ["", texts["door"], self.options_line(texts)]

    def enter_wedding(self) -> list[Message]:
        self.event["data"]["inside"] = True
        return self.continue_venue([VENUE_TEXTS["wedding"]["intro"]])

    def wedding_options(self) -> list[str]:
        used = self.event["used"]
        options = [option for option in ("eat", "congratulate")
                   if option not in used]
        if self.event["data"].get("night_ready") and "dance" not in used:
            options.append("dance")
        if "dance" in used and "night" not in used:
            options.append("night")
        return options + ["depart"]

    def wedding_examine(self) -> list[Message]:
        texts = VENUE_TEXTS["wedding"]
        if self.outside():
            return [Message(texts["door_examine"])]
        done = self.wedding_progress()
        return [Message("\n".join([texts["examine"], texts["sheath"],
                                   texts[f"boots_{done}"]]))]

    def wedding_night(self, now:float) -> list[Message]:
        session = self.session
        self.event["used"].add("night")
        self.rest_party()
        gold = stage_gold(session.stage) * random.randint(4, 6)
        lines = [random.choice(NIGHTS),
                 NIGHT_MORNING[0].format(gold=gold)]
        for member in session.living():
            member.gold += gold
        lines.append(give_item(session.living()[0],
                               roll_item(session.stage)))
        lines += self.ottilie_sweats("night")
        self.seal_marriage()
        self.save_party()
        return self.finish(lines, now)

    def seal_marriage(self) -> None:
        repository = self.session.repository
        people = {npc.npc: npc for npc in repository.npc_players()
                  if npc.npc in ("baroness_ottilie", "emmerich_grimhold")}
        ottilie = people.get("baroness_ottilie")
        emmerich = people.get("emmerich_grimhold")
        if ottilie is None or emmerich is None:
            return
        ottilie.spouse = emmerich.first_name
        emmerich.spouse = ottilie.first_name
        if not emmerich.pregnant:
            emmerich.pregnant = "party"
            emmerich.profile["pregnant_by"] = ottilie.first_name
            emmerich.profile["pregnant_by_id"] = ottilie.id
        repository.save(ottilie)
        repository.save(emmerich)

    def wedding_progress(self) -> int:
        return len(self.event["used"] & {"eat", "congratulate"})

    def mark_night_ready(self) -> None:
        if self.wedding_progress() == 2:
            self.event["data"]["night_ready"] = True

    def wedding_guest_examine(self, player:Player,
                              name:str) -> list[Message] | None:
        if self.event.get("phase") != "wedding":
            return None
        if name.casefold() == "ottilie":
            ottilie = self.ottilie()
            if ottilie is None:
                return None
            return [Message(f"{ottilie.profile.get('look', '')}\n"
                            f"{VENUE_TEXTS['wedding']['sheath']}\n"
                            f"{condition_line(ottilie)}", player.name)]
        if name.casefold() not in ("emmerich", "emmy"):
            return None
        text = VENUE_TEXTS["wedding"][f"emmerich_{self.wedding_progress()}"]
        if "eat" in self.event["used"]:
            text = f"{text} {NIGHT_HINTS['emmerich_eat']}"
        if "dance" in self.event["used"]:
            text = f"{text} {NIGHT_HINTS['emmerich_dance']}"
        return [Message(text, player.name)]

    def wedding_action(self, player:Player, command:str,
                       now:float) -> list[Message] | None:
        texts = VENUE_TEXTS["wedding"]
        session = self.session
        if command == "eat":
            self.event["used"].add("eat")
            self.mark_night_ready()
            self.heal_party(0.4)
            self.save_party()
            return self.continue_venue([texts["eat"],
                                        random.choice(EAT_CHALICE),
                                        random.choice(EAT_SMELLS),
                                        random.choice(EAT_REACTIONS)]
                                       + self.ottilie_sweats("eat"))
        if command == "dance":
            self.event["used"].add("dance")
            return self.continue_venue([random.choice(DANCES),
                                        random.choice(DANCE_SMELLS),
                                        random.choice(DANCE_TEARS),
                                        DANCE_TEARS_OTTILIE,
                                        random.choice(DANCE_REACTIONS)]
                                       + self.ottilie_sweats("dance"))
        if command == "night":
            return self.wedding_night(now)
        if command != "congratulate":
            return None
        self.event["used"].add("congratulate")
        self.mark_night_ready()
        gold = stage_gold(session.stage) * random.randint(2, 4)
        player.gold += gold
        lines = [texts["congratulate"].format(name=player.name),
                 texts["gift"].format(gold=gold),
                 give_item(player, roll_item(session.stage))]
        lines += self.ottilie_sweats("congratulate")
        session.repository.save(player)
        return self.continue_venue(lines)
