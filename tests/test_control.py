import re
from pathlib import Path

import pytest

from cursed_descent import control
from cursed_descent.towns import START_TOWN
from cursed_descent.control import ControlKind, discovery

README = Path(__file__).resolve().parent.parent / "readme" / "control.md"


def text(messages) -> str:
    return "\n".join(message.text for message in messages)


@pytest.fixture
def leash(monkeypatch):
    kind = ControlKind(key="test_leash", title="Leash", hours=10,
                       start_text="{holder} leashes {name}.")
    monkeypatch.setattr(discovery, "_FOUND", {kind.key: kind})
    return kind


def test_readme_example_is_a_valid_kind() -> None:
    block = re.search(r"```python\n(.*?)```", README.read_text(), re.S)
    scope: dict = {}
    exec(block.group(1), scope)
    assert all(isinstance(kind, ControlKind) for kind in scope["KINDS"])


def test_every_control_file_in_the_game_is_valid() -> None:
    discovery.reset()
    assert isinstance(control.kinds(), dict)


def test_held_player_is_locked_but_can_watch(controller, leash) -> None:
    player = controller.repository.load("Kerl")
    reply = text(control.start(controller.town, player, "test_leash", "Eve"))
    assert "Eve leashes" in reply
    assert control.holder_of(player) == "Eve"
    assert "leash" in text(controller.handle("Kerl", "!shop")).lower()
    assert "watch" in text(controller.handle("Kerl", "!slave")).lower()
    assert control.holders("test_leash", controller.repository) == [player]


def test_safeword_frees(controller, leash) -> None:
    player = controller.repository.load("Kerl")
    control.start(controller.town, player, "test_leash", "Eve")
    controller.handle("Kerl", "!slave release")
    assert control.kind_of(controller.repository.load("Kerl")) is None


def test_hold_expires_with_world_time(controller, leash) -> None:
    player = controller.repository.load("Kerl")
    control.start(controller.town, player, "test_leash", "Eve")
    player.profile["control"]["until"] = controller.town.world_hours() - 1
    controller.repository.save(player)
    assert "free again" in text(control.tick(controller.town))
    assert control.kind_of(player) is None


def test_end_leaves_a_slave_and_respawns_the_player(controller,
                                                    leash) -> None:
    player = controller.repository.load("Kerl")
    control.start(controller.town, player, "test_leash", "Eve")
    assert "button" in text(controller.handle("Kerl", "!slave end"))
    assert control.kind_of(player) is not None
    controller.handle("Kerl", "!slave end confirm")
    slaves = [npc for npc in controller.repository.npc_players()
              if npc.npc == "slave"]
    assert len(slaves) == 1 and slaves[0].profile["holder"] == "Eve"
    assert slaves[0].full_name == controller.repository.load("Kerl").name
    kerl = controller.repository.load("Kerl")
    assert control.kind_of(kerl) is None and kerl.records["respawn_day"]
    assert kerl.profile["town"] == START_TOWN
    locked = text(controller.handle("Kerl", "!shop"))
    assert "slave" in locked and "Café" not in locked


def test_no_safeword_kind(controller, monkeypatch) -> None:
    kind = ControlKind(key="hard", title="Hard", safeword=False)
    monkeypatch.setattr(discovery, "_FOUND", {"hard": kind})
    player = controller.repository.load("Kerl")
    control.start(controller.town, player, "hard", "Eve")
    assert "no safeword" in text(controller.handle("Kerl", "!slave release"))
    assert control.kind_of(player) is not None


def enter_castle(controller, name:str = "Kerl"):
    player = controller.repository.load(name)
    player.profile.update(town="dusk_hollow", where="castle",
                          castle_invite=True)
    controller.repository.save(player)
    controller.town.routines.tick(12.0)
    return player


def test_offering_yourself_warns_then_enslaves(controller,
                                               monkeypatch) -> None:
    enter_castle(controller)
    monkeypatch.setattr(controller.town.rng, "random", lambda: 0.0)
    first = text(controller.handle("Kerl", "!castle 4"))
    assert "never more" in first and "Select the offer again" in first
    second = text(controller.handle("Kerl", "!castle 4"))
    assert "collar" in second
    kerl = controller.repository.load("Kerl")
    assert control.holder_of(kerl) == "Alexandra"
    assert kerl.profile["control"]["data"]["npc"] == "alexandra"
    assert "leash" in text(controller.handle("Kerl", "!shop")).lower()


def test_offer_needs_invitation_and_a_present_duchess(controller) -> None:
    player = controller.repository.load("Kerl")
    player.profile.update(town="dusk_hollow", where="castle")
    controller.repository.save(player)
    controller.town.routines.tick(12.0)
    reply = text(controller.handle("Kerl", "!castle 4")).lower()
    assert "invitation" in reply or "letter" in reply
    player.profile["castle_invite"] = True
    controller.repository.save(player)
    controller.town.routines.tick(5.0)
    assert "asleep" in text(controller.handle("Kerl", "!castle 4"))


