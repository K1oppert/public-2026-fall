import typing as tp


def memoize_last(
        f: tp.Callable[[tp.Any], tp.Any]
) -> tuple[tp.Callable[[tp.Any], tp.Any], tp.Callable[[], int]]:
    """
    Cache for the last call only.
    :param f: function of one argument
    :return: pair (wrapper, calls_made):
        wrapper(x) - returns the remembered result if x equals the previous argument,
                     otherwise calls f(x), remembers x and the result, returns the result;
        calls_made() - how many times f was actually called.
    """
