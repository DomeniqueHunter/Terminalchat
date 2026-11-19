from typing import Any

from ...config import (
    SCENT_COUTURE_BONUS, VELOURS_GROWTH, VELOURS_GROWTH_MAX, VELOURS_PHYSIQUE,
    VELOURS_STAGE_STEP, VELOURS_SWEAT,
)
from ...scent import party_scent
from .content import EVENT_TEXTS


class BoutiqueNpcMixin:
    session: Any
    event: dict[str, Any]

    def velours_growth(self, enemy:Any) -> list[str]:
        stage = self.session.stage
        victims = len(self.session.boutique.entries)
        score = victims + stage // VELOURS_STAGE_STEP
        factor = 1 + min(score * VELOURS_GROWTH, VELOURS_GROWTH_MAX)
        for attribute in ("max_hp", "attack", "defense", "exp"):
            setattr(enemy, attribute,
                    round(getattr(enemy, attribute) * factor))
        enemy.hp = enemy.max_hp
        texts = EVENT_TEXTS["couture"]
        lines = [next((texts[key].format(count=victims)
                       for limit, key in VELOURS_PHYSIQUE if score >= limit),
                      "")]
        lines.append(next((texts[key] for limit, key in VELOURS_SWEAT
                           if stage >= limit), ""))
        scent = party_scent(self.session.party)
        if scent:
            enemy.attack = round(enemy.attack
                                 * (1 + scent * SCENT_COUTURE_BONUS))
            lines.append(texts["scent"])
        return [line for line in lines if line]
