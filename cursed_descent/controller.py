import random
import re
import time
from dataclasses import replace
from pathlib import Path

from .births import child_label
from .body_creation import parse_body_input
from .towns.last_light_humans.cafe.stool_trade import stool_command
from .commands import Command, parse_chat
from . import routines, seasons
from .config import (
    WORLD_DAY_SECONDS,
    LOBBY_OFFLINE_SECONDS, MAX_LOBBIES, MAX_PARTY_SIZE,
    AFFINITY_LABELS, COMMAND_PREFIX, EQUIPMENT_SLOTS, GAME_DATA_PATH,
    GENDERS, MAX_AGE, MIN_AGE, OFFSPRING_HP,
    PERSONALITY_MAX, SHOW_ACTION_HINTS, SLOT_LABELS, STAT_ALIASES,
    STAT_NAMES, STAT_SHORT,
)
from .body import (
    apply_body_mods, body_text, effects_text,
)
from .content import (
    CLINIC_TEXTS, ENEMIES, FATE_LABELS, ITEMS, OFFSPRING_TEXTS, SHOPKEEPER,
    SMITH_TEXTS, SPELLS,
)
from .debug_goddess import make_goddess
from .creation import CharacterCreator, find_gender
from .formulas import (
    allure, can_wear, effective_stat, exp_needed, knows_spell, max_hp,
    max_mana, set_lines, buff_lines, stat_total_text, totals_line,
    wear_refusal,
)
from .help import help_text
from .items import remove_item
from .smell import smell_note
from .item_report import item_report
from .models import Message, Player
from .races import race_of
from .lobbies import Bundle, Lobbies
from .ready_check import ReadyCheck
from .towns import TOWNS, mark_visited, town_key
from .towns.localize import localize
from . import home_scene
from .group_sleep import GroupSleep
from .houses import (
    CHEST_WORDS, chest_command, chest_of, home_command, home_of,
    shared_host)
from .intimacy import intimacy_command
from .npc_menu import npc_command
from .party_talk import party_chat
from .sweat import condition_line
from .debug_items import give_item, item_list
from .events.handler import EVENT_COMMANDS
from .events.drainer.content import EVENT_TEXTS as DRAINER_TEXTS
from .events.drainer.ledger import Ledger as DrainerLedger
from .events.drainer.ledger import can_receive, thing_text
from .events.drainer.ledger import restore as restore_part
from .locations.boutique.location import Boutique
from .locations.farm.location import FarmLedger, register_all_products
from .locations.dairy.location import register_all_dairy
from .events.maid.ledger import BusterLedger
from .locations.sweatery.location import (
    SweateryLedger, register_all as register_all_sweat,
)
from .locations.clinic.location import (
    clinic_menu, clinic_mod, enhancement_lines,
)
from .locations.smith.location import SMITH
from .locations.brewery.location import (
    register_all_brews, register_all_cum_brews, register_fresh_drinks,
)
from .locations.butcher.location import cook_meat, register_all_meat
from .locations.mage_tower.enchantments import setup as mage_setup
from .remains import RemainsLog
from .dungeon import find_inventory_item
from .combat import heal_player
from .needs import item_needs, needs_line
from .needs_runtime import change_text, consume
from .session import GameSession
from .locations.shop.location import VELVET, item_description
from .shop_system import CATEGORIES, ShopDef, ShopHub
from .examine_target import examine_target
from .npcs.seed import seed_npcs
from .settings import bind_npcs
from .sheet import sheet_lines
from .rename import rename_character
from .storage import Leaderboard, PlayerRepository
from .towns.last_light_humans.cafe.service import cafe_death, fed_item
from .inventory import grouped, sort_inventory
from .npcs.talk import talk_to
from .spawns import SPAWN_RULES
from .towns.last_light_humans.cafe.guests import deadly_toggle
from .town_buildings import observers
from .town_buildings.services import TOWN_COMMANDS, TownServices


PROFILE_COMMANDS = {"help", "create", "profile", "add", "inv", "equip",
                    "unequip", "spells", "top", "gender", "body",
                    "graveyard", "drop", "clinic", "mod", "smith",
                    "forge", "give", "consume", "needs", "item",
                    "age", "personality", "sheet", "banter", "intimate",
                    "consent", "refuse", "gift", "barter", "coach",
                    "romance", "home"} | TOWN_COMMANDS
LOBBY_COMMANDS = {"lobby", "lobbies", "join", "leave", "start", "status", "force",
                  "hire", "dismiss", "auto", "resume", "retire", "solo",
                  "surrender", "ready", "decline", "kick"}
COMBAT_COMMANDS = {"hit", "cast", "dodge", "guard", "use"}
CHEST_COMMANDS = {"open", "inspect", "skip"}
SHOP_COMMANDS = {"shop", "buy", "sell", *CATEGORIES}
REMAINS_COMMANDS = {"loot", "pray", "pass", "taste", "pack", "examine"}
MAX_SKIP_DAYS = 365
DEBUG_COMMANDS = {"events", "trigger", "cities", "teleport", "enemies",
                  "spawn", "stage", "deadlydame", "items", "goddess",
                  "time", "slavereset", "rename", "biomes", "nextbiome",
                  "itemlist", "giveitem"}
SLOT_ALIASES = {
    "weapon": "weapon",
    "chest": "chest", "armor": "chest", "armour": "chest", "body": "chest",
    "head": "head", "helmet": "head", "mask": "head", "hat": "head",
    "gloves": "gloves", "hands": "gloves", "gauntlets": "gloves",
    "feet": "feet", "boots": "feet", "shoes": "feet",
    "accessory": "accessory", "ring": "accessory", "neck": "accessory",
    "lingerie": "lingerie", "underwear": "lingerie",
    "crotch": "crotch", "groin": "crotch",
}


