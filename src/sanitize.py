import re
from typing import Any


UNSAFE_CHARACTERS = re.compile("[\x00-\x08\x0b-\x1f\x7f-\x9f‪-‮⁦-⁩]")
SAFE_URL_SCHEMES = ("http://", "https://")


def clean_text(text:str) -> str:
    return UNSAFE_CHARACTERS.sub("", text)


def clean_data(data:Any) -> Any:
    if isinstance(data, str):
        return clean_text(data)
    if isinstance(data, list):
        return [clean_data(item) for item in data]
    if isinstance(data, dict):
        return {key: clean_data(value) for key, value in data.items()}
    return data


def safe_path_part(name:str) -> str:
    part = clean_text(name).replace("/", "_").replace("\\", "_").strip()
    return "_" + part if not part or part.startswith(".") else part


def is_safe_url(url:str) -> bool:
    return url.strip().lower().startswith(SAFE_URL_SCHEMES)


def main() -> None:
    sample = "a\x1b]52;c;SGFjaw==\x1b\\b‮c\x9b2J\n\td"
    print(repr(clean_text(sample)))
    print(safe_path_part("../../etc"), safe_path_part("ADH-123"), safe_path_part("a/b"))
    print(is_safe_url("https://f-list.net"), is_safe_url("file:///etc/passwd"))


if __name__ == "__main__":
    main()
