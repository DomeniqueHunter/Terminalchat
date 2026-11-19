from typing import Any

from .body import (
    BUILDS, BUTT_DEFAULT, CREATION_LIMITS, ENDOWMENT_SHAPES, GIRTH_RATIO,
    bust_label, body_text, muscle_baseline, normalize_body,
)
from .config import HUNG_GENDERS


KEY_ALIASES = {"cock": "endowment", "penis": "endowment",
               "implants": "fake", "ass": "butt"}
HUNG_KEYS = ("endowment", "girth", "balls", "shape")
NUMERIC_KEYS = ("height", "weight", "bust", "fake", "muscle", "butt",
                "endowment", "girth", "balls")
FIELD_ORDER = ("height", "weight", "build", "bust", "fake", "muscle", "butt",
               "endowment", "girth", "balls", "shape")
FIELD_TEXTS = {
    "height": "Height in cm",
    "weight": "Weight in kg",
    "build": "Build",
    "bust": "Bust size in cc (both breasts together, 0 = flat)",
    "fake": "How much of the bust is implants, in cc (0 = all natural)",
    "muscle": "Musculature (0 = soft, 100 = bodybuilder)",
    "butt": "Butt/hip circumference in cm",
    "endowment": "Cock length in cm",
    "girth": "Cock girth in cm",
    "balls": "Ball diameter in cm",
    "shape": "Cock shape",
}
CHOICES = {"build": BUILDS, "shape": ENDOWMENT_SHAPES}
USAGE = ("Several values at once: 'height 180 bust 400 fake 100 muscle 40 "
         "butt 100 build toned' (keys: height, weight, build, bust, fake, "
         "muscle, butt")
HUNG_USAGE = ", cock, girth, balls, shape"
LATER_NOTE = ("After creation you can only change this at Dr. Vane's clinic "
              "for gold – and there you can grow beyond these limits.")


def fields_for(gender:str) -> list[str]:
    hung = gender in HUNG_GENDERS
    return [key for key in FIELD_ORDER if hung or key not in HUNG_KEYS]


def current_text(body:dict[str, Any], key:str) -> str:
    if key == "fake":
        return f"{body.get('fake', {}).get('bust', 0)} cc"
    if key == "shape":
        return body.get("endowment_shape", "Human")
    if key == "build":
        return body["build"]
    unit = {"height": " cm", "weight": " kg", "bust": " cc", "butt": " cm",
            "endowment": " cm", "girth": " cm", "balls": " cm"}.get(key, "")
    value = body.get(key, 0)
    extra = f" ({bust_label(value)})" if key == "bust" else ""
    return f"{value}{unit}{extra}"


def field_question(body:dict[str, Any], gender:str, index:int,
                   note:str="") -> str:
    fields = fields_for(gender)
    key = fields[index]
    head = f"Step 4/6 – Body, question {index + 1} of {len(fields)}"
    lines = [f"{note}\n" if note else "", head, FIELD_TEXTS[key] + ":"]
    if key in CHOICES:
        lines += [f"  {number}. {name}"
                  for number, name in enumerate(CHOICES[key], start=1)]
    else:
        low, high = CREATION_LIMITS[key]
        lines.append(f"  allowed at start: {low}–{high}")
    lines.append(f"  now: {current_text(body, key)}")
    lines.append("Send a value, 'ok' to keep it, 'back' for the previous "
                 "question or 'rest' to keep everything that is left.")
    if index == 0:
        lines.append(usage_line(gender))
    return "\n".join(line for line in lines if line != "")


def usage_line(gender:str) -> str:
    hung = HUNG_USAGE if gender in HUNG_GENDERS else ""
    return f"{USAGE}{hung}). {LATER_NOTE}"


def review_question(body:dict[str, Any], note:str="") -> str:
    lines = [f"{note}\n" if note else "",
             "Step 4/6 – Body, review:",
             f"  {body_text(body)}",
             "Send 'ok' to continue, 'back' to change the last answer, or "
             "pairs like 'bust 500 muscle 60' to adjust."]
    return "\n".join(line for line in lines if line != "")


def body_question(body:dict[str, Any], gender:str) -> str:
    return field_question(body, gender, 0,
                          f"Your starting body: {body_text(body)}")


