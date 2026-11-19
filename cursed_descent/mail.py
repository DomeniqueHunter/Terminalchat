import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import (
    MAIL_ATTACH_DAYS, MAIL_BODY_MAX, MAIL_BOX_SIZE, MAIL_FEE,
    MAIL_DIR_NAME, MAIL_FILE_NAME, MAIL_GOLD_FEE_PERCENT, MAIL_KEEP_DAYS,
    MAIL_NPC_REPLY_SECONDS, MAIL_PER_HOUR, MAIL_READ_DAYS,
    MAIL_SUBJECT_MAX, MAIL_TAKEN_DAYS,
)
from .content import ITEMS
from .dungeon import find_inventory_item
from .items import item_from_json, item_to_json, remove_item
from .models import Player
from .storage import PlayerRepository, read_json, write_json


HOUR = 3600.0
POST_NAME = "The Post Office"
MOST_SENT = 30


@dataclass
class Box:
    inbox: list[dict[str, Any]] = field(default_factory=list)
    sent: list[dict[str, Any]] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)
    log: list[float] = field(default_factory=list)


class MailLedger:
    def __init__(self, data_path:Path,
                 clock:Callable[[], float]=time.time) -> None:
        self.path = data_path / MAIL_FILE_NAME
        self.folder = data_path / MAIL_DIR_NAME
        self.clock = clock
        saved = read_json(self.path, {})
        self.counter: int = saved.get("counter", 0)
        self.pending: list[dict[str, Any]] = saved.get("pending", [])
        self.boxes: dict[str, Box] = {}
        for char_id, data in saved.get("boxes", {}).items():
            self.boxes[char_id] = Box(**data)
        if self.folder.exists():
            for path in self.folder.glob("*.json"):
                self.boxes[path.stem] = Box(**read_json(path, {}))
        if saved.get("boxes"):
            self.save()

    def box(self, char_id:str) -> Box:
        return self.boxes.setdefault(char_id, Box())

    def next_id(self) -> int:
        self.counter += 1
        return self.counter

    def save(self) -> None:
        write_json(self.path, {"counter": self.counter,
                               "pending": self.pending})
        self.folder.mkdir(parents=True, exist_ok=True)
        for char_id, box in self.boxes.items():
            path = self.folder / f"{char_id}.json"
            if box.inbox or box.sent or box.blocked or box.log:
                write_json(path, {"inbox": box.inbox, "sent": box.sent,
                                  "blocked": box.blocked, "log": box.log})
            elif path.exists():
                path.unlink()

    def unread(self, char_id:str) -> int:
        return sum(1 for mail in self.box(char_id).inbox
                   if not mail["read"])


def fee_for(gold:int) -> int:
    return MAIL_FEE + gold * MAIL_GOLD_FEE_PERCENT // 100


def attachment_text(mail:dict[str, Any]) -> str:
    parts = []
    if mail.get("gold"):
        parts.append(f"{mail['gold']} gold")
    if mail.get("item"):
        parts.append(ITEMS[item_from_json(mail["item"])]["name"])
    return " + ".join(parts)


def has_attachment(mail:dict[str, Any]) -> bool:
    return bool(mail.get("gold") or mail.get("item"))


def new_mail(ledger:MailLedger, sender_id:str, sender_name:str,
             target:Player, subject:str, body:str, day:int,
             gold:int=0, item:Any=None, kind:str="mail") -> dict[str, Any]:
    return {"id": ledger.next_id(), "from_id": sender_id,
            "from_name": sender_name, "to_id": target.id,
            "to_name": target.name, "subject": subject, "body": body,
            "day": day, "read": False, "gold": gold, "item": item,
            "kind": kind}


def clean(text:str, limit:int) -> str:
    return " ".join(text.split())[:limit]


def reply_subject(subject:str) -> str:
    return subject if subject.startswith("Re: ") else f"Re: {subject}"[
        :MAIL_SUBJECT_MAX]


def find_target(repository:PlayerRepository, reference:str) -> str:
    name = repository.resolve(reference)
    if repository.exists(name):
        return name
    wanted = reference.strip().casefold()
    found = [npc.name for npc in repository.npc_players()
             if wanted in (npc.name.casefold(), npc.first_name.casefold(),
                           npc.full_name.casefold())]
    return found[0] if len(found) == 1 else name


def known_names(ledger:MailLedger, repository:PlayerRepository,
                player:Player) -> set[str]:
    from .friends import friend_names
    box = ledger.box(player.id)
    names = set(friend_names(player, repository))
    for entry in player.profile.get("family", {}).values():
        names.add(entry.get("name", ""))
    names.update(mail["from_name"] for mail in box.inbox
                 if mail.get("from_name"))
    names.update(mail["to_name"] for mail in box.sent)
    for npc in repository.npc_players():
        if npc.profile.get("friends", {}).get(player.id, 0) > 0:
            names.add(npc.name)
    return {name for name in names if name}


