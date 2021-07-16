from ucs.foundation import Action

from . import Item

_SPRITE = (652, 74, 16, 16)


class Shield(Item):

    def __init__(self):
        super().__init__(_SPRITE)

    def use(self) -> Action:
        pass
