from ucs.components import SpriteComponent
from ucs.foundation import Actor, Component, Rect
from ucs.game.items.item import BodyPart, Item


class HumanoidComponent(Component):

    def __init__(self, actor: Actor, body_frame: Rect):
        super().__init__(actor)
        self.body = SpriteComponent(actor, body_frame)
        self.right_hand = None
        self.left_hand = None

    def equip_item(self, item: Item) -> bool:
        if item.equip_part is BodyPart.RIGHT_HAND:
            item.equip(self.actor, (15, 10))
            self.right_hand = item
        elif item.equip_part is BodyPart.LEFT_HAND:
            item.equip(self.actor, (4, 10))
            self.left_hand = item

    @property
    def primary_item(self) -> Item:
        return self.right_hand

    @property
    def secondary_item(self) -> Item:
        return self.left_hand

    def destroy(self) -> None:
        if self.left_hand is not None:
            self.left_hand.unequip()
            self.left_hand = None

        if self.right_hand is not None:
            self.right_hand.unequip()
            self.right_hand = None

        self.body.destroy()
