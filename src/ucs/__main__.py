import pathlib
from dataclasses import dataclass
from enum import Enum, IntEnum
from functools import partial
from typing import Any, List, Optional, Tuple, cast, Sequence
from abc import ABCMeta, abstractmethod
from raylib.colors import *
from raylib.pyray import PyRay


CAVE_DUDE = (0, 104, 16, 16)
CAVE_BABE = (17, 86, 16, 16)
ROCK = (567, 23, 16, 16)
SHIELD = (652, 74, 16, 16)
SWORD = (748, 123, 5, 10)

TIME_STEP = 1 / 60.0


Rect = Tuple[int, int, int, int]


class Key(IntEnum):
    W               = 87
    A               = 65
    S               = 83
    D               = 68
    RIGHT           = 262
    LEFT            = 263
    DOWN            = 264
    UP              = 265
    SPACE           = 32


CONTROLS_MAP = [
    # player 0
    (Key.W, Key.S, Key.A, Key.D),
    # player 1
    (Key.UP, Key.DOWN, Key.LEFT, Key.RIGHT),
]


COLLIDERS = []


PRESSED_KEYS = set()


@dataclass
class Sprite:
    frame: Rect


@dataclass
class DrawCommand:

    sprite: Sprite
    position: Tuple[int, int]


DRAW_LIST: List[DrawCommand] = []


def draw_sprite(sprite: Sprite, position: Tuple[int, int]):
    DRAW_LIST.append(DrawCommand(sprite, position))


class Action(metaclass=ABCMeta):

    @abstractmethod
    def perform(self):
        pass


class Entity(metaclass=ABCMeta):

    class Flags(IntEnum):

        DESTROY = 1

    def __init__(self, position: Tuple[int, int]):
        self.position = list(position)
        self.flags = 0

    @property
    def x(self) -> int:
        return self.position[0]

    @x.setter
    def x(self, value):
        self.position[0] = value

    @property
    def y(self) -> int:
        return self.position[1]

    @y.setter
    def y(self, value):
        self.position[1] = value

    @abstractmethod
    def tick(self) -> Sequence[Action]:
        pass


@dataclass
class Collider:

    entity: Entity
    size: int
    collision: Optional[Entity] = None


def add_collider(collider: Collider):
    COLLIDERS.append(collider)


def remove_collider(collider: Collider):
    COLLIDERS.remove(collider)


@dataclass
class Movement:

    entity: Entity
    vel_x: int
    vel_y: int


MOVEMENT_COMPONENTS = []

def add_movement_component(comp: Movement):
    MOVEMENT_COMPONENTS.append(comp)


def remove_movement_component(comp: Movement):
    MOVEMENT_COMPONENTS.remove(comp)


class Item(metaclass=ABCMeta):

    class BodyPart(Enum):
        LEFT_HAND = 'left_hand'
        RIGHT_HAND = 'right_hand'

    def __init__(self, body_part: BodyPart, sprite: Sprite):
        self.body_part = body_part
        self.sprite = sprite

    @abstractmethod
    def use(self) -> Action:
        pass


class Shield(Item):

    def __init__(self):
        super().__init__(Item.BodyPart.RIGHT_HAND, Sprite(SHIELD))

    def use(self) -> Action:
        pass


class Sword(Item):

    def __init__(self):
        super().__init__(Item.BodyPart.LEFT_HAND, Sprite(SWORD))

    def use(self) -> Action:
        pass


class MoveAction(Action):

    def __init__(self, movement, velocity):
        self.movement = movement
        self.velocity = velocity

    def perform(self):
        self.movement.vel_x, self.movement.vel_y = self.velocity


class LooksLikeHuman:
    parent: Entity
    body: Sprite
    left_hand: Optional[Item]
    right_hand: Optional[Item]
    items: List[Item]

    def __init__(self, parent: Entity, body: Sprite):
        self.parent = parent
        self.body = body
        self.right_hand = None
        self.left_hand = None
        self.items = []

    def draw(self):
        x, y = self.parent.x, self.parent.y

        draw_sprite(self.body, (x, y))

        if self.left_hand is not None:
            draw_sprite(self.left_hand.sprite, (x - 2, y + 3))

        if self.right_hand is not None:
            draw_sprite(self.right_hand.sprite, (x + 9, y + 4))


