from dataclasses import dataclass, field
from pathlib import Path

from ....config import (
    COURSE_DAYS, COURSE_PRICE, MAID_BUYBACK_PRICE, SCHOOL_FILE_NAME,
)
from ....models import Message, Player
from ....needs import satisfy
from ....storage import read_json, write_json
from .content import (
    COURSES, ENROLL_WARNING, GRADUATION, GREETING, LESSONS, LOCKED, QUIT,
    SCOLDS,
)


CLOSED = "The Maid School is closed while you are down in the dungeon."
UNIFORM = "maid_uniform"
BODY_LIMIT = 140


@dataclass
class Record:
    learned: list[str] = field(default_factory=list)
    course: str = ""
    days_done: int = 0


class SchoolLedger:
    def __init__(self, data_path:Path) -> None:
        self.path = data_path / SCHOOL_FILE_NAME
        self.records = {
            char_id: Record(data.get("learned", []), data.get("course", ""),
                            data.get("days_done", 0))
            for char_id, data in read_json(self.path, {}).items()}

    def record(self, player:Player) -> Record:
        return self.records.setdefault(player.id, Record())

    def save(self) -> None:
        write_json(self.path, {
            char_id: {"learned": record.learned, "course": record.course,
                      "days_done": record.days_done}
            for char_id, record in self.records.items()
            if record.learned or record.course})


def lock_message(record:Record) -> str:
    return LOCKED.format(day=record.days_done + 1, total=COURSE_DAYS)


def graduate(player:Player, record:Record) -> list[Message]:
    course = COURSES[record.course]
    player.stats[course["stat"]] += 3
    if "butt" in course:
        player.body["butt"] = min(BODY_LIMIT,
                                  player.body["butt"] + course["butt"])
    record.learned.append(record.course)
    record.course = ""
    record.days_done = 0
    return [Message(GRADUATION.format(title=course["title"],
                                      stat=course["stat"]), player.name)]


def attend(player:Player, record:Record) -> list[Message]:
    if not record.course:
        return [Message("You are not enrolled in a course.", player.name)]
    lesson = LESSONS[record.course][record.days_done]
    record.days_done += 1
    satisfy(player.needs, {"hunger": -40, "thirst": -40, "sleep": -50})
    messages = [Message(f"{lesson}\n(Meals and a narrow bed are included.)",
                        player.name)]
    if record.days_done >= COURSE_DAYS:
        messages += graduate(player, record)
    return messages


def quit_course(player:Player, record:Record) -> list[Message]:
    if not record.course:
        return [Message("You are not enrolled in a course.", player.name)]
    record.course = ""
    record.days_done = 0
    return [Message(QUIT, player.name)]


def school_menu(player:Player, record:Record) -> list[Message]:
    lines = [GREETING, f"💰 Gold: {player.gold}"]
    if record.course:
        lines.append(f"In training: {COURSES[record.course]['title']} – "
                     f"day {record.days_done + 1}/{COURSE_DAYS}. You "
                     f"cannot leave the school: [maidschool day] attends "
                     f"today's lesson, [maidschool quit] drops out (fee "
                     f"lost).")
    lines.append(f"Courses ([maidschool learn <name>], {COURSE_PRICE} gold, "
                 f"{COURSE_DAYS} days):")
    for key, course in COURSES.items():
        mark = " ✔" if key in record.learned else ""
        lines.append(f"  {key:<9} {course['title']}{mark} – "
                     f"{course['blurb']}")
    lines.append("Maids: look for one with the Look for maids button "
                 "(each further maid costs a fee, five at most) and "
                 "recruit the one you like.")
    lines.append("[maidschool enroll] – become a maid yourself "
                 "(permanent). [maidschool buyback <name>] – buy a "
                 "graduate back.")
    return [Message("\n".join(lines), player.name)]


def learn(player:Player, record:Record, text:str) -> list[Message]:
    key = text.strip().casefold()
    if key not in COURSES:
        return school_menu(player, record)
    if record.course:
        return [Message("One course at a time.", player.name)]
    if key in record.learned:
        return [Message("You already know that by heart.", player.name)]
    if player.gold < COURSE_PRICE:
        return [Message(f"The course costs {COURSE_PRICE} gold.",
                        player.name)]
    player.gold -= COURSE_PRICE
    record.course = key
    record.days_done = 0
    return [Message(f"Brunhild takes your gold and your measurements. "
                    f"{SCOLDS[len(record.learned) % len(SCOLDS)]} "
                    f"({COURSE_DAYS} days)", player.name)]


def school(player:Player, record:Record, args:list[str],
           in_run:bool) -> list[Message]:
    if in_run:
        return [Message(CLOSED, player.name)]
    sub = args[0].casefold() if args else ""
    if sub in ("day", "attend", "lesson"):
        return attend(player, record)
    if sub == "quit":
        return quit_course(player, record)
    if sub == "learn":
        return learn(player, record, " ".join(args[1:]))
    return school_menu(player, record)


def enroll_warning(player:Player) -> Message:
    return Message(ENROLL_WARNING.format(
        name=player.name, price=MAID_BUYBACK_PRICE), player.name)


def make_maid(player:Player) -> None:
    player.npc = "maid"
    player.profile["graduate"] = True
    player.equipment = {slot: None for slot in player.equipment}
    player.equipment["chest"] = UNIFORM
    player.inventory = []
    player.gold = 0
    player.free_points = 0


def buyback_price(player:Player) -> int:
    return MAID_BUYBACK_PRICE * player.level


def buy_back(buyer:Player, graduate_:Player) -> list[Message]:
    price = buyback_price(graduate_)
    if buyer.gold < price:
        return [Message(f"{graduate_.name} costs {price} gold to buy back.",
                        buyer.name)]
    buyer.gold -= price
    graduate_.npc = ""
    return [Message(f"{buyer.name} pays {price} gold. {graduate_.name} "
                    f"walks out of the school as a free adventurer again, "
                    f"uniform and all.", buyer.name)]
