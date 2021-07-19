from dataclasses import dataclass
from typing import Callable, List, Sequence

from ucs.anim import AnimationPlayer, VectorPropertyAnimation
from ucs.components.sprite import SpriteComponent
from ucs.foundation import Action, Actor, Scene
from ucs.game.components import HumanoidComponent
from ucs.game.config import TIME_STEP
from ucs.game.items import Item
from ucs.game.state import State
from ucs.ui import ui_get_instance


@dataclass
class FuncAction(Action):

    callable: Callable

    def __call__(self) -> bool:
        return self.callable


@dataclass
class WieldItemAction(Action):

    humanoid: HumanoidComponent
    item: Item
    name: str

    def __call__(self) -> bool:
        self.humanoid.wield_item(self.item)
        State.pickups.append(self.name)
        return True


class SequenceAction(Action):

    def __init__(self, actions: List[Action]) -> None:
        super().__init__()
        self.actions = actions

    def __call__(self) -> bool:
        while self.actions:
            if not self.actions[0]():
                return False
            self.actions.pop(0)


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


class SpawnActorsAction(Action):

    def __init__(self, factory: Callable[[], Sequence[Actor]], scene: Scene) -> None:
        self.factory = factory
        self.scene = scene

    def __call__(self) -> bool:
        self.scene.extend(self.factory())
        return True


class DestroyActorsAction(Action):

    def __init__(self, actors: Sequence[Actor]) -> None:
        self.actors = actors

    def __call__(self) -> bool:
        for actor in self.actors:
            actor.state = Actor.State.INACTIVE
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
