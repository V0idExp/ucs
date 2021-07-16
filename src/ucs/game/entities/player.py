from ucs.foundation import Action, Actor, Rect, Position
from ucs.input import is_key_pressed, PLAYER_CONTROLS_MAP
from typing import Optional

from ucs.game.components import HumanoidComponent
from ucs.components import CollisionComponent, MovementComponent


class Player(Actor):

    def __init__(self, position: Position, gamepad: int, body_frame: Rect):
        super().__init__(*position)
        self.gamepad = gamepad
        self.humanoid = HumanoidComponent(self, body_frame)
        self.collider = CollisionComponent(self, 16)
        self.movement = MovementComponent(self, (-8, 0, 16, 8))

    def tick(self) -> Optional[Action]:
        self._handle_input()
        return None

    def destroy(self) -> None:
        self.humanoid.destroy()
        self.collider.destroy()
        self.movement.destroy()

    def _handle_input(self):
        vel_x, vel_y = 0, 0
        up, down, left, right = PLAYER_CONTROLS_MAP[self.gamepad]
        if is_key_pressed(up):
            vel_y -= 1
        if is_key_pressed(down):
            vel_y += 1
        if is_key_pressed(left):
            vel_x -= 1
        if is_key_pressed(right):
            vel_x += 1

        self.movement.vel_x = vel_x
        self.movement.vel_y = vel_y
