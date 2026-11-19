import random
from dataclasses import replace
from typing import Any

from ..config import GIG_KEEP_BASE, GIG_KEEP_STEP, GIG_STAGE_PAY, GIG_TURNS
from ..models import Message, Player


GIGS = {
    "butcher_shop": {
        "owner": "Hamhock",
        "keep": "<<npc.hamhock_first>> stops mid-cut and looks {name} over, slowly. "
                "'You know, you'd look lovely on a hook.'",
        "roles": {
            "scrub": {
                "pay": 20, "risk": 0.5,
                "lines": ["{name} scrubs the chopping block until the "
                          "wood is pale. <<npc.hamhock_first>> inspects it and grunts.",
                          "{name} hauls a bucket of scraps to the drain. "
                          "The smell sticks to {their} clothes.",
                          "{name} sharpens knives on the whetstone while "
                          "<<npc.hamhock_first>> hums along, off key."]},
            "sausage": {
                "pay": 30, "risk": 1.0,
                "lines": ["{name} feeds meat into the grinder, one "
                          "handful at a time. 'Faster,' says <<npc.hamhock_first>>.",
                          "{name} ties off sausage links as they spill "
                          "from the nozzle, greasy to the elbows.",
                          "{name} hangs the day's sausages to cure. "
                          "<<npc.hamhock_first>> pats {their} shoulder with a "
                          "cleaver-sized hand."]},
            "hook": {
                "pay": 45, "risk": 2.0,
                "lines": ["{name} is hung up behind the counter as the "
                          "'fresh stock' display. Customers poke and "
                          "haggle.",
                          "{name} hangs there, swaying, while <<npc.hamhock_first>> "
                          "describes {their} best cuts to a buyer.",
                          "A buyer weighs {name}'s thigh in one hand. "
                          "'Marbled,' <<npc.hamhock_first>> says proudly."]},
        },
    },
    "boutique": {
        "owner": "<<boutique.figure_first>>",
        "keep": "<<boutique.figure_first>> snips the thread and smiles. 'Darling, "
                "you are exactly the cut I was missing.'",
        "roles": {
            "sew": {
                "pay": 20, "risk": 0.5,
                "lines": ["{name} hems a leather skirt under <<boutique.figure_short>>'s "
                          "critical eye. 'Straighter. Straighter!'",
                          "{name} sews tiny tags into every garment. "
                          "Some of the names look familiar.",
                          "{name} threads needles in the lamplight. "
                          "<<boutique.figure_short>> checks every stitch."]},
            "fit": {
                "pay": 30, "risk": 1.0,
                "lines": ["{name} models a corset while <<boutique.figure_short>> pins it "
                          "tighter. 'Breathe in. More.'",
                          "{name} turns slowly on the little round "
                          "stage. <<boutique.figure_short>> takes notes.",
                          "A customer fingers the lapel of {name}'s "
                          "jacket and asks the price of the model."]},
            "mannequin": {
                "pay": 45, "risk": 2.0,
                "lines": ["{name} stands in the window as a living "
                          "mannequin, still as a statue, in the newest "
                          "line.",
                          "<<boutique.figure_short>> adjusts {name}'s pose by a finger's "
                          "breadth. 'Perfect. Do not move.'",
                          "Passers-by stop to stare. <<boutique.figure_short>> whispers: "
                          "'Don't blink. They think you're plaster.'"]},
        },
    },
    "brewery": {
        "owner": "Astrid",
        "keep": "<<npc.astrid_first>> wipes her hands on her apron and fixes {name} "
                "with a warm, motherly smile. 'Come, dear. The vats are "
                "hungry.'",
        "roles": {
            "scrub": {
                "pay": 20, "risk": 0.5,
                "lines": ["{name} scours a copper kettle until it shines. "
                          "<<npc.astrid_first>> hums approvingly.",
                          "{name} mops the taproom floor, sticky with "
                          "cream. The smell is heavy and sweet.",
                          "{name} polishes tankards, one by one, under "
                          "<<npc.astrid_first>>'s watchful eye."]},
            "carry": {
                "pay": 30, "risk": 1.0,
                "lines": ["{name} rolls a full keg up the ramp, muscles "
                          "burning. <<npc.astrid_first>> nods.",
                          "{name} hauls crates of bottles to the cellar, "
                          "sweat running down {their} back.",
                          "{name} carries a tray of mugs through the "
                          "crowd. A hand pats {their} backside."]},
            "taste": {
                "pay": 45, "risk": 2.0,
                "lines": ["{name} sips from every new batch while <<npc.astrid_first>> "
                          "takes notes. 'Thick enough? Go on, swallow.'",
                          "{name} tastes the house special straight from "
                          "the tap, flushed and dizzy.",
                          "<<npc.astrid_first>> pours another cup for {name}. 'The "
                          "taster must be thorough. Open wide.'"]},
        },
    },
}


