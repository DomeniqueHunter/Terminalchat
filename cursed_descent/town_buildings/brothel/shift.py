import random

from ...config import (
    BROTHEL_CUT, WORK_TICK_SECONDS,
    BROTHEL_BELLY_PER_BALL, BROTHEL_KILL_ACTS, BROTHEL_KILL_CHANCE,
    RENT_PRICES,
)
from ...models import Message, Player
from ...needs import satisfy
from ..work.content import CLOSED
from ...races import race_of_town
from ...towns import town_key
from ..body_taste import taste_factor, taste_reaction
from ..work.jobs import Job, Shift, closed, finish, session_pay
from .clients import (
    Client, client_can, client_options, client_prompt, new_client,
)
from .content import (
    ESCORT_INTRO, ESCORT_RESULTS, NO_SHIFT, ROSE_ACTIVE, ROSE_CHANCE,
    ROSE_MID_BONUS, ROSE_MID_CHANCE, ROSE_MID_SUB, ROSE_MID_SUB_CHANCE,
    ROSE_MID_WORKING, ROSE_PASSIVE,
)
from .dialogue import (
    TONE_BONUS, default_tone, match_text, parse_tone, player_line, reaction,
    speaker, tone_matches,
)
from .practices import (
    options_for, can_do, describe, option_text, parse_choice, parse_direction,
)
from ..family import role_of
from .family_dialogue import family_line
from .practices_anatomy import balls_word
from .practices_kicks import COME_LINES, DEATH_LINES, LOOT_LINE
from .finish import FINISHERS, dom_finish, finish_client, problem
from ...preferences import brothel_mode


def rose_visit(player:Player, rng:random.Random,
               regulars=None) -> list[Message]:
    if rng.random() >= ROSE_CHANCE:
        return []
    if regulars is not None:
        regulars.owner_visit("brothel")
    text = ROSE_ACTIVE if rng.random() < 0.5 else ROSE_PASSIVE
    return [Message(text, player.name)]


def operator_drop_in(player:Player, shift:Shift,
                     rng:random.Random) -> list[Message]:
    sub = shift.mode == "sub"
    if rng.random() >= (ROSE_MID_SUB_CHANCE if sub else ROSE_MID_CHANCE):
        return []
    race = race_of_town(town_key(player))
    pool = (race.drop_in_sub if sub else race.drop_in_working) or (
        ROSE_MID_SUB if sub else ROSE_MID_WORKING)
    text = rng.choice(pool)
    shift.earned += ROSE_MID_BONUS
    if shift.endless:
        player.gold += ROSE_MID_BONUS
    return [Message(f"{text} +{ROSE_MID_BONUS} gold", player.name)]


def escort_shift(player:Player, job:Job,
                 rng:random.Random) -> list[Message]:
    weights = [entry[0] for entry in ESCORT_RESULTS]
    _, _, text, factor = rng.choices(ESCORT_RESULTS, weights)[0]
    shift = Shift("brothel", job, 1,
                  round(session_pay(player, job, rng) * factor))
    messages = rose_visit(player, rng)
    messages.append(Message(f"{ESCORT_INTRO} {text} +{shift.earned} gold",
                            player.name))
    return messages + finish(player, shift)


def start_shift(player:Player, job:Job, shifts:dict[str, Shift],
                rng:random.Random, regulars=None, mode:str="") -> list[Message]:
    if job.key == "escort":
        return escort_shift(player, job, rng)
    mode = brothel_mode(player, mode)
    shift = Shift("brothel", job, job.sessions, mode=mode,
                  client=new_client(player, rng, regulars, mode))
    shifts[player.name] = shift
    return rose_visit(player, rng, regulars) + [
        client_prompt(shift, player)]


def judge(client:Client, act:str, role:str, tone:str,
          pay:int) -> tuple[int, bool]:
    liked = (act, role) in client.likes
    if client.dominated or client.dominant:
        pay = round(pay * (2.0 if liked else 0.7))
    else:
        pay = round(pay * (1.5 if liked else 1.0))
    matched = tone_matches(client.temper, tone)
    if matched:
        pay = round(pay * TONE_BONUS)
    return pay, liked


def kill_chance(player:Player, client:Client) -> float:
    ratio = player.body.get("weight", 70) / max(client.weight, 40)
    return BROTHEL_KILL_CHANCE * max(0.5, min(2.5, ratio))


def next_client(player:Player, shift:Shift, shifts:dict[str, Shift],
                messages:list[Message], rng:random.Random,
                regulars) -> list[Message]:
    if shift.left <= 0 and not shift.endless:
        del shifts[player.name]
        return messages + finish(player, shift)
    visit = operator_drop_in(player, shift, rng)
    shift.client = new_client(player, rng, regulars, shift.mode)
    return messages + visit + [client_prompt(shift, player)]


def kill_client(player:Player, shift:Shift, act:str, rng:random.Random,
                regulars) -> Message:
    client = shift.client
    shift.served += 1
    if shift.endless:
        shift.earned += client.purse
        player.gold += client.purse - round(client.purse * BROTHEL_CUT)
    else:
        shift.earned += client.purse
        shift.left -= 1
    if regulars is not None:
        regulars.forget("brothel", client.name)
    text = rng.choice(DEATH_LINES[act]).format(client=client.name)
    return Message(f"{text}\n" + LOOT_LINE.format(
        client=client.name, gold=client.purse), player.name)


