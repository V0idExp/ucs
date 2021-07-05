from abc import ABCMeta, abstractmethod
from enum import IntEnum
from typing import Optional, Tuple


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

    @property
    def position(self) -> Pos:
        return (self.x, self.y)

    @abstractmethod
    def tick(self) -> Optional[Action]:
        return None

    def destroy(self) -> None:
        pass


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
