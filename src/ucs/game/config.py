import raylibpy.consts as keys


TIME_STEP = 1 / 60.0


#: Key configurations for each player:
#: (up, down, left, right, primary, secondary)
PLAYER_CONTROLS_MAP = [
    # player 0
    (keys.KEY_W, keys.KEY_S, keys.KEY_A, keys.KEY_D, keys.KEY_E, keys.KEY_Q),
    # player 1
    (keys.KEY_UP, keys.KEY_DOWN, keys.KEY_LEFT, keys.KEY_RIGHT, keys.KEY_J, keys.KEY_K),
]
