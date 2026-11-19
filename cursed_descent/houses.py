import random
import time
from typing import Any

from .config import (
    HOME_BIRTH_NIGHTS, HOUSE_BEDS_PER_ROOM, HOUSE_INVITE_POINTS,
    HOUSE_CONSENT_SECONDS, HOUSE_MATE_POINTS,
    HOUSE_TOWN_FACTOR, HOUSE_TYPES, INTIMACY_MIN_AGE, VISIT_ASK_VISITS,
    CAFE_LOCK,
)
from .formulas import max_hp, max_mana
from .births import give_birth
from . import home_scene
from .home_practice import USAGE as PRACTICE_USAGE, parse_practice, practice as home_practice
from .home_play import ACTIVITY_WORDS, activity, split_activity
from .house_regulars import (
    SavingOnly, find_regular, is_regular, regular_by_id, regular_chat,
)
from .house_modes import (
    mode_intro, seat_scene, split_mode, with_mode,
)
from .models import Message, Player
from .needs_runtime import rest_needs
from .npc_menu import romance_scene
from .npcs.store import find_local
from .npcs.talk import town_company
from .party_talk import banter, bonds
from .preferences import consent_of, scene_defaults
from .scenes import DEFAULTS, parse_options
from .town_buildings.bank.ledger import Account, bank_menu, bank_move
from .town_buildings.chat import chat, friendship, split_topic
from .house_store import current as house_store
from .furnishing import garden
from .furnishing.plants import say
from .furnishing import rules as furnishing
from .house_throne import throne_scene
from .house_kinky import bath_use, kinky_use
from .house_visit import DOING, describe_person, dynamic_of, pick_for
from .house_titles import (
    TITLES, order_title, parse_title, title_for, title_line,
)
from .partner_detail import partner_line
from .family_scenes import family_close, family_open
from .towns.last_light_humans.cafe.swallow import clear_belly
from .town_buildings.family import relations
from .towns import START_TOWN


def private(text:str, player:Player) -> list[Message]:
    return [Message(text, player.name)]


def catalogue(town:str) -> list[tuple[str, str, int, int]]:
    factor = HOUSE_TOWN_FACTOR.get(town, 1.0)
    return [(key, name, round(price * factor), rooms)
            for key, (name, price, rooms, _) in HOUSE_TYPES.items()]


def home_of(player:Player, town:str) -> dict[str, Any] | None:
    value = player.profile.get("houses", {}).get(town)
    if value is None:
        return None
    if isinstance(value, dict):
        return house_store().migrate(player, town)
    return house_store().get(value, town)


def grow_gardens(player:Player) -> None:
    for town, house_id in player.profile.get("houses", {}).items():
        if isinstance(house_id, str):
            home = house_store().get(house_id, town)
            if home is not None:
                garden.grow(home)


def lodging_of(player:Player, town:str) -> dict[str, Any] | None:
    house_id = player.profile.get("lodging", {}).get(town)
    return house_store().get(house_id, town) if house_id else None


def chest_of(player:Player, town:str) -> Any:
    house = home_of(player, town) or lodging_of(player, town)
    return house_store().account(house) if house is not None else None


def capacity(home:dict[str, Any]) -> int:
    return HOUSE_TYPES[home["type"]][2] * HOUSE_BEDS_PER_ROOM


def occupants(home:dict[str, Any]) -> int:
    return 1 + len(home["residents"])


def expecting_note(home:dict[str, Any], entry:dict[str, Any],
                   repository:Any=None) -> str:
    if entry.get("id") not in home.get("expecting", []):
        return ""
    nights = 0
    if repository is not None:
        carrier = next((npc for npc in repository.npc_players()
                        if npc.id == entry["id"]),
                       None) or repository.load_by_id(entry["id"])
        if carrier is not None:
            nights = carrier.profile.get("pregnant_nights", 0)
    return f"🤰 expecting (night {nights}/{HOME_BIRTH_NIGHTS})"


def lodging_lines(player:Player, town:str, repository:Any) -> list[str]:
    host = shared_host(player, town, repository)
    if host is None:
        return []
    home = home_of(host, town)
    name = HOUSE_TYPES[home["type"]][0]
    mates = [entry["name"] for entry in home["residents"]
             if entry["id"] != player.id]
    lines = [f"🏠 You live in {host.name}'s {name} "
             f"({occupants(home)}/{capacity(home)} beds). "
             f"[home sleep] rests you there."]
    if mates:
        lines.append("Living there with you: " + ", ".join(mates))
    return lines


