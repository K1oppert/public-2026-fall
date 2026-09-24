import random
import math
from typing import List, Tuple, TypeAlias
from pathlib import Path

import testlib

from int_sqrt import int_sqrt

###################
# Structure asserts
###################


def test_banned_modules() -> None:
    assert not testlib.is_module_imported(
        'math', Path(__file__).parent / 'int_sqrt.py'
    ), 'You should not use `math` module'


###################
# Tests
###################


Integer: TypeAlias = int
TestPair: TypeAlias = Tuple[Integer, Integer]


def test_perfect_squares() -> None:
    """Тест на точные квадраты"""
    test_cases: List[TestPair] = [
        (0, 0),
        (1, 1),
        (4, 2),
        (9, 3),
        (16, 4),
        (25, 5),
        (36, 6),
        (49, 7),
        (64, 8),
        (81, 9),
        (100, 10),
        (144, 12),
        (10000, 100),
        (1000000, 1000),
    ]

    for n, expected in test_cases:
        assert int_sqrt(n) == expected, f"int_sqrt({n}) != {expected}"


def test_non_perfect_squares() -> None:
    """Тест на неполные квадраты (округление вниз)"""
    test_cases: List[TestPair] = [
        (2, 1),
        (3, 1),
        (5, 2),
        (8, 2),
        (10, 3),
        (15, 3),
        (17, 4),
        (24, 4),
        (26, 5),
        (35, 5),
        (50, 7),
        (99, 9),
        (101, 10),
        (999, 31),
    ]

    for n, expected in test_cases:
        assert int_sqrt(n) == expected, f"int_sqrt({n}) != {expected}"


def test_edge_cases() -> None:
    """Граничные случаи"""
    assert int_sqrt(0) == 0
    assert int_sqrt(1) == 1
    assert int_sqrt(2) == 1
    assert int_sqrt(3) == 1
    assert int_sqrt(4) == 2


def test_large_perfect_squares() -> None:
    """Тест на большие точные квадраты"""
    test_cases: List[TestPair] = [
        (1_000_000_000_000, 1_000_000),  # 10^12 = (10^6)^2
        (999_999_999_999, 999_999),       # чуть меньше 10^12
        (1_000_000_000_000_000, 31_622_776),  # 10^15
        (1_000_000_000_000_000_000, 1_000_000_000),  # 10^18
    ]

    for n, expected in test_cases:
        result = int_sqrt(n)
        assert result == expected, f"int_sqrt({n}) != {expected}, got {result}"
        assert result * result <= n, f"Результат {result} слишком большой для {n}"
        assert (result + 1) * (result + 1) > n, f"Результат {result} слишком маленький для {n}"


def test_stress_random_values() -> None:
    """Стресс-тест на случайных значениях до 1_000_000_000_000"""
    random.seed(42)

    for _ in range(1000):
        n: Integer = random.randint(0, 1_000_000_000_000)
        result: Integer = int_sqrt(n)

        # Проверяем свойства квадратного корня
        assert result * result <= n, f"Для {n}: {result}^2 = {result*result} > {n}"
        assert (result + 1) * (result + 1) > n, f"Для {n}: ({result+1})^2 = {(result+1)*(result+1)} <= {n}"

        # Сравниваем с math.isqrt
        assert result == math.isqrt(n), f"Для {n}: {result} != {math.isqrt(n)}"


def test_stress_boundary_values() -> None:
    """Стресс-тест на граничных значениях"""
    boundary_values: List[Integer] = [
        0, 1, 2, 3, 4, 5,
        999_999, 1_000_000, 1_000_001,
        999_999_999, 1_000_000_000, 1_000_000_001,
        999_999_999_999, 1_000_000_000_000,
    ]

    for n in boundary_values:
        result: Integer = int_sqrt(n)
        assert result == math.isqrt(n), f"Для {n}: {result} != {math.isqrt(n)}"
        assert result * result <= n
        assert (result + 1) * (result + 1) > n


