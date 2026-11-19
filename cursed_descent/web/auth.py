from collections.abc import Mapping

from ..accounts import Account, AccountStore
from ..config import SESSION_DAYS


COOKIE = "cd_session"
MAX_AGE = SESSION_DAYS * 86400


def account_of(store:AccountStore, cookies:Mapping[str, str]) -> Account | None:
    token = cookies.get(COOKIE, "")
    return store.session_account(token) if token else None
