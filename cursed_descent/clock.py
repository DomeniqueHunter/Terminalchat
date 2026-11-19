from datetime import datetime


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M"
FROZEN = ""


def timestamp() -> str:
    return FROZEN or datetime.now().strftime(TIMESTAMP_FORMAT)
