import random
from typing import Any

from ...config import GRILL_SPECIAL_PRICE
from ...content import BUFFS
from ...formulas import apply_buff, set_bonus_text
from ...models import Message, Player
from .content import BUILD_WORDS, SPIT_LOOK, VENUE_TEXTS


MENU = ("grill_chicken_half", "grill_chicken_whole", "grill_kebab_wrap",
        "grill_kebab_plate")
FATE = "spit_roasted"


def spit_entries(remains:Any, run_id:str) -> list[dict[str, Any]]:
    return [entry for entry in remains.entries
            if entry["fate"] == FATE and entry["run"] != run_id
            and not entry.get("eaten")]


def spit_look(entry:dict[str, Any]) -> str:
    build = entry.get("victim", {}).get("build", "Average")
    text = SPIT_LOOK.get(entry.get("gender", ""), SPIT_LOOK["any"])
    return text.format(name=entry["name"],
                       build=BUILD_WORDS.get(build, BUILD_WORDS["Average"])
                       .capitalize())


class GrillMixin:
    session: Any
    event: dict[str, Any]

    def grill_spit(self) -> list[dict[str, Any]]:
        return spit_entries(self.session.remains, self.session.run_id)

    def grill_names(self) -> str:
        texts = VENUE_TEXTS["grill"]
        names = [entry["name"] for entry in self.grill_spit()][-4:]
        if not names:
            return texts["no_hooks"]
        return texts["hooks"].format(names=", ".join(names))

    def grill_spit_lines(self) -> list[str]:
        texts = VENUE_TEXTS["grill"]
        entries = self.grill_spit()
        if not entries:
            return [texts["look_spit_empty"]]
        return [texts["look_spit"]] + [spit_look(entry)
                                       for entry in entries[-2:]]

    def offer_grill(self) -> list[str]:
        texts = VENUE_TEXTS["grill"]
        return ["", texts["intro"], texts["door"], self.options_line(texts)]

    def grill_stock(self) -> list[str]:
        return list(MENU)

    def grill_options(self) -> list[str]:
        buys = [f"buy {nr}" for nr, _, _ in self.venue_stock()]
        return buys + ["special", "ask", "grumble", "depart"]

    def grill_examine(self) -> list[Message]:
        texts = VENUE_TEXTS["grill"]
        return [Message("\n".join([texts["look"]]
                                  + self.grill_spit_lines()
                                  + [self.grill_names()]))]

    def grill_action(self, player:Player, command:str,
                     now:float) -> list[Message] | None:
        word = command.split()[0]
        if word == "special":
            return self.grill_special(player)
        if word == "ask":
            return self.grill_ask(player)
        if word == "grumble":
            return self.grill_grumble(player, now)
        return None

    def grill_special(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["grill"]
        key = f"special:{player.name}"
        values = {"name": player.name, "price": GRILL_SPECIAL_PRICE,
                  "gold": player.gold}
        if key in self.event["used"]:
            return [Message(texts["special_used"].format(**values),
                            player.name)]
        if player.gold < GRILL_SPECIAL_PRICE:
            return [Message(texts["special_poor"].format(**values),
                            player.name)]
        player.gold -= GRILL_SPECIAL_PRICE
        self.event["used"].add(key)
        entries = self.grill_spit()
        buff = "grill_special" if entries else "grill_plain"
        lines = []
        if entries:
            entry = entries[-1]
            entry["eaten"] = True
            self.session.remains.save()
            lines.append(texts["special_named"].format(dead=entry["name"]))
        else:
            lines.append(texts["special_plain"])
        apply_buff(player, buff)
        lines.append(texts["special_eat"].format(
            name=player.name, bonus=set_bonus_text(BUFFS[buff])))
        if entries:
            lines.append(texts["special_eaten"].format(
                dead=entries[-1]["name"]))
        self.session.repository.save(player)
        return self.continue_venue(lines)

    def grill_ask(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["grill"]
        key = f"ask:{player.name}"
        if key in self.event["used"]:
            return [Message(texts["ask_used"].format(name=player.name),
                            player.name)]
        self.event["used"].add(key)
        roll = random.random()
        if roll < 0.5:
            lines = [random.choice(texts["ask_excuse"])]
        elif roll < 0.85:
            lines = [texts["ask_smile"], self.grill_names()]
        else:
            lines = [texts["ask_see"]] + self.grill_spit_lines()
        return self.continue_venue(lines)

    def grill_grumble(self, player:Player, now:float) -> list[Message]:
        texts = VENUE_TEXTS["grill"]
        warned = self.event["data"].setdefault("warned", [])
        if player.name not in warned:
            warned.append(player.name)
            return self.continue_venue(
                [texts["complain_warn"].format(name=player.name)])
        from ...combat import fate_text
        session = self.session
        lines = [texts["complain_kill"].format(name=player.name)]
        text = fate_text(player, FATE, None)
        lines += session.kill_outside(
            player, FATE, text, "<<npc.gul_first>>'s spit", "grill")
        if not session.living():
            self.reset()
            return [Message("\n".join(lines + session.end_run()))]
        self.save_party()
        return self.continue_venue(lines)
