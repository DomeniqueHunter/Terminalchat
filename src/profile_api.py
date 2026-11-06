import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Awaitable, Callable

import aiohttp

from chat_log import logging


API_BASE = "https://www.f-list.net/json/api/"
TIMEOUT_SECONDS = 20
MAPPING_MAX_AGE = 7 * 24 * 3600
KINK_CHOICES = ("fave", "yes", "maybe", "no")


class ProfileError(Exception):
    pass


@dataclass
class Profile:
    name: str
    title: str = ""
    description: str = ""
    infotags: list[tuple[str, list[tuple[str, str]]]] = field(default_factory=list)
    kinks: dict[str, list[str]] = field(default_factory=dict)
    images: list[tuple[str, str]] = field(default_factory=list)
    views: int = 0
    created: int = 0
    updated: int = 0


def as_dict(items:object) -> dict[str, dict]:
    if isinstance(items, dict):
        return {str(key): value for key, value in items.items() if isinstance(value, dict)}
    if isinstance(items, list):
        return {str(item.get("id")): item for item in items if isinstance(item, dict)}
    return {}


def build_profile(data:dict, mapping:dict) -> Profile:
    infotag_defs = as_dict(mapping.get("infotags"))
    group_names = {key: str(item.get("name", "")) for key, item in as_dict(mapping.get("infotag_groups")).items()}
    list_items = {key: str(item.get("value", "")) for key, item in as_dict(mapping.get("listitems")).items()}
    kink_names = {key: str(item.get("name", "")) for key, item in as_dict(mapping.get("kinks")).items()}

    groups: dict[str, list[tuple[str, str]]] = {}
    infotags = data.get("infotags") or {}
    for tag_id, value in (infotags.items() if isinstance(infotags, dict) else []):
        definition = infotag_defs.get(str(tag_id), {})
        name = str(definition.get("name") or f"#{tag_id}")
        text = str(value)
        if definition.get("type") == "list":
            text = list_items.get(text, text)
        group = group_names.get(str(definition.get("group_id")), "Other")
        groups.setdefault(group, []).append((name, text))
    ordered_groups = [(group, sorted(entries)) for group, entries in groups.items()]

    kinks: dict[str, list[str]] = {choice: [] for choice in KINK_CHOICES}
    raw_kinks = data.get("kinks") or {}
    for kink_id, choice in (raw_kinks.items() if isinstance(raw_kinks, dict) else []):
        if choice in kinks:
            kinks[choice].append(kink_names.get(str(kink_id), f"#{kink_id}"))
    custom = data.get("custom_kinks") or {}
    for item in (custom.values() if isinstance(custom, dict) else []):
        if isinstance(item, dict) and item.get("choice") in kinks:
            kinks[item["choice"]].append(f"{item.get('name', '?')} (custom)")
    for names in kinks.values():
        names.sort(key=str.lower)

    raw_images = data.get("images") or []
    if isinstance(raw_images, dict):
        raw_images = list(raw_images.values())
    images = []
    for item in sorted((item for item in raw_images if isinstance(item, dict)), key=lambda item: int(item.get("sort_order") or 0)):
        image_id, extension = str(item.get("image_id") or item.get("id") or ""), str(item.get("extension") or "")
        if image_id.isdigit() and extension.isalnum():
            images.append((f"{image_id}.{extension}", str(item.get("description") or "")))

    return Profile(
        images=images,
        name=str(data.get("name", "")),
        title=str(data.get("custom_title") or ""),
        description=str(data.get("description") or ""),
        infotags=ordered_groups,
        kinks=kinks,
        views=int(data.get("views") or 0),
        created=int(data.get("created_at") or 0),
        updated=int(data.get("updated_at") or 0),
    )


class ProfileApi:

    def __init__(self, account:str, ticket_source:Callable[[bool], Awaitable[str]], cache_dir:Path) -> None:
        self.account = account
        self.ticket_source = ticket_source
        self.mapping_file = cache_dir / "mapping-list.json"
        self.mapping_data: dict | None = None

    async def request(self, endpoint:str, data:dict[str, str]) -> dict:
        try:
            timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(API_BASE + endpoint, data=data) as response:
                    if response.status != 200:
                        raise ProfileError(f"f-list answered with HTTP {response.status}")
                    payload = await response.json(content_type=None)
        except ProfileError:
            raise
        except Exception as error:
            logging("debug.log", f"profile request {endpoint} failed: {error!r}\n")
            raise ProfileError(f"Request failed: {error}") from error
        if not isinstance(payload, dict):
            raise ProfileError("Unexpected answer from f-list")
        if payload.get("error"):
            raise ProfileError(str(payload["error"]))
        return payload

    async def mapping(self) -> dict:
        if self.mapping_data is not None:
            return self.mapping_data
        try:
            if time.time() - self.mapping_file.stat().st_mtime < MAPPING_MAX_AGE:
                self.mapping_data = json.loads(self.mapping_file.read_text(encoding="utf-8"))
                return self.mapping_data
        except (OSError, json.JSONDecodeError):
            pass
        self.mapping_data = await self.request("mapping-list.php", {})
        self.mapping_file.parent.mkdir(parents=True, exist_ok=True)
        self.mapping_file.write_text(json.dumps(self.mapping_data), encoding="utf-8")
        return self.mapping_data

    async def profile(self, name:str) -> Profile:
        try:
            data = await self.character_data(name, False)
        except ProfileError as error:
            if "ticket" not in str(error).lower():
                raise
            logging("debug.log", f"profile request: {error}, fetching a new ticket\n")
            data = await self.character_data(name, True)
        return build_profile(data, await self.mapping())

    async def character_data(self, name:str, new_ticket:bool) -> dict:
        ticket = await self.ticket_source(new_ticket)
        return await self.request("character-data.php", {"account": self.account, "ticket": ticket, "name": name})


def main() -> None:
    mapping = {
        "infotags": [{"id": "1", "name": "Gender", "type": "list", "group_id": "3"}, {"id": "2", "name": "Age", "type": "text", "group_id": "1"}],
        "infotag_groups": [{"id": "1", "name": "General details"}, {"id": "3", "name": "Character"}],
        "listitems": [{"id": "9", "name": "gender", "value": "Female"}],
        "kinks": [{"id": "5", "name": "Cuddling"}, {"id": "6", "name": "Rain"}],
    }
    data = {"name": "Alice", "custom_title": "Explorer", "description": "[b]Hi[/b]", "infotags": {"1": "9", "2": "25"},
            "kinks": {"5": "fave", "6": "no"}, "custom_kinks": {"1": {"name": "Tea", "choice": "yes"}}}
    print(build_profile(data, mapping))


if __name__ == "__main__":
    main()
