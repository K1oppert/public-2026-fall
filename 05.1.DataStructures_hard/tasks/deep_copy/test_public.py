import ast
import copy
import inspect
from typing import Any

import pytest
import testlib

import deep_copy as deep_copy_module
from deep_copy import deep_copy


###################
# Structure asserts
###################


def test_docs() -> None:
    assert testlib.is_function_docstring_exists(deep_copy)


def test_no_banned_imports() -> None:
    source = inspect.getsource(deep_copy_module)
    tree = ast.parse(source)

    banned = {"copy", "pickle", "marshal"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root not in banned, f"Module '{alias.name}' is banned"
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                root = node.module.split(".")[0]
                assert root not in banned, f"Module '{node.module}' is banned"


###################
# Immutable leaves
###################


@pytest.mark.parametrize("value", [5, -1, 0, 3.14, True, False, None, "hello", ""])
def test_immutable_leaf_is_shared(value: Any) -> None:
    """Immutable leaves should be returned as-is, not copied."""
    assert deep_copy(value) is value


def test_frozenset_is_shared() -> None:
    """frozenset is immutable all the way down, so it can be shared."""
    fs = frozenset([1, 2, 3])
    assert deep_copy(fs) is fs


def test_frozenset_with_hashable_tuple() -> None:
    """frozenset may contain tuples, which are hashable if their items are."""
    fs = frozenset([(1, 2), (3, 4)])
    assert deep_copy(fs) is fs


###################
# Container types
###################


def test_list_is_copied() -> None:
    a = [1, 2, 3]
    b = deep_copy(a)
    assert b == a
    assert b is not a
    assert b[0] is a[0]  # int is not copied


def test_dict_is_copied() -> None:
    a = {"x": 1, "y": 2}
    b = deep_copy(a)
    assert b == a
    assert b is not a


def test_tuple_is_copied() -> None:
    a = (1, [2, 3])
    b = deep_copy(a)
    assert b == a
    assert isinstance(b, tuple)
    assert b is not a
    assert b[1] is not a[1]  # inner list must be a new object


def test_set_is_copied() -> None:
    a = {1, 2, 3}
    b = deep_copy(a)
    assert b == a
    assert b is not a
    assert isinstance(b, set)


def test_container_types_preserved() -> None:
    assert isinstance(deep_copy((1, 2)), tuple)
    assert isinstance(deep_copy([1, 2]), list)
    assert isinstance(deep_copy({1, 2}), set)
    assert isinstance(deep_copy(frozenset([1, 2])), frozenset)
    assert isinstance(deep_copy({"a": 1}), dict)


###################
# Aliasing
###################


def test_aliasing_in_dict() -> None:
    shared = [1, 2]
    original = {"a": shared, "b": shared}
    copied = deep_copy(original)
    assert copied["a"] is copied["b"]
    assert copied["a"] is not shared


def test_aliasing_in_list() -> None:
    shared = {"k": 1}
    original = [shared, shared, shared]
    copied = deep_copy(original)
    assert copied[0] is copied[1] is copied[2]
    assert copied[0] is not shared


def test_aliasing_inside_tuple() -> None:
    shared = [1, 2]
    original = (shared, shared, 3)
    copied = deep_copy(original)
    assert copied[0] is copied[1]
    assert copied[0] is not shared


def test_aliasing_through_tuple_key() -> None:
    shared = [1, 2]
    key = ("k", 1)  # tuple of immutable, hashable
    original = {"a": shared, key: shared}
    copied = deep_copy(original)
    assert copied["a"] is copied[key]


###################
# Dict with non-string keys
###################


def test_dict_with_tuple_keys() -> None:
    d = {(1, 2): "a", (3, 4): "b"}
    copied = deep_copy(d)
    assert copied == d
    assert copied is not d


###################
# Nested structures
###################


def test_nested_deep_copy() -> None:
    original: dict[str, Any] = {"a": [1, 2, {"b": (3, [4])}]}
    copied = deep_copy(original)
    assert copied == original
    assert copied["a"] is not original["a"]
    assert copied["a"][2] is not original["a"][2]
    assert copied["a"][2]["b"] is not original["a"][2]["b"]
    assert copied["a"][2]["b"][1] is not original["a"][2]["b"][1]


###################
# Integration
###################


def test_deep_copy_basic() -> None:
    shared = [1, 2]
    original: dict[str, Any] = {
        "a": shared,
        "b": shared,
        "c": [3, {"d": 4}],
        "e": (5, [6]),
        "f": {7, 8},
    }

    copied = deep_copy(original)

    assert copied == original
    assert copied is not original
    assert copied["a"] is copied["b"]
    assert copied["a"] is not shared
    assert copied["c"] is not original["c"]
    assert copied["c"][1] is not original["c"][1]
    assert copied["e"][1] is not original["e"][1]
    assert copied["f"] is not original["f"]

    copied["a"].append(99)
    copied["c"][1]["d"] = 100

    assert shared == [1, 2]
    assert original["c"][1]["d"] == 4


def test_input_not_mutated() -> None:
    original = {"a": [1, {"b": 2}], "c": {3, 4}, "d": (5, [6])}
    snapshot = copy.deepcopy(original)

    deep_copy(original)

    assert original == snapshot


def test_result_is_not_original() -> None:
    original = {"a": [1, 2]}
    copied = deep_copy(original)
    assert copied is not original
    assert copied["a"] is not original["a"]
