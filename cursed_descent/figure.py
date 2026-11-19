from typing import Any

from .config import DEFAULT_GENDER, PRONOUNS
from .models import Player
from .endowment import endowment_geometry


WIDTH = 120
HEIGHT = 222
GROUND = 196
SKIN = "#eebb99"
OUTLINE = "#5a4030"
HAIR = "#7a4a2a"
OUTFIT = "#7a3e9d"
LEATHER = "#3a2a2a"
BUILD_SHAPES = {
    "Thin": (0.80, 0.75, 0.80),
    "Slim": (0.90, 0.85, 0.90),
    "Average": (1.00, 1.00, 1.00),
    "Toned": (1.05, 0.95, 1.00),
    "Muscular": (1.30, 1.05, 1.00),
    "Curvy": (0.95, 0.90, 1.30),
    "Chubby": (1.10, 1.35, 1.30),
    "Heavy": (1.25, 1.60, 1.45),
}
BUST_RADIUS = {"None": 0, "Flat": 0, "Small": 4, "Medium": 6, "Large": 8,
               "Huge": 11, "Massive": 15}
FLESH = "#e0a088"
BUFF_NOTES = {"balls": "enormous balls", "penis": "monstrous endowment"}
ENHANCEMENT_NOTES = {"balls": "heavy low-hangers",
                     "endowment": "impressive endowment"}


def draw_endowment(canvas:Any, x:float, y:float,
                   geo:dict) -> None:
    length, width, ball = geo["length"], geo["diameter"], geo["ball"]
    shape = geo["shape"]
    for side in (-1, 1):
        bx = x + side * ball * 0.5
        canvas.create_oval(bx - ball / 2, y + length * 0.2,
                           bx + ball / 2, y + length * 0.2 + ball,
                           fill=FLESH, outline=OUTLINE)
    tip = y + length
    canvas.create_rectangle(x - width / 2, y, x + width / 2, tip,
                            fill=FLESH, outline=OUTLINE)
    if shape == "Equine":
        canvas.create_oval(x - width * 0.85, tip - width * 0.4,
                           x + width * 0.85, tip + width * 0.5,
                           fill=FLESH, outline=OUTLINE)
    elif shape == "Canine":
        knot = y + length * 0.3
        canvas.create_oval(x - width * 0.95, knot - width * 0.6,
                           x + width * 0.95, knot + width * 0.6,
                           fill=FLESH, outline=OUTLINE)
        canvas.create_polygon(x - width / 2, tip, x + width / 2, tip, x,
                              tip + width * 0.9, fill=FLESH, outline=OUTLINE)
    elif shape == "Draconic":
        for step in range(1, 5):
            ridge = y + length * step / 5
            canvas.create_line(x - width * 0.7, ridge, x + width * 0.7,
                               ridge, fill=OUTLINE)
        canvas.create_polygon(x - width / 2, tip, x + width / 2, tip, x,
                              tip + width * 1.2, fill=FLESH, outline=OUTLINE)
    else:
        canvas.create_oval(x - width / 2, tip - width * 0.4,
                           x + width / 2, tip + width * 0.6,
                           fill=FLESH, outline=OUTLINE)


def bulge_box(geo:dict) -> tuple[float, float]:
    width = max(geo["diameter"] * 1.6, geo["ball"] * 2.2)
    return width, min(geo["length"] * 0.7, width * 2.2)


def draw_bulge(canvas:Any, x:float, y:float, geo:dict) -> None:
    width, height = bulge_box(geo)
    canvas.create_oval(x - width / 2, y, x + width / 2, y + height,
                       fill=OUTFIT, outline=OUTLINE)


def figure_height(height:int) -> float:
    return max(70.0, min(185.0, 150 * height / 170))


def draw_hair(canvas:Any, cx:float, top:float, radius:float,
              size:float) -> None:
    canvas.create_oval(cx - radius * 1.25, top - radius * 0.2,
                       cx + radius * 1.25, top + radius * 2 + size * 0.12,
                       fill=HAIR, outline="")


def torso_points(cx:float, rows:dict[str, float],
                 widths:dict[str, float]) -> list[float]:
    return [
        cx - widths["shoulder"], rows["shoulder"],
        cx + widths["shoulder"], rows["shoulder"],
        cx + widths["waist"], rows["waist"],
        cx + widths["hip"], rows["hip"],
        cx + widths["hip"] * 0.9, rows["crotch"],
        cx - widths["hip"] * 0.9, rows["crotch"],
        cx - widths["hip"], rows["hip"],
        cx - widths["waist"], rows["waist"],
    ]


