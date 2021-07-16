from ucs.components import SpriteComponent
from ucs.foundation import Actor, Component, Rect
from ucs.game.items import Item


class HumanoidComponent(Component):

    def __init__(self, actor: Actor, body_frame: Rect):
        super().__init__(actor)
        body_w, body_h = body_frame[2:]
        self.body = SpriteComponent(actor, body_frame, (-body_w / 2, -body_h / 2))
        self.right_hand = None
        self.left_hand = None

    def wield_item(self, item: Item) -> bool:
        if self.left_hand is None:
            self.left_hand = (
                SpriteComponent(self.actor, item.image, (0, 3)),
                item)
        elif self.right_hand is None:
            self.right_hand = (
                SpriteComponent(self.actor, item.image, (10, 3)),
                item)
        else:
            print('no free hand for the item!')
            return False

        return True

    def destroy(self) -> None:
        if self.left_hand is not None:
            self.left_hand[0].destroy()

        if self.right_hand is not None:
            self.right_hand[0].destroy()

        self.body.destroy()
