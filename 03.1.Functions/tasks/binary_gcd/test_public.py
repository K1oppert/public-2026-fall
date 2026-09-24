import random
import math
from typing import List
from pathlib import Path

import testlib

from binary_gcd import binary_gcd

###################
# Structure asserts
###################


def test_banned_modules() -> None:
    assert not testlib.is_module_imported(
        'math', Path(__file__).parent / 'binary_gcd.py'
    ), 'You should not use `math` module'


###################
# Tests
###################



def test_matches_known_gcd_values() -> None:
    assert binary_gcd(48, 18) == 6
    assert binary_gcd(17, 5) == 1
    assert binary_gcd(270, 192) == 6
    assert binary_gcd(1071, 462) == 21
    assert binary_gcd(123456, 789012) == 12
    assert binary_gcd(999983, 999979) == 1  # два простых числа


def test_zero_edge_cases() -> None:
    assert binary_gcd(0, 5) == 5
    assert binary_gcd(7, 0) == 7
    assert binary_gcd(0, 0) == 0  # особый случай, оба нуля


def test_equal_numbers() -> None:
    assert binary_gcd(9, 9) == 9
    assert binary_gcd(100, 100) == 100
    assert binary_gcd(1, 1) == 1


def test_both_even() -> None:
    assert binary_gcd(48, 18) == 6      # оба чётные на первом шаге
    assert binary_gcd(64, 32) == 32     # степень двойки
    assert binary_gcd(1000, 500) == 500


def test_both_odd() -> None:
    assert binary_gcd(15, 9) == 3       # оба нечётные на первом шаге
    assert binary_gcd(21, 35) == 7
    assert binary_gcd(99, 121) == 11


def test_coprime_numbers() -> None:
    assert binary_gcd(35, 64) == 1
    assert binary_gcd(17, 19) == 1
    assert binary_gcd(101, 103) == 1
    assert binary_gcd(1009, 1013) == 1


def test_powers_of_two() -> None:
    assert binary_gcd(1024, 512) == 512
    assert binary_gcd(1024, 256) == 256
    assert binary_gcd(2**10, 2**5) == 2**5
    assert binary_gcd(2**20, 2**15) == 2**15


def test_large_numbers() -> None:
    assert binary_gcd(1_000_000_000, 1_000_000_000) == 1_000_000_000
    assert binary_gcd(999_999_937, 999_999_929) == 1  # большие простые
    assert binary_gcd(1_000_000_000, 999_999_999) == 1


def test_fibonacci_numbers() -> None:
    # Числа Фибоначчи — худший случай для алгоритма Евклида
    fib: List[int] = [0, 1]
    for i in range(2, 30):
        fib.append(fib[i-1] + fib[i-2])

    for i in range(2, 29):
        assert binary_gcd(fib[i], fib[i+1]) == 1
        assert binary_gcd(fib[i], fib[i]) == fib[i]


def test_random_values_against_math_gcd() -> None:
    """Сравнение с math.gcd для случайных чисел"""
    random.seed(42)
    for _ in range(1000):
        a: int = random.randint(1, 100_000)
        b: int = random.randint(1, 100_000)
        assert binary_gcd(a, b) == math.gcd(a, b)


def test_stress_large_values() -> None:
    """Стресс-тест на значения до 1_000_000_000_000"""
    random.seed(123)
    for _ in range(100):
        a: int = random.randint(1, 1_000_000_000_000)
        b: int = random.randint(1, 1_000_000_000_000)
        assert binary_gcd(a, b) == math.gcd(a, b)


def test_stress_extreme_values() -> None:
    """Стресс-тест на максимальные значения"""
    random.seed(456)
    max_val: int = 1_000_000_000_000

    # Тест с максимальными значениями
    assert binary_gcd(max_val, max_val) == max_val
    assert binary_gcd(max_val, max_val // 2) == max_val // 2
    assert binary_gcd(max_val, max_val - 1) == 1

    # Случайные большие числа
    for _ in range(50):
        a: int = random.randint(max_val // 2, max_val)
        b: int = random.randint(max_val // 2, max_val)
        assert binary_gcd(a, b) == math.gcd(a, b)


def test_stress_prime_numbers() -> None:
    """Стресс-тест с большими простыми числами"""
    # Известные большие простые числа
    primes: List[int] = [
        999_999_937,  # простое
        999_999_929,  # простое
        999_999_893,  # простое
        999_999_883,  # простое
        999_999_797,  # простое
    ]

    for i in range(len(primes)):
        for j in range(i, len(primes)):
            if i == j:
                assert binary_gcd(primes[i], primes[j]) == primes[i]
            else:
                assert binary_gcd(primes[i], primes[j]) == 1


def test_stress_powers_of_two() -> None:
    """Стресс-тест со степенями двойки"""
    for i in range(1, 40):
        for j in range(1, 40):
            assert binary_gcd(2**i, 2**j) == 2**min(i, j)


def test_stress_sequential_numbers() -> None:
    """Стресс-тест с последовательными числами"""
    for i in range(1, 1000):
        assert binary_gcd(i, i + 1) == 1


def test_stress_multiples() -> None:
    """Стресс-тест с кратными числами"""
    random.seed(789)
    for _ in range(100):
        base: int = random.randint(1, 100_000)
        k1: int = random.randint(1, 100)
        k2: int = random.randint(1, 100)
        a: int = base * k1
        b: int = base * k2
        assert binary_gcd(a, b) == base * math.gcd(k1, k2)


def test_stress_alternating_even_odd() -> None:
    """Стресс-тест с чередованием чётных и нечётных"""
    random.seed(101)
    for _ in range(100):
        a: int = random.randint(1, 1_000_000)
        b: int = random.randint(1, 1_000_000)
        # Искусственно делаем одно чётным, другое нечётным
        if a % 2 == 0 and b % 2 == 0:
            b += 1
        elif a % 2 != 0 and b % 2 != 0:
            a += 1
        assert binary_gcd(a, b) == math.gcd(a, b)


def test_stress_boundary_values() -> None:
    """Стресс-тест на граничных значениях"""
    assert binary_gcd(1, 1) == 1
    assert binary_gcd(1, 2) == 1
    assert binary_gcd(2, 1) == 1
    assert binary_gcd(1_000_000_000_000, 1) == 1
    assert binary_gcd(1_000_000_000_000, 2) == 2
    assert binary_gcd(999_999_999_999, 3) == 3  # 999999999999 = 3 * 333333333333


def test_performance_large_values() -> None:
    """Проверка производительности на больших значениях"""
    import time

    start: float = time.time()
    for _ in range(1000):
        binary_gcd(1_000_000_000_000, 999_999_999_999)
    elapsed: float = time.time() - start

    # Не должно занимать больше 2 секунд
    assert elapsed < 2.0, f"Алгоритм слишком медленный: {elapsed:.2f} сек"
