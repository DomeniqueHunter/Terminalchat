import random
from typing import Any

from ..settings import fill
from ..config import (
    CITY_STOP_EVERY, CITY_STOP_FIRST, FARM_STOCK, LOCATION_EVERY,
    PAUSED_EVENT_KINDS, ROUND_TIMEOUT_SECONDS,
)
from ..content import ITEMS, LOCATION_NOTES, VENUE_TEXTS
from ..dungeon import give_item, is_boss_stage
from ..models import Message, Player
from .bivouac.location import BivouacMixin
from .mage_tower.location import MageTowerMixin
from .glory_hole.location import GloryHoleMixin
from .throne.location import ThroneMixin
from .wedding.location import WeddingMixin
from .wardrobe.location import WardrobeMixin
from .citystop.location import CityStopMixin
from .brewery.location import BreweryMixin
from .butcher.content import BUTCHER_CUTS
from .butcher.location import ButcherMixin, meat_piece_ids, register_meat
from .butcher.npc import butcher_comment
from ..spawns import eligible
from .common import cycle_stage, pronouns
from .couch.location import CouchMixin
from .farm.location import FarmMixin, farm_job
from .fisher.location import FisherMixin
from .grill.location import GrillMixin
from .privy.location import PrivyMixin
from .pod_garden.location import PodGardenMixin, pod_variant
from .north_pole.location import NorthPoleMixin
from .dairy.location import DairyMixin
from .lodge.content import HUNTER_HUTS
from .lodge.location import LodgeMixin, lodge_detail
from .shop.location import base_price, buy_price, item_summary
from .smokery.location import SmokeryMixin
from .sweatery.location import SweateryMixin


VENUE_KINDS = ("hut", "butcher_shop", "farm", "brewery", "couch",
               "sweatery", "smokery", "bivouac", "citystop",
               "mage_tower", "wardrobe", "throne", "glory_hole", "wedding", "fisher", "grill", "dairy", "privy", "pod_garden", "north_pole")
ENTRY_PHASES = ("hut", "butcher_shop", "farm", "boutique", "sweatery",
                "smokery", "mage_tower", "fisher", "dairy", "privy",
                "wedding")
LOCATION_FATES = ("lodge", "farmed", "butchered", "brewed",
                  "heated", "smoked")


def city_stop_at(stage:int) -> bool:
    return (stage >= CITY_STOP_FIRST
            and (stage - CITY_STOP_FIRST) % CITY_STOP_EVERY == 0)


def location_at(stage:int, skip:set[str] | frozenset[str]=frozenset(),
                biome:str="") -> str:
    current = cycle_stage(stage)
    if current % LOCATION_EVERY or is_boss_stage(stage):
        return ""
    rules = [rule for rule in eligible(current, "location")
             if rule.kind not in skip and rule.biome in ("", biome)]
    if not rules:
        return ""
    weights = [rule.weight for rule in rules]
    return random.choices(rules, weights=weights)[0].kind


def fate_location(fate:str, detail:str, stage:int) -> int:
    return cycle_stage(stage) if fate in LOCATION_FATES else 0


def location_note(player:Player, detail:str, location:int) -> list[str]:
    if not location or player.last_fate not in LOCATION_NOTES:
        return []
    _, them, _ = pronouns(player.gender)
    hut = HUNTER_HUTS.get(detail.split("|")[0], {}).get("name", "a lodge")
    return [LOCATION_NOTES[player.last_fate].format(
        name=player.name, them=them, stage=location, hut=hut)]


def fate_detail(player:Player, stage:int) -> str:
    fate = player.last_fate
    if fate == "lodge":
        return lodge_detail(player.last_fate_text, stage)
    if fate == "farmed":
        return farm_job(player)
    if fate == "butchered":
        return random.choice(list(BUTCHER_CUTS))
    if fate == "podded":
        return pod_variant(player.last_fate_text)
    if fate == "flattened":
        text = player.last_fate_text.casefold()
        return "hammer" if "sticks to the hammer" in text else "floor"
    return ""