@dataclass
class WieldItemAction(Action):

    humanoid: LooksLikeHuman
    item: Item

    def perform(self):
        if self.item.body_part is Item.BodyPart.LEFT_HAND:
            self.humanoid.left_hand = self.item
        elif self.item.body_part is Item.BodyPart.RIGHT_HAND:
            self.humanoid.right_hand = self.item

        self.humanoid.items.append(self.item)


@dataclass
class RemoveItemAction(Action):

    humanoid: LooksLikeHuman
    item: Item

    def perform(self):
        if self.item.body_part is Item.BodyPart.LEFT_HAND:
            self.humanoid.left_hand = None
        elif self.item.body_part is Item.BodyPart.RIGHT_HAND:
            self.humanoid.right_hand = None

        self.humanoid.items.remove(self.item)


class Player(Entity):

    def __init__(self, position, body, gamepad):
        super().__init__(position)
        self.gamepad = gamepad
        self.humanoid = LooksLikeHuman(self, body)
        self.collider = Collider(self, 16)
        self.movement = Movement(self, 0, 0)

        add_collider(self.collider)
        add_movement_component(self.movement)

    def tick(self) -> Sequence[Action]:
        actions = [self._handle_input()]

        self.humanoid.draw()

        return actions

    def _handle_input(self) -> Action:
        vel_x, vel_y = 0, 0
        up, down, left, right = CONTROLS_MAP[self.gamepad]
        if up in PRESSED_KEYS:
            vel_y -= 1
        if down in PRESSED_KEYS:
            vel_y += 1
        if left in PRESSED_KEYS:
            vel_x -= 1
        if right in PRESSED_KEYS:
            vel_x += 1

        return MoveAction(self.movement, (vel_x, vel_y))


class Pickup(Entity):

    def __init__(self, position: Tuple[int, int], item: Item):
        super().__init__(position)
        self.item = item
        self.collider = Collider(self, 16)

        add_collider(self.collider)

    def tick(self) -> Action:
        draw_sprite(self.item.sprite, (self.x, self.y))

        if self.collider.collision is not None and isinstance(self.collider.collision, Player):
            self.flags |= Entity.Flags.DESTROY
            target = self.collider.collision
            return [
                WieldItemAction(target.humanoid, self.item)
            ]

        return []


def check_collisions():
    # reset collisions
    for col in COLLIDERS:
        col.collision = None

    # check for new ones
    for col in COLLIDERS:
        x0, y0 = col.entity.position
        s0 = col.size

        for other in COLLIDERS:
            if col == other:
                continue

            x1, y1 = other.entity.x, other.entity.y
            s1 = other.size

            if x0 < x1 + s1 and x0 + s0 > x1 and y0 < y1 + s1 and y0 + s0 > y1:
                col.collision = other.entity
                other.collision = col.entity


def apply_movement():
    for mov in MOVEMENT_COMPONENTS:
        mov.entity.x += mov.vel_x
        mov.entity.y += mov.vel_y


if __name__ == '__main__':
    ray = cast(Any, PyRay())
    ray.init_window(800, 600, "Cave dudes")

    sheet = ray.load_texture(str(pathlib.Path('.').joinpath('assets', 'characters_sheet.png')))

    time_acc = 0
    last_update = ray.get_time()

    shield = Shield()
    sword = Sword()

    entities = [
        Player((400, 300), Sprite(CAVE_DUDE), 0),
        Pickup((200, 80), shield),
        Pickup((350, 330), sword),
    ]

    while not ray.window_should_close():
        now = ray.get_time()
        time_acc += now - last_update
        last_update = now

        while time_acc >= TIME_STEP:
            for key in Key:
                if ray.is_key_pressed(key.value):
                    PRESSED_KEYS.add(key)

                if ray.is_key_released(key.value) and key in PRESSED_KEYS:
                    PRESSED_KEYS.remove(key)

            check_collisions()
            apply_movement()

            ray.begin_drawing()
            ray.clear_background(BLACK)

            DRAW_LIST.clear()

            for entity in entities:
                for action in entity.tick():
                    action.perform()

            entities = [ent for ent in entities if not ent.flags & Entity.Flags.DESTROY]

            for draw_cmd in DRAW_LIST:
                ray.draw_texture_rec(sheet, draw_cmd.sprite.frame, draw_cmd.position, WHITE)

            time_acc -= TIME_STEP

            ray.end_drawing()

    ray.close_window()
