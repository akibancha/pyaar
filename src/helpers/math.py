from typing import Union


def percentage_value(percentage_rate: Union[int, float],
                     base_value: Union[int, float]) -> float:

    return base_value / 100 * percentage_rate


def percentage_rate(percentage_value: Union[int, float],
                    base_value: Union[int, float]) -> float:

    return percentage_value * 100 / base_value


def percentage_base_value(percentage_value: Union[int, float],
                          percentage_rate: Union[int, float]) -> float:

    return percentage_value * 100 / percentage_rate
