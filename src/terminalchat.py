#!/usr/bin/env python3

import asyncio
import html
import os
import shutil
import subprocess
import sys

from rich.style import Style
from rich.text import Text
from textual.app import App, ComposeResult
from textual.css.query import NoMatches
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Label, ListItem, ListView, OptionList, Static, TextArea

import login
from chat_store import CHANNEL, CONSOLE, USER, Chat, is_ad_line
from chat_widgets import ChatInput, ChatLine, CommandHints, InputModeBar, StatusHeader
from client import Client
from color_config import gender_style
import paths
from chat_log import set_log_dir
from config import Config
from eicons import EiconCache
from panels.channels_list_panel import ChannelsList
from panels.character_panel import CharacterScreen
from panels.login_panel import Credentials, LoginScreen
from panels.emoji_panel import EmojiScreen
from panels.sidebar import Sidebar
from presence import FRIENDS
from sanitize import is_safe_url
from terminal_config import APP_BINDINGS, APP_CSS


LIST_REFRESH_SECONDS = 300
SIDEBAR_REFRESH_SECONDS = 1.0
GENDER_SAVE_SECONDS = 30
INPUT_BAR_REFRESH_SECONDS = 1.0
RECONNECT_DELAYS = (5, 15, 30, 60, 120, 300)
NO_RECONNECT_ERRORS = {9, 31}
CHAT_PLACEHOLDER = "Type message or /help ...  (ctrl+enter: new line, ctrl+r: ads)"


