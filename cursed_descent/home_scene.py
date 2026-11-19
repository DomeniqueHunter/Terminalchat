import random
import time
from typing import Any, Callable

from .config import (
    HOUSE_AIR_DRAIN, HOUSE_AUTO_BEATS, HOUSE_AUTO_END, HOUSE_CRUSH_KO,
    HOUSE_KO_SECONDS,
    HOUSE_SCENE_PULSE,
)
from .home_practice import other_role, practice as home_practice
from .house_regulars import is_regular
from .house_titles import KIN_REMINDERS, REMINDERS, kin_of, titles_of
from .house_visit import pick_for
from .models import Message, Player
from .npcs.store import find_local
from .npcs.talk import town_company
from .preferences import prefs_of
from .scenes import DEFAULTS
from . import sex_overlays
from .sex_core import (
    add_heat, content_of, heat_of, mercy, obedience, rate, wish_chance,
)
from .town_buildings.brothel.practices import can_do
from .town_buildings.brothel.practices_content import ACT_LABELS


RANK = {"dom": 2, "switch": 1, "sub": 0}
AUTO: dict[str, Callable[[Player], bool]] = {"check": lambda player: False}
DEMANDS = (
    "{a} looks {b} up and down. 'From now on you call me {title}. "
    "Answer me.'",
    "'Say it,' {a} says, quietly. 'Tell me what I am to you: {title}.'",
)
SILENCE = ("{b} stays silent. {a} raises an eyebrow and lets the quiet "
           "grow: that was not the answer.")
WISH_TEXT = "{b} wishes for {act} ({role}). Only {a} decides."


def is_auto(player:Player) -> bool:
    return AUTO["check"](player)


def pair_key(first:Player, second:Player) -> str:
    return ":".join(sorted((first.id, second.id)))


def scenes_of(home:dict[str, Any]) -> dict[str, dict[str, Any]]:
    return home.setdefault("scenes", {})


def new_scene(first:Player, second:Player, wall:float) -> dict[str, Any]:
    return {"a": first.id, "b": second.id, "due": wall + HOUSE_SCENE_PULSE,
            "queue": None, "wish": None, "air": None, "smothered": "",
            "owed": None, "overlay": None, "acts": {}}


def hierarchy(first:Player, second:Player) -> tuple[Player, Player] | None:
    rank_first = RANK[prefs_of(first)["role"]]
    rank_second = RANK[prefs_of(second)["role"]]
    if rank_first == rank_second:
        return None
    return (first, second) if rank_first > rank_second else (second, first)


def both(text:str, first:Player, second:Player) -> list[Message]:
    return [Message(text, first.name), Message(text, second.name)]


def air_line(air:int) -> str:
    filled = round(air / 10)
    return f"🫁 Air {'█' * filled}{'░' * (10 - filled)} {air} %"


def boss_of(player:Player, repository:Any) -> Player | None:
    if not player.profile.get("home_sex"):
        return None
    for home in repository.houses.houses.values():
        people = house_people(home, repository)
        if player.id not in people:
            continue
        mate = mate_named(player, people)
        if mate is None or not linked(player, mate, people):
            continue
        lead = hierarchy(player, mate)
        if lead is not None and lead[1] is player:
            return lead[0]
    return None


def bound_text(player:Player, repository:Any) -> str:
    boss = boss_of(player, repository)
    if boss is None:
        return ""
    return f"{boss.name} decides when this is over. Enjoy it, endure it."


def knocked_out(player:Player, wall:float | None=None) -> bool:
    wall = time.time() if wall is None else wall
    return player.profile.get("ko_until", 0) > wall


def refusal(player:Player, other:Player, act:str, role:str) -> str:
    if not can_do(player.gender, act, role, player.body):
        return f"You cannot do {ACT_LABELS[act]} {role} with your body."
    if not can_do(other.gender, act, other_role(role), other.body):
        return f"{other.name} cannot do the other side of {ACT_LABELS[act]}."
    return ""


