import json
import random
import uuid
from dataclasses import dataclass
from pathlib import Path

from .content import AROMAS, BASE_HEAL, BATH_DONE, BREW_DONE, KEY, STYLES
from .content import HIDDEN_JOBS
from .sisters import (
    BOIL_DEATH, BOIL_ESCAPE, BOIL_SURVIVE, DEAD_LOCK, SISTERS, TEMPS,
    SERVICE, SERVICE_FIT, SERVICE_HELP, TOO_HEAVY, UNDRESS, VAT_INTRO,
    VATS, VORE, VORE_DEATH, VORE_HELP,
)


LOCKER = "brewhouse_locker"
BOOT_SLOT = "feet"
VORE_CHANCE = 0.10
HOT_HURT_CHANCE = 0.15
HOT_HURT_SHARE = 0.04
BOIL_DEATH_CHANCE = 0.35
VORE_DEATH_BASE = 0.4
SURE_OFFER_ROUND = 2
VORE_DEATH_MAX = 0.8
ESCAPE_BASE = 0.3
GROWTH_PER_LIMIT_KG = 8
FREE_GROWTH = 8
STAGES = (2, 4, 6)
STORE = {"path": None}


@dataclass
class BrewState:
    services: object
    town: str
    temp: str
    vat: str
    kind: str = "bath"
    pending: str = ""
    last_action: str = ""
    relax: int = 0
    struggle: int = 0
    eager: int = 0
    rounds: int = 0
    offered: bool = False
    outcome: str = ""


def town_of_player(player) -> str:
    from ...towns import town_key
    key = town_key(player)
    return key if key in SISTERS else "last_light"


def sister_player(services, town:str):
    for npc in services.repository.npc_players():
        if (npc.profile.get("town") == town
                and npc.profile.get("building") == KEY):
            return npc
    return None


def grown(services, town:str) -> int:
    sister = sister_player(services, town)
    if sister is None:
        return 0
    return sister.body.get("balls", SISTERS[town]["start_balls"]) - (
        SISTERS[town]["start_balls"])


def limit_kg(services, town:str) -> float | None:
    steps = grown(services, town)
    if steps >= FREE_GROWTH:
        return None
    return SISTERS[town]["limit"] + steps * GROWTH_PER_LIMIT_KG


def fits(services, player, town:str) -> bool:
    limit = limit_kg(services, town)
    return limit is None or player.body.get("weight", 70) <= limit


def stage_of(steps:int) -> int:
    return sum(1 for step in STAGES if steps >= step)


def undress(player) -> None:
    dress(player)
    locker = {slot: item_id for slot, item_id in player.equipment.items()
              if item_id and slot != BOOT_SLOT}
    for slot in locker:
        player.equipment[slot] = None
    player.profile[LOCKER] = locker


def dress(player) -> None:
    locker = player.profile.pop(LOCKER, {})
    for slot, item_id in locker.items():
        if player.equipment.get(slot) is None:
            player.equipment[slot] = item_id
        else:
            player.inventory.append(item_id)


def idle_hook(player) -> None:
    if player.profile.get(LOCKER):
        dress(player)


def pick_temp(rng:random.Random) -> str:
    names = list(TEMPS)
    return rng.choices(names, [TEMPS[name][0] for name in names])[0]


