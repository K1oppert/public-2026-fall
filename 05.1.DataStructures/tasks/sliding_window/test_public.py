import builtins
import copy
import dataclasses

import pytest
import testlib

from sliding_window import sliding_window_max


@dataclasses.dataclass
class Case:
    nums: list[int]
    k: int
    result: list[int]

    def __str__(self) -> str:
        return f"{self.nums}, k={self.k}"


TEST_CASES = [
    Case(nums=[2, 4, 1, 7, 3], k=3, result=[4, 7, 7]),
    Case(nums=[1, 2, 3], k=1, result=[1, 2, 3]),
    Case(nums=[1, 2, 3], k=3, result=[3]),
    Case(nums=[1, 2], k=5, result=[]),
    Case(nums=[1, 2], k=0, result=[]),
    Case(nums=[1, 2], k=-1, result=[]),
    Case(nums=[], k=3, result=[]),
]


###################
# Structure asserts
###################


def test_docs() -> None:
    assert testlib.is_function_docstring_exists(sliding_window_max)


###################
# Tests
###################


@pytest.mark.parametrize("t", TEST_CASES, ids=str)
def test_sliding_window_max(t: Case) -> None:
    nums_copy = copy.deepcopy(t.nums)

    result = sliding_window_max(t.nums, t.k)

    assert t.nums == nums_copy, "You shouldn't mutate input list"
    assert result == t.result


def test_does_not_use_builtin_max(monkeypatch: pytest.MonkeyPatch) -> None:
    real_max = builtins.max
    calls = []

    def spy_max(*args, **kwargs):
        calls.append((args, kwargs))
        return real_max(*args, **kwargs)

    monkeypatch.setattr(builtins, "max", spy_max)

    result = sliding_window_max([2, 4, 1, 7, 3], 3)

    assert result == [4, 7, 7]
    assert not calls, (
        "You shouldn't use max() on the whole window. "
        "Expected an O(n) solution."
    )
