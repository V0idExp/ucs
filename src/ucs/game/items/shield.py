from ucs.foundation import Action

from .item import Item, BodyPart

_SPRITE = (652, 74, 16, 16)


class Shield(Item):

    def __init__(self):
        super().__init__(_SPRITE, BodyPart.LEFT_HAND, (-5, -6))

    def use(self) -> Action:
        pass
