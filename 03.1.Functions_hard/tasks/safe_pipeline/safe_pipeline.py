import typing as tp


def safe_pipeline(f: tp.Callable[[tp.Any], tp.Any]) -> tp.Callable[..., tp.Any]:
    """
    Start a function pipeline that stops at the first None.
    :param f: first function of the pipeline (one argument, returns a result or None on error)
    :return: add: add(g) returns a NEW continuation with g appended to the end,
             add() returns the composition of all functions; as soon as some step returns None,
             the composition returns None without calling the remaining steps
    """
