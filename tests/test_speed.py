from anki_audio_speed.speed import snap


def test_rounds_to_nearest_step():
    assert snap(0.83, 0.5, 1.5, 0.05) == 0.85
    assert snap(0.82, 0.5, 1.5, 0.05) == 0.8


def test_drops_float_noise_from_key_steps():
    assert snap(0.8 + 0.05, 0.5, 1.5, 0.05) == 0.85
    assert snap(1.0 - 0.05 - 0.05 - 0.05, 0.5, 1.5, 0.05) == 0.85


def test_clamps_to_range():
    assert snap(0.3, 0.5, 1.5, 0.05) == 0.5
    assert snap(2.0, 0.5, 1.5, 0.05) == 1.5


def test_bound_off_the_step_grid_still_holds():
    assert snap(1.0, 0.5, 0.98, 0.05) == 0.98
