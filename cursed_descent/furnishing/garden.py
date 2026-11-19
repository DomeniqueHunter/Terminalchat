import random
from typing import Any

from ..body import DEFAULT_BALLS, DEFAULT_ENDOWMENT
from ..config import HUNG_GENDERS
from ..content import ITEMS
from ..formulas import apply_buff
from ..models import Message, Player
from ..sweat import sweat_tier
from .layout import slots_of
from ..plants import PLANTS
from .plants import BLOOM, HUNGRY_AFTER, STAGES, TEXTS, WILT_AFTER, say
from .rules import irrigated, mood, neglect_days, plants_of, private, stage_of, today


NEGLECT_SAFE = ("", "status", "water", "feed", "harvest", "uproot",
                "rescue", "accept", "decline", "pull")


def seed_kind(item_id:str) -> str:
    return ITEMS.get(item_id, {}).get("seed", "")


def seeds(player:Player) -> list[tuple[int, str]]:
    return [(number, item) for number, item in
            enumerate(player.inventory, 1) if seed_kind(item) in PLANTS]


def state_text(state:dict[str, Any]) -> str:
    plant = PLANTS[state["kind"]]
    if state.get("wilted"):
        return f"{plant['name']} (wilted)"
    return f"{plant['name']} ({STAGES[stage_of(state)]})"


def plant(player:Player, home:dict[str, Any], slot:str,
          number:int) -> list[Message]:
    kinds = slots_of(home["type"])
    if kinds.get(slot) != "plant":
        return private(TEXTS["no_spot"], player)
    if not 1 <= number <= len(player.inventory):
        return private("You do not carry that.", player)
    item = player.inventory[number - 1]
    if seed_kind(item) not in PLANTS:
        return private(TEXTS["no_seed"], player)
    states = plants_of(home)
    if slot in states:
        return private(TEXTS["taken"], player)
    player.inventory.pop(number - 1)
    kind = seed_kind(item)
    start = ITEMS[item].get("sprout", 0)
    states[slot] = {"kind": kind, "growth": PLANTS[kind]["need"][start],
                    "dry": 0, "watered": False, "wilted": False,
                    "tended": today()}
    return private(TEXTS["planted"].format(seed=ITEMS[item]["name"],
                                           spot="garden"), player)


def feed_block(player:Player, kind:str) -> str:
    rules = PLANTS[kind]["feed"]
    if player.gender not in HUNG_GENDERS:
        return "feed_no_body"
    body = player.body
    if (body.get("endowment", DEFAULT_ENDOWMENT) < rules["min_endowment"]
            or body.get("balls", DEFAULT_BALLS) < rules["min_balls"]):
        return "feed_small"
    if sweat_tier(player) < rules["min_sweat_tier"]:
        return "feed_dry"
    return ""


def feed_open(player:Player, state:dict[str, Any]) -> bool:
    return (not state["wilted"]
            and not state.get("victim") and not state.get("pod")
            and not player.profile.get("vine_held")
            and player.id not in state.get("fed_by", [])
            and not feed_block(player, state["kind"]))


def feed(player:Player, home:dict[str, Any], slot:str,
         rng:random.Random | None=None) -> list[Message]:
    rng = rng or random.Random()
    state = plants_of(home).get(slot)
    if state is None:
        return private(TEXTS["nothing"], player)
    if state.get("victim") or state.get("pod"):
        return private(TEXTS["occupied"], player)
    if state["wilted"]:
        return private(say(state["kind"], "feed_wilted"), player)
    if player.id in state.get("fed_by", []):
        return private(say(state["kind"], "feed_done"), player)
    blocked = feed_block(player, state["kind"])
    if blocked:
        return private(say(state["kind"], blocked), player)
    rules = PLANTS[state["kind"]]["feed"]
    player.sweat = 0
    state.setdefault("fed_by", []).append(player.id)
    state.update(watered=True, hungry=0, tended=today())
    lines = [say(state["kind"], "feed")]
    pulls = PLANTS[state["kind"]].get("hold", {}).get(stage_of(state), 0)
    if pulls:
        player.profile["vine_held"] = {"kind": state["kind"], "left": pulls}
        lines.append(say(state["kind"], "held"))
    if (stage_of(state) >= rules["store_from"]
            and state.get("stored", 0) < rules["store_cap"]):
        state["stored"] = state.get("stored", 0) + 1
        lines.append(say(state["kind"], "feed_store"))
    lines.extend(soothe(player, state["kind"]))
    if "home_afterglow" not in player.buffs:
        apply_buff(player, "home_afterglow")
    if (can_swallow(state) and rng.random()
            < PLANTS[state["kind"]]["neglect"]["seduce"]):
        lines.append(swallow(player, home, slot, "seduce"))
    return private("\n".join(lines), player)


