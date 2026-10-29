from dataclasses import dataclass, field

import aiohttp


API_TICKET_URL = "https://www.f-list.net/json/getApiTicket.php"
TIMEOUT_SECONDS = 20


@dataclass
class LoginResult:
    ticket: str = ""
    characters: list[str] = field(default_factory=list)
    default_character: str = ""
    error: str = ""


async def fetch_ticket(account:str, password:str) -> LoginResult:
    if not account or not password:
        return LoginResult(error="Account and password are required")

    data = {
        "account": account,
        "password": password,
        "no_friends": "true",
        "no_bookmarks": "true",
        "new_character_list": "true",
    }
    try:
        timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(API_TICKET_URL, data=data) as response:
                if response.status != 200:
                    return LoginResult(error=f"Login server answered with HTTP {response.status}")
                payload = await response.json(content_type=None)
    except Exception as error:
        return LoginResult(error=f"Login request failed: {error}")

    if not isinstance(payload, dict):
        return LoginResult(error="Unexpected answer from login server")
    if payload.get("error"):
        return LoginResult(error=str(payload["error"]))

    characters = payload.get("characters") or []
    names = list(characters.keys()) if isinstance(characters, dict) else [str(name) for name in characters]
    return LoginResult(
        ticket=str(payload.get("ticket", "")),
        characters=sorted(names, key=str.lower),
        default_character=str(payload.get("default_character", "")),
    )


def main() -> None:
    pass


if __name__ == "__main__":
    main()
