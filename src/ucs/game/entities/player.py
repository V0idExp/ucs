from typing import Optional

from ucs.components import CollisionComponent, WalkComponent
from ucs.components.walk import WalkDirection
from ucs.foundation import Action, Actor, Position, Rect
from ucs.game.actions import WalkAction
from ucs.game.components import HumanoidComponent
from ucs.game.config import PLAYER_CONTROLS_MAP
from ucs.gfx import get_camera
from raylibpy.spartan import is_key_down, is_key_pressed

class Player(Actor):

    def __init__(self, position: Position, gamepad: int, body_frame: Rect):
        super().__init__(*position)
        self.gamepad = gamepad
        self.humanoid = HumanoidComponent(self, body_frame)
        self.collider = CollisionComponent(self, 16)
        self.walk = WalkComponent(self, 1)
        self.walk_action = None
        self.primary_action = None
        self.secondary_action = None

    def tick(self) -> Optional[Action]:
        get_camera().target = self.position

        # clear finished actions
        actions = ['primary_action', 'secondary_action', 'walk_action']
        for action_attr in actions:
            action = getattr(self, action_attr)
            if action is not None and action.finished:
                setattr(self, action_attr, None)

        return self._handle_input()

    def destroy(self) -> None:
        self.humanoid.destroy()
        self.collider.destroy()
        self.walk.destroy()

    def _handle_input(self):
        up, down, left, right, primary, secondary = PLAYER_CONTROLS_MAP[self.gamepad]

        direction = WalkDirection.STOP
        if is_key_down(up):
            direction = WalkDirection.NORTH
        elif is_key_down(down):
            direction = WalkDirection.SOUTH
        elif is_key_down(left):
            direction = WalkDirection.WEST
        elif is_key_down(right):
            direction = WalkDirection.EAST

        # start new walk action
        if self.walk_action is None and direction != WalkDirection.STOP:
            self.walk_action = WalkAction(self.walk, direction, True)
            return self.walk_action
        # update the direction of an ongoing one
        elif self.walk_action is not None:
            self.walk_action.direction = direction

        if self.primary_action is None and is_key_pressed(primary) and self.humanoid.primary_item is not None:
            self.primary_action = self.humanoid.primary_item.use()
            return self.primary_action

        if self.secondary_action is None and is_key_pressed(secondary) and self.humanoid.secondary_item is not None:
            self.secondary_action = self.humanoid.secondary_item.use()
            return self.secondary_action
