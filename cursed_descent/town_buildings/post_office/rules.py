import random

from ...config import MAIL_BOX_SIZE
from ...content import ITEMS
from ...dungeon import find_inventory_item
from ...items import item_from_json, remove_item
from ...mail import (
    attachment_text, deliver_due, fee_for, has_attachment, reply_subject,
    send, sweep,
)
from ...models import Message, Player
from ...towns import town_key
from ..world_days import date_text
from . import content


PLACE = content.KEY


def clerk_line(player:Player) -> str:
    entry = content.CLERKS.get(town_key(player))
    return entry[2] if entry else content.OFFER


def tidy(services, player:Player) -> None:
    deliver_due(services.mail, services.repository, services.rng,
                services.world.day, player.id)


def find(services, player:Player, ref:str) -> dict | None:
    if not ref.isdigit():
        return None
    number = int(ref)
    return next((mail for mail in services.mail.box(player.id).inbox
                 if mail["id"] == number), None)


def header(mail:dict) -> str:
    mark = "●" if not mail["read"] else "○"
    extra = attachment_text(mail)
    parcel = f" 🎁 {extra}" if extra else ""
    return (f"{mark} #{mail['id']} {mail['from_name']}: {mail['subject']} "
            f"({date_text(mail['day'])}){parcel}")


def inbox(services, player:Player) -> list[Message]:
    tidy(services, player)
    box = services.mail.box(player.id)
    mails = sorted(box.inbox, key=lambda mail: -mail["id"])
    lines = [f"📬 Mailbox of {player.name}: {len(mails)}/{MAIL_BOX_SIZE} "
             f"letters, {services.mail.unread(player.id)} new"]
    lines += [f"  {header(mail)}" for mail in mails] or [content.EMPTY]
    return [Message("\n".join(lines), player.name)]


def read(services, player:Player, ref:str) -> list[Message]:
    mail = find(services, player, ref)
    if mail is None:
        return [Message(content.UNKNOWN, player.name)]
    mail["read"] = True
    mail.setdefault("seen_day", services.world.day)
    services.mail.save()
    lines = [f"✉ #{mail['id']} from {mail['from_name']} "
             f"({date_text(mail['day'])})", f"Subject: {mail['subject']}",
             mail["body"]]
    if has_attachment(mail):
        lines.append(f"🎁 Parcel: {attachment_text(mail)}")
    return [Message("\n".join(lines), player.name)]


def delete(services, player:Player, ref:str) -> list[Message]:
    mail = find(services, player, ref)
    if mail is None:
        return [Message(content.UNKNOWN, player.name)]
    if has_attachment(mail):
        return [Message("That letter still holds a parcel. Collect it first.",
                        player.name)]
    services.mail.box(player.id).inbox.remove(mail)
    services.mail.save()
    return [Message(f"🗑 Letter #{mail['id']} thrown away.", player.name)]


def collect(services, player:Player, ref:str) -> list[Message]:
    if services.where(player) != PLACE:
        return [Message(content.NOT_HERE, player.name)]
    mail = find(services, player, ref)
    if mail is None:
        return [Message(content.UNKNOWN, player.name)]
    if not has_attachment(mail):
        return [Message(content.NO_ATTACH, player.name)]
    lines = []
    if mail["gold"]:
        player.gold += mail["gold"]
        lines.append(f"💰 {mail['gold']} gold collected.")
        mail["gold"] = 0
    if mail["item"]:
        if len(player.inventory) >= player.bag_size:
            lines.append(content.BAG_FULL)
        else:
            item = item_from_json(mail["item"])
            player.inventory.append(item)
            lines.append(f"🎁 {ITEMS[item]['name']} collected.")
            mail["item"] = None
    mail["read"] = True
    if not has_attachment(mail):
        mail["taken_day"] = services.world.day
    services.mail.save()
    return [Message("\n".join(lines), player.name)]


def sent(services, player:Player) -> list[Message]:
    box = services.mail.box(player.id)
    lines = ["📤 Sent letters:"]
    for mail in reversed(box.sent[-10:]):
        extra = attachment_text(mail)
        lines.append(f"  To {mail['to_name']}: {mail['subject']} "
                     f"({date_text(mail['day'])})"
                     + (f" 🎁 {extra}" if extra else ""))
    if len(lines) == 1:
        lines.append("  Nothing yet.")
    return [Message("\n".join(lines), player.name)]


def block(services, player:Player, name:str, on:bool) -> list[Message]:
    other = services.repository.load(services.repository.resolve(name))
    if other is None:
        return [Message("There is nobody like that.", player.name)]
    box = services.mail.box(player.id)
    if on and other.id not in box.blocked:
        box.blocked.append(other.id)
    if not on and other.id in box.blocked:
        box.blocked.remove(other.id)
    services.mail.save()
    return [Message(f"{other.name} is {'blocked' if on else 'unblocked'}.",
                    player.name)]


def parts_of(args:list[str]) -> list[str]:
    return [part.strip() for part in " ".join(args).split("|")]


def number_of(text:str) -> int:
    return int(text) if text.isdigit() else -1


def write(services, player:Player, to:str, subject:str, body:str,
          gold:str, item:str) -> list[Message]:
    amount = number_of(gold) if gold else 0
    if amount < 0:
        return [Message("The gold has to be a number.", player.name)]
    target, text = send(services.mail, services.repository, player, to,
                        subject, body, amount, item, services.world.day)
    services.mail.save()
    messages = [Message(text, player.name)]
    if target:
        recipient = services.repository.load(target)
        if recipient is not None and not recipient.npc:
            messages.append(Message(
                f"📬 New letter from {player.name}: {subject}", target))
    return messages


def do_mail(services, player:Player, args:list[str]) -> list[Message]:
    if services.in_run(player):
        return [Message(content.AWAY, player.name)]
    word = args[0].casefold() if args else ""
    rest = args[1:]
    sweep(services.mail, services.repository, services.world.day)
    if word in ("", "inbox"):
        return inbox(services, player)
    if word == "read" and rest:
        return read(services, player, rest[0])
    if word == "delete" and rest:
        return delete(services, player, rest[0])
    if word == "collect" and rest:
        return collect(services, player, rest[0])
    if word == "sent":
        return sent(services, player)
    if word in ("block", "unblock") and rest:
        return block(services, player, " ".join(rest), word == "block")
    if word == "send":
        fields = parts_of(rest)
        fields += [""] * (5 - len(fields))
        return write(services, player, *fields[:5])
    if word == "reply" and rest:
        fields = parts_of(rest)
        mail = find(services, player, fields[0])
        if mail is None:
            return [Message(content.UNKNOWN, player.name)]
        if mail["kind"] == "return":
            return [Message(content.NO_REPLY, player.name)]
        fields += [""] * (4 - len(fields))
        return write(services, player, mail["from_name"],
                     reply_subject(mail["subject"]), fields[1], fields[2],
                     fields[3])
    return [Message(content.HELP, player.name)]


def do_post_office(services, player:Player, args:list[str]) -> list[Message]:
    if services.in_run(player):
        return [Message(content.CLOSED, player.name)]
    tidy(services, player)
    lines = [clerk_line(player),
             f"Posting a letter costs {fee_for(0)} gold, plus a share of "
             f"any gold you attach."]
    unread = services.mail.unread(player.id)
    if unread:
        lines.append(f"📬 {unread} new letter(s) wait for you.")
    return [Message("\n".join(lines), player.name)]
