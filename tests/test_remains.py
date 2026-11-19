from pathlib import Path

from cursed_descent.config import REMAINS_LIMIT
from cursed_descent.remains import RemainsLog


def add_entry(log:RemainsLog, name:str="Lyra", stage:int=3,
              run_id:str="run1", fate:str="eaten") -> None:
    log.add(name=name, gender="Female", fate=fate, stage=stage,
            killer="Rat", tribe="monsters", run_id=run_id)


def test_entries_are_saved_and_reloaded(empty_data_path:Path) -> None:
    log = RemainsLog(empty_data_path)
    add_entry(log)
    reloaded = RemainsLog(empty_data_path)
    assert [entry["name"] for entry in reloaded.entries] == ["Lyra"]
    assert reloaded.entries[0]["id"]


def test_log_is_trimmed_to_limit(empty_data_path:Path) -> None:
    log = RemainsLog(empty_data_path)
    for index in range(REMAINS_LIMIT + 5):
        add_entry(log, name=f"n{index}")
    assert len(log.entries) == REMAINS_LIMIT
    assert log.entries[-1]["name"] == f"n{REMAINS_LIMIT + 4}"


def test_pick_skips_own_run_and_seen_entries(empty_data_path:Path) -> None:
    log = RemainsLog(empty_data_path)
    add_entry(log, run_id="run1")
    assert log.pick(3, "run1", set()) is None
    entry = log.pick(3, "run2", set())
    assert entry["name"] == "Lyra"
    assert log.pick(3, "run2", {entry["id"]}) is None


def test_item_can_be_attached_and_looted_once(
        empty_data_path:Path) -> None:
    log = RemainsLog(empty_data_path)
    add_entry(log)
    assert log.attach_item("Lyra", "run1", "potion_small")
    entry = log.entries[0]
    assert log.loot(entry) == "potion_small"
    assert log.loot(entry) is None


def test_attach_item_needs_matching_run(empty_data_path:Path) -> None:
    log = RemainsLog(empty_data_path)
    add_entry(log)
    assert not log.attach_item("Lyra", "other", "potion_small")


def test_skeletons_are_unique_per_name(empty_data_path:Path) -> None:
    log = RemainsLog(empty_data_path)
    add_entry(log, stage=3)
    add_entry(log, stage=4)
    assert len(log.skeletons("run2", ("eaten",))) == 1


def test_lay_to_rest_hides_skeleton(empty_data_path:Path) -> None:
    log = RemainsLog(empty_data_path)
    add_entry(log)
    entry = log.entries[0]
    log.lay_to_rest(entry["id"], ("eaten",))
    assert log.skeletons("run2", ("eaten",)) == []


def test_graveyard_mentions_empty_wall(empty_data_path:Path) -> None:
    assert "No names yet" in "\n".join(RemainsLog(empty_data_path)
                                       .graveyard())
