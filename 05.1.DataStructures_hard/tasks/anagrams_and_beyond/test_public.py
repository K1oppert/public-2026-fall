import copy

import pytest
import testlib

from anagrams_and_beyond import (
    group_anagrams,
    group_anagrams_linear,
    group_words_by_unique_letters,
)


def normalize_groups(groups: list[list[str]]) -> list[tuple[str, ...]]:
    """
    Gets a canonical form of the groups for comparison.
    """
    assert isinstance(groups, list)

    for group in groups:
        assert isinstance(group, list)

    return sorted(tuple(sorted(group)) for group in groups)


###################
# Structure asserts
###################


def test_docs() -> None:
    assert testlib.is_function_docstring_exists(group_anagrams)
    assert testlib.is_function_docstring_exists(group_anagrams_linear)
    assert testlib.is_function_docstring_exists(group_words_by_unique_letters)


def test_group_anagrams_linear_does_not_use_sorted() -> None:
    assert not testlib.is_global_used(group_anagrams_linear, "sorted"), (
        "group_anagrams_linear should not use sorted(). "
        "Expected an O(n * L) solution."
    )


###################
# Tests
###################


@pytest.mark.parametrize(
    "func",
    [group_anagrams, group_anagrams_linear],
)
def test_empty_list(func) -> None:
    assert func([]) == []


@pytest.mark.parametrize(
    "func",
    [group_anagrams, group_anagrams_linear],
)
def test_anagrams(func) -> None:
    words = ["eat", "tea", "tan", "ate", "nat", "bat"]
    words_copy = copy.deepcopy(words)
    result = func(words_copy)
    assert words_copy == words, "You shouldn't mutate input"
    assert normalize_groups(result) == [
        ("ate", "eat", "tea"),
        ("bat",),
        ("nat", "tan"),
    ]

    repeated_words = ["ab", "ba", "aab", "aba"]
    repeated_words_copy = copy.deepcopy(repeated_words)
    result = func(repeated_words_copy)
    assert repeated_words_copy == repeated_words, "You shouldn't mutate input"
    assert normalize_groups(result) == [
        ("aab", "aba"),
        ("ab", "ba"),
    ]


def test_group_words_by_unique_letters() -> None:
    assert group_words_by_unique_letters([]) == []

    words = ["ab", "ba", "aab", "aba"]
    words_copy = copy.deepcopy(words)
    result = group_words_by_unique_letters(words_copy)
    assert words_copy == words, "You shouldn't mutate input"
    assert normalize_groups(result) == [
        ("aab", "ab", "aba", "ba"),
    ]


def test_empty_string_corner_case() -> None:
    words = ["", "a", ""]

    words_copy = copy.deepcopy(words)
    result = group_anagrams(words_copy)
    assert words_copy == words, "You shouldn't mutate input"
    assert normalize_groups(result) == [
        ("", ""),
        ("a",),
    ]

    words_copy = copy.deepcopy(words)
    result = group_anagrams_linear(words_copy)
    assert words_copy == words, "You shouldn't mutate input"
    assert normalize_groups(result) == [
        ("", ""),
        ("a",),
    ]

    words_copy = copy.deepcopy(words)
    result = group_words_by_unique_letters(words_copy)
    assert words_copy == words, "You shouldn't mutate input"
    assert normalize_groups(result) == [
        ("", ""),
        ("a",),
    ]


def test_input_not_mutated() -> None:
    words = ["ab", "ba", "aab", "aba"]
    words_copy = copy.deepcopy(words)

    group_anagrams(words)
    group_anagrams_linear(words)
    group_words_by_unique_letters(words)

    assert words == words_copy, "You shouldn't mutate input list"
