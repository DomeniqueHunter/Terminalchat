from ..models import Player
from ..town_buildings.brothel.practices import can_do


ACT_KEYS = {
    "face": "facesitting", "tramp": "trampling", "foot": "foot",
    "spank": "spanking", "bdsm": "bdsm", "peg": "pegging",
    "water": "watersports", "scat": "scat", "ball": "ballbusting",
    "fjob": "footjob", "bond": "bondage",
    "tit": "titfuck", "oral": "oral", "anal": "anal", "vag": "vaginal",
}
KINKS: dict[str, tuple[str, str, str]] = {
    "bertha": ("dom", "face tramp foot spank", ""),
    "brunhild": ("dom", "spank bdsm foot tramp", ""),
    "starch": ("dom", "spank bdsm peg", ""),
    "rose": ("dom", "vag anal oral peg", "oral tit"),
    "zinnia": ("switch", "oral vag", "oral anal tit"),
    "granita": ("switch", "oral vag", "oral anal"),
    "slithe": ("switch", "oral vag fjob", "oral anal"),
    "tilly": ("switch", "oral vag anal tit", "oral tit"),
    "ada": ("switch", "oral anal tit", "oral tit"),
    "snizzle": ("switch", "oral vag", "oral anal tit"),
    "gerda": ("dom", "oral anal spank", "tit"),
    "astrid": ("dom", "oral anal vag water", "oral tit"),
    "hodra": ("dom", "bdsm spank face", ""),
    "ottoline": ("switch", "bdsm", "spank"),
    "orla": ("switch", "", "spank bdsm"),
    "snikka": ("switch", "ball spank", "tramp"),
    "fizzwick": ("switch", "bdsm peg", "anal bdsm"),
    "hjalmar": ("switch", "bdsm", "foot"),
    "vane": ("switch", "bdsm", "spank peg"),
    "grizzla": ("dom", "bdsm peg ball", ""),
    "hilda": ("dom", "spank tramp water", ""),
    "gurda": ("dom", "spank tramp", "oral tit"),
    "mabel": ("switch", "oral", "oral tit"),
    "brenna": ("switch", "oral vag spank", "anal"),
    "pippa": ("sub", "oral", "spank tramp"),
    "dagna": ("dom", "face spank tramp", ""),
    "velvet": ("switch", "oral fjob", "spank bdsm"),
    "zibba": ("sub", "oral", "tramp foot tit"),
    "alexandra": ("dom", "bdsm face tramp oral anal", ""),
    "edric_vane": ("sub", "oral", "bdsm foot peg"),
    "tomas_wren": ("sub", "oral", "bdsm spank"),
    "mina_vasek": ("dom", "bdsm foot spank", ""),
    "kasia": ("sub", "foot", "bdsm spank"),
    "nadia": ("sub", "oral", "bdsm spank"),
    "ambrose_vale": ("dom", "oral", "bdsm"),
    "mirela_dane": ("sub", "oral", "foot"),
    "vesna_orlov": ("dom", "face bdsm foot", ""),
    "lucian_hale": ("dom", "oral bdsm", ""),
    "selene_draven": ("dom", "face foot", ""),
    "hollis": ("sub", "oral", "foot spank"),
    "cornelius_harrow": ("dom", "oral", ""),
    "cogsby": ("sub", "", "ball spank"),
    "thrain": ("switch", "anal oral bdsm", "oral bdsm"),
    "morgrin": ("switch", "spank ball", "spank"),
    "grunk": ("sub", "", "foot bdsm"),
    "tobble": ("sub", "fjob", "tramp face"),
    "durgin": ("switch", "oral", "spank face"),
    "bram": ("sub", "", "foot spank"),
    "hedda": ("switch", "", ""),
    "ysabel": ("switch", "", ""),
    "skitter": ("switch", "", ""),
    "thorgrim": ("switch", "", ""),
    "wimble": ("switch", "", ""),
    "mortimer": ("switch", "", ""),
    "seraphine": ("dom", "spank", "oral"),
    "ilaria": ("switch", "oral vag", "oral anal tit"),
    "taren": ("dom", "oral anal", ""),
    "ysolde": ("dom", "oral vag face", ""),
    "camille": ("switch", "oral anal peg", "oral tit"),
    "klink": ("sub", "oral", "spank peg"),
    "old_gorm": ("switch", "water", "bdsm"),
    "gul": ("dom", "oral face", ""),
    "odile": ("dom", "bdsm", ""),
    "marguerite": ("sub", "oral", "bdsm"),
    "constance": ("dom", "spank bdsm", ""),
    "reginald": ("dom", "bdsm tramp ball", ""),
    "vesper": ("dom", "bdsm foot face peg", ""),
    "isolde": ("dom", "face foot tramp bdsm", ""),
    "hamhock": ("dom", "bdsm ball spank oral", ""),
    "old_trotter": ("switch", "peg", "spank"),
    "null_master": ("dom", "bdsm peg water", ""),
    "archmage_orlen": ("switch", "bdsm", "spank"),
    "adept_pip": ("sub", "oral", "bdsm peg"),
    "grizzle": ("switch", "foot face", "fjob"),
    "tinkerwick": ("switch", "fjob", "foot"),
    "jorveig": ("dom", "bdsm ball spank anal foot face", "anal"),
    "snik": ("sub", "", "bdsm ball"),
    "brokk": ("sub", "", "bdsm spank"),
    "grash": ("sub", "oral", "bdsm ball"),
    "baroness_ottilie": ("dom", "bdsm face vag", ""),
    "emmerich_grimhold": ("sub", "oral", "spank peg"),
    "old_brannock": ("switch", "", "spank"),
    "sister_merewyn": ("dom", "spank bdsm oral", ""),
    "tobin_kitchen": ("sub", "oral", "face spank"),
    "camilla": ("dom", "face tramp spank bdsm bond oral", "tit"),
    "serafine": ("switch", "oral vag", "oral tit"),
    "isabeau": ("switch", "oral vag tit", "oral anal"),
    "noemi": ("sub", "oral", "spank bdsm foot"),
    "dorian": ("switch", "oral anal", "oral"),
    "cassian": ("dom", "bdsm bond spank peg oral", ""),
    "ignatius": ("switch", "bdsm bond spank", "oral"),
    "leopoldine": ("switch", "bdsm bond", "spank peg"),
    "delphine": ("dom", "bdsm bond spank", ""),
    "sigrunn": ("dom", "face tramp foot spank bdsm bond", "oral"),
    "gudrun": ('dom', 'foot face spank', ''),
    "brynhild": ('dom', 'face spank tramp', 'oral'),
    "orm": ('sub', 'oral', 'foot face'),
    "solveig": ('dom', 'foot tramp', ''),
    "hallvard": ('sub', 'oral', 'bond'),
    "leif": ('sub', 'foot', 'oral'),
    "hjordis": ('dom', 'foot face', 'oral'),
    "gunnar": ('sub', 'foot face', 'oral'),
    "ragnhild": ('dom', 'foot face', 'oral'),
    "ketil": ('sub', 'foot face', 'oral'),
    "ingibjorg": ('dom', 'foot tramp', 'oral'),
    "torben": ('sub', 'foot face', 'oral'),
    "svanhild": ('dom', 'foot face tramp', 'oral'),
    "odd": ('sub', 'foot', 'oral'),
    "ulfhild": ('dom', 'bdsm spank', 'foot'),
    "sven": ('sub', 'bdsm oral', 'foot'),
    "gudlaug": ('dom', 'oral face', 'foot'),
    "eyvind": ('sub', 'oral foot', 'face'),
    "hallgerd": ('dom', 'bdsm foot', 'oral'),
    "eyjolf": ('sub', 'bdsm foot', 'oral'),
    "gunhild": ('dom', 'oral face tramp', 'foot'),
    "thorgrim": ('sub', 'bdsm foot', 'oral'),
    "thyra": ('dom', 'bdsm spank foot', ''),
    "freydis": ('switch', 'oral foot bond', 'tit'),
    "helga": ('dom', 'face tramp spank', ''),
    "bjarni": ('sub', 'oral bond', 'foot'),
    "eira": ('dom', 'foot', 'oral'),
}


OUTCOMES = {"bertha": ["vore"], "astrid": ["anal_vore"]}


def kink_prefs(npc:Player) -> dict | None:
    entry = KINKS.get(npc.npc)
    if entry is None:
        return None
    role, giving, taking = entry
    flow: dict[str, str] = {}
    for letter, words, name in (("G", giving, "give"),
                                ("T", taking, "receive")):
        for word in words.split():
            act = ACT_KEYS[word]
            if can_do(npc.gender, act, name, npc.body):
                flow[act] = flow.get(act, "") + letter
    prefs = {"role": role, "positions": [],
             "flow": {act: "".join(sorted(letters))
                      for act, letters in flow.items()}}
    if npc.npc in OUTCOMES:
        prefs["outcomes"] = list(OUTCOMES[npc.npc])
    return prefs


def apply_kinks(players:list[Player]) -> None:
    for npc in players:
        if "prefs" in npc.profile:
            continue
        prefs = kink_prefs(npc)
        if prefs is not None:
            npc.profile["prefs"] = prefs
