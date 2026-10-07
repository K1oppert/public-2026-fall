def group_anagrams(words: list[str]) -> list[list[str]]:
    """
    Groups anagrams by sorting each word.

    Args:
        words: List of lowercase latin words.

    Returns:
        List of groups of anagrams.
        The order of groups and the order inside groups are not specified.
    """
    raise NotImplementedError


def group_anagrams_linear(words: list[str]) -> list[list[str]]:
    """
    Groups anagrams using a linear-time word feature.

    Args:
        words: List of lowercase latin words.

    Returns:
        List of groups of anagrams.
        The order of groups and the order inside groups are not specified.
    """
    raise NotImplementedError


def group_words_by_unique_letters(words: list[str]) -> list[list[str]]:
    """
    Groups words by the set of unique letters.

    Letter multiplicity is ignored. For example, "ab" and "aab"
    will be placed in the same group.

    Args:
        words: List of lowercase latin words.

    Returns:
        List of groups of words with the same set of unique letters.
        The order of groups and the order inside groups are not specified.
    """
    raise NotImplementedError
