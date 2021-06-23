import pathlib
from dataclasses import dataclass
from enum import IntEnum
from functools import partial
from typing import Any, Tuple, List

from raylib.colors import *
from raylib.pyray import PyRay


CAVE_DUDE = (0, 104, 16, 16)
CAVE_BABE = (17, 86, 16, 16)
TIME_STEP = 1 / 60.0


class Key(IntEnum):
    W               = 87
    A               = 65
    S               = 83
    D               = 68
    RIGHT           = 262
    LEFT            = 263
    DOWN            = 264
    UP              = 265


CONTROLS_MAP = [
    # player 0
    (Key.W, Key.S, Key.A, Key.D),
    # player 1
    (Key.UP, Key.DOWN, Key.LEFT, Key.RIGHT),
]


@dataclass
class Movement:
    vel_x: int = 0
    vel_y: int = 0


@dataclass
class Health:
    hp: int = 0


@dataclass
class Sprite:
    frame: Tuple[int, int, int, int]


@dataclass
class HumanControl:
    gamepad: int


class Entity(list):

    def __init__(self, position: List[int], *components):
        self.extend(components)
        self.position = position


ray = None
sheet = None
player_entities = [
    Entity([100, 100], Sprite(CAVE_DUDE), Movement(), HumanControl(0)),
    Entity([300, 200], Sprite(CAVE_BABE), Movement(), HumanControl(1)),
]


def sprite_system(entities, sprite_offset):
    ray.begin_drawing()
    ray.clear_background(BLACK)
    for ent in entities:
        ray.draw_texture_rec(sheet, ent[sprite_offset].frame, ent.position, WHITE)
    ray.end_drawing()


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


systems = [
    lambda: sprite_system(player_entities, 0),
    lambda: movement_system(player_entities, 1),
    lambda: human_control_system(player_entities, 2, 1),
]


if __name__ == '__main__':
    ray = PyRay()
    ray.init_window(800, 450, "Cave dudes")

    sheet = ray.load_texture(str(pathlib.Path('.').joinpath('assets', 'characters_sheet.png')))

    time_acc = 0
    last_update = ray.get_time()

    while not ray.window_should_close():
        now = ray.get_time()
        time_acc += now - last_update
        last_update = now

        while time_acc >= TIME_STEP:
            for system in systems:
                system()
            time_acc -= TIME_STEP

    ray.close_window()
