import random
from types import SimpleNamespace
from typing import Any

from ...body import fake_amount
from ...config import (
    DEFAULT_GENDER, FISHER_BAIT_LOST, FISHER_BAIT_CAUGHT, FISHER_BITE_HURT,
    FISHER_BOOT_CHANCE, FISHER_BITE_CHANCE, FISHER_CAST_LIMIT,
    FISHER_FISH_ODDS, FISHER_ROD_PRICE, GORM_BALLS, GORM_BUTT,
    GORM_CONCEPTION_FACTOR, GORM_TALL,
    HUNG_GENDERS, PRONOUNS,
)
from ...content import BUFFS
from ...dungeon import give_item
from ...formulas import apply_buff, max_hp, set_bonus_text
from ...intimacy import conception
from ...models import Message, Player
from .content import (
    FISH_BY_RARITY, GORM_ID, GORM_NAME, LIE_AFTER, LIE_CLIMAX_DOM,
    LIE_CLIMAX_GORM, LIE_SCENE_DOM, LIE_SCENE_GORM, VENUE_TEXTS,
)


FAKE_PARTS = ("bust", "butt", "endowment", "balls")


def values_of(player:Player) -> dict[str, str]:
    they, them, their = PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])
    return {"name": player.name, "they": they, "them": them, "their": their}


def fake_parts(player:Player) -> list[str]:
    body = player.body
    return [part for part in FAKE_PARTS
            if body.get(part, 0) > 0
            and fake_amount(body, part) / body[part] > 0.5]


def gorm_taste(player:Player) -> int:
    body = player.body
    score = 0
    score += body.get("height", 0) >= GORM_TALL
    score += body.get("butt", 0) >= GORM_BUTT
    score += (player.gender in HUNG_GENDERS
              and body.get("balls", 0) >= GORM_BALLS)
    score += not fake_parts(player)
    return int(score)


def taste_tier(score:int) -> int:
    if score >= 4:
        return 3
    if score >= 3:
        return 2
    return 1 if score >= 2 else 0


def roll_fish() -> str:
    rarities = list(FISHER_FISH_ODDS)
    weights = [FISHER_FISH_ODDS[rarity] for rarity in rarities]
    rarity = random.choices(rarities, weights=weights)[0]
    return random.choice(FISH_BY_RARITY[rarity])


def hook_names(remains:Any, run_id:str) -> list[str]:
    names = [entry["name"] for entry in remains.entries
             if entry["fate"] in ("fished", "fish_food")
             and entry["run"] != run_id]
    return names[-4:]


