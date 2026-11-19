from pathlib import Path

from cursed_descent.accounts import AccountStore
from cursed_descent.admin_cli import main


def test_serial_password_and_admin_flow(tmp_path:Path, capsys) -> None:
    assert main(["--data", str(tmp_path), "serial", "2"]) == 0
    keys = capsys.readouterr().out.split()
    assert len(keys) == 2
    store = AccountStore(tmp_path)
    store.register(keys[0], "Brain", "longpassword")
    store.close()
    assert main(["--data", str(tmp_path), "password", "Brain",
                 "--password", "anotherpass"]) == 0
    assert main(["--data", str(tmp_path), "admin", "Brain"]) == 0
    assert main(["--data", str(tmp_path), "admin", "Nobody"]) == 1
    store = AccountStore(tmp_path)
    assert store.login("Brain", "anotherpass").admin
    store.close()
    assert main(["--data", str(tmp_path), "admin", "Brain", "--revoke"]) == 0
    store = AccountStore(tmp_path)
    assert not store.login("Brain", "anotherpass").admin
    store.close()
