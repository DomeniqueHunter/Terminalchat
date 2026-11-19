import asyncio
import json
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from fastapi import WebSocket
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from ..accounts import Account
from ..config import (CLOSE_UNAUTHORIZED, MAX_CHARS_PER_ACCOUNT, WEEKDAYS, WORLD_DAY_SECONDS,
                      YEAR_DAYS)
from ..content import ITEMS
from ..controller import GameController, profile_text
from ..create_form import evaluate
from ..models import Message, Player
from ..settings import fill
from ..main_char import MainChar
from . import audience, chat, create, furnish, stash, tabs, tools, trade, views, visit
from .ribbon import biome_ribbon


TICK_SECONDS = 1.0
HISTORY = 300
TEMPLATES = Path(__file__).parent / "templates"


def resolve_tokens(value:Any) -> Any:
    if isinstance(value, str) and not isinstance(value, Markup):
        return fill(value)
    return value


ENVIRONMENT = Environment(loader=FileSystemLoader(TEMPLATES),
                          autoescape=select_autoescape(["html"]),
                          finalize=resolve_tokens)
GUARDED = ("hit", "guard")
PLACES = ("shop", "smith", "clinic")


@dataclass
class Client:
    socket: WebSocket
    viewer: str = ""
    prefix: str = ""
    ambient_off: set[str] = field(default_factory=set)
    account: Account | None = None
    admin_seen: bool = False
    powers: bool = True
    find_lobbies: bool = False
    stash: str = ""
    house: bool = False
    house_slot: str = ""


def assets_version() -> int:
    folder = Path(__file__).parent / "static"
    return int(max(path.stat().st_mtime for path in folder.iterdir()))


def mail_text(data:dict[str, Any]) -> str:
    def field(key:str) -> str:
        value = data.get(key, "")
        if isinstance(value, list):
            value = next((entry for entry in value if str(entry).strip()),
                         "")
        return str(value).replace("|", "/").strip()

    parts = [field(key) for key in ("mail_to", "mail_subject", "mail_body",
                                    "mail_gold", "mail_item")]
    parts[0] = field("mail_name") or parts[0]
    return "!mail send " + " | ".join(parts) if parts[0] else ""


