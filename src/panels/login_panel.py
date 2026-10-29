from dataclasses import dataclass, field

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, Static

import login


LOGIN_CSS = """
LoginScreen {
    align: center middle;
}

#login_box {
    width: 60;
    height: auto;
    border: solid $accent;
    background: $panel;
    padding: 1 2;
}

#login_box Input, #login_box Checkbox, #login_box Button {
    margin-top: 1;
}

#login_box Button {
    width: 100%;
}

#login_status {
    margin-top: 1;
    color: $error;
}
"""


@dataclass
class Credentials:
    account: str
    password: str
    remember: bool
    characters: list[str] = field(default_factory=list)
    default_character: str = ""


class LoginScreen(ModalScreen[Credentials | None]):

    CSS = LOGIN_CSS

    def __init__(self, account:str="", remember:bool=True, message:str="") -> None:
        super().__init__()
        self.account = account
        self.remember = remember
        self.message = message
        self.busy = False

    def compose(self) -> ComposeResult:
        with Vertical(id="login_box"):
            yield Static("[b]F-Chat Login[/b]")
            yield Input(value=self.account, placeholder="account", id="login_account")
            yield Input(placeholder="password", password=True, id="login_password")
            yield Checkbox("Remember password", value=self.remember, id="login_remember")
            yield Button("Login", variant="primary", id="login_button")
            yield Static(self.message, id="login_status", markup=False)

    def on_mount(self) -> None:
        target = "#login_password" if self.account else "#login_account"
        self.query_one(target, Input).focus()

    def on_input_submitted(self, event:Input.Submitted) -> None:
        if event.input.id == "login_account":
            self.query_one("#login_password", Input).focus()
        else:
            self.start_login()

    def on_button_pressed(self, event:Button.Pressed) -> None:
        self.start_login()

    def on_key(self, event:object) -> None:
        if getattr(event, "key", "") == "escape":
            self.dismiss(None)

    def set_status(self, text:str) -> None:
        self.query_one("#login_status", Static).update(text)

    def start_login(self) -> None:
        if not self.busy:
            self.run_worker(self.try_login(), exclusive=True)

    async def try_login(self) -> None:
        account = self.query_one("#login_account", Input).value.strip()
        password = self.query_one("#login_password", Input).value
        remember = self.query_one("#login_remember", Checkbox).value

        self.busy = True
        button = self.query_one("#login_button", Button)
        button.disabled = True
        self.set_status("Logging in ...")
        result = await login.fetch_ticket(account, password)
        self.busy = False
        button.disabled = False

        if result.error:
            self.set_status(result.error)
            return
        if not result.characters:
            self.set_status("This account has no characters")
            return
        self.dismiss(Credentials(account, password, remember, result.characters, result.default_character))
