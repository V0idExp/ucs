from abc import ABCMeta, abstractmethod
from typing import Any, List, Optional, Tuple

from ucs.foundation import Event


class Animation(metaclass=ABCMeta):
    """
    Abstract animation.
    """

    @abstractmethod
    def seek(self, position: float):
        """
        Set the animation position, where position is in [0..1] interval.
        """
        pass


class FloatAnimation(Animation):
    """
    Float property animation.
    """

    def __init__(self, obj: Any, attr: str, start: float, end: float) -> None:
        self.obj = obj
        self.attr = attr
        self.start = start
        self.end = end
        self.seek(0)

    def seek(self, position: float):
        val = self.start + (self.end - self.start) * position
        setattr(self.obj, self.attr, val)


class VectorAnimation(Animation):
    """
    2D vector tuple-like property animation.
    """

    def __init__(self, obj: Any, attr: str, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        self.obj = obj
        self.attr = attr
        self.start = start
        self.end = end
        self.seek(0)

    def seek(self, position: float):
        x0, y0 = self.start
        x1, y1 = self.end
        x = x0 + (x1 - x0) * position
        y = y0 + (y1 - y0) * position
        setattr(self.obj, self.attr, (x, y))


class AnimationPlayer:

    def __init__(self, duration: float, speed: float=1.0, channels: Optional[List[Animation]]=None) -> None:
        self.on_started = Event()
        self.on_finished = Event()
        self.position = 0
        self.duration = duration
        self.speed = speed
        self.channels: List[Animation] = channels or []

    def add_channel(self, anim: Animation):
        self.channels.append(anim)

    def play(self, dt: float):
        """
        Advance the animation by given Δt, which can also be negative.
        """

        if self.position == 0:
            self.on_started()

        new_pos = self.position + (dt / self.duration) * self.speed
        if new_pos >= 1:
            finished = True
            new_pos = 1.0
        else:
            finished = False

        for chan in self.channels:
            chan.seek(new_pos)

        self.position = new_pos

        if finished:
            self.on_finished()
