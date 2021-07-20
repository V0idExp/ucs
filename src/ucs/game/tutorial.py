import pathlib
import random
from typing import Optional

from ucs.components.walk import WalkDirection
from ucs.foundation import Action, Game, ReactiveListener, react
from ucs.game.actions import (SequenceAction, ShowMessageAction, WaitAction,
                              WalkAction)
from ucs.game.entities import Pickup, Player
from ucs.game.entities.npc import NPC, NPCBehavior
from ucs.game.items import Shield, Sword
from ucs.game.state import State
from ucs.tilemap import TileMap, tilemap_set_active

CAVE_DUDE = (0, 104, 16, 16)
CAVE_BABE = (17, 86, 16, 16)
CAVE_BRUTE = (17, 172, 16, 14)


class TutorialNPCBehavior(NPCBehavior, metaclass=ReactiveListener):

    def __init__(self, npc: 'NPC') -> None:
        super().__init__(npc)
        self.weapons_given = False
        self.weapons_collected = False
        self.mobs_spawned = False

    def on_sight(self, _) -> Optional[Action]:
        if not self.weapons_given:

            def spawn_pickups():
                x, y = self.npc.position
                self.npc.scene.extend([
                    Pickup((x - 32, y), Shield(), 'shield'),
                    Pickup((x + 32, y), Sword(), 'sword'),
                ])
                self.weapons_given = True
                return True

            return SequenceAction([
                ShowMessageAction('It\'s dangerous to go alone!\nTake these!'),
                spawn_pickups,
            ])

    def on_idle(self) -> Optional[Action]:
        if self.weapons_collected and not self.mobs_spawned:
            self.mobs_spawned = True

            def spawn_mobs():
                self.npc.scene.extend([
                    NPC((656, 656), CAVE_BRUTE, MobNPCBehavior),
                    NPC((880, 656), CAVE_BRUTE, MobNPCBehavior),
                ])
                self.mobs_spawned = True
                return True

            return SequenceAction([
                ShowMessageAction('Now, defeat the mobs!'),
                spawn_mobs,
            ])

    @react(pickups=State.pickups)
    def on_pickups_changed(self, pickups: list[str]):
        if 'sword' in pickups and 'shield' in pickups:
            self.weapons_collected = True



class MobNPCBehavior(NPCBehavior):

    def on_idle(self) -> Optional[Action]:
        direction = random.choice(list(WalkDirection))
        return SequenceAction([
            WaitAction(1.0),
            WalkAction(self.npc.walker, direction),
        ])


class Tutorial(Game):

    def enter(self):
        # load the map
        tilemap = TileMap(pathlib.Path('assets', 'test_indoor.tmx'))
        tilemap_set_active(tilemap)

        self.scene.extend([
            Player(tilemap.entry, 0, CAVE_DUDE),
            NPC((768, 624), CAVE_BABE, TutorialNPCBehavior)
        ])
