from dataclasses import dataclass
from typing import Collection, List, Optional, Type

from raylibpy.spartan import get_time
from ucs.anim import AnimationPlayer
from ucs.components.walk import WalkComponent, WalkDirection
from ucs.foundation import Action, Actor
from ucs.game.components import HumanoidComponent
from ucs.game.config import TIME_STEP
from ucs.game.items.item import Item
from ucs.game.state import State
from ucs.tilemap import tilemap_get_active
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
        self.humanoid.equip_item(self.item)
        State.pickups.append(self.name)
        return True


class MeleeAttackAction(Action):

    def __init__(self, actor: Actor, damage: int, pre_anim: Optional[AnimationPlayer]=None, post_anim: Optional[AnimationPlayer]=None) -> None:
        self.actor = actor
        self.damage = damage
        self.pre_anim = pre_anim
        self.post_anim = post_anim

    def __call__(self) -> bool:
        is_anim_finished = True
        if self.pre_anim is not None:
            self.pre_anim.play(TIME_STEP)
            is_anim_finished &= self.pre_anim.is_finished
            if is_anim_finished:
                self.__do_damage()

        if is_anim_finished and self.post_anim is not None:
            self.post_anim.play(TIME_STEP)
            is_anim_finished &= self.post_anim.is_finished

        return is_anim_finished

    def __do_damage(self):
        tilemap = tilemap_get_active()
        col, row = tilemap.pixels_to_coords(self.actor.position)
        nearby_actors = list(tilemap.get_nearest_occupants(col, row))
        for actor in nearby_actors:
            if actor != self.actor:
                actor.state = Actor.State.INACTIVE


class WalkAction(Action):

    def __init__(self, walker: WalkComponent, direction: WalkDirection, continuous: bool=False) -> None:
        self.started = False
        self.walker = walker
        self.direction = direction
        self.continuous = continuous

    def __call__(self) -> bool:
        if not self.started or self.continuous:
            self.walker.direction = self.direction
            self.started = True
            return self.direction is WalkDirection.STOP

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
