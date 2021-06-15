from mytpyes import Num


def percentage_value(percentage_rate: Num,
                     base_value: Num) -> float:

    return base_value / 100 * percentage_rate


def percentage_rate(percentage_value: Num,
                    base_value: Num) -> float:

    return percentage_value * 100 / base_value


def percentage_base_value(percentage_value: Num,
                          percentage_rate: Num) -> float:

    return percentage_value * 100 / percentage_rate