def entry_of(player:Player, act:str, role:str, options:dict[str, str],
             direction:str="") -> dict[str, Any]:
    return {"by": player.id, "act": act, "role": role,
            "options": dict(options), "direction": direction}


def request(player:Player, other:Player, home:dict[str, Any], act:str,
            role:str, options:dict[str, str], direction:str,
            repository:Any, wall:float | None=None) -> list[Message]:
    wall = time.time() if wall is None else wall
    problem = refusal(player, other, act, role)
    if problem:
        return [Message(problem, player.name)]
    scene = scenes_of(home).setdefault(pair_key(player, other),
                                       new_scene(player, other, wall))
    entry = entry_of(player, act, role, options, direction)
    for me, you in ((player, other), (other, player)):
        me.profile["home_sex"] = you.name
        repository.save(me)
    lead = hierarchy(player, other)
    if lead is not None and lead[1] is player:
        scene["wish"] = entry
        return [Message(f"You wish for {ACT_LABELS[act]} ({role}). Only "
                        f"{other.name} decides.", player.name),
                Message("★ " + WISH_TEXT.format(
                    a=other.name, b=player.name, act=ACT_LABELS[act],
                    role=other_role(role)), other.name)]
    scene["queue"] = entry
    left = max(0, round(scene["due"] - wall))
    return [Message(f"⏱ {ACT_LABELS[act].capitalize()} ({role}) is "
                    f"registered in {left} s.", player.name)]


def wish_valid(entry:dict[str, Any], actor:Player, target:Player) -> bool:
    return not refusal(actor, target, entry["act"], entry["role"])


def house_people(home:dict[str, Any], repository:Any) -> dict[str, Player]:
    entries = [{"id": home["owner"], "name": ""}] + [
        entry for entry in home["residents"] + home["guests"]]
    found: dict[str, Player] = {}
    for entry in entries:
        person = repository.load_by_id(entry["id"])
        if person is None and entry["name"]:
            person = find_local(town_company(repository), entry["name"])
        if person is not None and not is_regular(person):
            found[person.id] = person
    return found


def mate_named(player:Player, people:dict[str, Player]) -> Player | None:
    name = player.profile.get("home_sex", "").casefold()
    if not name:
        return None
    for person in people.values():
        if person is not player and name in (
                person.name.casefold(), person.full_name.casefold(),
                (person.first_name or person.name).casefold()):
            return person
    return None


def linked(first:Player, second:Player,
           people:dict[str, Player]) -> bool:
    return (mate_named(first, people) is second
            and mate_named(second, people) is first)


def autopilot_choice(scene:dict[str, Any], first:Player, second:Player,
                     rng:random.Random) -> None:
    lead = hierarchy(first, second)
    if lead is None:
        if scene.get("overlay") is not None:
            overlay_choice(scene, first, second, rng)
            return
        for auto, human in ((first, second), (second, first)):
            if is_auto(auto) and scene["queue"] is None:
                pick = pick_for(human, auto, rng, False)
                if pick is not None:
                    scene["queue"] = entry_of(human, pick[0], pick[1],
                                              dict(DEFAULTS))
        return
    dom, sub = lead
    if scene.get("overlay") is not None:
        overlay_choice(scene, first, second, rng)
        if is_auto(dom) and rng.random() > 0.2:
            return
    if is_auto(sub) and scene["wish"] is None and rng.random() < 0.6:
        pick = pick_for(dom, sub, rng, False)
        if pick is not None:
            scene["wish"] = entry_of(sub, pick[0], other_role(pick[1]),
                                     dict(DEFAULTS))
    if is_auto(dom) and scene["queue"] is None:
        wish = scene["wish"]
        if (wish is not None and wish_valid(wish, sub, dom)
                and rng.random() < wish_chance(dom, sub)):
            scene["queue"] = wish
        else:
            pick = pick_for(sub, dom, rng, True)
            if pick is not None:
                scene["queue"] = entry_of(sub, pick[0], pick[1],
                                          dict(DEFAULTS))


