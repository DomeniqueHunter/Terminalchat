import asyncio
import html
import os
import re
from typing import Any, Awaitable, Callable

from rich.style import Style
from rich.text import Text

from bbcode import to_text
from chat_store import CHANNEL, CONSOLE
from color_config import STATUS_STYLES, make_style
from fchat import Opcode as opcode
from own_status import MAX_MESSAGE_LENGTH, VALID_STATUSES
from panels.edit_panel import EditScreen
from panels.info_panel import InfoScreen


DEFAULT_DICE = "1d6"
DICE_PATTERN = re.compile(r"^(\d*d\d+|\d+)([+-](\d*d\d+|\d+))*$")


COMMAND_INFO = [
    ("join", "<channel>", "join a channel (name or code)"),
    ("leave", "", "leave / close the current chat"),
    ("priv", "<name>", "open a private chat"),
    ("invite", "<name>", "invite a character into the current channel"),
    ("code", "", "copy the current channel as [session] link"),
    ("makeroom", "<title>", "create a private channel"),
    ("openroom", "", "make the current private channel public"),
    ("closeroom", "", "make the current private channel invite-only"),
    ("kick", "<name>", "kick a character from the current channel"),
    ("ban", "<name>", "ban a character from the current channel"),
    ("unban", "<name>", "unban a character"),
    ("banlist", "", "show the ban list of the current channel"),
    ("timeout", "<name> <minutes>", "time out a character"),
    ("op", "<name>", "make a character channel operator"),
    ("deop", "<name>", "remove channel operator rights"),
    ("setowner", "<name>", "hand the channel over to a character"),
    ("setdescription", "<text>", "set the channel description"),
    ("setmode", "<chat|ads|both>", "allow chat, ads or both"),
    ("me", "<text>", "emote in the current chat"),
    ("ad", "<text>", "post a role play ad in the current channel"),
    ("roll", "[dice]", "roll dice on the server, e.g. 2d6+3 (default 1d6)"),
    ("bottle", "", "spin the bottle (channels only)"),
    ("status", "[status] [text]", "set status and/or status message"),
    ("status:flag", "<status>", "change only the status"),
    ("status:message", "[text]", "change only the message; without text opens an editor"),
    ("channels", "", "open the channel list"),
    ("users", "", "show/hide friends and channel users"),
    ("pin", "", "pin the current chat, restored on start"),
    ("unpin", "", "unpin the current chat"),
    ("pins", "", "show pinned chats"),
    ("ads", "[on|off]", "show or hide ads in the current channel"),
    ("gif", "[on|off]", "toggle animated eicons"),
    ("char", "[name]", "switch character"),
    ("reconnect", "", "reconnect to the chat server now"),
    ("logout", "", "log out and forget password"),
    ("minimize", "", "detach, keep running in background"),
    ("chatstatus", "", "show the partner's status or the channel description"),
    ("help", "", "show all commands"),
    ("shortcuts", "", "show all key bindings"),
    ("quit", "", "exit"),
]

COMMAND_NAMES = [name for name, _, _ in COMMAND_INFO]

COMMAND_ALIASES = {"close": "leave", "create": "makeroom", "detach": "minimize", "keys": "shortcuts"}


def command_usage(name:str, args:str) -> str:
    return f"/{name} {args}".rstrip()


def matching_commands(prefix:str) -> list[tuple[str, str, str]]:
    prefix = prefix.lower()
    return [entry for entry in COMMAND_INFO if entry[0].startswith(prefix)]


HELP_TEXT = "\n".join(f"{command_usage(name, args):<26} {description}" for name, args, description in COMMAND_INFO)

SHORTCUT_INFO = [
    ("enter", "send the message (Ads mode: post the ad)"),
    ("shift+enter", "new line (if the terminal supports it)"),
    ("ctrl+enter", "new line (if the terminal supports it)"),
    ("ctrl+j / alt+enter", "new line (works everywhere)"),
    ("up / down", "move between lines, then browse sent input"),
    ("tab", "complete a command or character name"),
    ("ctrl+tab", "previous name match"),
    ("ctrl+r", "switch input between Chat and Ads"),
    ("ctrl+o", "open the channel list"),
    ("ctrl+l", "leave / close the current chat"),
    ("ctrl+f", "show/hide friends and channel users"),
    ("ctrl+t", "minimize (detach, keep running)"),
    ("ctrl+p", "command palette"),
    ("ctrl+q", "quit"),
    ("escape", "close a dialog"),
    ("click title bar", "show/hide your status message"),
    ("click link", "open it in the browser"),
]

