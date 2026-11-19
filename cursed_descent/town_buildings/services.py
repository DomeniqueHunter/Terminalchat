import random
import time
from pathlib import Path

from ..config import (
    HAPPY_DEFAULT,
    HAPPY_MAX,
    HAPPY_WORDS,
    TRAIN_MAX,
    WORLD_CATCHUP_DAYS,
    WORLD_DAY_SECONDS,
    CAFE_LOCK,
    CAFE_RESPAWN_DAYS,
    VISIT_ASK_VISITS,
    REVIVE_PRICE,
    WORLD_NEED_STAGES,
    WORLD_HP_REGEN,
    WORLD_MANA_REGEN,
    KEPT_GEAR_KEY,
    CAFE_REACTION_SECONDS,
    CAFE_RIDER_RELIEF,
    NULL_RANSOM_PRICE,
    HOUSE_HOLD_PULSE,
    HOUSE_HOLD_SECONDS,
    HOUSE_PIN_SCAN,
    POD_SCAN_SECONDS,
    HOUSE_GUEST_IDLE,
)
from ..inventory import backpack_full, backpack_price
from ..furnishing import garden
from ..furnishing.plants import say
from ..home_scene import bound_text, tick_scenes, timer_line
from ..models import Message, Player
from ..needs import satisfy
from ..needs_runtime import tick_needs
from ..dungeon import regenerate
from ..storage import PlayerRepository
from ..house_regulars import regular_player
from ..house_visit import (
    KEY as VISIT_KEY, enter, hold_update, house_command, release,
    state_of)
from ..houses import home_of, shared_host
from ..preferences import prefs_command
from ..npcs.store import find_local
from ..npcs.visiting import VisitBoard, npc_record, profiles
from ..spawns import AWAY_KINDS
from ..towns import TOWNS, Town, town_key, town_of, town_text
from ..npcs.store import find_local, residents_of
from .chat import chat, friendship, split_topic, tier_of
from .locals import meet, rumors
from ..towns.last_light_humans.maidschool.school import lock_message
from .brothel.building import examine as brothel_examine
from ..towns.last_light_humans.cafe.service import (
    ambient,
    cafe_active,
    cafe_death,
    cafe_examine,
    fed,
    seat_timer,
    sitting_on,
    tick_rides,
    tick_seats,
)
from ..towns.last_light_humans.cafe.content import NO_HOME_SAFEWORD
from ..towns.last_light_humans.cafe.home_seat import NO_CONTROL, WARNING, guest_of
from ..towns.last_light_humans.cafe.training import (
    accepts_invite, add_training, parse_options, train_margin, training_of,
)
from ..captivity import free as free_captive, is_captive
from ..towns.last_light_humans.cafe.stool_trade import release as release_stool
from .world_days import WorldDays, date_text
from ..towns.last_light_humans.cafe.stool_trade import (
    claim, npc_buys, owner_of, ransom_home, stand_up, stool_lock,
    stool_price, where_text,
)
from .visits import (
    ask_address,
    new_home,
    status_line,
    visit_scene,
    invite_scene,
)
from .bodies import MIN_PREF_WIDTH as MIN_WIDTH, normalise_pref, pref_of
from ..towns.last_light_humans.cafe.guests import guest_record
from ..towns.last_light_humans.cafe.seat import (
    guest_prompt,
    rise,
    safeword,
    seat_lock,
    seat_of_rider,
)
from .brothel.clients import client_record
from .brothel.shift import auto_serve
from .brothel.visitors import visit_worker, worker_shift
from .dishes import DISH_KG
from .menu import order
from .regulars import Regulars
from .shifts import work
from .work.content import CLOSED as WORK_CLOSED
from . import registry
from .. import control, routines
from .family import family_command
from ..friends import friend_command
from .regular_talk import regular_talk
from .work.jobs import JOBS, Shift, building_menu, finish
from .work.moves import moves_for
from ..mail import sweep as sweep_mail
from .greeting import GREETED, greeting_for
from .work.timed import step_timed


TOWN_COMMANDS = {"move", "town", "job", "meet", "rumors", "chat",
                 "backpack", "ransom", "salvage", "safeword", "order", "endrun",
                 "regular", "agepref", "regulars", "visit", "invite", "family", "friend", "house",
                 "prefs", "round", "slave", *registry.commands()}
WORK_BUILDINGS = ("brothel", "cafe", *(key for key, spec in registry.specs().items() if spec.jobs))
LEAVES_CAFE = {"town", "meet", "rumors", "book", "practices",
               *registry.place_of()}
PLACE_OF = {**registry.place_of(),
            "town": "town", "meet": "town", "rumors": "town"}
RIDER_ENDS = LEAVES_CAFE | {"job", "visit", "invite", "family", "house"}
CONTROL_CHECK_SECONDS = 20
DEAD_OPEN = {"help", "profile", "sheet", "inv", "needs", "spells", "top",
             "graveyard", "examine", "status", "town", "talk", "chat",
             "meet", "rumors", "endrun"}
DEAD_LOCK = ("You are dead – crushed under a lady in the Fat Ass Café. "
             "You sit out until the current dungeon round is over.")
DEAD_TEXTS = {
    "home_podded": ("You are dead – digested by the Seductress in the "
                    "garden. You sit out until the new day begins."),
    "drained": ("You are dead – drunk dry by Alexandra. You sit out until "
                "the new day begins."),
    "enslaved": ("You are gone – your old self stayed behind as a slave in "
                 "chains. You sit out until the new day begins."),
    "vored": ("You are dead – swallowed whole by Madame Bertha. BAD END: "
              "you sit out until the current dungeon round is over."),
    "anal_vored": ("You are dead – swallowed whole by <<npc.astrid_first>> <<npc.astrid_last>>. "
                   "BAD END: you sit out until the current dungeon round "
                   "is over."),
    "cummed": (
    "You are dead – spent as a load by a <<npc.astrid_last>> sister. You sit out "
    "until the current dungeon round is over."), "brewed": (
    "You are dead – brewed into a batch in the <<npc.astrid_last>> vats. You sit "
    "out until the current dungeon round is over.")}
