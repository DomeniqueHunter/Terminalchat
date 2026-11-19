from typing import Any


class Item(str):
    traces: dict[str, dict[str, Any]]
    soak: int
    iid: str
    stats: dict[str, Any] | None
    restriction: str
    creator: str

    def __new__(cls, template_id:str,
                traces:dict[str, dict[str, Any]] | None=None,
                soak:int=0, iid:str="",
                stats:dict[str, Any] | None=None,
                restriction:str="both", creator:str="") -> "Item":
        item = super().__new__(cls, template_id)
        item.traces = {key: dict(value)
                       for key, value in (traces or {}).items()}
        item.soak = soak
        item.iid = iid
        item.stats = None if stats is None else dict(stats)
        item.restriction = restriction
        item.creator = creator
        return item

    @property
    def has_state(self) -> bool:
        return (bool(self.traces) or self.soak > 0 or bool(self.iid)
                or self.stats is not None or self.restriction != "both"
                or bool(self.creator))


def as_item(value:str) -> Item:
    return value if isinstance(value, Item) else Item(value)


def item_to_json(value:str) -> str | dict[str, Any]:
    if isinstance(value, Item) and value.has_state:
        data: dict[str, Any] = {"id": str(value)}
        if value.traces:
            data["traces"] = value.traces
        if value.soak:
            data["soak"] = value.soak
        if value.iid:
            data["iid"] = value.iid
        if value.stats is not None:
            data["stats"] = value.stats
        if value.restriction != "both":
            data["for"] = value.restriction
        if value.creator:
            data["by"] = value.creator
        return data
    return str(value)


def item_from_json(data:str | dict[str, Any]) -> str:
    if isinstance(data, dict):
        return Item(data["id"], data.get("traces"), data.get("soak", 0),
                    data.get("iid", ""), data.get("stats"),
                    data.get("for", "both"), data.get("by", ""))
    return data


def item_state(value:str) -> dict[str, Any]:
    if isinstance(value, Item) and value.has_state:
        state: dict[str, Any] = {"traces": value.traces, "soak": value.soak}
        if value.iid:
            state["iid"] = value.iid
        if value.stats is not None:
            state["stats"] = value.stats
        if value.restriction != "both":
            state["for"] = value.restriction
        if value.creator:
            state["by"] = value.creator
        return state
    return {}


def restore_item(template_id:str, state:dict[str, Any] | None) -> str:
    if not state:
        return template_id
    return Item(template_id, state.get("traces"), state.get("soak", 0),
                state.get("iid", ""), state.get("stats"),
                state.get("for", "both"), state.get("by", ""))


def remove_item(items:list[str], item:str) -> None:
    for index, candidate in enumerate(items):
        if candidate is item:
            del items[index]
            return
    items.remove(item)


def pack_items(items:list[str]) -> list[str | dict[str, Any]]:
    packed: list[str | dict[str, Any]] = []
    for item in items:
        data = item_to_json(item)
        if (isinstance(data, dict) and packed
                and isinstance(packed[-1], dict)
                and {key: value for key, value in packed[-1].items()
                     if key != "n"} == data):
            packed[-1]["n"] = packed[-1].get("n", 1) + 1
            continue
        packed.append(data)
    return packed


def unpack_items(data:list[str | dict[str, Any]]) -> list[str]:
    items: list[str] = []
    for entry in data:
        copies = entry.get("n", 1) if isinstance(entry, dict) else 1
        items.extend(item_from_json(entry) for _ in range(copies))
    return items
