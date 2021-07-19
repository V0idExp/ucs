from ucs.foundation import Reactive, ReactiveListener, react


def test_basic_types_reactivity():

    class State(metaclass=Reactive):

        hp: int = 50
        score: int = 0
        alive: bool = True
        name: str
        progress: float = 0.0


    class Listener(metaclass=ReactiveListener):

        def __init__(self):
            self.condition = 'playing'

        @react(hp=State.hp, alive=State.alive)
        def check_health(self, hp, alive):
            if hp == 0 or not alive:
                self.condition = 'defeat'

        @react(name=State.name)
        def check_name(self, name):
            if name == 'cheater':
                self.condition = 'victory'

        @react(score=State.score)
        def check_score(self, score):
            State.progress.value = score / 50.0

        @react(prog=State.progress)
        def check_progress(self, prog):
            if prog == 1.0:
                self.condition = 'victory'

    listener = Listener()

    # `listener` should auto-register its methods as callbacks for State's
    # properties `on_changed` event on creation
    props = [State.hp, State.score, State.progress, State.alive, State.name]
    assert all(prop.on_changed.subscribers for prop in props)

    assert listener.condition == 'playing'

    State.name.value = 'cheater'
    assert listener.condition == 'victory'

    listener.condition = 'playing'
    State.hp.value = 0
    assert listener.condition == 'defeat'

    State.hp.value = 20
    listener.condition = 'playing'
    State.alive.value = False
    assert listener.condition == 'defeat'

    listener.condition = 'playing'
    State.score.value += 15
    assert listener.condition == 'playing'
    State.score.value += 35
    assert listener.condition == 'victory'
    assert State.progress.value == 1.0

    # when `listener` is collected, it should auto-unregister itself from the
    # State's properties `on_changed` event
    del listener
    assert not any(prop.on_changed.subscribers for prop in props)


def test_list_reactivity():
    class State(metaclass=Reactive):

        items: list[str]

    class Listener(metaclass=ReactiveListener):

        def __init__(self) -> None:
            self.mission_complete = False

        @react(items=State.items)
        def check_items(self, items):
            self.mission_complete = 'sword' in items and 'shield' in items

    listener = Listener()
    assert not listener.mission_complete
    assert State.items.on_changed.subscribers

    State.items.append('sword')
    assert not listener.mission_complete

    State.items.append('shield')
    assert listener.mission_complete

    del listener
    assert not State.items.on_changed.subscribers