def start(services, player, job_key:str):
    from ...models import Message
    from ...config import WORK_TICK_SECONDS
    from ..work.model import Shift
    town = town_of_player(player)
    cfg = SISTERS[town]
    if player.name in services.shifts:
        return [Message("Finish your current shift first.", player.name)]
    if job_key == "vore" and not fits(services, player, town):
        return [Message(TOO_HEAVY.format(sister=cfg["name"]), player.name)]
    if job_key == "service" and fits(services, player, town):
        return [Message(SERVICE_FIT.format(sister=cfg["name"]),
                        player.name)]
    job = HIDDEN_JOBS[job_key]
    rng = services.rng
    temp = pick_temp(rng)
    state = BrewState(services, town, temp, rng.choice(VATS[town]),
                      kind=job_key)
    undress(player)
    shift = Shift(KEY, job, job.sessions, due=services.now + (
        WORK_TICK_SECONDS), mode=temp, client=state)
    services.shifts[player.name] = shift
    if job_key == "service":
        return [Message(f"{UNDRESS.format(sister=cfg['name'])}\n"
                        f"{SERVICE[town]['start']}\n"
                        f"{SERVICE_HELP}. {job.sessions} rounds.",
                        player.name)]
    if job_key == "vore":
        return [Message(f"{UNDRESS.format(sister=cfg['name'])}\n"
                        f"{VORE[town]['swallow']}\n{VORE_HELP}. "
                        f"{job.sessions} rounds.", player.name)]
    extra = (" The sister may make you an offer at the end of a round:"
             " watch the vat box in the panel.")
    lines = [UNDRESS.format(sister=cfg["name"]),
             VAT_INTRO.format(sister=cfg["name"], temp=temp, vat=state.vat,
                              temp_line=TEMPS[temp][2], title=job.title.lower(),
                              rounds=job.sessions, extra=extra)]
    return [Message("\n".join(lines), player.name)]


def start_bath(services, player, offer):
    return start(services, player, "bath")


def start_vore(services, player, offer):
    return start(services, player, "vore")


def start_service(services, player, offer):
    return start(services, player, "service")


def kill(player, text:str, fate:str="brewed") -> None:
    from ...config import CAFE_LOCK
    player.deaths[fate] = player.deaths.get(fate, 0) + 1
    player.last_fate = fate
    player.last_fate_text = text
    player.records[CAFE_LOCK] = 1


