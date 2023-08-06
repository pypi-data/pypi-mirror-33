import pytest

from weighted_choice import alive, WeightedChoice, WeightedChoiceError


def test_alive():
    assert alive()


def test_weighted_choice():
    """
    This test verifies that a WeightedChoice is constrained to appropriate
    values and creation time and that over a long range of producing
    choices renders the expected distribution
    """
    with pytest.raises(WeightedChoiceError):
        WeightedChoice(a=3, b=4, total=6)

    chooser = WeightedChoice(a=.3, b=.2, c=.1, total=1.0, default='d')
    choices = dict(a=0, b=0, c=0, d=0)
    total = 10000
    for i in range(total):
        choices[chooser.get_choice()] += 1

    assert choices['a'] / total == pytest.approx(.3, 0.1)
    assert choices['b'] / total == pytest.approx(.2, 0.1)
    assert choices['c'] / total == pytest.approx(.1, 0.1)
    assert choices['d'] / total == pytest.approx(.4, 0.1)

    chooser = WeightedChoice(a=3, b=2, c=1)
    choices = {'a': 0, 'b': 0, 'c': 0, None: 0}
    total = 10000
    for i in range(total):
        choices[chooser.get_choice()] += 1

    assert choices['a'] / total == pytest.approx(3 / 6, 0.1)
    assert choices['b'] / total == pytest.approx(2 / 6, 0.1)
    assert choices['c'] / total == pytest.approx(1 / 6, 0.1)
    assert choices[None] == 0

    chooser = WeightedChoice(a=13)
    choices = {'a': 0, None: 0}
    total = 10000
    for i in range(total):
        choices[chooser.get_choice()] += 1

    assert choices['a'] == total
    assert choices[None] == 0
