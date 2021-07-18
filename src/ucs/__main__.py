import pathlib

from raylibpy.spartan import close_window, get_time, window_should_close

from ucs.components.collision import collision_init, collision_update
from ucs.components.movement import movement_init, movement_update
from ucs.components.sprite import sprite_init, sprite_update
from ucs.components.walk import walk_init, walk_update
from ucs.foundation import Scene
from ucs.game.config import TIME_STEP
from ucs.game.tutorial import Tutorial
from ucs.gfx import get_camera, gfx_frame, gfx_init
from ucs.input import input_update
from ucs.tilemap import tilemap_get_active
from ucs.ui import ui_get_instance, ui_init


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DRAW_SCALE = 2.0


if __name__ == '__main__':
    gfx_init("Cave dudes", (SCREEN_WIDTH, SCREEN_HEIGHT), DRAW_SCALE)
    ui_init(SCREEN_WIDTH, SCREEN_HEIGHT)
    walk_init()
    sprite_init()
    movement_init()
    collision_init()

    camera = get_camera()
    camera.offset = (SCREEN_WIDTH / 2 - 8, SCREEN_HEIGHT / 2 - 8)

    # time vars
    time_acc = 0
    last_update = get_time()

    ui = ui_get_instance()

    game = Tutorial()
    game.enter()

    # main loop
    while not window_should_close():
        now = get_time()
        time_acc += now - last_update
        last_update = now

        # fixed-frame time step
        while time_acc >= TIME_STEP:
            time_acc -= TIME_STEP

            # handle input
            input_update()

            # update the UI
            pause = ui.update()

            # tick actors and update components if not in pause
            if not pause:
                collision_update()
                movement_update(tilemap_get_active())
                walk_update(tilemap_get_active())

                game.actions.extend(game.scene.tick())
                game.actions = [action for action in game.actions if not action()]

            with gfx_frame() as ctx:
                tilemap_get_active().draw(ctx)
                sprite_update(ctx)
                ui.draw(ctx)

    game.exit()

    close_window()
