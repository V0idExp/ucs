from typing import Optional, Type

from ucs.components import CollisionComponent
from ucs.foundation import Action, Actor, Position, Rect
from ucs.game.components import HumanoidComponent


class NPCBehavior:

    def __init__(self, npc: 'NPC') -> None:
        self.npc = npc

    def on_sight(self, seen: Actor) -> Optional[Action]:
        pass

    def on_idle(self) -> Optional[Action]:
        pass


class NPC(Actor):

    def __init__(self, position: Position, body_frame: Rect, behavior: Type[NPCBehavior]):
        super().__init__(*position)
        self.humanoid = HumanoidComponent(self, body_frame)
        self.behavior = behavior(self)
        self.sight_area = CollisionComponent(self, 20)
        self.seen_actors = []
        self.current_action = None

    def tick(self) -> Optional[Action]:
        if self.current_action is not None and not self.current_action.finished:
            return None

        self.current_action = None

        seen_actor = self.sight_area.collision
        if seen_actor is not None:
            if seen_actor not in self.seen_actors:
                self.seen_actors.append(seen_actor)
                self.current_action = self.behavior.on_sight(seen_actor)

        if self.current_action is None:
            self.current_action = self.behavior.on_idle()

        return self.current_action

    def destroy(self) -> None:
        self.humanoid.destroy()
        self.sight_area.destroy()