def status_lines(player:Player, town:str,
                 repository:Any=None) -> list[str]:
    home = home_of(player, town)
    if home is None:
        lines = (lodging_lines(player, town, repository)
                 if repository is not None else [])
        lines.append("🏠 You own no house here. [home buy <nr|name>]:")
        lines += [f"  {number}. {name} – {price} gold, {rooms} room(s), "
                  f"{rooms * HOUSE_BEDS_PER_ROOM} beds"
                  for number, (_, name, price, rooms)
                  in enumerate(catalogue(town), 1)]
        return lines
    name = HOUSE_TYPES[home["type"]][0]
    lines = [f"🏠 Your {name} ({occupants(home)}/{capacity(home)} beds).",
             HOUSE_TYPES[home["type"]][3]]
    if home["residents"]:
        lines.append("Living with you: " + ", ".join(
            entry["name"] for entry in home["residents"]))
    if home["guests"]:
        lines.append("Guests tonight: " + ", ".join(
            entry["name"] for entry in home["guests"]))
    for entry in home["residents"] + home["guests"]:
        note = expecting_note(home, entry, repository)
        if note:
            lines.append(f"{entry['name']}: {note}")
    lines.append("[home sleep] [home invite <npc>] [home movein <name>] "
                 "[home talk <name> [topic]] [home do <name> "
                 + "|".join(ACTIVITY_WORDS) + "] "
                 "[home practice <name> <act> <give|receive> [amount] "
                 "[in|on]] [home romance <name> [domina|sub|seat]] "
                 "[home order <name> " + "|".join(TITLES) + "] "
                 "[home leave <name>] [home chest] [home look] [home eat] "
                 "[home cook] [home sex <name>] [home back] "
                 "[home accept|decline] [home moveout]")
    return lines


def find_type(text:str, town:str) -> str:
    wanted = text.strip().casefold()
    entries = catalogue(town)
    if wanted.isdigit() and 1 <= int(wanted) <= len(entries):
        return entries[int(wanted) - 1][0]
    for key, name, _, _ in entries:
        if wanted in (key, name.casefold()):
            return key
    return ""


def buy(player:Player, town:str, text:str, repository:Any
        ) -> list[Message]:
    if home_of(player, town) is not None:
        return private("You already own a house in this town.", player)
    key = find_type(text, town)
    if not key:
        return private("\n".join(status_lines(player, town, repository)),
                       player)
    _, name, price, _ = next(entry for entry in catalogue(town)
                             if entry[0] == key)
    if player.gold < price:
        return private(f"The {name} costs {price} gold. You have "
                       f"{player.gold}.", player)
    player.gold -= price
    house = house_store().create(town, player, key, price)
    player.profile.setdefault("houses", {})[town] = house["id"]
    repository.save(player)
    return [Message(f"🔑 {player.name} buys the {name} for {price} gold. "
                    f"💰 {player.gold}")]


def shared_host(player:Player, town:str, repository:Any
                ) -> Player | None:
    house = lodging_of(player, town)
    if house is not None and any(entry["id"] == player.id
                                 for entry in house["residents"]):
        host = repository.load_by_id(house["owner"])
        if host is not None:
            return host
    player.profile.get("lodging", {}).pop(town, None)
    for name in repository.names():
        host = repository.load(name)
        home = home_of(host, town) if host is not None else None
        if home is not None and any(entry["id"] == player.id
                                    for entry in home["residents"]):
            note_residence(player, host, home, town, repository)
            return host
    return None


def note_residence(player:Player, host:Player, home:dict[str, Any],
                   town:str, repository:Any) -> None:
    lodging = player.profile.setdefault("lodging", {})
    if lodging.get(town) != home["id"] and not is_regular(player):
        lodging[town] = home["id"]
        repository.save(player)


def home_births(player:Player, home:dict[str, Any],
                repository:Any) -> list[str]:
    lines: list[str] = []
    carriers = {npc.id: npc for npc in repository.npc_players()
                if npc.pregnant}
    ids = [entry["id"] for entry in home["residents"] + home["guests"]]
    for entry_id in ids + home.get("expecting", []):
        other = (repository.load_by_id(entry_id)
                 if not entry_id.startswith("reg:") else None)
        if other is not None and other.pregnant:
            carriers[other.id] = other
    for other in carriers.values():
        nights = other.profile.get("pregnant_nights", 0) + 1
        other.profile["pregnant_nights"] = nights
        if nights >= HOME_BIRTH_NIGHTS:
            lines.append(f"👶 {give_birth(other)}")
        repository.save(other)
    home["expecting"] = [entry_id for entry_id in home.get("expecting", [])
                         if entry_id in carriers
                         and carriers[entry_id].pregnant]
    return lines


