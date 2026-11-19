from pathlib import Path

from cursed_descent.commands import parse_chat
from cursed_descent.config import (
    MAIL_ATTACH_DAYS, MAIL_BOX_SIZE, MAIL_FEE, MAIL_KEEP_DAYS,
    MAIL_PER_HOUR,
)
from cursed_descent.town_buildings.post_office import content
from cursed_descent.town_buildings.post_office.ui import mail_panels
from cursed_descent.towns import TOWNS
from cursed_descent.web.hub import GameHub, mail_text


def setup(data_path:Path, gold:int=500):
    hub = GameHub(data_path)
    services = hub.controller.town
    for name in ("kerl", "galactica"):
        player = hub.controller.repository.load(name)
        player.gold = gold
        player.profile["town"] = "last_light"
        player.profile["where"] = "home"
        hub.controller.repository.save(player)
    return hub, services


def run(hub:GameHub, who:str, line:str) -> str:
    messages = hub.controller.execute(who, parse_chat(f"!{line}"))
    return " ".join(message.text for message in messages)


def load(hub:GameHub, name:str):
    return hub.controller.repository.load(name)


def box_of(services, hub:GameHub, name:str) -> list:
    return services.mail.box(load(hub, name).id).inbox


def test_a_letter_arrives_and_costs_the_fee(data_path:Path) -> None:
    hub, services = setup(data_path)
    reply = run(hub, "kerl", "mail send galactica | Hello | Good morning!")
    assert "posted" in reply
    assert load(hub, "kerl").gold == 500 - MAIL_FEE
    mail = box_of(services, hub, "galactica")[0]
    assert mail["subject"] == "Hello" and not mail["read"]
    assert services.mail.unread(load(hub, "galactica").id) == 1
    text = run(hub, "galactica", f"mail read {mail['id']}")
    assert "Good morning!" in text and mail["read"]


def test_a_letter_needs_subject_and_text(data_path:Path) -> None:
    hub, services = setup(data_path)
    assert "needs a subject" in run(hub, "kerl", "mail send galactica | | x")
    assert load(hub, "kerl").gold == 500


def test_a_parcel_is_collected_only_at_a_post_office(
        data_path:Path) -> None:
    hub, services = setup(data_path)
    kerl = load(hub, "kerl")
    kerl.inventory = ["potion_small", "potion_small"]
    hub.controller.repository.save(kerl)
    run(hub, "kerl", "mail send galactica | Gift | For you | 100 | 1")
    kerl = load(hub, "kerl")
    assert kerl.gold == 500 - MAIL_FEE - 5 - 100
    assert len(kerl.inventory) == 1
    mail = box_of(services, hub, "galactica")[0]
    assert mail["gold"] == 100 and mail["item"]
    assert "post office" in run(hub, "galactica", f"mail collect {mail['id']}")
    run(hub, "galactica", "post_office")
    before = load(hub, "galactica")
    gold, bag = before.gold, len(before.inventory)
    assert "collected" in run(hub, "galactica", f"mail collect {mail['id']}")
    after = load(hub, "galactica")
    assert after.gold == gold + 100 and len(after.inventory) == bag + 1
    assert "no parcel" in run(hub, "galactica", f"mail collect {mail['id']}")


def test_a_full_bag_keeps_the_item_in_the_letter(data_path:Path) -> None:
    hub, services = setup(data_path)
    run(hub, "kerl", "mail send galactica | Gift | For you | 0 | 1")
    full = load(hub, "galactica")
    full.inventory = ["potion_small"] * full.bag_size
    hub.controller.repository.save(full)
    run(hub, "galactica", "post_office")
    mail = box_of(services, hub, "galactica")[0]
    assert "full" in run(hub, "galactica", f"mail collect {mail['id']}")
    assert mail["item"]


def test_uncollected_parcels_go_back_to_the_sender(data_path:Path) -> None:
    hub, services = setup(data_path)
    run(hub, "kerl", "mail send galactica | Gift | For you | 100")
    gold = load(hub, "kerl").gold
    services.world.day += MAIL_ATTACH_DAYS
    services.pass_day()
    back = [mail for mail in box_of(services, hub, "kerl")
            if mail["kind"] == "return"]
    assert back and back[0]["gold"] == 100
    assert "Returned" in back[0]["subject"]
    assert box_of(services, hub, "galactica") == []
    run(hub, "kerl", "post_office")
    run(hub, "kerl", f"mail collect {back[0]['id']}")
    assert load(hub, "kerl").gold == gold + 100
    assert "Nobody can answer" in run(hub, "kerl", f"mail reply {back[0]['id']} | hi")


def test_old_plain_letters_vanish(data_path:Path) -> None:
    hub, services = setup(data_path)
    run(hub, "kerl", "mail send galactica | Old | News")
    services.world.day += MAIL_KEEP_DAYS
    services.pass_day()
    assert box_of(services, hub, "galactica") == []


