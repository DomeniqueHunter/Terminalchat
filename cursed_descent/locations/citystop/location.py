import random
from types import SimpleNamespace
from typing import Any

from ...config import (
    HUNG_GENDERS, MILK_BUSTS, PASS_SNEAK_CHANCE, STAKES_SHOWN,
    VAGINA_GENDERS,
)
from ...intimacy import conception
from ...models import Message, Player
from ...remains import unique_names
from ...town_buildings.station.rail_pass import (
    grant_pass, has_pass, keeper_name, try_pass,
)
from ...towns import START_TOWN, TOWNS, mark_visited
from .content import ACTS, STATION_ID, VENUE_TEXTS


NEW_TOWN_WEIGHT = 3


def pick_town(members:list[Player], rng:random.Random | None=None) -> str:
    rng = rng or random
    keys = [key for key in TOWNS if key != START_TOWN]
    weights = [NEW_TOWN_WEIGHT if any(not has_pass(member, key)
                                      for member in members) else 1
               for key in keys]
    return rng.choices(keys, weights=weights)[0]


def eligible_acts(player:Player) -> list[str]:
    acts = ["anal", "oral"]
    if player.gender in VAGINA_GENDERS:
        acts.append("vaginal")
    if player.body.get("breasts") in MILK_BUSTS:
        acts.append("milk_bust")
    if player.gender in HUNG_GENDERS:
        acts.append("milk_cock")
    return acts


class CityStopMixin:
    session: Any
    event: dict[str, Any]

    def offer_citystop(self) -> list[str]:
        texts = VENUE_TEXTS["citystop"]
        key = pick_town(self.session.living())
        self.event["data"]["town"] = key
        self.event["data"]["tried"] = {}
        for member in self.session.living():
            mark_visited(member, key)
            self.session.repository.save(member)
        town = TOWNS[key]
        intro = texts["intro"].format(town=town.name, race=town.race,
                                      keeper=keeper_name(key))
        return ["", intro, *self.stake_lines(key), self.options_line(texts)]

    def stake_lines(self, key:str) -> list[str]:
        entries = unique_names([
            entry for entry in self.session.remains.entries
            if entry["fate"] == "staked" and entry.get("detail") == key])
        if not entries:
            return []
        names = [entry["name"] for entry in entries[-STAKES_SHOWN:]]
        if len(entries) > STAKES_SHOWN:
            names.append(f"and {len(entries) - STAKES_SHOWN} more")
        return [VENUE_TEXTS["citystop"]["stakes"].format(
            names=", ".join(names), keeper=keeper_name(key))]

    def citystop_ready(self) -> bool:
        key = self.event["data"]["town"]
        living = [member for member in self.session.living()
                  if not member.npc]
        return bool(living) and all(has_pass(member, key)
                                    for member in living)

    def citystop_options(self) -> list[str]:
        options = ["talk", "pay", "bribe", "sneak", "offer"]
        if self.citystop_ready():
            options.append("enter")
        return options + ["depart"]

    def citystop_action(self, player:Player, command:str,
                        now:float) -> list[Message]:
        data = self.event["data"]
        texts = VENUE_TEXTS["citystop"]
        key = data["town"]
        tried = data["tried"].setdefault(player.name, [])
        if command == "enter":
            for member in self.session.living():
                if member.npc:
                    grant_pass(member, key)
                    self.session.repository.save(member)
            return [Message("\n".join(self.session.pause_run(key)))]
        if command == "offer":
            return self.citystop_offer(player)
        if command == "sneak":
            return self.citystop_sneak(player, tried)
        if command in ("talk", "bribe") and command in tried:
            return [Message(texts["tried"].format(name=player.name),
                            player.name)]
        tried.append(command)
        done, text = try_pass(player, key, command)
        self.session.repository.save(player)
        if has_pass(player, key) or command in ("talk", "bribe"):
            return self.continue_venue([text])
        return [Message(text, player.name)]

    def citystop_values(self, player:Player) -> dict[str, Any]:
        key = self.event["data"]["town"]
        return {"name": player.name, "keeper": keeper_name(key),
                "town": TOWNS[key].name}

    def citystop_offer(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["citystop"]
        key = self.event["data"]["town"]
        values = self.citystop_values(player)
        act = random.choice(eligible_acts(player))
        lines = [random.choice(ACTS[act]).format(**values)]
        if act in ("anal", "vaginal"):
            giver = SimpleNamespace(gender="Male", name=values["keeper"],
                                    id=f"{STATION_ID}{key}")
            lines += conception(giver, player, random, 1.0)
        fresh = not has_pass(player, key)
        grant_pass(player, key)
        lines.append(texts["end_new" if fresh else "end_have"].format(
            **values))
        self.session.repository.save(player)
        return self.continue_venue(lines)

    def citystop_sneak(self, player:Player,
                       tried:list[str]) -> list[Message]:
        texts = VENUE_TEXTS["citystop"]
        key = self.event["data"]["town"]
        if has_pass(player, key) or "sneak" in tried:
            note = ("tried" if "sneak" in tried else "end_have")
            return [Message(texts[note].format(
                **self.citystop_values(player)), player.name)]
        tried.append("sneak")
        values = self.citystop_values(player)
        session = self.session
        if random.random() < PASS_SNEAK_CHANCE:
            grant_pass(player, key)
            session.repository.save(player)
            return self.continue_venue(
                [random.choice(texts["sneak_ok"]).format(**values)])
        from ...combat import fate_text
        text = fate_text(player, "staked", None)
        lines = session.kill_outside(player, "staked", text,
                                     values["keeper"], "stationmasters",
                                     detail=key)
        if not session.living():
            self.reset()
            return [Message("\n".join(lines + session.end_run()))]
        self.save_party()
        return self.continue_venue(lines)
