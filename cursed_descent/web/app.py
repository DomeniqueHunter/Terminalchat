from contextlib import asynccontextmanager
import asyncio
from pathlib import Path

from fastapi import FastAPI, Form, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from ..accounts import AccountError, ban_text
from ..config import CLOSE_UNAUTHORIZED, MIN_PASSWORD_LENGTH
from . import auth
from .hub import Client, GameHub


STATIC = Path(__file__).parent / "static"


def create_app(data_dir:Path, debug:bool=False,
               login:bool=True) -> FastAPI:
    hub = GameHub(data_dir, debug, login)

    @asynccontextmanager
    async def lifespan(app:FastAPI):
        app.state.hub = hub
        app.state.controller = hub.controller
        hub.ticker = asyncio.create_task(hub.tick_loop())
        yield
        hub.ticker.cancel()

    app = FastAPI(title="Cursed Descent", lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=STATIC), name="static")

    def login_page(error:str="", status:int=200) -> HTMLResponse:
        return HTMLResponse(hub.render(
            "login.html", error=error, min_password=MIN_PASSWORD_LENGTH),
            status_code=status)

    def welcome(account_id:str) -> RedirectResponse:
        response = RedirectResponse("/", status_code=303)
        response.set_cookie(auth.COOKIE, hub.store.start_session(account_id),
                            max_age=auth.MAX_AGE, httponly=True,
                            samesite="strict")
        return response

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    def index(request:Request) -> HTMLResponse:
        if not login:
            return HTMLResponse(hub.page())
        account = auth.account_of(hub.store, request.cookies)
        if account is None:
            return login_page()
        return HTMLResponse(hub.page(Client(None, account=account)))

    @app.post("/login")
    def do_login(name:str=Form(""), password:str=Form("")):
        account = hub.store.login(name, password)
        if account is None:
            return login_page("Unknown account or wrong password.", 401)
        if account.banned:
            return login_page(ban_text(account), 403)
        return welcome(account.id)

    @app.post("/register")
    def do_register(serial:str=Form(""), name:str=Form(""),
                    password:str=Form("")):
        try:
            account = hub.store.register(serial, name, password)
        except AccountError as error:
            return login_page(str(error), 400)
        return welcome(account.id)

    @app.post("/logout")
    def do_logout(request:Request) -> RedirectResponse:
        hub.store.end_session(request.cookies.get(auth.COOKIE, ""))
        response = RedirectResponse("/", status_code=303)
        response.delete_cookie(auth.COOKIE)
        return response

    @app.websocket("/ws")
    async def socket(websocket:WebSocket) -> None:
        account = auth.account_of(hub.store, websocket.cookies)
        if login and account is None:
            await websocket.close(code=CLOSE_UNAUTHORIZED)
            return
        client = await hub.connect(websocket, account)
        try:
            while True:
                await hub.handle(client, await websocket.receive_text())
        except WebSocketDisconnect:
            hub.disconnect(client)

    return app
