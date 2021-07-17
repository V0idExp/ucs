from abc import ABCMeta, abstractmethod
from typing import Any, List, Optional

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
