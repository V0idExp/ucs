from typing import List, Optional

from ucs.foundation import Actor, Component


class CollisionComponent(Component):
    size: int
    collision: Optional[Actor] = None

    def __init__(self, actor: Actor, size: int) -> None:
        super().__init__(actor)
        self.size = size
        self.collision = None
        _colliders.append(self)

    def destroy(self) -> None:
        _colliders.remove(self)


_colliders: List[CollisionComponent] = None


def collision_system_init():
    global _colliders
    _colliders = []


def collider_system_update():
    # reset collisions
    for col in _colliders:
        col.collision = None

    # check for new ones
    for col in _colliders:
        x0, y0 = col.actor.x, col.actor.y
        s0 = col.size

        for other in _colliders:
            if col == other:
                continue

            x1, y1 = other.actor.x, other.actor.y
            s1 = other.size

            if x0 < x1 + s1 and x0 + s0 > x1 and y0 < y1 + s1 and y0 + s0 > y1:
                col.collision = other.actor
                other.collision = col.actor
