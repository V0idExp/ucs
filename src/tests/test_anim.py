from ucs.anim import FloatAnimation, AnimationPlayer


def test_float_animation(mocker):
    o = mocker.Mock()
    started, finished = mocker.Mock(), mocker.Mock()
    anim = AnimationPlayer(
        duration=2.0,
        speed=1.0,
        channels=[
            FloatAnimation(o, 'value', 10.0, 20.0),
        ])

    anim.on_started += started
    anim.on_finished += finished

    assert o.value == 10.0

    anim.play(1.0)
    assert o.value == 15.0
    started.assert_called_once()
    finished.assert_not_called()

    anim.play(0.5)
    assert o.value == 17.5
    finished.assert_not_called()

    anim.play(0.5)
    assert o.value == 20.0
    finished.assert_called_once()