def family_lines(player:Player) -> list[str]:
    lines: list[str] = []
    if player.pregnant == "party":
        lines.append(OFFSPRING_TEXTS["expecting_party"].format(
            parent=player.profile.get("pregnant_by", "?")))
    elif player.pregnant:
        lines.append(OFFSPRING_TEXTS["expecting"].format(
            kind=player.pregnant))
    if player.offspring:
        children = ", ".join(
            child_label(child) for child in player.offspring)
        lines.append(OFFSPRING_TEXTS["summary"].format(
            children=children, hp=len(player.offspring) * OFFSPRING_HP))
    return lines


def run_condition(player:Player) -> str:
    state = (f"HP {max(player.hp, 0)}/{max_hp(player)} | "
             f"Mana {player.mana}/{max_mana(player)}"
             if player.alive else "fallen")
    return f"In the dungeon: {state} | {condition_line(player)}"


def profile_text(player:Player) -> str:
    stat_parts = []
    for stat in STAT_NAMES:
        stat_parts.append(stat_total_text(player, stat))
    equipment = " | ".join(
        f"{SLOT_LABELS[slot]}: "
        f"{ITEMS[item_id]['name'] if item_id else '-'}"
        for slot, item_id in player.equipment.items()
    )
    affinity = ", ".join(f"{AFFINITY_LABELS[name]} {value}"
                         for name, value in player.affinity.items())
    deaths = ", ".join(f"{count}× {FATE_LABELS[fate]}"
                       for fate, count in player.deaths.items()) or "none"
    records = player.records
    return "\n".join([
        f"=== {player.full_name} – Lv {player.level} {player.title} "
        f"({player.gender}) ===",
        f"Handle: {player.name} | Race: {race_of(player).name} | "
        f"ID: {player.id[:8]}",
        *sheet_lines(player),
        f"EXP {player.exp}/{exp_needed(player.level)} | "
        f"free points: {player.free_points} | gold: {player.gold}",
        " | ".join(stat_parts),
        f"HP {max_hp(player)} | Mana {max_mana(player)} | "
        f"{totals_line(player)}",
        needs_line(player.needs),
        *family_lines(player),
        f"Body: {body_text(player.body)} – {effects_text(player.body)}",
        *enhancement_lines(player),
        f"Equipment: {equipment}",
        *set_lines(player),
        f"Affinity: {affinity}",
        f"Record: stage {records['deepest_stage']} | runs {records['runs']} "
        f"| kills {records['kills']}",
        f"Fates: {deaths}",
    ] + buff_lines(player))


HINT_TAIL = re.compile(r"\s*(Actions|Options): \[\w.*$")


def strip_hints(messages:list[Message]) -> list[Message]:
    if SHOW_ACTION_HINTS:
        return messages
    cleaned: list[Message] = []
    for message in messages:
        original = message.text.split("\n")
        lines = [HINT_TAIL.sub("", line) for line in original]
        lines = [line for line, before in zip(lines, original)
                 if line.strip() or not before.strip()
                 or not HINT_TAIL.search(before)]
        if lines == original:
            cleaned.append(message)
        elif any(line.strip() for line in lines):
            cleaned.append(replace(message, text="\n".join(lines).rstrip()))
    return cleaned


