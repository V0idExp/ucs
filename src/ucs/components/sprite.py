import pathlib
from typing import Optional, Tuple, List

from raylibpy.spartan import Texture2D, load_texture
from ucs.gfx import DrawMaskedTextureRectCommand, RenderContext
from ucs.foundation import Actor, Component, Rect, Pos


class SpriteComponent(Component):
    frame: Optional[Rect]
    offset: Tuple[int, int]

    def __init__(self, actor: Actor, frame: Optional[Rect]=None, offset: Pos=(0, 0)) -> None:
        super().__init__(actor)
        self.frame = frame
        self.offset = offset
        _sprite_components.append(self)

    def destroy(self) -> None:
        _sprite_components.remove(self)


_sprite_components: List[SpriteComponent] = []
_sheet: Texture2D = None


def sprite_init():
    global _sheet
    _sheet = load_texture(str(pathlib.Path('assets', 'characters_sheet.png')))


def sprite_update(ctx: RenderContext):
    for sprite in _sprite_components:
        if sprite.actor.state is Actor.State.INACTIVE:
            continue
        off_x, off_y = sprite.offset
        position = sprite.actor.x + off_x, sprite.actor.y + off_y
        ctx.append(DrawMaskedTextureRectCommand(1e6, _sheet, sprite.frame, position))
