import os
import pathlib
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional, Sequence, Tuple

# NOTE: libraylib_shared.dll should be in the project's root!
os.environ["RAYLIB_BIN_PATH"] = os.getcwd()
from raylibpy.colors import *
from raylibpy.spartan import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TIME_STEP = 1 / 60.0

CAVE_DUDE = (0, 104, 16, 16)
CAVE_BABE = (17, 86, 16, 16)
ROCK = (567, 23, 16, 16)
SHIELD = (652, 74, 16, 16)
SWORD = (748, 123, 5, 10)


Rect = Tuple[int, int, int, int]


class UI:

    def __init__(self) -> None:
        self.message = None
        self.message_show_time = None

    def update(self) -> bool:
        if self.message is not None \
           and (get_time() - self.message_show_time) > 1.0 \
           and get_key_pressed() != 0:
            self.message = None
            self.message_show_time = None

        if self.message is not None:
            anchor_x = SCREEN_WIDTH / 2
            anchor_y = SCREEN_HEIGHT - 150
            font = get_font_default()
            tw, th = measure_text_ex(font, self.message, 14.0, 1.0)
            tx = anchor_x - tw / 2
            ty = anchor_y - th / 2
            rx = tx - 10
            ry = ty - 10
            rw = tw + 20
            rh = th + 10
            draw_rectangle(rx, ry, rw, rh, WHITE)
            draw_text_ex(font, self.message, (tx, ty), 14.0, 1.0, BLACK)
            return True
        return False

    def show_message(self, message: str) -> None:
        self.message = message
        self.message_show_time = get_time()


g_ui = UI()


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


PRESSED_KEYS = set()


class Action(metaclass=ABCMeta):
    """
    An object representing an abstract action performed upon actions.
    """

    @abstractmethod
    def __call__(self) -> bool:
        """
        Perform the action.

        An action is considered finished its call returns `True`, otherwise, it
        will be performed again on the next tick.
        """
        return True


class Actor(metaclass=ABCMeta):
    """
    A primary subject of the game world, with it's own behavior and look-n-feel.

    An actor is made up of components, that define it's actual capabilities.
    All interaction with other actions is done via actions.
    """

    class State(IntEnum):

        INACTIVE = 0
        ACTIVE = 1

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.state = Actor.State.ACTIVE

    @abstractmethod
    def tick(self) -> Sequence[Action]:
        pass

    def destroy(self) -> None:
        pass


class Component:
    """
    Component.

    A component is always attached to an actor and its lifetime is bound to
    actor's lifetime.
    """

    actor: Actor

    def __init__(self, actor: Actor) -> None:
        self.actor = actor

    def destroy(self) -> None:
        pass


class ColliderComponent(Component):
    size: int
    collision: Optional[Actor] = None

    def __init__(self, actor: Actor, size: int) -> None:
        super().__init__(actor)
        self.size = size
        self.collision = None
        add_collider(self)

    def destroy(self) -> None:
        remove_collider(self)


COLLIDERS: List[ColliderComponent] = []


def add_collider(collider: ColliderComponent):
    COLLIDERS.append(collider)


def remove_collider(collider: ColliderComponent):
    COLLIDERS.remove(collider)


def check_collisions():
    # reset collisions
    for col in COLLIDERS:
        col.collision = None

    # check for new ones
    for col in COLLIDERS:
        x0, y0 = col.actor.x, col.actor.y
        s0 = col.size

        for other in COLLIDERS:
            if col == other:
                continue

            x1, y1 = other.actor.x, other.actor.y
            s1 = other.size

            if x0 < x1 + s1 and x0 + s0 > x1 and y0 < y1 + s1 and y0 + s0 > y1:
                col.collision = other.actor
                other.collision = col.actor


class SpriteComponent(Component):
    frame: Optional[Rect]
    offset: Tuple[int, int]

    def __init__(self, actor: Actor, frame: Optional[Rect]=None, offset: Tuple[int, int]=(0, 0)) -> None:
        super().__init__(actor)
        self.frame = frame
        self.offset = offset
        add_sprite_component(self)

    def destroy(self) -> None:
        remove_sprite_component(self)


SPRITE_COMPONENTS: List[SpriteComponent] = []


def add_sprite_component(sprite: SpriteComponent):
    SPRITE_COMPONENTS.append(sprite)


def remove_sprite_component(sprite: SpriteComponent):
    SPRITE_COMPONENTS.remove(sprite)


def draw_sprites():
    for sprite in SPRITE_COMPONENTS:
        off_x, off_y = sprite.offset
        position = sprite.actor.x + off_x, sprite.actor.y + off_y
        draw_texture_rec(sheet, sprite.frame, position, WHITE)


