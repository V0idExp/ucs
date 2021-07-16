from abc import ABCMeta, abstractmethod
from enum import IntEnum
from typing import Iterable, Optional, Sequence, Tuple

Rect = Tuple[int, int, int, int]
Size = Tuple[int, int]
Pos = Tuple[int, int]


class Action(metaclass=ABCMeta):
    """
    An object representing an abstract action performed by an actor.
    """

    @abstractmethod
    def __call__(self) -> bool:
        """
        Perform the action.

        An action is considered finished if this call returns `True`, otherwise,
        it will be kept and executed over and over again.
        """
        return True


class Actor(metaclass=ABCMeta):
    """
    A primary subject of the game world, with it's own behavior and look-n-feel.

    An actor is made up of components, that define it's actual capabilities.
    All interaction with other actors is done via actions.
    """

    class State(IntEnum):

        INACTIVE = 0
        ACTIVE = 1

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.state = Actor.State.ACTIVE
        self.scene: Scene = None

    @property
    def position(self) -> Pos:
        return (self.x, self.y)

    @abstractmethod
    def tick(self) -> Optional[Action]:
        return None

    def destroy(self) -> None:
        pass


class Scene(list):
    """
    A scene for actors.
    """

    def __init__(self, actors: Optional[Iterable[Actor]]=None):
        super().__init__(actors)
        for actor in self:
            actor.scene = self

    def tick(self) -> Sequence[Action]:
        to_remove = []
        for actor in self:
                action = actor.tick()
                if action is not None:
                    yield action

                if actor.state == Actor.State.INACTIVE:
                    to_remove.append(actor)

        for actor in to_remove:
            self.remove(actor)
            actor.destroy()
            actor.scene = None

    def append(self, actor: Actor) -> None:
        super().append(actor)
        actor.scene = self

    def extend(self, iterable: Iterable[Actor]) -> None:
        super().extend(iterable)
        for actor in iterable:
            actor.scene = self


class Component:
    """
    Component.

    A component is always attached to an actor and its lifetime is bound to
    actor's lifetime.
    """

    actor: Actor

    def __init__(self, actor: Actor) -> None:
        self.actor = actor

    def destroy(self) -> None:
        pass
