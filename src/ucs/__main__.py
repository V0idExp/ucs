import pathlib
from typing import List, Optional

from raylibpy.spartan import close_window, get_time, window_should_close

from ucs.components.collision import collision_init, collision_update
from ucs.components.movement import movement_init, movement_update
from ucs.components.sprite import sprite_init, sprite_update
from ucs.foundation import Action, Actor, Scene
from ucs.game.actions import (DestroyActorsAction, SequenceAction,
                              ShowMessageAction, SpawnActorsAction)
from ucs.game.entities import Pickup, Player
from ucs.game.entities.npc import NPC, NPCBehavior
from ucs.game.items import Shield, Sword
from ucs.gfx import get_camera, gfx_frame, gfx_init, gfx_set_map_params
from ucs.input import input_update
from ucs.tilemap import TileMap
from ucs.ui import ui_get_instance, ui_init

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TIME_STEP = 1 / 60.0
DRAW_SCALE = 2.0

CAVE_DUDE = (0, 104, 16, 16)
CAVE_BABE = (17, 86, 16, 16)
CAVE_WISE = (17, 155, 16, 14)
ROCK = (567, 23, 16, 16)


class CaveWiseLogic(NPCBehavior):

    def on_sight(self, npc: Actor, _: Actor) -> Optional[Action]:
        x, y = npc.position

        def spawn_pickups():
            return [
                Pickup((x - 30, y), Shield()),
                Pickup((x + 20, y), Sword()),
            ]

        return SequenceAction([
            ShowMessageAction('It\'s dangerous to go alone!\nTake these!'),
            DestroyActorsAction([npc]),
            SpawnActorsAction(spawn_pickups, npc.scene),
        ])


if __name__ == '__main__':
    gfx_init("Cave dudes", (SCREEN_WIDTH, SCREEN_HEIGHT), DRAW_SCALE)
    ui_init(SCREEN_WIDTH, SCREEN_HEIGHT)
    sprite_init()
    movement_init()
    collision_init()

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
    scene = Scene([
        player,
        NPC((775, 650), CAVE_BABE, CaveWiseLogic()),
    ])

    # current game actions
    actions: List[Action] = []

    # time vars
    time_acc = 0
    last_update = get_time()

    ui = ui_get_instance()

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
                movement_update(tilemap)

                actions.extend(scene.tick())
                actions = [action for action in actions if not action()]

                camera.target = player.position

            with gfx_frame() as ctx:
                tilemap.draw(ctx)
                sprite_update(ctx)
                ui.draw(ctx)

    close_window()