def test_replying_and_deleting(data_path:Path) -> None:
    hub, services = setup(data_path)
    run(hub, "kerl", "mail send galactica | Hello | Hi there")
    mail = box_of(services, hub, "galactica")[0]
    run(hub, "galactica", f"mail reply {mail['id']} | Hi back")
    answer = box_of(services, hub, "kerl")[0]
    assert answer["subject"] == "Re: Hello" and answer["from_name"] == "Galactica"
    assert "Hi back" in answer["body"]
    run(hub, "galactica", f"mail delete {mail['id']}")
    assert box_of(services, hub, "galactica") == []


def test_parcel_letters_cannot_be_deleted(data_path:Path) -> None:
    hub, services = setup(data_path)
    run(hub, "kerl", "mail send galactica | Gift | Money | 50")
    mail = box_of(services, hub, "galactica")[0]
    assert "still holds a parcel" in run(
        hub, "galactica", f"mail delete {mail['id']}")


def test_poor_senders_and_bad_gold(data_path:Path) -> None:
    hub, services = setup(data_path, gold=12)
    assert "much gold" in run(hub, "kerl", "mail send galactica | A | B | 50")
    assert "wants" in run(hub, "kerl", "mail send galactica | A | B | 5")
    assert "number" in run(hub, "kerl", "mail send galactica | A | B | lots")
    assert load(hub, "kerl").gold == 12


def test_blocking_stops_letters(data_path:Path) -> None:
    hub, services = setup(data_path)
    run(hub, "galactica", "mail block kerl")
    assert "does not want" in run(hub, "kerl",
                                  "mail send galactica | A | B")
    run(hub, "galactica", "mail unblock kerl")
    assert "posted" in run(hub, "kerl", "mail send galactica | A | B")


def test_the_mailbox_and_the_hour_are_limited(data_path:Path) -> None:
    hub, services = setup(data_path, gold=100000)
    stamp = [1000.0]
    services.mail.clock = lambda: stamp[0]
    for number in range(MAIL_PER_HOUR):
        assert "posted" in run(hub, "kerl", f"mail send galactica | {number} | x")
    assert "per hour" in run(hub, "kerl", "mail send galactica | A | B")
    stamp[0] += 3601
    assert "posted" in run(hub, "kerl", "mail send galactica | A | B")
    box = services.mail.box(load(hub, "galactica").id)
    box.inbox = box.inbox * 3
    box.inbox = box.inbox[:MAIL_BOX_SIZE]
    stamp[0] += 3601
    assert "full" in run(hub, "kerl", "mail send galactica | A | B")


def test_letters_to_npcs_are_answered_later(data_path:Path) -> None:
    hub, services = setup(data_path)
    stamp = [1000.0]
    services.mail.clock = lambda: stamp[0]
    npc = next(npc for npc in hub.controller.repository.npc_players()
               if npc.npc == "hedda")
    gold = npc.gold
    run(hub, "kerl", "mail send hedda | Hello | Good morning | 20")
    assert next(n for n in hub.controller.repository.npc_players()
                if n.npc == "hedda").gold == gold + 20
    assert box_of(services, hub, "kerl") == []
    stamp[0] += 400
    assert "Hedda" in run(hub, "kerl", "mail")
    answer = box_of(services, hub, "kerl")[0]
    assert answer["kind"] == "npc" and "gift" in answer["body"]
    assert answer["subject"] == "Re: Hello"


def test_nobody_to_write_to_and_no_mail_in_a_run(data_path:Path) -> None:
    hub, services = setup(data_path)
    assert "nobody" in run(hub, "kerl", "mail send nobodyhere | A | B")
    assert "nobody" in run(hub, "kerl", "mail send kerl | A | B")
    services.run_check = lambda name: True
    assert "back from the dungeon" in run(hub, "kerl", "mail")


def test_every_town_has_a_post_office_and_a_clerk() -> None:
    from cursed_descent.towns import town_of  # noqa: F401
    for key, town in TOWNS.items():
        if town.wip:
            continue
        assert "post_office" in town.buildings, key
        clerk = content.CLERKS[key][0]
        assert clerk in {resident.key for resident in town.residents}, key


def test_the_panels_and_the_form_text(data_path:Path) -> None:
    hub, services = setup(data_path)
    run(hub, "kerl", "mail send galactica | Hello | Hi")
    panels = mail_panels(services, load(hub, "galactica"))
    titles = [panel.title for panel in panels]
    assert titles[0].startswith("Inbox (1)") and "Write a letter" in titles
    assert mail_text({"mail_to": "galactica", "mail_subject": "A|B",
                      "mail_body": "Body", "mail_gold": "5",
                      "mail_item": ""}) == (
        "!mail send galactica | A/B | Body | 5 | ")
    assert mail_text({"mail_to": ""}) == ""


