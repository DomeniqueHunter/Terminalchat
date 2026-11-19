from typing import Any

from ..config import MAX_PARTY_SIZE
from ..models import Action, Message, Player
from .autopilot import autopilot_choice
from .hire import hire_price, owns_maid, spend_points


DISSOLVES = ("💨 {name} is gone. The curse unravels the fallen maid until "
             "nothing is left but a few specks of dust.")


class CompanionsMixin:
    state: str
    party: list[Player]
    enemies: list[Any]
    autopilot: set[str]
    manual: set[str]
    heir_notes: list[str]
    repository: Any

    def is_auto(self, player:Player) -> bool:
        return ((bool(player.npc) or player.name in self.autopilot)
                and player.name not in self.manual)

    def is_companion(self, player:Player) -> bool:
        return bool(player.npc) or player.name in self.autopilot

    def set_auto(self, player:Player, args:list[str]) -> list[Message]:
        if self.member(player.name) is None:
            return [Message("You are not in a party.", player.name)]
        words = [word for word in args if word.casefold() not in ("on", "off")]
        mode = next((word.casefold() for word in args
                     if word.casefold() in ("on", "off")), "")
        if not words:
            return self.auto_overview(player)
        handle = self.repository.resolve(" ".join(words))
        companion = self.member(handle)
        if companion is None:
            return [Message("There is no such companion in the party.",
                            player.name)]
        if not self.is_companion(companion):
            return self.hand_over(player, companion, mode)
        enable = (mode == "on") if mode else companion.name in self.manual
        if enable:
            self.manual.discard(companion.name)
            if self.state == "combat" and companion.alive:
                companion.action = self.npc_action(companion)
        else:
            self.manual.add(companion.name)
        state = "on" if enable else "off (you steer them)"
        return [Message(f"Autopilot for {companion.full_name}: {state}.")]

    def hand_over(self, player:Player, hero:Player,
                  mode:str) -> list[Message]:
        if mode == "off":
            return [Message(f"{hero.full_name} is already steered by "
                            f"hand.", player.name)]
        others = [member for member in self.party
                  if member is not hero and not self.is_auto(member)]
        if not others:
            return [Message("At least one hero must stay under manual "
                            "control.", player.name)]
        self.autopilot.add(hero.name)
        self.manual.discard(hero.name)
        if self.state == "combat" and hero.alive:
            hero.action = self.npc_action(hero)
        return [Message(f"Autopilot for {hero.full_name}: on.")]

    def auto_overview(self, player:Player) -> list[Message]:
        companions = [member for member in self.party
                      if self.is_companion(member)]
        if not companions:
            return [Message("There are no companions in the party.",
                            player.name)]
        lines = [f"  {member.full_name}: "
                 f"{'on' if self.is_auto(member) else 'off'}"
                 for member in companions]
        return [Message("Autopilot ([auto <name> on|off]):\n"
                        + "\n".join(lines), player.name)]

    def dissolves(self, player:Player) -> bool:
        return player.npc == "maid" and not player.profile.get("graduate")

    def dissolve_dead_maids(self) -> list[str]:
        lines: list[str] = []
        for member in list(self.party):
            if member.alive or not self.dissolves(member):
                continue
            self.party.remove(member)
            self.manual.discard(member.name)
            self.autopilot.discard(member.name)
            self.repository.bury(member, "maid: fell in the dungeon")
            self.repository.release(member)
            lines.append(DISSOLVES.format(name=member.full_name))
        return lines

    def living(self) -> list[Player]:
        alive = [player for player in self.party if player.alive]
        if any(not self.is_auto(player) for player in alive):
            return alive
        heirs = [player for player in alive if not player.npc]
        if not heirs:
            return []
        self.manual.add(heirs[0].name)
        self.heir_notes.append(
            f"👑 {heirs[0].full_name} takes over as main hero.")
        return alive

    def take_heir_notes(self) -> list[str]:
        notes, self.heir_notes[:] = list(self.heir_notes), []
        return notes

    def humans(self) -> list[Player]:
        return [player for player in self.party
                if not self.is_auto(player)]

    def hire(self, player:Player, text:str) -> list[Message]:
        if self.state != "lobby" or self.member(player.name) is None:
            return [Message("You can only hire a companion from inside an "
                            "open lobby.", player.name)]
        if not text.strip():
            return self.roster_lines(player)
        target = self.repository.load(self.repository.resolve(text))
        if target is not None and not target.npc:
            return self.recruit(player, target)
        if target is not None and target.npc == "maid":
            return self.hire_graduate(player, target)
        if (target is not None and target.npc == "mercenary"
                and not self.repository.is_story(target)):
            return self.hire_mercenary(player, target)
        return [Message(f"Nobody called '{text}' is for hire. [hire] "
                        f"lists your characters, maids and mercenaries.",
                        player.name)]

    def party_blocked(self, player:Player, handle:str) -> list[Message]:
        if self.member(handle):
            return [Message("They are already in the party.", player.name)]
        if len(self.party) >= MAX_PARTY_SIZE:
            return [Message("The party is full.", player.name)]
        return []

    def recruit(self, player:Player, target:Player) -> list[Message]:
        if target.name == player.name:
            return [Message("You can't recruit yourself.", player.name)]
        blocked = self.party_blocked(player, target.name)
        if blocked:
            return blocked
        self.autopilot.add(target.name)
        self.party.append(target)
        return [Message(f"{target.full_name} joins {player.name}'s party "
                        f"as a companion on autopilot "
                        f"({len(self.party)}/{MAX_PARTY_SIZE}).")]

    def hire_graduate(self, player:Player, maid:Player) -> list[Message]:
        blocked = self.party_blocked(player, maid.name)
        if blocked:
            return blocked
        owned = owns_maid(self.repository, player, maid)
        price = 0 if owned else hire_price(maid)
        if player.gold < price:
            return [Message(f"{maid.full_name} wants {price} gold "
                            f"(you have {player.gold}).", player.name)]
        player.gold -= price
        self.repository.save(player)
        self.party.append(maid)
        paid = f"{player.name} pays {price} gold: the" if price else "The"
        return [Message(f"{paid} maid {maid.full_name} (Lv {maid.level}) "
                        f"joins the party as a companion "
                        f"({len(self.party)}/{MAX_PARTY_SIZE}).")]

    def hire_mercenary(self, player:Player, npc:Player) -> list[Message]:
        blocked = self.party_blocked(player, npc.name)
        if blocked:
            return blocked
        price = hire_price(npc)
        if player.gold < price:
            return [Message(f"{npc.full_name} wants {price} gold "
                            f"(you have {player.gold}).", player.name)]
        player.gold -= price
        spend_points(npc)
        self.repository.add(npc)
        self.repository.save(player)
        self.party.append(npc)
        return [Message(f"{player.name} pays {price} gold: {npc.full_name} "
                        f"joins the party "
                        f"({len(self.party)}/{MAX_PARTY_SIZE}).")]

    def roster_lines(self, player:Player) -> list[Message]:
        lines = ["Your characters (free, autopilot):"]
        others = [name for name in self.repository.names()
                  if name != player.name and not self.member(name)]
        lines.append("  " + (", ".join(others) if others else "none"))
        hirable = [npc for npc in self.repository.npc_players()
                   if not self.member(npc.name)]
        own = [npc for npc in hirable if npc.npc == "maid"
               and owns_maid(self.repository, player, npc)]
        mercs = [npc for npc in hirable if npc.npc == "mercenary"]
        graduates = [npc for npc in self.repository.graduates()
                     if not self.member(npc.name)]
        if own:
            lines.append("Your maids (free):")
            lines += [f"  {maid.full_name} (Lv {maid.level})"
                      for maid in own]
        lines.append("Mercenaries for hire ([hire <name>]):")
        lines += ([f"  {merc.full_name} (Lv {merc.level}, "
                   f"{hire_price(merc)} gold) – {merc.profile.get('blurb', '')}"
                   for merc in mercs] or ["  none"])
        if graduates:
            lines.append("Graduates of the Maid School (former adventurers, "
                         "double price):")
            lines += [f"  {grad.full_name} (Lv {grad.level}, "
                      f"{hire_price(grad)} gold)" for grad in graduates]
        return [Message("\n".join(lines), player.name)]

    def dismiss(self, player:Player, text:str) -> list[Message]:
        if self.state != "lobby" or self.member(player.name) is None:
            return [Message("You can only dismiss a companion in the "
                            "lobby.", player.name)]
        handle = self.repository.resolve(text)
        companion = self.member(handle)
        if companion is None or not self.is_auto(companion):
            return [Message("There is no such companion in the party.",
                            player.name)]
        self.party.remove(companion)
        self.autopilot.discard(companion.name)
        self.manual.discard(companion.name)
        return [Message(f"{companion.full_name} leaves the party "
                        f"({len(self.party)}/{MAX_PARTY_SIZE}).")]

    def npc_action(self, npc:Player) -> Action:
        kind, args = autopilot_choice(npc, self.living(), self.enemies)
        action = self.parse_action(npc, kind, args)
        return action if isinstance(action, Action) else Action("hit")