class MovementComponent(Component):
    vel_x: int
    vel_y: int

    def __init__(self, actor: Actor) -> None:
        super().__init__(actor)
        self.vel_x = 0
        self.vel_y = 0
        add_movement_component(self)

    def destroy(self) -> None:
        remove_movement_component(self)


MOVEMENT_COMPONENTS: List[MovementComponent] = []


def add_movement_component(comp: MovementComponent):
    MOVEMENT_COMPONENTS.append(comp)


def remove_movement_component(comp: MovementComponent):
    MOVEMENT_COMPONENTS.remove(comp)


def apply_movement():
    for mov in MOVEMENT_COMPONENTS:
        mov.actor.x += mov.vel_x
        mov.actor.y += mov.vel_y


class Item(metaclass=ABCMeta):
    """
    Wieldable or equippable game item.
    """

    def __init__(self, image: Rect):
        self.image = image

    @abstractmethod
    def use(self) -> Action:
        pass


class Shield(Item):

    def __init__(self):
        super().__init__(SHIELD)

    def use(self) -> Action:
        pass


class Sword(Item):

    def __init__(self):
        super().__init__(SWORD)

    def use(self) -> Action:
        pass


class HumanoidComponent(Component):

    def __init__(self, actor: Actor, body_frame: Rect):
        super().__init__(actor)
        self.body = SpriteComponent(actor, body_frame)
        self.right_hand = None
        self.left_hand = None

    def wield_item(self, item: Item) -> bool:
        if self.left_hand is None:
            self.left_hand = (
                SpriteComponent(self.actor, item.image, (0, 3)),
                item)
        elif self.right_hand is None:
            self.right_hand = (
                SpriteComponent(self.actor, item.image, (10, 3)),
                item)
        else:
            print('no free hand for the item!')
            return False

        return True

    def destroy(self) -> None:
        if self.left_hand is not None:
            self.left_hand[0].destroy()

        if self.right_hand is not None:
            self.right_hand[0].destroy()

        self.body.destroy()


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
        if not self.shown:
            g_ui.show_message(self.message)
            self.shown = True
            return False

        return g_ui.message is None


class Player(Actor):

    def __init__(self, position, gamepad, body_frame: Rect):
        super().__init__(*position)
        self.gamepad = gamepad
        self.humanoid = HumanoidComponent(self, body_frame)
        self.collider = ColliderComponent(self, 16)
        self.movement = MovementComponent(self)

    def tick(self) -> Sequence[Action]:
        self._handle_input()
        return []

    def destroy(self) -> None:
        self.humanoid.destroy()
        self.collider.destroy()
        self.movement.destroy()

    def _handle_input(self):
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

        self.movement.vel_x = vel_x
        self.movement.vel_y = vel_y


class Pickup(Actor):

    def __init__(self, position: Tuple[int, int], item: Item):
        super().__init__(*position)
        self.item = item
        self.collider = ColliderComponent(self, 16)
        self.sprite = SpriteComponent(self, item.image)

    def tick(self) -> Action:
        if self.collider.collision is not None and isinstance(self.collider.collision, Player):
            self.state = Actor.State.INACTIVE
            target = self.collider.collision
            return [SequenceAction([
                ShowMessageAction('It\'s dangerous to go alone!'),
                WieldItemAction(target.humanoid, self.item),
            ])]

        return []

    def destroy(self) -> None:
        self.collider.destroy()
        self.sprite.destroy()


if __name__ == '__main__':
    init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Cave dudes")

    sheet = load_texture(str(pathlib.Path('.').joinpath('assets', 'characters_sheet.png')))

    time_acc = 0
    last_update = get_time()

    # collection of actors
    actors = [
        Player((400, 300), 0, CAVE_DUDE),
        Pickup((200, 80), Shield()),
        Pickup((350, 330), Sword()),
    ]

    # current game actions
    actions = []

    while not window_should_close():
        now = get_time()
        time_acc += now - last_update
        last_update = now

        while time_acc >= TIME_STEP:
            time_acc -= TIME_STEP

            begin_drawing()
            clear_background(BLACK)

            for key in Key:
                if is_key_pressed(key.value):
                    PRESSED_KEYS.add(key)

                if is_key_released(key.value) and key in PRESSED_KEYS:
                    PRESSED_KEYS.remove(key)

            if not g_ui.update():
                check_collisions()
                apply_movement()

                for actor in actors:
                    actions.extend(actor.tick())

                    if actor.state == Actor.State.INACTIVE:
                        actor.destroy()

                actors = [actor for actor in actors if actor.state == Actor.State.ACTIVE]
                actions = [action for action in actions if not action()]

            draw_sprites()
            end_drawing()

    close_window()
