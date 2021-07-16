from ucs.foundation import Action, Actor, Rect, Position
from typing import Optional

from ucs.game.components import HumanoidComponent
from ucs.components import CollisionComponent


class NPCBehavior:

    def on_sight(self, actor: Actor, other: Actor) -> Optional[Action]:
        pass


class NPC(Actor):

    def __init__(self, position: Position, body_frame: Rect, behavior: NPCBehavior):
        super().__init__(*position)
        self.humanoid = HumanoidComponent(self, body_frame)
        self.behavior = behavior
        self.sight_area = CollisionComponent(self, 20)
        self.seen_actors = []

    def tick(self) -> Optional[Action]:
        seen_actor = self.sight_area.collision
        if seen_actor is not None:
            if seen_actor not in self.seen_actors:
                self.seen_actors.append(seen_actor)
                return self.behavior.on_sight(self, seen_actor)
        return None

    def destroy(self) -> None:
        self.humanoid.destroy()
        self.sight_area.destroy()
