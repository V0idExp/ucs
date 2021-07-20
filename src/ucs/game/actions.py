from dataclasses import dataclass
from typing import List

from raylibpy.spartan import get_time

from ucs.anim import AnimationPlayer, VectorPropertyAnimation
from ucs.components.sprite import SpriteComponent
from ucs.components.walk import WalkComponent, WalkDirection
from ucs.foundation import Action
from ucs.game.components import HumanoidComponent
from ucs.game.config import TIME_STEP
from ucs.game.items import Item
from ucs.game.state import State
from ucs.ui import ui_get_instance


class SequenceAction(Action):

    def __init__(self, actions: List[Action]) -> None:
        super().__init__()
        self.actions = actions

    def __call__(self) -> bool:
        while self.actions:
            if not self.actions[0]():
                return False
            self.actions.pop(0)
        return True


class ShowMessageAction(Action):
    def __init__(self, message: str) -> None:
        self.message = message
        self.shown = False

    def __call__(self) -> bool:
        ui = ui_get_instance()
        if not self.shown:
            ui.show_message(self.message)
            self.shown = True
            return False

        return not ui.prompt


@dataclass
class WieldItemAction(Action):

    humanoid: HumanoidComponent
    item: Item
    name: str

    def __call__(self) -> bool:
        self.humanoid.wield_item(self.item)
        State.pickups.append(self.name)
        return True


class MeleeAttackAction(Action):

    def __init__(self, weapon: SpriteComponent) -> None:
        dx, dy = weapon.offset
        self.attack_anim = AnimationPlayer(
            duration=0.2,
            channels=[
                VectorPropertyAnimation(
                    weapon,
                    'offset',
                    [
                        (0.0, (dx, dy)),
                        (0.5, (dx, dy - 2)),
                        (1.0, (dx, dy)),
                    ]),
                ])

    def __call__(self) -> bool:
        self.attack_anim.play(TIME_STEP)
        return self.attack_anim.is_finished


class WalkAction(Action):

    def __init__(self, walker: WalkComponent, direction: WalkDirection) -> None:
        self.started = False
        self.walker = walker
        self.direction = direction

    def __call__(self) -> bool:
        if not self.started:
            self.walker.direction = self.direction
            self.started = True
            return False

        self.walker.direction = WalkDirection.STOP
        return self.walker.dst is None


class WaitAction(Action):

    def __init__(self, seconds: float) -> None:
        super().__init__()
        self.seconds = seconds
        self.started_at = None

    def __call__(self) -> bool:
        if self.started_at is None:
            self.started_at = get_time()
        self.seconds -= get_time() - self.started_at
        return self.seconds <= 0
