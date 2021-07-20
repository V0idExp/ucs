from abc import ABCMeta, abstractmethod
from enum import Enum

from ucs.foundation import Action, Offset, Rect, Actor


class BodyPart(Enum):

    LEFT_HAND = 'left_hand'
    RIGHT_HAND = 'right_hand'


class Item(metaclass=ABCMeta):
    """
    Wieldable or equippable game item.
    """

    def __init__(self, image: Rect, equip_part: BodyPart):
        self.image = image
        self.equip_part = equip_part

    @abstractmethod
    def equip(self, actor: Actor, equip_offset: Offset):
        """
        Equip the item on the given actor.
        """

    @abstractmethod
    def unequip(self):
        """
        Remove the item from currently equipped actor.
        """

    @abstractmethod
    def use(self) -> Action:
        """
        Use the item.
        """
