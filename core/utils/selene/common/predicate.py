import re


def is_truthy(something):
    return bool(something) if not something == '' else True


def equals_ignoring_case(expected):
    return lambda actual: str(expected).lower() == str(actual).lower()


def equals(expected, ignore_case=False):
    return (
        lambda actual: expected == actual
        if not ignore_case
        else equals_ignoring_case(expected)
    )


def is_greater_than(expected):
    return lambda actual: actual > expected


def is_greater_than_or_equal(expected):
    return lambda actual: actual >= expected


def is_less_than(expected):
    return lambda actual: actual < expected


def is_less_than_or_equal(expected):
    return lambda actual: actual <= expected


def includes_ignoring_case(expected):
    return lambda actual: str(expected).lower() in str(actual).lower()


def includes(expected, ignore_case=False):
    def fn(actual):
        try:
            return (
                expected in actual
                if not ignore_case
                else includes_ignoring_case(expected)
            )
        except TypeError:
            return False

    return fn


def includes_word_ignoring_case(expected):
    return lambda actual: str(expected).lower() in re.split(
        r'\s+', str(actual).lower()
    )


def includes_word(expected, ignore_case=False):
    return (
        lambda actual: expected in re.split(r'\s+', actual)
        if not ignore_case
        else includes_ignoring_case(expected)
    )


seq_compare_by = (
    lambda f: lambda x=None, *xs: lambda y=None, *ys: True
    if x is None and y is None
    else bool(f(x)(y)) and seq_compare_by(f)(*xs)(*ys)
)

list_compare_by = lambda f: lambda expected: lambda actual: (
    seq_compare_by(f)(*expected)(*actual)
)

equals_to_list = list_compare_by(equals)
equals_by_contains_to_list = list_compare_by(includes)
