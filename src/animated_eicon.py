from typing import Any

from PIL import Image as PILImage
from textual.app import ComposeResult
from textual.geometry import Region
from textual.strip import Strip
from textual_image.renderable import Image as AutoRenderable
from textual_image.widget import Image, SixelImage
from textual_image.widget._base import Image as BaseImage
from textual_image.widget.sixel import _ImageSixelImpl, _NoopRenderable

from eicons import Eicon


IDLE_SECONDS = 0.5


class FrameAnimation:

    def setup_animation(self, eicon:Eicon) -> None:
        self.frames = eicon.frames
        self.durations = eicon.durations
        self.frame_index = 0

    def on_mount(self) -> None:
        if len(self.frames) > 1:
            self.set_timer(self.durations[0] / 1000, self.next_frame)

    def animation_enabled(self) -> bool:
        return bool(getattr(self.app, "gif_enabled", True))

    def next_frame(self) -> None:
        if not self.is_attached:
            return
        if not self.animation_enabled():
            if self.frame_index != 0:
                self.frame_index = 0
                self.show_frame(0)
            self.set_timer(IDLE_SECONDS, self.next_frame)
            return
        if not self.is_on_screen:
            self.set_timer(IDLE_SECONDS, self.next_frame)
            return
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.show_frame(self.frame_index)
        self.set_timer(self.durations[self.frame_index] / 1000, self.next_frame)

    def show_frame(self, index:int) -> None:
        raise NotImplementedError


class _FrameSixelImpl(_ImageSixelImpl):

    def __init__(self, frames:list[PILImage.Image]) -> None:
        super().__init__(frames[0], None)
        self.frames = frames
        self.frame_index = 0
        self.frame_cache: dict[int, Any] = {}

    def show(self, index:int) -> None:
        self.frame_index = index
        self.image = self.frames[index]
        self.refresh()

    def render_lines(self, crop:Region) -> list[Strip]:
        self._cached_sixels = self.frame_cache.get(self.frame_index)
        lines = super().render_lines(crop)
        if self._cached_sixels is not None:
            self.frame_cache[self.frame_index] = self._cached_sixels
        return lines


class SixelEicon(FrameAnimation, SixelImage, Renderable=_NoopRenderable):

    def __init__(self, eicon:Eicon) -> None:
        super().__init__(eicon.frames[0])
        self.setup_animation(eicon)
        self.impl: _FrameSixelImpl | None = None

    def compose(self) -> ComposeResult:
        self.impl = _FrameSixelImpl(self.frames)
        yield self.impl

    def show_frame(self, index:int) -> None:
        if self.impl is not None:
            self.impl.show(index)


class GenericEicon(FrameAnimation, BaseImage, Renderable=AutoRenderable):

    def __init__(self, eicon:Eicon) -> None:
        super().__init__(eicon.frames[0])
        self.setup_animation(eicon)

    def show_frame(self, index:int) -> None:
        self.image = self.frames[index]


def make_eicon_widget(eicon:Eicon) -> SixelEicon | GenericEicon:
    if Image is SixelImage:
        return SixelEicon(eicon)
    return GenericEicon(eicon)
