import random
import uuid

from .births import age_offspring, give_birth
from .combat import (
    RoundResult, ambush, choose_intents, enemy_hp_text, find_enemy,
    find_player, kill_player, player_hp_text, resolve_round,
)
from .config import (
    CAFE_LOCK, COMPANION_NAME,
    BONUS_GOLD_FACTOR, CHEST_CHANCE, CONSORT_CHANCE, CONSORT_MIN_STAGE,
    SKELETON_CHANCE, SKELETON_CRYPT, SKELETON_CRYPT_CHANCE, SKELETON_FATES,
    SKELETON_MIN_STAGE,
    DAIRY_PRODUCTS, DEFAULT_GENDER,
    EVENT_CHANCE, MAX_PARTY_SIZE, MIMIC_GOLD_FACTOR,
    PRAY_HEAL, PRONOUNS, REMAINS_CHANCE, ROUND_TIMEOUT_SECONDS, STAGE_HP_REGEN,
    STAGE_MANA_REGEN, STEW_FATES, STEW_HEAL, STEW_ITEM, STEW_SPOIL_CHANCE,
    STEW_SPOIL_DAMAGE,
)
from .content import (
    BIOMES, CHEST_TEXTS, CONSORT_TEXTS, ENEMIES, EVENT_TEXTS, ITEMS,
    OFFSPRING_NAMES,
    SKELETON_TEXTS,
    OFFSPRING_TEXTS,
    REMAINS_TEXTS, SPELLS,
)
from .config import (
    BIOME_SEGMENT, DEBUG_BIOME_SEARCH, TEMP_MONSTER_CHANCE,
    TEMP_MONSTER_MIN_STAGE,
)
from .hoard import lost_line, take_hoards
from .houses import grow_gardens
from .items import Item
from .towns import TOWNS, town_key
from .dungeon import (
    apply_curse, build_consort, build_enemy, build_skeleton, build_temp_monster, chest_loot, current_biome,
    find_inventory_item, give_item, grant_exp, is_biome_start, segment_of, vine_ambush,
    is_boss_stage, regenerate, roll_loot, spawn_mimic, seed_drops, spawn_stage,
    stage_exp, stage_gold,
)
from .formulas import (
    clear_buffs, inspect_chance, knows_spell, max_hp, max_mana, mimic_chance,
)
from .events.handler import EventHandler
from .events.common import bonus_drop
from .events.mrs_claus.event import claus_gifts
from .events.recruiter.event import RecruiterMixin
from .npc_trophies import trophy_lines
from .models import Action, Enemy, Message, Player
from .npcs.store import credit_kill, dress_keeper
from .npcs.party import CompanionsMixin
from .needs_runtime import reset_needs, tick_needs
from .smell import absorb_gear
from .sweat import sweat_label
from .locations.boutique.location import Boutique
from .locations.farm.location import FarmLedger
from .locations.sweatery.location import SweateryLedger
from .examine import remains_report
from .remains import RemainsLog
from .locations.displays.location import (
    enemy_displays, maiden_buff, maiden_squeeze,
)
from .locations.venues import (
    city_stop_at, fate_detail, fate_location, location_note,
)
from .locations.mage_tower.spawn import mage_tower_at
from .locations.butcher.npc import butcher_comment
from .locations.butcher.location import meat_profile, register_meat
from .shop_system import ShopHub
from .storage import Leaderboard, PlayerRepository


def find_spell(name:str) -> str | None:
    wanted = name.casefold()
    for spell_id, spell in SPELLS.items():
        if wanted in (spell_id, spell["name"].casefold()):
            return spell_id
    return None


