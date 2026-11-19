import random
from typing import Any

from .config import INTIMACY_BOND, INTIMACY_RELIEF
from .models import Message, Player
from .needs_runtime import satisfy
from .npc_menu import bump
from .partner_detail import partner_line
from .towns.last_light_humans.cafe.home_seat import guest_of, home_sittings
from .towns.last_light_humans.cafe.guests import heavy_futa
from .towns.last_light_humans.cafe.kin_seat import SIT, kin_text
from .town_buildings.family import relations


MODES = ("domina", "sub", "seat", "throne")
ROLE_FOR_MODE = {"domina": "top", "sub": "bottom"}
INTRO = {
    "domina": "{guest} came because you called, and {guest} knows who "
              "gives the orders in this house.",
    "sub": "You went down on your knees at your own door. {guest} sets "
           "the rules tonight, and you follow them.",
    "throne": "{guest} lies down on the rug without being told twice – "
              "tonight you will use {guest} as your seat.",
    "seat": "{guest} did not come to talk. {guest} came to sit, and you "
            "are the seat.",
}


def split_mode(args:list[str]) -> tuple[list[str], str]:
    if len(args) > 1 and args[-1].casefold() in MODES:
        return args[:-1], args[-1].casefold()
    return args, ""


def seat_record(guest:Player) -> dict[str, Any]:
    return {"name": guest.full_name,
            "weight": guest.body.get("weight", 80),
            "butt": guest.body.get("butt", 110), "cruel": 1,
            "age": guest.age, "height": guest.body.get("height", 170),
            "gender": guest.gender,
            "endowment": guest.body.get("endowment", 0)}


def seat_scene(player:Player, guest:Player, repository:Any,
               rng:random.Random, called:str="") -> list[Message]:
    record = seat_record(guest)
    lines, _, fate = home_sittings(player, record, rng)
    lines.insert(0, INTRO["seat"].format(guest=guest.first_name))
    lines.insert(1, partner_line("facesitting", "receive", player, guest,
                                 rng))
    if called:
        lines.insert(2, called)
    if relations(player).get(guest.id, {}).get("role") == "mother":
        sitter = guest_of(record)
        if heavy_futa(sitter):
            sitter.kin = "son" if player.gender == "Male" else "daughter"
            lines.insert(1, kin_text(SIT, sitter, player.first_name
                                     or player.name, rng))
    if fate:
        player.profile["home_fate"] = fate
    satisfy(player.needs, INTIMACY_RELIEF)
    note = bump(guest, player, INTIMACY_BOND)
    if note:
        lines.append(note.strip())
    repository.save(player)
    repository.save(guest)
    return [Message("\n".join(lines))]


def with_mode(options:dict[str, str], mode:str) -> dict[str, str]:
    if mode in ROLE_FOR_MODE:
        return dict(options, role=ROLE_FOR_MODE[mode])
    return options


def mode_intro(mode:str, guest:Player) -> str:
    return INTRO[mode].format(guest=guest.first_name) if mode else ""
