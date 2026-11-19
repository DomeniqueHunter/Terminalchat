from ...body import bust_label
from ...config import HUNG_GENDERS, VAGINA_GENDERS
from ...models import Player


def bmi(body:dict) -> float:
    return body["weight"] / (body["height"] / 100) ** 2


def height_word(height:int) -> str:
    for limit, word in ((155, "petite"), (170, "compact"), (185, "tall"),
                        (200, "towering")):
        if height < limit:
            return word
    return "giant"


def weight_word(value:float) -> str:
    for limit, word in ((19, "light"), (25, "lean"), (30, "solid")):
        if value < limit:
            return word
    return "heavy"


def butt_word(butt:int) -> str:
    for limit, word in ((85, "tight"), (100, "round"), (115, "full")):
        if butt < limit:
            return f"{word} backside"
    return "huge, heavy backside"


def cock_word(body:dict) -> str:
    length = body.get("endowment", 0)
    girth = body.get("girth", 0)
    size = ("small" if length < 10 else "average" if length < 16 else
            "long" if length < 22 else "monstrous")
    thick = "thick " if girth >= 14 else ""
    shape = body.get("endowment_shape", "Human").lower()
    return f"{size}, {thick}{shape} cock ({length} cm)"


def balls_word(balls:float) -> str:
    return ("small" if balls < 4 else "full" if balls < 7 else
            "heavy" if balls < 10 else "massive") + " balls"


def flow_word(body:dict, hung:bool) -> str:
    height = body["height"]
    weight = body["weight"]
    length = body.get("endowment", 0) if hung else 0
    if height >= 200 or weight >= 130 or length >= 30:
        return "a roaring flood that goes on and on"
    if height >= 185 or weight >= 100 or length >= 22:
        return "a thick, hissing torrent like a shower"
    if height >= 170 or weight >= 75:
        return "a heavy, steady stream"
    return "a warm, steady stream"


def anatomy(player:Player) -> dict[str, object]:
    body = player.body
    height = body["height"]
    ratio = bmi(body)
    cc = body.get("bust", 0)
    butt = body.get("butt", 95)
    foot_cm = round(height * 0.155)
    hung = player.gender in HUNG_GENDERS
    tags = {"bust": cc >= 150, "bigbust": cc >= 500, "cock": hung, "vagina": player.gender in VAGINA_GENDERS,
            "bigcock": hung and body.get("endowment", 0) >= 20,
            "butt": butt >= 105, "tall": height >= 185,
            "small": height < 160, "heavy": ratio >= 27,
            "muscle": body.get("muscle", 0) >= 50,
            "big": flow_word(body, hung).startswith(("a thick", "a roaring")),
            "giant": flow_word(body, hung).startswith("a roaring")}
    words = {
        "height_word": height_word(height),
        "weight_word": weight_word(ratio),
        "build": str(body["build"]).lower(),
        "bust": f"{bust_label(cc).lower()} breasts" if cc > 0
        else "flat chest",
        "butt": butt_word(butt),
        "cock": cock_word(body) if hung else "",
        "balls": balls_word(body.get("balls", 5)) if hung else "",
        "feet": f"size {round((foot_cm + 1.5) * 1.5)} feet",
        "legs": "long legs" if height >= 175 else "legs",
        "client_thighs": "thighs",
        "flow": flow_word(body, hung),
        "flow_cap": flow_word(body, hung).capitalize(),
    }
    return {"tags": tags, "words": words}