def test_the_form_sends_a_letter_over_the_socket(data_path:Path) -> None:
    import json
    from fastapi.testclient import TestClient
    from cursed_descent.web.app import create_app
    with TestClient(create_app(data_path, login=False)) as client:
        hub = client.app.state.hub
        with client.websocket_connect("/ws") as socket:
            socket.receive_text()
            socket.send_text(json.dumps({
                "action": "cmd", "text": "!mail send", "viewer": "kerl",
                "mail_to": "galactica", "mail_subject": "Hi",
                "mail_body": "From the form", "mail_gold": "",
                "mail_item": ""}))
            socket.receive_text()
        galactica = hub.controller.repository.load("galactica")
        mails = hub.controller.town.mail.box(galactica.id).inbox
        assert mails and mails[0]["body"] == "From the form"
        panel = hub.panels_for(hub.clients[0]) if hub.clients else ""
        assert "tab-mail" in panel or panel == ""


def test_double_forms_and_empty_gold_still_send(data_path:Path) -> None:
    assert mail_text({"mail_to": ["a", "b"], "mail_subject": ["x", ""],
                      "mail_body": ["y", ""], "mail_gold": ["", ""],
                      "mail_item": ["", ""]}) == "!mail send a | x | y |  | "
    hub, services = setup(data_path)
    assert "posted" in run(hub, "kerl", "mail send galactica | A | B |  | ")


def test_the_post_office_panel_has_no_second_form(data_path:Path) -> None:
    from cursed_descent.town_buildings.post_office.ui import panel
    hub, services = setup(data_path)
    shown = panel(services, load(hub, "kerl"))
    assert all(not section.choices for section in shown.sections)


def recipients(services, hub:GameHub, who:str) -> set[str]:
    panel = next(item for item in mail_panels(services, load(hub, who))
                 if item.title == "Write a letter")
    choice = next(item for item in panel.choices if item.name == "mail_to")
    return {value for value, _ in choice.options if value}


def test_only_known_people_are_listed_as_recipients(data_path:Path) -> None:
    hub, services = setup(data_path)
    assert "Galactica" not in recipients(services, hub, "kerl")
    assert "hilda" not in {name.casefold()
                           for name in recipients(services, hub, "kerl")}
    run(hub, "kerl", "mail send galactica | Hello | Hi")
    assert "Galactica" in recipients(services, hub, "kerl")
    hilda = next(npc for npc in hub.controller.repository.npc_players()
                 if npc.npc == "hilda")
    hilda.profile.setdefault("friends", {})[load(hub, "kerl").id] = 2
    hub.controller.repository.save(hilda)
    assert hilda.name in recipients(services, hub, "kerl")


def test_a_typed_name_overrides_the_list_and_may_hit_an_npc(
        data_path:Path) -> None:
    hub, services = setup(data_path)
    assert mail_text({"mail_to": "kerl", "mail_name": "Hilda",
                      "mail_subject": "S", "mail_body": "B"}).startswith(
        "!mail send Hilda | S")
    assert "posted" in run(hub, "kerl", "mail send hilda | Hi | Hello")
    assert "nobody like that" in run(hub, "kerl",
                                     "mail send Nobody Atall | Hi | Hello")


def test_read_letters_vanish_after_two_weeks_and_each_player_has_a_file(
        data_path:Path) -> None:
    from cursed_descent.mail import sweep
    hub, services = setup(data_path)
    run(hub, "kerl", "mail send galactica | Hello | Good morning!")
    run(hub, "kerl", "mail send galactica | Again | Still there?")
    first, second = box_of(services, hub, "galactica")
    run(hub, "galactica", f"mail read {first['id']}")
    services.mail.save()
    galactica = load(hub, "galactica")
    assert (data_path / "mail" / f"{galactica.id}.json").exists()
    day = first["day"]
    assert not sweep(services.mail, hub.controller.repository, day + 13)
    assert sweep(services.mail, hub.controller.repository, day + 14) == 1
    assert box_of(services, hub, "galactica") == [second]


def test_collected_parcels_vanish_after_a_week(data_path:Path) -> None:
    from cursed_descent.mail import sweep
    hub, services = setup(data_path)
    run(hub, "kerl", "mail send galactica | Gift | Here! | 50")
    mail = box_of(services, hub, "galactica")[0]
    load(hub, "galactica").profile["where"] = "post_office"
    player = load(hub, "galactica")
    player.profile["where"] = "post_office"
    hub.controller.repository.save(player)
    run(hub, "galactica", f"mail collect {mail['id']}")
    assert "taken_day" in mail
    day = mail["taken_day"]
    assert not sweep(services.mail, hub.controller.repository, day + 6)
    assert sweep(services.mail, hub.controller.repository, day + 7) == 1


def test_admin_rename_updates_handle_file_and_references(
        data_path:Path) -> None:
    hub, services = setup(data_path)
    hub.controller.debug = True
    run(hub, "kerl", "mail send galactica | Hello | Good morning!")
    kerl_id = load(hub, "kerl").id
    reply = run(hub, "kerl", "rename kerl | Brainy")
    assert "now called Brainy" in reply
    repository = hub.controller.repository
    assert repository.load("Brainy").id == kerl_id
    assert not repository.exists("kerl")
    mail = box_of(services, hub, "galactica")[0]
    assert mail["from_name"] == "Brainy"
    assert "taken" in run(hub, "Brainy", "rename Brainy | galactica")
    assert "Usage" in run(hub, "Brainy", "rename Brainy")