def test_stress_sequential_values() -> None:
    """Стресс-тест на последовательных значениях"""
    for n in range(0, 10_000):
        result: Integer = int_sqrt(n)
        assert result == math.isqrt(n), f"Для {n}: {result} != {math.isqrt(n)}"


def test_stress_squares_around_boundary() -> None:
    """Стресс-тест вокруг границы 1_000_000_000_000"""
    base: Integer = 1_000_000  # sqrt(10^12)

    # Тестируем вокруг точного квадрата
    for delta in range(-100, 101):
        n: Integer = base * base + delta
        if n >= 0:
            result: Integer = int_sqrt(n)
            expected: Integer = math.isqrt(n)
            assert result == expected, f"Для {n}: {result} != {expected}"


def test_stress_powers_of_ten() -> None:
    """Стресс-тест на степенях десятки"""
    for power in range(0, 13):  # до 10^12
        n: Integer = 10 ** power
        result: Integer = int_sqrt(n)
        expected: Integer = math.isqrt(n)
        assert result == expected, f"Для 10^{power}: {result} != {expected}"


def test_stress_max_value() -> None:
    """Стресс-тест на максимальном значении"""
    max_val: Integer = 1_000_000_000_000

    result: Integer = int_sqrt(max_val)
    assert result == math.isqrt(max_val)
    assert result * result <= max_val
    assert (result + 1) * (result + 1) > max_val

    # Проверяем соседние значения
    for delta in range(-10, 11):
        n: Integer = max_val + delta
        if n >= 0:
            assert int_sqrt(n) == math.isqrt(n), f"Для {n}"


def test_stress_random_large_values() -> None:
    """Стресс-тест на случайных больших значениях"""
    random.seed(123)

    for _ in range(500):
        # Генерируем числа в диапазоне от 10^9 до 10^12
        n: Integer = random.randint(1_000_000_000, 1_000_000_000_000)
        result: Integer = int_sqrt(n)

        assert result * result <= n
        assert (result + 1) * (result + 1) > n
        assert result == math.isqrt(n)


def test_stress_alternating_boundaries() -> None:
    """Стресс-тест на чередующихся границах"""
    # Тестируем значения, которые являются квадратами
    for i in range(1, 1000):
        square: Integer = i * i
        assert int_sqrt(square) == i, f"int_sqrt({square}) != {i}"

        # Проверяем значение перед квадратом
        if square > 0:
            assert int_sqrt(square - 1) == i - 1, f"int_sqrt({square-1}) != {i-1}"

        # Проверяем значение после квадрата
        assert int_sqrt(square + 1) == i, f"int_sqrt({square+1}) != {i}"


def test_stress_performance() -> None:
    """Проверка производительности на больших значениях"""
    import time

    start: float = time.time()

    for _ in range(1000):
        int_sqrt(1_000_000_000_000)

    elapsed: float = time.time() - start
    assert elapsed < 2.0, f"Алгоритм слишком медленный: {elapsed:.2f} сек"


def test_stress_recursion_depth() -> None:
    """Проверка глубины рекурсии на больших значениях"""
    import sys

    # Увеличиваем лимит рекурсии для теста
    old_limit: Integer = sys.getrecursionlimit()
    sys.setrecursionlimit(10000)

    try:
        # Для 10^12 глубина рекурсии ~ 40 (log2(10^12) ≈ 40)
        result: Integer = int_sqrt(1_000_000_000_000)
        assert result == 1_000_000
    finally:
        sys.setrecursionlimit(old_limit)


def test_stress_known_values() -> None:
    """Стресс-тест на известных значениях"""
    known_values: List[TestPair] = [
        (1_000_000_000_000, 1_000_000),
        (999_999_999_999, 999_999),
        (1_000_000_000, 31_622),
        (999_999_999, 31_622),
        (100_000_000, 10_000),
        (10_000_000, 3_162),
        (1_000_000, 1_000),
        (100_000, 316),
        (10_000, 100),
        (1_000, 31),
        (100, 10),
        (10, 3),
    ]

    for n, expected in known_values:
        result: Integer = int_sqrt(n)
        assert result == expected, f"int_sqrt({n}) != {expected}, got {result}"
