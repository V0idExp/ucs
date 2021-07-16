from abc import ABCMeta, abstractmethod

from ucs.foundation import Action, Rect


class Item(metaclass=ABCMeta):
    """
    Wieldable or equippable game item.
    """

    def __init__(self, image: Rect):
        self.image = image

    @abstractmethod
    def use(self) -> Action:
        pass
