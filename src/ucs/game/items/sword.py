from ucs.anim import AnimationPlayer, VectorPropertyAnimation
from ucs.components.sprite import SpriteComponent
from ucs.foundation import Action, Actor, Offset
from ucs.game.actions import MeleeAttackAction

from .item import BodyPart, Item

_SPRITE = (748, 123, 5, 10)
_OFFSET = (-3, -8)


class Sword(Item):

    def __init__(self):
        super().__init__(_SPRITE, BodyPart.RIGHT_HAND)
        self.sprite = None
        self.equipped_by = None

    def equip(self, actor: Actor, equip_offset: Offset):
        off_x, off_y = equip_offset
        off_x += _OFFSET[0]
        off_y += _OFFSET[1]
        self.sprite = SpriteComponent(actor, _SPRITE, (off_x, off_y))
        self.equipped_by = actor

    def unequip(self):
        self.sprite.destroy()
        self.sprite = None
        self.equipped_by = None

    def use(self) -> Action:
        if self.equipped_by is None:
            return None

        dx, dy = self.sprite.offset
        pre_anim = AnimationPlayer(
            duration=0.075,
            channels=[
                VectorPropertyAnimation(
                    self.sprite,
                    'offset',
                    [
                        (0.0, (dx, dy)),
                        (1.0, (dx, dy - 3)),
                    ]),
                ])

        post_anim = AnimationPlayer(
            duration=0.075,
            channels=[
                VectorPropertyAnimation(
                    self.sprite,
                    'offset',
                    [
                        (0.0, (dx, dy - 3)),
                        (1.0, (dx, dy)),
                    ]),
                ])

        return MeleeAttackAction(self.equipped_by, 3, pre_anim=pre_anim, post_anim=post_anim)
