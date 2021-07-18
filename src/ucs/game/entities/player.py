from typing import Optional

from ucs.components import CollisionComponent, WalkComponent
from ucs.components.walk import WalkDirection
from ucs.foundation import Action, Actor, Position, Rect
from ucs.game.actions import MeleeAttackAction
from ucs.game.components import HumanoidComponent
from ucs.game.config import PLAYER_CONTROLS_MAP
from ucs.input import is_key_pressed, is_key_released
from ucs.gfx import get_camera


class Player(Actor):

    def __init__(self, position: Position, gamepad: int, body_frame: Rect):
        super().__init__(*position)
        self.gamepad = gamepad
        self.humanoid = HumanoidComponent(self, body_frame)
        self.collider = CollisionComponent(self, 16)
        self.walk = WalkComponent(self, 1)
        self.attack = None

    def tick(self) -> Optional[Action]:
        get_camera().target = self.position

        self._handle_input()
        return self.attack

    def destroy(self) -> None:
        self.humanoid.destroy()
        self.collider.destroy()
        self.walk.destroy()

    def _handle_input(self):
        up, down, left, right, primary, _ = PLAYER_CONTROLS_MAP[self.gamepad]
        self.walk.direction = WalkDirection.STOP

        if is_key_pressed(up):
            self.walk.direction = WalkDirection.NORTH
        elif is_key_pressed(down):
            self.walk.direction = WalkDirection.SOUTH
        elif is_key_pressed(left):
            self.walk.direction = WalkDirection.WEST
        elif is_key_pressed(right):
            self.walk.direction = WalkDirection.EAST

        if is_key_released(primary) and self.humanoid.has_weapon:
            self.attack = MeleeAttackAction(self.humanoid.right_hand)