def can_swallow(state:dict[str, Any]) -> bool:
    return (not state["wilted"] and not state.get("victim")
            and not state.get("pod") and "neglect" in PLANTS[state["kind"]]
            and stage_of(state) == len(STAGES) - 1)


def swallow(player:Player, home:dict[str, Any], slot:str, how:str) -> str:
    state = plants_of(home)[slot]
    days = PLANTS[state["kind"]]["neglect"]["rescue"]
    state["victim"] = {"id": player.id, "name": player.name,
                       "until": today() + days}
    player.profile["pod"] = {"house": home["id"], "town": home["town"],
                             "slot": slot}
    player.profile.pop("vine_held", None)
    player.profile.pop("offer_ask", None)
    return say(state["kind"], how)


def offer(player:Player, home:dict[str, Any], slot:str,
          confirm:bool) -> list[Message]:
    state = plants_of(home).get(slot)
    if state is None:
        return private(TEXTS["nothing"], player)
    if not can_swallow(state):
        return private(TEXTS["offer_no"], player)
    if not confirm or player.profile.get("offer_ask") != slot:
        player.profile["offer_ask"] = slot
        return private(say(state["kind"], "offer_ask"), player)
    return private(swallow(player, home, slot, "offer"), player)


def neglect_take(player:Player, home:dict[str, Any],
                 word:str) -> list[Message]:
    hungry = [(slot, state) for slot, state in plants_of(home).items()
              if mood(state) == "evil"]
    if not hungry:
        player.profile.pop("plant_warned", None)
        return []
    slot, state = hungry[0]
    if word in NEGLECT_SAFE and word not in ("", "status"):
        return []
    if player.profile.get("plant_warned") != today() or word in (
            "", "status"):
        player.profile["plant_warned"] = today()
        return private(say(state["kind"], "warn_take"), player)
    return private(swallow(player, home, slot, "take"), player)


def rescue(player:Player, home:dict[str, Any], slot:str,
           repository:Any) -> list[Message]:
    state = plants_of(home).get(slot)
    victim = state.get("victim") if state else None
    if not victim:
        return private(TEXTS["nobody"], player)
    if victim["id"] == player.id:
        return private(TEXTS["no_self_rescue"], player)
    state.pop("victim")
    state["tended"] = today()
    values = {"rescuer": player.name, "name": victim["name"]}
    messages = private(say(state["kind"], "rescue").format(**values),
                       player)
    person = repository.load_by_id(victim["id"])
    if person is not None:
        person.profile.pop("pod", None)
        repository.save(person)
        messages.append(Message(say(state["kind"], "rescued").format(
            **values), person.name))
    return messages


def expired(repository:Any, store:Any) -> list[tuple[Player, dict, dict]]:
    day = store.day()
    found = []
    for name in repository.names():
        player = repository.load(name)
        pod = player.profile.get("pod") if player is not None else None
        if not pod:
            continue
        home = store.get(pod["house"], pod["town"])
        state = plants_of(home).get(pod["slot"]) if home else None
        victim = state.get("victim") if state else None
        if victim and victim["id"] == player.id and day < victim["until"]:
            continue
        found.append((player, home, state))
    return found


def devour(player:Player, state:dict[str, Any] | None,
           rng:random.Random) -> str:
    player.profile.pop("pod", None)
    if not state or not state.get("victim"):
        return ""
    state.pop("victim")
    kinds = PLANTS[state["kind"]]["pod_kinds"]
    state["pod"] = {"name": player.name, "id": player.id,
                    "variant": rng.choice(kinds)}
    return say(state["kind"], "dead")


def harvest_pod(player:Player, state:dict[str, Any],
                rng:random.Random) -> list[Message]:
    if len(player.inventory) + 3 > player.bag_size:
        return private(TEXTS["full"], player)
    kind = PLANTS[state["kind"]]
    pod = state.pop("pod")
    lines = [say(state["kind"], "pod_harvest")]
    player.inventory.append(f"pod_{pod['variant']}")
    lines.append(f"You take the {ITEMS['pod_' + pod['variant']]['name']}.")
    if rng.random() < 0.5:
        player.inventory.append("pod_goo")
        lines.append(f"You also get {ITEMS['pod_goo']['name']}.")
    if rng.random() < 0.4:
        player.inventory.append("pod_seed")
        lines.append(f"You also get {ITEMS['pod_seed']['name']}.")
    state.update(growth=kind["need"][kind["regrow"]], watered=False,
                 hungry=0, stored=0, tended=today())
    return private("\n".join(lines), player)


def pull(player:Player) -> list[Message]:
    held = player.profile.get("vine_held")
    if not held:
        return private(TEXTS["not_held"], player)
    held["left"] -= 1
    if held["left"] > 0:
        return private(say(held["kind"], "pull"), player)
    player.profile.pop("vine_held")
    return private(say(held["kind"], "freed"), player)


