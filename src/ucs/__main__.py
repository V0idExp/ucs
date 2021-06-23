from dataclasses import dataclass
from raylib.pyray import PyRay
from raylib.colors import *


@dataclass
class Movement:
    vel_x: int = 0
    vel_y: int = 0


@dataclass
class Health:
    hp: int = 0


class Entity(list):

    def __init__(self, *components):
        self.extend(components)
        self.position = [0, 0, 0]


foo_entities = [Entity(Movement(), Health()), Entity(Movement(), Health()), Entity(Movement(), Health())]
bar_entities = [Entity(Health()), Entity(Health())]
baz_entities = [Entity(Movement(), Health())]


def apply_gravity(entites, movement_offset):
    for ent in entites:
        ent[movement_offset].vel_y -= 10  # 9.81 m/s


ray = PyRay()

ray.init_window(800, 450, "Hello Pyray")

while not ray.window_should_close():
    ray.begin_drawing()
    ray.clear_background(RAYWHITE)
    ray.draw_text("Hello world", 190, 200, 20, VIOLET)
    ray.end_drawing()
ray.close_window()
