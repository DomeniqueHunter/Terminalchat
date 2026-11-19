from cursed_descent.npcs.kinks import KINKS, kink_prefs
from cursed_descent.npcs.seed import default_npcs, sync_prefs
from cursed_descent.preferences import prefs_of


def by_key(key:str):
    return next(npc for npc in default_npcs() if npc.npc == key)


def test_every_fixed_npc_has_a_role_and_kinks() -> None:
    npcs = default_npcs()
    assert {npc.npc for npc in npcs} == set(KINKS)
    assert all("prefs" in npc.profile for npc in npcs)


def test_bertha_loves_facesitting_as_giver() -> None:
    prefs = prefs_of(by_key("bertha"))
    assert prefs["role"] == "dom"
    assert prefs["flow"]["facesitting"] == "G"


def test_roles_follow_the_job_list() -> None:
    assert prefs_of(by_key("hamhock"))["role"] == "dom"
    assert prefs_of(by_key("jorveig"))["flow"]["foot"] == "G"
    assert prefs_of(by_key("emmerich_grimhold"))["role"] == "sub"


def test_kinks_respect_the_body() -> None:
    npc = by_key("bertha")
    npc.gender = "Female"
    assert "vaginal" not in (kink_prefs(by_key("hodra")) or {})["flow"]


def test_sync_fills_missing_prefs_only(controller) -> None:
    repository = controller.repository
    npc = next(n for n in repository.npc_players() if n.npc == "bertha")
    npc.profile.pop("prefs", None)
    repository.save(npc)
    sync_prefs(repository, default_npcs())
    again = next(n for n in repository.npc_players() if n.npc == "bertha")
    assert again.profile["prefs"]["role"] == "dom"
    again.profile["prefs"] = {"role": "sub", "positions": [], "flow": {}}
    repository.save(again)
    sync_prefs(repository, default_npcs())
    kept = next(n for n in repository.npc_players() if n.npc == "bertha")
    assert kept.profile["prefs"]["role"] == "sub"


def test_flow_letters_use_g_before_t() -> None:
    flow = prefs_of(by_key("rose"))["flow"]
    assert flow["oral"] == "GT"


def test_bertha_and_astrid_carry_vore_outcomes() -> None:
    assert by_key("bertha").profile["prefs"]["outcomes"] == ["vore"]
    assert by_key("astrid").profile["prefs"]["outcomes"] == ["anal_vore"]
    assert "outcomes" not in by_key("hilda").profile["prefs"]
