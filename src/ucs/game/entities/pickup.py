from typing import Optional, Tuple

from ucs.components import CollisionComponent, SpriteComponent
from ucs.foundation import Action, Actor
from ucs.game.actions import WieldItemAction
from ucs.game.entities import Player
from ucs.game.items.item import Item


class Pickup(Actor):

    def __init__(self, position: Tuple[int, int], item: Item, name: str):
        super().__init__(*position)
        self.item = item
        self.collider = CollisionComponent(self, 16)
        self.sprite = SpriteComponent(self, item.image)
        self.name = name

    def tick(self) -> Optional[Action]:
        if self.collider.collision is not None and isinstance(self.collider.collision, Player):
            self.state = Actor.State.INACTIVE
            target = self.collider.collision
            return WieldItemAction(target.humanoid, self.item, self.name)

        return None

    def destroy(self) -> None:
        self.collider.destroy()
        self.sprite.destroy()
