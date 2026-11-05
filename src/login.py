from dataclasses import dataclass, field

import aiohttp

from chat_log import logging


API_TICKET_URL = "https://www.f-list.net/json/getApiTicket.php"
TIMEOUT_SECONDS = 20


@dataclass
class LoginResult:
    ticket: str = ""
    characters: list[str] = field(default_factory=list)
    default_character: str = ""
    bookmarks: list[str] = field(default_factory=list)
    friends: list[tuple[str, str]] | None = None
    error: str = ""
    temporary: bool = False


def bookmark_names(items:object) -> list[str]:
    if not isinstance(items, list):
        return []
    names = [item.get("name") if isinstance(item, dict) else item for item in items]
    return [str(name) for name in names if name]


def friend_pairs(items:object) -> list[tuple[str, str]] | None:
    if not isinstance(items, list):
        logging("debug.log", f"ticket friends: {type(items).__name__}\n")
        return None
    dicts = [item for item in items if isinstance(item, dict)]
    return [(str(item.get("source_name", "")), str(item.get("dest_name", ""))) for item in dicts]


async def fetch_ticket(account:str, password:str) -> LoginResult:
    if not account or not password:
        return LoginResult(error="Account and password are required")

    data = {
        "account": account,
        "password": password,
        "no_friends": "false",
        "no_bookmarks": "false",
        "new_character_list": "true",
    }
    try:
        timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(API_TICKET_URL, data=data) as response:
                if response.status != 200:
                    return LoginResult(error=f"Login server answered with HTTP {response.status}", temporary=True)
                payload = await response.json(content_type=None)
    except Exception as error:
        return LoginResult(error=f"Login request failed: {error}", temporary=True)

    if not isinstance(payload, dict):
        return LoginResult(error="Unexpected answer from login server", temporary=True)
    if payload.get("error"):
        return LoginResult(error=str(payload["error"]))

    characters = payload.get("characters") or []
    names = list(characters.keys()) if isinstance(characters, dict) else [str(name) for name in characters]
    return LoginResult(
        ticket=str(payload.get("ticket", "")),
        characters=sorted(names, key=str.lower),
        default_character=str(payload.get("default_character", "")),
        bookmarks=bookmark_names(payload.get("bookmarks")),
        friends=friend_pairs(payload.get("friends")),
    )


def main() -> None:
    pass


if __name__ == "__main__":
    main()