class ChatApp(App):
    BINDINGS = APP_BINDINGS
    CSS = APP_CSS
    TITLE = "Terminal Chat"

    def __init__(self, config:Config) -> None:
        super().__init__()
        self.config = config
        self.client = Client(config, self)
        self.characters: list[str] = []
        self.online = False
        self.startup_notes: list[str] = []
        self.sidebar_dirty: set[str] = {FRIENDS}
        self.list_lock = asyncio.Lock()
        self.eicons = None
        if config.get("eicons", "inline") == "inline":
            self.eicons = EiconCache(max_age_hours=float(config.get("eicon_max_age_hours", 24)))
        self.eicon_height = int(config.get("eicon_height", 4))
        self.gif_enabled = bool(config.get("eicon_animate", True))
        self.active_chat: str | None = None
        self.list_ids: list[str | None] = []
        self.input_mode = "chat"
        self.ad_channel: str | None = None
        self.chat_draft = ""

    def compose(self) -> ComposeResult:
        yield StatusHeader()
        with Horizontal(id="main"):
            yield ListView(id="chat_list")
            with Vertical(id="chat_container"):
                yield VerticalScroll(id="chat_view")
                yield CommandHints(id="command_hints")
                yield InputModeBar(id="input_bar")
                yield ChatInput(placeholder=CHAT_PLACEHOLDER, id="chat_input")
            yield Sidebar(id="sidebar")
        yield Footer()

    def notify(self, message:str, *, title:str="", severity:str="information", timeout:float | None=None,
               markup:bool=False) -> None:
        super().notify(message, title=title, severity=severity, timeout=timeout, markup=markup)

    @property
    def list_view(self) -> ListView:
        return self.query_one("#chat_list", ListView)

    @property
    def chat_view(self) -> VerticalScroll:
        return self.query_one("#chat_view", VerticalScroll)

    def current_chat(self) -> Chat | None:
        return self.client.store.get(self.active_chat) if self.active_chat else None

    @property
    def chat_input(self) -> ChatInput:
        return self.query_one("#chat_input", ChatInput)

    @property
    def sidebar(self) -> Sidebar:
        return self.query_one("#sidebar", Sidebar)

    async def on_mount(self) -> None:
        self.sidebar.display = bool(self.config.get("show_sidebar", False))
        self.set_interval(SIDEBAR_REFRESH_SECONDS, self.refresh_sidebar)
        self.set_interval(GENDER_SAVE_SECONDS, self.save_genders)
        self.set_interval(INPUT_BAR_REFRESH_SECONDS, self.refresh_input_bar)
        self.chat_input.name_source = self.complete_names
        self.sidebar.name_style = self.name_style
        self.sub_title = "offline"
        await self.reset_view()
        self.query_one("#chat_input", ChatInput).focus()
        if self.config.is_complete():
            self.connect()
        else:
            self.show_login()

    def connect(self) -> None:
        self.run_worker(self.start_backend(), exclusive=True, group="backend")

    def show_login(self, message:str="") -> None:
        screen = LoginScreen(str(self.config.get("account", "")), bool(self.config.get("remember_password", True)), message)
        self.push_screen(screen, self.on_login_done)

    def on_login_done(self, credentials:Credentials | None) -> None:
        if credentials is None:
            self.exit()
            return
        self.config["account"] = credentials.account
        self.config["password"] = credentials.password
        self.config["remember_password"] = credentials.remember
        self.characters = credentials.characters
        preferred = self.match_character(str(self.config.get("character"))) or credentials.default_character
        self.choose_character(preferred)

    def choose_character(self, preferred:str="") -> None:
        self.push_screen(CharacterScreen(self.characters, preferred or self.client.character), self.on_character_chosen)

    def on_character_chosen(self, name:str | None) -> None:
        if name is None:
            if not self.online:
                self.show_login()
            return
        self.run_worker(self.switch_character(name), exclusive=True, group="backend")

    def match_character(self, name:str) -> str | None:
        name = name.strip().lower()
        return next((character for character in self.characters if character.lower() == name), None)

    async def switch_character(self, name:str) -> None:
        await self.shutdown_client()
        self.config["character"] = name
        self.config.save()
        self.client = Client(self.config, self)
        await self.reset_view()
        await self.start_backend()

    async def logout(self) -> None:
        await self.shutdown_client()
        self.config["password"] = ""
        self.config.save()
        await self.reset_view()
        self.sub_title = "offline"
        self.show_login()

    def open_link(self, url:str) -> None:
        if not is_safe_url(url):
            self.notify(f"Not opening link, only http and https are allowed: {url}", severity="warning", timeout=10)
            return
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        graphical = sys.platform == "darwin" or os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
        if graphical and not os.environ.get("SSH_CONNECTION") and shutil.which(opener):
            subprocess.Popen([opener, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            self.notify(url, title="Opening link")
            return
        self.copy_to_clipboard(url)
        self.notify(url, title="Link copied to clipboard", timeout=15)

    def status_message(self) -> str:
        return self.client.own_status.message if self.online else ""

    def update_subtitle(self) -> None:
        self.sub_title = f"{self.client.own_status.status} \u2014 as {self.client.character}"
        self.query_one(StatusHeader).refresh_title()

    def save_genders(self) -> None:
        self.client.genders.save()
        self.store_ad_draft()
        self.client.ad_drafts.save()

    def name_style(self, name:str) -> Style:
        return gender_style(self.client.genders.get(name))

    async def shutdown_client(self) -> None:
        self.save_genders()
        self.online = False
        self.workers.cancel_group(self, "reconnect")
        self.workers.cancel_group(self, "receiver")
        self.workers.cancel_group(self, "periodic")
        await self.client.stop()

    async def reset_view(self) -> None:
        if self.input_mode == "ads":
            self.leave_ad_mode()
        self.active_chat = None
        self.sidebar_dirty.add(FRIENDS)
        await self.rebuild_list()
        await self.chat_view.remove_children()
        await self.chat_view.mount(Static("No chats - press ctrl+o for the channel list or type /help", classes="placeholder"))

    async def on_unmount(self) -> None:
        self.save_genders()
        await self.client.stop()
        if self.eicons is not None:
            await self.eicons.close()

    async def start_backend(self) -> None:
        self.sub_title = "logging in..."
        result = await login.fetch_ticket(str(self.config.get("account")), str(self.config.get("password")))
        if result.error:
            self.sub_title = "offline"
            self.show_login(result.error)
            return

        self.characters = result.characters
        name = self.match_character(str(self.config.get("character")))
        if name is None:
            self.sub_title = "offline"
            self.notify(f"Character '{self.config.get('character')}' not found on this account", severity="warning")
            self.choose_character(result.default_character)
            return
        if name != self.client.character:
            self.config["character"] = name
            self.config.save()
            self.client = Client(self.config, self)

        self.sub_title = "connecting..."
        error = await self.client.start(result.ticket)
        if error:
            self.sub_title = "offline"
            self.notify(error, severity="error")
            return

        await self.after_connect()
        await self.client.restore_pins()
        defaults = self.client.config.get("default_channels") or []
        for index, channel in enumerate(defaults):
            await self.client.join(channel, open_chat=index == 0)
        self.run_worker(self.periodic_worker(), group="periodic")
        for note in self.startup_notes:
            await self.client.log_console(note)
        self.startup_notes = []
        await self.client.log_console(f"Connected as [user]{self.client.character}[/user]")
        first = self.first_chat_id()
        if not defaults and first and self.active_chat is None:
            await self.open_chat(first)

    async def after_connect(self) -> None:
        self.online = True
        self.update_subtitle()
        await self.client.restore_status()
        self.run_worker(self.client.consumer.receive(), group="receiver")

    def schedule_reconnect(self, immediate:bool=False) -> None:
        self.run_worker(self.reconnect_worker(immediate), exclusive=True, group="reconnect")

    async def reconnect_worker(self, immediate:bool) -> None:
        attempt = 0
        while not self.online:
            delay = 0 if immediate and attempt == 0 else RECONNECT_DELAYS[min(attempt, len(RECONNECT_DELAYS) - 1)]
            for remaining in range(delay, 0, -1):
                self.sub_title = f"disconnected \u2014 reconnecting in {remaining}s (/reconnect: now)"
                await asyncio.sleep(1)
            attempt += 1
            self.sub_title = "reconnecting..."
            error = await self.reconnect_once()
            if not error:
                return
            await self.client.log_console(f"Reconnect attempt {attempt} failed: {error}")

    async def reconnect_once(self) -> str | None:
        result = await login.fetch_ticket(str(self.config.get("account")), str(self.config.get("password")))
        if result.error and not result.temporary:
            self.sub_title = "offline"
            self.show_login(result.error)
            return ""
        if result.error:
            return result.error
        await self.client.stop()
        self.client.reset_connection()
        error = await self.client.start(result.ticket)
        if error:
            await self.client.stop()
            return error
        await self.after_connect()
        for chat in list(self.client.store.chats.values()):
            if chat.kind == CHANNEL:
                await self.client.join(chat.key, open_chat=False)
        self.sidebar_dirty.add(FRIENDS)
        await self.client.log_console(f"Reconnected as [user]{self.client.character}[/user]")
        self.notify("Reconnected to the chat server")
        return None

    async def periodic_worker(self) -> None:
        while True:
            removed = self.client.store.cleanup(int(self.config.get("log_keep_days", 0)))
            if removed:
                await self.client.log_console(f"Removed {removed} old log files")
            await self.client.request_channel_lists()
            await asyncio.sleep(LIST_REFRESH_SECONDS)

    async def connection_lost(self) -> None:
        self.online = False
        self.sub_title = "disconnected"
        await self.client.log_console("Connection to the chat server lost")
        await self.client.stop()
        if self.client.last_error in NO_RECONNECT_ERRORS:
            await self.client.log_console("Not reconnecting automatically after this error, use /reconnect")
            self.notify("Connection to the chat server lost, use /reconnect", severity="error", timeout=15)
            return
        self.notify("Connection to the chat server lost, reconnecting ...", severity="error", timeout=10)
        self.schedule_reconnect()

    def channel_lists_updated(self) -> None:
        if isinstance(self.screen, ChannelsList):
            self.screen.run_worker(self.screen.render_lists(), exclusive=True)

    def presence_changed(self, key:str) -> None:
        self.sidebar_dirty.add(key)

    def refresh_sidebar(self) -> None:
        if not self.sidebar_dirty or not self.sidebar.display:
            return
        self.sidebar_dirty.clear()
        presence = self.client.presence

        friends = presence.online_friends()
        self.sidebar.update_list("friends_list", "tab_friends", f"Friends ({len(friends)})", friends, "No friends online")

        chat = self.current_chat()
        if chat is None or chat.kind != CHANNEL:
            self.sidebar.update_list("members_list", "tab_channel", "Channel", [], "No channel open")
            return
        members = presence.channel_members(chat.key)
        if members is None:
            self.sidebar.update_list("members_list", "tab_channel", "Channel", [], "Loading ...")
        else:
            self.sidebar.update_list("members_list", "tab_channel", f"Channel ({len(members)})", members, "Nobody here")

    async def action_minimize(self) -> None:
        await self.client.commands.cmd_minimize("")

    def action_toggle_sidebar(self) -> None:
        self.sidebar.display = not self.sidebar.display
        if self.sidebar.display:
            chat = self.current_chat()
            self.sidebar.show_tab("tab_channel" if chat and chat.kind == CHANNEL else "tab_friends")
            self.sidebar_dirty.add("view")
            self.refresh_sidebar()

    async def on_option_list_option_selected(self, event:OptionList.OptionSelected) -> None:
        if event.option_list.id not in ("friends_list", "members_list") or event.option.id is None:
            return
        await self.client.open_private(event.option.id)
        self.query_one("#chat_input", ChatInput).focus()

    def chat_line(self, line:str) -> ChatLine:
        return ChatLine(line, self.eicons, self.eicon_height, self.name_style)

    def first_chat_id(self) -> str | None:
        chats = list(self.client.store.chats.values())
        ordered = [chat for kind in (CHANNEL, USER, CONSOLE) for chat in chats if chat.kind == kind]
        return ordered[0].id if ordered else None

    def list_entry(self, chat:Chat) -> ListItem:
        prefix = {CHANNEL: "#", CONSOLE: ">"}.get(chat.kind, "@")
        marker = "*" if chat.unread else " "
        pin = "+" if self.client.pins.is_pinned(chat) else " "
        title = html.unescape(chat.title)
        style = self.name_style(chat.key) if chat.kind == USER else Style()
        return ListItem(Label(Text.assemble(f"{marker}{pin}{prefix}", (title, style))))

    async def rebuild_list(self) -> None:
        async with self.list_lock:
            await self._rebuild_list()

    async def _rebuild_list(self) -> None:
        chats = list(self.client.store.chats.values())
        groups = [[chat for chat in chats if chat.kind == kind] for kind in (CONSOLE, CHANNEL, USER)]

        self.list_ids = []
        items = []
        for group in [group for group in groups if group]:
            if items:
                self.list_ids.append(None)
                items.append(ListItem(Label(""), disabled=True))
            for chat in group:
                self.list_ids.append(chat.id)
                items.append(self.list_entry(chat))

        await self.list_view.clear()
        if items:
            await self.list_view.extend(items)
        if self.active_chat in self.list_ids:
            self.list_view.index = self.list_ids.index(self.active_chat)

    async def open_chat(self, chat_id:str) -> None:
        chat = self.client.store.get(chat_id)
        if chat is None:
            return
        if self.input_mode == "ads" and chat.key != self.ad_channel:
            if chat.kind == CHANNEL:
                self.store_ad_draft()
                self.ad_channel = chat.key
                self.chat_input.set_text(self.client.ad_drafts.get(chat.key))
            else:
                self.leave_ad_mode()
        self.active_chat = chat_id
        chat.unread = False
        self.sidebar_dirty.add("view")
        if self.sidebar.display:
            self.sidebar.show_tab("tab_channel" if chat.kind == CHANNEL else "tab_friends")
            self.refresh_sidebar()

        await self.chat_view.remove_children()
        lines = self.client.store.history(chat)
        if chat.kind == CHANNEL and not self.client.ads.visible(chat.key):
            lines = [line for line in lines if not is_ad_line(line)]
        widgets = [self.chat_line(line) for line in lines] or [Static("No messages yet", classes="placeholder")]
        await self.chat_view.mount_all(widgets)
        self.chat_view.scroll_end(animate=False)
        self.update_input_mode()
        await self.rebuild_list()

    async def show_line(self, chat_id:str, line:str) -> None:
        if chat_id == self.active_chat:
            await self.chat_view.query(".placeholder").remove()
            await self.chat_view.mount(self.chat_line(line))
            self.chat_view.scroll_end(animate=False)
            return
        chat = self.client.store.get(chat_id)
        if chat is not None:
            chat.unread = True
        await self.rebuild_list()

    async def chat_removed(self, chat_id:str) -> None:
        if chat_id != self.active_chat:
            await self.rebuild_list()
            return
        self.active_chat = None
        first = self.first_chat_id()
        if first:
            await self.open_chat(first)
            return
        await self.chat_view.remove_children()
        await self.chat_view.mount(Static("No chats", classes="placeholder"))
        await self.rebuild_list()

    async def on_list_view_selected(self, event:ListView.Selected) -> None:
        if event.list_view.id != "chat_list":
            return
        index = event.list_view.index
        if index is not None and 0 <= index < len(self.list_ids) and self.list_ids[index]:
            await self.open_chat(self.list_ids[index])
            self.query_one("#chat_input", ChatInput).focus()

    def action_open_channels_list(self) -> None:
        if not isinstance(self.screen, ChannelsList):
            self.push_screen(ChannelsList(self.client))

    async def action_close_chat(self) -> None:
        chat = self.current_chat()
        if chat is None:
            return
        if chat.kind == CONSOLE:
            self.notify("The console cannot be closed", severity="warning")
            return
        if chat.kind == CHANNEL:
            await self.client.leave(chat.key)
        self.client.store.remove(chat.id)
        await self.chat_removed(chat.id)

    def on_text_area_changed(self, event:TextArea.Changed) -> None:
        if event.text_area.id == "chat_input":
            self.query_one(CommandHints).show_for(event.text_area.text)
            self.store_ad_draft()
            self.refresh_input_bar()

    def complete_names(self, prefix:str) -> list[str]:
        chat = self.current_chat()
        code = chat.key if chat is not None and chat.kind == CHANNEL else None
        names = self.client.presence.complete_names(prefix, code)
        if chat is not None and chat.kind == USER:
            names.sort(key=lambda name: name.lower() != chat.key.lower())
        return names

    def store_ad_draft(self) -> None:
        if self.input_mode != "ads" or not self.ad_channel:
            return
        try:
            text = self.chat_input.text
        except NoMatches:
            return
        if not text.startswith("/"):
            self.client.ad_drafts.set(self.ad_channel, text)

    def leave_ad_mode(self) -> None:
        self.store_ad_draft()
        self.client.ad_drafts.save()
        self.input_mode = "chat"
        self.ad_channel = None
        self.chat_input.set_text(self.chat_draft)
        self.update_input_mode()

    def set_input_mode(self, mode:str) -> None:
        if mode == self.input_mode:
            return
        if mode == "chat":
            self.leave_ad_mode()
        else:
            chat = self.current_chat()
            if chat is None or chat.kind != CHANNEL:
                self.notify("Ads can only be posted in channels", severity="warning")
                return
            self.chat_draft = self.chat_input.text
            self.input_mode = "ads"
            self.ad_channel = chat.key
            self.chat_input.set_text(self.client.ad_drafts.get(chat.key))
            self.update_input_mode()
        self.chat_input.focus()

    def action_emoji(self, query:str="") -> None:
        if not isinstance(self.screen, EmojiScreen):
            self.push_screen(EmojiScreen(query), self.insert_emoji)

    def insert_emoji(self, emoji:str | None) -> None:
        box = self.chat_input
        if emoji:
            box.insert(emoji)
        box.focus()

    def action_toggle_ad_mode(self) -> None:
        self.set_input_mode("chat" if self.input_mode == "ads" else "ads")

    def on_input_mode_bar_mode_selected(self, event:InputModeBar.ModeSelected) -> None:
        self.set_input_mode(event.mode)

    def update_input_mode(self) -> None:
        box = self.chat_input
        box.history_enabled = self.input_mode == "chat"
        if self.input_mode == "ads":
            chat = self.current_chat()
            title = html.unescape(chat.title) if chat else self.ad_channel
            box.placeholder = f"Ad for {title} - enter posts it, the text stays  (ctrl+r: chat)"
        else:
            box.placeholder = CHAT_PLACEHOLDER
        self.refresh_input_bar()

    def input_limit(self, chat:Chat | None) -> int | None:
        if chat is None or chat.kind == CONSOLE:
            return None
        if self.input_mode == "ads":
            name = "lfrp_max"
        else:
            name = "chat_max" if chat.kind == CHANNEL else "priv_max"
        return int(self.client.variables.get(name, 50000))

    def refresh_input_bar(self) -> None:
        try:
            bar = self.query_one("#input_bar", InputModeBar)
        except NoMatches:
            return
        chat = self.current_chat()
        limit = self.input_limit(chat)
        info = Text()
        if self.input_mode == "ads" and self.ad_channel:
            wait = self.client.ad_wait_seconds(self.ad_channel)
            if wait:
                minutes, seconds = divmod(wait, 60)
                info.append(f"next ad in {minutes}:{seconds:02d}   ")
        if limit is not None:
            length = len(self.chat_input.text)
            info.append(f"{length} / {limit}", "bold red" if length > limit else "")
        bar.show(info, self.input_mode, chat is not None and chat.kind == CHANNEL)

    async def on_chat_input_submitted(self, event:ChatInput.Submitted) -> None:
        if event.value.strip() and not event.value.startswith("/") and not self.online:
            self.notify("Not connected, message not sent (/reconnect to try now)", severity="warning")
            return
        if self.input_mode == "ads" and not event.value.startswith("/"):
            if event.value.strip():
                await self.client.commands.cmd_ad(event.value.strip())
            self.store_ad_draft()
            self.client.ad_drafts.save()
            self.refresh_input_bar()
            return

        text = event.value.strip()
        event.chat_input.set_text("")
        if not text:
            return
        event.chat_input.remember(text)

        if text.startswith("/"):
            await self.client.commands.handle(text)
            if self.input_mode == "ads" and self.ad_channel and not self.chat_input.text:
                self.chat_input.set_text(self.client.ad_drafts.get(self.ad_channel))
            return

        chat = self.current_chat()
        if chat is None:
            self.notify("No chat open", severity="warning")
            return
        if chat.kind == CONSOLE:
            self.notify("The console is read-only, use /commands here", severity="warning")
            return
        await self.client.send(chat, text)


def build_app() -> ChatApp:
    config_file = paths.config_file()
    notes = [paths.migrate_config(config_file)]
    config = Config(str(config_file))
    config.data_dir = paths.data_dir(config.get("data_dir"))
    notes.append(paths.migrate_data(config.data_dir))
    set_log_dir(config.data_dir)

    app = ChatApp(config)
    app.startup_notes = [note for note in notes if note]
    app.startup_notes.append(f"Config: {config.path} | Data: {config.data_dir}")
    return app


def main() -> None:
    build_app().run()


if __name__ == "__main__":
    main()
