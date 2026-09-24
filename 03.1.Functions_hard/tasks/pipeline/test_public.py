from pipeline import pipeline

import pytest
import time
import testlib


def test_three_step_pipeline():
    p = pipeline(lambda x: x + 1)(lambda x: x * 2)(lambda x: x - 3)()
    assert p(5) == 9      # ((5 + 1) * 2) - 3


def test_single_function_pipeline_behaves_like_that_function():
    p = pipeline(lambda x: x * x)()
    assert p(4) == 16
    assert p(-3) == 9


def test_order_of_application_matters():
    # ВАЖНО: сначала f, потом g - а не наоборот
    p = pipeline(lambda x: x - 1)(lambda x: x * 10)()
    assert p(3) == 20      # (3 - 1) * 10, а не (3 * 10) - 1


def test_pipeline_reused_from_intermediate_point_does_not_interfere():
    base = pipeline(lambda x: x + 1)(lambda x: x * 2)   # ещё не завершён

    p_a = base(lambda x: x - 1)()
    p_b = base(lambda x: x + 100)()

    assert p_a(5) == 11     # ((5+1)*2) - 1
    assert p_b(5) == 112    # ((5+1)*2) + 100


def test_functions_are_called_exactly_once_per_pipeline_run():
    calls = []

    def f(x):
        calls.append("f")
        return x + 1

    def g(x):
        calls.append("g")
        return x * 2

    p = pipeline(f)(g)()
    p(1)
    assert calls == ["f", "g"]


# ==================== Базовые тесты ====================

def test_empty_pipeline_returns_function():
    """Пустой конвейер возвращает исходную функцию"""
    def double(x):
        return x * 2

    result = pipeline(double)()
    assert result(5) == 10


def test_single_function():
    """Одна функция в конвейере"""
    def add_one(x):
        return x + 1

    result = pipeline(add_one)()
    assert result(5) == 6


def test_two_functions():
    """Две функции в конвейере"""
    def add_one(x):
        return x + 1

    def double(x):
        return x * 2

    # pipeline(add_one)(double)() = double(add_one(x))
    result = pipeline(add_one)(double)()
    assert result(5) == 12  # double(6) = 12


def test_multiple_functions():
    """Несколько функций в конвейере"""
    def add_one(x):
        return x + 1

    def double(x):
        return x * 2

    def square(x):
        return x ** 2

    # square(double(add_one(x)))
    result = pipeline(add_one)(double)(square)()
    assert result(3) == 64  # square(double(4)) = square(8) = 64


def test_order_of_execution():
    """Порядок выполнения функций"""
    def add_one(x):
        return x + 1

    def double(x):
        return x * 2

    # Проверяем, что функции применяются слева направо
    result = pipeline(add_one)(double)()
    assert result(5) == 12  # double(add_one(5)) = double(6) = 12

    result2 = pipeline(double)(add_one)()
    assert result2(5) == 11  # add_one(double(5)) = add_one(10) = 11


# ==================== Тесты с различными функциями ====================

def test_with_lambda_functions():
    """С лямбда-функциями"""
    result = pipeline(lambda x: x + 1)(lambda x: x * 2)()
    assert result(5) == 12


def test_with_string_operations():
    """С строковыми операциями"""
    def to_upper(s):
        return s.upper()

    def add_exclamation(s):
        return s + "!"

    result = pipeline(to_upper)(add_exclamation)()
    assert result("hello") == "HELLO!"


def test_with_list_operations():
    """С операциями над списками"""
    def sort_list(lst):
        return sorted(lst)

    def reverse_list(lst):
        return list(reversed(lst))

    result = pipeline(sort_list)(reverse_list)()
    assert result([3, 1, 2]) == [3, 2, 1]


def test_with_math_operations():
    """С математическими операциями"""
    import math

    def square(x):
        return x ** 2

    def sqrt(x):
        return math.sqrt(x)

    result = pipeline(square)(sqrt)()
    assert result(16) == 16  # sqrt(256) = 16


