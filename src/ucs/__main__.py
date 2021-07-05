import pathlib
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional, Tuple

from raylibpy.spartan import (close_window, get_time, is_key_pressed,
                              is_key_released, window_should_close)

from ucs.components.collision import (CollisionComponent,
                                      collision_system_update,
                                      collision_system_init)
from ucs.components.movement import (MovementComponent, movement_system_init,
                                     movement_system_update)
from ucs.components.sprite import (SpriteComponent, sprite_system_init,
                                   sprite_system_update)
from ucs.foundation import Action, Actor, Component, Rect
from ucs.gfx import get_camera, gfx_frame, gfx_init, gfx_set_map_params
from ucs.tilemap import TileMap
from ucs.ui import UI

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TIME_STEP = 1 / 60.0
DRAW_SCALE = 2.0

CAVE_DUDE = (0, 104, 16, 16)
CAVE_BABE = (17, 86, 16, 16)
ROCK = (567, 23, 16, 16)
SHIELD = (652, 74, 16, 16)
SWORD = (748, 123, 5, 10)


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


g_ui: UI = None


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
        body_w, body_h = body_frame[2:]
        self.body = SpriteComponent(actor, body_frame, (-body_w / 2, -body_h / 2))
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
        self.collider = CollisionComponent(self, 16)
        self.movement = MovementComponent(self, (-8, 0, 16, 8))

    def tick(self) -> Optional[Action]:
        self._handle_input()
        return None

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
        self.collider = CollisionComponent(self, 16)
        self.sprite = SpriteComponent(self, item.image)

    def tick(self) -> Optional[Action]:
        if self.collider.collision is not None and isinstance(self.collider.collision, Player):
            self.state = Actor.State.INACTIVE
            target = self.collider.collision
            return SequenceAction([
                ShowMessageAction('It\'s dangerous to go alone!'),
                WieldItemAction(target.humanoid, self.item),
            ])

        return None

    def destroy(self) -> None:
        self.collider.destroy()
        self.sprite.destroy()


if __name__ == '__main__':
    gfx_init("Cave dudes", (SCREEN_WIDTH, SCREEN_HEIGHT), DRAW_SCALE)
    sprite_system_init()
    movement_system_init()
    collision_system_init()

    # load the map
    tilemap = TileMap(pathlib.Path('assets', 'test_indoor.tmx'))

    gfx_set_map_params(
        tilemap.foreground_mask_texture,
        (tilemap.map.tilewidth, tilemap.map.tileheight),
        (tilemap.map.width, tilemap.map.height))

    player = Player((tilemap.entry.x, tilemap.entry.y), 0, CAVE_DUDE)
    camera = get_camera()
    camera.offset = (SCREEN_WIDTH / 2 - 8, SCREEN_HEIGHT / 2 - 8)

    # collection of actors
    actors: List[Actor] = [
        player,
        # Pickup((200, 80), Shield()),
        # Pickup((350, 330), Sword()),
    ]

    # current game actions
    actions: List[Action] = []

    # time vars
    time_acc = 0
    last_update = get_time()

    # main loop
    while not window_should_close():
        now = get_time()
        time_acc += now - last_update
        last_update = now

        # fixed-frame time step
        while time_acc >= TIME_STEP:
            time_acc -= TIME_STEP

            # process input
            for key in Key:
                if is_key_pressed(key.value):
                    PRESSED_KEYS.add(key)

                if is_key_released(key.value) and key in PRESSED_KEYS:
                    PRESSED_KEYS.remove(key)

            # update and draw the UI
            # FIXME: g_ui.update()
            # FIXME: pause = g_ui.prompt

            # tick actors and update components if not in pause
            # FIXME: if not pause:
            if True:
                collision_system_update()
                movement_system_update(tilemap)

                for actor in actors:
                    action = actor.tick()  # pylint: disable=assignment-from-none
                    if action is not None:
                        actions.append(action)

                    if actor.state == Actor.State.INACTIVE:
                        actor.destroy()

                actors = [actor for actor in actors if actor.state == Actor.State.ACTIVE]
                actions = [action for action in actions if not action()]

                camera.target = player.position

            with gfx_frame() as ctx:
                tilemap.draw(ctx)
                sprite_system_update(ctx)

    close_window()