def progress_text(state:dict[str, Any]) -> str:
    victim = state.get("victim")
    if victim:
        return (f"{victim['name']} is inside. "
                f"{max(0, victim['until'] - today())} days left.")
    if state.get("pod"):
        return "A pod hangs on the vine. Harvest it, or leave it."
    if state["wilted"]:
        return "Wilted. Water it to revive it."
    need = PLANTS[state["kind"]]["need"]
    stage = stage_of(state)
    if stage < len(need) - 1:
        span = need[stage + 1] - need[stage]
        done = state["growth"] - need[stage]
        parts = [f"{STAGES[stage]} {'▓' * done}{'░' * (span - done)} "
                 f"{state['growth']}/{need[stage + 1]} → "
                 f"{STAGES[stage + 1]}"]
    else:
        parts = [f"{STAGES[stage]} ▓▓▓▓ fully grown"]
    parts.append("watered" if state["watered"] else "thirsty")
    if state.get("fed_by"):
        parts.append(f"fed x{len(state['fed_by'])}")
    if state["dry"]:
        parts.append(f"dry {state['dry']}/{WILT_AFTER}")
    if state.get("hungry"):
        parts.append(f"hungry {state['hungry']}/{HUNGRY_AFTER}")
    if state.get("stored"):
        parts.append(f"{state['stored']} nectar stored")
    if mood(state):
        parts.append(f"neglected {neglect_days(state)} days")
    return " · ".join(parts)


def soothe(player:Player, kind:str) -> list[str]:
    if "home_drained" not in player.buffs:
        return []
    player.buffs.remove("home_drained")
    return [say(kind, "drained_off")]


def water(player:Player, home:dict[str, Any], slot:str) -> list[Message]:
    state = plants_of(home).get(slot)
    if state is None:
        return private(TEXTS["nothing"], player)
    name = PLANTS[state["kind"]]["name"]
    if state.get("victim") or state.get("pod"):
        return private(TEXTS["occupied"], player)
    if state["wilted"]:
        state.update(wilted=False, dry=0, watered=True, tended=today())
        return private(say(state["kind"], "revive").format(plant=name),
                       player)
    if state["watered"]:
        return private(TEXTS["watered"].format(plant=name), player)
    state.update(watered=True, tended=today())
    return private(TEXTS["water"].format(plant=name), player)


def harvest(player:Player, home:dict[str, Any], slot:str,
            rng:random.Random) -> list[Message]:
    state = plants_of(home).get(slot)
    if state is None:
        return private(TEXTS["nothing"], player)
    kind = PLANTS[state["kind"]]
    if state.get("victim"):
        return private(TEXTS["occupied"], player)
    if state.get("pod"):
        return harvest_pod(player, state, rng)
    if state["wilted"]:
        return private(TEXTS["wilted"], player)
    if stage_of(state) < BLOOM:
        return private(TEXTS["not_ready"].format(
            plant=kind["name"], stage=STAGES[stage_of(state)]), player)
    overgrown = stage_of(state) == len(STAGES) - 1
    amount = rng.randint(*kind["nectar_overgrown" if overgrown
                              else "nectar"]) + state.get("stored", 0)
    extra = rng.random() < kind["seed_chance"]
    if len(player.inventory) + amount + extra > player.bag_size:
        return private(TEXTS["full"], player)
    lines = [say(state["kind"], "harvest")]
    player.inventory += [kind["nectar_item"]] * amount
    lines.append(f"You gather {amount}x "
                 f"{ITEMS[kind['nectar_item']]['name']}.")
    if extra:
        player.inventory.append(kind["seed_item"])
        lines.append(say(state["kind"], "seed"))
    state.update(growth=kind["need"][kind["regrow"]], watered=False,
                 hungry=0, stored=0, tended=today())
    lines.extend(soothe(player, state["kind"]))
    return private("\n".join(lines), player)


def uproot(player:Player, home:dict[str, Any], slot:str) -> list[Message]:
    states = plants_of(home)
    if slot not in states:
        return private(TEXTS["nothing"], player)
    if states[slot].get("victim"):
        return private(TEXTS["occupied"], player)
    kind = states.pop(slot)["kind"]
    name = PLANTS[kind]["name"]
    return private("\n".join([TEXTS["uproot"].format(plant=name)]
                              + soothe(player, kind)), player)


def grow(home:dict[str, Any]) -> None:
    pipes = irrigated(home)
    for state in plants_of(home).values():
        kind = PLANTS[state["kind"]]
        if state["wilted"]:
            continue
        fed = len(state.get("fed_by", []))
        if state["watered"]:
            top = kind["need"][-1]
            state["growth"] = min(top, state["growth"] + 1 + min(fed, 2))
            state["dry"] = 0
        elif not pipes:
            state["dry"] += 1
            if state["dry"] >= WILT_AFTER:
                state["wilted"] = True
        if stage_of(state) == len(STAGES) - 1 and not fed:
            state["hungry"] = state.get("hungry", 0) + 1
        state["fed_by"] = []
        state["watered"] = False
