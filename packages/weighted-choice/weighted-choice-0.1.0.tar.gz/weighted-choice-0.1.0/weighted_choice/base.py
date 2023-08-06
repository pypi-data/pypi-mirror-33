import random

from weighted_choice.exceptions import WeightedChoiceError


class WeightedChoice:
    """
    Provides a random generator of a limited set of choices with a probability
    of occuring described as a weight
    """

    random.seed()

    def __init__(self, total=None, default=None, **weighted_choices):
        self.default = default
        self.sorted_keys = sorted(
            weighted_choices,
            key=weighted_choices.__getitem__,
        )
        weight_sum = sum(weighted_choices.values())
        WeightedChoiceError.require_condition(
            total is None or weight_sum <= total,
            "Sum of weights must be less than or equal to the supplied total",
        )
        self.total = total if total is not None else weight_sum

        self.weighted_choices = {}
        running_total = 0.0
        for choice in self.sorted_keys:
            weight = weighted_choices[choice] / self.total
            self.weighted_choices[choice] = (
                running_total,
                running_total + weight,
            )
            running_total += weight

    def get_choice(self):
        value = random.random()
        for (choice, interval) in self.weighted_choices.items():
            if value >= interval[0] and value < interval[1]:
                return choice
        return self.default
