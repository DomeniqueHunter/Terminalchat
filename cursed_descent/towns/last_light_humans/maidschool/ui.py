from ....config import (
    COMPANION_NAME, COURSE_DAYS, COURSE_PRICE, MAID_SEARCH_FEE,
    MAID_SEARCH_MAX,
)
from ....models import Player
from ....npcs.hire import hire_price
from ....view import Button, Panel
from .content import COURSES
from .building import armed
from .search import current


def course_panel(services, player:Player) -> Panel:
    record = services.school.record(player)
    lines = []
    buttons = []
    for key, course in COURSES.items():
        done = key in record.learned
        usable = (not done and not record.course
                  and player.gold >= COURSE_PRICE)
        lines.append(f"{course['title']}{' ✔' if done else ''}: "
                     f"{course['blurb']}")
        buttons.append(Button(course["title"] + (" ✔" if done else ""),
                              f"!maidschool learn {key}", "", usable))
    return Panel(f"Courses ({COURSE_PRICE} g, {COURSE_DAYS} days)",
                 tuple(lines), tuple(buttons))


def training_panel(services, player:Player) -> Panel | None:
    record = services.school.record(player)
    if not record.course:
        return None
    return Panel(f"In training: {COURSES[record.course]['title']} – day "
                 f"{record.days_done + 1}/{COURSE_DAYS}", (), (
                     Button("Attend today's lesson", "!maidschool day"),
                     Button("Drop out", "!maidschool quit")))


def search_panel(services, player:Player) -> Panel:
    search = current(services, player)
    if search is None or not search.maids:
        return Panel("Maids for hire", (), (
            Button("Look for maids", "!maidschool look"),))
    maid = search.maids[search.index]
    last = search.index + 1 >= len(search.maids)
    capped = last and len(search.maids) >= MAID_SEARCH_MAX
    free = not last or player.gold >= MAID_SEARCH_FEE
    price = hire_price(maid)
    label = "Next maid" if not last else f"Next maid ({MAID_SEARCH_FEE} g)"
    return Panel("Maids for hire", (
        f"{search.index + 1}/{MAID_SEARCH_MAX}: {maid.full_name}, "
        f"{maid.age}, Lv {maid.level}", maid.profile["blurb"],
        maid.personality), (
            Button("Previous", "!maidschool prev", "", bool(search.index)),
            Button(label, "!maidschool next", "", not capped and free),
            Button(f"Recruit {maid.first_name} ({price} g)",
                   "!maidschool recruit", "", player.gold >= price)))


def panel(services, player:Player) -> Panel:
    buttons = []
    session = services.session
    if (session.state == "paused"
            and session.member(COMPANION_NAME) is not None):
        buttons.append(Button("Hand over Connie", "!maidschool handover"))
    grads = services.graduates()
    graduates = (Panel("Graduates", (), tuple(
        Button(f"Buy back {grad.name}", f"!maidschool buyback {grad.name}")
        for grad in grads)),) if grads else ()
    enroll_buttons = [Button("Enroll as a maid…", "!maidschool enroll")]
    if armed(services, player.name):
        enroll_buttons.append(Button("Confirm: become a maid for good",
                                     "!maidschool enroll confirm", "danger"))
    enroll = Panel("Enroll", (), tuple(enroll_buttons))
    sections = [section for section in (
        training_panel(services, player), course_panel(services, player),
        search_panel(services, player), *graduates, enroll)
        if section is not None]
    return Panel("🎀 Maid School", ("Headmistress Brunhild",),
                 tuple(buttons), tuple(sections))
