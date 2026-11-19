from typing import Any

from .content import ITEMS
from .models import Message

PAGE_SIZE = 40
RARITIES = ("common", "rare", "epic", "cursed", "legendary")
USAGE = ("Usage: itemlist [slot|rarity|search word] [page number]. "
         "Examples: itemlist weapon, itemlist legendary 2, itemlist bed")


def matches(key:str, item:dict[str, Any], word:str) -> bool:
    if not word:
        return True
    return word in (item.get("slot", ""), item.get("rarity", "")) or (
        word in key.casefold() or word in item["name"].casefold())


def item_list(sender:str, args:list[str]) -> list[Message]:
    page = 1
    if args and args[-1].isdigit():
        page = max(1, int(args[-1]))
        args = args[:-1]
    word = " ".join(args).casefold()
    found = sorted(((key, item) for key, item in ITEMS.items()
                    if matches(key, item, word)),
                   key=lambda pair: (pair[1].get("slot", ""), pair[0]))
    if not found:
        return [Message(f"No items match '{word}'. {USAGE}", sender)]
    pages = (len(found) + PAGE_SIZE - 1) // PAGE_SIZE
    page = min(page, pages)
    rows = found[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]
    lines = [f"Items {word or 'all'}: {len(found)} found, page "
             f"{page}/{pages} ([giveitem <id>] hands one out)"]
    lines += [f"  {key}: {item['name']} ({item.get('slot', '?')}, "
              f"{item.get('rarity', '?')})" for key, item in rows]
    return [Message("\n".join(lines), sender)]


def give_item(controller:Any, sender:str, args:list[str]) -> list[Message]:
    if not args:
        return [Message("Usage: giveitem <item id or name> [player]",
                        sender)]
    repository = controller.repository
    target = None
    words = list(args)
    if len(words) > 1:
        target = repository.load(repository.resolve(words[-1]))
        if target is not None:
            words = words[:-1]
    wanted = " ".join(words).casefold()
    key = next((key for key in ITEMS if key.casefold() == wanted), None)
    if key is None:
        names = [key for key, item in ITEMS.items()
                 if item["name"].casefold() == wanted]
        key = names[0] if len(names) == 1 else None
    if key is None:
        close = [f"{key} ({item['name']})" for key, item in ITEMS.items()
                 if wanted in key.casefold()
                 or wanted in item["name"].casefold()][:8]
        hint = f" Did you mean: {', '.join(close)}?" if close else ""
        return [Message(f"No single item '{wanted}'.{hint}", sender)]
    if target is None:
        target = repository.load(repository.resolve(sender))
    if target is None:
        return [Message("That player does not exist.", sender)]
    if len(target.inventory) >= target.bag_size:
        return [Message(f"{target.name}'s bag is full.", sender)]
    target.inventory.append(key)
    repository.save(target)
    return [Message(f"{ITEMS[key]['name']} goes into {target.name}'s bag.",
                    sender)]
