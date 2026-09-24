import typing as tp


def pipeline(f: tp.Callable[[tp.Any], tp.Any]) -> tp.Callable[..., tp.Any]:
    """
    Start a function pipeline.
    :param f: first function of the pipeline (one argument, one result)
    :return: add: add(g) returns a NEW continuation with g appended to the end,
             add() returns the composition of all functions in the order they were added
    """
