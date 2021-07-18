import inspect
import weakref
from abc import ABCMeta, abstractmethod
from enum import IntEnum
from functools import wraps
from typing import (Callable, Generic, Iterable, List, Optional, Sequence,
                    Tuple, Type, TypeVar)

Rect = Tuple[int, int, int, int]
Size = Tuple[int, int]
Position = Tuple[int, int]
Offset = Tuple[int, int]


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
    def position(self) -> Position:
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


class Event:

    def __init__(self) -> None:
        super().__init__()
        self.subscribers = []

    def __iadd__(self, listener: Callable[..., None]):
        self.subscribers.append(listener)
        return self

    def __isub__(self, listener: Callable[..., None]):
        self.subscribers.remove(listener)
        return self

    def __call__(self, *args):
        for listener in self.subscribers:
            listener(*args)


T = TypeVar('T')
class Prop(Generic[T]):

    def __init__(self, t: Type) -> None:
        self.on_changed = Event()
        self.__v = t()

    @property
    def value(self) -> T:
        return self.__v

    @value.setter
    def value(self, v: T):
        self.__v = v
        self.on_changed()


class Reactive(type):
    """
    Metaclass for reactive data structures.
    """

    def __new__(cls, name, bases, attrs):
        props = attrs.pop('__annotations__', {})
        for propname, proptype in props.items():
            attrs[propname] = Prop(proptype)
        return super(Reactive, cls).__new__(cls, name, bases, attrs)


def react(**props):
    """
    Decorator for registering methods as reactive state change handlers.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            f(*args, **kwargs)
        setattr(wrapper, '_observed_props', props)
        return wrapper

    return decorator


class ReactiveListener(type):
    """
    Metaclass for listener classes, that react to state changes.
    """
    def __init__(self, name, bases, attrs):

        def decorator(f):
            @wraps(f)
            def init_wrapper(self, *args, **kwargs):
                f(self, *args, **kwargs)

                for _, meth in inspect.getmembers(self, inspect.ismethod):
                    if not hasattr(meth, '_observed_props'):
                        continue

                    meth_ref = weakref.WeakMethod(meth)
                    props = meth._observed_props

                    def listener():
                        meth_ref()(**{arg: prop.value for arg, prop in props.items()})

                    for prop in props.values():
                        prop.on_changed += listener

                    def unsubscribe():
                        for prop in props.values():
                            prop.on_changed -= listener

                    weakref.finalize(self, unsubscribe)

            return init_wrapper

        self.__init__ = decorator(self.__init__)

        super(ReactiveListener, self).__init__(name, bases, attrs)


class Game:

    scene: Scene
    actions: List[Action]

    def __init__(self) -> None:
        self.scene = Scene([])
        self.actions = []

    def enter(self):
        pass

    def exit(self):
        pass
