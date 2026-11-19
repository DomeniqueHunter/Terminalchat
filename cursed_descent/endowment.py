import math

from cursed_descent.config import HUNG_GENDERS


HANG_FACTOR = 0.55
MAX_HANG_RATIO = 0.4


def endowment_geometry(body:dict, gender:str, scale:float,
                       limit:float=0.0, hang:float=HANG_FACTOR
                       ) -> dict | None:
    if gender not in HUNG_GENDERS:
        return None
    length = max(3.0, body.get("endowment", 0) * scale * hang)
    if limit:
        length = min(length, limit * MAX_HANG_RATIO)
    return {"length": length,
            "diameter": max(1.6, body.get("girth", 0) / math.pi * scale),
            "ball": max(2.0, body.get("balls", 0) * scale * 0.9),
            "shape": body.get("endowment_shape", "Human")}


def preview_scale(body:dict, width:float, height:float) -> float:
    length = body.get("endowment", 0) + body.get("balls", 0)
    wide = max(body.get("girth", 0) / math.pi, body.get("balls", 0) * 2, 1)
    return max(0.5, min(9.0, (height - 40) / max(length, 1), width / wide))


def preview_caption(body:dict, gender:str) -> str:
    if gender not in HUNG_GENDERS:
        return "No endowment for this gender."
    shape = body.get("endowment_shape", "Human")
    return (f"{body.get('endowment', 0)} cm long, Ø "
            f"{body.get('girth', 0) / math.pi:.1f} cm | balls "
            f"{body.get('balls', 0)} cm | {shape}")
