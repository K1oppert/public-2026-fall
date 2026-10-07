from typing import Any


def deep_copy(obj: Any) -> Any:
    """
    Creates a deep copy of the given object.

    Supported types:
        dict, list, tuple, set, frozenset,
        int, float, bool, str, None.

    Immutable leaves and frozensets are shared as references.
    Mutable containers are copied recursively.
    Aliasing is preserved.

    Args:
        obj: Object to copy.

    Returns:
        A deep copy of obj.
    """
    raise NotImplementedError