def sleep(player:Player, town:str, repository:Any) -> list[Message]:
    home = home_of(player, town)
    away = hosted_by(player, town, repository)
    if home is None or away is not None:
        host = away or shared_host(player, town, repository)
        if host is None:
            return private("You have no house here.", player)
        return rest_at(player, host, repository)
    player.hp = max_hp(player)
    player.mana = max_mana(player)
    player.sweat = 0
    rest_needs(player)
    births = home_births(player, home, repository)
    guests = [entry["name"] for entry in home["guests"]]
    home["guests"] = []
    belly = clear_belly(player)
    repository.save(player)
    tail = (f" {', '.join(guests)} leaves in the morning."
            if guests else "")
    text = (f"🛏 {player.name} sleeps in a real bed. HP, mana and sleep "
            f"are restored.{tail}")
    extra = [line for line in (furnishing.bed_line(home),
                               furnishing.comfort_buff(player, home))
             if line]
    repository.save(player)
    return [Message("\n".join([text] + extra + ([belly] if belly else [])
                              + births), player.name)]


def rest_at(player:Player, host:Player, repository:Any) -> list[Message]:
    player.hp = max_hp(player)
    player.mana = max_mana(player)
    player.sweat = 0
    rest_needs(player)
    belly = clear_belly(player)
    repository.save(player)
    return [Message(f"🛏 {player.name} sleeps in {host.name}'s house. HP, "
                    f"mana and sleep are restored."
                    + (f"\n{belly}" if belly else ""), player.name)]


def lookup(player:Player, repository:Any, name:str,
           home:dict[str, Any] | None=None,
           regulars:Any=None) -> Player | None:
    wanted = name.casefold()
    if home is not None:
        for entry in home["residents"] + home["guests"]:
            if entry["id"] == player.id:
                continue
            names = {entry["name"].casefold(),
                     entry["name"].split()[0].casefold()}
            found = (regular_by_id(regulars, entry["id"])
                     or repository.load_by_id(entry["id"])
                     or find_local(town_company(repository), entry["name"]))
            if found is not None:
                names |= {found.full_name.casefold(), found.name.casefold(),
                          (found.first_name or found.name).casefold()}
            if wanted in names:
                return found
    if home is not None and home.get("owner") != player.id:
        boss = repository.load_by_id(home["owner"])
        if boss is not None and wanted in (
                boss.full_name.casefold(), boss.name.casefold(),
                (boss.first_name or boss.name).casefold()):
            return boss
    other = find_local(town_company(repository), name)
    if other is not None:
        return other
    other = find_regular(regulars, name)
    if other is not None:
        return other
    other = repository.load(repository.resolve(name))
    return other if other is not None and other is not player else None


def trusted(player:Player, other:Player) -> bool:
    return is_regular(other) or (friendship(other, player) >= HOUSE_INVITE_POINTS
            or bonds(player).get(other.id, 0) >= HOUSE_INVITE_POINTS
            or other.id in relations(player))


def invite(player:Player, home:dict[str, Any], other:Player,
           repository:Any, mode:str="") -> list[Message]:
    if any(entry["id"] == other.id
           for entry in home["residents"] + home["guests"]):
        return private(f"{other.name} is already here.", player)
    if occupants(home) + len(home["guests"]) >= capacity(home):
        return private("The house has no free bed.", player)
    if other.npc and not trusted(player, other):
        return private(f"{other.first_name or other.name} doesn't know "
                       f"you well enough to visit.", player)
    elsewhere = house_store().guest_elsewhere(other.id, home)
    if elsewhere is not None:
        return private(f"{other.name} is a guest at "
                       f"{elsewhere['owner_name']}'s house right now.",
                       player)
    entry = {"id": other.id, "name": other.full_name,
             "npc": other.npc != "" or is_regular(other),
             "seen": time.monotonic()}
    if mode:
        entry["mode"] = mode
    home["guests"].append(entry)
    repository.save(player)
    intro = mode_intro(mode, other)
    hello = title_for(home, player, other, "greet", random.Random())
    return [Message(f"🕯 {other.full_name} comes over for the evening"
                    f"{role_note(player, other)}."
                    + (f" {intro}" if intro else "")
                    + (f"\n{hello}" if hello else ""))]


def role_note(player:Player, other:Player) -> str:
    role = relations(player).get(other.id, {}).get("role", "")
    return f" – your {role}" if role else ""


def invitees(player:Player, home:dict[str, Any], repository:Any,
             regulars:Any) -> list[Player]:
    present = {entry["id"] for entry in home["residents"] + home["guests"]}
    people = [npc for npc in town_company(repository)
              if trusted(player, npc)]
    for name in repository.names():
        hero = repository.load(name)
        if hero is not None and not hero.npc and hero.id != player.id:
            people.append(hero)
    if regulars is not None:
        for building in ("cafe", "brothel"):
            for record in regulars.all(building):
                found = find_regular(regulars, record["name"])
                if found is not None:
                    people.append(found)
    seen: set[str] = set()
    return [person for person in people
            if person.id not in present and not seen.add(person.id)]


def is_hero(other:Player) -> bool:
    return not other.npc and not is_regular(other)


