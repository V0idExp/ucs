from ucs.anim import (AnimationPlayer, FloatPropertyAnimation,
                      VectorPropertyAnimation)


def test_float_animation(mocker):
    o = mocker.Mock()
    o.value = 0
    anim = AnimationPlayer(
        duration=1.0,
        speed=1.0,
        channels=[FloatPropertyAnimation(o, 'value', [(0, 10), (0.5, 15), (1.0, 25)]),])

    assert not anim.is_finished
    assert not anim.is_started

    # t = 0
    anim.play(0.0)
    assert o.value == 10.0
    assert anim.is_started
    assert not anim.is_finished

    # t = 0.25
    anim.play(0.25)
    assert o.value == 12.5
    assert not anim.is_finished

    # t = 0.75
    anim.play(0.5)
    assert o.value == 20.0
    assert not anim.is_finished

    # t = 1.0
    anim.play(0.25)
    assert o.value == 25.0
    assert anim.is_finished


def test_vector_animation(mocker):
    o = mocker.Mock()
    anim = AnimationPlayer(
        duration=1.0,
        speed=1.0,
        channels=[VectorPropertyAnimation(o, 'position', [
            (0.0, (0, 0)),
            (1.0, (5, 3)),
        ])])

    assert o.position == (0, 0)
    assert not anim.is_started
    assert not anim.is_finished

    anim.play(0.5)
    assert anim.is_started
    assert not anim.is_finished
    assert o.position == (2.5, 1.5)

    anim.play(0.5)
    assert o.position == (5, 3)
    assert anim.is_finished