def role_list(phase:str) -> list[str]:
    return list(GIGS[phase]["roles"])


class GigMixin:
    session: Any
    event: dict[str, Any]

    def gig_active(self) -> bool:
        phase = self.event.get("phase")
        if phase not in GIGS:
            return False
        if phase == "brewery":
            return self.brewery_inside()
        return not self.outside()

    def gig_options(self) -> list[str]:
        if not self.gig_active() or self.event["phase"] == "farm":
            return []
        return [f"work {role}" for role in role_list(self.event["phase"])]

    def gig_action(self, player:Player, command:str,
                   now:float) -> list[Message] | None:
        parts = command.split()
        phase = self.event.get("phase")
        if not parts or parts[0] != "work" or phase not in GIGS or (
                phase == "farm") or not self.gig_active():
            return None
        spec = GIGS[phase]
        roles = spec["roles"]
        role = parts[1] if len(parts) > 1 else ""
        if role not in roles:
            names = " | ".join(f"[work {name}]" for name in roles)
            return [Message(f"{spec['owner']} has work: {names}",
                            player.name)]
        done = self.event["data"].setdefault("gigs_done", set())
        if player.name in done:
            return [Message(f"{spec['owner']} shakes a head. 'One shift "
                            f"a day, {player.name}.'", player.name)]
        done.add(player.name)
        return self.run_gig(player, spec, role, now)

    def run_gig(self, player:Player, spec:dict[str, Any], role:str,
                now:float) -> list[Message]:
        job = spec["roles"][role]
        values = {"name": player.name, "their": self.gig_their(player)}
        lines = [f"🛠 {player.name} takes a shift: {role}."]
        earned = round(job["pay"] * GIG_TURNS * (
            1 + self.session.stage * GIG_STAGE_PAY))
        scenes = random.sample(job["lines"], len(job["lines"]))
        for turn in range(1, GIG_TURNS + 1):
            lines.append(scenes[turn - 1].format(**values))
            chance = (GIG_KEEP_BASE + GIG_KEEP_STEP * turn) * job["risk"]
            if random.random() < chance:
                lines.append(spec["keep"].format(**values))
                return self.gig_kept(player, lines, now)
        player.gold += earned
        lines.append(f"The shift is over. {spec['owner']} pays "
                     f"{earned} gold.")
        self.session.repository.save(player)
        return self.gig_continue(lines)

    def gig_their(self, player:Player) -> str:
        from ..config import DEFAULT_GENDER, PRONOUNS
        return PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])[2]

    def gig_kept(self, player:Player, lines:list[str],
                 now:float) -> list[Message]:
        phase = self.event["phase"]
        if phase == "butcher_shop":
            messages = self.venue_sell_self(player, now)
        elif phase == "boutique":
            messages = self.sell_self(player, now)
        else:
            messages = self.brewery_sell_self(player, now, forced=True)
        if messages:
            first = messages[0]
            messages[0] = replace(first, text="\n".join(
                lines + [first.text]))
        return messages

    def gig_continue(self, lines:list[str]) -> list[Message]:
        phase = self.event["phase"]
        if phase == "brewery":
            return self.brewery_continue(lines)
        if phase == "boutique":
            return self.continue_event(lines)
        return self.continue_venue(lines)