VAT_OPEN = {"vat", "quit", "round", "help", "status", "examine", "needs", "inv",
            "sheet", "profile", "town"}
PIN_OPEN = {"house", "help", "status", "examine", "needs", "sheet", "profile",
            "inv", "spells", "top", "graveyard", "hold", "pat", "kiss", "lick",
            "struggle", "giveup", "wait", "breath", "encourage"}
TRAINING_OPEN = {"maidschool", "town", "meet", "rumors", "chat", "slave"}
TRAINING_BLOCKED = (TOWN_COMMANDS - TRAINING_OPEN) | {
    "shop", "buy", "sell", "clinic", "mod", "smith", "forge", "lobby",
    "join", "start", "hire", "dismiss", "force", "surrender", "leave"}


def ransom_kind(npc:Player) -> str:
    return ("stool of the café" if npc.npc == "furniture"
            else "drone of the Null Master")


def ransom_price(npc:Player) -> int:
    if npc.npc == "furniture":
        return stool_price(npc)
    return NULL_RANSOM_PRICE * npc.level


DROP_WORDS = ("drop", "ditch", "remove", "forget")


def owners_of(town:str) -> dict[str, str]:
    found: dict[str, str] = {}
    for resident in TOWNS[town].residents:
        if resident.building in ("cafe", "brothel") and resident.role.split(
                )[0] in ("Owner", "Madame"):
            found.setdefault(resident.building, resident.key)
    return found