def offer_to(owner:Player, home:dict[str, Any], other:Player, word:str,
             mode:str, repository:Any, town:str) -> list[Message]:
    here = home["residents"] if word == "movein" else (
        home["residents"] + home["guests"])
    if any(entry["id"] == other.id for entry in here):
        return private(f"{other.name} is already "
                       f"{'living' if word == 'movein' else ''} here."
                       .replace("  ", " "), owner)
    other.profile["house_offer"] = {
        "from_id": owner.id, "from": owner.name, "kind": word,
        "mode": mode, "town": town}
    repository.save(other)
    ask = ("asks you to move into" if word == "movein"
           else "invites you to")
    return [Message(f"📨 You ask {other.name}"
                    f"{' to move in' if word == 'movein' else ' over'}. "
                    f"{other.name} has to confirm on their own screen.",
                    owner.name),
            Message(f"📨 {owner.name} {ask} their house. Confirm with "
                    f"[home accept] or [home decline].", other.name)]


def answer_offer(player:Player, accept:bool,
                 repository:Any) -> list[Message]:
    offer = player.profile.pop("house_offer", None)
    if offer is None:
        repository.save(player)
        return private("Nobody has invited you.", player)
    owner = repository.load_by_id(offer["from_id"])
    home = home_of(owner, offer["town"]) if owner is not None else None
    if home is None:
        repository.save(player)
        return private("That invitation is no longer valid.", player)
    if not accept:
        repository.save(player)
        return [Message(f"You decline {owner.name}'s invitation.",
                        player.name),
                Message(f"{player.name} declines your invitation.",
                        owner.name)]
    player.profile["where"] = "home"
    player.profile["home_host"] = owner.id
    repository.save(player)
    if offer["kind"] == "movein":
        return move_in(owner, home, player, repository, True)
    return invite(owner, home, player, repository, offer.get("mode", ""))


def consented(player:Player, other:Player) -> bool:
    stamp = other.profile.get("sex_ok", {}).get(player.id, 0)
    return (player.profile.get("home_sex") == other.name
            and time.time() - stamp < HOUSE_CONSENT_SECONDS)


def ask_consent(player:Player, other:Player, word:str, args:list[str],
                repository:Any) -> list[Message]:
    other.profile["sex_offer"] = {
        "from_id": player.id, "from": player.name, "word": word,
        "args": args}
    repository.save(other)
    return [Message(f"📨 You ask {other.name} for intimacy. "
                    f"{other.name} has to confirm on their own screen.",
                    player.name),
            Message(f"📨 {player.name} asks you for something intimate. "
                    f"Confirm with [home accept] or [home decline].",
                    other.name)]


def answer_consent(player:Player, accept:bool,
                   repository:Any) -> list[Message]:
    offer = player.profile.pop("sex_offer", None)
    asker = repository.load_by_id(offer["from_id"])
    if asker is None:
        repository.save(player)
        return private("That request is no longer valid.", player)
    if not accept:
        repository.save(player)
        return [Message(f"You decline {asker.name}.", player.name),
                Message(f"{player.name} declines.", asker.name)]
    player.profile.setdefault("sex_ok", {})[asker.id] = time.time()
    player.profile["home_sex"] = asker.name
    asker.profile["home_sex"] = player.name
    repository.save(player)
    repository.save(asker)
    return [Message(f"💞 You agree to {asker.name}. Pick what you want in "
                    f"the Sex tab.", player.name),
            Message(f"💞 {player.name} agrees. You take "
                    f"{player.first_name or player.name} to the bedroom.",
                    asker.name)]


def invite_all(player:Player, home:dict[str, Any], repository:Any,
               regulars:Any, mode:str="", away_of:Any=None,
               town:str=START_TOWN) -> list[Message]:
    guests = [guest for guest in invitees(player, home, repository, regulars)
              if not (away_of is not None and not guest.npc
                      and not is_regular(guest)
                      and away_of(guest) in BUSY_PLACES)]
    if not guests:
        return private("There is nobody left to invite.", player)
    lines: list[str] = []
    extra: list[Message] = []
    for guest in guests:
        if occupants(home) + len(home["guests"]) >= capacity(home):
            lines.append("The house is full.")
            break
        saver = SavingOnly(repository) if is_regular(guest) else repository
        if is_hero(guest):
            asked = offer_to(player, home, guest, "invite", mode,
                             repository, town)
            lines.append(asked[0].text)
            extra += asked[1:]
            continue
        lines += [message.text for message in
                  invite(player, home, guest, saver, mode)]
    return [Message("\n".join(lines))] + extra


def send_everyone_home(player:Player, home:dict[str, Any],
                       repository:Any) -> list[Message]:
    names = [entry["name"] for entry in home["guests"]]
    if not names:
        return private("Nobody to send home. Residents stay – use "
                       "[home leave <name>] for them.", player)
    home["guests"] = []
    repository.save(player)
    return [Message(f"{', '.join(names)} head home for the night.")]


