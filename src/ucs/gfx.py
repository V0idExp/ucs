import pathlib
import struct
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from enum import IntEnum
from typing import ContextManager, List, Mapping

from raylibpy.colors import BLACK, WHITE
from raylibpy.consts import SHADER_UNIFORM_VEC2
from raylibpy.core import Camera2D
from raylibpy.spartan import (Color, Texture2D, begin_drawing, begin_mode2d,
                              begin_shader_mode, clear_background,
                              draw_rectangle_lines, draw_texture_rec,
                              end_drawing, end_mode2d, end_shader_mode,
                              get_shader_location, init_window, load_shader,
                              set_shader_value, set_shader_value_texture)

from ucs.foundation import Position, Rect, Size

_camera: Camera2D = None
_screen_width: int = 0
_screen_height: int = 0


class RenderStage(metaclass=ABCMeta):

    @abstractmethod
    def enter(self):
        pass

    @abstractmethod
    def exit(self):
        pass


class DefaultRenderStage(RenderStage):

    def enter(self):
        begin_mode2d(_camera)

    def exit(self):
        end_mode2d()


class MaskedRenderStage(RenderStage):

    def __init__(self) -> None:
        self.mask_texture: Texture2D = None
        self.tilemap_size: Size = (0, 0)
        self.tile_size: Size = (0, 0)
        self.sprite_size: Size = (0, 0)

        shader_dir = pathlib.Path('assets', 'shaders')
        self.shader = load_shader(
            str(shader_dir.joinpath('mask.vs')),
            str(shader_dir.joinpath('mask.fs')))

        self.mask_texture_loc = get_shader_location(self.shader, "texture1")
        self.sprite_size_loc = get_shader_location(self.shader, "spriteSize")
        self.tilemap_size_loc = get_shader_location(self.shader, "tilemapSize")
        self.tile_size_loc = get_shader_location(self.shader, "tileSize")

    def set_mask_texture(self, texture: Texture2D):
        self.mask_texture = texture

    def set_tilemap_size(self, size: Size):
        self.tilemap_size = size

    def set_tile_size(self, size: Size):
        self.tile_size = size

    def set_sprite_size(self, size: Size):
        self.sprite_size = size
        set_shader_value(
            self.shader,
            self.sprite_size_loc,
            struct.pack('=ff', *self.sprite_size),
            SHADER_UNIFORM_VEC2)

    def enter(self):
        begin_mode2d(_camera)
        begin_shader_mode(self.shader)
        set_shader_value_texture(self.shader, self.mask_texture_loc, self.mask_texture)
        set_shader_value(
            self.shader,
            self.tilemap_size_loc,
            struct.pack('=ff', *self.tilemap_size),
            SHADER_UNIFORM_VEC2)
        set_shader_value(
            self.shader,
            self.tile_size_loc,
            struct.pack('=ff', *self.tile_size),
            SHADER_UNIFORM_VEC2)


    def exit(self):
        end_shader_mode()
        end_mode2d()


class UIRenderStage(RenderStage):

    def enter(self):
        pass

    def exit(self):
        pass


class StageID(IntEnum):

    DEFAULT = 0
    MASKED = 1
    UI = 2

_stages: Mapping[StageID, RenderStage] = None


class DrawCommand(metaclass=ABCMeta):

    order: int
    stage: StageID

    @abstractmethod
    def draw(self):
        pass


DRAW_COMMANDS: List[DrawCommand] = []


class DrawRectOutlineCommand(DrawCommand):

    def __init__(self, order: int, rect: Rect, color: Color) -> None:
        self.order = order
        self.rect = rect
        self.color = color
        self.stage = StageID.DEFAULT

    def draw(self):
        draw_rectangle_lines(*self.rect, self.color)


class DrawTextureRectCommand(DrawCommand):

    def __init__(
            self,
            order: int,
            texture: Texture2D,
            rect: Rect,
            position: Position) -> None:
        self.order = order
        self.texture = texture
        self.position = position
        self.rect = rect
        self.stage = StageID.DEFAULT

    def draw(self):
        draw_texture_rec(self.texture, self.rect, self.position, WHITE)


class DrawMaskedTextureRectCommand(DrawCommand):
    def __init__(
            self,
            order: int,
            texture: Texture2D,
            rect: Rect,
            position: Position) -> None:
        self.order = order
        self.texture = texture
        self.position = position
        self.rect = rect
        self.stage = StageID.MASKED

    def draw(self):
        stage: MaskedRenderStage = _stages[StageID.MASKED]
        stage.set_sprite_size(self.rect[2:])
        draw_texture_rec(self.texture, self.rect, self.position, WHITE)


class RenderContext(List[DrawCommand]):

    pass


def gfx_init(window_title: str, screen_size: Size, scaling_factor: float=1.0):
    """
    Initialize the graphics subsystem.
    """
    global _stages
    global _camera
    global _screen_width
    global _screen_height

    _screen_width, _screen_height = screen_size

    init_window(_screen_width, _screen_height, window_title)

    _camera = Camera2D(zoom=scaling_factor)

    _stages = {
        StageID.DEFAULT: DefaultRenderStage(),
        StageID.MASKED: MaskedRenderStage(),
        StageID.UI: UIRenderStage(),
    }


@contextmanager
def gfx_frame() -> ContextManager[RenderContext]:
    """
    Creates a new frame rendering context, to which draw commands can be added.
    """
    ctx = RenderContext()
    yield ctx

    begin_drawing()
    clear_background(BLACK)

    current_stage_id = None

    for cmd in sorted(ctx, key=lambda c: (c.stage, c.order)):
        if current_stage_id != cmd.stage:
            if current_stage_id is not None:
                _stages[current_stage_id].exit()
            current_stage_id = cmd.stage
            _stages[current_stage_id].enter()

        cmd.draw()

    if current_stage_id is not None:
        _stages[current_stage_id].exit()

    end_drawing()


def gfx_set_map_params(foreground_mask_texture: Texture2D, tile_size: Size, tilemap_size: Size):
    """
    Update the info about the currently active tilemap, needed for rendering
    effects such as background objects masked by foreground and others.
    """
    stage: MaskedRenderStage = _stages[StageID.MASKED]
    stage.set_mask_texture(foreground_mask_texture)
    stage.set_tile_size(tile_size)
    stage.set_tilemap_size(tilemap_size)


def get_camera() -> Camera2D:
    return _camera