class GameHub:
    def __init__(self, data_dir:Path, debug:bool=False,
                 login:bool=False) -> None:
        self.debug = debug
        self.login = login
        self.data_dir = data_dir
        self.controller = GameController(data_dir, debug=debug)
        self.store = self.controller.repository.store
        self.store.clear_admins()
        self.mains: dict[str, MainChar] = {}
        self.limiter = chat.Limiter()
        self.auto_time = True
        self.clients: list[Client] = []
        self.history: dict[str, deque[dict[str, str]]] = {}
        self.ticker: asyncio.Task | None = None
        self.last_online: set[str] = set()
        self.controller.online = lambda: {
            client.viewer for client in self.clients if client.viewer}
        self.controller.is_admin = lambda name: any(
            client.viewer == name and self.powers(client)
            for client in self.clients)
        self.controller.town.online = lambda: {
            client.viewer for client in self.clients if client.viewer}

    def render(self, name:str, **values:Any) -> str:
        return ENVIRONMENT.get_template(name).render(**values)

    def player(self, name:str):
        return self.controller.repository.load(name) if name else None

    def main_of(self, client:Client) -> MainChar:
        scope = client.account.id if client.account else ""
        if scope not in self.mains:
            self.mains[scope] = MainChar(self.data_dir, scope)
        return self.mains[scope]

    def admin(self, client:Client) -> bool:
        if not self.login:
            return False
        fresh = (self.store.by_id(client.account.id)
                 if client.account else None)
        return bool(fresh and fresh.admin)

    def powers(self, client:Client) -> bool:
        return client.powers and self.admin(client)

    def tools_on(self, client:Client) -> bool:
        return self.debug or self.powers(client)

    def visible(self, client:Client) -> list[str]:
        if not self.login:
            return views.known_players(self.controller)
        if client.account is None:
            return []
        rows = self.store.characters_of(client.account.id)
        return sorted((row["handle"] for row in rows if not row["npc"]),
                      key=str.casefold)

    def page(self, client:Client | None=None) -> str:
        tools = self.debug if client is None else self.tools_on(client)
        return self.render("page.html", assets=assets_version(),
                           spells=views.spell_choices(None),
                           debug=tools, form=create.form_context(),
                           account=client.account if client else None)

    def panels_for(self, client:Client) -> str:
        with self.controller.lobbies.focus(client.viewer):
            return self.build_panels(client)

    def build_panels(self, client:Client) -> str:
        controller = self.controller
        viewer = self.player(client.viewer)
        players = sorted({*self.visible(client),
                          *([client.viewer] if client.viewer else [])},
                         key=str.casefold)
        main = self.main_of(client)
        context: dict[str, Any] = {
            "viewer": client.viewer, "players": players,
            "stage": views.stage_text(controller, viewer),
            "main": main.name, "debug": self.tools_on(client),
            "world": {"day": controller.town.world.day,
                      "elapsed": round(controller.town.world.elapsed(), 1),
                      "length": WORLD_DAY_SECONDS,
                      "year_days": YEAR_DAYS,
                      "weekdays": ",".join(WEEKDAYS)},
            "account_name": client.account.name if client.account else "",
            "is_admin": bool(client.account) and self.admin(client),
            "admin_on": self.powers(client),
            "auto_time": self.auto_time,
            "status": views.status_text(controller),
            "slots": views.slot_rows(controller, client.viewer,
                                     main.name),
            "hire": views.hire_options(controller, client.viewer, [
                name for name in players if name != client.viewer]),
            "encounter": views.encounter_buttons(controller, client.viewer),
            "hits": views.hit_rows(controller),
            "party_buttons": views.party_buttons(controller, client.viewer),
            "death_note": views.death_note(controller, client.viewer),
            "party_rows": views.party_rows(controller, client.viewer),
            "profile_buttons": views.PROFILE_BUTTONS,
            "combat_buttons": views.COMBAT_BUTTONS_LEFT,
            "debug_buttons": views.DEBUG_BUTTONS,
            "targets": views.target_choices(controller),
            "visit": None, "sex": None, "visit_label": "", "sex_label": "",
            "free": 0, "character": None, "inventory": None,
            "party": None, "family": None, "contacts": [], "location": [],
            "friends": [], "lobby": None, "stash": None, "house": None, "w_names": [], "ribbon": None,
            "mail": None,
        }
        if viewer is not None:
            state = visit.current_visit(controller, viewer)
            if state is not None:
                context["visit"] = visit.visit_panel(controller, viewer,
                                                     state)
                context["visit_label"] = f"Home – {state['host']}"
            sex = visit.sex_panel(controller, viewer)
            if sex is not None:
                context["sex"] = sex
            context.update(
                free=viewer.free_points,
                character=tabs.character_tab(controller, viewer),
                inventory=tabs.inventory_tab(controller, viewer),
                party=tabs.party_tab(controller, viewer),
                lobby=(tabs.lobby_overlay(controller, viewer)
                       if client.find_lobbies else None),
                stash=self.stash_overlay(client, viewer),
                house=self.house_overlay(client, viewer),
                friends=tabs.friend_panels(controller, viewer),
                w_names=tabs.whisper_names(controller, viewer),
                family=tabs.family_tab(controller, viewer),
                mail=tabs.mail_tab(controller, viewer),
                contacts=tabs.contacts_tab(controller, viewer),
                location=views.location_panel(
                    controller, viewer, frozenset(client.ambient_off)),
                run_shop=controller.session.in_run(viewer.name),
                ribbon=biome_ribbon(controller.session, viewer))
        return self.render("panels.html", **context)

    def stash_overlay(self, client:Client, viewer:Player) -> dict | None:
        if not client.stash:
            return None
        found = stash.overlay(self.controller, viewer, client.stash)
        if found is None:
            client.stash = ""
        return found

    def house_overlay(self, client:Client, viewer:Player) -> dict | None:
        if not client.house:
            return None
        found = furnish.overlay(self.controller, viewer, client.house_slot)
        if found is None:
            client.house = False
            client.house_slot = ""
        return found

    def log_html(self, entries:list[dict[str, str]],
                 mode:str="beforeend") -> str:
        return self.render("log.html", entries=entries, mode=mode)

    def shown(self, client:Client, entry:dict[str, str]) -> bool:
        if entry.get("kind") == "witness":
            return "witness" not in client.ambient_off
        return not (entry.get("kind") == "ambient"
                    and entry.get("place") in client.ambient_off)

    def log_of(self, client:Client) -> list[dict[str, str]]:
        return [entry for entry in self.history.get(client.viewer, ())
                if self.shown(client, entry)]

    def replace_log(self, client:Client) -> str:
        return self.log_html(self.log_of(client), "innerHTML")

    def toggle_ambient(self, client:Client, place:str) -> None:
        if place not in (*views.AMBIENT_PLACES, "witness"):
            return
        client.ambient_off ^= {place}
        client.prefix = self.replace_log(client)

    async def connect(self, socket:WebSocket,
                      account:Account | None=None) -> Client:
        await socket.accept()
        client = Client(socket, account=account)
        self.clients.append(client)
        own = self.visible(client)
        main = self.main_of(client).name
        chosen = main if main in own else own[0] if len(own) == 1 else ""
        if chosen:
            client.viewer = chosen
            client.prefix = self.replace_log(client)
        await self.push(client, self.replace_log(client),
                        self.panels_for(client))
        return client

    def disconnect(self, client:Client) -> None:
        if client in self.clients:
            self.clients.remove(client)

    async def push(self, client:Client, *fragments:str) -> None:
        try:
            text = "".join((client.prefix, *fragments))
            client.prefix = ""
            await client.socket.send_text(text)
        except RuntimeError:
            self.disconnect(client)

    async def broadcast(self, items:list[audience.Item]) -> None:
        everyone = views.known_players(self.controller)
        for found, entry in items:
            for name in (everyone if found is None else found):
                self.history.setdefault(name, deque(maxlen=HISTORY)).append(
                    entry)
        for client in list(self.clients):
            visible = [entry for found, entry in items
                       if (found is None or client.viewer in found)
                       and self.shown(client, entry)]
            log = self.log_html(visible) if visible else ""
            await self.push(client, log, self.panels_for(client))

    async def tell(self, client:Client, entries:list[dict[str, str]]) -> None:
        await self.push(client, self.log_html(entries),
                        self.panels_for(client))

    def command_text(self, data:dict[str, Any]) -> str:
        text = str(data.get("text", "")).strip()
        name = text[1:].split(" ")[0].lower() if text.startswith("!") else ""
        target = str(data.get("target", "")).strip()
        if name in GUARDED and text == f"!{name}" and target:
            return f"{text} {target}"
        if name in ("hire", "dismiss") and text == f"!{name}":
            chosen = str(data.get("hire", "")).strip()
            return f"{text} {chosen}" if chosen else text
        if name == "auto" and text == "!auto":
            return f"{text} {str(data.get('viewer', '')).strip()}".strip()
        if text == "!friend add":
            char = str(data.get("friend_char", "")).strip()
            return f"!friend {char}" if char else ""
        if text == "!mail send":
            return mail_text(data)
        if text == "!family mark":
            char = str(data.get("fam_char", "")).strip()
            role = str(data.get("fam_role", "")).strip()
            return f"!family {char} {role}" if char and role else ""
        if name in ("home", "house"):
            return self.scene_text(self.home_text(text, data), data)
        if name in ("gift", "barter", "romance"):
            return trade.trade_text(text, data)
        if name == "serve" and len(text.split()) == 3:
            kick = (str(data.get("kick", "")).strip()
                    if text.split()[1] == "ballbusting" else "")
            tone = str(data.get("tone", "")).strip()
            return " ".join(part for part in (text, tone, kick) if part)
        if text == "!potion":
            return self.potion_text(str(data.get("viewer", "")).strip(),
                                    target)
        if name == "cast" and text == "!cast":
            spell = str(data.get("spell", "")).strip()
            return " ".join(part for part in (text, spell, target) if part)
        return text

    def scene_text(self, text:str, data:dict[str, Any]) -> str:
        words = text.split()
        if len(words) < 3 or words[0] not in ("!home", "!house"):
            return text
        sub = words[1]
        if sub == "practice":
            amount = str(data.get("s_amount", "")).strip() or "some"
            where = str(data.get("s_where", "")).strip() or "in"
            return f"{text} {amount} {where}"
        if sub == "order":
            title = str(data.get("title", "")).strip()
            return f"{text} {title}" if title else text
        return text

    def home_text(self, text:str, data:dict[str, Any]) -> str:
        guest = str(data.get("guest", "")).strip()
        mode = str(data.get("mode", "")).strip()
        amount = str(data.get("amount", "")).strip()
        if text in ("!home invite", "!home movein"):
            if not guest:
                return ""
            extra = mode if text == "!home invite" else ""
            return " ".join(part for part in (text, guest, extra) if part)
        if text == "!home invite all":
            return " ".join(part for part in (text, mode) if part)
        if text in ("!home store gold", "!home take gold"):
            ok = amount.isdigit() or amount.casefold() == "all"
            return f"{text} {amount}" if ok else ""
        if text == "!house seat":
            return " ".join(("!house seat",
                             str(data.get("intensity", "")).strip()
                             or "normal",
                             str(data.get("length", "")).strip() or "long",
                             "confirm"))
        return text

    def potion_text(self, viewer:str, target:str) -> str:
        player = self.player(viewer)
        potions = [item_id for item_id in player.inventory
                   if ITEMS[item_id]["slot"] == "consumable"] if player else []
        if not potions:
            return ""
        return " ".join(part for part in ("!use", potions[0], target)
                        if part)

    async def run_tool(self, client:Client, name:str) -> None:
        if name == "main":
            if client.viewer and client.viewer in self.visible(client):
                self.main_of(client).set(client.viewer)
                await self.broadcast(audience.private(client.viewer, [
                    views.echo_entry(client.viewer,
                                     f"★ {client.viewer} is the main "
                                     f"character now.")]))
            return
        if name == "auto_time":
            self.auto_time = not self.auto_time
            await self.broadcast([])
            return
        allowed = self.tools_on(client) or (name == "random_party"
                                            and not self.login)
        if name not in tools.TOOLS or not allowed:
            return
        with self.controller.lobbies.focus(client.viewer):
            messages = tools.TOOLS[name](self.controller)
        await self.broadcast(audience.scoped(self.controller, client.viewer,
                                             messages))

    def leave_house(self, viewer:str) -> str:
        player = self.player(viewer)
        if player is not None and player.profile.pop("home_host", None):
            self.controller.repository.save(player)
        return "!town"

    def enter_place(self, viewer:str, text:str) -> None:
        word = text[1:].split(" ")[0].lower() if text.startswith("!") else ""
        player = self.player(viewer)
        bundle = (self.controller.lobbies.of(player.name)
                  if player is not None else None)
        if (word not in PLACES or player is None or bundle is not None
                and bundle.session.state not in ("idle", "lobby")):
            return
        self.controller.town.go(player, word)
        self.controller.repository.save(player)

    def preview_html(self, data:dict[str, Any], errors:list[str]|None=None,
                     done:bool=False) -> str:
        figure, left, hints, invalid = create.preview(
            data, strict=errors is not None)
        return self.render("create_preview.html", figure=figure, left=left,
                           errors=hints if errors is None else errors,
                           invalid=invalid, done=done)

    async def create_submit(self, client:Client, data:dict[str, Any]) -> None:
        repository = self.controller.repository
        if client.account is not None:
            own = [row for row in self.store.characters_of(
                client.account.id) if not row["npc"]]
            if len(own) >= MAX_CHARS_PER_ACCOUNT:
                await self.push(client, self.preview_html(data, [
                    f"Every account may have at most "
                    f"{MAX_CHARS_PER_ACCOUNT} characters."]))
                return
        result = evaluate(create.form_values(data), repository)
        if result.errors:
            await self.push(client, self.preview_html(data, result.errors))
            return
        player = result.player
        if client.account is not None:
            player.account_id = client.account.id
        try:
            repository.add(player)
        except ValueError as error:
            await self.push(client, self.preview_html(data, [str(error)]))
            return
        client.viewer = player.name
        client.prefix = self.replace_log(client)
        await self.push(client, self.preview_html(data, done=True))
        await self.broadcast(audience.private(player.name, [{
            "text": f"{profile_text(player)}\n✔ Character saved. "
                    f"[lobby] opens a party, [join] joins one.",
            "kind": ""}]))

    async def chat_send(self, client:Client, kind:str, target:str,
                        body:str) -> None:
        try:
            if not self.limiter.allow(client.viewer):
                raise chat.ChatError("Slow down a little.")
            items = chat.deliver(self.controller, client.viewer, kind,
                                 target, body)
        except chat.ChatError as error:
            lines = [{"text": str(error), "kind": "input"}]
            if error.usage:
                lines.append({"text": error.usage, "kind": "usage"})
            await self.tell(client, lines)
            return
        await self.broadcast(items)

    def start_creation(self, client:Client, wanted:str) -> str:
        repository = self.controller.repository
        name = repository.unique_handle(wanted)
        if client.account is not None:
            own = [row for row in self.store.characters_of(
                client.account.id) if not row["npc"]]
            if len(own) >= MAX_CHARS_PER_ACCOUNT:
                return (f"Every account may have at most "
                        f"{MAX_CHARS_PER_ACCOUNT} characters.")
            self.controller.creator.owners[repository.key(name)] = (
                client.account.id)
        client.viewer = name
        return ""

    async def handle(self, client:Client, raw:str) -> None:
        data = json.loads(raw)
        action = data.get("action", "cmd")
        viewer = str(data.get("viewer", "")).strip()
        before = client.viewer
        if viewer in self.visible(client):
            client.viewer = viewer
        if client.viewer != before:
            client.prefix = self.replace_log(client)
        if action == "admin_powers":
            await self.toggle_powers(client)
            return
        if action == "create_preview":
            await self.push(client, self.preview_html(data))
            return
        if action == "create_submit":
            await self.create_submit(client, data)
            return
        if action == "select":
            await self.push(client, self.panels_for(client))
            return
        if action == "tool":
            await self.run_tool(client, str(data.get("tool", "")))
            return
        if action == "create":
            name = str(data.get("newname", "")).strip()
            if not name:
                await self.push(client, self.panels_for(client))
                return
            error = self.start_creation(client, name)
            if error:
                await self.tell(client, [{"text": error, "kind": ""}])
                return
            client.prefix = self.replace_log(client)
            text = "!create"
        else:
            text = self.command_text(data)
        if not text:
            return
        if text in ("!findlobby", "!findlobby close"):
            client.find_lobbies = text == "!findlobby"
            await self.push(client, self.panels_for(client))
            return
        if text.startswith("!stash "):
            kind = text.split(maxsplit=1)[1]
            client.stash = "" if kind == "close" else kind
            await self.push(client, self.panels_for(client))
            return
        if text.startswith("!house "):
            word, _, rest = text.split(maxsplit=1)[1].partition(" ")
            client.house = word != "close"
            if word == "slot":
                client.house_slot = rest.strip()
            elif word != "open":
                client.house_slot = ""
            await self.push(client, self.panels_for(client))
            return
        if text.startswith("!ambient "):
            self.toggle_ambient(client, text.split(maxsplit=1)[1])
            await self.push(client, self.panels_for(client))
            return
        if not client.viewer:
            await self.tell(client, [views.echo_entry("?", text), {
                "text": "Select or create a character first.",
                "kind": ""}])
            return
        spoken = (None if self.controller.creator.is_active(client.viewer)
                  else chat.parse(text))
        if spoken is not None:
            await self.chat_send(client, *spoken)
            return
        entries = audience.private(client.viewer, [
            views.echo_entry(client.viewer, text)])
        if text == "!houseleave":
            text = self.leave_house(client.viewer)
        self.enter_place(client.viewer, text)
        messages = self.controller.handle(client.viewer, text)
        await self.broadcast(entries + audience.scoped(
            self.controller, client.viewer, messages))

    async def push_live(self) -> None:
        for client in list(self.clients):
            viewer = self.player(client.viewer)
            if viewer is None or self.controller.town.in_run(viewer):
                continue
            with self.controller.lobbies.focus(viewer.name):
                parts = views.live_panels(self.controller, viewer)
            if parts:
                await self.push(client, self.render("live.html",
                                                    parts=parts))

    def run_refresh(self, scope:str, target:str) -> tuple[str, set[str] | None]:
        repository = self.controller.repository
        busy = {member.name for bundle in self.controller.lobbies.all()
                for member in bundle.session.party}
        if scope == "account":
            account = self.store.by_name(target)
            if account is None:
                return f"No account named {target}.", set()
            rows = [row for row in self.store.characters_of(account.id)]
            who: set[str] | None = {row["handle"] for row in rows}
        elif scope == "npcs":
            repository.reconcile_npcs()
            rows, who = self.store.characters(False), set()
        else:
            repository.reconcile_npcs()
            rows, who = self.store.characters(), None
        done, skipped = repository.reload(rows, busy)
        text = f"{done} characters reloaded"
        if skipped:
            text += f", skipped (in a party): {', '.join(skipped)}"
        return text + ".", who

    async def kick(self, target:str) -> str:
        account = self.store.by_name(target)
        if account is None:
            return f"No account named {target}."
        self.store.end_sessions(target)
        hit = [client for client in self.clients
               if client.account is not None
               and client.account.id == account.id]
        for client in hit:
            await client.socket.close(code=CLOSE_UNAUTHORIZED)
        return f"{account.name} kicked, {len(hit)} connections closed."

    async def process_refreshes(self) -> None:
        for request in self.store.open_refreshes():
            if request["scope"] == "kick":
                self.store.finish_refresh(request["id"],
                                          await self.kick(request["target"]))
                continue
            result, who = self.run_refresh(request["scope"],
                                           request["target"])
            affected = [client for client in self.clients
                        if who is None or client.viewer in who]
            self.store.finish_refresh(
                request["id"], f"{result} {len(affected)} clients "
                               f"refreshed.")
            for client in affected:
                await self.push(client, self.panels_for(client))

    async def toggle_powers(self, client:Client) -> None:
        if not self.admin(client):
            return
        client.powers = not client.powers
        shown = self.visible(client)
        if client.viewer not in shown:
            client.viewer = shown[0] if shown else ""
            client.prefix = self.replace_log(client)
        await self.push(client, self.panels_for(client))

    async def refresh_admin(self) -> None:
        for client in list(self.clients):
            if client.account is None:
                continue
            state = self.admin(client)
            if state != client.admin_seen:
                client.admin_seen = state
                await self.push(client, self.panels_for(client))

    async def tick_loop(self) -> None:
        while True:
            await asyncio.sleep(TICK_SECONDS)
            if not self.auto_time:
                for bundle in self.controller.lobbies.all():
                    bundle.session.hold_clock(TICK_SECONDS)
            await self.refresh_admin()
            await self.process_refreshes()
            names = {client.viewer for client in self.clients
                     if client.viewer}
            if names != self.last_online:
                self.last_online = names
                await self.broadcast([])
            messages: list[Message] = self.controller.tick()
            if messages:
                await self.broadcast(audience.scoped(self.controller, "",
                                                    messages))
            else:
                await self.push_live()