# ==================== Тесты независимости ====================

def test_separate_pipelines_are_independent():
    """Разные конвейеры не влияют друг на друга"""
    def add_one(x):
        return x + 1

    def double(x):
        return x * 2

    pipeline1 = pipeline(add_one)(double)
    pipeline2 = pipeline(double)(add_one)

    assert pipeline1()(5) == 12
    assert pipeline2()(5) == 11


def test_branching_from_same_point():
    """Ветвление от одной точки"""
    def add_one(x):
        return x + 1

    def double(x):
        return x * 2

    def square(x):
        return x ** 2

    base = pipeline(add_one)

    branch1 = base(double)
    branch2 = base(square)

    assert branch1()(3) == 8  # double(4) = 8
    assert branch2()(3) == 16  # square(4) = 16
    assert base()(3) == 4  # base не изменился


def test_reuse_after_completion():
    """Повторное использование после завершения"""
    def add_one(x):
        return x + 1

    def double(x):
        return x * 2

    chain = pipeline(add_one)(double)

    # Завершаем
    result = chain()
    assert result(5) == 12

    # Продолжаем с того же места
    extended = chain(lambda x: x + 10)
    assert extended()(5) == 22  # (double(add_one(5))) + 10 = 12 + 10 = 22


# ==================== Тесты типизации ====================

def test_returns_callable_for_partial_chain():
    """Незавершённый конвейер возвращает callable"""
    def add_one(x):
        return x + 1

    partial = pipeline(add_one)
    assert callable(partial)


def test_returns_function_when_completed():
    """Завершённый конвейер возвращает функцию"""
    def add_one(x):
        return x + 1

    result = pipeline(add_one)()
    assert callable(result)
    assert result(5) == 6


def test_composed_function_works():
    """Композиция функций работает корректно"""
    def add_one(x):
        return x + 1

    def double(x):
        return x * 2

    composed = pipeline(add_one)(double)()
    assert composed(10) == 22  # double(11) = 22


# ==================== Тесты крайних случаев ====================

def test_empty_function_list():
    """Пустой список функций"""
    def identity(x):
        return x

    result = pipeline(identity)()
    assert result(42) == 42


def test_single_function_chain():
    """Цепочка из одной функции"""
    def double(x):
        return x * 2

    result = pipeline(double)()
    assert result(21) == 42


def test_many_functions():
    """Много функций в конвейере"""
    def add_one(x):
        return x + 1

    chain = pipeline(add_one)
    for _ in range(100):
        chain = chain(add_one)

    result = chain()
    assert result(0) == 101


def test_identity_functions():
    """Функции-идентичности"""
    def identity(x):
        return x

    result = pipeline(identity)(identity)(identity)()
    assert result(5) == 5


# ==================== Тесты реализации ====================

def test_no_nonlocal_variables():
    """Проверка, что нет nonlocal переменных"""
    import inspect

    source = inspect.getsource(pipeline)
    assert 'nonlocal' not in source


def test_no_list_accumulation():
    """Проверка, что нет накопления в списке"""
    assert not testlib.is_bytecode_op_used(pipeline, 'BUILD_LIST'), 'Не используйте списки для хранения состояния'
    assert not testlib.is_bytecode_op_used(pipeline, 'LIST_APPEND'), 'Не используйте списки для хранения состояния'
    assert not testlib.is_global_used(pipeline, 'list'), 'Не используйте списки для хранения состояния'


def test_closure_behavior():
    """Проверка поведения замыканий"""
    def add_one(x):
        return x + 1

    def double(x):
        return x * 2

    pipeline1 = pipeline(add_one)
    pipeline2 = pipeline(double)

    # Каждый конвейер имеет своё собственное состояние
    assert pipeline1()(5) == 6
    assert pipeline2()(5) == 10

    # Изменение одного не влияет на другой
    pipeline1(double)
    assert pipeline2()(5) == 10


# ==================== Параметризованные тесты ====================