def send(ledger:MailLedger, repository:PlayerRepository, sender:Player,
         reference:str, subject:str, body:str, gold:int, item_ref:str,
         day:int) -> tuple[str, str]:
    target_name = find_target(repository, reference)
    target = repository.load(target_name) if target_name else None
    if target is None or target.id == sender.id:
        return "", "There is nobody like that to write to."
    subject = clean(subject, MAIL_SUBJECT_MAX)
    body = body.strip()[:MAIL_BODY_MAX]
    if not subject or not body:
        return "", "A letter needs a subject and a text."
    box = ledger.box(target.id)
    now = ledger.clock()
    mine = ledger.box(sender.id)
    mine.log = [stamp for stamp in mine.log if now - stamp < HOUR]
    if len(mine.log) >= MAIL_PER_HOUR:
        return "", (f"The post office takes at most {MAIL_PER_HOUR} letters "
                    f"per hour from you. Come back later.")
    if sender.id in box.blocked:
        return "", f"{target.name} does not want letters from you."
    if not target.npc and len(box.inbox) >= MAIL_BOX_SIZE:
        return "", f"{target.name}'s mailbox is full."
    if gold < 0 or gold > sender.gold:
        return "", "You do not carry that much gold."
    cost = fee_for(gold)
    if sender.gold < gold + cost:
        return "", (f"The post office wants {cost} gold for this letter "
                    f"plus the {gold} gold you attach.")
    item = None
    if item_ref:
        item = find_inventory_item(sender, item_ref)
        if item is None:
            return "", "No such item in your bag."
    if target.npc:
        if item is not None and len(target.inventory) >= target.bag_size:
            return "", f"{target.name} cannot carry any more."
    sender.gold -= gold + cost
    packed = None
    if item is not None:
        packed = item_to_json(item)
        remove_item(sender.inventory, item)
    mine.log.append(now)
    mine.sent.append({"id": ledger.next_id(), "to_name": target.name,
                      "subject": subject, "body": body, "day": day,
                      "gold": gold, "item": packed})
    mine.sent = mine.sent[-MOST_SENT:]
    if target.npc:
        accept_gift(target, gold, packed)
        lo, hi = MAIL_NPC_REPLY_SECONDS
        ledger.pending.append({
            "due": now + random.uniform(lo, hi), "npc_id": target.id,
            "to_id": sender.id, "subject": subject, "gold": gold,
            "item": packed is not None})
        repository.save(target)
        return target.name, (f"📮 Letter to {target.name} posted "
                             f"(fee {cost} gold).")
    box.inbox.append(new_mail(ledger, sender.id, sender.name, target,
                              subject, body, day, gold, packed))
    return target.name, f"📮 Letter to {target.name} posted (fee {cost} gold)."



def accept_gift(npc:Player, gold:int, packed:Any) -> None:
    npc.gold += gold
    if packed is not None:
        npc.inventory.append(item_from_json(packed))


def npc_reply_text(npc:Player, pending:dict[str, Any],
                   rng:random.Random, asker:Player | None) -> str:
    topics = npc.profile.get("topics", {})
    lines = [line for group in topics.values() for line in group]
    lines += list(npc.profile.get("quotes", []))
    greeting = f"Dear {asker.first_name or asker.name}," if asker else "Dear friend,"
    parts = [greeting, "thank you for your letter."]
    if pending.get("gold") or pending.get("item"):
        parts.append("And thank you for the gift.")
    if lines:
        parts.append(rng.choice(lines))
    parts.append(f"– {npc.full_name}")
    return " ".join(parts)


def deliver_due(ledger:MailLedger, repository:PlayerRepository,
                rng:random.Random, day:int, owner_id:str="") -> int:
    now = ledger.clock()
    delivered = 0
    keep = []
    for pending in ledger.pending:
        if pending["due"] > now or (owner_id and pending["to_id"] != owner_id):
            keep.append(pending)
            continue
        npc = next((candidate for candidate in repository.npc_players()
                    if candidate.id == pending["npc_id"]), None)
        asker = next((candidate for candidate in map(
            repository.load, repository.names())
            if candidate is not None and candidate.id == pending["to_id"]),
            None)
        if npc is None or asker is None:
            continue
        body = npc_reply_text(npc, pending, rng, asker)
        ledger.box(asker.id).inbox.append(new_mail(
            ledger, npc.id, npc.name, asker,
            reply_subject(pending["subject"]), body, day, kind="npc"))
        delivered += 1
    ledger.pending = keep
    return delivered


def expired(mail:dict[str, Any], day:int) -> bool:
    if day - mail["day"] >= MAIL_KEEP_DAYS:
        return True
    if "taken_day" in mail:
        return day - mail["taken_day"] >= MAIL_TAKEN_DAYS
    return "seen_day" in mail and day - mail["seen_day"] >= MAIL_READ_DAYS


def sweep(ledger:MailLedger, repository:PlayerRepository, day:int) -> int:
    changed = 0
    for char_id, box in list(ledger.boxes.items()):
        kept = []
        for mail in box.inbox:
            age = day - mail["day"]
            if has_attachment(mail) and age >= MAIL_ATTACH_DAYS:
                give_back(ledger, repository, mail, day)
                changed += 1
                mail["gold"], mail["item"] = 0, None
                mail["body"] += "\n[The attachment was returned to the sender.]"
            if not has_attachment(mail) and expired(mail, day):
                changed += 1
                continue
            kept.append(mail)
        box.inbox = kept
    return changed


def give_back(ledger:MailLedger, repository:PlayerRepository,
              mail:dict[str, Any], day:int) -> None:
    sender = next((candidate for candidate in map(
        repository.load, repository.names())
        if candidate is not None and candidate.id == mail["from_id"]), None)
    recipient_id = mail["to_id"]
    if sender is None or sender.npc:
        return
    note = new_mail(ledger, recipient_id, POST_NAME, sender,
                    f"Returned: {mail['subject']}",
                    f"{mail['to_name']} never collected this. It is back "
                    f"with you.", day, mail["gold"], mail["item"], "return")
    ledger.box(sender.id).inbox.append(note)
