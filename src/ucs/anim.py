from abc import ABCMeta, abstractmethod
from typing import Any, List, Optional, Sequence, Tuple


class Animation(metaclass=ABCMeta):
    """
    Base animation class.
    """

    def __init__(self, keys: Sequence[Tuple[float, Any]]) -> None:
        if not keys:
            raise ValueError('animations require at least one key value')
        self.keys = sorted(keys, key=lambda k: k[0])
        self.seek(0)

    def seek(self, t: float):
        """
        Set the animation position, where position is in [0..1] interval.
        """
        t0 = 0.0
        t1 = 1.0
        for i, (t1, value) in enumerate(self.keys):
            if t1 >= t:
                start = stop = value
                if i > 0:
                    t0, start = self.keys[i - 1]
                break

        dt = t1 - t0
        if dt == 0:
            f = 1.0
        else:
            f = (t - t0) / dt

        self.animate(start, stop, f)

    @abstractmethod
    def animate(self, start: Any, stop: Any, f: float):
        """
        Animate between two key values.
        """
        pass


class FloatPropertyAnimation(Animation):
    """
    Float property animation.
    """

    def __init__(self, obj: Any, attr: str, keys: Sequence[Tuple[float, float]]=()) -> None:
        self.obj = obj
        self.attr = attr
        super().__init__(keys)

    def animate(self, start: float, stop: float, f: float):
        value = start + (stop - start) * f
        setattr(self.obj, self.attr, value)


class VectorPropertyAnimation(Animation):
    """
    2D vector tuple-like property animation.
    """

    def __init__(self, obj: Any, attr: str, keys: Sequence[Tuple[float, Tuple[int, int]]]=()) -> None:
        self.obj = obj
        self.attr = attr
        super().__init__(keys)

    def animate(self, start: Tuple[int, int], end: Tuple[int, int], f: float):
        x0, y0 = start
        x1, y1 = end
        x = x0 + (x1 - x0) * f
        y = y0 + (y1 - y0) * f
        setattr(self.obj, self.attr, (x, y))


class AnimationPlayer:

    def __init__(self, duration: float, speed: float=1.0, channels: Optional[List[Animation]]=None) -> None:
        self.is_started = False
        self.is_finished = False
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
            self.is_started = True

        self.position = min(self.position + (dt / self.duration) * self.speed, 1.0)

        for chan in self.channels:
            chan.seek(self.position)

        self.is_finished = self.position == 1.0