@pytest.mark.parametrize("functions,value,expected", [
    ([lambda x: x + 1], 5, 6),
    ([lambda x: x + 1, lambda x: x * 2], 5, 12),
    ([lambda x: x * 2, lambda x: x + 1], 5, 11),
    ([lambda x: x ** 2, lambda x: x + 1, lambda x: x * 2], 3, 20),
    ([lambda x: x - 1, lambda x: x * 3], 10, 27),
])
def test_parametrized_pipelines(functions, value, expected):
    """Параметризованные тесты для различных комбинаций"""
    chain = pipeline(functions[0])
    for func in functions[1:]:
        chain = chain(func)

    result = chain()
    assert result(value) == expected


@pytest.mark.parametrize("count,value", [
    (1, 5),
    (10, 3),
    (100, 2),
])
def test_parametrized_repeated_functions(count, value):
    """Параметризованные тесты с повторяющимися функциями"""
    def add_one(x):
        return x + 1

    chain = pipeline(add_one)
    for _ in range(count - 1):
        chain = chain(add_one)

    result = chain()
    assert result(value) == value + count


# ==================== Дополнительные тесты ====================

def test_chain_continuation_after_completion():
    """Продолжение конвейера после его завершения"""
    def add_one(x):
        return x + 1

    def double(x):
        return x * 2

    chain = pipeline(add_one)(double)

    # Завершаем
    result = chain()
    assert result(5) == 12

    # Продолжаем с того же места
    continued = chain(lambda x: x + 100)
    assert continued()(5) == 112  # 12 + 100 = 112
    assert result(5) == 12  # оригинал не изменился


def test_multiple_completions():
    """Многократное завершение одного конвейера"""
    def add_one(x):
        return x + 1

    chain = pipeline(add_one)

    result1 = chain()
    result2 = chain()

    assert result1(5) == 6
    assert result2(5) == 6


def test_nested_pipelines():
    """Вложенные конвейеры"""
    def add_one(x):
        return x + 1

    def double(x):
        return x * 2

    inner = pipeline(add_one)(double)  # double(add_one(x))
    outer = inner(lambda x: x + 10)  # (double(add_one(x))) + 10

    assert inner()(5) == 12
    assert outer()(5) == 22


def test_complex_function_composition():
    """Сложная композиция функций"""
    import math

    def square(x):
        return x ** 2

    def sqrt(x):
        return math.sqrt(x)

    def add_one(x):
        return x + 1

    # sqrt(square(add_one(x))) = |x + 1|
    result = pipeline(add_one)(square)(sqrt)()
    assert result(5) == 6  # sqrt(36) = 6
    assert result(-5) == 4  # sqrt(16) = 4


def test_function_with_side_effects():
    """Функции с побочными эффектами"""
    calls = []

    def track(x):
        calls.append(x)
        return x + 1

    result = pipeline(track)(track)()
    result(5)

    assert calls == [5, 6]  # порядок вызовов


def test_error_handling():
    """Обработка ошибок"""
    def divide_by_zero(x):
        return x / 0

    chain = pipeline(divide_by_zero)()

    with pytest.raises(ZeroDivisionError):
        chain(5)


def test_composed_function_reuse():
    """Повторное использование скомпонованной функции"""
    def add_one(x):
        return x + 1

    def double(x):
        return x * 2

    composed = pipeline(add_one)(double)()

    # Функцию можно использовать многократно
    assert composed(1) == 4  # double(2) = 4
    assert composed(2) == 6  # double(3) = 6
    assert composed(3) == 8  # double(4) = 8

def test_million_elements_mixed_types():
    """Миллион элементов с разными типами функций"""
    def add_one(x):
        return x + 1

    def double(x):
        return x * 2

    def square(x):
        return x ** 2

    functions = [add_one, double, square, lambda x: x - 1]

    start = time.time()

    p = pipeline(functions[0])
    for i in range(1_000_000):
        p = p(functions[i % len(functions)])

    elapsed = time.time() - start
    assert callable(p)
    print(f"Миллион смешанных функций за {elapsed:.2f} сек")
