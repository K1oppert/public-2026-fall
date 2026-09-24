import pytest
import time
from safe_pipeline import safe_pipeline

# ==================== Базовые тесты ====================

def test_normal_execution():
    """Обычное выполнение без ошибок"""
    def add_one(x):
        return x + 1

    def double(x):
        return x * 2

    result = safe_pipeline(add_one)(double)()
    assert result(5) == 12  # double(6) = 12


def test_error_in_first_function():
    """Ошибка в первой функции"""
    def fail(x):
        return None

    def double(x):
        return x * 2

    result = safe_pipeline(fail)(double)()
    assert result(5) is None


def test_error_in_middle_function():
    """Ошибка в середине конвейера"""
    def add_one(x):
        return x + 1

    def fail(x):
        return None

    def double(x):
        return x * 2

    result = safe_pipeline(add_one)(fail)(double)()
    assert result(5) is None


def test_error_in_last_function():
    """Ошибка в последней функции"""
    def add_one(x):
        return x + 1

    def double(x):
        return x * 2

    def fail(x):
        return None

    result = safe_pipeline(add_one)(double)(fail)()
    assert result(5) is None


def test_no_functions_called_after_error():
    """Функции после ошибки не вызываются"""
    calls = []

    def add_one(x):
        calls.append('add_one')
        return x + 1

    def fail(x):
        calls.append('fail')
        return None

    def double(x):
        calls.append('double')  # Не должна быть вызвана
        return x * 2

    result = safe_pipeline(add_one)(fail)(double)()(5)

    assert result is None
    assert calls == ['add_one', 'fail']  # double не вызвана


def test_error_propagates_through_chain():
    """Ошибка распространяется через всю цепочку"""
    def add_one(x):
        return x + 1

    def fail(x):
        return None

    def double(x):
        return x * 2

    def square(x):
        return x ** 2

    result = safe_pipeline(add_one)(fail)(double)(square)()(5)
    assert result is None


# ==================== Тесты с None как валидным значением ====================

def test_none_input():
    """None как входное значение"""
    def process(x):
        if x is None:
            return 0
        return x + 1

    result = safe_pipeline(process)()
    assert result(None) == 0


def test_none_in_middle_with_valid_continuation():
    """None в середине, но следующая функция может обработать"""
    def maybe_fail(x):
        if x < 0:
            return None
        return x + 1

    def handle_none(x):
        if x is None:
            return 0
        return x * 2

    # Сначала ошибка, потом обработка
    result = safe_pipeline(maybe_fail)(handle_none)()
    assert result(-5) is None

    # Без ошибки
    result = safe_pipeline(maybe_fail)(handle_none)()
    assert result(5) == 12  # handle_none(6) = 12


# ==================== Тесты независимости цепочек ====================

def test_independent_chains_with_errors():
    """Независимые цепочки с ошибками"""
    def add_one(x):
        return x + 1

    def fail(x):
        return None

    def double(x):
        return x * 2

    # Цепочка с ошибкой
    chain1 = safe_pipeline(add_one)(fail)(double)

    # Цепочка без ошибки
    chain2 = safe_pipeline(add_one)(double)

    assert chain1()(5) is None
    assert chain2()(5) == 12


def test_branching_with_errors():
    """Ветвление от одной точки с ошибками"""
    def add_one(x):
        return x + 1

    def fail(x):
        return None

    def double(x):
        return x * 2

    base = safe_pipeline(add_one)

    branch1 = base(fail)  # Ошибка
    branch2 = base(double)  # Без ошибки

    assert branch1()(5) is None
    assert branch2()(5) == 12
    assert base()(5) == 6  # База не изменилась


def test_reuse_after_error():
    """Повторное использование после ошибки"""
    def add_one(x):
        return x + 1

    def fail(x):
        return None

    def double(x):
        return x * 2

    chain = safe_pipeline(add_one)(fail)

    # Ошибка
    assert chain()(5) is None

    # Продолжаем цепочку
    extended = chain(double)
    assert extended()(5) is None  # Ошибка сохраняется


# ==================== Тесты с различными типами ====================

def test_error_with_strings():
    """Ошибка со строковыми операциями"""
    def to_upper(s):
        if not isinstance(s, str):
            return None
        return s.upper()

    def add_exclamation(s):
        return s + "!"

    result = safe_pipeline(to_upper)(add_exclamation)()
    assert result("hello") == "HELLO!"
    assert result(123) is None  # Не строка - ошибка


def test_error_with_lists():
    """Ошибка с операциями над списками"""
    def sort_list(lst):
        if not isinstance(lst, list):
            return None
        return sorted(lst)

    def reverse_list(lst):
        return list(reversed(lst))

    result = safe_pipeline(sort_list)(reverse_list)()
    assert result([3, 1, 2]) == [3, 2, 1]
    assert result("not a list") is None


def test_error_with_dicts():
    """Ошибка с операциями над словарями"""
    def get_key(d):
        if not isinstance(d, dict):
            return None
        return d.get('key')

    def double_value(v):
        if v is None:
            return None
        return v * 2

    result = safe_pipeline(get_key)(double_value)()
    assert result({'key': 5}) == 10
    assert result({'other': 5}) is None  # Нет ключа 'key'
    assert result("not dict") is None


# ==================== Стресс-тесты ====================

def test_million_elements_creation():
    """Создание конвейера с миллионом элементов"""
    def add_one(x):
        return x + 1

    start = time.time()

    p = safe_pipeline(add_one)
    for i in range(1_000_000):
        p = p(add_one)

    elapsed = time.time() - start

    assert callable(p)
    print(f"Время создания: {elapsed:.2f} сек")
    assert elapsed < 10.0

def test_million_elements_branching():
    """Ветвление от разных точек миллионного конвейера"""
    def add_one(x):
        return x + 1

    def fail(x):
        return None

    # Создаём базовый конвейер
    base = safe_pipeline(add_one)
    for i in range(500_000):
        base = base(add_one)

    # Ветвимся
    branch1 = base
    branch2 = base

    # Продолжаем каждую ветку
    for i in range(500_000):
        branch1 = branch1(add_one)
        branch2 = branch2(add_one)

    assert callable(branch1)
    assert callable(branch2)
    assert callable(base)

def test_million_elements_no_recursion_error():
    """Создание миллиона элементов без RecursionError"""
    def add_one(x):
        return x + 1

    p = safe_pipeline(add_one)

    try:
        for i in range(1_000_000):
            p = p(add_one)
    except RecursionError:
        pytest.fail("RecursionError при создании конвейера")

    assert callable(p)


def test_million_elements_with_error_functions():
    """Создание миллиона элементов с функциями, которые могут вернуть None"""
    def process(x):
        if x < 0:
            return None
        return x + 1

    start = time.time()

    p = safe_pipeline(process)
    for i in range(1_000_000):
        p = p(process)

    elapsed = time.time() - start

    assert callable(p)
    print(f"Время создания: {elapsed:.2f} сек")
    assert elapsed < 10.0

def test_million_elements_with_mixed_functions():
    """Миллион элементов с разными типами функций"""
    def add_one(x):
        return x + 1

    def double(x):
        return x * 2

    def maybe_fail(x):
        if x > 100:
            return None
        return x + 1

    functions = [add_one, double, maybe_fail]

    start = time.time()

    p = safe_pipeline(functions[0])
    for i in range(1_000_000):
        p = p(functions[i % 3])

    elapsed = time.time() - start

    assert callable(p)
    print(f"Время создания: {elapsed:.2f} сек")
    assert elapsed < 10.0