def resolve_boil(player, shift, state, rng:random.Random,
                 choice:str) -> None:
    state.pending = ""
    shift.earned = 0
    if choice == "escape":
        stats = player.stats
        chance = min(0.9, ESCAPE_BASE + (stats.get("agility", 5)
                                         + stats.get("strength", 5)) / 200)
        if rng.random() < chance:
            state.outcome = "escaped"
            player.hp = max(1, player.hp // 2)
            return
    if rng.random() < BOIL_DEATH_CHANCE:
        state.outcome = "dead"
        kill(player, BOIL_DEATH.format(sister=SISTERS[state.town]["name"],
                                       name=player.name))
        return
    state.outcome = "survived"
    player.hp = 1


def round_hook(player, shift, rng:random.Random) -> list[str]:
    state = shift.client
    if not isinstance(state, BrewState):
        return []
    cfg = SISTERS[state.town]
    lines = []
    state.rounds += 1
    if state.pending == "boil":
        resolve_boil(player, shift, state, rng, "endure")
        shift.left = 1
        return [f"   ✦ {outcome_line(state, player)}"]
    state.pending = ""
    if state.kind == "service":
        action = state.last_action or "gentle"
        state.last_action = ""
        return [f"   ✦ {SERVICE[state.town][action]}"]
    if state.kind == "vore":
        action = state.last_action or "relax"
        lines.append(f"   ✦ {VORE[state.town]['inside'][action]}")
        state.last_action = ""
        return lines
    if state.temp == "hot" and rng.random() < HOT_HURT_CHANCE:
        from ..offers import hurt
        lines.append(f"   ✦ The hot vat scalds you: -"
                     f"{hurt(player, HOT_HURT_SHARE)} HP.")
    if rng.random() < cfg["boil_chance"]:
        state.pending = "boil"
        lines.append(f"   ✦ {cfg['boil']} Decide in the vat box.")
    elif fits(state.services, player, state.town) and (
            rng.random() < VORE_CHANCE
            or (state.rounds >= SURE_OFFER_ROUND and not state.offered)):
        state.pending = "offer"
        state.offered = True
        lines.append(f"   ✦ {cfg['ask'].format(name=player.name)}")
    return lines


def outcome_line(state:BrewState, player) -> str:
    cfg = SISTERS[state.town]
    return {"escaped": BOIL_ESCAPE, "survived": BOIL_SURVIVE,
            "dead": BOIL_DEATH}[state.outcome].format(
        sister=cfg["name"], name=player.name)


def vat_command(services, player, args):
    from ...models import Message
    shift = services.shifts.get(player.name)
    state = shift.client if shift is not None else None
    if not isinstance(state, BrewState):
        return [Message("You are not in a vat. Pick an offer at the "
                        "brewhouse counter.", player.name)]
    word = args[0].casefold() if args else ""
    cfg = SISTERS[state.town]
    rng = services.rng
    if word in ("yes", "no") and state.pending == "offer":
        state.pending = ""
        if word == "no":
            return [Message(f"{cfg['name']} shrugs. 'Another time.'",
                            player.name)]
        job = HIDDEN_JOBS["vore"]
        shift.job = job
        shift.left = job.sessions
        state.kind = "vore"
        return [Message(VORE[state.town]["swallow"] + " "
                        + f"{VORE_HELP}.", player.name)]
    if word in ("escape", "endure") and state.pending == "boil":
        resolve_boil(player, shift, state, rng, word)
        from ..work.jobs import finish
        del services.shifts[player.name]
        return finish(player, shift)
    if word in ("gentle", "eager", "deep") and state.kind == "service":
        state.last_action = word
        state.eager += {"gentle": 0, "eager": 1, "deep": 2}[word]
        return [Message(SERVICE[state.town][word], player.name)]
    if word in ("relax", "struggle", "squirm") and state.kind == "vore":
        state.last_action = word
        if word == "relax":
            state.relax += 1
        elif word == "struggle":
            state.struggle += 1
        return [Message(VORE[state.town]["inside"][word], player.name)]
    return [Message(f"Nothing to answer with [vat {word}] right now.",
                    player.name)]


def vat_actions(state:BrewState) -> list[tuple[str, str]]:
    name = SISTERS[state.town]["name"]
    if state.pending == "boil":
        return [("Fight your way out of the vat", "escape"),
                ("Hold still and endure it", "endure")]
    if state.pending == "offer":
        return [(f"Let {name} swallow you", "yes"),
                ("Decline her offer", "no")]
    if state.kind == "vore":
        return [("Relax and let it happen", "relax"),
                ("Struggle inside her", "struggle"),
                ("Squirm", "squirm")]
    if state.kind == "service":
        return [("Lick gently", "gentle"), ("Work her eagerly", "eager"),
                ("Take her deep", "deep")]
    return []


def quality(state:BrewState) -> float:
    if state.kind == "service":
        return 1.0 + 0.15 * state.eager
    base = TEMPS[state.temp][1]
    return max(0.4, base + 0.15 * state.relax - 0.1 * state.struggle) * (
        1.5 if state.kind == "vore" else 1.0)


def register_drink(entry:dict) -> None:
    from ...content import ITEMS
    ITEMS[entry["id"]] = {
        "name": entry["name"], "slot": "consumable", "no_loot": True,
        "rarity": entry["rarity"], "heal": entry["heal"],
        "mana": entry["mana"], "price": entry["price"],
        "note": entry["note"]}


def store_path() -> Path | None:
    return STORE["path"]


def load_drinks(path:Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def setup(services) -> None:
    STORE["path"] = Path(services.data_path) / "brewhouse_drinks.json"
    for entry in load_drinks(STORE["path"]):
        register_drink(entry)


def make_drink(player, state:BrewState, label:str, rarity:str,
               factor:float) -> str:
    entry = {
        "id": f"brew_{uuid.uuid4().hex[:8]}",
        "name": label, "rarity": rarity,
        "heal": round(BASE_HEAL * 2 * factor),
        "mana": round(50 * factor), "price": round(110 * factor),
        "note": f"brewed in the {state.temp} {state.vat} vat by "
                f"{SISTERS[state.town]['name']} <<npc.astrid_last>>"}
    register_drink(entry)
    path = store_path()
    if path is not None:
        entries = load_drinks(path) + [entry]
        path.write_text(json.dumps(entries), encoding="utf-8")
    return entry["id"]


def finish_hook(player, shift) -> list:
    from ...dungeon import give_item
    from ...models import Message
    state = shift.client
    if not isinstance(state, BrewState):
        return plain_drink(player)
    dress(player)
    cfg = SISTERS[state.town]
    rng = state.services.rng
    if state.pending == "boil":
        resolve_boil(player, shift, state, rng, "endure")
    if state.outcome == "escaped":
        return [Message(BOIL_ESCAPE.format(sister=cfg["name"],
                                           name=player.name), player.name)]
    if state.outcome == "dead":
        return [Message(f"💀 {BOIL_DEATH.format(sister=cfg['name'], name=player.name)}",
                        player.name)]
    if state.outcome == "survived":
        drink = make_drink(player, state, f"{player.name}'s Reduction",
                           "epic", 2.0)
        return [Message(BOIL_SURVIVE.format(sister=cfg["name"],
                                            name=player.name) + "\n"
                        + give_item(player, drink), player.name)]
    if state.kind == "service":
        drink = make_drink(player, state,
                           f"{player.name}'s Brewmistress Cream", "epic",
                           quality(state))
        return [Message(f"{SERVICE[state.town]['done']}\n"
                        f"{give_item(player, drink)}", player.name)]
    if state.kind == "vore":
        return vore_finish(player, state, give_item)
    from ...locations.sweatery.location import dominant_feature
    aroma = AROMAS[dominant_feature(player)]
    drink = make_drink(player, state, f"{player.name}'s {aroma} {state.vat}",
                       "rare", quality(state))
    text = BATH_DONE.format(sister=cfg["name"], aroma=aroma)
    return [Message(f"{text}\n{give_item(player, drink)}", player.name)]


def vore_finish(player, state, give_item) -> list:
    from ...models import Message
    cfg = SISTERS[state.town]
    services = state.services
    sister = sister_player(services, state.town)
    chance = min(VORE_DEATH_MAX, max(0.1, VORE_DEATH_BASE - 0.1 * state.relax
                          + 0.1 * state.struggle))
    dies = services.rng.random() < chance
    lines = [VORE_DEATH[state.town].format(name=player.name) if dies
             else VORE[state.town]["release"]]
    if sister is not None:
        before = stage_of(grown(services, state.town))
        sister.body["balls"] = sister.body.get("balls", 0) + 1 + (
            1 if state.struggle >= 2 else 0)
        services.repository.save(sister)
        after = stage_of(grown(services, state.town))
        if after > before:
            lines.append(cfg["growth"][after - 1])
    if dies:
        kill(player, VORE_DEATH[state.town].format(name=player.name),
             "cummed")
        return [Message("💀 " + "\n".join(lines), player.name)]
    drink = make_drink(player, state, f"{player.name}'s Special Cream",
                       "epic", quality(state))
    lines.append(give_item(player, drink))
    return [Message("\n".join(lines), player.name)]


def plain_drink(player) -> list:
    from ...dungeon import give_item
    from ...models import Message
    key = town_of_player(player)
    sister, style = STYLES[key]
    stock = item_id(key)
    return [Message(f"{BREW_DONE.format(sister=sister, style=style)}\n"
                    f"{give_item(player, stock)}", player.name)]


def item_id(town:str) -> str:
    return f"brew_{town}_plain"


def make_items() -> dict[str, dict]:
    items = {item_id(town): {
        "name": f"Plain {style}", "slot": "consumable", "no_loot": True,
        "rarity": "common", "heal": BASE_HEAL, "mana": 0, "price": 45,
        "note": "straight from the vat"}
        for town, (_, style) in STYLES.items()}
    for town, (_, style) in STYLES.items():
        for feature, aroma in AROMAS.items():
            items[f"brew_{town}_bath_{feature}"] = {
                "name": f"{aroma} {style}", "slot": "consumable",
                "no_loot": True, "rarity": "rare",
                "heal": round(BASE_HEAL * 1.5), "mana": 40, "price": 90,
                "note": "an older bath batch"}
    return items


def greeter(player, rng:random.Random) -> str:
    cfg = SISTERS[town_of_player(player)]
    return (f"🍺 {cfg['name']} <<npc.astrid_last>> (Master Brewer) greets "
            f"{player.name}: {cfg['greeting']}")
