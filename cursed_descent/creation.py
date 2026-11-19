from dataclasses import dataclass, field

from .config import (
    GENDERS, START_FREE_POINTS, START_STAT_VALUE, STAT_NAMES, STAT_SHORT,
)
from .body import body_text, default_body
from .body_creation import answer_field, fields_for, question_at
from .models import Message, Player
from .races import RACES
from .storage import PlayerRepository


CANCEL_WORDS = {"cancel", "stop", "!cancel"}
YES_WORDS = {"yes", "y", "ok"}
NO_WORDS = {"no", "n"}

STAT_HELP = (
    "STR = melee damage\n"
    "AGI = dodge, crit chance\n"
    "VIT = hit points, armor\n"
    "INT = spell damage, healing, mana, loot luck"
)


def find_gender(value:str) -> str | None:
    wanted = value.strip().casefold()
    if wanted.isdigit() and 1 <= int(wanted) <= len(GENDERS):
        return GENDERS[int(wanted) - 1]
    for gender in GENDERS:
        if gender.casefold() == wanted:
            return gender
    return None


def playable_races() -> dict:
    return {key: race for key, race in RACES.items() if race.playable}


def find_race(value:str):
    word = value.strip().casefold()
    if word in YES_WORDS or not word:
        return RACES["human"]
    choices = playable_races()
    keys = list(choices)
    if word.isdigit():
        index = int(word) - 1
        return choices[keys[index]] if 0 <= index < len(keys) else None
    return next((race for race in choices.values()
                 if word in (race.key, race.name, race.plural)), None)


def full_name(state:"CreationState") -> str:
    parts = [part for part in (state.first_name, state.last_name) if part]
    return " ".join(parts) or state.name


def parse_distribution(text:str) -> dict[str, int] | str:
    parts = text.replace(",", " ").split()
    if len(parts) != len(STAT_NAMES) or not all(p.isdigit() for p in parts):
        return (f"Please enter exactly {len(STAT_NAMES)} numbers, "
                f"e.g. '4 2 2 2'.")
    values = [int(part) for part in parts]
    if sum(values) != START_FREE_POINTS:
        return (f"That's {sum(values)} points – it has to be exactly "
                f"{START_FREE_POINTS}.")
    return dict(zip(STAT_NAMES, values))


@dataclass
class CreationState:
    name: str
    step: str = "name"
    first_name: str = ""
    last_name: str = ""
    char_id: str = ""
    gender: str = ""
    race: str = "human"
    distribution: dict[str, int] = field(default_factory=dict)
    body: dict = field(default_factory=dict)
    body_index: int = 0


