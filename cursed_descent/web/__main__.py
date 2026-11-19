import argparse
import os
from pathlib import Path

import uvicorn

from .app import create_app


DEFAULT_PORT = 6969


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cursed Descent server")
    parser.add_argument("--data", type=Path, default=Path("game_data"))
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--debug", action="store_true",
                        default=os.environ.get("CURSED_DEBUG") == "1",
                        help="show the debug tools")
    parser.add_argument("--no-login", action="store_true",
                        help="skip accounts (local testing only)")
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    app = create_app(arguments.data, arguments.debug,
                      login=not arguments.no_login)
    uvicorn.run(app, host=arguments.host, port=arguments.port)


if __name__ == "__main__":
    main()
