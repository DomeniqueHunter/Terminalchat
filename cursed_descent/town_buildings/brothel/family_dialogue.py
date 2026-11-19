import random


KIN_ACTS = {
    "son": {
        "foot": (
            "{worker} plants her sole on {client}'s face: 'Breathe through "
            "your mother's foot, sweetheart. You wanted this, didn't you?' "
            "{client} whimpers: 'Yes, Mom…'",
            "{worker} presses her toes over {client}'s nose and mouth. "
            "'Mommy decides when you get air.' {client}'s hands tap, "
            "then fall open in surrender.",
        ),
        "facesitting": (
            "{worker} settles over {client}'s face with her whole weight: "
            "'Mom was here first. Now be a good boy and breathe me in.' "
            "{client} answers with a muffled 'Yes, Mom.'",
        ),
        "trampling": (
            "{worker} steps onto {client}'s chest, heel by heel. "
            "'Mommy raised you to hold still, didn't she?' {client} "
            "gasps: 'Yes, Mistress… Mom…'",
        ),
        "any": (
            "{worker} looks down at her son {client} and smiles: 'You can "
            "call me Mom or Mistress. Tonight you may choose, once.'",
        ),
    },
    "daughter": {
        "any": ("{worker} tells her daughter {client}: 'Mommy is strict "
                "because she loves you.' {client} nods, flushed.",),
    },
    "brother": {
        "any": ("{worker}: 'Big brother, little rules.' {client} grins "
                "sheepishly: 'You always won.'",),
    },
    "sister": {
        "any": ("{worker}: 'Little sister, big favour.' {client} laughs "
                "and gives in.",),
    },
    "partner": {
        "any": ("{worker} to {client}: 'You pay now, and at home too.' "
                "{client}: 'Yes, Mistress.'",),
    },
    "mother": {
        "any": ("{worker} to her mother {client}: 'Just this once, "
                "Mother. Do not tell anyone.'",),
    },
    "father": {
        "any": ("{worker} to her father {client}: 'You never listened. "
                "Now you will.'",),
    },
}


def family_line(kin:str, act:str, worker:str, client:str,
                rng:random.Random) -> str:
    table = KIN_ACTS.get(kin)
    if not table:
        return ""
    pool = table.get(act) or table["any"]
    return rng.choice(pool).format(worker=worker, client=client)
