from typing import Optional

from ucs.components import CollisionComponent, WalkComponent
from ucs.components.walk import WalkDirection
from ucs.foundation import Action, Actor, Position, Rect
from ucs.game.components import HumanoidComponent
from ucs.input import PLAYER_CONTROLS_MAP, is_key_pressed


class Player(Actor):

    def __init__(self, position: Position, gamepad: int, body_frame: Rect):
        super().__init__(*position)
        self.gamepad = gamepad
        self.humanoid = HumanoidComponent(self, body_frame)
        self.collider = CollisionComponent(self, 16)
        self.walk = WalkComponent(self, 1)

    def tick(self) -> Optional[Action]:
        self._handle_input()
        return None

    def destroy(self) -> None:
        self.humanoid.destroy()
        self.collider.destroy()
        self.walk.destroy()

    def _handle_input(self):
        up, down, left, right = PLAYER_CONTROLS_MAP[self.gamepad]
        if is_key_pressed(up):
            self.walk.direction = WalkDirection.NORTH
        elif is_key_pressed(down):
            self.walk.direction = WalkDirection.SOUTH
        elif is_key_pressed(left):
            self.walk.direction = WalkDirection.WEST
        elif is_key_pressed(right):
            self.walk.direction = WalkDirection.EAST
        else:
            self.walk.direction = WalkDirection.STOP
