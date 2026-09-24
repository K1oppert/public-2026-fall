import typing as tp


def make_adder() -> tp.Callable[..., tp.Any]:
    """
    Start a new curried summation chain.
    :return: adder: adder(x) returns a NEW adder that also remembers x,
             adder() returns the sum of all numbers passed in this chain (0 for an empty chain)
    """
