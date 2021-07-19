from ucs.foundation import Reactive


class State(metaclass=Reactive):

    pickups: list[str]
