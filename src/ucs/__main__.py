import pathlib
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import List, NamedTuple, Optional, Tuple

import pytmx
from raylibpy.colors import *
from raylibpy.core import Camera2D, Color, Texture2D
from raylibpy.spartan import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TIME_STEP = 1 / 60.0
DRAW_SCALE = 2.0

CAVE_DUDE = (0, 104, 16, 16)
CAVE_BABE = (17, 86, 16, 16)
ROCK = (567, 23, 16, 16)
SHIELD = (652, 74, 16, 16)
SWORD = (748, 123, 5, 10)


Rect = Tuple[int, int, int, int]
Size = Tuple[int, int]

class UI:

    prompt: bool = False  # is the UI currently waiting for prompt

    def __init__(self) -> None:
        self.message = None
        self.message_show_time = None
        self.prompt = False

    def update(self):
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
            self.prompt = True
        else:
            self.prompt = False

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
    An object representing an abstract action performed by an actor.
    """

    @abstractmethod
    def __call__(self) -> bool:
        """
        Perform the action.

        An action is considered finished if this call returns `True`, otherwise,
        it will be kept and executed over and over again.
        """
        return True


class Actor(metaclass=ABCMeta):
    """
    A primary subject of the game world, with it's own behavior and look-n-feel.

    An actor is made up of components, that define it's actual capabilities.
    All interaction with other actors is done via actions.
    """

    class State(IntEnum):

        INACTIVE = 0
        ACTIVE = 1

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.state = Actor.State.ACTIVE

    @abstractmethod
    def tick(self) -> Optional[Action]:
        return None

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
    rect: Rect

    def __init__(self, actor: Actor, rect: Rect) -> None:
        super().__init__(actor)
        self.vel_x = 0
        self.vel_y = 0
        self.rect = rect
        add_movement_component(self)

    def destroy(self) -> None:
        remove_movement_component(self)


g_camera = None


class CameraComponent(Component):

    def __init__(self, actor: Actor) -> None:
        global g_camera
        if g_camera is not None:
            raise RuntimeError('only one camera component is allowed at a time')
        super().__init__(actor)
        self.camera = Camera2D(offset=(SCREEN_WIDTH / 2 - 16, SCREEN_HEIGHT / 2 - 16), zoom=DRAW_SCALE)
        g_camera = self


MOVEMENT_COMPONENTS: List[MovementComponent] = []


def add_movement_component(comp: MovementComponent):
    MOVEMENT_COMPONENTS.append(comp)


def remove_movement_component(comp: MovementComponent):
    MOVEMENT_COMPONENTS.remove(comp)


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
        self.collider = ColliderComponent(self, 16)
        self.movement = MovementComponent(self, (-8, 0, 16, 8))
        self.camera = CameraComponent(self)

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
        self.collider = ColliderComponent(self, 16)
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


class Map:

    def __init__(self, filename) -> None:
        self.textures = {}
        self.map = pytmx.TiledMap(filename, self.image_loader)
        self.x = 0
        self.y = 0

        try:
            self.entry = self.map.objects_by_name['entry']
        except KeyError:
            raise ValueError(f'no entry point defined for map {filename}')

    def image_loader(self, filename, flags, **kwargs):
        if filename not in self.textures:
            self.textures[filename] = load_texture(filename)

        def load(rect=None, flags=None):
            return filename, rect, flags

        return load

    def obstacle_at(self, point):
        collision_layer = self.map.layernames.get('Obstacles')
        if collision_layer is None:
            return False
        x, y = point
        x -= self.x
        y -= self.y
        row = int(y // self.map.tilewidth)
        col = int(x // self.map.tileheight)
        tile = collision_layer.data[row][col]
        if self.map.images[tile] is not None:
            return True
        return False

    def draw(self):
        tile_width = self.map.tilewidth
        tile_height = self.map.tileheight

        for layer in self.map.layers:
            name = layer.name.lower()
            if any(skip in name for skip in ('meta', 'obstacles')):
                continue

            for r, row in enumerate(layer.data):
                y_offset = self.y + r * tile_width
                for c, col in enumerate(row):
                    x_offset = self.x + c * tile_height
                    if self.map.images[col] is not None:
                        filename, rect, _ = self.map.images[col]
                        tex = self.textures[filename]
                        draw_texture_rec(tex, rect, (x_offset, y_offset), WHITE)
                        dst_rect = (x_offset, y_offset, tile_width, tile_height)
                        draw_texture_pro(tex, rect, dst_rect, (0, 0), 0, WHITE)


class DrawCommand(metaclass=ABCMeta):

    order: int

    @abstractmethod
    def draw(self):
        pass


DRAW_COMMANDS: List[DrawCommand] = []


class DrawRectOutlineCommand(DrawCommand):

    def __init__(self, order: int, rect: Rect, color: Color) -> None:
        super().__init__()
        self.order = order
        self.rect = rect
        self.color = color

    def draw(self):
        draw_rectangle_lines(*self.rect, self.color)



def apply_movement(map):
    for mov in MOVEMENT_COMPONENTS:
        x = mov.actor.x + mov.vel_x
        y = mov.actor.y + mov.vel_y
        x0, y0, w, h = mov.rect
        x0 += x
        y0 += y
        x1 = x0 + w
        y1 = y0 + h
        # top-left, top-right, bottom-left, bottom-right
        points = [
            (x0, y0),
            (x0, y1),
            (x1, y1),
            (x1, y0),
        ]
        collision = any(map.obstacle_at(point) for point in points)
        if not collision:
            mov.actor.x = x
            mov.actor.y = y
            color = GREEN
        else:
            color = RED

        DRAW_COMMANDS.append(DrawRectOutlineCommand(1000, (x0, y0, w, h), color))


if __name__ == '__main__':
    init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Cave dudes")

    sheet = load_texture(str(pathlib.Path('.').joinpath('assets', 'characters_sheet.png')))
    map = Map(pathlib.Path('assets', 'sample_indoor.tmx'))

    time_acc = 0
    last_update = get_time()

    # collection of actors
    actors: List[Actor] = [
        Player((map.entry.x, map.entry.y), 0, CAVE_DUDE),
        # Pickup((200, 80), Shield()),
        # Pickup((350, 330), Sword()),
    ]

    # current game actions
    actions: List[Action] = []

    if g_camera is None:
        raise RuntimeError('at elast one entity must have a CameraComponent!')

    while not window_should_close():
        now = get_time()
        time_acc += now - last_update
        last_update = now

        while time_acc >= TIME_STEP:
            time_acc -= TIME_STEP

            begin_drawing()
            clear_background(BLACK)
            DRAW_COMMANDS.clear()

            for key in Key:
                if is_key_pressed(key.value):
                    PRESSED_KEYS.add(key)

                if is_key_released(key.value) and key in PRESSED_KEYS:
                    PRESSED_KEYS.remove(key)

            # update the UI
            g_ui.update()

            pause = g_ui.prompt

            if not pause:
                check_collisions()
                apply_movement(map)

                # update the camera
                # TODO: move this into some sort of camera system... although
                # it's pretty simple
                g_camera.camera.target = (g_camera.actor.x, g_camera.actor.y)

                for actor in actors:
                    action = actor.tick()  # pylint: disable=assignment-from-none
                    if action is not None:
                        actions.append(action)

                    if actor.state == Actor.State.INACTIVE:
                        actor.destroy()

                actors = [actor for actor in actors if actor.state == Actor.State.ACTIVE]
                actions = [action for action in actions if not action()]

            begin_mode2d(g_camera.camera)
            map.draw()
            draw_sprites()

            for cmd in DRAW_COMMANDS:
                cmd.draw()

            end_mode2d()
            end_drawing()

    close_window()
