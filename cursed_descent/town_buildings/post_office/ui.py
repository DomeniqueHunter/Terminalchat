from ...content import ITEMS
from ...mail import attachment_text, fee_for, known_names
from ...models import Player
from ...view import Button, Choice, Panel, Row
from ..world_days import date_text
from . import content
from .rules import PLACE, header, tidy


SHOWN = 20


def panel(services, player:Player) -> Panel:
    tidy(services, player)
    unread = services.mail.unread(player.id)
    lines = [content.OFFER, f"Posting a letter costs {fee_for(0)} gold, "
             f"plus a share of any gold you attach.",
             f"📬 {unread} new letter(s)." if unread else
             "No new letters."]
    return Panel(f"📮 {content.TITLE}", tuple(lines), (),
                 sections=tuple(mail_panels(services, player)[:1]))


def mail_panels(services, player:Player) -> list[Panel]:
    tidy(services, player)
    box = services.mail.box(player.id)
    at_post = services.where(player) == PLACE
    mails = sorted(box.inbox, key=lambda mail: -mail["id"])[:SHOWN]
    rows = []
    for mail in mails:
        parcel = bool(mail["gold"] or mail["item"])
        buttons = [Button("Read", f"!mail read {mail['id']}"),
                   Button("Reply", f"!mail reply {mail['id']} |", "fill")]
        if parcel:
            buttons.append(Button("Collect", f"!mail collect {mail['id']}",
                                  "", at_post))
        else:
            buttons.append(Button("Delete", f"!mail delete {mail['id']}",
                                  "danger"))
        rows.append(Row(header(mail), tuple(buttons)))
    inbox = Panel(f"Inbox ({len(box.inbox)})",
                  () if rows else ("Your mailbox is empty.",), (),
                  rows=tuple(rows))
    known = known_names(services.mail, services.repository, player)
    people = tuple((name, name) for name in sorted(
        known, key=str.casefold)
        if name != player.name and services.repository.exists(name)
        and not services.repository.load(name).npc)
    npcs = tuple((npc.name, f"{npc.full_name} ({npc.profile.get('role', '')})"
                  if npc.profile.get("role") else npc.full_name)
                 for npc in sorted(services.repository.npc_players(),
                                   key=lambda npc: npc.full_name.casefold())
                 if npc.name in known)
    items = (("", "no item"),) + tuple(
        (str(number), ITEMS[item]["name"]) for number, item in
        enumerate(player.inventory, 1))
    compose = Panel("Write a letter", (
        f"Posting costs {fee_for(0)} gold plus 5 % of attached gold.",),
        (Button("Send", "!mail send"),), choices=(
            Choice("mail_to", "To (people you know)",
                   (("", "— choose —"), *people, *npcs), "select"),
            Choice("mail_name", "or type a name", (), "text"),
            Choice("mail_subject", "Subject", (), "wide"),
            Choice("mail_body", "Text", (), "area"),
            Choice("mail_gold", "Gold", (), "text"),
            Choice("mail_item", "Item", items, "select")))
    sent = Panel("Sent", () if box.sent else ("Nothing sent yet.",), (),
                 rows=tuple(Row(
                     f"To {mail['to_name']}: {mail['subject']} "
                     f"({date_text(mail['day'])})"
                     + (f" 🎁 {attachment_text(mail)}"
                        if attachment_text(mail) else ""))
                     for mail in reversed(box.sent[-8:])))
    blocked = [services.repository.load_by_id(char_id)
               for char_id in box.blocked]
    panels = [inbox, compose, sent]
    if blocked:
        panels.append(Panel("Blocked", (), (), rows=tuple(
            Row(other.name, (Button("Unblock",
                                    f"!mail unblock {other.name}"),))
            for other in blocked if other is not None)))
    return panels
