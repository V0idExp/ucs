from ucs.foundation import Action

from .item import BodyPart, Item

_SPRITE = (748, 123, 5, 10)


class Sword(Item):

    def __init__(self):
        super().__init__(_SPRITE, BodyPart.RIGHT_HAND, (-3, -8))

    def use(self) -> Action:
        pass