def come_inside(player:Player, client:Client, rng:random.Random,
                regulars) -> str:
    balls = player.body.get("balls", 5)
    growth = max(1, round(balls * BROTHEL_BELLY_PER_BALL))
    client.belly += growth
    if regulars is not None:
        regulars.set("brothel", client.name, {"belly": client.belly})
    tier = min(len(COME_LINES) - 1, growth // 3)
    text = COME_LINES[tier].format(client=client.name,
                                   balls=balls_word(balls))
    return f"{text} (+{growth} cm, belly now +{client.belly} cm)"


def auto_serve(player:Player, shifts:dict[str, Shift], rng:random.Random,
               now:float, regulars=None) -> list[Message]:
    shift = shifts.get(player.name)
    client = shift.client if shift is not None else None
    if client is None:
        return []
    options = [(act, role) for act, role in client_options(
        player, client)
        if (shift.mode != "domina" or role == "give")
        and (shift.mode != "sub" or role == "receive")]
    liked = [pair for pair in client.likes if pair in options]
    act, role = rng.choice(liked if liked and rng.random() < 0.5
                           else options)
    messages = serve(player, f"{act} {role}", shifts, rng, regulars, now)
    note = (f"You took too long – the house picks for you: {act} "
            f"{role}.")
    if messages:
        messages[0] = Message(f"{note}\n{messages[0].text}",
                              messages[0].recipient)
    return messages


def serve(player:Player, text:str, shifts:dict[str, Shift],
          rng:random.Random, regulars=None,
          now:float | None=None) -> list[Message]:
    shift = shifts.get(player.name)
    if shift is None:
        return [Message(NO_SHIFT, player.name)]
    if now is not None:
        shift.due = now + WORK_TICK_SECONDS
    words = text.split()
    if words and words[0].casefold() in FINISHERS:
        word = words[0].casefold()
        refused = problem(player, shift, word)
        if refused:
            return [Message(refused, player.name)]
        messages, _ = finish_client(player, shift, word, rng, regulars)
        return next_client(player, shift, shifts, messages, rng, regulars)
    act, role = parse_choice(words, town_key(player))
    options = option_text(player.gender, player.body, town_key(player))
    if not act or not role:
        return [Message(f"Say what and how: [serve <act> give|receive "
                        f"[tone]]. You can: {options}.", player.name)]
    if not can_do(player.gender, act, role, player.body):
        return [Message(f"As {player.gender} you can't {act} {role}. "
                        f"You can: {options}.", player.name)]
    if shift.mode == "domina" and role != "give":
        return [Message("You work as a domina: you give, you do not "
                        "receive. [serve <act> give]", player.name)]
    if shift.mode == "sub" and role != "receive":
        return [Message("You work as a sub: you receive and obey. "
                        "[serve <act> receive]", player.name)]
    client = shift.client
    if not client_can(client, act, role):
        return [Message(f"{client.name} cannot do the other side of "
                        f"{act} {role}. Possible: "
                        + " | ".join(f"{a} {r}" for a, r in
                                     client_options(player, client)),
                        player.name)]
    tone = parse_tone(words) or default_tone(player)
    if role == "receive":
        ended = dom_finish(player, shift, act, rng, shifts)
        if ended is not None:
            return ended
    if (role == "give" and act in BROTHEL_KILL_ACTS
            and rng.random() < kill_chance(player, client)):
        return next_client(player, shift, shifts, [kill_client(
            player, shift, act, rng, regulars)], rng, regulars)
    pay, liked = judge(client, act, role, tone,
                       session_pay(player, shift.job, rng))
    pay = round(pay * taste_factor(player, client.name))
    shift.earned += pay
    shift.served += 1
    if shift.endless:
        player.gold += pay - round(pay * BROTHEL_CUT)
    else:
        shift.left -= 1
    if regulars is not None and regulars.has("brothel", client.name):
        client.history = regulars.count("brothel", client.name,
                                        f"{act}/{role}")
    lines = [f"You ({tone}): {player_line(tone, role, rng)}",
             describe(player, act, role, rng, parse_direction(words)),
             f"{speaker(client.name)}: {reaction(client.temper, liked, rng)}"]
    if client.player:
        kin = role_of(player, client.player)
        extra = family_line(kin, act, player.name, client.player, rng)
        if extra:
            lines.insert(2, extra)
    if tone_matches(client.temper, tone):
        lines.append(match_text(tone))
    reaction_note = taste_reaction(player, client.name)
    if reaction_note:
        lines.append(reaction_note)
    if act == "anal" and role == "give" and player.body.get("balls"):
        lines.append(come_inside(player, client, rng, regulars))
    lines.append(f"+{pay} gold")
    if client.player:
        lines.append(f"{client.player} leaves with shaking knees.")
    shown = [Message("\n".join(lines), player.name)]
    if client.player:
        shown.append(Message("\n".join(lines[:3]), client.player))
    return next_client(player, shift, shifts,
                       shown, rng, regulars)


def rent(player:Player, text:str, in_run:bool) -> list[Message]:
    if in_run:
        return closed("brothel", player)
    kind = text.strip().casefold()
    if kind not in RENT_PRICES:
        return [Message("[book classic] or [book fetish].", player.name)]
    price = RENT_PRICES[kind]
    if player.gold < price:
        return [Message(f"Madame <<npc.rose_first>> wants {price} gold for that.",
                        player.name)]
    player.gold -= price
    satisfy(player.needs, {"arousal": -100})
    flavor = ("A gentle, well-practised hour." if kind == "classic" else
              "Madame <<npc.rose_first>> sends her most inventive girl with a locked "
              "chest of toys.")
    return [Message(f"{flavor} You feel completely relieved. "
                    f"-{price} gold (💰 {player.gold})", player.name)]
