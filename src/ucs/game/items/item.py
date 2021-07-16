from abc import ABCMeta, abstractmethod
from enum import Enum

from ucs.foundation import Action, Offset, Rect


class BodyPart(Enum):

    LEFT_HAND = 'left_hand'
    RIGHT_HAND = 'right_hand'


class Item(metaclass=ABCMeta):
    """
    Wieldable or equippable game item.
    """

    def __init__(self, image: Rect, equip_part: BodyPart, equip_offset: Offset):
        self.image = image
        self.equip_part = equip_part
        self.equip_offset = equip_offset

    @abstractmethod
    def use(self) -> Action:
        pass
