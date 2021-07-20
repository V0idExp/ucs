from ucs.components.sprite import SpriteComponent
from ucs.foundation import Action, Actor, Offset

from .item import BodyPart, Item

_SPRITE = (652, 74, 16, 16)
_OFFSET = (-5, -6)


class Shield(Item):

    def __init__(self):
        super().__init__(_SPRITE, BodyPart.LEFT_HAND)
        self.sprite = None

    def equip(self, actor: Actor, equip_offset: Offset):
        off_x, off_y = equip_offset
        off_x += _OFFSET[0]
        off_y += _OFFSET[1]
        self.sprite = SpriteComponent(actor, _SPRITE, (off_x, off_y))

    def unequip(self):
        self.sprite.destroy()
        self.sprite = None

    def use(self) -> Action:
        return None
