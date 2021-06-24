import pathlib
from dataclasses import dataclass
from enum import Enum, IntEnum
from functools import partial
from typing import Any, List, Optional, Tuple, cast

from raylib.colors import *
from raylib.pyray import PyRay

CAVE_DUDE = (0, 104, 16, 16)
CAVE_BABE = (17, 86, 16, 16)
ROCK = (567, 23, 16, 16)
SHIELD = (652, 74, 16, 16)

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


COLLIDEABLES = {}


class Entity(list):

    class State(IntEnum):
        DISABLED = 0
        ENABLED = 1

    class Kind(Enum):
        OTHER = 'other'
        NPC = 'npc'
        PLAYER = 'player'
        SHIELD = 'shield'

    def __init__(self, position: List[int], components, kind: Kind=Kind.OTHER):
        self.extend(components)
        self.position = position
        self.state = Entity.State.ENABLED
        self.kind = kind


@dataclass
class Movement:
    vel_x: int = 0
    vel_y: int = 0


@dataclass
class Sprite:
    frame: Rect


@dataclass
class HumanControl:
    gamepad: int


@dataclass
class NPCControl:
    pass


@dataclass
class PhysicsBody:
    mass: int


@dataclass
class Collideable:
    size: int
    collided_with: Optional[Entity] = None


@dataclass
class Humanoid:
    body: Rect
    shield: Optional[Rect] = None


ray = None
sheet = None


player_entities = [
    Entity([600, 200], [Humanoid(CAVE_BABE, None), Movement(), HumanControl(1), Collideable(16)], kind=Entity.Kind.PLAYER),
]

npc_entities = [
    Entity([50, 200], [Humanoid(CAVE_DUDE, SHIELD), Movement(), NPCControl(), Collideable(16)], kind=Entity.Kind.NPC),
]

rock_entities = [
    Entity([400, 0], [Sprite(ROCK), Movement(), PhysicsBody(1)]),
]

pickup_entities = [
    Entity([400, 300], [Sprite(SHIELD), Collideable(32)], Entity.Kind.SHIELD),
]


def player_wield_shield(player_entity):
    player_entity[0].shield = SHIELD


def sprite_system(entities, sprite_offset):
    for ent in entities:
        ray.draw_texture_rec(sheet, ent[sprite_offset].frame, ent.position, WHITE)


def humanoid_system(entities, humanoid_offset):
    for ent in entities:
        humanoid = ent[humanoid_offset]
        ray.draw_texture_rec(sheet, humanoid.body, ent.position, WHITE)
        if humanoid.shield is not None:
            shield_x, shield_y = ent.position
            shield_x += 8
            shield_y += 3
            ray.draw_texture_rec(sheet, humanoid.shield, (shield_x, shield_y), WHITE)


def movement_system(entities, movement_offset):
    for ent in entities:
        mov = ent[movement_offset]
        ent.position[0] += mov.vel_x
        ent.position[1] += mov.vel_y


def human_control_system(entities, human_control_offset, movement_offset):
    for ent in entities:
        ctrl = ent[human_control_offset]
        mov = ent[movement_offset]
        mov.vel_x = mov.vel_y = 0
        up, down, left, right = CONTROLS_MAP[ctrl.gamepad]
        if ray.is_key_down(up):
            mov.vel_y -= 1
        if ray.is_key_down(down):
            mov.vel_y += 1
        if ray.is_key_down(left):
            mov.vel_x -= 1
        if ray.is_key_down(right):
            mov.vel_x += 1


def npc_control_system(entities, movement_offset, npc_control_offset):
    for ent in entities:
        ctrl = ent[npc_control_offset]
        mov = ent[movement_offset]
        mov.vel_x = 1


def physics_system(entities, movement_offset, body_offset):
    for ent in entities:
        mov = ent[movement_offset]
        body = ent[body_offset]
        if body.mass > 0:
            mov.vel_y = 2


def collision_system(entities, collideable_offset):
    for ent in entities:
        key = id(ent)
        if key not in COLLIDEABLES and ent.state is not Entity.State.DISABLED:
            COLLIDEABLES[key] = (ent, ent[collideable_offset])
        elif COLLIDEABLES[key][0].state is Entity.State.DISABLED:
            COLLIDEABLES.pop(key)

    for _, col in COLLIDEABLES.values():
        col.collided_with = None

    ids = COLLIDEABLES.keys()
    for ent_id in ids:
        ent, col = COLLIDEABLES[ent_id]
        x0, y0 = ent.position
        s0 = col.size

        for other_id in ids:
            if other_id == ent_id:
                continue

            other_ent, other_col = COLLIDEABLES[other_id]
            x1, y1 = other_ent.position
            s1 = other_col.size

            if x0 < x1 + s1 and x0 + s0 > x1 and y0 < y1 + s1 and y0 + s0 > y1:
                col.collided_with = other_ent
                other_col.collided_with = ent


def pickup_system(entities, humanoid_offset, collideable_offset):
    for ent in entities:
        humanoid = ent[humanoid_offset]
        col = ent[collideable_offset]
        if col.collided_with is None:
            continue
        elif col.collided_with.kind is Entity.Kind.SHIELD:
            col.collided_with.state = Entity.State.DISABLED
            humanoid.shield = SHIELD
        elif ent.kind is Entity.Kind.NPC\
             and col.collided_with.kind is Entity.Kind.PLAYER\
             and humanoid.shield is not None:
            # FIXME: ok, this is the weak point of the system: we explicitly
            # access specific entity archetype internals
            player_wield_shield(col.collided_with)
            humanoid.shield = None
            ent.state = Entity.State.DISABLED

ITERATIONS = 0

def filter_active(entities):
    global ITERATIONS
    for ent in entities:
        ITERATIONS += 1
        if ent.state is Entity.State.ENABLED:
            yield ent


systems = [
    lambda: physics_system(filter_active(rock_entities), 1, 2),
    lambda: movement_system(filter_active(rock_entities), 1),
    lambda: sprite_system(filter_active(rock_entities), 0),

    lambda: collision_system(filter_active(pickup_entities), 1),
    lambda: sprite_system(filter_active(pickup_entities), 0),

    lambda: human_control_system(filter_active(player_entities), 2, 1),
    lambda: collision_system(filter_active(player_entities), 3),
    lambda: movement_system(filter_active(player_entities), 1),
    lambda: pickup_system(filter_active(player_entities), 0, 3),
    lambda: humanoid_system(filter_active(player_entities), 0),

    lambda: npc_control_system(filter_active(npc_entities), 1, 2),
    lambda: collision_system(filter_active(npc_entities), 3),
    lambda: movement_system(filter_active(npc_entities), 1),
    lambda: pickup_system(filter_active(npc_entities), 0, 3),
    lambda: humanoid_system(filter_active(npc_entities), 0),
]


if __name__ == '__main__':
    ray = cast(Any, PyRay())
    ray.init_window(800, 600, "Cave dudes")

    sheet = ray.load_texture(str(pathlib.Path('.').joinpath('assets', 'characters_sheet.png')))

    time_acc = 0
    last_update = ray.get_time()

    printed = False

    while not ray.window_should_close():
        now = ray.get_time()
        time_acc += now - last_update
        last_update = now

        while time_acc >= TIME_STEP:
            ray.begin_drawing()
            ray.clear_background(BLACK)

            ITERATIONS = 0

            for system in systems:
                system()
            time_acc -= TIME_STEP

            if not printed:
                print('Total entities visited:', ITERATIONS)

            ray.end_drawing()

    ray.close_window()
