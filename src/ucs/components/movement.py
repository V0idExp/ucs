from typing import List

from ucs.tilemap import TileMap
from ucs.foundation import Actor, Component, Rect


class MovementComponent(Component):
    vel_x: int
    vel_y: int
    rect: Rect

    def __init__(self, actor: Actor, rect: Rect) -> None:
        super().__init__(actor)
        self.vel_x = 0
        self.vel_y = 0
        self.rect = rect
        _movement_components.append(self)

    def destroy(self) -> None:
        _movement_components.remove(self)


_movement_components: List[MovementComponent] = None


def movement_system_init():
    global _movement_components
    _movement_components = []


def movement_system_update(tilemap: TileMap):
    for mov in _movement_components:
        x = mov.actor.x + mov.vel_x
        y = mov.actor.y + mov.vel_y
        x0, y0, w, h = mov.rect
        x0 += x
        y0 += y
        x1 = x0 + w
        y1 = y0 + h
        # top-left, top-right, bottom-left, bottom-right
        points = [ (x0, y0), (x0, y1), (x1, y1), (x1, y0), ]
        collision = any(not tilemap.is_walkable_at(point) for point in points)
        if not collision:
            mov.actor.x = x
            mov.actor.y = y
