from ucs.components import SpriteComponent
from ucs.foundation import Actor, Component, Rect
from ucs.game.items import Item
from ucs.game.items.item import BodyPart


class HumanoidComponent(Component):

    def __init__(self, actor: Actor, body_frame: Rect):
        super().__init__(actor)
        self.body = SpriteComponent(actor, body_frame)
        self.right_hand = None
        self.left_hand = None

    def wield_item(self, item: Item) -> bool:
        off_x, off_y = item.equip_offset
        if item.equip_part is BodyPart.RIGHT_HAND:
            off_x += 15
            off_y += 10
            self.right_hand = SpriteComponent(self.actor, item.image, (off_x, off_y))
        elif item.equip_part is BodyPart.LEFT_HAND:
            off_x += 4
            off_y += 10
            self.left_hand = SpriteComponent(self.actor, item.image, (off_x, off_y))

    @property
    def has_weapon(self) -> bool:
        return self.right_hand is not None

    def destroy(self) -> None:
        if self.left_hand is not None:
            self.left_hand.destroy()

        if self.right_hand is not None:
            self.right_hand.destroy()

        self.body.destroy()