def draw_limbs(canvas:Any, cx:float, rows:dict[str, float],
               widths:dict[str, float], player:Player) -> None:
    leg = max(4.0, widths["hip"] * 0.75)
    arm = max(3.0, widths["shoulder"] * 0.35)
    for side in (-1, 1):
        hip_x = cx + side * widths["hip"] * 0.5
        foot_x = cx + side * widths["hip"] * 0.45
        canvas.create_line(hip_x, rows["crotch"] - 2, foot_x, GROUND,
                           width=leg, fill=SKIN, capstyle="round")
        if player.equipment.get("feet"):
            boot_top = GROUND - (GROUND - rows["crotch"]) * 0.35
            canvas.create_line(foot_x, boot_top, foot_x, GROUND,
                               width=leg + 1, fill=LEATHER, capstyle="round")
        shoulder_x = cx + side * widths["shoulder"]
        hand_x = shoulder_x + side * 6
        canvas.create_line(shoulder_x, rows["shoulder"] + 3, hand_x,
                           rows["hip"] + 6, width=arm, fill=SKIN,
                           capstyle="round")
        if player.equipment.get("gloves"):
            canvas.create_oval(hand_x - arm * 0.7, rows["hip"] + 6 - arm * 0.7,
                               hand_x + arm * 0.7, rows["hip"] + 6 + arm * 0.7,
                               fill=LEATHER, outline="")
    if player.equipment.get("weapon"):
        hand_x = cx + widths["shoulder"] + 6
        canvas.create_line(hand_x, rows["hip"] + 10, hand_x + 14,
                           rows["shoulder"] - 10, width=3, fill="#888888")


def draw_bust(canvas:Any, cx:float, rows:dict[str, float],
              size:float, player:Player, color:str) -> None:
    radius = BUST_RADIUS.get(player.body["breasts"], 0) * size / 150
    radius += max(0, player.buffs.count("breasts") - 1) * 4
    if radius <= 0:
        return
    y = rows["shoulder"] + size * 0.09
    for side in (-1, 1):
        x = cx + side * radius * 0.85
        canvas.create_oval(x - radius, y - radius * 0.8, x + radius,
                           y + radius * 1.1, fill=color, outline=OUTLINE)


def draw_figure(canvas:Any, player:Player, size:float | None=None,
                cx:float=WIDTH / 2, width:float=WIDTH,
                labels:bool=True) -> None:
    if labels:
        canvas.delete("all")
    size = figure_height(player.body["height"]) if size is None else size
    top = GROUND - size
    radius = size * 0.065
    shoulder, waist, hip = BUILD_SHAPES.get(player.body["build"],
                                            BUILD_SHAPES["Average"])
    if "butt" in player.buffs:
        hip *= 1.6
    elif "butt" in player.enhancements:
        hip *= 1.3
    rows = {"shoulder": top + radius * 2 + size * 0.04,
            "waist": top + size * 0.40, "hip": top + size * 0.50,
            "crotch": top + size * 0.54}
    widths = {"shoulder": size * 0.13 * shoulder,
              "waist": size * 0.085 * waist, "hip": size * 0.115 * hip}
    glow = "#d02020" if "strength" in player.buffs else OUTLINE
    she = PRONOUNS.get(player.gender, PRONOUNS[DEFAULT_GENDER])[0] == "she"
    canvas.create_line(cx - width / 2 + 4, GROUND, cx + width / 2 - 4, GROUND,
                       fill="#bbbbbb")
    if she:
        draw_hair(canvas, cx, top, radius, size)
    draw_limbs(canvas, cx, rows, widths, player)
    torso_color = OUTFIT if player.equipment.get("chest") else SKIN
    canvas.create_polygon(torso_points(cx, rows, widths), fill=torso_color,
                          outline=glow, width=2 if glow != OUTLINE else 1,
                          smooth=True)
    if player.equipment.get("lingerie") and not player.equipment.get("chest"):
        canvas.create_line(cx - widths["hip"] * 0.9, rows["crotch"] - 3,
                           cx + widths["hip"] * 0.9, rows["crotch"] - 3,
                           width=4, fill="#222222")
    if player.pregnant:
        belly = size * 0.09
        by = (rows["waist"] + rows["hip"]) / 2
        canvas.create_oval(cx - belly, by - belly, cx + belly, by + belly,
                           fill=torso_color, outline=OUTLINE)
    geo = endowment_geometry(player.body, player.gender,
                             size / max(player.body["height"], 1), size)
    if geo and player.equipment.get("crotch"):
        draw_bulge(canvas, cx, rows["crotch"] - 2, geo)
    elif geo:
        draw_endowment(canvas, cx, rows["crotch"] - 2, geo)
    bust_color = OUTFIT if player.equipment.get("chest") else SKIN
    if player.equipment.get("lingerie") and not player.equipment.get("chest"):
        bust_color = "#222222"
    draw_bust(canvas, cx, rows, size, player, bust_color)
    canvas.create_rectangle(cx - radius * 0.4, top + radius * 1.8,
                            cx + radius * 0.4, rows["shoulder"] + 1,
                            fill=SKIN, outline="")
    canvas.create_oval(cx - radius, top, cx + radius, top + radius * 2,
                       fill=SKIN, outline=glow)
    if player.equipment.get("head"):
        canvas.create_rectangle(cx - radius * 1.2, top - radius * 0.5,
                                cx + radius * 1.2, top + radius * 0.5,
                                fill=LEATHER, outline="")
    notes = [BUFF_NOTES[buff] for buff in player.buffs if buff in BUFF_NOTES]
    notes += [ENHANCEMENT_NOTES[key] for key in player.enhancements
              if key in ENHANCEMENT_NOTES]
    if not labels:
        return
    canvas.create_text(4, 4, text=f"{player.body['height']} cm",
                       anchor="nw", fill="#777777", font=("TkDefaultFont", 7))
    for index, note in enumerate(notes):
        canvas.create_text(cx, GROUND + 9 + index * 11, text=f"✨ {note}",
                           fill="#9a6700", font=("TkDefaultFont", 7, "bold"))
