import inspect
import weakref
from abc import ABCMeta, abstractmethod
from enum import IntEnum
from functools import partial, wraps
from typing import (Callable, Generic, GenericAlias, Iterable, List, Optional,
                    Sequence, Tuple, TypeVar)

Rect = Tuple[int, int, int, int]
Size = Tuple[int, int]
Position = Tuple[int, int]
Offset = Tuple[int, int]


class Action(metaclass=ABCMeta):
    """
    An object representing an abstract action performed by an actor.
    """

    finished: bool

    def __init__(self) -> None:
        self.finished = False

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

    def __init__(self, x: int, y: int, name: str='') -> None:
        self.x = x
        self.y = y
        self.state = Actor.State.ACTIVE
        self.scene: Scene = None
        self.name = name or f'{self.__class__.__name__}_{id(self)}'

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

    def __init__(self, default_value: T) -> None:
        self.on_changed = Event()
        self.__v = default_value

    @property
    def value(self) -> T:
        return self.__v

    @value.setter
    def value(self, v: T):
        changed = self.__v != v
        self.__v = v
        if changed:
            self.on_changed()


_T = TypeVar('_T')
class ListProp(List[_T]):

    def __init__(self):
        super().__init__()
        self.value = self
        self.on_changed = Event()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.on_changed()

    def remove(self, __value: _T):
        elem = super().remove(__value)
        self.on_changed()
        return elem

    def pop(self, __index: int) -> _T:
        elem = super().pop(__index=__index)
        self.on_changed()
        return elem

    def append(self, __object: _T):
        super().append(__object)
        self.on_changed()

    def extend(self, __iterable: Iterable[_T]):
        super().extend(__iterable)
        self.on_changed()

    def insert(self, __index: int, __object: _T):
        super().insert(__index, __object)
        self.on_changed()

    def reverse(self):
        super().reverse()
        self.on_changed()

    def sort(self):
        super().sort()
        self.on_changed()

    def clear(self):
        super().clear()
        self.on_changed()


class Reactive(type):
    """
    Metaclass for reactive data structures.
    """

    def __new__(cls, name, bases, attrs):
        props = attrs.pop('__annotations__', {})
        for propname, proptype in props.items():
            if isinstance(proptype, GenericAlias) and issubclass(proptype.__origin__, list):
                prop = ListProp()
            else:
                prop = Prop(attrs.get(propname, proptype()))
            attrs[propname] = prop
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

                subscriptions = []

                for _, meth in inspect.getmembers(self, inspect.ismethod):
                    if not hasattr(meth, '_observed_props'):
                        continue

                    meth_ref = weakref.WeakMethod(meth)
                    props = meth._observed_props

                    def callback(method, props):
                        method()(**{arg: prop.value for arg, prop in props.items()})

                    handler = partial(callback, meth_ref, props)
                    for prop in props.values():
                        prop.on_changed += handler
                        subscriptions.append((prop, handler))

                def unsubscribe():
                    for prop, handler in subscriptions:
                        prop.on_changed -= handler

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