def move_in(player:Player, home:dict[str, Any], other:Player,
            repository:Any, force:bool=False) -> list[Message]:
    if is_regular(other):
        return private(f"{other.name} only comes over as a guest.", player)
    if any(entry["id"] == other.id for entry in home["residents"]):
        return private(f"{other.name} already lives here.", player)
    if occupants(home) >= capacity(home):
        return private("The house has no free bed.", player)
    invited = any(entry["id"] == other.id for entry in home["guests"])
    if not force and not (invited and not other.npc) and not trusted(
            player, other):
        return private(f"{other.name} would only move in as family or a "
                       f"close friend.", player)
    home["guests"] = [entry for entry in home["guests"]
                      if entry["id"] != other.id]
    home["residents"].append({"id": other.id, "name": other.full_name})
    repository.save(player)
    if not is_regular(other):
        note_residence(other, player, home, home["town"], repository)
    messages = [Message(f"📦 {other.full_name} moves into {player.name}'s "
                        f"house{role_note(player, other)}.")]
    if not other.npc and not is_regular(other):
        messages.append(Message(
            f"📦 You move into {player.name}'s house. It is your home "
            f"now: [home sleep] rests you there.", other.name))
    return messages


def leave(player:Player, home:dict[str, Any], other:Player,
          repository:Any) -> list[Message]:
    before = len(home["residents"]) + len(home["guests"])
    home["residents"] = [entry for entry in home["residents"]
                         if entry["id"] != other.id]
    home["guests"] = [entry for entry in home["guests"]
                      if entry["id"] != other.id]
    if before == len(home["residents"]) + len(home["guests"]):
        return private(f"{other.name} is not in your house.", player)
    repository.save(player)
    if (other.profile.get("lodging", {}).get(home["town"]) == home["id"]
            and not is_regular(other)):
        other.profile["lodging"].pop(home["town"], None)
        other.profile.pop("home_host", None)
        repository.save(other)
    bye = title_for(home, player, other, "bye", random.Random())
    return [Message(f"{other.full_name} leaves the house."
                    + (f"\n{bye}" if bye else ""))]


def talk(player:Player, other:Player, repository:Any,
         rng:random.Random, regulars:Any=None,
         topic:str="") -> list[Message]:
    if is_regular(other):
        return private(regular_chat(other, regulars, rng), player)
    if other.npc:
        messages = chat(player, other, topic, rng)
        repository.save(other)
        return messages
    return banter(player, other, topic, rng)


def called(messages:list[Message], home:dict[str, Any], player:Player,
           other:Player, kind:str, rng:random.Random) -> list[Message]:
    line = title_for(home, player, other, kind, rng)
    if line and messages:
        first = messages[0]
        messages[0] = Message(f"{first.text}\n{line}", first.recipient)
    return messages


def stored_mode(home:dict[str, Any], other:Player) -> str:
    for entry in home["residents"] + home["guests"]:
        if entry["id"] == other.id:
            return entry.get("mode", "")
    return ""


def intimate(player:Player, other:Player, home:dict[str, Any],
             repository:Any, rng:random.Random,
             options:dict[str, str] | None=None,
             mode:str="") -> list[Message]:
    if min(player.age, other.age) < INTIMACY_MIN_AGE:
        return private(f"{other.name} is not available.", player)
    if (other.npc and not is_regular(other)
            and friendship(other, player) < HOUSE_MATE_POINTS):
        return private(f"{other.first_name} smiles politely. 'Not yet.'",
                       player)
    mode = mode or stored_mode(home, other)
    if mode == "throne":
        return throne_scene(player, other, repository, rng,
                            title_line(home, player, other, rng))
    if mode == "seat":
        return seat_scene(player, other, repository, rng,
                          title_line(home, player, other, rng))
    messages = romance_scene(player, other, repository, rng,
                             with_mode(options or dict(DEFAULTS), mode))
    intro = mode_intro(mode, other)
    detail = partner_line("romance", (options or DEFAULTS)["role"], player,
                          other, rng)
    intro = f"{intro}\n{detail}" if intro else detail
    called = title_line(home, player, other, rng)
    tail = f"\n{called}" if called else ""
    messages[0] = Message(f"{intro}\n{messages[0].text}{tail}")
    opener = family_open(player, other, rng)
    if opener:
        messages[0] = Message(f"{opener}\n{messages[0].text}\n"
                              f"{family_close(player, other, rng)}")
    if other.pregnant and not is_regular(other):
        expecting = home.setdefault("expecting", [])
        if other.id not in expecting:
            expecting.append(other.id)
            repository.save(player)
    return messages


