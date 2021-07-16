from enum import IntEnum

from raylibpy.spartan import is_key_pressed as rl_is_key_pressed
from raylibpy.spartan import is_key_released as rl_is_key_released


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


PLAYER_CONTROLS_MAP = [
    # player 0
    (Key.W, Key.S, Key.A, Key.D),
    # player 1
    (Key.UP, Key.DOWN, Key.LEFT, Key.RIGHT),
]


_pressed_keys = set()


def input_update():
    # process input
    for key in Key:
        if rl_is_key_pressed(key.value):
            _pressed_keys.add(key)

        if rl_is_key_released(key.value) and key in _pressed_keys:
            _pressed_keys.remove(key)


def is_key_pressed(key: Key) -> bool:
    return key in _pressed_keys