SHORTCUTS_TEXT = "\n".join(f"{key:<20} {description}" for key, description in SHORTCUT_INFO)


def unquote(text:str) -> str:
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1].strip()
    return text


class ChatCommands:

    def __init__(self, client:Any) -> None:
        self.client = client
        self.commands: dict[str, Callable[[str], Awaitable[None]]] = {
            "join": self.cmd_join,
            "leave": self.cmd_leave,
            "close": self.cmd_leave,
            "priv": self.cmd_priv,
            "invite": self.cmd_invite,
            "code": self.cmd_code,
            "makeroom": self.cmd_makeroom,
            "create": self.cmd_makeroom,
            "openroom": self.cmd_openroom,
            "closeroom": self.cmd_closeroom,
            "kick": self.cmd_kick,
            "ban": self.cmd_ban,
            "unban": self.cmd_unban,
            "banlist": self.cmd_banlist,
            "timeout": self.cmd_timeout,
            "op": self.cmd_op,
            "deop": self.cmd_deop,
            "setowner": self.cmd_setowner,
            "setdescription": self.cmd_setdescription,
            "setmode": self.cmd_setmode,
            "me": self.cmd_me,
            "ad": self.cmd_ad,
            "roll": self.cmd_roll,
            "bottle": self.cmd_bottle,
            "status": self.cmd_status,
            "status:flag": self.cmd_status_flag,
            "status:message": self.cmd_status_message,
            "channels": self.cmd_channels,
            "users": self.cmd_users,
            "pin": self.cmd_pin,
            "unpin": self.cmd_unpin,
            "pins": self.cmd_pins,
            "ads": self.cmd_ads,
            "gif": self.cmd_gif,
            "char": self.cmd_char,
            "reconnect": self.cmd_reconnect,
            "logout": self.cmd_logout,
            "minimize": self.cmd_minimize,
            "detach": self.cmd_minimize,
            "chatstatus": self.cmd_chatstatus,
            "help": self.cmd_help,
            "shortcuts": self.cmd_shortcuts,
            "keys": self.cmd_shortcuts,
            "quit": self.cmd_quit,
        }

    @property
    def app(self) -> Any:
        return self.client.app

    async def handle(self, text:str) -> None:
        name, _, args = text[1:].partition(" ")
        func = self.commands.get(name.lower())
        if func is None:
            self.app.notify(f"Unknown command: /{name}  (see /help)", severity="warning")
            return
        await func(args.strip())

    async def cmd_join(self, args:str) -> None:
        if not args:
            self.app.notify("Usage: /join <channel>", severity="warning")
            return
        await self.client.join(unquote(args))

    async def cmd_leave(self, args:str) -> None:
        await self.app.action_close_chat()

    async def cmd_priv(self, args:str) -> None:
        if not args:
            self.app.notify("Usage: /priv <character>", severity="warning")
            return
        await self.client.open_private(unquote(args))

    def current_conversation(self) -> Any:
        chat = self.app.current_chat()
        if chat is None or chat.kind == CONSOLE:
            self.app.notify("Open a channel or private chat first", severity="warning")
            return None
        return chat

    async def cmd_me(self, args:str) -> None:
        chat = self.current_conversation()
        if chat is None or not args:
            return
        await self.client.send(chat, f"/me {args}")

    async def cmd_ad(self, args:str) -> None:
        chat = self.current_channel()
        if chat is None:
            return
        message = args.strip()
        if not message:
            self.app.notify("Usage: /ad <text>", severity="warning")
            return
        limit = int(self.client.variables.get("lfrp_max", 50000))
        if len(message) > limit:
            self.app.notify(f"Ad too long ({len(message)}/{limit})", severity="warning")
            return
        wait = self.client.ad_wait_seconds(chat.key)
        if wait:
            minutes, seconds = divmod(wait, 60)
            self.app.notify(f"You can post the next ad in {chat.title} in {minutes}:{seconds:02d} min", severity="warning")
            return
        await self.client.send_ad(chat, message)

    async def cmd_invite(self, args:str) -> None:
        chat = self.app.current_chat()
        if chat is None or chat.kind != CHANNEL:
            self.app.notify("/invite only works in a channel", severity="warning")
            return
        name = unquote(args)
        if not name:
            self.app.notify("Usage: /invite <character>", severity="warning")
            return
        name = self.client.find_online(name) or name
        await self.client.invite(chat.key, name)
        self.app.notify(f"Invited {name} to {chat.title}")

    def current_channel(self) -> Any:
        chat = self.app.current_chat()
        if chat is None or chat.kind != CHANNEL:
            self.app.notify("This command only works in a channel", severity="warning")
            return None
        return chat

    async def channel_name_command(self, op:str, args:str, usage:str) -> None:
        chat = self.current_channel()
        if chat is None:
            return
        name = unquote(args)
        if not name:
            self.app.notify(f"Usage: {usage}", severity="warning")
            return
        name = self.client.find_online(name) or name
        await self.client.channel_command(op, {"channel": chat.key, "character": name})

    async def cmd_code(self, args:str) -> None:
        chat = self.current_channel()
        if chat is None:
            return
        code = f"[session={html.unescape(chat.title)}]{chat.key}[/session]"
        self.app.copy_to_clipboard(code)
        self.app.notify(code, title="Channel code copied to clipboard", timeout=15)

    async def cmd_makeroom(self, args:str) -> None:
        title = unquote(args)
        if not title:
            self.app.notify("Usage: /makeroom <title>", severity="warning")
            return
        await self.client.create_room(title)

    async def cmd_openroom(self, args:str) -> None:
        chat = self.current_channel()
        if chat is not None:
            await self.client.channel_command(opcode.SET_PRIVATE_CHANNEL_STATE, {"channel": chat.key, "status": "public"})

    async def cmd_closeroom(self, args:str) -> None:
        chat = self.current_channel()
        if chat is not None:
            await self.client.channel_command(opcode.SET_PRIVATE_CHANNEL_STATE, {"channel": chat.key, "status": "private"})

    async def cmd_kick(self, args:str) -> None:
        await self.channel_name_command(opcode.KICK, args, "/kick <name>")

    async def cmd_ban(self, args:str) -> None:
        await self.channel_name_command(opcode.BAN, args, "/ban <name>")

    async def cmd_unban(self, args:str) -> None:
        await self.channel_name_command(opcode.UNBAN, args, "/unban <name>")

    async def cmd_op(self, args:str) -> None:
        await self.channel_name_command(opcode.PROMOTE_OP, args, "/op <name>")

    async def cmd_deop(self, args:str) -> None:
        await self.channel_name_command(opcode.DEMOTE_OP, args, "/deop <name>")

    async def cmd_setowner(self, args:str) -> None:
        await self.channel_name_command(opcode.SET_CHANNEL_OWNER, args, "/setowner <name>")

    async def cmd_banlist(self, args:str) -> None:
        chat = self.current_channel()
        if chat is not None:
            await self.client.channel_command(opcode.BANLIST, {"channel": chat.key})

    async def cmd_timeout(self, args:str) -> None:
        chat = self.current_channel()
        if chat is None:
            return
        name_part, _, minutes = args.strip().rpartition(" ")
        name = unquote(name_part)
        if not name or not minutes.isdigit() or int(minutes) < 1:
            self.app.notify("Usage: /timeout <name> <minutes>", severity="warning")
            return
        name = self.client.find_online(name) or name
        payload = {"channel": chat.key, "character": name, "length": int(minutes)}
        await self.client.channel_command(opcode.TIMEOUT, payload)

    async def cmd_setdescription(self, args:str) -> None:
        chat = self.current_channel()
        if chat is None:
            return
        if not args.strip():
            self.app.notify("Usage: /setdescription <text>", severity="warning")
            return
        await self.client.channel_command(opcode.CHANNEL_DESCRIPTION, {"channel": chat.key, "description": args.strip()})

    async def cmd_setmode(self, args:str) -> None:
        chat = self.current_channel()
        if chat is None:
            return
        mode = args.strip().lower()
        if mode not in ("chat", "ads", "both"):
            self.app.notify("Usage: /setmode <chat|ads|both>", severity="warning")
            return
        await self.client.channel_command(opcode.SET_CHANNEL_MODE, {"channel": chat.key, "mode": mode})

    async def cmd_roll(self, args:str) -> None:
        chat = self.current_conversation()
        if chat is None:
            return
        dice = args.replace(" ", "").lower() or DEFAULT_DICE
        if not DICE_PATTERN.match(dice):
            self.app.notify(f"Invalid dice '{args.strip()}', e.g. /roll 1d20 or /roll 2d6+3", severity="warning")
            return
        await self.client.roll(chat, dice)

    async def cmd_bottle(self, args:str) -> None:
        chat = self.app.current_chat()
        if chat is None or chat.kind != CHANNEL:
            self.app.notify("/bottle only works in channels", severity="warning")
            return
        await self.client.roll(chat, "bottle")

    async def cmd_pin(self, args:str) -> None:
        chat = self.current_conversation()
        if chat is None:
            return
        if self.client.pins.pin(chat):
            self.app.notify(f"Pinned {chat.title}")
        await self.app.rebuild_list()

    async def cmd_unpin(self, args:str) -> None:
        chat = self.app.current_chat()
        if chat is None:
            self.app.notify("No chat open", severity="warning")
            return
        if self.client.pins.unpin(chat):
            self.app.notify(f"Unpinned {chat.title}")
        await self.app.rebuild_list()

    async def cmd_pins(self, args:str) -> None:
        items = self.client.pins.items
        if not items:
            self.app.notify("No pinned chats")
            return
        lines = [f"{'#' if item['kind'] == 'channel' else '@'}{item.get('title') or item['key']}" for item in items]
        self.app.notify("\n".join(lines), title="Pinned", timeout=10)

    async def cmd_ads(self, args:str) -> None:
        chat = self.current_channel()
        if chat is None:
            return
        value = args.strip().lower()
        if value not in ("", "on", "off"):
            self.app.notify("Usage: /ads [on|off]", severity="warning")
            return
        if value:
            self.client.ads.set_visible(chat.key, value == "on")
            await self.app.open_chat(chat.id)
        state = "shown" if self.client.ads.visible(chat.key) else "hidden"
        self.app.notify(f"Ads in {chat.title}: {state}")

    async def cmd_gif(self, args:str) -> None:
        value = args.lower()
        if value in ("on", "off"):
            self.app.gif_enabled = value == "on"
        elif value:
            self.app.notify("Usage: /gif [on|off]", severity="warning")
            return
        else:
            self.app.gif_enabled = not self.app.gif_enabled
        self.app.notify(f"Animated eicons {'on' if self.app.gif_enabled else 'off'}")

    async def cmd_char(self, args:str) -> None:
        if not self.app.characters:
            self.app.notify("Character list not available yet", severity="warning")
            return
        name = unquote(args)
        if not name:
            self.app.choose_character()
            return
        match = self.app.match_character(name)
        if match is None:
            self.app.notify(f"'{name}' is not a character of this account", severity="warning")
        elif match == self.client.character:
            self.app.notify(f"Already logged in as {match}")
        else:
            self.app.run_worker(self.app.switch_character(match), exclusive=True, group="backend")

    async def cmd_logout(self, args:str) -> None:
        await self.app.logout()

    async def cmd_minimize(self, args:str) -> None:
        if not os.environ.get("TMUX"):
            self.app.notify("/minimize needs the 'terminalchat' launcher (runs inside tmux)", severity="warning")
            return
        process = await asyncio.create_subprocess_exec(
            "tmux", "detach-client", stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
        )
        if await process.wait() != 0:
            self.app.notify("Could not detach from tmux", severity="error")

    async def cmd_users(self, args:str) -> None:
        self.app.action_toggle_sidebar()

    async def cmd_status(self, args:str) -> None:
        own = self.client.own_status
        if not args:
            message = f": {own.message}" if own.message else ""
            self.app.notify(f"Status {own.status}{message}\nUsage: /status [{'|'.join(VALID_STATUSES)}] [message]",
                            title="Status", timeout=8)
            return
        first, _, rest = args.partition(" ")
        if first.lower() in VALID_STATUSES:
            status, message = first.lower(), rest.strip()
        else:
            status, message = own.status, args.strip()
        await self.apply_status(status, message)

    async def cmd_status_flag(self, args:str) -> None:
        own = self.client.own_status
        status = args.strip().lower()
        if not status:
            self.app.notify(f"Status {own.status}\nUsage: /status:flag <{'|'.join(VALID_STATUSES)}>", title="Status", timeout=8)
            return
        if status not in VALID_STATUSES:
            self.app.notify(f"Unknown status '{status}', use one of: {', '.join(VALID_STATUSES)}", severity="warning")
            return
        await self.apply_status(status, own.message)

    async def cmd_status_message(self, args:str) -> None:
        if args.strip():
            await self.apply_status(self.client.own_status.status, args.strip())
            return
        screen = EditScreen("Status message", self.client.own_status.message, MAX_MESSAGE_LENGTH)
        self.app.push_screen(screen, self.on_status_message_edited)

    def on_status_message_edited(self, message:str | None) -> None:
        if message is not None and message != self.client.own_status.message:
            self.app.run_worker(self.apply_status(self.client.own_status.status, message))

    async def apply_status(self, status:str, message:str) -> None:
        if len(message) > MAX_MESSAGE_LENGTH:
            self.app.notify(f"Status message too long ({len(message)}/{MAX_MESSAGE_LENGTH})", severity="warning")
            return
        self.client.own_status.set(status, message)
        if self.app.online:
            await self.client.send_status()
            self.app.update_subtitle()
        self.app.notify(f"Status set to {status}" + (f": {message}" if message else ""))

    async def cmd_channels(self, args:str) -> None:
        self.app.action_open_channels_list()

    async def cmd_reconnect(self, args:str) -> None:
        if self.app.online:
            self.app.notify("Already connected")
            return
        self.app.schedule_reconnect(immediate=True)

    async def cmd_chatstatus(self, args:str) -> None:
        chat = self.app.current_chat()
        if chat is None or chat.kind == CONSOLE:
            self.app.notify("Open a private chat or a channel first", severity="warning")
            return
        title = html.unescape(chat.title)
        text = Text()
        if chat.kind == CHANNEL:
            members = self.client.presence.channel_members(chat.key)
            text.append(title, "bold")
            text.append(f"\n{chat.key}", "dim")
            if members is not None:
                text.append(f"  ·  {len(members)} users", "dim")
            description = self.client.descriptions.get(chat.key, "")
            text.append("\n\n")
            text.append_text(to_text(description, False) if description.strip() else Text("(no description)", "dim"))
            self.app.push_screen(InfoScreen("Channel description", text, wide=True))
            return
        text.append(title, self.app.name_style(chat.key) + Style(bold=True))
        state = self.client.presence.status_of(chat.key)
        if state is None:
            text.append("\noffline", "dim")
        else:
            status, message = state
            text.append(f"\n{status}", make_style(STATUS_STYLES.get(status, "")))
            text.append("\n\n")
            text.append_text(to_text(message, False) if message.strip() else Text("(no status message)", "dim"))
        self.app.push_screen(InfoScreen("Status", text, wide=len(text.plain) > 60))

    async def cmd_help(self, args:str) -> None:
        self.app.push_screen(InfoScreen("Commands", HELP_TEXT))

    async def cmd_shortcuts(self, args:str) -> None:
        self.app.push_screen(InfoScreen("Shortcuts", SHORTCUTS_TEXT))

    async def cmd_quit(self, args:str) -> None:
        self.app.exit()


def main() -> None:
    pass


if __name__ == "__main__":
    main()