def overlay_choice(scene:dict[str, Any], first:Player, second:Player,
                   rng:random.Random) -> None:
    overlay = scene["overlay"]
    giver, receiver = ((first, second) if overlay["giver"] == first.id
                       else (second, first))
    acts = scene.setdefault("acts", {})
    if is_auto(giver) and giver.id not in acts:
        merciful = rng.random() < mercy(giver, receiver)
        asked = overlay["plea"] == "mercy" or (
            scene["air"] is not None and scene["air"] <= 40)
        if asked and merciful:
            acts[giver.id] = sex_overlays.MERCY_ACTION.get(
                overlay["kind"], "stop")
        else:
            pool = [name for name in sex_overlays.SIDES[overlay["kind"]][
                "giver"] if name not in ("stop", "raise", "lift")]
            acts[giver.id] = rng.choice(pool)
    if is_auto(receiver) and receiver.id not in acts:
        pool = list(sex_overlays.SIDES[overlay["kind"]]["receiver"])
        if scene["air"] is not None and scene["air"] <= 50:
            pool = ["breath", "tap"]
        elif scene.get("order") and rng.random() < obedience(giver,
                                                             receiver):
            pool = list(sex_overlays.sex_sole.OBEYING)
        acts[receiver.id] = rng.choice(pool)


def execute(scene:dict[str, Any], home:dict[str, Any], first:Player,
            second:Player, repository:Any,
            rng:random.Random) -> list[Message]:
    queued = scene["queue"]
    scene["queue"] = None
    actor, target = (first, second) if queued["by"] == first.id else (
        second, first)
    options = queued["options"]
    args = [queued["act"], queued["role"], options["amount"],
            options["where"]] + ([queued["direction"]]
                                 if queued["direction"] else [])
    done = home_practice(actor, target, home, args, repository, rng)
    lines = [message.text for message in done]
    lead = hierarchy(first, second)
    wish, scene["wish"] = scene["wish"], None
    if lead is not None:
        dom, sub = lead
        sub_role = (queued["role"] if actor is sub
                    else other_role(queued["role"]))
        lines += rate(dom, sub, wish, queued["act"], sub_role, rng)
    lines += add_heat(scene, queued["act"], queued["role"], actor, target,
                      rng, options["where"])
    repository.save(first)
    repository.save(second)
    overlay = sex_overlays.start(scene, queued["act"], queued["role"],
                                 actor, target, options["where"])
    scene["air"], scene["smothered"] = None, ""
    if overlay is not None and (
            overlay["kind"] in sex_overlays.SMOTHERING):
        under = target if queued["role"] == "give" else actor
        scene["air"], scene["smothered"] = sex_overlays.AIR_START, under.id
        lines.append(f"{air_line(100)} – {under.name} cannot breathe "
                     f"freely.")
    return both("\n".join(lines), first, second)


def knock_out(scene:dict[str, Any], first:Player, second:Player,
              repository:Any, wall:float) -> list[Message]:
    under = first if scene["smothered"] == first.id else second
    crushed = scene.pop("crushed", "") == under.id
    seconds = HOUSE_KO_SECONDS * (HOUSE_CRUSH_KO if crushed else 1)
    under.profile["ko_until"] = wall + seconds
    for person in (first, second):
        person.profile.pop("home_sex", None)
        repository.save(person)
    scene["over"] = True
    if crushed:
        return both(f"{air_line(0)}\n💫 The crushing weight is too much: "
                    f"{under.name}'s head is squeezed until the world goes "
                    f"black. Out cold, bruised, but alive. The scene ends.",
                    first, second)
    return both(f"{air_line(0)}\n💫 {under.name} runs out of air and goes "
                f"limp: out cold, but breathing. The scene ends.",
                first, second)


