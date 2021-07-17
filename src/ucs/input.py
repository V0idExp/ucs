from enum import IntEnum

from raylibpy.spartan import is_key_pressed as rl_is_key_pressed
from raylibpy.spartan import is_key_released as rl_is_key_released
import raylibpy.consts

class Key(IntEnum):
    W               = 87
    A               = 65
    S               = 83
    D               = 68
    J               = raylibpy.consts.KEY_J
    K               = raylibpy.consts.KEY_K
    Q               = raylibpy.consts.KEY_Q
    E               = raylibpy.consts.KEY_E
    RIGHT           = 262
    LEFT            = 263
    DOWN            = 264
    UP              = 265
    SPACE           = 32


_pressed_keys = set()
_released_keys = set()


def input_update():
    global _released_keys

    current_keys = set(_pressed_keys)

    # process input
    for key in Key:
        if rl_is_key_pressed(key.value):
            _pressed_keys.add(key)

        if rl_is_key_released(key.value) and key in _pressed_keys:
            _pressed_keys.remove(key)

    _released_keys = current_keys - _pressed_keys


def is_key_pressed(key: Key) -> bool:
    return key in _pressed_keys


def is_key_released(key: Key) -> bool:
    return key in _released_keys
