from ucs.input import Key


TIME_STEP = 1 / 60.0


#: Key configurations for each player:
#: (up, down, left, right, primary, secondary)
PLAYER_CONTROLS_MAP = [
    # player 0
    (Key.W, Key.S, Key.A, Key.D, Key.Q, Key.E),
    # player 1
    (Key.UP, Key.DOWN, Key.LEFT, Key.RIGHT, Key.J, Key.K),
]