class FisherMixin:
    session: Any
    event: dict[str, Any]

    def casts(self) -> dict[str, int]:
        return self.event["data"].setdefault("casts", {})

    def offer_fisher(self) -> list[str]:
        texts = VENUE_TEXTS["fisher"]
        self.event["data"]["inside"] = False
        return ["", texts["intro"], texts["door"], self.options_line(texts)]

    def enter_fisher(self) -> list[Message]:
        texts = VENUE_TEXTS["fisher"]
        self.event["data"]["inside"] = True
        return self.continue_venue([texts["enter"]]
                                   + self.fisher_hook_lines())

    def fisher_hook_lines(self) -> list[str]:
        texts = VENUE_TEXTS["fisher"]
        names = hook_names(self.session.remains, self.session.run_id)
        if not names:
            return [texts["no_hooks"]]
        return [texts["hooks"].format(names=", ".join(names))]

    def fisher_options(self) -> list[str]:
        living = self.session.living()
        options = ["cast"]
        if "bait" not in self.event["used"]:
            options += [f"bait {member.name}" for member in living]
        if any(f"lie:{member.name}" not in self.event["used"]
               for member in living):
            options.append("lie")
        return options + ["depart"]

    def fisher_examine(self) -> list[Message]:
        texts = VENUE_TEXTS["fisher"]
        if self.outside():
            return [Message(texts["look_outside"])]
        return [Message("\n".join([texts["look_inside"]]
                                  + self.fisher_hook_lines()))]

    def fisher_action(self, player:Player, command:str,
                      now:float) -> list[Message] | None:
        word = command.split()[0]
        if word == "cast":
            return self.fisher_cast(player)
        if word == "bait":
            return self.fisher_bait(player, command.partition(" ")[2], now)
        if word == "lie":
            return self.fisher_lie(player)
        return None

    def fisher_cast(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["fisher"]
        values = {"name": player.name, "price": FISHER_ROD_PRICE,
                  "gold": player.gold}
        casts = self.casts()
        if casts.get(player.name, 0) >= FISHER_CAST_LIMIT:
            return [Message(texts["cast_limit"].format(**values),
                            player.name)]
        if player.gold < FISHER_ROD_PRICE:
            return [Message(texts["cast_poor"].format(**values),
                            player.name)]
        player.gold -= FISHER_ROD_PRICE
        casts[player.name] = casts.get(player.name, 0) + 1
        lines = [texts["cast_start"].format(**values)]
        roll = random.random()
        if roll < FISHER_BOOT_CHANCE:
            lines.append(texts["boot"].format(**values))
        elif roll < FISHER_BOOT_CHANCE + FISHER_BITE_CHANCE:
            hp = max(1, round(max_hp(player) * FISHER_BITE_HURT))
            player.hp = max(1, player.hp - hp)
            lines.append(texts["bite"].format(hp=hp, **values))
        elif len(player.inventory) >= player.bag_size:
            lines.append(texts["cast_full"].format(**values))
        else:
            lines.append(give_item(player, roll_fish()))
        self.session.repository.save(player)
        return self.continue_venue(lines)

    def fisher_target(self, name:str) -> Player | None:
        wanted = name.strip().casefold()
        for member in self.session.living():
            if member.name.casefold() == wanted:
                return member
        return None

    def fisher_bait(self, player:Player, name:str,
                    now:float) -> list[Message]:
        texts = VENUE_TEXTS["fisher"]
        target = self.fisher_target(name) if name else player
        if target is None:
            return [Message(texts["bait_unknown"], player.name)]
        values = values_of(target)
        if "bait" in self.event["used"]:
            return [Message(texts["bait_gone"], player.name)]
        if self.event["data"].get("confirm") != target.name:
            self.event["data"]["confirm"] = target.name
            return [Message(texts["bait_confirm"].format(**values),
                            player.name)]
        self.event["used"].add("bait")
        roll = random.random()
        lines = [texts["bait_start"].format(**values)]
        if roll < FISHER_BAIT_LOST:
            return self.fisher_kill(target, "fished", lines, now)
        if roll < FISHER_BAIT_LOST + FISHER_BAIT_CAUGHT:
            return self.fisher_kill(target, "fish_food",
                                    lines + [texts["bait_caught"]], now,
                                    catch=True)
        apply_buff(target, "fish_survivor")
        lines.append(texts["bait_survive"].format(**values))
        lines.append(texts["bait_survive_line"].format(
            name=target.name,
            bonus=set_bonus_text(BUFFS["fish_survivor"])))
        self.session.repository.save(target)
        return self.continue_venue(lines)

    def fisher_kill(self, target:Player, fate:str, lines:list[str],
                    now:float, catch:bool=False) -> list[Message]:
        from ...combat import fate_text
        session = self.session
        text = fate_text(target, fate, None)
        lines += session.kill_outside(target, fate, text, "<<npc.old_gorm_first>>'s giant fish",
                                      "fish")
        living = session.living()
        if catch and living:
            lines.append(VENUE_TEXTS["fisher"]["bait_catch_line"])
            for member in living:
                lines.append(give_item(member, "giant_catch"))
                session.repository.save(member)
        if not living:
            self.reset()
            return [Message("\n".join(lines + session.end_run()))]
        self.save_party()
        return self.continue_venue(lines)

    def fisher_lie(self, player:Player) -> list[Message]:
        texts = VENUE_TEXTS["fisher"]
        key = f"lie:{player.name}"
        if key in self.event["used"]:
            return [Message(texts["lie_limit"].format(name=player.name),
                            player.name)]
        self.event["used"].add(key)
        values = values_of(player)
        dom = player.profile.get("prefs", {}).get("role") == "dom"
        scene = LIE_SCENE_DOM if dom else LIE_SCENE_GORM
        climax = LIE_CLIMAX_DOM if dom else LIE_CLIMAX_GORM
        lines = [random.choice(texts["lie_intro"]).format(**values),
                 texts["lie_dom" if dom else "lie_gorm"].format(**values),
                 random.choice(scene).format(**values),
                 random.choice(climax).format(**values)]
        score = gorm_taste(player)
        tier = taste_tier(score)
        lines.append(texts["lie_taste"][tier])
        for part in fake_parts(player):
            lines.append(texts["fake"][part].format(**values))
        fish_rarity = ("common", "rare", "rare", "epic")[tier]
        fish = random.choice(FISH_BY_RARITY[fish_rarity])
        lines.append(random.choice(LIE_AFTER).format(**values))
        lines.append(give_item(player, fish))
        gorm = SimpleNamespace(gender="Male", name=GORM_NAME, id=GORM_ID)
        lines += conception(gorm, player, random, GORM_CONCEPTION_FACTOR)
        self.session.repository.save(player)
        return self.continue_venue(lines)
