import json
from pathlib import Path

from fastapi.testclient import TestClient

from cursed_descent.create_form import evaluate
from cursed_descent.web.app import create_app


def form(**changes:str) -> dict[str, str]:
    data = {
        "cf_first": "Lyra", "cf_last": "Dawn", "cf_gender": "Female",
        "cf_race": "human", "cf_age": "25", "cf_orientation": "both",
        "cf_height": "170", "cf_weight": "65", "cf_build": "Average",
        "cf_bust": "300", "cf_fake": "0", "cf_muscle": "25",
        "cf_butt": "95", "cf_stat_strength": "3", "cf_stat_agility": "3",
        "cf_stat_vitality": "2", "cf_stat_intelligence": "2",
        "cf_personality": "Dry wit.", "cf_look": "Tall, freckled.",
        "cf_flist": "https://www.f-list.net/c/Lyra Dawn"}
    data.update(changes)
    return data


def test_a_valid_form_builds_the_character() -> None:
    result = evaluate(form())
    assert result.errors == [] and result.points_left == 0
    player = result.player
    assert player.name == "Lyra Dawn" and player.race == "human"
    assert player.age == 25 and player.personality == "Dry wit."
    assert player.body["bust"] == 300 and player.stats["strength"] == 5 + 3
    assert player.profile["look"] == "Tall, freckled."
    assert player.profile["flist"] == "https://www.f-list.net/c/Lyra Dawn"
    assert player.profile["orientation"] == "both"


def test_none_gender_and_other_races_are_refused() -> None:
    assert evaluate(form(cf_gender="None")).errors
    for race in ("dwarf", "goblin", "vampire", "elf"):
        assert evaluate(form(cf_race=race)).errors


def test_bad_values_are_reported() -> None:
    cases = {"cf_first": "", "cf_first": "Lyra<script>", "cf_age": "17",
             "cf_height": "300", "cf_stat_strength": "9",
             "cf_flist": "http://evil.example/c/x",
             "cf_personality": "x" * 501, "cf_orientation": "nope"}
    for key, value in cases.items():
        assert evaluate(form(**{key: value})).errors, key


def test_hung_fields_only_count_for_hung_genders() -> None:
    ignored = evaluate(form(cf_endowment="99", cf_shape="Bogus"))
    assert not ignored.errors and ignored.player.body["endowment"] != 99
    assert not evaluate(form(cf_gender="Male", cf_endowment="20",
                             cf_girth="14", cf_balls="6",
                             cf_shape="Human")).errors


def test_the_form_creates_a_character_over_the_socket(
        tmp_path:Path) -> None:
    with TestClient(create_app(tmp_path, login=False)) as client:
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            socket.send_text(json.dumps({"action": "create_preview",
                                         **form(cf_stat_strength="1")}))
            assert "<svg" in socket.receive_text()
            socket.send_text(json.dumps({"action": "create_submit",
                                         **form(cf_age="12")}))
            assert "Age must be" in socket.receive_text()
            socket.send_text(json.dumps({"action": "create_submit",
                                         **form()}))
            reply = socket.receive_text()
            assert 'data-done="1"' in reply
        saved = client.app.state.controller.repository.load("Lyra Dawn")
        assert saved is not None and saved.age == 25


def test_one_bad_field_does_not_reset_the_others() -> None:
    result = evaluate(form(cf_height="185", cf_butt="14"))
    assert result.player.body["height"] == 185
    assert set(result.fields) == {"cf_butt"}


def test_flist_links_may_be_percent_encoded() -> None:
    link = "https://www.f-list.net/c/Lyra%20Dawn"
    result = evaluate(form(cf_flist=link))
    assert not result.errors and result.player.profile["flist"] == link
    assert evaluate(form(cf_flist="https://www.f-list.net/c/a%zz")).errors
    assert evaluate(form(cf_flist="https://www.f-list.net/c/a/b")).errors
