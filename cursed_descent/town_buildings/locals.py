import random

from .. import routines
from ..models import Message, Player
from ..npcs.store import find_local
from ..sheet import sheet_lines
from ..towns import Town
from .chat_content import GENDER_QUOTES


def meet(town:Town, player:Player, text:str, rng:random.Random,
         locals_:list[Player],
         visiting:dict[str, str] | None=None) -> list[Message]:
    visiting = visiting or {}
    if not text.strip():
        lines = ["Locals ([meet <name>]):"] + [
            f"  {npc.full_name} – {npc.profile.get('role', '')}"
            + (f" (visiting the {visiting[npc.npc]})"
               if npc.npc in visiting else "")
            for npc in locals_]
        return [Message("\n".join(lines), player.name)]
    resident = find_local(locals_, text)
    if resident is None:
        return [Message(routines.away_message(player, text)
                        or f"Nobody called '{text}' lives here. [meet] "
                           f"lists the locals.", player.name)]
    profile = resident.profile
    lines = [f"👤 {resident.full_name} – {profile.get('role', '')} "
             f"(at the {visiting.get(resident.npc) or profile.get('building', '')})",
             profile.get("look", ""), "\n".join(sheet_lines(resident)),
             rng.choice(GENDER_QUOTES.get(resident.npc, {}).get(
                 player.gender) or profile.get("quotes") or [""])]
    return [Message("\n".join(line for line in lines if line),
                    player.name)]


def rumors(town:Town, player:Player, rng:random.Random) -> list[Message]:
    heard = rng.sample(town.rumors, min(3, len(town.rumors)))
    lines = ["🗣 You listen in on the town:"] + [f"  • {line}"
                                                  for line in heard]
    deepest = player.records.get("deepest_stage", 0)
    if deepest:
        lines.append(f"  • They still talk about how deep {player.name} "
                     f"got: stage {deepest}.")
    return [Message("\n".join(lines), player.name)]