def pulse(home:dict[str, Any], scene:dict[str, Any], first:Player,
          second:Player, repository:Any, rng:random.Random,
          wall:float) -> list[Message]:
    scene["due"] = wall + HOUSE_SCENE_PULSE
    scene["beats"] = scene.get("beats", 0) + 1
    messages: list[Message] = []
    lead = hierarchy(first, second)
    if (lead is not None and is_auto(lead[0])
            and scene["beats"] >= HOUSE_AUTO_BEATS
            and rng.random() < HOUSE_AUTO_END):
        for person in (first, second):
            person.profile.pop("home_sex", None)
            repository.save(person)
        scene["over"] = True
        return both(f"{lead[0].name} has had enough for tonight and "
                    f"ends it.", first, second)
    owed = scene["owed"]
    if owed is not None:
        scene["owed"] = None
        silent = first if owed["id"] == first.id else second
        boss = second if silent is first else first
        messages += both(SILENCE.format(a=boss.name, b=silent.name),
                         first, second)
    autopilot_choice(scene, first, second, rng)
    if scene["queue"] is not None:
        return messages + execute(scene, home, first, second, repository,
                                  rng)
    if scene.get("overlay") is not None:
        return messages + run_overlay(scene, first, second, repository,
                                      rng, wall)
    return messages


def run_overlay(scene:dict[str, Any], first:Player, second:Player,
                repository:Any, rng:random.Random,
                wall:float) -> list[Message]:
    overlay = scene["overlay"]
    giver, receiver = ((first, second) if overlay["giver"] == first.id
                       else (second, first))
    lines, out = sex_overlays.resolve(scene, giver, receiver, rng)
    if out:
        return both("\n".join(lines), first, second) + knock_out(
            scene, first, second, repository, wall)
    if scene["air"] is not None:
        lines.append(air_line(scene["air"]))
    repository.save(first)
    repository.save(second)
    return both("\n".join(lines), first, second) if lines else []


def tick_scenes(repository:Any, rng:random.Random,
                wall:float | None=None) -> list[Message]:
    wall = time.time() if wall is None else wall
    messages: list[Message] = []
    for home in list(repository.houses.houses.values()):
        people = house_people(home, repository)
        for person in people.values():
            mate = mate_named(person, people)
            if mate is not None and linked(person, mate, people):
                scenes_of(home).setdefault(pair_key(person, mate),
                                           new_scene(person, mate, wall))
        for key, scene in list(scenes_of(home).items()):
            first, second = people.get(scene["a"]), people.get(scene["b"])
            if first is None or second is None or not linked(
                    first, second, people):
                del scenes_of(home)[key]
                continue
            if wall < scene["due"]:
                continue
            messages += pulse(home, scene, first, second, repository, rng,
                              wall)
            if scene.get("over"):
                del scenes_of(home)[key]
    return messages


def order_hero(player:Player, other:Player, home:dict[str, Any],
               title:str, repository:Any, rng:random.Random) -> list[Message]:
    scene = scenes_of(home).setdefault(pair_key(player, other),
                                       new_scene(player, other, time.time()))
    titles_of(home)[other.id] = title.capitalize()
    repository.save(player)
    text = rng.choice(DEMANDS).format(a=player.name, b=other.name,
                                      title=title.capitalize())
    scene["owed"] = {"id": other.id, "title": title.capitalize()}
    messages = both(f"👑 {text}", player, other)
    if is_auto(other) and rng.random() < obedience(player, other):
        messages += answer_for(scene, home, player, other, rng)
    elif is_auto(other):
        messages += both(SILENCE.format(a=player.name, b=other.name),
                         player, other)
        scene["owed"] = None
    else:
        messages.append(Message("Press Answer in the Sex tab (or type "
                                "!home answer) before the next beat.", other.name))
    return messages


