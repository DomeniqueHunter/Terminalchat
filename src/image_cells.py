import sys

from textual.dom import DOMNode
from textual_image._terminal import CellSize, get_tiocgwinsz, probe_terminal
from textual_image.widget._base import Image as BaseImage
from textual_image.widget.sixel import _ImageSixelImpl


def current_cell_size() -> CellSize:
    return probe_terminal().cell_size


def measure_cell_size() -> CellSize | None:
    if not sys.__stdout__ or not sys.__stdout__.isatty():
        return None
    try:
        rows, columns, width, height = get_tiocgwinsz()
    except OSError:
        return None
    if not rows or not columns or not width or not height:
        return None
    return CellSize(int(width / columns), int(height / rows))


def set_cell_size(cell:CellSize) -> bool:
    capabilities = probe_terminal()
    if capabilities.cell_size == cell:
        return False
    setattr(probe_terminal, "_result", capabilities._replace(cell_size=cell))
    return True


def refresh_images(root:DOMNode) -> int:
    count = 0
    for node in root.walk_children(with_self=True):
        if isinstance(node, (BaseImage, _ImageSixelImpl)):
            node.refresh(layout=True)
            count += 1
    return count


def main() -> None:
    print("current:", current_cell_size(), "measured:", measure_cell_size())


if __name__ == "__main__":
    main()
