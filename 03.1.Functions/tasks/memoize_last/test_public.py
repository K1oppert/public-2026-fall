import random
from typing import List, Tuple, Any, Optional
from pathlib import Path

import testlib

from memoize_last import memoize_last

###################
# Structure asserts
###################


STATE_MSG = 'Состояние храните в переменных замыкания, без списков/словарей'


def test_banned_modules() -> None:
    assert not testlib.is_module_imported(
        'functools', Path(__file__).parent / 'memoize_last.py'
    ), 'You should not use `functools` module'

    for op in ('BUILD_LIST', 'BUILD_MAP', 'BUILD_SET'):
        assert not testlib.is_bytecode_op_used(memoize_last, op), STATE_MSG
    for name in ('list', 'dict', 'set'):
        assert not testlib.is_global_used(memoize_last, name), STATE_MSG


###################
# Tests
###################



def test_basic_caching() -> None:
    """Тест базового кэширования"""
    calls: List[int] = []

    def add_one(x: int) -> int:
        calls.append(x)
        return x + 1

    memoized, calls_made = memoize_last(add_one)

    assert memoized(1) == 2
    assert memoized(1) == 2  # из кэша
    assert memoized(2) == 3  # новый вызов
    assert memoized(2) == 3  # из кэша
    assert memoized(1) == 2  # снова вызов (кэш перезаписан)

    assert calls_made() == 3  # реальных вызовов: 1, 2, 1


def test_cache_only_last() -> None:
    """Тест что кэшируется только последний аргумент"""
    calls: List[int] = []

    def square(x: int) -> int:
        calls.append(x)
        return x * x

    memoized, calls_made = memoize_last(square)

    memoized(1)  # вызов
    memoized(2)  # вызов (другой аргумент)
    memoized(1)  # вызов (кэш был перезаписан на 2)

    assert calls_made() == 3
    assert calls == [1, 2, 1]


def test_string_arguments() -> None:
    """Тест с строковыми аргументами"""
    def upper(x: str) -> str:
        return x.upper()

    memoized, calls_made = memoize_last(upper)

    assert memoized("hello") == "HELLO"
    assert memoized("hello") == "HELLO"  # из кэша
    assert memoized("world") == "WORLD"
    assert memoized("world") == "WORLD"  # из кэша

    assert calls_made() == 2


def test_float_arguments() -> None:
    """Тест с float аргументами"""
    def multiply_by_two(x: float) -> float:
        return x * 2.0

    memoized, calls_made = memoize_last(multiply_by_two)

    assert memoized(1.5) == 3.0
    assert memoized(1.5) == 3.0  # из кэша
    assert memoized(2.5) == 5.0
    assert memoized(2.5) == 5.0  # из кэша

    assert calls_made() == 2


def test_tuple_arguments() -> None:
    """Тест с tuple аргументами"""
    def sum_tuple(x: Tuple[int, int]) -> int:
        return x[0] + x[1]

    memoized, calls_made = memoize_last(sum_tuple)

    assert memoized((1, 2)) == 3
    assert memoized((1, 2)) == 3  # из кэша
    assert memoized((3, 4)) == 7
    assert memoized((3, 4)) == 7  # из кэша

    assert calls_made() == 2


def test_none_arguments() -> None:
    """Тест с None аргументом"""
    def process(x: Optional[int]) -> str:
        return f"Processed: {x}"

    memoized, calls_made = memoize_last(process)

    assert memoized(None) == "Processed: None"
    assert memoized(None) == "Processed: None"  # из кэша
    assert memoized(5) == "Processed: 5"
    assert memoized(5) == "Processed: 5"  # из кэша

    assert calls_made() == 2


def test_calls_counter() -> None:
    """Тест счетчика вызовов"""
    def identity(x: int) -> int:
        return x

    memoized, calls_made = memoize_last(identity)

    assert calls_made() == 0

    memoized(1)
    assert calls_made() == 1

    memoized(1)  # из кэша
    assert calls_made() == 1

    memoized(2)
    assert calls_made() == 2

    memoized(2)  # из кэша
    assert calls_made() == 2