def answer_for(scene:dict[str, Any], home:dict[str, Any], boss:Player,
               sub:Player, rng:random.Random) -> list[Message]:
    owed = scene.get("owed")
    if owed is None or owed["id"] != sub.id:
        return [Message("Nobody is waiting for an answer.", sub.name)]
    scene["owed"] = None
    pool = KIN_REMINDERS.get(kin_of(boss, sub), ()) * 2 + REMINDERS
    text = rng.choice(pool).format(a=boss.name, b=sub.name,
                                   title=owed["title"])
    return both(text, boss, sub)


word_actions = {"breathe": "tap", "lift": "raise"}


def scene_command(word:str, player:Player, home:dict[str, Any],
                  repository:Any, rng:random.Random,
                  action:str="") -> list[Message]:
    people = house_people(home, repository)
    for scene in scenes_of(home).values():
        if player.id not in (scene["a"], scene["b"]):
            continue
        other = people.get(scene["b"] if scene["a"] == player.id
                           else scene["a"])
        if other is None:
            continue
        if word == "answer":
            return answer_for(scene, home, other, player, rng)
        if word in ("breathe", "lift", "act"):
            overlay = scene.get("overlay")
            name = (word_actions[word] if word != "act" else action)
            if overlay is not None and word == "lift":
                name = sex_overlays.MERCY_ACTION.get(overlay["kind"], name)
            if overlay is None:
                return [Message("Nothing is going on that needs an "
                                "answer.", player.name)]
            problem = sex_overlays.queue(scene, player, name)
            if problem:
                return [Message(problem, player.name)]
            left = max(0, round(scene["due"] - time.time()))
            return [Message(f"⏱ {sex_overlays.LABELS[name]} is registered "
                            f"in {left} s.", player.name)]
    return [Message("There is no scene going on.", player.name)]


def overlay_info(scene:dict[str, Any], player:Player) -> dict[str, Any]:
    overlay = scene.get("overlay")
    if overlay is None:
        return {}
    return {"kind": overlay["kind"], "act": overlay["act"],
            "side": sex_overlays.side_of(overlay, player),
            "actions": list(sex_overlays.actions_for(overlay, player)),
            "chosen": scene.get("acts", {}).get(player.id, ""),
            "plea": overlay["plea"], "order": bool(scene.get("order")),
            "sweat": scene.get("sweat")}


def scene_info(player:Player, repository:Any,
               wall:float | None=None) -> dict[str, Any] | None:
    wall = time.time() if wall is None else wall
    for home in repository.houses.houses.values():
        for scene in scenes_of(home).values():
            if player.id not in (scene["a"], scene["b"]):
                continue
            wish = scene["wish"]
            mine = None
            if wish is not None:
                mine = ((wish["act"], wish["role"]) if wish["by"] == player.id
                        else (wish["act"], other_role(wish["role"])))
            owed = scene["owed"]
            mate = house_people(home, repository).get(
                scene["b"] if scene["a"] == player.id else scene["a"])
            return {"left": max(0, round(scene["due"] - wall)),
                    "heat": heat_of(scene, player),
                    "mate_heat": (heat_of(scene, mate)
                                  if mate is not None else 0),
                    "content": (content_of(player, mate)
                                if mate is not None else 0),
                    "air": scene["air"],
                    "air_owner": (player.name if scene["smothered"]
                                  == player.id else
                                  mate.name if mate is not None else ""),
                    "smothered": scene["smothered"] == player.id,
                    "wish": mine,
                    "owes": owed["title"] if owed and owed["id"] == player.id
                    else "",
                    "queued": scene["queue"] is not None,
                    "overlay": overlay_info(scene, player)}
    return None


def timer_line(player:Player, repository:Any,
               wall:float | None=None) -> str:
    info = scene_info(player, repository, wall)
    if info is None:
        return ""
    return f"Next interaction in {info['left']} s"
