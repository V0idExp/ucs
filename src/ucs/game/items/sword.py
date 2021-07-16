from ucs.foundation import Action

from . import Item

_SPRITE = (748, 123, 5, 10)


class Sword(Item):

    def __init__(self):
        super().__init__(_SPRITE)

    def use(self) -> Action:
        pass