def test_stress_random_values() -> None:
    """Стресс-тест со случайными значениями"""
    random.seed(42)

    def expensive_function(x: int) -> int:
        return x * x + 2 * x + 1

    memoized, calls_made = memoize_last(expensive_function)

    # Генерируем последовательность с повторениями
    values: List[int] = [random.randint(1, 1000) for _ in range(1000)]

    for i, val in enumerate(values):
        expected: int = expensive_function(val)
        result: int = memoized(val)
        assert result == expected

        # Каждый второй вызов должен быть из кэша
        if i > 0 and values[i] == values[i-1]:
            assert calls_made() <= i  # не должно быть нового вызова


def test_stress_large_numbers() -> None:
    """Стресс-тест с большими числами до 1_000_000_000_000"""
    random.seed(123)

    def factorial_like(x: int) -> int:
        result: int = 1
        for i in range(1, min(x, 100) + 1):
            result *= i
        return result

    memoized, calls_made = memoize_last(factorial_like)

    # Тест с большими числами
    for _ in range(100):
        val: int = random.randint(1, 1_000_000_000_000)
        expected: int = factorial_like(val)
        result: int = memoized(val)
        assert result == expected

    # Повторяем те же значения (должны быть из кэша)
    for _ in range(100):
        val: int = random.randint(1, 1_000_000_000_000)
        expected: int = factorial_like(val)
        result: int = memoized(val)
        assert result == expected


def test_stress_alternating_values() -> None:
    """Стресс-тест с чередующимися значениями"""
    random.seed(456)

    def compute(x: int) -> int:
        return x ** 3 + x ** 2 + x

    memoized, calls_made = memoize_last(compute)

    # Чередуем два значения
    for _ in range(1000):
        val1: int = random.randint(1, 1000)
        val2: int = random.randint(1001, 2000)

        assert memoized(val1) == compute(val1)
        assert memoized(val2) == compute(val2)
        assert memoized(val1) == compute(val1)  # должен быть вызов (кэш перезаписан)
        assert memoized(val2) == compute(val2)  # должен быть вызов (кэш перезаписан)

    # Проверяем что реальных вызовов было ровно 2 * 1000 * 2 (по 2 на итерацию)
    assert calls_made() == 4000


def test_stress_boundary_values() -> None:
    """Стресс-тест на граничных значениях"""

    def process(x: int) -> int:
        return x * 2

    memoized, calls_made = memoize_last(process)

    # Граничные значения
    boundary_values: List[int] = [
        0,
        1,
        -1,
        1_000_000_000_000,
        -1_000_000_000_000,
        2**31 - 1,  # максимальное int32
        -2**31,     # минимальное int32
        2**63 - 1,  # максимальное int64
        -2**63,     # минимальное int64
    ]

    for val in boundary_values:
        assert memoized(val) == process(val)
        assert memoized(val) == process(val)  # из кэша

    assert calls_made() == len(boundary_values)


def test_stress_mixed_types() -> None:
    """Стресс-тест с разными типами данных"""

    def process(x: Any) -> str:
        return f"Type: {type(x).__name__}, Value: {x}"

    memoized, calls_made = memoize_last(process)

    test_values: List[Any] = [
        1,
        "hello",
        3.14,
        (1, 2, 3),
        [1, 2, 3],
        {"key": "value"},
        None,
        True,
        False,
        1_000_000_000_000,
    ]

    for val in test_values:
        assert memoized(val) == process(val)
        assert memoized(val) == process(val)  # из кэша

    assert calls_made() == len(test_values)


def test_performance() -> None:
    """Тест производительности"""
    import time

    def expensive(x: int) -> int:
        # Имитация дорогой операции
        result: int = 0
        for i in range(1000):
            result += x * i
        return result

    memoized, calls_made = memoize_last(expensive)

    # Первый вызов
    start: float = time.time()
    memoized(42)
    first_call_time: float = time.time() - start

    # Второй вызов (из кэша)
    start = time.time()
    memoized(42)
    cached_call_time: float = time.time() - start

    # Кэшированный вызов должен быть значительно быстрее
    assert cached_call_time < first_call_time / 10, \
        f"Кэшированный вызов должен быть в 10 раз быстрее: first={first_call_time:.4f}, cached={cached_call_time:.4f}"