def test_full_household_loses_its_oldest(controller, monkeypatch) -> None:
    from cursed_descent.towns.dusk_hollow_vampires.castle import slaves
    enter_castle(controller)
    monkeypatch.setattr(controller.town.rng, "random", lambda: 0.0)
    controller.town.world.day = 1
    before = {m.who.name: m.since
              for m in slaves.members(controller.town)}
    assert len(before) == 2
    for name in ("Galactica",):
        extra = controller.repository.load(name)
        extra.profile.update(town="dusk_hollow", where="castle",
                             castle_invite=True)
        controller.repository.save(extra)
        controller.handle(name, "!castle 4")
        controller.handle(name, "!castle 4")
    controller.handle("Kerl", "!castle 4")
    reply = text(controller.handle("Kerl", "!castle 4"))
    assert "nothing left to take" in reply
    members = slaves.members(controller.town)
    assert len(members) == slaves.CAP
    assert not {m.who.name for m in members} & {
        name for name, since in before.items() if since == min(
            before.values())}


def test_presentation_button_vanishes_with_the_invitation(controller) -> None:
    from cursed_descent.web import views
    player = controller.repository.load("Kerl")
    player.profile.update(town="dusk_hollow", where="salon")
    controller.repository.save(player)

    def labels() -> str:
        panels = views.location_panel(controller, player)
        return str([button.label for panel in panels
                    for button in panel.buttons])

    assert "presented" in labels()
    player.profile["castle_invite"] = True
    assert "presented" not in labels()
    assert "Take tea" in labels()


def test_oldest_player_slave_is_drunk_dry_and_told(controller,
                                                    monkeypatch) -> None:
    from cursed_descent.towns.dusk_hollow_vampires.castle import slaves
    enter_castle(controller)
    monkeypatch.setattr(controller.town.rng, "random", lambda: 0.0)
    for name in ("Galactica", "Kerl"):
        who = controller.repository.load(name)
        who.profile.update(town="dusk_hollow", where="castle",
                           castle_invite=True)
        controller.repository.save(who)
        controller.handle(name, "!castle 4")
        controller.handle(name, "!castle 4")
    assert all(m.kind == "player" for m in slaves.members(controller.town))
    other = next(n for n in controller.repository.names()
                 if n not in ("Kerl", "Galactica"))
    who = controller.repository.load(other)
    who.profile.update(town="dusk_hollow", where="castle",
                       castle_invite=True)
    controller.repository.save(who)
    controller.handle(other, "!castle 4")
    reply = controller.handle(other, "!castle 4")
    told = [m for m in reply if "drunk dry" in m.text]
    assert any(m.recipient != who.name for m in told)
    galactica = controller.repository.load("Galactica")
    assert control.kind_of(galactica) is None
    assert galactica.last_fate == "drained" and galactica.records["respawn_day"]
    assert "drunk dry" in text(controller.handle("Galactica", "!shop"))



def test_held_player_can_examine_people_around(controller) -> None:
    from cursed_descent.control import discovery
    from cursed_descent.web import views
    discovery.reset()
    controller.town.routines.tick(12.0)
    player = controller.repository.load("Kerl")
    player.profile.update(town="dusk_hollow", where="castle")
    control.start(controller.town, player, "leash_slave", "Alexandra",
                  npc="alexandra")
    panel = views.location_panel(controller, player)[0]
    around = panel.sections[0]
    labels = str(around)
    assert "Examine" in labels and "Alexandra" in labels
    assert "Talk" not in labels


def test_drained_slave_disappears_from_the_castle(controller,
                                                  monkeypatch) -> None:
    from cursed_descent.towns import TOWNS
    from cursed_descent.web import views
    enter_castle(controller)
    monkeypatch.setattr(controller.town.rng, "random", lambda: 0.0)
    town = TOWNS["dusk_hollow"]
    assert "Edric" in str(views.residents_panel(town, "castle"))
    controller.handle("Kerl", "!castle 4")
    controller.handle("Kerl", "!castle 4")
    shown = str(views.residents_panel(town, "castle"))
    assert ("Edric" in shown) != ("Tomas" in shown)


def test_drained_slave_stays_dead_and_the_herd_is_refilled(
        controller, monkeypatch) -> None:
    from cursed_descent.towns.dusk_hollow_vampires.castle import slaves
    enter_castle(controller)
    monkeypatch.setattr(controller.town.rng, "random", lambda: 0.0)
    for _ in range(3):
        controller.town.world.day += 1
        for name in ("Kerl",):
            who = controller.repository.load(name)
            who.profile["control"] = None
            who.profile.pop("control", None)
            controller.repository.save(who)
            controller.handle(name, "!castle 4")
            controller.handle(name, "!castle 4")
    npcs = controller.repository.npc_players()
    dead = [npc for npc in npcs if npc.profile.get("dead")]
    assert dead
    assert all(npc.profile["gone_until"] > 10 ** 6 for npc in dead)
    members = slaves.members(controller.town)
    assert len(members) == slaves.CAP
    assert not any(member.who in dead for member in members)
    assert any(npc.npc == "slave" and npc.profile.get("control")
               == slaves.KIND for npc in controller.repository.npc_players())


