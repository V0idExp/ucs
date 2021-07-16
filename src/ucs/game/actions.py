from dataclasses import dataclass
from typing import Callable, List, Sequence, Union

from ucs.foundation import Action, Scene, Actor
from ucs.game.components import HumanoidComponent
from ucs.game.items import Item
from ucs.ui import ui_get_instance


@dataclass
class WieldItemAction(Action):

    humanoid: HumanoidComponent
    item: Item

    def __call__(self) -> bool:
        self.humanoid.wield_item(self.item)
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