CHEST_WORDS = ("chest", "store", "take")
CHEST_USAGE = ("[home store <nr>|gold <n>|gold all] and "
               "[home take <nr>|gold <n>|gold all]")


def chest_command(player:Player, args:list[str], account:Any,
                  in_run:bool, on_shift:bool, town:str) -> list[Message]:
    if in_run:
        return private("Your house is far away while you are in the "
                       "dungeon.", player)
    if on_shift:
        return private("Not during a shift.", player)
    if account is None:
        return private("You have no house here, so no chest either.",
                       player)
    word = args[0].casefold()
    if word == "chest":
        return bank_menu(player, account, "📦 Home chest", CHEST_USAGE)
    return bank_move(player, account, args[1:], word == "store", False)


class HostSaving:
    def __init__(self, repository:Any, player:Player, host:Player) -> None:
        self.repository = repository
        self.player = player
        self.host = host

    def __getattr__(self, name:str) -> Any:
        return getattr(self.repository, name)

    def save(self, target:Any) -> Any:
        result = self.repository.save(target)
        if target is self.player:
            self.repository.save(self.host)
        return result


BUSY_PLACES = ("cafe", "brothel", "tavern", "dungeon")
PLACE_TEXT = {"home": "at home", "cafe": "at the Fat Ass Café", "brothel": "at the Rose Chamber",
              "tavern": "at the tavern", "dungeon": "down in the dungeon",
              "bank": "at the bank", "maidschool": "at the maid school",
              "tuning_room": "at the Tuning Room",
              "post_office": "at the post office",
              "town": "out in town", "station": "at the station"}


def away_note(other:Player, away_of:Any) -> str:
    if away_of is None or other.npc or is_regular(other):
        return ""
    place = away_of(other)
    if not place or place == "home":
        return ""
    return (f"{other.name} is not home right now – "
            f"{PLACE_TEXT.get(place, place)}.")


def hosted_by(player:Player, town:str, repository:Any) -> Player | None:
    host_id = player.profile.get("home_host")
    if not host_id:
        return None
    host = repository.load_by_id(host_id)
    home = home_of(host, town) if host is not None else None
    if home is not None and any(
            entry["id"] == player.id
            for entry in home["residents"] + home["guests"]):
        return host
    player.profile.pop("home_host", None)
    return None


def home_partner(player:Player, town:str, repository:Any,
                 regulars:Any) -> Player | None:
    name = player.profile.get("home_sex", "")
    if not name:
        return None
    host = hosted_by(player, town, repository)
    home = home_of(host, town) if host is not None else home_of(player, town)
    if home is None:
        host = shared_host(player, town, repository)
        home = home_of(host, town) if host is not None else None
    if home is None:
        return None
    other = lookup(player, repository, name, home, regulars)
    if (other is not None and not other.npc and not is_regular(other)
            and other.profile.get("where", "home") != "home"):
        return None
    return other


def look_text(player:Player, home:dict[str, Any], rng:random.Random) -> str:
    name, _, _, description = HOUSE_TYPES[home["type"]]
    lines = [f"🏠 {name}. {description}", furnishing.describe(home)]
    people = [entry for entry in home["residents"] + home["guests"]
              if entry["id"] != player.id]
    for entry in people:
        doing = rng.choice(DOING["visitor"]).format(their="their")
        lines.append(f"{entry['name']} is {doing}.")
    if not people:
        lines.append("Nobody else is here.")
    return "\n".join(lines)


def furnish_command(player:Player, owner:Player, home:dict[str, Any],
                    word:str, args:list[str],
                    repository:Any) -> list[Message]:
    if owner is not player:
        return private("Only the owner can change the furnishing.", player)
    spot = args[0] if args else ""
    if word == "carpenter":
        messages = furnishing.order(player, spot)
    elif word == "plant":
        if len(args) < 2 or not args[1].isdigit():
            return private("Usage: plant <garden spot> <bag number>", player)
        messages = garden.plant(player, home, spot, int(args[1]))
    elif word == "water":
        messages = garden.water(player, home, spot)
    elif word == "harvest":
        messages = garden.harvest(player, home, spot, random.Random())
    elif word == "uproot":
        messages = garden.uproot(player, home, spot)
    elif word == "clear":
        messages = furnishing.clear(player, home, args[0] if args else "")
    else:
        if len(args) < 2 or not args[1].isdigit():
            return private("Usage: place <spot> <bag number>", player)
        messages = furnishing.place(player, home, args[0], int(args[1]))
    repository.save(player)
    return messages