class VenueMixin(LodgeMixin, ButcherMixin, FarmMixin,
                 BreweryMixin, CouchMixin, SweateryMixin,
                 SmokeryMixin, BivouacMixin, CityStopMixin, MageTowerMixin,
                 WardrobeMixin, ThroneMixin, GloryHoleMixin, WeddingMixin,
                 FisherMixin, GrillMixin, DairyMixin, PrivyMixin,
                 PodGardenMixin, NorthPoleMixin):
    session: Any
    event: dict[str, Any]

    def venue_entries(self, fate:str) -> list[dict[str, Any]]:
        return [entry for entry in self.session.remains.entries
                if entry["fate"] == fate
                and entry["run"] != self.session.run_id]

    def located(self, fate:str) -> list[dict[str, Any]]:
        current = cycle_stage(self.session.stage)
        return [entry for entry in self.venue_entries(fate)
                if entry.get("location") == current]

    def strip_timer(self, template:str) -> str:
        if self.event.get("kind") in PAUSED_EVENT_KINDS:
            return template.replace(" ({seconds} s)", " – no time limit")
        return template

    def options_line(self, texts:dict[str, str]) -> str:
        shown: list[str] = []
        for option in self.available():
            label = option
            if option.startswith("buy "):
                label = "buy <nr>"
            elif option.startswith("harvest "):
                label = "harvest <nr>"
            if label not in shown:
                shown.append(label)
        options = " | ".join(f"[{option}]" for option in shown)
        return self.strip_timer(texts["options"]).format(
            options=options, seconds=int(ROUND_TIMEOUT_SECONDS))

    def own_lines(self, entries:list[dict[str, Any]],
                  text:str) -> list[str]:
        lines: list[str] = []
        names = {entry["name"] for entry in entries}
        for player in self.session.party:
            if player.name in names:
                their = pronouns(player.gender)[2]
                lines.append(text.format(name=player.name, their=their))
        return lines

    def offer_venue(self, kind:str) -> list[str]:
        self.event["phase"] = kind
        if kind == "hut":
            return self.offer_hut()
        if kind == "butcher_shop":
            return self.offer_butcher()
        if kind == "farm":
            return self.offer_farm()
        if kind == "brewery":
            return self.offer_brewery()
        if kind == "sweatery":
            return self.offer_sweatery()
        if kind == "smokery":
            return self.offer_smokery()
        if kind == "bivouac":
            return self.offer_bivouac()
        if kind == "citystop":
            return self.offer_citystop()
        if kind == "mage_tower":
            return self.offer_mage_tower()
        if kind == "wardrobe":
            return self.offer_wardrobe()
        if kind == "throne":
            return self.offer_throne()
        if kind == "glory_hole":
            return self.offer_glory_hole()
        if kind == "wedding":
            return self.offer_wedding()
        if kind == "fisher":
            return self.offer_fisher()
        if kind == "grill":
            return self.offer_grill()
        if kind == "dairy":
            return self.offer_dairy()
        if kind == "privy":
            return self.offer_privy()
        if kind == "pod_garden":
            return self.offer_pod_garden()
        if kind == "north_pole":
            return self.offer_north_pole()
        return self.offer_couch()

    def venue_stock(self) -> list[tuple[int, str, int]]:
        phase = self.event.get("phase")
        if phase == "butcher_shop":
            stock = self.butcher_stock()
        elif phase == "brewery":
            return self.brewery_stock()
        elif phase == "sweatery":
            stock = self.sweatery_stock()
        elif phase == "smokery":
            stock = self.smokery_stock()
        elif phase == "grill":
            stock = self.grill_stock()
        elif phase == "dairy":
            stock = self.dairy_stock()
        elif phase == "farm":
            stock = list(FARM_STOCK) + [
                item_id for item_id in self.farm_products()
                if item_id not in self.event["used"]]
        else:
            return []
        return [(nr, item_id, base_price(item_id))
                for nr, item_id in enumerate(stock, 1)]

    def venue_stock_lines(self) -> list[str]:
        texts = VENUE_TEXTS[self.event["phase"]]
        stock = self.venue_stock()
        if not stock and "empty" in texts:
            return [texts["empty"]]
        return [texts["stock"].format(nr=nr, item=item_summary(item_id),
                                      price=price)
                for nr, item_id, price in stock]

    def outside(self) -> bool:
        phase = self.event.get("phase")
        if phase not in ENTRY_PHASES or self.event["data"].get("inside"):
            return False
        return phase != "farm" or not self.shifts()

    def enter_place(self) -> list[Message]:
        phase = self.event["phase"]
        if phase == "hut":
            return self.enter_hut()
        if phase == "butcher_shop":
            return self.enter_butcher()
        if phase == "farm":
            return self.enter_farm()
        if phase == "boutique":
            return self.enter_boutique()
        if phase == "couch":
            return self.enter_couch()
        if phase == "sweatery":
            return self.enter_sweatery()
        if phase == "smokery":
            return self.enter_smokery()
        if phase == "mage_tower":
            return self.enter_mage_tower()
        if phase == "fisher":
            return self.enter_fisher()
        if phase == "dairy":
            return self.enter_dairy()
        if phase == "privy":
            return self.enter_privy()
        if phase == "wedding":
            return self.enter_wedding()
        if phase == "wardrobe":
            return self.enter_wardrobe()
        if phase == "throne":
            return self.enter_throne()
        return self.enter_adept()

    def venue_options(self) -> list[str]:
        phase = self.event["phase"]
        if phase == "brewery":
            return self.brewery_options()
        if phase == "sweatery":
            return self.sweatery_options()
        if phase == "smokery":
            return self.smokery_options()
        if phase == "bivouac":
            return self.bivouac_options()
        if phase == "citystop":
            return self.citystop_options()
        if phase == "mage_tower":
            return self.mage_tower_options()
        if phase == "wardrobe":
            return ["open", "depart"]
        if phase == "throne":
            return self.throne_options()
        if phase == "glory_hole":
            return self.glory_hole_options()
        if phase == "wedding":
            return self.wedding_options()
        if phase == "fisher":
            return self.fisher_options()
        if phase == "grill":
            return self.grill_options()
        if phase == "dairy":
            return self.dairy_options()
        if phase == "privy":
            return self.privy_options()
        if phase == "pod_garden":
            return self.pod_garden_options()
        if phase == "north_pole":
            return self.north_pole_options()
        if phase == "hut":
            cook = ["cook"] if self.party_has_raw_meat() else []
            return [option for option in ("rest", "sleep", "search", "eat",
                                          *cook, "depart")
                    if option not in self.event["used"]]
        if phase == "couch":
            return [option for option in ("rest", "inspect", "depart")
                    if option not in self.event["used"]]
        if phase == "farm" and self.shifts():
            return self.rent_options() + self.shift_options()
        buys = [f"buy {nr}" for nr, _, _ in self.venue_stock()]
        rents = self.rent_options() if phase == "farm" else []
        return buys + rents + ["sellself", "depart"]

    def venue_action(self, player:Player, command:str,
                     now:float) -> list[Message]:
        phase = self.event["phase"]
        texts = VENUE_TEXTS[phase]
        if phase == "sweatery":
            handled = self.sweatery_action(player, command, now)
            if handled is not None:
                return handled
        if phase == "smokery":
            handled = self.smokery_action(player, command, now)
            if handled is not None:
                return handled
        if phase == "bivouac" and command != "depart":
            return self.bivouac_action(player, command, now)
        if phase == "citystop" and command != "depart":
            return self.citystop_action(player, command, now)
        if phase == "farm" and command in ("work", "quit"):
            return self.shift_action(player, command, now)
        if phase == "farm" and command.startswith("work "):
            return self.continue_venue(self.rent(player, command.split()[1]))
        if command == "depart":
            self.save_party()
            return self.finish([texts["depart"]], now)
        if phase == "hut" and command == "enter":
            return self.enter_hut()
        if phase == "butcher_shop" and command == "enter":
            return self.enter_butcher()
        if phase == "farm" and command == "enter":
            return self.enter_farm()
        if phase == "hut" and command == "search":
            return self.hut_search(player, now)
        if phase == "hut" and command == "eat":
            return self.hut_eat(player, now)
        if phase == "hut" and command == "cook":
            return self.hut_cook(player, now)
        if phase == "hut":
            return self.hut_rest(player, command, now)
        if phase == "couch":
            return self.couch_action(player, command, now)
        if phase == "wardrobe":
            return self.wardrobe_action(player, command, now)
        if phase == "throne":
            handled = self.throne_action(player, command, now)
            if handled is not None:
                return handled
        if phase == "glory_hole":
            handled = self.glory_hole_action(player, command, now)
            if handled is not None:
                return handled
        if phase == "fisher":
            handled = self.fisher_action(player, command, now)
            if handled is not None:
                return handled
        if phase == "grill":
            handled = self.grill_action(player, command, now)
            if handled is not None:
                return handled
        if phase == "dairy":
            handled = self.dairy_action(player, command, now)
            if handled is not None:
                return handled
        if phase == "privy":
            handled = self.privy_action(player, command, now)
            if handled is not None:
                return handled
        if phase == "pod_garden":
            handled = self.pod_garden_action(player, command, now)
            if handled is not None:
                return handled
        if phase == "north_pole":
            handled = self.north_pole_action(player, command, now)
            if handled is not None:
                return handled
        if phase == "wedding":
            handled = self.wedding_action(player, command, now)
            if handled is not None:
                return handled
        if command == "sellself":
            return self.venue_sell_self(player, now)
        return self.venue_buy(player, int(command.split()[1]))

    def venue_buy(self, player:Player, nr:int) -> list[Message]:
        texts = VENUE_TEXTS[self.event["phase"]]
        stock = {number: item_id for number, item_id, _ in self.venue_stock()}
        item_id = stock[nr]
        price = buy_price(item_id, player)
        values = {"name": player.name, "item": ITEMS[item_id]["name"],
                  "price": price, "gold": player.gold}
        if player.gold < price:
            return [Message(texts["poor"].format(**values), player.name)]
        if len(player.inventory) >= player.bag_size:
            return [Message(texts["full"].format(**values), player.name)]
        player.gold -= price
        lines = [texts["buy"].format(**values), give_item(player, item_id)]
        if item_id.startswith("dairy_p_"):
            self.event["used"].add(item_id)
        if item_id.startswith("farm_"):
            self.event["used"].add(item_id)
            if item_id.startswith("farm_shift_"):
                self.session.farm_ledger.take(item_id)
        if self.event["phase"] == "sweatery":
            self.sweatery_bought(item_id)
        if self.event["phase"] == "smokery":
            self.smokery_bought(item_id)
        if self.event["phase"] == "butcher_shop":
            self.event["used"].add(item_id)
            for entry in self.session.remains.entries:
                if (entry["fate"] == "butchered"
                        and item_id in meat_piece_ids(entry)):
                    entry.setdefault("meat_sold_ids", []).append(item_id)
            self.session.remains.save()
        self.session.repository.save(player)
        return self.continue_venue(lines)

    def venue_sell_self(self, player:Player, now:float) -> list[Message]:
        from ..combat import fate_text
        from ..events.common import self_price
        session = self.session
        phase = self.event["phase"]
        texts = VENUE_TEXTS[phase]
        fate = "butchered" if phase == "butcher_shop" else "farmed"
        known = fate == "farmed" and any(
            player.owns(entry) for entry in self.located("farmed"))
        gold = self_price(player)
        player.gold += gold
        their = pronouns(player.gender)[2]
        lines = [texts["sellself"].format(name=player.name, gold=gold,
                                          their=their)]
        if known:
            lines.append(texts["known"].format(name=player.name))
        text = fate_text(player, fate, None)
        player.last_fate = fate
        player.last_fate_text = text
        detail = fate_detail(player, session.stage)
        killer = fill("<<npc.hamhock_first>>" if fate == "butchered"
                      else "<<npc.old_trotter_first>>")
        lines += session.kill_outside(player, fate, text, killer, "pigmen",
                                      detail)
        if fate == "butchered":
            entry = session.remains.entries[-1]
            register_meat(entry)
            lines += butcher_comment(entry)
            lines += [texts["fresh"].format(item=item_summary(piece),
                                            price=base_price(piece))
                      for piece in meat_piece_ids(entry)]
        if not session.living():
            self.reset()
            return [Message("\n".join(lines + session.end_run()))]
        return self.continue_venue(lines)

    def continue_venue(self, lines:list[str]) -> list[Message]:
        self.session.deadline += ROUND_TIMEOUT_SECONDS / 2
        texts = VENUE_TEXTS[self.event["phase"]]
        busy = (self.shifts() or self.sweat_shifts()
                or self.event.get("phase") in ("sweatery", "smokery"))
        if "stock" in texts and not busy:
            lines += self.venue_stock_lines()
        return [Message("\n".join(lines + [self.options_line(texts)]))]