def mood_text(record:dict) -> str:
    level = record.get("happiness", HAPPY_DEFAULT)
    word = HAPPY_WORDS[min(len(HAPPY_WORDS) - 1,
                           level * len(HAPPY_WORDS) // (HAPPY_MAX + 1))]
    return f", mood {word} ({level}/{HAPPY_MAX})"


class TownServices:
    def __init__(self, data_path:Path, repository:PlayerRepository,
                 rng:random.Random | None=None) -> None:
        self.repository = repository
        self.world = WorldDays(data_path)
        self.pod_scan_due = 0.0
        repository.houses.day = lambda: self.world.day
        self.notes: list[Message] = []
        self.online = lambda: set()
        self.is_admin = lambda name: False
        self.data_path = data_path
        self.regular_stores: dict[str, Regulars] = {}
        self.pulses: dict[str, float] = {}
        self.pin_scan_due = 0.0
        self.ambient_on = True
        self.maid_search: dict = {}
        self.enroll_armed: dict[str, float] = {}
        self.now = 0.0
        self.control_due = 0.0
        self.shifts: dict[str, Shift] = {}
        self.rng = rng or random.Random()
        self.visits = VisitBoard(random.Random(7))
        self.visits_on = True
        self.routines = routines.RoutineBoard(random.Random())
        self.npc_actions = routines.actions.ActionBoard(random.Random())
        AWAY_KINDS.clear()
        self.session = None
        self.run_check = None
        registry.run_setup(self)

    def regulars_of(self, player:Player) -> Regulars:
        store = self.regular_stores.get(player.id)
        if store is None:
            store = Regulars(self.data_path, town_key(player), player.id)
            store.provider = lambda building, who=player: (
                self.visitor_records(who, building))
            store.resolver = self.resolve_ref
            store.credit = self.credit_npc_kill
            store.owners = owners_of(town_key(player))
            self.regular_stores[player.id] = store
        return store

    def pass_day(self) -> list[Message]:
        for name in self.repository.names():
            fallen = self.repository.load(name)
            if (fallen is not None and fallen.records.get(CAFE_LOCK)
                    and "respawn_day" not in fallen.records):
                fallen.records["respawn_day"] = (
                    self.world.day + CAFE_RESPAWN_DAYS)
                self.repository.save(fallen)
        day = self.world.advance()
        messages: list[Message] = []
        fallen_ones = [self.repository.load(name)
                       for name in self.repository.names()]
        fallen_ones += [npc for npc in self.repository.npc_players()
                        if is_captive(npc)]
        for fallen in fallen_ones:
            if (fallen is None or not fallen.records.get(CAFE_LOCK)
                    or fallen.records.get("respawn_day", day) > day):
                continue
            self.revive(fallen)
            messages.append(Message(
                f"{date_text(day)}: {fallen.name} is back among the living.",
                fallen.name))
        messages += npc_buys(self, day)
        if sweep_mail(self.mail, self.repository, day):
            self.mail.save()
        self.notes += messages
        return messages

    def revive(self, fallen:Player) -> None:
        if is_captive(fallen):
            owner = self.repository.load(fallen.profile.get("owner", ""))
            if owner is not None:
                release_stool(self, owner, fallen)
            else:
                free_captive(fallen, self.repository)
        else:
            fallen.records[CAFE_LOCK] = 0
            fallen.records.pop("respawn_day", None)
            self.repository.save(fallen)

    def upkeep(self) -> list[Message]:
        messages: list[Message] = []
        for name in sorted(self.online()):
            player = self.repository.load(name)
            if (player is None or player.npc or not player.alive
                    or player.records.get(CAFE_LOCK) or self.in_run(player)):
                continue
            lines: list[str] = []
            for _ in range(WORLD_NEED_STAGES):
                lines += tick_needs(player)
            lines = list(dict.fromkeys(lines))
            regenerate([player], WORLD_HP_REGEN, WORLD_MANA_REGEN)
            self.repository.save(player)
            messages += [Message(line, name) for line in lines]
        return messages

    def tick_world(self, wall:float | None=None) -> list[Message]:
        due = self.world.due(wall)
        if not due:
            return []
        messages: list[Message] = []
        for _ in range(min(due, WORLD_CATCHUP_DAYS)):
            messages += self.pass_day()
        messages += self.upkeep()
        if due > WORLD_CATCHUP_DAYS:
            self.world.advance(due - WORLD_CATCHUP_DAYS)
        return messages

    def lock(self, player:Player, command:str) -> list[Message]:
        leashed = control.lock(self, player, command)
        if leashed:
            return leashed
        state = state_of(player)
        if (state is not None and state.get("held_by")
                and command not in PIN_OPEN):
            return [Message(f"{state['held_by']} has you pinned. All you "
                            f"can do now: enjoy it, squirm, please "
                            f"{state['held_by']} – or die.", player.name)]
        for spec in registry.specs().values():
            held = spec.lock(self, player, command) if spec.lock else []
            if held:
                return held
        if player.profile.get("pod") and command not in PIN_OPEN:
            return [Message("You are sealed inside the blossom, warm and "
                            "helpless. Only somebody else can pull you "
                            "out now.", player.name)]
        stooled = stool_lock(player, command)
        if stooled:
            return stooled
        stuck = seat_lock(player, command, self.shifts)
        if stuck:
            return stuck
        if (player.records.get(CAFE_LOCK)
                and command not in DEAD_OPEN):
            dead = DEAD_TEXTS.get(player.last_fate, DEAD_LOCK)
            return [Message(dead, player.name)]
        vat = self.shifts.get(player.name)
        if (vat is not None and vat.building == "brewhouse"
                and command not in VAT_OPEN):
            return [Message("You are in the vat. Answer the sisters "
                            "with the buttons in the panel, or leave the "
                            "shift early.", player.name)]
        record = self.school.records.get(player.id)
        if record is None or not record.course:
            return []
        if command not in TRAINING_BLOCKED:
            return []
        return [Message(lock_message(record), player.name)]

    def in_run(self, player:Player) -> bool:
        if self.run_check is not None:
            return self.run_check(player.name)
        return self.session.in_run(player.name)

    def handle(self, player:Player, command:str,
               args:list[str]) -> list[Message]:
        handler = getattr(self, f"do_{command}", None)
        if handler is None:
            building_handler = registry.commands()[command]
            handler = lambda player, args: building_handler(self, player, args)
        missing = self.missing_building(player, command)
        if missing:
            return [Message(missing, player.name)]
        if command in LEAVES_CAFE:
            self.cafe_seen.pop(player.name, None)
        welcome = []
        if command in PLACE_OF:
            place = PLACE_OF[command]
            if (place in GREETED and self.where(player) != place
                    and not self.in_run(player)):
                welcome = [Message(greeting_for(player, place, self.rng),
                                   player.name)]
            self.go(player, place)
        parted = (self.release_rider(player) if command in RIDER_ENDS
                  else [])
        if command in RIDER_ENDS:
            self.rides.pop(player.name, None)
        if player.name not in self.shifts:
            registry.run_idle(player)
        messages = parted + welcome + handler(player, args)
        messages += self.settle_home(player)
        registry.run_save(self)
        self.repository.save(player)
        return messages

    def missing_building(self, player:Player, command:str) -> str:
        town = town_of(player)
        if command in registry.specs() and (
                command not in town.buildings):
            return (f"There is no {command} in {town.name}. "
                    f"Take the train back to the town that has one.")
        return ""

    def where(self, player:Player) -> str:
        shift = self.shifts.get(player.name)
        if shift is not None:
            return shift.building
        if player.name in self.rides or seat_of_rider(
                player, self.shifts) is not None:
            return "cafe"
        if self.in_run(player):
            return "dungeon"
        return player.profile.get("where", "home")

    def go(self, player:Player, place:str) -> None:
        player.profile["where"] = place

    def release_rider(self, player:Player) -> list[Message]:
        if seat_of_rider(player, self.shifts) is None:
            return []
        return rise(player, self.shifts, self.rng, self.now)

    def do_town(self, player:Player, args:list[str]) -> list[Message]:
        if self.in_run(player):
            return [Message("You are down in the dungeon, not in town.",
                            player.name)]
        town = town_of(player)
        return [Message(town_text(town, self.rng.choice(town.happenings)),
                        player.name)]

    def do_meet(self, player:Player, args:list[str]) -> list[Message]:
        if self.in_run(player):
            return [Message("Nobody to meet down here.", player.name)]
        town = town_of(player)
        locals_ = (self.locals_in(town, player)
                   + [npc for npc in self.visitors_in(town.key)
                      if routines.reachable(player, npc.npc)])
        return meet(town, player, " ".join(args), self.rng, locals_,
                    self.visit_places())

    def do_chat(self, player:Player, args:list[str]) -> list[Message]:
        if self.in_run(player):
            return [Message("Nobody to chat with down here.", player.name)]
        town = town_of(player)
        locals_ = (self.locals_in(town, player)
                   + [npc for npc in self.visitors_in(town.key)
                      if routines.reachable(player, npc.npc)])
        name, topic = split_topic(args)
        if not name:
            names = ", ".join(npc.first_name for npc in locals_)
            return [Message(f"Chat with: {names}. Topics: work, town, "
                            f"self ([chat <name> [topic]]).", player.name)]
        npc = find_local(locals_, name)
        if npc is None:
            return [Message(routines.away_message(player, name)
                            or f"Nobody called '{name}' lives here.",
                            player.name)]
        spot = routines.texts.at_place(npc.npc)
        if spot is not None and not spot.dialogues:
            return [Message(f"{npc.first_name} has nothing to say here yet.",
                            player.name)]
        messages = chat(player, npc, topic, self.rng,
                        spot.dialogues if spot else ())
        self.repository.save(npc)
        return messages

    def do_rumors(self, player:Player, args:list[str]) -> list[Message]:
        if self.in_run(player):
            return [Message("Only the dungeon whispers down here.",
                            player.name)]
        return rumors(town_of(player), player, self.rng)

    def do_backpack(self, player:Player, args:list[str]) -> list[Message]:
        if self.in_run(player):
            return [Message("The pack-maker only works in town.",
                            player.name)]
        full, price = backpack_full(player), backpack_price(player)
        info = (f"🎒 Pack-maker – bag {len(player.inventory)}/"
                f"{player.bag_size} slots, extra slots: {player.bag_extra}.")
        if not args or args[0].lower() != "buy":
            if full:
                return [Message(f"{info} Nothing more to sew on.",
                                player.name)]
            return [Message(f"{info} One more slot costs {price} gold "
                            f"([backpack buy]).", player.name)]
        if full:
            return [Message("The pack-maker shakes his head: no more "
                            "pockets fit on that bag.", player.name)]
        if player.gold < price:
            return [Message(f"A new slot costs {price} gold, you carry "
                            f"{player.gold}.", player.name)]
        player.gold -= price
        player.bag_extra += 1
        return [Message(f"🎒 Slot sewn on for {price} gold. Bag now has "
                        f"{player.bag_size} slots.", player.name)]

    def do_salvage(self, player:Player, args:list[str]) -> list[Message]:
        return claim(self, player)

    def do_ransom(self, player:Player, args:list[str]) -> list[Message]:
        if self.in_run(player):
            return [Message("The drones and stools wait far from here.",
                            player.name)]
        held = [npc for npc in self.repository.npc_players()
                if npc.npc in ("drone", "furniture")
                and (not owner_of(npc) or owner_of(npc) != player.name
                     or npc.profile.get("place") != "home")]
        home = bool(args) and args[-1].casefold() == "home"
        name = " ".join(args[:-1] if home else args)
        if not name:
            if not held:
                return [Message("Nobody is waiting to be ransomed.",
                                player.name)]
            lines = ["Ransom ([ransom <name>] or [ransom <name> home]):"]
            lines += [
                f"  {npc.full_name} – {ransom_kind(npc)}, "
                f"{where_text(npc)} (Lv {npc.level}, "
                f"{ransom_price(npc)} gold)" for npc in held]
            return [Message("\n".join(lines), player.name)]
        npc = find_local(held, name)
        if npc is None:
            return [Message(f"Nobody called '{name}' to ransom.",
                            player.name)]
        if home:
            if npc.npc != "furniture":
                return [Message("Only stools go to a home.", player.name)]
            return ransom_home(self, player, npc)
        price = ransom_price(npc)
        if player.gold < price:
            return [Message(f"{npc.full_name} costs {price} gold to "
                            f"ransom.", player.name)]
        player.gold -= price
        if is_captive(npc):
            free_captive(npc, self.repository)
        else:
            restore = npc.profile.get("restore_npc", "")
            npc.profile = dict(npc.profile.get("kept", {}))
            npc.records[CAFE_LOCK] = 0
            npc.records.pop("respawn_day", None)
            self.repository.convert(npc.name, restore)
        return [Message(f"{player.name} pays {price} gold. "
                        f"{npc.full_name} blinks, shudders, and "
                        f"stands up at last – free, but very quiet.",
                        player.name)]

    def place_menu(self, player:Player, building:str) -> list[Message]:
        if self.in_run(player):
            return [Message(WORK_CLOSED[building], player.name)]
        return building_menu(building, player)

    def do_job(self, player:Player, args:list[str]) -> list[Message]:
        if not args or args[0].casefold() not in WORK_BUILDINGS:
            return [Message("[job tavern <job>], [job brothel <job>] or "
                            "[job cafe <job>]. See [tavern], [brothel] "
                            "and [cafe]. Guild jobs: [mine_guild 1], "
                            "[rune_forge 4].", player.name)]
        building = args[0].casefold()
        messages = work(player, building, " ".join(args[1:]),
                        self.in_run(player), self.shifts, self.rng, self.now,
                        self.regulars_of(player), timed=True)
        if player.name in self.shifts and not self.in_run(player):
            self.go(player, building)
        return messages

    def do_move(self, player:Player, args:list[str]) -> list[Message]:
        shift = self.shifts.get(player.name)
        moves = (moves_for(shift.job.key, player) if shift is not None
                 else {})
        if not moves or shift.due <= 0:
            return [Message("You have no show to put on. Start a dancer or "
                            "milk barrel shift first.", player.name)]
        word = " ".join(args).strip().casefold()
        if word not in moves:
            return [Message(f"Moves: {', '.join(moves)}. [move <name>]",
                            player.name)]
        return step_timed(player, shift, self.shifts, self.rng, self.now,
                          word)

    def do_round(self, player:Player, args:list[str]) -> list[Message]:
        shift = self.shifts.get(player.name)
        if shift is None or shift.job.interactive or shift.due <= 0:
            return [Message("You are not on a timed shift. Start a "
                            "waiter, dancer, milk or café shift first.",
                            player.name)]
        return step_timed(player, shift, self.shifts, self.rng, self.now)

    def graduates(self) -> list[Player]:
        return self.repository.graduates()

    def do_order(self, player:Player, args:list[str]) -> list[Message]:
        return order(player, args, self.in_run(player),
                     lambda building, key: fed(
                         self, player, DISH_KG.get((building, key), 0)))

    def real_address(self, client) -> str:
        other = self.repository.load(getattr(client, "player", "") or "")
        if other is None:
            return ""
        town = town_key(other)
        home = home_of(other, town)
        host = None
        if home is None:
            host = shared_host(other, town, self.repository)
            home = home_of(host, town) if host is not None else None
        if home is None or not home.get("address"):
            return ""
        owner = f" ({host.name}'s house)" if host is not None else ""
        return f"{home['address']}{owner}, {TOWNS[town].name}"

    def do_regular(self, player:Player, args:list[str]) -> list[Message]:
        shift = self.shifts.get(player.name)
        client = shift.client if shift is not None else None
        if shift is None or client is None or getattr(client, "rider", ""):
            return [Message("There is nobody here to make a regular. Do "
                            "it while a guest or client is with you.",
                            player.name)]
        building = shift.building
        record = (guest_record(client) if building == "cafe"
                  else client_record(client))
        record.update(new_home(self.rng, getattr(client, "age", 30)))
        store = self.regulars_of(player)
        real = self.real_address(client)
        if real:
            record["home"] = real
            store.set(building, client.name, {"home": real})
        if args and args[0].casefold() == "ask":
            if building == "brothel" and getattr(client, "dominated", False):
                store.add(building, record)
                stored = store.get(building, client.name)
                if stored.get("address_known"):
                    return [Message(f"You already have {client.name}'s "
                                    f"address: {stored.get('home', '?')}.",
                                    player.name)]
                store.set(building, client.name, {"address_known": True})
                return [Message(
                    f"You snap your fingers: 'Your address. Now.' "
                    f"{client.name} stammers 'Yes, Mistress' and writes it "
                    f"on your palm: {stored.get('home', '?')}. He is a "
                    f"regular now. [visit {client.name.split()[-1]}] to "
                    f"call on him.", player.name)]
            stored = store.get(building, client.name)
            if stored is None:
                return [Message(f"{client.name} is no regular yet. "
                                f"[regular] first.", player.name)]
            if stored.get("address_known"):
                return [Message(f"You already have {client.name}'s "
                                f"address: {stored.get('home', '?')}.",
                                player.name)]
            if not ask_address(stored):
                return [Message(f"{client.name} smiles: 'We hardly know "
                                f"each other yet.' (visits "
                                f"{stored.get('visits', 1)}/"
                                f"{VISIT_ASK_VISITS})", player.name)]
            store.set(building, client.name, {"address_known": True})
            return [Message(f"{client.name} presses a folded note into "
                            f"your hand: {stored.get('home', '?')}. "
                            f"[visit {client.name.split()[-1]}] to call on "
                            f"them.", player.name)]
        if args and args[0].casefold() in ("remove", "forget"):
            gone = self.regulars_of(player).forget(building, client.name)
            return [Message(f"{client.name} is no longer a regular."
                            if gone else f"{client.name} was no regular.",
                            player.name)]
        if self.regulars_of(player).add(building, record):
            return [Message(f"{client.name} is now a regular of the "
                            f"{building}. Age, height and body stay the "
                            f"same from now on.", player.name)]
        return [Message(f"{client.name} is already a regular.",
                        player.name)]

    def do_agepref(self, player:Player, args:list[str]) -> list[Message]:
        if len(args) >= 2 and all(word.isdigit() for word in args[:2]):
            low, high = normalise_pref(int(args[0]), int(args[1]))
            player.profile["age_pref"] = [low, high]
            self.repository.save(player)
            return [Message(f"Age preference set: {low} to {high} years. "
                            f"Café guests and stools and brothel clients "
                            f"are drawn from this range.", player.name)]
        low, high = pref_of(player)
        return [Message(f"Your age preference is {low} to {high} years. "
                        f"[agepref <min> <max>] changes it (min 18, at "
                        f"least {MIN_WIDTH + 1} years wide).",
                        player.name)]

    def do_prefs(self, player:Player, args:list[str]) -> list[Message]:
        return prefs_command(player, args, self.repository)

    def do_friend(self, player:Player, args:list[str]) -> list[Message]:
        return friend_command(player, args, self.repository)

    def do_family(self, player:Player, args:list[str]) -> list[Message]:
        return family_command(player, args, self.repository)

    def drop_regular(self, player:Player, args:list[str]) -> list[Message]:
        store = self.regulars_of(player)
        confirm = any(word.casefold() == "confirm" for word in args)
        name = " ".join(word for word in args
                        if word.casefold() != "confirm")
        found = store.find(name)
        if found is None:
            return [Message(f"You have no regular called '{name}'.",
                            player.name)]
        building, record = found
        if not confirm:
            return [Message(f"Ditch {record['name']} as a regular? Body, "
                            f"address and history are gone. "
                            f"[regulars drop {record['name']} confirm]",
                            player.name)]
        store.forget(building, record["name"])
        return [Message(f"{record['name']} is no longer a regular.",
                        player.name)]

    def talk_regular(self, player:Player, args:list[str]) -> list[Message]:
        found = self.regulars_of(player).find(" ".join(args))
        if found is None:
            return [Message("You have no regular by that name.",
                            player.name)]
        building, record = found
        self.regulars_of(player).bump(building, record["name"], "talks")
        return [Message(regular_talk(record, building, self.rng),
                        player.name)]

    def do_regulars(self, player:Player, args:list[str]) -> list[Message]:
        if args and args[0].casefold() in DROP_WORDS:
            return self.drop_regular(player, args[1:])
        if args and args[0].casefold() == "talk":
            if self.in_run(player):
                return [Message("Nobody to talk to down here.",
                                player.name)]
            return self.talk_regular(player, args[1:])
        if args and args[0].casefold() in ("look", "examine"):
            return self.look_regular(player, args[1:])
        store = self.regulars_of(player)
        lines = ["Your regulars:"]
        for building in ("cafe", "brothel"):
            for record in store.all(building):
                kills = (f", {record['kills']} kills"
                         if record.get("kills") else "")
                kills += mood_text(record)
                lines.append(
                    f"  [{building}] {record['name']} – "
                    f"{record.get('age', '?')} years, visits "
                    f"{record.get('visits', 1)}{kills}. "
                    f"{status_line(record)}")
        if len(lines) == 1:
            lines.append("  nobody yet – [regular] makes a guest one.")
        return [Message("\n".join(lines), player.name)]

    def look_regular(self, player:Player, args:list[str]) -> list[Message]:
        found = self.regulars_of(player).find(" ".join(args))
        if found is None:
            return [Message("Look at whom? [regulars look <name>]",
                            player.name)]
        building, record = found
        kills = (f", {record['kills']} kills"
                 if record.get("kills") else "")
        kills += mood_text(record)
        return [Message(
            f"[{building}] {record['name']} – {record.get('age', '?')} "
            f"years, visits {record.get('visits', 1)}{kills}.\n"
            f"{status_line(record)}", player.name)]

    def do_visit(self, player:Player, args:list[str]) -> list[Message]:
        if self.in_run(player):
            return [Message("You cannot visit anyone from the dungeon.",
                            player.name)]
        if player.name in self.shifts or sitting_on(self, player):
            return [Message("Finish what you are doing first.",
                            player.name)]
        _, rest = parse_options(args)
        worker = worker_shift(self.shifts, " ".join(rest))
        if worker is not None:
            boss = self.repository.load(worker[0])
            return visit_worker(player, boss, worker[1], self.rng,
                                self.now)
        if state_of(player) is not None:
            return [Message("You are already visiting somebody: "
                            "[house leave] first.", player.name)]
        text = " ".join(word for word in rest if word.casefold() != "confirm")
        found = self.regulars_of(player).find(text)
        friend = self.friend_host(player, text) if found is None else None
        if friend is not None:
            messages, _ = enter(
                player, friend, "npc", "", friend.profile["address"],
                friend.profile.get("home", ""), "", self.repository,
                self.rng)
            return messages
        if found is None:
            return [Message("Visit whom? [visit <name>] – see [regulars] "
                            "and the address book.", player.name)]
        building, record = found
        if not record.get("address_known"):
            return [Message(f"You do not know where {record['name']} "
                            f"lives. Ask for the address with [regular ask] "
                            f"while they are with you.", player.name)]
        self.cafe_seen.pop(player.name, None)
        messages, home = enter(
            player, regular_player(building, record), "regular", building,
            record.get("address", ""), record.get("home", ""),
            record.get("spouse", "") if record.get("married") else "",
            self.repository, self.rng)
        if home:
            self.regulars_of(player).set(building, record["name"], {
                "visits": record.get("visits", 1) + 1,
                "home_visits": record.get("home_visits", 0) + 1})
        return messages

    def friend_host(self, player:Player, text:str) -> Player | None:
        npc = find_local(self.repository.npc_players(), text)
        if (npc is None or tier_of(friendship(npc, player)) != "friend"
                or not npc.profile.get("address")):
            return None
        return npc

    def do_house(self, player:Player, args:list[str]) -> list[Message]:
        if self.in_run(player):
            return [Message("You are down in the dungeon.", player.name)]
        state = state_of(player)
        word = args[0].casefold() if args else ""
        if state is not None and word == "seat":
            return self.house_seat(player, state, args[1:])
        messages = house_command(player, args, self.repository, self.rng,
                                 self.regulars_of(player))
        fate = player.profile.pop("house_fate", "")
        if fate:
            player.profile.pop(VISIT_KEY, None)
            messages += cafe_death(self, player, fate)
            self.repository.save(player)
        return messages

    def held_text(self, player:Player) -> str:
        if player.records.get(CAFE_LOCK):
            return DEAD_TEXTS.get(player.last_fate, DEAD_LOCK)
        state = state_of(player)
        if state is not None and state.get("held_by"):
            return (f"{state['held_by']} holds you pinned. You are going "
                    f"nowhere, least of all down into a dungeon.")
        shift = self.shifts.get(player.name)
        if shift is not None and shift.mode == "home":
            return "You are in the middle of a seat session. No dungeon now."
        if player.profile.get("pod"):
            return "You are sealed inside the blossom."
        vine = player.profile.get("vine_held")
        if vine:
            return say(vine["kind"], "held_block")
        return bound_text(player, self.repository)

    def tick_pods(self, now:float) -> list[Message]:
        if now < self.pod_scan_due:
            return []
        self.pod_scan_due = now + POD_SCAN_SECONDS
        messages: list[Message] = []
        for player, home, state in garden.expired(
                self.repository, self.repository.houses):
            text = garden.devour(player, state, self.rng)
            if text:
                messages += control.die(
                    self, player, "home_podded", text)
            else:
                self.repository.save(player)
        return messages

    def tick_pins(self, now:float, wall:float | None=None
                  ) -> list[Message]:
        wall = time.time() if wall is None else wall
        if now < self.pin_scan_due:
            return []
        self.pin_scan_due = now + HOUSE_PIN_SCAN
        messages: list[Message] = []
        for name in self.repository.names():
            player = self.repository.load(name)
            state = state_of(player) if player is not None else None
            if state is None or not state.get("held_by"):
                self.pulses.pop(name, None)
                continue
            if "held_until" not in state:
                state["held_until"] = wall + random.uniform(
                    *HOUSE_HOLD_SECONDS)
                self.repository.save(player)
            if wall >= state["held_until"]:
                self.pulses.pop(name, None)
                messages += release(player, self.repository)
            elif wall >= self.pulses.setdefault(name, wall
                                                + HOUSE_HOLD_PULSE):
                self.pulses[name] = wall + HOUSE_HOLD_PULSE
                messages += hold_update(player, self.rng)
        return messages

    def house_seat(self, player:Player, state:dict,
                   args:list[str]) -> list[Message]:
        owner_home = any(entry["kind"] == "owner"
                         for entry in state["present"])
        record = (self.regulars_of(player).get("cafe", state["host"])
                  if state["building"] == "cafe" else None)
        if record is None or not owner_home:
            return [Message("There is no seat session here: only a café "
                            "lady who is at home can offer one.",
                            player.name)]
        return self.home_session(player, "cafe", record, args, "visit")

    def do_invite(self, player:Player, args:list[str]) -> list[Message]:
        if self.in_run(player):
            return [Message("You cannot invite anyone from the dungeon.",
                            player.name)]
        if player.name in self.shifts or sitting_on(self, player):
            return [Message("Finish what you are doing first.",
                            player.name)]
        if state_of(player) is not None:
            return [Message("You are visiting somebody: [house leave] "
                            "first.", player.name)]
        options, rest = parse_options(args)
        found = self.regulars_of(player).find(
            " ".join(word for word in rest if word.casefold() != "confirm"))
        if found is None or found[0] != "cafe":
            return [Message("Invite whom? A café regular: [invite <name>] "
                            "– see [regulars].", player.name)]
        record = found[1]
        mood = record.get("happiness", HAPPY_DEFAULT)
        confirmed = any(word.casefold() == "confirm" for word in args)
        if confirmed and not accepts_invite(mood, self.rng):
            return [Message(f"{record['name']} declines: 'Not today, dear.' "
                            f"(mood {mood}/{HAPPY_MAX})", player.name)]
        return self.home_session(player, "cafe", record, args, "invite")

    def home_session(self, player:Player, building:str,
                     record:dict, args:list[str],
                     command:str) -> list[Message]:
        options, _ = parse_options(args)
        seated = building == "cafe"
        confirmed = any(word.casefold() == "confirm" for word in args)
        if seated and not confirmed:
            place = (f"{record['name']}'s home" if command == "visit"
                     else "your own home")
            return [Message(WARNING.format(
                place=place, sits=options.sits, chosen=options.label(),
                command="house seat" if command == "visit" else command,
                name=record["name"]), player.name)]
        text, _ = (invite_scene(record, self.rng) if command == "invite"
                     else visit_scene(record, building, self.rng))
        guest = guest_of(record)
        shift = Shift("cafe", JOBS[("cafe", "seat")], options.sits,
                      client=guest, due=self.now + CAFE_REACTION_SECONDS,
                      mode="home", bonus=(
                          options.margin_mod + train_margin(
                              training_of(player, guest.name))),
                      risk=options.risk)
        self.shifts[player.name] = shift
        player.profile["home_session"] = {
            "name": record["name"], "points": options.points()}
        store = self.regulars_of(player)
        store.set(building, record["name"], {
            "visits": record.get("visits", 1) + 1,
            "home_visits": record.get("home_visits", 0) + 1})
        self.repository.save(player)
        return [Message(f"{text}\n{NO_CONTROL}", player.name),
                guest_prompt(shift, player)]

    def settle_home(self, player:Player) -> list[Message]:
        info = player.profile.get("home_session")
        if not info or player.name in self.shifts:
            return []
        player.profile.pop("home_session")
        if player.records.get(CAFE_LOCK):
            return []
        level = add_training(player, info["name"], info["points"])
        self.regulars_of(player).mood("cafe", info["name"], 1)
        satisfy(player.needs, {"arousal": -CAFE_RIDER_RELIEF})
        return [Message(f"Seat training with {info['name']}: "
                        f"{level}/{TRAIN_MAX}.", player.name)]

    def respawn_minutes(self, player:Player) -> int:
        left = player.records.get("respawn_day", 0) - self.world.day
        return int((self.world.seconds_left()
                    + max(0, left - 1) * WORLD_DAY_SECONDS) // 60) + 1

    def do_endrun(self, player:Player, args:list[str]) -> list[Message]:
        if not player.records.get(CAFE_LOCK):
            return [Message("There is no run to end for you. [endrun] is "
                            "for the dead – sitting out a round after "
                            "dying in town.", player.name)]
        minutes = self.respawn_minutes(player)
        if args and args[0].casefold() == "pay":
            return self.pay_revive(player)
        return [Message(f"The world clock decides: you are back among the "
                        f"living in about {minutes} minutes. Or skip the "
                        f"wait for {REVIVE_PRICE} gold: [endrun pay]",
                        player.name)]

    def pay_revive(self, player:Player) -> list[Message]:
        purse = (player.profile.get(KEPT_GEAR_KEY)
                 if is_captive(player) else None)
        gold = purse["gold"] if purse is not None else player.gold
        if gold < REVIVE_PRICE:
            return [Message(f"Coming back early costs {REVIVE_PRICE} gold "
                            f"and you only have {gold}. Wait for the "
                            f"world clock.", player.name)]
        if purse is not None:
            purse["gold"] -= REVIVE_PRICE
        else:
            player.gold -= REVIVE_PRICE
        self.repository.save(player)
        self.revive(player)
        return [Message(f"You pay {REVIVE_PRICE} gold. Somebody drags you "
                        f"back into the light: you are among the living "
                        f"again.", player.name)]

    def do_safeword(self, player:Player,
                    args:list[str]) -> list[Message]:
        if player.profile.get("stool_of"):
            return stand_up(self, player)
        shift = self.shifts.get(player.name)
        if shift is not None and shift.mode == "home":
            return [Message(NO_HOME_SAFEWORD, player.name)]
        if shift is not None and not cafe_active(self, player):
            del self.shifts[player.name]
            return ([Message("You leave your shift early.", player.name)]
                    + finish(player, shift))
        return safeword(player, self.shifts, self.rng)

    def do_slave(self, player:Player, args:list[str]) -> list[Message]:
        return control.command(self, player, args)

    def timer_text(self, player:Player) -> str:
        if cafe_active(self, player):
            return seat_timer(self, player)
        shift = self.shifts.get(player.name)
        if shift is not None and shift.due > 0:
            progress = (f"{shift.served} served" if shift.endless
                        else f"{shift.left} left")
            return (f"Next round in "
                    f"{max(0, round(shift.due - self.now))} s – "
                    f"{progress}, {shift.earned} g earned")
        return seat_timer(self, player) or timer_line(player, self.repository)

    def active_kinds(self) -> set[str]:
        event = getattr(getattr(self.session, "events", None), "event", {})
        return {event.get(key, "") for key in ("kind", "phase")} - {""}

    def tick_visits(self, now:float) -> None:
        if not self.visits_on:
            return
        genders = {npc.npc: npc.gender
                   for npc in self.repository.npc_players()
                   if npc.npc in profiles()}
        self.visits.tick(now, tuple(TOWNS), self.active_kinds(), genders)
        AWAY_KINDS.clear()
        AWAY_KINDS.update(self.visits.away_kinds())

    def world_hours(self) -> float:
        share = self.world.elapsed() / WORLD_DAY_SECONDS
        return self.world.day * 24 + share * 24

    def tick_routines(self) -> list[Message]:
        self.routines.tick(self.world_hours())
        routines.actions.follow(self)
        now = self.world_hours()
        routines.HIDDEN.clear()
        routines.HIDDEN.update(
            npc.npc for npc in self.repository.npc_players()
            if npc.profile.get("gone_until", 0) > now
            or npc.profile.get("dead"))
        return self.npc_actions.tick(self, self.now)

    def locals_in(self, town:Town, player:Player) -> list[Player]:
        natives = residents_of(self.repository.npc_players(),
                               town.buildings, town.key)
        return [npc for npc in natives
                if routines.reachable(player, npc.npc)]

    def visitors_in(self, town:str) -> list[Player]:
        keys = {visit.npc for visit in self.visits.visits.values()
                if visit.town == town}
        homes = routines.board.homes()
        keys |= {key for key, place in routines.PLACES.items()
                 if place.town == town and homes[key].town != town}
        return [npc for npc in self.repository.npc_players()
                if npc.npc in keys]

    def visit_places(self) -> dict[str, str]:
        places = {key: place.building
                  for key, place in routines.PLACES.items()}
        places.update({key: visit.building
                       for key, visit in self.visits.visits.items()})
        return places

    def credit_npc_kill(self, ref_id:str) -> None:
        for npc in self.repository.npc_players():
            if ref_id in (npc.id, npc.npc):
                npc.records["kills"] = npc.records.get("kills", 0) + 1
                self.repository.save(npc)
                return

    def resolve_ref(self, ref_id:str) -> dict | None:
        for npc in self.repository.npc_players():
            if ref_id in (npc.id, npc.npc):
                return npc_record(npc, profiles().get(npc.npc))
        return None

    def visitor_records(self, player:Player, building:str) -> list[dict]:
        if not self.visits_on:
            return []
        keys = self.visits.here(town_key(player), building)
        keys += routines.actions.guests_at(town_key(player), building)
        found = (find_local(self.repository.npc_players(), key)
                 for key in keys)
        return [npc_record(npc, profiles().get(npc.npc)) for npc in found
                if npc is not None]

    def tick(self, now:float) -> list[Message]:
        self.now = now
        self.tick_visits(now)
        routine_lines = self.tick_routines()
        if now >= self.control_due:
            self.control_due = now + CONTROL_CHECK_SECONDS
            routine_lines += control.tick(self)
        messages: list[Message] = self.notes
        self.notes = []
        messages += routine_lines
        messages += tick_seats(self, now)
        messages += self.tick_jobs(now)
        messages += self.tick_pins(now)
        messages += self.tick_pods(now)
        messages += tick_scenes(self.repository, self.rng)
        for owner, guest, _ in self.repository.houses.sweep(
                now, HOUSE_GUEST_IDLE):
            messages.append(Message(f"{guest} says goodbye and heads home.",
                                    owner))
        messages += tick_rides(self, now)
        return messages + ambient(self, now)

    def tick_jobs(self, now:float) -> list[Message]:
        messages: list[Message] = []
        for name, shift in list(self.shifts.items()):
            if (shift.building == "cafe" and shift.job.key == "seat") or (
                    shift.due <= 0 or now < shift.due):
                continue
            player = self.repository.load(name)
            if player is None:
                del self.shifts[name]
                continue
            if shift.job.interactive:
                messages += auto_serve(player, self.shifts, self.rng, now,
                                       self.regulars_of(player))
            else:
                messages += step_timed(player, shift, self.shifts,
                                       self.rng, now)
            self.repository.save(player)
        return messages

    def look(self, player:Player, text:str) -> list[Message]:
        seen = cafe_examine(self, player, text)
        return seen or brothel_examine(self, player, text)

    def on_shift(self, player:Player) -> bool:
        return player.name in self.shifts