class GameController:
    def __init__(self, data_path:Path=GAME_DATA_PATH,
                 debug:bool=False) -> None:
        self.debug = debug
        seasons.set_all_year(debug)
        self.is_admin = lambda name: False
        self.boutique = Boutique(data_path)
        farm_ledger = FarmLedger(data_path)
        sweatery_ledger = SweateryLedger(data_path)
        self.remains = RemainsLog(data_path)
        register_fresh_drinks()
        DrainerLedger(data_path).register_all()
        register_all_meat(self.remains.entries)
        mage_setup(data_path)
        register_all_brews(self.remains.entries)
        register_all_products(self.remains.entries, farm_ledger.entries)
        register_all_dairy(self.remains.entries)
        register_all_cum_brews(farm_ledger.entries)
        register_all_sweat(sweatery_ledger.entries, self.remains.entries)
        self.repository = PlayerRepository(data_path)
        self.remains.backfill_ids(self.repository.id_map())
        self.leaderboard = Leaderboard(data_path)
        self.shops = ShopHub(data_path, [ShopDef.from_data(VELVET),
                                         ShopDef.from_data(SMITH)])
        self.shop = self.shops.shops["velvet"]
        self.smith = self.shops.shops["smith"]
        self.visiting: dict[str, str] = {}
        self.farm_ledger = farm_ledger
        self.sweatery_ledger = sweatery_ledger
        self.buster_ledger = BusterLedger(data_path)
        self.online = None
        self.town = TownServices(data_path, self.repository)
        self.town.is_admin = lambda name: self.is_admin(name)
        primary = self.make_bundle("L1")
        self.lobbies = Lobbies(primary, self.make_bundle)
        self.lobbies.counter = 1
        self.group_sleep = GroupSleep(self)
        home_scene.AUTO["check"] = lambda hero: bool(hero.npc) or (
            hero.name in self.session.autopilot
            and hero.name not in self.session.manual)
        self.proposals: dict[str, str] = {}
        self.runs_seen = 0
        self.town.session = primary.session
        self.town.run_check = lambda name: any(
            bundle.session.in_run(name) for bundle in self.lobbies.all())
        self.bank = self.town.bank
        self.creator = CharacterCreator(self.repository)
        seed_npcs(self.repository)
        bind_npcs(self.repository)

    def make_bundle(self, bundle_id:str) -> Bundle:
        session = GameSession(self.repository, self.leaderboard,
                              self.shops, self.remains, self.boutique,
                              self.farm_ledger, self.sweatery_ledger)
        session.buster_ledger = self.buster_ledger
        session.today = lambda: self.town.world.day
        return Bundle(bundle_id, session,
                      ReadyCheck(session, self.town.held_text))

    @property
    def session(self) -> GameSession:
        return self.lobbies.current().session

    @property
    def ready(self) -> ReadyCheck:
        return self.lobbies.current().ready

    def stamp(self, messages:list[Message], bundle_id:str) -> list[Message]:
        for message in messages:
            if not message.recipient and not message.lobby:
                message.lobby = bundle_id
        return messages

    def handle(self, sender:str, text:str, now:float | None=None,
               ) -> list[Message]:
        now = time.monotonic() if now is None else now
        text = text.strip()
        sender = self.repository.resolve(sender)
        if self.creator.is_active(sender):
            return self.handle_creation(sender, text)
        parsed = parse_chat(text)
        if parsed is None:
            return []
        return self.execute(sender, parsed, now)

    def execute(self, sender:str, parsed:Command,
                now:float | None=None) -> list[Message]:
        sender = self.repository.resolve(sender)
        with self.lobbies.focus(sender):
            seen = observers.before(self, sender)
            messages = self.execute_raw(sender, parsed, now)
            observers.after(self, sender, parsed.name, list(parsed.args),
                            seen, messages)
            messages += self.wipe_check()
            found = self.lobbies.of(sender)
        self.lobbies.prune()
        if found is not None:
            self.stamp(messages, found.id)
        return localize(strip_hints(messages), self.repository)

    def execute_raw(self, sender:str, parsed:Command,
                    now:float | None=None) -> list[Message]:
        now = time.monotonic() if now is None else now
        self.town.now = now
        sender = self.repository.resolve(sender)
        command, args = parsed.name, list(parsed.args)
        if (command == "talk" and not args and self.session.state == "event"
                and self.session.events.brewery_inside()):
            command = "shop"
        if command == "help":
            return [Message(help_text(" ".join(args)), sender)]
        if command == "create":
            return self.create(sender)
        if command == "top":
            return self.top(sender)
        if command in DEBUG_COMMANDS:
            return self.debug_command(sender, command, args, now)
        known = (PROFILE_COMMANDS | LOBBY_COMMANDS | COMBAT_COMMANDS
                 | CHEST_COMMANDS | SHOP_COMMANDS | REMAINS_COMMANDS
                 | EVENT_COMMANDS)
        if command not in known:
            return []
        self.runs_seen = self.session.runs_ended
        player = self.repository.load(sender)
        if player is None:
            return [Message("You don't have a character yet. Use [create] to "
                            "make one.", sender)]
        sort_inventory(player)
        if (command in ("accept", "decline")
                and player.name in self.session.recruit_offers):
            return self.session.answer_recruit(player.name, command)
        locked = self.town.lock(player, command)
        if locked:
            return locked
        slept = self.group_sleep.gate(player, command, args, now)
        if slept is not None:
            return slept
        if command == "talk" and args:
            return talk_to(
                player, " ".join(args), self.repository, random.Random(),
                self.session.in_run(player.name), self.session.events.event,
                self.session.enemies, self.session.party)
        if command == "examine" and args:
            if self.session.state == "event":
                guest = self.session.events.guest_examine(
                    player, " ".join(args))
                if guest:
                    return guest
            seen = self.town.look(player, " ".join(args))
            if seen:
                return seen
            return examine_target(
                player, " ".join(args), self.session.enemies,
                self.session.party, self.repository,
                self.session.in_run(player.name))
        if command == "quit" and self.town.on_shift(player):
            return self.town.handle(player, "safeword", args)
        if self.event_give(command, args):
            return self.session.event_action(player.name, command, now, args)
        if command in PROFILE_COMMANDS:
            return self.handle_profile(player, command, args)
        if command in LOBBY_COMMANDS:
            return self.handle_lobby(player, command, now, args)
        if (command in ("shop", "sell") and self.session.state == "event"
                and self.session.events.brewery_inside()):
            return self.session.event_action(player.name, command, now, args)
        if self.session.state == "event" and command in EVENT_COMMANDS:
            return self.session.event_action(player.name, command, now, args)
        if command in CHEST_COMMANDS:
            return self.session.chest_action(player.name, command, now)
        if command == "buy" and self.session.state == "event":
            return self.session.event_action(player.name, command, now, args)
        if command == "shop" and self.session.events.boutique_active():
            return [Message("\n".join(self.session.events.boutique_lines()),
                            player.name)]
        if command == "sell" and self.session.events.boutique_active():
            return self.session.events.boutique_sell(player.name,
                                                     " ".join(args))
        if command in SHOP_COMMANDS:
            return self.handle_shop(player, command, args)
        if command in REMAINS_COMMANDS:
            return self.session.remains_action(player.name, command, now)
        if command in EVENT_COMMANDS and self.session.state != "combat":
            return self.session.event_action(player.name, command, now, args)
        return self.session.submit(player.name, command, args, now)

    def event_give(self, command:str, args:list[str]) -> bool:
        if command != "give" or self.session.state != "event":
            return False
        if "give" not in self.session.events.available():
            return False
        return not (len(args) > 1 and self.repository.exists(args[-1]))

    def handle_shop(self, player:Player, command:str,
                    args:list[str]) -> list[Message]:
        if self.session.in_run(player.name):
            return [Message(SHOPKEEPER["closed"], player.name)]
        if command == "shop":
            self.visiting[player.name] = "velvet"
            return self.shop.command(player, args)
        shop = self.shops.shops[self.visiting.get(player.name, "velvet")]
        if command in CATEGORIES:
            return shop.command(player, [command, *args])
        reference = " ".join(args)
        if command == "buy":
            messages = shop.buy(player, reference)
        else:
            messages = shop.sell(player, reference)
        self.repository.save(player)
        return messages

    def handle_smith(self, player:Player, command:str,
                     args:list[str]) -> list[Message]:
        if self.session.in_run(player.name):
            return [Message(SMITH_TEXTS["closed"], player.name)]
        self.visiting[player.name] = "smith"
        if command == "smith":
            return self.smith.command(player, args)
        messages = self.smith.buy(player, " ".join(args))
        self.repository.save(player)
        return messages

    def wipe_check(self) -> list[Message]:
        session = self.session
        if (session.state not in ("combat", "chest", "remains", "event")
                or not session.party
                or session.recruit_offers or session.living()):
            return []
        session.events.reset()
        return [Message("\n".join(session.end_run()))]

    def tick(self, now:float | None=None) -> list[Message]:
        now = time.monotonic() if now is None else now
        messages: list[Message] = []
        for bundle in self.lobbies.all():
            with self.lobbies.on(bundle):
                messages += self.stamp(
                    self.session.tick(now) + self.drop_fallen()
                    + self.ready.tick(now) + self.offline_sweep(now),
                    bundle.id)
        messages += self.town.tick(now) + self.town.tick_world()
        for bundle in self.lobbies.all():
            with self.lobbies.on(bundle):
                messages += self.stamp(self.wipe_check(), bundle.id)
        self.lobbies.prune()
        return localize(strip_hints(messages), self.repository)

    def is_online(self, name:str) -> bool:
        return self.online is None or name in self.online()

    def offline_sweep(self, now:float) -> list[Message]:
        bundle = self.lobbies.current()
        session = bundle.session
        if self.online is None or session.state != "lobby":
            bundle.offline.clear()
            return []
        messages: list[Message] = []
        for member in list(session.humans()):
            if self.is_online(member.name):
                bundle.offline.pop(member.name, None)
                continue
            since = bundle.offline.setdefault(member.name, now)
            if now - since < LOBBY_OFFLINE_SECONDS:
                continue
            bundle.offline.pop(member.name, None)
            was_leader = session.party[0] is member
            messages += self.ready.void() + session.leave(member.name)
            if was_leader and session.state == "lobby" and session.party:
                messages.append(Message(f"{session.party[0].name} leads the "
                                        f"party now."))
        return messages

    def drop_fallen(self) -> list[Message]:
        messages = self.session.drop_fallen()
        if messages:
            messages += self.ready.void()
        return messages

    def create(self, sender:str) -> list[Message]:
        known = self.repository.load(sender)
        if known is not None and known.npc:
            return [Message("That name belongs to a companion. Pick "
                            "another one.", sender)]
        if self.repository.exists(sender):
            return [Message("You already have a profile. [profile] shows "
                            "it.", sender)]
        return self.creator.start(sender)

    def debug_command(self, sender:str, command:str, args:list[str],
                      now:float) -> list[Message]:
        if not (self.debug or self.is_admin(sender)):
            return []
        if command == "events":
            lines = [f"{rule.kind} ({rule.slot}, from stage {rule.min_stage})"
                     for rule in sorted(SPAWN_RULES,
                                        key=lambda rule: rule.kind)]
            listing = "\n".join(f"  {line}" for line in lines)
            return [Message(f"Events:\n{listing}", sender)]
        if command == "stage":
            return self.session.debug_stage(sender, args, now)
        if command == "enemies":
            return self.debug_enemies(sender)
        if command == "biomes":
            return self.session.debug_biomes(sender)
        if command == "nextbiome":
            return self.session.debug_nextbiome(sender, args, now)
        if command == "spawn":
            return self.session.debug_spawn(sender, " ".join(args), now)
        if command == "deadlydame":
            return [Message(deadly_toggle(), sender)]
        if command == "cities":
            return self.debug_cities(sender)
        if command == "items":
            return self.debug_items(sender, args)
        if command == "itemlist":
            return item_list(sender, args)
        if command == "giveitem":
            return give_item(self, sender, args)
        if command == "goddess":
            return make_goddess(self.repository, args, sender)
        if command == "teleport":
            return self.debug_teleport(sender, args)
        if command == "time":
            return self.debug_time(sender, args)
        if command == "slavereset":
            return self.debug_slavereset(sender)
        if command == "rename":
            return self.debug_rename(sender, args)
        if not args:
            return [Message("Usage: trigger <event> (see [events])", sender)]
        return self.session.debug_trigger(sender, args[0].lower(), now)

    def debug_rename(self, sender:str, args:list[str]) -> list[Message]:
        parts = " ".join(args).split("|")
        if len(parts) != 2 or not all(part.strip() for part in parts):
            return [Message("Usage: rename <old name> | <new name>", sender)]
        text = rename_character(self.repository, getattr(self.town, "mail", None),
                                parts[0].strip(), parts[1].strip())
        return [Message(text, sender)]

    def debug_slavereset(self, sender:str) -> list[Message]:
        player = self.repository.load(sender)
        if player is None:
            return []
        for key in ("castle_offer_later", "control"):
            player.profile.pop(key, None)
        self.town.__dict__.get("castle_offer_pending", set()).discard(
            player.name)
        self.repository.save(player)
        return [Message("Slave state reset: leash gone, Alexandra's "
                        "cooldown cleared.", sender)]

    def debug_time(self, sender:str, args:list[str]) -> list[Message]:
        world = self.town.world
        skip = re.fullmatch(r"\+(\d+)d", args[0].casefold()) if args else None
        if skip:
            days = min(int(skip.group(1)), MAX_SKIP_DAYS)
            lines = []
            for _ in range(days):
                lines += [message.text for message in self.town.pass_day()]
            self.town.tick_routines()
            lines.insert(0, f"⏩ {days} world days passed.")
            args = []
            return [Message("\n".join(lines + [world.clock_text()]),
                            sender)]
        if args:
            try:
                hours, _, minutes = args[0].partition(":")
                hour = int(hours) + int(minutes or 0) / 60
            except ValueError:
                hour = -1.0
            if not 0 <= hour < 24:
                return [Message("Usage: time [hour] – e.g. time 19 or "
                                "time 19:30.", sender)]
            world.anchor = time.time() - hour / 24 * WORLD_DAY_SECONDS
            world.save()
            self.town.tick_routines()
        left = round(world.seconds_left() / 60, 1)
        lines = [f"🕐 {world.clock_text()} (the world day ends in {left} min)"]
        lines += routines.where_lines()
        return [Message("\n".join(lines), sender)]

    def debug_items(self, sender:str, args:list[str]) -> list[Message]:
        for player in list(self.repository.cache.values()):
            self.repository.save(player)
        self.bank.save()
        self.repository.houses.flush()
        store = self.repository.items
        data_path = store.directory.parent
        orphans = store.orphans(store.referenced(data_path))
        if args and args[0].lower() == "purge":
            store.purge(data_path)
            return [Message(f"Removed {len(orphans)} unused item records.",
                            sender)]
        return [Message(f"{len(orphans)} item records are not referenced "
                        f"anywhere. [items purge] deletes them.", sender)]

    def debug_enemies(self, sender:str) -> list[Message]:
        lines = ["Enemies ([spawn <enemy>] starts a fight, key or name):"]
        for key, template in sorted(ENEMIES.items()):
            lines.append(f"  {key}: {template['name']} (hp {template['hp']}, "
                         f"atk {template['attack']}, def "
                         f"{template['defense']}, "
                         f"{template.get('tribe', 'monsters')})")
        lines.append("Places like the wardrobe or the throne are events: "
                     "see [events], start them with [trigger <event>].")
        return [Message("\n".join(lines), sender)]

    def debug_cities(self, sender:str) -> list[Message]:
        player = self.repository.load(self.repository.resolve(sender))
        here = town_key(player) if player is not None else ""
        lines = ["Cities ([teleport <city>] jumps there for free):"]
        for key, town in TOWNS.items():
            marker = " ◀ you are here" if key == here else ""
            lines.append(f"  {key}: {town.name} ({town.race}){marker}")
            lines.append(f"    buildings: {', '.join(town.buildings)}")
            lines.append(f"    locals: " + ", ".join(
                resident.first_name for resident in town.residents))
        return [Message("\n".join(lines), sender)]

    def debug_teleport(self, sender:str, args:list[str]) -> list[Message]:
        player = self.repository.load(self.repository.resolve(sender))
        if player is None:
            return [Message("No character with that name.", sender)]
        wanted = " ".join(args).casefold()
        goal = next((key for key, town in TOWNS.items()
                     if wanted in (key, town.name.casefold(),
                                   town.race.casefold())), "")
        if not goal:
            return [Message("Usage: teleport <city> (see [cities])",
                            player.name)]
        if self.session.in_run(player.name) or self.town.on_shift(player):
            return [Message("Not during a run or a shift.", player.name)]
        self.town.release_rider(player)
        self.town.rides.pop(player.name, None)
        self.town.cafe_seen.pop(player.name, None)
        self.town.regular_stores.pop(player.id, None)
        player.profile["town"] = goal
        mark_visited(player, goal)
        self.town.go(player, "town")
        self.repository.save(player)
        return [Message(f"⚡ Teleported to {TOWNS[goal].name}.", player.name)]

    def set_body(self, name:str, pairs:str) -> list[Message]:
        name = self.repository.resolve(name)
        player = self.repository.load(name)
        if player is None:
            return [Message("No character with that name.", name)]
        if self.session.in_run(name):
            return [Message("Your body can't change in the middle of a "
                            "run.", name)]
        if not (self.debug or self.is_admin(name)):
            return [Message("Your body only changes at Dr. Vane's clinic "
                            "([clinic]).", name)]
        result = parse_body_input(pairs, player.body, player.gender)
        if isinstance(result, str):
            return [Message(result, name)]
        player.body = result
        apply_body_mods(player.body, player.body_mods)
        self.repository.save(player)
        return [Message(f"Body set: {body_text(player.body)} – "
                        f"{effects_text(player.body)}", name)]

    def handle_creation(self, sender:str, text:str) -> list[Message]:
        words = text.lower().split()
        command = words[0] if words else ""
        if command == f"{COMMAND_PREFIX}help":
            return [Message(help_text(" ".join(words[1:])), sender)]
        if command == f"{COMMAND_PREFIX}create":
            return self.creator.start(sender)
        messages, player = self.creator.answer(sender, text)
        if player is not None:
            messages.append(Message(
                f"{profile_text(player)}\n✔ Character saved. "
                f"[lobby] opens a party, [join] joins one.", sender))
        return messages

    def top(self, sender:str) -> list[Message]:
        entries = self.leaderboard.entries()
        if not entries:
            return [Message("Nobody has fallen yet. Yet.", sender)]
        lines = ["📜 Deepest descents"]
        lines += [f"{place}. Stage {entry['stage']} – "
                  f"{', '.join(entry['players'])} ({entry['date']})"
                  for place, entry in enumerate(entries, start=1)]
        return [Message("\n".join(lines), sender)]

    def handle_profile(self, player:Player, command:str,
                       args:list[str]) -> list[Message]:
        if command == "profile":
            target = (self.repository.load(
                self.repository.resolve(" ".join(args))) if args else player)
            if target is None:
                return [Message("Profile not found.", player.name)]
            member = self.session.member(target.name)
            if member is not None:
                return [Message(profile_text(member) + "\n"
                                + run_condition(member), player.name)]
            return [Message(profile_text(target), player.name)]
        if command == "add":
            return self.add_points(player, args)
        if command == "sheet":
            return self.handle_profile(player, "profile", args)
        if command == "age":
            return self.set_age(player, args)
        if command == "personality":
            return self.set_personality(player, args)
        if command == "gender":
            return self.set_gender(player, args)
        if command == "body":
            return [Message(f"Body: {body_text(player.body)}\n"
                            f"Effects: {effects_text(player.body)}",
                            player.name)]
        if command in ("smith", "forge"):
            return self.handle_smith(player, command, args)
        if command == "clinic":
            if self.session.in_run(player.name):
                return [Message(CLINIC_TEXTS["closed"], player.name)]
            return clinic_menu(player, town_key(player))
        if command == "mod":
            messages = clinic_mod(player, args,
                                  self.session.in_run(player.name))
            self.repository.save(player)
            return messages
        if command in TOWN_COMMANDS:
            return self.town.handle(player, command, args)
        if command == "graveyard":
            return [Message("\n".join(self.remains.graveyard()),
                            player.name)]
        if command == "inv":
            return self.inventory(player)
        if command == "item":
            lines = item_report(player, " ".join(args), self.repository)
            return [Message("\n".join(lines), player.name)]
        if command == "drop":
            return self.drop(player, args)
        if command == "give":
            return self.give(player, args)
        if (command == "home" and args
                and args[0].casefold() in ("eat", "cook")):
            return self.home_meal(player, args[0].casefold())
        if command == "home" and args and args[0].casefold() in CHEST_WORDS:
            messages = chest_command(
                player, args, chest_of(player, town_key(player)),
                self.session.in_run(player.name),
                self.town.on_shift(player), town_key(player))
            self.repository.save(player)
            return messages
        if (command == "home" and args
                and args[0].casefold() in ("stool", "sit", "free", "yield")):
            return stool_command(self.town, player, args)
        if command == "home":
            self.town.cafe_seen.pop(player.name, None)
            self.town.go(player, "home")
            parted = self.town.release_rider(player)
            self.town.rides.pop(player.name, None)
            messages = parted + home_command(
                player, args, self.repository,
                self.session.in_run(player.name),
                self.town.on_shift(player), random.Random(),
                town=town_key(player),
                regulars=self.town.regulars_of(player),
                regulars_of=self.town.regulars_of,
                away_of=self.town.where)
            fate = player.profile.pop("home_fate", "")
            if fate:
                messages += cafe_death(self.town, player, fate)
                self.repository.save(player)
            return messages
        if command in ("gift", "barter", "coach", "romance"):
            return npc_command(
                command, args, player, self.repository,
                self.session.in_run(player.name),
                self.town.on_shift(player), random.Random())
        if command in ("intimate", "consent", "refuse"):
            return intimacy_command(self.session, self.proposals, player,
                                    command, args, random.Random())
        if command == "banter":
            members = (self.session.party
                       if self.session.member(player.name) else [])
            return party_chat(player, args, members, random.Random())
        if command == "consume":
            return self.consume_item(player, args)
        if command == "needs":
            return [Message(needs_line(player.needs), player.name)]
        if command == "equip":
            return self.equip(player, args)
        if command == "unequip":
            return self.unequip(player, args)
        return self.spells(player)

    def handle_lobby(self, player:Player, command:str, now:float,
                     args:list[str]) -> list[Message]:
        held = self.town.held_text(player)
        fallen = self.drop_fallen()
        if fallen:
            return fallen + self.handle_lobby(player, command, now, args)
        if held and command in ("lobby", "join", "start", "force",
                                "resume", "ready"):
            return [Message(held, player.name)]
        if command in ("join", "leave", "hire", "dismiss"):
            voided = self.ready.void()
        else:
            voided = []
        if command == "ready":
            return self.ready.ready(player, now)
        if command == "decline":
            return self.ready.decline(player)
        if command == "kick":
            return self.ready.kick(player, " ".join(args))
        if command == "lobbies":
            return self.lobby_list(player)
        if command == "lobby":
            return self.open_or_invite(player, args)
        if command == "join":
            return voided + self.join_lobby(player, args)
        if command == "leave":
            return voided + self.session.leave(player.name)
        if command == "hire":
            return voided + self.session.hire(player, " ".join(args))
        if command == "auto":
            return self.session.set_auto(player, args)
        if command == "dismiss":
            return voided + self.session.dismiss(player, " ".join(args))
        if command == "start":
            return self.ready.start(player, now)
        if command == "solo":
            return self.solo(player, now)
        if command == "resume":
            return self.session.resume(player.name, now)
        if command == "retire":
            return self.session.retire(player.name)
        if command == "force":
            return self.session.force(player.name, now)
        if command == "surrender":
            return self.session.surrender(player.name, now)
        return self.session.status(player.name)

    def solo(self, player:Player, now:float) -> list[Message]:
        if self.lobbies.of(player.name) is not None:
            return self.ready.start(player, now)
        bundle = self.lobbies.free_bundle()
        if bundle is None:
            return [Message(f"All {MAX_LOBBIES} run slots are busy. Try "
                            f"again later.", player.name)]
        with self.lobbies.on(bundle):
            opened = bundle.session.open_lobby(player)
            if bundle.session.state != "lobby":
                return opened
            return self.stamp(bundle.ready.start(player, now), bundle.id)

    def lobby_list(self, player:Player) -> list[Message]:
        rows = []
        for bundle in self.lobbies.open_lobbies():
            session = bundle.session
            rows.append(
                f"  {bundle.id}: {session.party[0].name}'s lobby in "
                f"{TOWNS[session.lobby_town].name} – "
                f"{len(session.party)}/{MAX_PARTY_SIZE}: "
                f"{', '.join(member.name for member in session.party)} "
                f"([join {session.party[0].name}])")
        if not rows:
            return [Message("No open lobbies. [lobby] opens one.",
                            player.name)]
        return [Message("Open lobbies:\n" + "\n".join(rows), player.name)]

    def open_or_invite(self, player:Player,
                       args:list[str]) -> list[Message]:
        if args and args[0].casefold() in ("invite", "decline"):
            return self.lobby_invite(player, args)
        mine = self.lobbies.of(player.name)
        if mine is not None:
            return mine.session.open_lobby(player)
        bundle = self.lobbies.free_bundle()
        if bundle is None:
            return [Message(f"All {MAX_LOBBIES} run slots are busy. Try "
                            f"again later.", player.name)]
        with self.lobbies.on(bundle):
            return bundle.session.open_lobby(player)

    def lobby_invite(self, player:Player,
                     args:list[str]) -> list[Message]:
        name = " ".join(args[1:])
        if args[0].casefold() == "decline":
            self.lobbies.invites.pop(player.name, None)
            return [Message("Invitation declined.", player.name)]
        mine = self.lobbies.of(player.name)
        if (mine is None or mine.session.state != "lobby"
                or mine.session.party[0].name != player.name):
            return [Message("Only the one who opened a lobby can invite. "
                            "[lobby] opens one.", player.name)]
        other = next((self.repository.load(known)
                      for known in self.repository.names()
                      if known.casefold() == name.casefold()), None)
        if other is None or other.npc or other.name == player.name:
            return [Message("Invite whom? [lobby invite <name>]",
                            player.name)]
        if self.lobbies.of(other.name) is not None:
            return [Message(f"{other.name} is already in a party.",
                            player.name)]
        if not self.is_online(other.name):
            return [Message(f"{other.name} is offline.", player.name)]
        self.lobbies.invites[other.name] = player.name
        return [Message(f"You invite {other.name}.", player.name),
                Message(f"{player.name} invites you to the lobby in "
                        f"{TOWNS[mine.session.lobby_town].name} "
                        f"({len(mine.session.party)}/{MAX_PARTY_SIZE}). "
                        f"[join {player.name}]", other.name)]

    def join_lobby(self, player:Player, args:list[str]) -> list[Message]:
        if self.lobbies.of(player.name) is not None:
            return self.session.join(player)
        word = " ".join(args)
        if word:
            bundle = self.lobbies.find(word)
            if bundle is None:
                return [Message(f"No open lobby '{word}'. [lobbies] lists "
                                f"them.", player.name)]
        else:
            invited = self.lobbies.invites.get(player.name)
            options = self.lobbies.open_lobbies()
            bundle = (self.lobbies.find(invited) if invited else
                      options[0] if len(options) == 1 else None)
            if bundle is None and options:
                return self.lobby_list(player)
            if bundle is None:
                return [Message("No lobby is open right now. [lobby] opens "
                                "one.", player.name)]
        with self.lobbies.on(bundle):
            messages = bundle.session.join(player)
        self.lobbies.invites.pop(player.name, None)
        return self.stamp(messages, bundle.id)

    def set_age(self, player:Player, args:list[str]) -> list[Message]:
        if player.npc:
            return [Message("NPCs keep the age they have.", player.name)]
        if self.session.in_run(player.name):
            return [Message("Not during a run.", player.name)]
        if not args:
            return [Message(f"{player.name} is {player.age} years old. "
                            f"[age <{MIN_AGE}-{MAX_AGE}>] changes it.",
                            player.name)]
        if (not args[0].isdigit()
                or not MIN_AGE <= int(args[0]) <= MAX_AGE):
            return [Message(f"Age must be {MIN_AGE} to {MAX_AGE}.",
                            player.name)]
        player.age = int(args[0])
        self.repository.save(player)
        return [Message(f"{player.name} is now {player.age} years old.",
                        player.name)]

    def set_personality(self, player:Player,
                        args:list[str]) -> list[Message]:
        if player.npc:
            return [Message("NPCs keep their personality.", player.name)]
        text = " ".join(args).strip()
        if not text:
            return [Message(f"Personality: {player.personality or 'none'}. "
                            f"[personality <few words>] sets it.",
                            player.name)]
        player.personality = text[:PERSONALITY_MAX]
        self.repository.save(player)
        return [Message(f"Personality set: {player.personality}",
                        player.name)]

    def set_gender(self, player:Player, args:list[str]) -> list[Message]:
        gender = find_gender(" ".join(args)) if args else None
        if gender is None:
            return [Message(f"Usage: gender <{'|'.join(GENDERS)}>",
                            player.name)]
        player.gender = gender
        self.repository.save(player)
        return [Message(f"Gender set: {gender}", player.name)]

    def update_pools(self, player:Player, old_hp:int, old_mana:int) -> None:
        if not self.session.in_run(player.name) or not player.alive:
            return
        player.hp = max(1, min(max_hp(player),
                               player.hp + max_hp(player) - old_hp))
        player.mana = max(0, min(max_mana(player),
                                 player.mana + max_mana(player) - old_mana))

    def add_points(self, player:Player, args:list[str]) -> list[Message]:
        if not args or args[0].lower() not in STAT_ALIASES:
            return [Message("Usage: add <str|agi|vit|int> [amount]",
                            player.name)]
        stat = STAT_ALIASES[args[0].lower()]
        amount = int(args[1]) if len(args) > 1 and args[1].isdigit() else 1
        if amount < 1 or amount > player.free_points:
            return [Message(f"You only have {player.free_points} free "
                            f"points.", player.name)]
        old_hp, old_mana = max_hp(player), max_mana(player)
        player.stats[stat] += amount
        player.free_points -= amount
        self.update_pools(player, old_hp, old_mana)
        self.repository.save(player)
        return [Message(f"{STAT_SHORT[stat]} is now {player.stats[stat]}. "
                        f"Free points: {player.free_points}", player.name)]

    def drop(self, player:Player, args:list[str]) -> list[Message]:
        if not args:
            return [Message("Usage: drop <nr|name> – [inv] shows the "
                            "numbers.", player.name)]
        item_id = find_inventory_item(player, " ".join(args))
        if item_id is None:
            return [Message("No such item in your bag.", player.name)]
        remove_item(player.inventory, item_id)
        self.repository.save(player)
        return [Message(f"{player.name} tosses the {ITEMS[item_id]['name']} "
                        f"aside. Bag: {len(player.inventory)}/"
                        f"{player.bag_size}", player.name)]

    def give(self, player:Player, args:list[str]) -> list[Message]:
        if len(args) < 2:
            return [Message("Usage: give <nr|name> <player>", player.name)]
        target = self.repository.load(
            self.repository.resolve(args[-1]))
        if target is None or target is player:
            return [Message("There is nobody like that to give it to.",
                            player.name)]
        if self.session.in_run(player.name) != self.session.in_run(
                target.name):
            return [Message("You can only trade with someone in the same "
                            "situation (both in the run or both outside).",
                            player.name)]
        if not target.alive:
            return [Message("The dead can't carry anything.", player.name)]
        item_id = find_inventory_item(player, " ".join(args[:-1]))
        if item_id is None:
            return [Message("No such item in your bag.", player.name)]
        if len(target.inventory) >= target.bag_size:
            return [Message(f"{target.name}'s bag is full.", player.name)]
        remove_item(player.inventory, item_id)
        target.inventory.append(item_id)
        self.repository.save(player)
        self.repository.save(target)
        return [Message(f"🎁 {player.name} gives {target.name} "
                        f"{ITEMS[item_id]['name']}{smell_note(item_id)}.")]

    def home_meal(self, player:Player, word:str) -> list[Message]:
        town = town_key(player)
        owned = chest_of(player, town) is not None
        if self.session.in_run(player.name):
            return [Message("Your house is far away while you are in the "
                            "dungeon.", player.name)]
        if not owned and shared_host(player, town,
                                     self.repository) is None:
            return [Message("You have no house here.", player.name)]
        if word == "cook":
            cooked = cook_meat(player)
            if not cooked:
                return [Message("You have nothing to cook: raw meat from "
                                "the butcher goes on the stove.",
                                player.name)]
            self.repository.save(player)
            return [Message(f"🍳 {player.name} cooks: "
                            f"{', '.join(cooked)}.")]

        def food(item_id:str) -> bool:
            return (not ITEMS[item_id].get("raw_meat")
                    and item_needs(item_id).get("hunger", 0) < 0)

        pick = next((item for item in player.inventory if food(item)), None)
        if pick is None and owned:
            account = chest_of(player, town)
            pick = next((item for item in account.items if food(item)),
                        None)
            if pick is not None:
                account.items.remove(pick)
                player.inventory.append(pick)
                self.repository.save(player)
        if pick is None:
            return [Message("You have nothing to eat: food from your bag "
                            "or your chest.", player.name)]
        return self.consume_item(player, [ITEMS[pick]["name"]])

    def consume_item(self, player:Player,
                     args:list[str]) -> list[Message]:
        item_id = find_inventory_item(player, " ".join(args)) if args else None
        item = ITEMS.get(item_id) if item_id else None
        if item is not None and item.get("bottle"):
            return self.drink_bottle(player, item_id, item["bottle"])
        if item is None or item["slot"] != "consumable" or not (
                item_needs(item_id) or item.get("heal")
                or item.get("mana")):
            return [Message("Usage: consume <nr|name> (food, drink or "
                            "tonic from your bag, any time).", player.name)]
        if not player.alive and self.session.in_run(player.name):
            return [Message("The dead do not eat.", player.name)]
        old_hp, old_mana = max_hp(player), max_mana(player)
        remove_item(player.inventory, item_id)
        changes = consume(player, item_id)
        if item.get("heal"):
            heal_player(player, item["heal"])
        if item.get("mana"):
            player.mana = min(max_mana(player), player.mana + item["mana"])
        self.update_pools(player, old_hp, old_mana)
        self.repository.save(player)
        return [Message(f"🍽️ {player.name} consumes {item['name']}: "
                        f"{change_text(changes) or 'no effect'}.")
                ] + fed_item(self.town, player, item_id)

    def drink_bottle(self, player:Player, item_id:str,
                     bottle_id:str) -> list[Message]:
        texts = DRAINER_TEXTS["drainer"]
        if not player.alive and self.session.in_run(player.name):
            return [Message("The dead do not drink.", player.name)]
        ledger = DrainerLedger(self.repository.data_path)
        bottle = ledger.get(bottle_id)
        if bottle is None:
            remove_item(player.inventory, item_id)
            self.repository.save(player)
            return [Message(texts["bottle_empty"], player.name)]
        if not can_receive(player, bottle):
            return [Message(texts["bottle_cannot"].format(
                name=player.name), player.name)]
        remove_item(player.inventory, item_id)
        restore_part(player, bottle)
        ledger.remove(bottle_id)
        self.repository.save(player)
        return [Message(texts["restore_done"].format(
            name=player.name, thing=thing_text(bottle).capitalize()))]

    def inventory(self, player:Player) -> list[Message]:
        if not player.inventory:
            return [Message("Your bag is empty.", player.name)]
        sort_inventory(player)
        gear, consumables = grouped(player)
        lines = [f"Bag ({len(player.inventory)}/{player.bag_size})"]
        index = 1
        for title, items in (("Gear", gear), ("Consumables", consumables)):
            if not items:
                continue
            lines.append(f"-- {title} --")
            for item_id in items:
                lines.append(f"{index}. {item_description(item_id)}")
                index += 1
        return [Message("\n".join(lines), player.name)]

    def equip(self, player:Player, args:list[str]) -> list[Message]:
        if not args:
            return [Message("Usage: equip <nr|name>", player.name)]
        item_id = find_inventory_item(player, " ".join(args))
        if item_id is None or ITEMS[item_id]["slot"] not in EQUIPMENT_SLOTS:
            return [Message("No equippable item found.", player.name)]
        if not can_wear(player, item_id):
            return [Message(wear_refusal(player, item_id), player.name)]
        slot = ITEMS[item_id]["slot"]
        old_hp, old_mana = max_hp(player), max_mana(player)
        remove_item(player.inventory, item_id)
        previous = player.equipment[slot]
        if previous:
            player.inventory.append(previous)
        player.equipment[slot] = item_id
        self.update_pools(player, old_hp, old_mana)
        self.repository.save(player)
        return [Message(f"Equipped: {item_description(item_id)}",
                        player.name)]

    def unequip(self, player:Player, args:list[str]) -> list[Message]:
        slot = SLOT_ALIASES.get(args[0].lower()) if args else None
        if slot is None or player.equipment[slot] is None:
            slots = "|".join(EQUIPMENT_SLOTS)
            return [Message(f"Usage: unequip <{slots}> (slot must be "
                            f"occupied)", player.name)]
        if len(player.inventory) >= player.bag_size:
            return [Message("Your bag is full.", player.name)]
        old_hp, old_mana = max_hp(player), max_mana(player)
        item_id = player.equipment[slot]
        player.equipment[slot] = None
        player.inventory.append(item_id)
        self.update_pools(player, old_hp, old_mana)
        self.repository.save(player)
        return [Message(f"Unequipped: {ITEMS[item_id]['name']}", player.name)]

    def spells(self, player:Player) -> list[Message]:
        lines = ["Spellbook"]
        for spell_id, spell in SPELLS.items():
            if knows_spell(player, spell_id):
                lines.append(f"✔ {spell_id} – {spell['name']} "
                             f"({spell['mana']} mana)")
            else:
                affinity = AFFINITY_LABELS[spell["affinity"]]
                lines.append(f"🔒 {spell['name']} – {affinity} "
                             f"{spell['req_affinity']} or INT "
                             f"{spell['req_intelligence']}")
        return [Message("\n".join(lines), player.name)]