def home_command(player:Player, args:list[str], repository:Any,
                 in_run:bool, on_shift:bool, rng:random.Random,
                 town:str=START_TOWN, regulars:Any=None,
                 regulars_of:Any=None,
                 away_of:Any=None) -> list[Message]:
    if in_run:
        return private("Your house is far away while you are in the "
                       "dungeon.", player)
    if on_shift:
        return private("Not during a shift.", player)
    word = args[0].casefold() if args else ""
    if word == "pull":
        messages = garden.pull(player)
        repository.save(player)
        return messages
    vine = player.profile.get("vine_held")
    if vine and word not in ("", "status"):
        return private(say(vine["kind"], "held_block"), player)
    options = scene_defaults(player)
    mode = ""
    kind = ""
    topic = ""
    practice_args: list[str] = []
    if word == "do":
        do_args, kind = split_activity(args[1:])
        args = [args[0]] + do_args
    use_slot = ""
    use_place = ""
    if word == "use":
        use_slot = args[1] if len(args) > 1 else ""
        args = [args[0]] + args[2:]
        if len(args) > 2 and args[-1].casefold() in ("top", "bottom"):
            use_place = args.pop().casefold()
    if word == "practice":
        name_words, *_ = parse_practice(args[1:])
        practice_args = args[1 + len(name_words):]
        args = [args[0]] + name_words
    if word == "talk":
        talk_args = split_topic(args[1:])
        args = [args[0]] + ([talk_args[0]] if talk_args[0] else [])
        topic = talk_args[1]
    if word == "romance":
        scene_args, options = parse_options(args[1:], options)
        scene_args, mode = split_mode(scene_args)
        args = [args[0]] + scene_args
    if word == "invite":
        invite_args, mode = split_mode(args[1:])
        args = [args[0]] + invite_args
    title = ""
    if word == "order":
        order_args, title = parse_title(args[1:])
        args = [args[0]] + order_args
    rest = " ".join(args[1:])
    away_host = (hosted_by(player, town, repository)
                 if word not in ("buy", "accept", "decline", "moveout")
                 else None)
    home = None if away_host is not None else home_of(player, town)
    owner = player
    if word in ("accept", "decline"):
        if "sex_offer" in player.profile:
            return answer_consent(player, word == "accept", repository)
        return answer_offer(player, word == "accept", repository)
    if (home is not None and word != "pull"
            and not player.profile.get("pod")):
        taken = garden.neglect_take(player, home, word)
        if taken:
            repository.save(player)
            if word in ("", "status"):
                taken += private("\n".join(
                    status_lines(player, town, repository)), player)
            return taken
    if not word or word == "status":
        return private("\n".join(status_lines(player, town, repository)),
                       player)
    if word == "buy":
        return buy(player, town, rest, repository)
    if word == "sleep":
        return sleep(player, town, repository)
    if word == "moveout":
        host = shared_host(player, town, repository)
        if host is None:
            return private("You live in nobody else's house.", player)
        return leave(host, home_of(host, town), player, repository)
    if home is None:
        host = away_host or shared_host(player, town, repository)
        if host is None:
            return private("You have no house here. [home] lists the "
                           "offers.", player)
        if word == "movein":
            return private("Only the owner can let someone move in.",
                           player)
        home = home_of(host, town)
        owner = host
        repository = HostSaving(repository, player, host)
        if regulars_of is not None and word != "invite":
            regulars = regulars_of(host)
    if word in ("feed", "rescue", "offer"):
        spot = args[1] if len(args) > 1 else ""
        if word == "feed":
            messages = garden.feed(player, home, spot, rng)
        elif word == "rescue":
            messages = garden.rescue(player, home, spot, repository)
        else:
            messages = garden.offer(player, home, spot,
                                    "confirm" in args[2:])
        repository.save(player)
        return messages
    if word in ("place", "clear", "carpenter", "plant", "water", "harvest",
                "uproot"):
        return furnish_command(player, owner, home, word, args[1:],
                               repository)
    if word == "use":
        if owner is not player:
            return private("Only the owner uses the furniture.", player)
        what = furnishing.use_of(home, use_slot)
        if not what:
            return private("Usage: home use <slot> [name]. That spot has "
                           "nothing to use.", player)
        if what == "bath":
            return bath_use(player, home, use_slot, repository)
    if word in ("back", "leave", "moveout", "sleep") and not rest:
        held = home_scene.bound_text(player, repository)
        if held:
            return private(held, player)
    if word == "back":
        mate = lookup(player, repository, player.profile.get("home_sex", ""),
                      home, regulars) if player.profile.get("home_sex") else None
        if mate is not None and is_hero(mate) and (
                mate.profile.get("home_sex") == player.name):
            mate.profile.pop("home_sex", None)
            repository.save(mate)
        player.profile.pop("home_sex", None)
        repository.save(player)
        return private("You leave the bedroom and return to the rooms.",
                       player)
    if word in ("answer", "lift", "breathe", "act"):
        return home_scene.scene_command(
            word, player, home, repository, rng,
            args[1].casefold() if len(args) > 1 else "")
    if word in ("look", "examine"):
        if not rest:
            return private(look_text(player, home, rng), player)
        target = lookup(player, repository, rest, home, regulars)
        if target is None or not (
                target.id == home["owner"] or any(
                    entry["id"] == target.id
                    for entry in home["residents"] + home["guests"])):
            return private(f"Nobody called '{rest}' is in this house.",
                           player)
        kind = ("owner" if target.id == home["owner"] else "visitor")
        return private(describe_person(
            {"kind": kind, "name": target.name}, target, {"building": ""},
            rng), player)
    if word == "invite" and rest.casefold() == "all":
        return invite_all(owner, home, repository, regulars, mode,
                          away_of, town)
    if word == "leave" and rest.casefold() in ("all", "everyone"):
        return send_everyone_home(player, home, repository)
    other = (lookup(player, repository, rest, home, regulars)
             if rest else None)
    if other is None:
        if rest:
            return private(
                f"Nobody called '{rest}' is here or could come: regulars "
                f"need {VISIT_ASK_VISITS}+ visits and a known address, "
                f"town people need to trust you.", player)
        return private(f"Usage: home {word} <name>", player)
    gone = away_note(other, away_of)
    if gone and word not in ("leave", "movein", "invite"):
        return private(gone, player)
    if gone and word in ("movein", "invite") and (
            away_of(other) in BUSY_PLACES):
        return private(gone, player)
    if word in ("invite", "movein") and is_hero(other):
        return offer_to(owner, home, other, word, mode, repository, town)
    if other.records.get(CAFE_LOCK) and not is_regular(other):
        return private(f"{other.name} is gone for this round – they were "
                       f"swallowed or crushed at the café.", player)
    if is_regular(other):
        repository = SavingOnly(repository)
    if word == "invite":
        return invite(player, home, other, repository, mode)
    if word == "order" and is_hero(other) and title:
        return home_scene.order_hero(player, other, home, title,
                                     repository, rng)
    if word == "order":
        if not any(entry["id"] == other.id
                   for entry in home["residents"] + home["guests"]):
            return private(f"{other.name} is not in your house.", player)
        return order_title(player, home, other, title, repository, rng)
    if word == "movein":
        return move_in(player, home, other, repository)
    if word == "leave":
        return leave(player, home, other, repository)
    here = False
    for entry in home["residents"] + home["guests"] + [
            {"id": owner.id}]:
        if entry["id"] == other.id and (other is not player):
            entry["seen"] = time.monotonic()
            here = True
    if not here:
        return private(f"{other.name} is not in your house.", player)
    if word in ("sex", "practice", "romance", "use") and is_hero(other):
        for person in (player, other):
            if home_scene.knocked_out(person):
                return private(f"{person.name} is out cold.", player)
    if (word in ("sex", "practice", "romance", "use") and is_hero(other)
            and not consented(player, other)):
        if player.profile.get("sex_offer", {}).get("from_id") == other.id:
            return answer_consent(player, True, repository)
        mode = consent_of(other)
        if mode == "deny":
            return private(f"{other.name} does not accept this right "
                           f"now.", player)
        if mode == "allow":
            ask_consent(player, other, word, args[1:], repository)
            return answer_consent(other, True, repository)
        return ask_consent(player, other, word, args[1:], repository)
    if word == "talk":
        return called(talk(player, other, repository, rng, regulars,
                           topic), home, player, other, "chat", rng)
    if word == "sex":
        player.profile["home_sex"] = other.name
        repository.save(player)
        return private(f"You take {other.first_name or other.name} to the "
                       f"bedroom.", player)
    if word == "practice" and not is_regular(other):
        _, act, role, options, direction = parse_practice(practice_args)
        if not act or not role:
            return private(PRACTICE_USAGE, player)
        return home_scene.request(player, other, home, act, role, options,
                                  direction, repository)
    if word == "practice":
        if dynamic_of(player, other, {"building": ""}) == "npc":
            _, act, role, options, direction = parse_practice(practice_args)
            chosen = pick_for(player, other, rng, True)
            if chosen is not None:
                practice_args = [chosen[0], chosen[1], options["amount"],
                                 options["where"]] + ([direction]
                                                      if direction else [])
        return home_practice(player, other, home, practice_args, repository,
                             rng)
    if word == "do":
        if not kind:
            return private("Usage: home do <name> "
                           + "|".join(ACTIVITY_WORDS), player)
        return called(activity(player, other, kind, repository, rng),
                      home, player, other, "act", rng)
    if word == "use":
        if furnishing.use_of(home, use_slot) == "bed":
            return intimate(player, other, home, repository, rng, options,
                            mode)
        return kinky_use(player, other, home, use_slot, repository, rng,
                         title_line(home, player, other, rng), use_place)
    if word == "romance":
        return intimate(player, other, home, repository, rng, options,
                        mode)
    return private("[home] shows what you can do.", player)