class GameSession(CompanionsMixin, RecruiterMixin):
    def __init__(self, repository:PlayerRepository,
                 leaderboard:Leaderboard, shop:ShopHub,
                 remains:RemainsLog, boutique:Boutique,
                 farm_ledger:FarmLedger,
                 sweatery_ledger:SweateryLedger) -> None:
        self.repository = repository
        self.today = lambda: 0
        self.farm_ledger = farm_ledger
        self.sweatery_ledger = sweatery_ledger
        self.leaderboard = leaderboard
        self.shop = shop
        self.remains = remains
        self.boutique = boutique
        self.events = EventHandler(self)
        self.recruit_offers: set[str] = set()
        self.runs_ended = 0
        self.reset()

    def reset(self) -> None:
        self.state = "idle"
        self.party: list[Player] = []
        self.autopilot: set[str] = set()
        self.manual: set[str] = set()
        self.heir_notes: list[str] = []
        self.proposal_options: dict[str, dict[str, str]] = {}
        self.enemies: list[Enemy] = []
        self.stage = 0
        self.paused_town = ""
        self.lobby_town = ""
        self.round_no = 0
        self.deadline = 0.0
        self.run_kills: dict[str, int] = {}
        self.chest_mimic = False
        self.chest_revealed = False
        self.inspected: set[str] = set()
        self.bonus_fight = ""
        self.trophies: set[str] = set()
        self.events.reset()
        self.run_id = ""
        self.remains_entry: dict | None = None
        self.seen_remains: set[str] = set()

    def member(self, name:str) -> Player | None:
        return find_player(self.party, name)

    def member_for(self, entry:dict) -> Player | None:
        return next((player for player in self.party
                     if player.owns(entry)), None)

    def in_run(self, name:str) -> bool:
        return (self.state in ("combat", "chest", "remains", "event")
                and self.member(name) is not None)

    def available_commands(self) -> list[str]:
        if self.state == "chest":
            return ["open", "inspect", "skip"]
        if self.state == "remains":
            commands = ["loot", "pray", "pass", "examine"]
            if self.remains.has_stew(self.remains_entry, STEW_FATES):
                commands += ["taste", "pack"]
            return commands
        if self.state == "event":
            return self.events.available()
        return []

    def open_lobby(self, player:Player) -> list[Message]:
        if self.state == "paused":
            return [Message("A run is waiting in town: [resume] goes on, "
                            "[retire] ends it.", player.name)]
        if self.state != "idle":
            return [Message("A lobby or run is already in progress.",
                            player.name)]
        pending = self.recruit_pending(player.name)
        if pending:
            return pending
        self.state = "lobby"
        self.party = [player]
        self.lobby_town = town_key(player)
        return [Message(f"🕯 {player.name} opens the gate to the cursed "
                        f"dungeon. [join] to join "
                        f"(1/{MAX_PARTY_SIZE}), [start] to descend.")]

    def join(self, player:Player) -> list[Message]:
        if self.state != "lobby":
            return [Message("No lobby is open right now. [lobby] opens "
                            "one.", player.name)]
        pending = self.recruit_pending(player.name)
        if pending:
            return pending
        if self.member(player.name):
            return [Message("You are already in the party.", player.name)]
        if town_key(player) != self.lobby_town:
            return [Message(
                f"The lobby gathers in {TOWNS[self.lobby_town].name}, you "
                f"are in {TOWNS[town_key(player)].name}. Travel there "
                f"first.", player.name)]
        if len(self.party) >= MAX_PARTY_SIZE:
            return [Message("The party is full.", player.name)]
        self.party.append(player)
        return [Message(f"{player.name} joins the party "
                        f"({len(self.party)}/{MAX_PARTY_SIZE}).")]

    def drop_fallen(self) -> list[Message]:
        if self.state not in ("lobby", "paused"):
            return []
        fallen = [member for member in self.party
                  if member.records.get(CAFE_LOCK)]
        if not fallen:
            return []
        leader = self.party[0]
        messages = []
        for member in fallen:
            self.party.remove(member)
            messages.append(Message(
                f"☠ {member.name} is dead and leaves the party."))
        if not self.humans():
            if self.state == "paused":
                self.party = fallen + self.party
                return messages + [Message("\n".join(
                    self.end_run(town=self.paused_town)))]
            self.reset()
            return messages + [Message("The lobby disbands.")]
        if leader in fallen:
            messages.append(Message(f"{self.party[0].name} leads the "
                                    f"party now."))
        return messages

    def leave(self, name:str) -> list[Message]:
        player = self.member(name)
        if self.state != "lobby" or player is None:
            return [Message("You can only leave while in the lobby.", name)]
        self.party.remove(player)
        if not self.humans():
            self.reset()
            return [Message(f"{player.name} leaves. The lobby disbands.")]
        return [Message(f"{player.name} leaves the party "
                        f"({len(self.party)}/{MAX_PARTY_SIZE}).")]

    def start(self, name:str, now:float) -> list[Message]:
        if self.state != "lobby" or self.member(name) is None:
            return [Message("Only a member of the open lobby can "
                            "start.", name)]
        self.state = "combat"
        self.stage = 1
        self.run_id = uuid.uuid4().hex
        self.run_kills = {player.name: 0 for player in self.party}
        for player in self.party:
            player.hp = max_hp(player)
            player.mana = max_mana(player)
            player.alive = True
            player.action = None
            player.last_hit_by = None
            player.sweat = 0
            player.records["runs"] += 1
        names = ", ".join(player.name for player in self.party)
        verb = "descends" if len(self.party) == 1 else "descend"
        lines = [f"🕳 {names} {verb}. The curse is watching."]
        return [Message("\n".join(lines + self.begin_stage(now)))]

    def enemy_lines(self) -> list[str]:
        lines: list[str] = []
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            note = " – resists melee, weak to magic" if (
                enemy.melee_mult < 1) else ""
            lines.append(f"  {enemy.label} ({enemy_hp_text(enemy)}){note}")
        return lines

    def begin_stage(self, now:float) -> list[str]:
        self.state = "combat"
        self.enemies = spawn_stage(self.stage, self.run_id,
                                      self.lobby_town)
        self.round_no = 0
        biome = current_biome(self.stage, self.run_id,
                              self.lobby_town)
        lines = [""]
        if self.new_biome(biome):
            lines.append(f"🗺 {biome['name']}: {biome['intro']}")
        boss_text = " – BOSS" if is_boss_stage(self.stage) else ""
        lines.append(f"=== Stage {self.stage} · {biome['name']}{boss_text} "
                     f"===")
        lines += self.add_consort()
        lines += self.add_skeleton(biome["name"])
        lines += self.add_temp_monster()
        lines += vine_ambush(biome, self.living(), self.enemies, self.stage)
        lines += maiden_buff(self.enemies, self.remains.entries)
        lines += enemy_displays(self.enemies, self.remains.entries,
                                self.run_id)
        lines += self.enemy_lines()
        return lines + self.begin_round(now)

    def new_biome(self, biome:dict) -> bool:
        if self.stage == 1:
            return True
        if not is_biome_start(self.stage):
            return False
        return current_biome(self.stage - 1, self.run_id,
                             self.lobby_town) is not biome

    def add_consort(self) -> list[str]:
        if (is_boss_stage(self.stage) or self.stage < CONSORT_MIN_STAGE
                or random.random() >= CONSORT_CHANCE):
            return []
        pool = self.remains.consorts(self.run_id)
        if not pool:
            return []
        entry = random.choice(pool)
        uid = self.enemies[-1].uid
        self.enemies[-1] = build_consort(uid, entry, self.stage)
        lines = [CONSORT_TEXTS["appear"].format(dead=entry["name"])]
        return lines + self.consort_recognition([entry])

    def add_skeleton(self, biome_name:str) -> list[str]:
        crypt = biome_name == SKELETON_CRYPT
        chance = SKELETON_CRYPT_CHANCE if crypt else SKELETON_CHANCE
        if (is_boss_stage(self.stage) or self.stage < SKELETON_MIN_STAGE
                or random.random() >= chance):
            return []
        pool = self.remains.skeletons(self.run_id, SKELETON_FATES)
        if not pool:
            return []
        entry = random.choice(pool)
        uid = max(enemy.uid for enemy in self.enemies) + 1
        self.enemies.append(build_skeleton(uid, entry, self.stage))
        key = "crypt" if crypt else "appear"
        lines = [SKELETON_TEXTS[key].format(dead=entry["name"])]
        player = self.member_for(entry)
        if player:
            their = PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])[2]
            lines.append(SKELETON_TEXTS["own"].format(name=player.name,
                                                      their=their))
        return lines

    def add_temp_monster(self) -> list[str]:
        if is_boss_stage(self.stage) or self.stage < TEMP_MONSTER_MIN_STAGE:
            return []
        met = {enemy.temp_id for enemy in self.enemies}
        pool = [entry for entry in self.repository.temp_monsters.all()
                if entry["id"] not in met]
        if not pool or random.random() >= TEMP_MONSTER_CHANCE:
            return []
        entry = random.choice(pool)
        uid = max(enemy.uid for enemy in self.enemies) + 1
        self.enemies.append(build_temp_monster(uid, entry, self.stage))
        kind = ("a wandering adventurer" if entry.get("role") == "adventurer"
                else f"a grown-up {entry.get('species', 'monster')}")
        return [f"👣 {entry['name']} steps out of the dark – {kind}, "
                f"once {entry.get('parent', 'somebody')}'s child. The "
                f"world was not kind to the little one."]

    def fell_temp_monster(self, enemy:Enemy) -> list[str]:
        killer = enemy.killed_by or "the party"
        store = self.repository.temp_monsters
        if not store.die(enemy.temp_id,
                         f"slain on stage {self.stage} by {killer}"):
            return []
        return [f"🪦 {enemy.name} falls and is buried in the graveyard."]

    def rest_skeleton(self, enemy:Enemy) -> list[str]:
        entry = self.remains.lay_to_rest(enemy.origin, SKELETON_FATES)
        if entry is None:
            return []
        lines = [SKELETON_TEXTS["rest"].format(dead=entry["name"])]
        item_id = self.remains.loot(entry)
        living = self.living()
        if item_id and living:
            killer = self.member(enemy.killed_by)
            finder = killer if killer and killer.alive else living[0]
            lines.append(SKELETON_TEXTS["item"].format(
                dead=entry["name"], item=ITEMS[item_id]["name"]))
            lines.append(give_item(finder, item_id))
        return lines

    def consort_recognition(self, entries:list[dict]) -> list[str]:
        lines: list[str] = []
        for entry in entries:
            player = self.member_for(entry)
            if player is None:
                continue
            _, them, their = PRONOUNS.get(player.gender,
                                          PRONOUNS[DEFAULT_GENDER])
            lines.append(CONSORT_TEXTS["own"].format(
                name=player.name, them=them, their=their))
        return lines

    def free_consort(self, enemy:Enemy) -> list[str]:
        entry = self.remains.free(enemy.origin)
        if entry is None:
            return []
        they = PRONOUNS.get(entry["gender"], PRONOUNS[DEFAULT_GENDER])[0]
        plural = they == "they"
        lines = [CONSORT_TEXTS["freed"].format(
            dead=entry["name"], they=they,
            look="look" if plural else "looks",
            crumble="crumble" if plural else "crumbles")]
        item_id = self.remains.loot(entry)
        living = self.living()
        if item_id and living:
            killer = self.member(enemy.killed_by)
            finder = killer if killer and killer.alive else living[0]
            lines.append(CONSORT_TEXTS["item"].format(
                dead=entry["name"], item=ITEMS[item_id]["name"]))
            lines.append(give_item(finder, item_id))
        return lines

    def begin_round(self, now:float) -> list[str]:
        self.round_no += 1
        self.deadline = now + ROUND_TIMEOUT_SECONDS
        lines = ["", f"-- Round {self.round_no} --"]
        lines += choose_intents(self.enemies, self.party)
        for member in self.living():
            if self.is_auto(member):
                member.action = self.npc_action(member)
        lines += [f"  {player.name}: {player_hp_text(player)}, "
                  f"{player.mana}/{max_mana(player)} Mana"
                  for player in self.living()]
        lines.append(f"Actions: [hit] | [cast] | [dodge] | [guard] | [use] "
                     f"({int(ROUND_TIMEOUT_SECONDS)} s)")
        return lines

    def status(self, name:str) -> list[Message]:
        if self.state == "idle":
            return [Message("No run active. [lobby] opens a party.",
                            name)]
        if self.state == "lobby":
            names = ", ".join(player.name for player in self.party)
            return [Message(f"Lobby: {names}", name)]
        if self.state == "paused":
            return [Message(f"The run waits in town after stage "
                            f"{self.stage}: [resume] | [retire]", name)]
        if self.state == "chest":
            return [Message(f"Before stage {self.stage}: a chest waits – "
                            f"[open] | [inspect] | [skip]", name)]
        if self.state == "remains":
            stew = (" | [taste] | [pack]" if self.remains.has_stew(
                self.remains_entry, STEW_FATES) else "")
            return [Message(f"Before stage {self.stage}: remains of "
                            f"{self.remains_entry['name']} – "
                            f"[loot] | [pray] | [pass]{stew}", name)]
        if self.state == "event":
            return [Message(self.events.status(), name)]
        lines = [f"Stage {self.stage}, round {self.round_no}"]
        lines += self.enemy_lines()
        for player in self.party:
            state = player_hp_text(player) if player.alive else "dead"
            sweat = sweat_label(player)
            lines.append(f"  {player.name}: {state}"
                         f"{f' – 💧 {sweat}' if sweat else ''}")
        return [Message("\n".join(lines), name)]

    def parse_action(self, player:Player, kind:str,
                     args:list[str]) -> Action | str:
        rest = " ".join(args[1:])
        if kind == "hit":
            if args and not self.valid_enemy(args[0]):
                return f"No living enemy with number {args[0]}."
            return Action("hit", target=args[0] if args else "")
        if kind == "dodge":
            return Action("dodge")
        if kind == "guard":
            target = " ".join(args)
            if target and not self.valid_ally(target):
                return f"{target} is not a living party member."
            return Action("guard", target=target)
        if kind == "cast":
            return self.parse_cast(player, args)
        if kind == "use":
            if not args:
                return "Which item? [use <nr|name> [target]]"
            item_id = find_inventory_item(player, args[0])
            if item_id is None or ITEMS[item_id]["slot"] != "consumable":
                return f"No usable item '{args[0]}' in your bag."
            if ITEMS[item_id].get("bottle"):
                return "Drink it outside a fight, with consume."
            if rest and not self.valid_ally(rest):
                return f"{rest} is not a living party member."
            return Action("use", target=rest, item=item_id)
        return f"Unknown action '{kind}'."

    def parse_cast(self, player:Player, args:list[str]) -> Action | str:
        if not args:
            return "Which spell? [spells] shows your spells."
        spell_id = find_spell(args[0])
        if spell_id is None or not knows_spell(player, spell_id):
            return f"You don't know '{args[0]}'."
        spell = SPELLS[spell_id]
        if player.mana < spell["mana"]:
            return (f"Not enough mana for {spell['name']} "
                    f"({player.mana}/{spell['mana']}).")
        target = " ".join(args[1:])
        if spell["target"] == "single" and target:
            if not self.valid_enemy(target):
                return f"No living enemy with number {target}."
        if spell["target"] == "ally" and target:
            if not self.valid_ally(target):
                return f"{target} is not a living party member."
        return Action("cast", target=target, spell=spell_id)

    def valid_enemy(self, uid:str) -> bool:
        enemy = find_enemy(self.enemies, uid)
        return enemy is not None and enemy.alive

    def valid_ally(self, name:str) -> bool:
        ally = self.member(name)
        return ally is not None and ally.alive

    def submit(self, name:str, kind:str, args:list[str],
               now:float) -> list[Message]:
        player = self.member(name)
        if self.state != "combat" or player is None:
            return [Message("You are not in an ongoing fight.", name)]
        if not player.alive:
            return [Message("The dead don't fight. You are "
                            "dungeon inventory now.", name)]
        action = self.parse_action(player, kind, args)
        if isinstance(action, str):
            return [Message(action, name)]
        changed = player.action is not None
        player.action = action
        for member in self.living():
            if member.npc and member.action is None:
                member.action = self.npc_action(member)
        ready = sum(1 for member in self.living() if member.action)
        total = len(self.living())
        if ready >= total:
            return self.resolve(now)
        verb = "changes their action" if changed else "is ready"
        return [Message(f"✔ {player.name} {verb} ({ready}/{total}).")]

    def hold_clock(self, seconds:float) -> None:
        if self.state in ("combat", "chest", "remains", "event"):
            self.deadline += seconds

    def tick(self, now:float) -> list[Message]:
        if now < self.deadline:
            return []
        if self.state == "combat":
            return self.resolve(now)
        if self.state == "chest":
            return self.skip_chest(now, "⏳ Nobody dares to touch the chest.")
        if self.state == "remains":
            return self.pass_remains(now)
        if self.state == "event":
            return self.events.expire(now)
        return []

    def force(self, name:str, now:float) -> list[Message]:
        if not self.in_run(name):
            return [Message("You are not in an ongoing fight.", name)]
        if self.state == "chest":
            return self.skip_chest(now)
        if self.state == "remains":
            return self.pass_remains(now)
        if self.state == "event":
            return self.events.expire(now)
        return self.resolve(now)

    def kill_outside(self, player:Player, fate:str, text:str,
                     killer:str, tribe:str, detail:str="",
                     hoard:list[dict] | None=None) -> list[str]:
        player.hp = 0
        player.alive = False
        player.last_hit_by = None
        player.last_fate = fate
        player.last_fate_text = text
        player.deaths[fate] = player.deaths.get(fate, 0) + 1
        clear_buffs(player)
        location = fate_location(fate, detail, self.stage)
        self.remains.add(name=player.name, gender=player.gender, fate=fate,
                         stage=self.stage, killer=killer, tribe=tribe,
                         run_id=self.run_id, detail=detail,
                         location=location, victim=meat_profile(player),
                         char_id=player.id, hoard=hoard)
        self.repository.save(player)
        self.keeper_takes(fate, player)
        lines = ([f"💀 {text}"] + lost_line(player, killer, hoard)
                 + location_note(player, detail, location))
        lines += self.dissolve_dead_maids()
        self.living()
        return lines + self.take_heir_notes()

    def keeper_takes(self, fate:str, victim:Player | None=None,
                     garment:str="") -> None:
        npcs = self.repository.npc_players()
        for keeper in (credit_kill(npcs, fate) if garment == "" else None,
                       dress_keeper(npcs, fate, victim, garment)):
            if keeper is not None:
                self.repository.save(keeper)

    def surrender(self, name:str, now:float) -> list[Message]:
        player = self.member(name)
        if not self.in_run(name) or player is None or self.state == "lobby":
            return [Message("You are not on a run.", name)]
        if self.state != "combat":
            self.bonus_fight = ""
            self.enemies = spawn_stage(self.stage, self.run_id,
                                      self.lobby_town)
        killers = [enemy for enemy in self.enemies if enemy.alive]
        result = RoundResult()
        for member in self.living():
            member.last_hit_by = random.choice(killers)
            kill_player(member, result)
        death_stage = self.stage - 1 if self.bonus_fight else self.stage
        notes = self.record_deaths(result.fallen, death_stage)
        lines = [f"🏳 {name} gives up. The party throws down its weapons."]
        lines += result.lines + notes + self.end_run()
        return [Message("\n".join(lines))]

    def debug_trigger(self, name:str, kind:str, now:float) -> list[Message]:
        if not self.in_run(name) or self.state in ("idle", "lobby"):
            return [Message("Start a run first, then [trigger <event>].",
                            name)]
        self.bonus_fight = ""
        lines = self.events.trigger(kind, now)
        if lines is None:
            return [Message(f"Unknown event '{kind}'. See [events].", name)]
        return [Message("\n".join(lines))]

    def debug_stage(self, name:str, args:list[str],
                    now:float) -> list[Message]:
        if not self.in_run(name) or self.state in ("idle", "lobby"):
            return [Message("Start a run first, then [stage <n>].", name)]
        if len(args) != 1 or not args[0].isdigit() or int(args[0]) < 1:
            return [Message("Usage: stage <n> (jumps to that stage).", name)]
        self.bonus_fight = ""
        self.events.reset()
        self.stage = int(args[0])
        lines = [f"🛠 Debug: jumped to stage {self.stage}."]
        return [Message("\n".join(lines + self.begin_stage(now)))]

    def debug_biomes(self, name:str) -> list[Message]:
        here = ""
        if self.in_run(name) and self.state not in ("idle", "lobby"):
            here = current_biome(self.stage, self.run_id,
                                 self.lobby_town)["name"]
        lines = ["Biomes ([nextbiome] jumps to the next different biome, "
                 "[nextbiome <name>] to a specific one):"]
        for biome in sorted(BIOMES, key=lambda item: item["min_stage"]):
            marker = " ◀ you are here" if biome["name"] == here else ""
            lines.append(f"  {biome['name']} (from stage "
                         f"{biome['min_stage']}, boss "
                         f"{biome['boss']['name']}){marker}")
            lines.append(f"    enemies: "
                         f"{', '.join(dict.fromkeys(biome['enemies']))}")
        return [Message("\n".join(lines), name)]

    def debug_nextbiome(self, name:str, args:list[str],
                        now:float) -> list[Message]:
        if not self.in_run(name) or self.state in ("idle", "lobby"):
            return [Message("Start a run first, then [nextbiome].", name)]
        wanted = " ".join(args).strip().casefold()
        if wanted and not any(wanted in biome["name"].casefold()
                              for biome in BIOMES):
            return [Message("Unknown biome, see [biomes].", name)]
        here = current_biome(self.stage, self.run_id,
                             self.lobby_town)["name"]
        stage = self.stage
        for _ in range(DEBUG_BIOME_SEARCH):
            stage = (segment_of(stage) + 1) * BIOME_SEGMENT + 1
            found = current_biome(stage, self.run_id,
                                  self.lobby_town)["name"]
            if (wanted and wanted in found.casefold()) or (
                    not wanted and found != here):
                break
        else:
            return [Message("No such biome found ahead.", name)]
        self.bonus_fight = ""
        self.events.reset()
        self.stage = stage
        lines = [f"🛠 Debug: jumped to stage {stage} ({found})."]
        return [Message("\n".join(lines + self.begin_stage(now)))]

    def debug_spawn(self, name:str, wanted:str, now:float) -> list[Message]:
        if not self.in_run(name) or self.state in ("idle", "lobby"):
            return [Message("Start a run first, then [spawn <enemy>].",
                            name)]
        wanted = wanted.strip().casefold()
        key = next((key for key, template in ENEMIES.items()
                    if wanted in (key.casefold(),
                                  template["name"].casefold())), "")
        if not key:
            return [Message("Usage: spawn <enemy> (see [enemies]).", name)]
        self.events.reset()
        enemy = build_enemy(1, key, ENEMIES[key], self.stage)
        intro = ["", f"🛠 Debug: {enemy.name} appears."]
        return [Message("\n".join(self.start_bonus_fight(
            "spawn", [enemy], intro, now)))]

    def event_action(self, name:str, command:str, now:float,
                     args:list[str] | None=None) -> list[Message]:
        return self.events.action(name, command, now, args)

    def start_bonus_fight(self, kind:str, enemies:list[Enemy],
                          lines:list[str], now:float) -> list[str]:
        self.state = "combat"
        self.bonus_fight = kind
        self.enemies = enemies
        self.round_no = 0
        return lines + self.enemy_lines() + self.begin_round(now)

    def offer_chest(self, now:float) -> list[str]:
        self.state = "chest"
        self.chest_mimic = random.random() < mimic_chance(self.stage)
        self.chest_revealed = False
        self.inspected = set()
        self.deadline = now + ROUND_TIMEOUT_SECONDS
        return ["", random.choice(CHEST_TEXTS["appear"]),
                f"Actions: [open] | [inspect] | [skip] "
                f"({int(ROUND_TIMEOUT_SECONDS)} s)"]

    def chest_action(self, name:str, command:str,
                     now:float) -> list[Message]:
        player = self.member(name)
        if self.state != "chest" or player is None:
            return [Message("There is no chest in front of you.", name)]
        if not player.alive:
            return [Message("The dead don't open chests.", name)]
        if command == "inspect":
            return self.inspect_chest(player)
        if command == "skip":
            return self.skip_chest(now)
        return self.open_chest(player, now)

    def inspect_chest(self, player:Player) -> list[Message]:
        if player.name in self.inspected:
            return [Message("You already inspected this chest.",
                            player.name)]
        self.inspected.add(player.name)
        if random.random() >= inspect_chance(player):
            return [Message(CHEST_TEXTS["inspect_fail"].format(
                name=player.name))]
        if not self.chest_mimic:
            return [Message(CHEST_TEXTS["inspect_safe"].format(
                name=player.name))]
        self.chest_revealed = True
        found = CHEST_TEXTS["inspect_mimic"].format(name=player.name)
        return [Message(f"{found} [open] to fight it, [skip] to leave "
                        f"it.")]

    def skip_chest(self, now:float, reason:str="") -> list[Message]:
        lines = [reason] if reason else []
        lines.append(CHEST_TEXTS["skip"])
        return [Message("\n".join(lines + self.begin_stage(now)))]

    def open_chest(self, player:Player, now:float) -> list[Message]:
        if not self.chest_mimic:
            lines = [CHEST_TEXTS["loot"].format(name=player.name)]
            lines += chest_loot(self.stage, player, stage_gold(self.stage))
            self.repository.save(player)
            return [Message("\n".join(lines + self.begin_stage(now)))]
        self.state = "combat"
        self.bonus_fight = "mimic"
        self.enemies = spawn_mimic(self.stage)
        self.round_no = 0
        lines = ["", "=== Mimic! ==="]
        if self.chest_revealed:
            lines.append(CHEST_TEXTS["fight"])
        else:
            lines.append(CHEST_TEXTS["ambush"].format(name=player.name))
            result = ambush(self.enemies[0], player)
            lines += result.lines
            lines += self.record_deaths(result.fallen, self.stage - 1)
            if not self.living():
                return [Message("\n".join(lines + self.end_run()))]
        lines += self.enemy_lines()
        return [Message("\n".join(lines + self.begin_round(now)))]

    def clear_bonus(self, now:float) -> list[str]:
        kind = self.bonus_fight
        self.bonus_fight = ""
        amount = sum(enemy.exp for enemy in self.enemies)
        name = self.enemies[0].name
        lines = ["", f"🏆 {name} is defeated! +{amount} EXP"]
        living = self.living()
        for player in living:
            lines += grant_exp(player, amount)
        finder = random.choice(living)
        if kind == "mimic":
            lines.append(f"{finder.name} digs through the Mimic's hoard.")
            gold = stage_gold(self.stage) * MIMIC_GOLD_FACTOR
            lines += chest_loot(self.stage, finder, gold)
            lines += take_hoards(self.remains, ("couch_mimic",),
                                 self.run_id, finder)
        elif kind == "spawn":
            lines.append("🛠 Debug fight won.")
        else:
            gold = stage_gold(self.stage) * BONUS_GOLD_FACTOR
            lines.append(EVENT_TEXTS[kind]["win"].format(name=finder.name))
            finder.gold += gold
            lines.append(f"💰 {finder.name} pockets {gold} gold.")
            if kind == "mrs_claus":
                lines += claus_gifts(living)
            elif kind != "drainer":
                lines.append(give_item(finder, bonus_drop(kind)))
            if kind == "couture" and self.boutique.stock():
                piece = random.choice(self.boutique.stock())
                self.boutique.sell(piece)
                lines.append(EVENT_TEXTS["couture"]["loot"])
                lines.append(give_item(finder, piece))
        lines += trophy_lines(self, finder)
        for player in self.party:
            self.repository.save(player)
        if kind == "drainer":
            return lines + self.events.offer_restore(now)
        return lines + self.begin_stage(now)

    def record_deaths(self, fallen:list[Player], stage:int) -> list[str]:
        notes: list[str] = []
        for player in fallen:
            killer = player.last_hit_by
            detail = fate_detail(player, stage)
            location = fate_location(player.last_fate, detail, stage)
            self.remains.add(
                name=player.name, gender=player.gender,
                fate=player.last_fate, stage=stage,
                killer=killer.name if killer else "the dungeon",
                tribe=killer.tribe if killer else "monsters",
                run_id=self.run_id, detail=detail, location=location,
                soul=player.soul_weapon, victim=meat_profile(player),
                char_id=player.id,
            )
            player.soul_weapon = ""
            notes += location_note(player, detail, location)
            if player.last_fate == "fashion":
                garment = self.boutique.add(player, "hunted")
                self.keeper_takes("fashion", player)
                self.keeper_takes("fashion", player, garment)
            elif player.last_fate == "brewed":
                self.keeper_takes("brewed", player)
            if player.last_fate == "butchered":
                register_meat(self.remains.entries[-1])
                notes += butcher_comment(self.remains.entries[-1])
            if player.last_fate == "iron_maiden":
                notes += maiden_squeeze(self.remains,
                                        self.remains.entries[-1], stage)
        notes += self.dissolve_dead_maids()
        self.living()
        return (notes + self.recruit_notes(fallen)
                + self.take_heir_notes())

    def offer_remains(self, entry:dict, now:float) -> list[str]:
        if entry["fate"] == "fashion" and self.boutique.stock():
            self.seen_remains.add(entry["id"])
            values = {"dead": entry["name"]}
            intro = ["", REMAINS_TEXTS["fashion"].format(**values)]
            return self.events.open_boutique(now, intro)
        self.state = "remains"
        self.remains_entry = entry
        self.seen_remains.add(entry["id"])
        self.deadline = now + ROUND_TIMEOUT_SECONDS
        _, them, their = PRONOUNS.get(entry["gender"],
                                      PRONOUNS[DEFAULT_GENDER])
        values = {"dead": entry["name"], "killer": entry["killer"],
                  "tribe": entry["tribe"], "their": their, "them": them,
                  "Their": their.capitalize()}
        key = f"{entry['fate']}_{entry.get('detail', '')}"
        if key not in REMAINS_TEXTS:
            key = entry["fate"]
        lines = ["", REMAINS_TEXTS[key].format(**values)]
        owner = self.member_for(entry)
        if owner:
            own_their = PRONOUNS.get(owner.gender,
                                     PRONOUNS[DEFAULT_GENDER])[2]
            lines.append(REMAINS_TEXTS["own"].format(name=owner.name,
                                                     their=own_their))
        if entry["item"] and not entry["looted"]:
            lines.append(REMAINS_TEXTS["item"].format(
                dead=entry["name"], item=ITEMS[entry["item"]]["name"]))
        else:
            lines.append(REMAINS_TEXTS["no_item"].format(dead=entry["name"]))
        extra = ""
        if self.remains.has_stew(entry, STEW_FATES):
            lines.append(REMAINS_TEXTS["stew"].format(dead=entry["name"]))
            extra = " | [taste] | [pack]"
        elif entry["fate"] in STEW_FATES:
            lines.append(REMAINS_TEXTS["stew_gone"])
        if self.remains.has_dairy(entry):
            lines.append(REMAINS_TEXTS["dairy_bucket"])
        elif entry["fate"] == "dairy":
            lines.append(REMAINS_TEXTS["dairy_gone"])
        lines.append(REMAINS_TEXTS["commands"].format(
            extra=extra, seconds=int(ROUND_TIMEOUT_SECONDS)))
        return lines

    def remains_action(self, name:str, command:str,
                       now:float) -> list[Message]:
        player = self.member(name)
        if self.state != "remains" or player is None:
            return [Message("There are no remains in front of you.", name)]
        if not player.alive:
            return [Message("The dead have their own remains to worry "
                            "about.", name)]
        if command == "examine":
            self.deadline += ROUND_TIMEOUT_SECONDS / 4
            return [Message("\n".join(remains_report(
                self.remains_entry, player.name, self.remains.entries,
                self.repository)))]
        if command == "pray":
            return self.pray_remains(player, now)
        if command == "pass":
            return self.pass_remains(now)
        if command in ("taste", "pack"):
            if not self.remains.has_stew(self.remains_entry, STEW_FATES):
                return [Message(REMAINS_TEXTS["no_stew"], name)]
            if command == "taste":
                return self.taste_stew(player, now)
            return self.pack_stew(player, now)
        return self.loot_remains(player, now)

    def taste_stew(self, player:Player, now:float) -> list[Message]:
        entry = self.remains_entry
        self.remains.finish_stew(entry)
        their = PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])[2]
        if random.random() < STEW_SPOIL_CHANCE:
            for member in self.living():
                loss = round(max_hp(member) * STEW_SPOIL_DAMAGE)
                member.hp = max(1, member.hp - loss)
            line = REMAINS_TEXTS["taste_spoiled"].format(
                name=player.name, dead=entry["name"],
                percent=round(STEW_SPOIL_DAMAGE * 100))
        else:
            for member in self.living():
                member.hp = min(max_hp(member),
                                member.hp + round(max_hp(member) * STEW_HEAL))
            key = "taste_own" if player.owns(entry) else "taste"
            line = REMAINS_TEXTS[key].format(
                name=player.name, dead=entry["name"], their=their,
                percent=round(STEW_HEAL * 100))
        return [Message("\n".join([line] + self.begin_stage(now)))]

    def pack_stew(self, player:Player, now:float) -> list[Message]:
        entry = self.remains_entry
        if len(player.inventory) >= player.bag_size:
            return [Message("Your bag is full – no room for a jar.",
                            player.name)]
        self.remains.finish_stew(entry)
        player.inventory.append(Item(STEW_ITEM, creator="remains"))
        self.repository.save(player)
        their = PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])[2]
        key = "pack_own" if player.owns(entry) else "pack"
        line = REMAINS_TEXTS[key].format(name=player.name, dead=entry["name"],
                                         their=their)
        return [Message("\n".join([line] + self.begin_stage(now)))]

    def loot_remains(self, player:Player, now:float) -> list[Message]:
        entry = self.remains_entry
        their = PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])[2]
        if len(player.inventory) >= player.bag_size:
            lines = [f"{player.name}'s bag is full – the remains stay "
                     f"untouched."]
            return [Message("\n".join(lines + self.begin_stage(now)))]
        own = player.owns(entry)
        lines: list[str] = []
        item_id = self.remains.loot(entry)
        if item_id is not None:
            key = "loot_own" if own else "loot"
            lines.append(REMAINS_TEXTS[key].format(
                name=player.name, dead=entry["name"], their=their,
                item=ITEMS[item_id]["name"]))
            player.inventory.append(item_id)
        if self.remains.has_dairy(entry):
            lines.append(self.take_dairy(player, entry, own, their))
        if not lines:
            lines = [REMAINS_TEXTS["loot_none"].format(name=player.name)]
        self.repository.save(player)
        return [Message("\n".join(lines + self.begin_stage(now)))]

    def take_dairy(self, player:Player, entry:dict, own:bool,
                   their:str) -> str:
        product = random.choices(list(DAIRY_PRODUCTS),
                                 weights=list(DAIRY_PRODUCTS.values()))[0]
        name = ITEMS[product]["name"]
        if len(player.inventory) >= player.bag_size:
            return REMAINS_TEXTS["dairy_full"].format(item=name,
                                                      name=player.name)
        self.remains.finish_dairy(entry)
        player.inventory.append(Item(product, creator="remains"))
        key = "dairy_found_own" if own else "dairy_found"
        return REMAINS_TEXTS[key].format(name=player.name, item=name,
                                         dead=entry["name"], their=their)

    def pray_remains(self, player:Player, now:float) -> list[Message]:
        for member in self.living():
            member.hp = min(max_hp(member),
                            member.hp + round(max_hp(member) * PRAY_HEAL))
        lines = [REMAINS_TEXTS["pray"].format(
            name=player.name, dead=self.remains_entry["name"],
            percent=round(PRAY_HEAL * 100))]
        return [Message("\n".join(lines + self.begin_stage(now)))]

    def pass_remains(self, now:float) -> list[Message]:
        lines = [REMAINS_TEXTS["pass"].format(
            dead=self.remains_entry["name"])]
        return [Message("\n".join(lines + self.begin_stage(now)))]

    def resolve(self, now:float) -> list[Message]:
        result = resolve_round(self.party, self.enemies)
        lines = [f"~~ Resolving round {self.round_no} ~~"] + result.lines
        death_stage = self.stage - 1 if self.bonus_fight else self.stage
        lines += self.record_deaths(result.fallen, death_stage)
        for enemy in result.killed:
            killer = self.member(enemy.killed_by)
            if killer:
                killer.records["kills"] += 1
                self.run_kills[killer.name] = (
                    self.run_kills.get(killer.name, 0) + 1)
            if enemy.temp_id:
                lines += self.fell_temp_monster(enemy)
            elif enemy.origin and enemy.template_id == "risen_skeleton":
                lines += self.rest_skeleton(enemy)
            elif enemy.origin:
                lines += self.free_consort(enemy)
        if not self.living():
            lines += self.end_run()
        elif not any(enemy.alive for enemy in self.enemies):
            if self.bonus_fight:
                lines += self.clear_bonus(now)
            else:
                lines += self.clear_stage(now)
        else:
            lines += self.begin_round(now)
        return [Message("\n".join(lines))]

    def clear_stage(self, now:float) -> list[str]:
        amount = stage_exp(self.enemies, self.stage)
        gold = stage_gold(self.stage)
        double = " (double!)" if is_boss_stage(self.stage) else ""
        lines = ["", f"🏆 Stage {self.stage} cleared! +{amount} EXP, "
                     f"+{gold} gold each{double}"]
        for player in self.living():
            player.gold += gold
            lines += grant_exp(player, amount)
            absorb_gear(player)
            lines += tick_needs(player)
        lines += roll_loot(self.stage, self.party)
        lines += seed_drops(self.enemies, self.party)
        regenerate(self.party, STAGE_HP_REGEN, STAGE_MANA_REGEN)
        for player in self.party:
            self.repository.save(player)
        return lines + self.next_stage(now)

    def next_stage(self, now:float) -> list[str]:
        lines: list[str] = []
        cleared = self.stage
        self.stage += 1
        if city_stop_at(self.stage):
            return lines + self.events.offer_location("citystop", now)
        if mage_tower_at(self.stage):
            return lines + self.events.offer_location("mage_tower", now)
        location = self.events.location_for(self.stage)
        if location:
            return lines + self.events.offer_location(location, now)
        if random.random() < CHEST_CHANCE:
            return lines + self.offer_chest(now)
        entry = self.remains.pick(cleared, self.run_id, self.seen_remains)
        if entry and random.random() < REMAINS_CHANCE:
            return lines + self.offer_remains(entry, now)
        if random.random() < EVENT_CHANCE:
            return lines + self.events.offer(now)
        return lines + self.begin_stage(now)

    def births(self) -> list[str]:
        lines: list[str] = []
        for player in self.party:
            lines += age_offspring(
                player, self.repository.temp_monsters)
            if player.pregnant:
                lines.append(give_birth(player))
        return lines

    def pause_run(self, town:str) -> list[str]:
        self.state = "paused"
        self.paused_town = town
        self.events.reset()
        self.enemies = []
        for player in self.party:
            player.action = None
            player.profile["town"] = town
            player.profile["where"] = "town"
            self.repository.save(player)
        return ["", f"🚉 The party boards the train to {TOWNS[town].name}. "
                    f"The run waits at stage {self.stage}: [resume] goes "
                    f"on with stage {self.stage + 1}, [retire] ends it."]

    def resume(self, name:str, now:float) -> list[Message]:
        if self.state != "paused" or self.member(name) is None:
            return [Message("There is no waiting run for you.", name)]
        for player in self.party:
            player.hp = max_hp(player)
            player.mana = max_mana(player)
            player.alive = True
            player.action = None
            player.sweat = 0
            self.repository.save(player)
        self.paused_town = ""
        names = ", ".join(player.name for player in self.party)
        lines = [f"🕳 {names} return to the dungeon. The curse is still "
                 f"watching."]
        return [Message("\n".join(lines + self.next_stage(now)))]

    def retire(self, name:str) -> list[Message]:
        if self.state != "paused" or self.member(name) is None:
            return [Message("There is no waiting run for you.", name)]
        return [Message("\n".join(self.end_run(town=self.paused_town)))]

    def release_wanderers(self) -> list[str]:
        lines: list[str] = []
        for member in list(self.party):
            if member.npc == "mercenary" and member.name == COMPANION_NAME:
                self.party.remove(member)
                self.repository.release(member)
                lines.append(random.choice(
                    EVENT_TEXTS["buster_maid"]["goodbye"]).format(
                        name=member.name))
        return lines

    def end_run(self, town:str="") -> list[str]:
        self.runs_ended += 1
        gone = self.release_wanderers() + self.dissolve_dead_maids()
        depth = self.stage - 1 if self.bonus_fight else self.stage
        place = self.leaderboard.add_run(
            depth, [player.name for player in self.party])
        if self.bonus_fight == "mimic":
            where = f"at a chest after stage {depth}"
        elif self.bonus_fight:
            where = f"to {self.enemies[0].name} after stage {depth}"
        else:
            where = f"on stage {depth}"
        lines = ["", f"🌑 The party has fallen – {where}."]
        if town:
            lines = ["", f"🚉 The party boards the train to "
                         f"{TOWNS[town].name}. The run ends after stage "
                         f"{depth}."]
        for player in self.party:
            grow_gardens(player)
            player.records["deepest_stage"] = max(
                player.records["deepest_stage"], depth)
            lines.append(f"  {player.name}: {self.run_kills.get(player.name, 0)} "
                         f"kills, record stage "
                         f"{player.records['deepest_stage']}")
        if place:
            lines.append(f"📜 Rank {place} on the leaderboard!")
        if not town:
            lines.append("The curse awakens. Statues crumble, walls spit "
                         "out, stomachs give back – you all wake up at the "
                         "entrance.")
        if self.bonus_fight == "drainer":
            lines += self.events.drainer_wipe()
        lines += gone
        lines += self.births()
        for player, item_id in ([] if town else apply_curse(self.party)):
            lines.append(f"The curse takes {ITEMS[item_id]['name']} from "
                         f"{player.name} and leaves it with "
                         f"{player.name}'s remains.")
            self.remains.attach_item(player.name, self.run_id, item_id,
                                     player.id)
        restock = self.shop.restock()
        if not town:
            lines.append(restock)
        for player in self.party:
            player.alive = True
            player.action = None
            player.last_hit_by = None
            reset_needs(player)
            clear_buffs(player)
            if town:
                player.profile["town"] = town
                player.profile["where"] = "town"
            self.repository.save(player)
        self.reset()
        return lines
