from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from rich.text import Text
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Static

from chat_store import CHANNEL, Chat, is_ad_line, read_entries


BLOCK_LINES = 300
MIN_OPEN_LINES = 20
TOP_TRIGGER_ROWS = 1
RULE_WIDTH = 24


def children_of(parent:Any, kind:type) -> list[Any]:
    return [child for child in parent.children if isinstance(child, kind)]


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


class DayRule(Static):

    DEFAULT_CSS = """
    DayRule {
        width: 1fr;
        text-align: center;
        color: $text-muted;
        margin: 1 0 0 0;
    }
    """

    def __init__(self, day:str) -> None:
        bar = "─" * RULE_WIDTH
        super().__init__(Text(f"{bar} {day} {bar}", "dim"))
        self.day = day


class LogStart(Static):

    DEFAULT_CSS = """
    LogStart {
        width: 1fr;
        text-align: center;
        color: $text-muted;
    }
    """

    def __init__(self) -> None:
        super().__init__(Text("Beginning of the log", "dim italic"))


class Block(Vertical):

    DEFAULT_CSS = """
    Block {
        height: auto;
    }
    """

    def __init__(self, day:str, start:int, end:int) -> None:
        super().__init__()
        self.day = day
        self.start = start
        self.end = end
        self.pending: list[Any] = []


@dataclass
class OlderRange:
    day: str
    start: int
    end: int
    lines: list[str]


class ChatPager:

    def __init__(self, app:Any, view:VerticalScroll, make_line:Callable[[str], Any]) -> None:
        self.app = app
        self.view = view
        self.make_line = make_line
        self.chat: Chat | None = None
        self.loading = False

    @property
    def blocks(self) -> list[Block]:
        return children_of(self.view, Block)

    def entries(self, day:str) -> list[str]:
        store = self.app.client.store
        path = store.log_dir(self.chat) / f"{day}.log"
        if not path.is_file():
            return []
        lines = read_entries(path)
        if self.chat.kind == CHANNEL and not self.app.client.ads.visible(self.chat.key):
            lines = [line for line in lines if not is_ad_line(line)]
        return lines

    def days_before(self, day:str) -> list[str]:
        files = self.app.client.store.day_files(self.chat)
        return [path.stem for path in files if path.stem < day]

    def build_block(self, day:str, start:int, end:int, lines:list[str]) -> Block:
        block = Block(day, start, end)
        children = [DayRule(day)] if start == 0 else []
        children.extend(self.make_line(line) for line in lines)
        block.pending = children
        return block

    async def mount_block(self, block:Block, before:Any=None) -> None:
        children = block.pending
        block.pending = []
        if before is None:
            await self.view.mount(block)
        else:
            await self.view.mount(block, before=before)
        if children:
            await block.mount_all(children)

    def older_range(self) -> OlderRange | None:
        blocks = self.blocks
        if not blocks:
            return None
        top = blocks[0]
        if top.start > 0:
            lines = self.entries(top.day)
            start = max(0, top.start - BLOCK_LINES)
            return OlderRange(top.day, start, top.start, lines[start:top.start])
        for day in reversed(self.days_before(top.day)):
            lines = self.entries(day)
            if lines:
                start = max(0, len(lines) - BLOCK_LINES)
                return OlderRange(day, start, len(lines), lines[start:])
        return None

    async def reset(self) -> None:
        self.chat = None
        await self.view.remove_children()

    async def open(self, chat:Chat, day:str | None=None, fill:bool=True) -> None:
        self.chat = chat
        await self.view.remove_children()
        self.request_trim()
        day = day or today()
        self.app.client.store.migrate(chat)
        lines = self.entries(day)
        start = max(0, len(lines) - BLOCK_LINES)
        await self.mount_block(self.build_block(day, start, len(lines), lines[start:]))
        if fill and len(lines) < MIN_OPEN_LINES:
            await self.load_older(keep_position=False)
        await self.update_log_start()
        self.view.scroll_end(animate=False)
        self.view.call_after_refresh(self.view.scroll_end, animate=False)

    async def update_log_start(self) -> None:
        has_start = bool(children_of(self.view, LogStart))
        if self.older_range() is None:
            if not has_start:
                await self.view.mount(LogStart(), before=0)
        elif has_start:
            await self.view.remove_children(children_of(self.view, LogStart))

    async def load_older(self, keep_position:bool=True) -> bool:
        older = self.older_range()
        if older is None:
            await self.update_log_start()
            return False
        old_height = self.view.virtual_size.height
        old_y = self.view.scroll_y
        block = self.build_block(older.day, older.start, older.end, older.lines)
        await self.mount_block(block, before=self.blocks[0])
        await self.update_log_start()
        if keep_position:
            def restore() -> None:
                delta = self.view.virtual_size.height - old_height
                self.view.scroll_to(y=old_y + delta, animate=False)
            self.view.call_after_refresh(restore)
        return True

    def at_end(self) -> bool:
        return self.view.scroll_y >= self.view.max_scroll_y - 1

    async def append(self, line:str) -> None:
        blocks = self.blocks
        if self.chat is None or not blocks:
            return
        day = line[1:11]
        if day > blocks[-1].day:
            await self.open(self.chat, day, fill=False)
            blocks = self.blocks
        at_end = self.at_end()
        live = blocks[-1]
        await live.mount(self.make_line(line))
        live.end += 1
        await self.trim_live(at_end)
        if at_end:
            self.view.call_after_refresh(self.view.scroll_end, animate=False)

    async def trim_live(self, at_end:bool) -> None:
        blocks = self.blocks
        if len(blocks) != 1 or not at_end:
            return
        live = blocks[0]
        lines = [child for child in live.children if not isinstance(child, DayRule)]
        if len(lines) <= 2 * BLOCK_LINES:
            return
        await live.remove_children(children_of(live, DayRule) + lines[:BLOCK_LINES])
        live.start += BLOCK_LINES
        self.request_trim()
        await self.update_log_start()

    async def on_scroll(self, y:float) -> None:
        if self.loading or self.chat is None:
            return
        self.loading = True
        try:
            if y <= TOP_TRIGGER_ROWS:
                await self.load_older()
            else:
                await self.unload_far()
        finally:
            self.loading = False

    async def unload_far(self) -> None:
        limit = self.view.scroll_y - self.view.size.height
        far = []
        for block in self.blocks[:-1]:
            if block.virtual_region.bottom >= limit:
                break
            far.append(block)
        if not far:
            return
        starts = children_of(self.view, LogStart)
        height = sum(widget.virtual_region.height for widget in far + starts)
        old_y = self.view.scroll_y
        await self.view.remove_children(starts + far)
        self.view.call_after_refresh(self.view.scroll_to, y=max(0, old_y - height), animate=False)
        self.request_trim()

    def request_trim(self) -> None:
        schedule = getattr(self.app, "schedule_memory_trim", None)
        if schedule is not None:
            schedule()

    async def check_day(self) -> None:
        blocks = self.blocks
        if self.chat is not None and blocks and today() > blocks[-1].day:
            await self.open(self.chat, today(), fill=False)


def main() -> None:
    print(today(), BLOCK_LINES, MIN_OPEN_LINES)


if __name__ == "__main__":
    main()
