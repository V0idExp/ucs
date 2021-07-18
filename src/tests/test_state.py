from ucs.foundation import Reactive, ReactiveListener, react


class State(metaclass=Reactive):

    hp: int


class Listener(metaclass=ReactiveListener):

    def __init__(self):
        self.current_hp = None

    @react(hp=State.hp)
    def on_hp_changed(self, hp: int):
        self.current_hp = hp


def test_reactivity():
    listener = Listener()

    # `listener` has auto-registered itself for `State.hp.on_changed` event
    assert State.hp.on_changed.subscribers

    # test the reaction to `State.hp` prop change
    assert listener.current_hp is None
    State.hp.value = 99
    assert listener.current_hp == 99

    # when `listener` is collected, it should auto-unregister itself from the
    # `State.hp.on_changed` event
    del listener
    assert not State.hp.on_changed.subscribers
