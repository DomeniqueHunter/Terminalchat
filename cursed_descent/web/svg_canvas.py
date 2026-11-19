from typing import Any
from xml.sax.saxutils import escape


POINT_PX = 4 / 3


def paint(value:str, default:str="none") -> str:
    return value or default


class SvgCanvas:
    def __init__(self, width:int, height:int) -> None:
        self.width = width
        self.height = height
        self.parts: list[str] = []

    def delete(self, _tag:str="all") -> None:
        self.parts = []

    def create_line(self, x1:float, y1:float, x2:float, y2:float,
                    width:float=1, fill:str="black",
                    capstyle:str="butt") -> None:
        self.parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{fill}" stroke-width="{width:.1f}" '
            f'stroke-linecap="{capstyle}"/>')

    def create_oval(self, x1:float, y1:float, x2:float, y2:float,
                    fill:str="", outline:str="black") -> None:
        self.parts.append(
            f'<ellipse cx="{(x1 + x2) / 2:.1f}" cy="{(y1 + y2) / 2:.1f}" '
            f'rx="{abs(x2 - x1) / 2:.1f}" ry="{abs(y2 - y1) / 2:.1f}" '
            f'fill="{paint(fill)}" stroke="{paint(outline)}"/>')

    def create_rectangle(self, x1:float, y1:float, x2:float, y2:float,
                         fill:str="", outline:str="black") -> None:
        self.parts.append(
            f'<rect x="{min(x1, x2):.1f}" y="{min(y1, y2):.1f}" '
            f'width="{abs(x2 - x1):.1f}" height="{abs(y2 - y1):.1f}" '
            f'fill="{paint(fill)}" stroke="{paint(outline)}"/>')

    def create_polygon(self, *coords:Any, fill:str="",
                       outline:str="black", width:float=1,
                       smooth:bool=False) -> None:
        if len(coords) == 1:
            coords = tuple(coords[0])
        points = list(zip(coords[::2], coords[1::2]))
        stroke = (f'stroke="{paint(outline)}" stroke-width="{width}" '
                  f'stroke-linejoin="round"')
        if not smooth:
            text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
            self.parts.append(f'<polygon points="{text}" '
                              f'fill="{paint(fill)}" {stroke}/>')
            return
        self.parts.append(f'<path d="{smooth_path(points)}" '
                          f'fill="{paint(fill)}" {stroke}/>')

    def create_text(self, x:float, y:float, text:str="", anchor:str="center",
                    fill:str="black", font:tuple[Any, ...]=("", 8)) -> None:
        size = font[1] * POINT_PX
        weight = "bold" if "bold" in font[2:] else "normal"
        align = "start" if anchor == "nw" else "middle"
        baseline = "hanging" if anchor == "nw" else "central"
        self.parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" '
            f'font-size="{size:.1f}" font-weight="{weight}" '
            f'text-anchor="{align}" dominant-baseline="{baseline}">'
            f'{escape(text)}</text>')

    def svg(self) -> str:
        return (f'<svg class="figure" viewBox="0 0 {self.width} '
                f'{self.height}" width="{self.width}" '
                f'height="{self.height}" role="img" '
                f'xmlns="http://www.w3.org/2000/svg">'
                + "".join(self.parts) + "</svg>")


def smooth_path(points:list[tuple[float, float]]) -> str:
    count = len(points)
    middles = [((points[i][0] + points[(i + 1) % count][0]) / 2,
                (points[i][1] + points[(i + 1) % count][1]) / 2)
               for i in range(count)]
    path = f"M{middles[-1][0]:.1f},{middles[-1][1]:.1f}"
    for index, (x, y) in enumerate(points):
        mx, my = middles[index]
        path += f" Q{x:.1f},{y:.1f} {mx:.1f},{my:.1f}"
    return path + " Z"