class CharacterCreator:
    def __init__(self, repository:PlayerRepository) -> None:
        self.repository = repository
        self.states: dict[str, CreationState] = {}
        self.owners: dict[str, str] = {}

    def is_active(self, name:str) -> bool:
        return self.repository.key(name) in self.states

    def start(self, name:str, char_id:str="") -> list[Message]:
        state = CreationState(name=name, char_id=char_id,
                              body=default_body())
        self.states[self.repository.key(name)] = state
        intro = ("🕯 Welcome to the gate of the cursed dungeon.\n"
                 "Let's create your character in 6 steps. "
                 "'cancel' aborts at any time.\n")
        return [Message(intro + self.name_question(state), name)]

    def name_question(self, state:CreationState) -> str:
        return (f"Step 1/6 – First and last name, e.g. 'Lyra Dawn' "
                f"(one word = first name only, 'ok' keeps "
                f"'{state.name}').")

    def gender_question(self, state:CreationState) -> str:
        options = "\n".join(f"  {index}. {gender}"
                            for index, gender in enumerate(GENDERS, start=1))
        return f"Step 2/6 – Gender (number or name):\n{options}"

    def race_question(self) -> str:
        options = "\n".join(
            f"  {index}. {race.name.capitalize()} – {race.height[0]}-"
            f"{race.height[1]} cm, {race.weight[0]}-{race.weight[1]} kg"
            for index, race in enumerate(playable_races().values(),
                                         start=1))
        return (f"Step 3/6 – Race (number or name, 'ok' = human):\n"
                f"{options}")

    def stats_question(self) -> str:
        return (f"Step 5/6 – Distribute {START_FREE_POINTS} points across "
                f"STR AGI VIT INT (every stat starts at "
                f"{START_STAT_VALUE}).\n{STAT_HELP}\n"
                f"Answer with 4 numbers in that order, e.g. '4 1 3 2'.")

    def summary(self, state:CreationState) -> str:
        stats = " | ".join(
            f"{STAT_SHORT[stat]} {START_STAT_VALUE + state.distribution[stat]}"
            for stat in STAT_NAMES
        )
        return (f"Step 6/6 – Summary:\n"
                f"  Name: {full_name(state)}\n"
                f"  Gender: {state.gender}\n"
                f"  Race: {state.race}\n"
                f"  Body: {body_text(state.body)}\n"
                f"  {stats}\n"
                f"Is that right? (yes / no)")

    def answer(self, name:str, text:str) -> tuple[list[Message],
                                                  Player | None]:
        key = self.repository.key(name)
        state = self.states[key]
        answer = text.strip()
        if answer.casefold() in CANCEL_WORDS:
            del self.states[key]
            return [Message("Character creation cancelled.", name)], None
        if state.step == "name":
            return self.answer_name(state, answer), None
        if state.step == "gender":
            return self.answer_gender(state, answer), None
        if state.step == "race":
            return self.answer_race(state, answer), None
        if state.step == "body":
            return self.answer_body(state, answer), None
        if state.step == "stats":
            return self.answer_stats(state, answer), None
        return self.answer_confirm(state, answer)

    def answer_name(self, state:CreationState, answer:str) -> list[Message]:
        if answer.casefold() in YES_WORDS:
            parts = [state.name]
        else:
            parts = answer.split()
        if not parts or len(parts) > 2:
            return [Message(f"Please give one or two words.\n"
                            f"{self.name_question(state)}", state.name)]
        state.first_name = parts[0]
        state.last_name = parts[1] if len(parts) == 2 else ""
        state.step = "gender"
        return [Message(self.gender_question(state), state.name)]

    def answer_gender(self, state:CreationState,
                      answer:str) -> list[Message]:
        gender = find_gender(answer)
        if gender is None:
            return [Message(f"I don't know '{answer}'.\n"
                            f"{self.gender_question(state)}", state.name)]
        state.gender = gender
        state.step = "race"
        return [Message(self.race_question(), state.name)]

    def answer_race(self, state:CreationState,
                    answer:str) -> list[Message]:
        race = find_race(answer)
        if race is None:
            return [Message(f"I don't know '{answer}'.\n"
                            f"{self.race_question()}", state.name)]
        state.race = race.key
        state.body["height"] = round(sum(race.height) / 2)
        state.body["weight"] = round(sum(race.weight) / 2)
        length, girth, balls = race.member
        state.body.update(endowment=length, girth=girth, balls=balls,
                          endowment_shape=race.member_shape)
        state.step = "body"
        state.body_index = 0
        return [Message(self.body_prompt(state, f"You are "
                                         f"{race.name}. Your starting "
                                         f"body: {body_text(state.body)}"),
                        state.name)]

    def body_prompt(self, state:CreationState, note:str="") -> str:
        return question_at(state.body, state.gender, state.body_index, note)

    def answer_body(self, state:CreationState,
                    answer:str) -> list[Message]:
        state.body, state.body_index, error = answer_field(
            state.body, state.gender, state.body_index, answer)
        if state.body_index > len(fields_for(state.gender)):
            state.step = "stats"
            note = self.fit_to_race(state)
            return [Message(note + self.stats_question(), state.name)]
        return [Message(self.body_prompt(state, error), state.name)]

    def fit_to_race(self, state:CreationState) -> str:
        race = RACES[state.race]
        changes = []
        for key, (low, high) in (("height", race.height),
                                 ("weight", race.weight)):
            value = state.body[key]
            fitted = min(max(value, low), high)
            if fitted != value:
                state.body[key] = fitted
                changes.append(f"{key} {value} -> {fitted}")
        if not changes:
            return ""
        return (f"As {race.name} your body was adjusted to fit the race: "
                f"{', '.join(changes)}.\n")

    def answer_stats(self, state:CreationState,
                     answer:str) -> list[Message]:
        distribution = parse_distribution(answer)
        if isinstance(distribution, str):
            return [Message(f"{distribution}\n{self.stats_question()}",
                            state.name)]
        state.distribution = distribution
        state.step = "confirm"
        return [Message(self.summary(state), state.name)]

    def answer_confirm(self, state:CreationState,
                       answer:str) -> tuple[list[Message], Player | None]:
        word = answer.casefold()
        if word in NO_WORDS:
            state.step = "name"
            return [Message(f"Okay, starting over.\n"
                            f"{self.name_question(state)}",
                            state.name)], None
        if word not in YES_WORDS:
            return [Message("Please answer with 'yes' or 'no'.",
                            state.name)], None
        player = Player(name=state.name, gender=state.gender, free_points=0,
                        body=dict(state.body), first_name=state.first_name,
                        last_name=state.last_name, race=state.race)
        if state.char_id:
            player.id = state.char_id
        player.account_id = self.owners.pop(
            self.repository.key(state.name), None)
        for stat, value in state.distribution.items():
            player.stats[stat] = START_STAT_VALUE + value
        self.repository.add(player)
        del self.states[self.repository.key(state.name)]
        return [], player
