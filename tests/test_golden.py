import json
from pathlib import Path

from tests.scenario import fingerprint, run_scenario


GOLDEN_FILE = Path(__file__).parent / "golden" / "scenario.json"


def test_scenario_matches_golden_transcript() -> None:
    expected = json.loads(GOLDEN_FILE.read_text(encoding="utf-8"))
    actual = fingerprint(run_scenario())
    assert actual["messages"] == expected["messages"]
    for index, (got, want) in enumerate(zip(actual["chunks"],
                                            expected["chunks"])):
        assert got == want, f"first difference in message chunk {index}"


def test_scenario_is_deterministic() -> None:
    assert run_scenario(steps=300) == run_scenario(steps=300)