def question_at(body:dict[str, Any], gender:str, index:int,
                note:str="") -> str:
    if index >= len(fields_for(gender)):
        return review_question(body, note)
    return field_question(body, gender, index, note)


def answer_field(body:dict[str, Any], gender:str, index:int,
                 text:str) -> tuple[dict[str, Any], int, str]:
    """Returns the new body, the next question index and an error text."""
    fields = fields_for(gender)
    word = text.strip().casefold()
    if word == "back":
        return body, max(0, index - 1), ""
    if word == "rest":
        return body, len(fields), ""
    if index >= len(fields):
        if word in ("ok", "yes", "y"):
            return body, index + 1, ""
    elif word in ("ok", "yes", "y"):
        return body, index + 1, ""
    tokens = text.replace(",", " ").split()
    if len(tokens) > 1 and all(token.isdigit() for token in tokens):
        return body, index, ("Those look like stat points – they come in "
                             "step 4. Right now I need your body.")
    if len(tokens) == 1 and index < len(fields):
        key = fields[index]
        value = tokens[0]
        if key in CHOICES and value.isdigit() \
                and 1 <= int(value) <= len(CHOICES[key]):
            value = CHOICES[key][int(value) - 1]
        result = parse_body_input(f"{key} {value}", body, gender)
        if isinstance(result, str):
            return body, index, result
        return result, index + 1, ""
    result = parse_body_input(text, body, gender)
    if isinstance(result, str):
        return body, index, result
    return result, len(fields), ""


def parse_body_input(text:str, body:dict[str, Any],
                     gender:str) -> dict[str, Any] | str:
    words = text.replace(",", " ").split()
    if not words or len(words) % 2:
        return ("I need pairs of 'key value', e.g. 'height 180 bust 400'.\n"
                + usage_line(gender))
    pairs = {KEY_ALIASES.get(key.casefold(), key.casefold()): value
             for key, value in zip(words[::2], words[1::2])}
    unknown = [key for key in pairs if key not in NUMERIC_KEYS + ("build",
                                                                   "shape")]
    if unknown:
        return (f"I don't know '{unknown[0]}'.\n{usage_line(gender)}")
    if gender not in HUNG_GENDERS:
        hung = [key for key in pairs if key in HUNG_KEYS]
        if hung:
            return f"'{hung[0]}' doesn't apply to this character."
    updated = dict(body)
    updated["fake"] = dict(body.get("fake", {}))
    errors = apply_pairs(updated, pairs)
    if updated["fake"].get("bust", 0) > updated["bust"]:
        errors.append("The implants can't be larger than the whole bust.")
    if errors:
        return "\n".join(errors)
    return normalize_body(updated)


def apply_pairs(body:dict[str, Any], pairs:dict[str, str]) -> list[str]:
    errors: list[str] = []
    if "build" in pairs:
        build = pairs["build"].capitalize()
        if build not in BUILDS:
            errors.append(f"Unknown build '{pairs['build']}' – choose from "
                          f"{', '.join(BUILDS)}.")
        else:
            body["build"] = build
            body["muscle"] = muscle_baseline(build)
            body["butt"] = BUTT_DEFAULT.get(build, 95)
    if "shape" in pairs:
        shape = pairs["shape"].capitalize()
        if shape not in ENDOWMENT_SHAPES:
            errors.append(f"Unknown shape '{pairs['shape']}' – choose from "
                          f"{', '.join(ENDOWMENT_SHAPES)}.")
        else:
            body["endowment_shape"] = shape
    for key in NUMERIC_KEYS:
        if key not in pairs:
            continue
        if not pairs[key].isdigit():
            errors.append(f"{FIELD_TEXTS[key]}: please send a whole number, "
                          f"not '{pairs[key]}'.")
            continue
        value = int(pairs[key])
        low, high = CREATION_LIMITS[key]
        if not low <= value <= high:
            errors.append(f"{FIELD_TEXTS[key]}: {value} is outside the "
                          f"start range {low}–{high}.")
            continue
        if key == "fake":
            body["fake"]["bust"] = value
        else:
            body[key] = value
    if "endowment" in pairs and "girth" not in pairs and not errors:
        body["girth"] = round(body["endowment"] * GIRTH_RATIO)
    return errors
