import pathlib
from typing import Optional

from ucs.foundation import Action, Game, ReactiveListener, react
from ucs.game.actions import (SequenceAction, ShowMessageAction,
                              SpawnActorsAction)
from ucs.game.entities import Pickup, Player
from ucs.game.entities.npc import NPC, NPCBehavior
from ucs.game.items import Shield, Sword
from ucs.game.state import State
from ucs.tilemap import TileMap, tilemap_set_active

CAVE_DUDE = (0, 104, 16, 16)
CAVE_BABE = (17, 86, 16, 16)


class TutorialNPC(NPCBehavior):

    def on_sight(self, npc: NPC, _) -> Optional[Action]:
        x, y = npc.position

        def spawn_pickups():
            return [
                Pickup((x - 32, y), Shield()),
                Pickup((x + 32, y), Sword()),
            ]

        return SequenceAction([
            ShowMessageAction('It\'s dangerous to go alone!\nTake these!'),
            SpawnActorsAction(spawn_pickups, npc.scene),
        ])


class Tutorial(Game, metaclass=ReactiveListener):

    def enter(self):
        # load the map
        tilemap = TileMap(pathlib.Path('assets', 'test_indoor.tmx'))
        tilemap_set_active(tilemap)

        self.scene.extend([
            Player(tilemap.entry, 0, CAVE_DUDE),
            NPC((768, 624), CAVE_BABE, TutorialNPC())
        ])

    @react(pickups=State.pickups_count)
    def _on_pickups_count_change(self, pickups: int):
        if pickups == 2:
            self.actions.append(ShowMessageAction('Now, defeat these mobs!'))
