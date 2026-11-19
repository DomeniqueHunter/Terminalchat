import json
import shutil
from pathlib import Path

from cursed_descent.config import LOCAL_ACCOUNT_ID
from cursed_descent.identity import new_id
from cursed_descent.storage import PlayerRepository


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "game_data"


def build(target:Path) -> None:
    shutil.copytree(FIXTURE_DIR, target,
                    ignore=shutil.ignore_patterns("players"))
    repository = PlayerRepository(target)
    for path in sorted((FIXTURE_DIR / "players").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault("id", new_id())
        file = repository.file_for(data["id"], LOCAL_ACCOUNT_ID)
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(data), encoding="utf-8")
        repository.store.add_character(
            data["id"], LOCAL_ACCOUNT_ID, data["name"],
            repository.key(data["name"]), False)
    repository.store.close()