def test_slavereset_clears_cooldown_and_leash(controller, leash) -> None:
    controller.debug = True
    player = controller.repository.load("Kerl")
    player.profile["castle_offer_later"] = 10 ** 9
    controller.repository.save(player)
    control.start(controller.town, player, "test_leash", "Eve")
    reply = text(controller.handle("Kerl", "!slavereset"))
    kerl = controller.repository.load("Kerl")
    assert "reset" in reply and "castle_offer_later" not in kerl.profile
    assert control.kind_of(kerl) is None


def test_old_drained_marks_are_made_final(controller) -> None:
    from cursed_descent.towns.dusk_hollow_vampires.castle import slaves
    edric = next(npc for npc in controller.repository.npc_players()
                 if npc.npc == "edric_vane")
    edric.profile["slave_gone"] = 5
    controller.repository.save(edric)
    controller.town.world.day = 10
    members = slaves.members(controller.town)
    assert edric not in [member.who for member in members]
    assert controller.repository.load(edric.name).profile["dead"]


def test_new_slaves_are_listed_and_can_be_examined(controller) -> None:
    from cursed_descent.towns import TOWNS
    from cursed_descent.towns.dusk_hollow_vampires.castle import slaves
    from cursed_descent.web import views
    enter_castle(controller)
    for edric in ("edric_vane", "tomas_wren"):
        npc = next(n for n in controller.repository.npc_players()
                   if n.npc == edric)
        npc.profile["dead"] = True
        controller.repository.save(npc)
    members = slaves.members(controller.town)
    assert len(members) == slaves.CAP
    shown = str(views.residents_panel(TOWNS["dusk_hollow"], "castle", True,
                                      controller))
    assert members[0].who.first_name in shown
    reply = text(controller.handle(
        "Kerl", f"!examine {members[0].who.first_name}"))
    assert "kneels" in reply


def test_household_count_is_shown(controller) -> None:
    from cursed_descent.web import views
    enter_castle(controller)
    player = controller.repository.load("Kerl")
    assert "of 2 slaves" in str(views.location_panel(controller, player))


def test_time_can_skip_days(controller) -> None:
    controller.debug = True
    before = controller.town.world.day
    reply = text(controller.handle("Kerl", "!time +3d"))
    assert "3 world days passed" in reply
    assert controller.town.world.day == before + 3


def test_other_players_see_held_player_in_locals(controller) -> None:
    from cursed_descent.control import discovery
    from cursed_descent.web import views
    discovery.reset()
    nick = controller.repository.load("Kerl")
    nick.profile.update(town="dusk_hollow", where="castle")
    control.start(controller.town, nick, "leash_slave", "Alexandra",
                  npc="alexandra")
    other = controller.repository.load("Galactica")
    other.profile.update(town="dusk_hollow", where="castle")
    controller.repository.save(other)
    panels = views.location_panel(controller, other)
    shown = str(panels)
    assert nick.name in shown and "(player)" in shown


def test_others_in_the_room_are_told_and_can_see_who_is_held(
        controller, monkeypatch) -> None:
    from cursed_descent.control import discovery
    discovery.reset()
    enter_castle(controller)
    watcher = controller.repository.load("Galactica")
    watcher.profile.update(town="dusk_hollow", where="castle")
    controller.repository.save(watcher)
    monkeypatch.setattr(controller.town.rng, "random", lambda: 0.0)
    controller.handle("Kerl", "!castle 4")
    reply = controller.handle("Kerl", "!castle 4")
    seen = [m.text for m in reply if m.recipient.casefold() == "galactica"]
    assert any("collar" in line for line in seen)
    assert any("nothing left to take" in line for line in seen)
    look = text(controller.handle("Galactica", "!examine Kerl"))
    assert "collar" in look and "cannot act" in look


def test_blood_bank_first_donation_of_the_day_is_free(controller) -> None:
    player = controller.repository.load("Kerl")
    player.profile.update(town="dusk_hollow", where="blood_bank")
    controller.repository.save(player)
    from cursed_descent.formulas import max_hp
    full = controller.repository.load("Kerl")
    full.hp = max_hp(full)
    controller.repository.save(full)
    first = text(controller.handle("Kerl", "!blood_bank 1"))
    assert "❤ −" not in first
    second = text(controller.handle("Kerl", "!blood_bank 1"))
    assert "−" in second and "HP" in second
    controller.town.pass_day()
    third = text(controller.handle("Kerl", "!blood_bank 1"))
    assert "−" not in third


def test_stored_regular_without_address_gets_one_fixed_address(
        data_path) -> None:
    from cursed_descent.town_buildings.regulars import Regulars, slug
    from cursed_descent.storage import write_json
    reg = Regulars(data_path, "last_light", "owner")
    path = reg.folder("brothel") / f"{slug('Old Tom')}.json"
    write_json(path, {"name": "Old Tom", "age": 40, "visits": 3})
    first = reg.get("brothel", "Old Tom")["home"]
    assert first.startswith("No. ")
    assert reg.get("brothel", "Old Tom")["home"] == first
    again = Regulars(data_path, "last_light", "owner")
    assert again.get("brothel", "Old Tom")["home"] == first
