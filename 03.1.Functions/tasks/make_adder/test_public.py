from make_adder import make_adder
import pytest
import time
import testlib

def test_chain_of_three_numbers():
    chain = make_adder()
    assert chain(1)(2)(3)() == 6


def test_empty_chain_is_zero():
    chain = make_adder()
    assert chain() == 0


def test_single_number():
    chain = make_adder()
    assert chain(7)() == 7


def test_different_lengths_and_values():
    assert make_adder()(5)(10)() == 15
    assert make_adder()(-1)(1)(-1)(1)() == 0


def test_independent_chains_do_not_interfere():
    a = make_adder()
    b = make_adder()
    a = a(1)(2)   # цепочка a "продолжена" - a теперь новое замыкание
    b = b(100)
    assert a(3)() == 6      # 1 + 2 + 3, цепочка b её не затронула
    assert b(1)() == 101    # 100 + 1, цепочка a её не затронула


def test_intermediate_steps_are_reusable_independently():
    # a2 и a3 - оба продолжения ОДНОЙ и той же промежуточной точки chain(1)(2);
    # они не должны портить друг друга.
    chain = make_adder()
    mid = chain(1)(2)
    a3 = mid(3)
    a30 = mid(30)
    assert a3() == 6
    assert a30() == 33



# ==================== Базовые тесты ====================

def test_empty_call_returns_zero():
    """Вызов без аргументов возвращает 0"""
    adder = make_adder()
    assert adder() == 0


def test_single_argument():
    """Одно слагаемое"""
    adder = make_adder()
    assert adder(5)() == 5


def test_two_arguments():
    """Два слагаемых"""
    adder = make_adder()
    assert adder(3)(4)() == 7


def test_multiple_arguments():
    """Несколько слагаемых"""
    adder = make_adder()
    assert adder(1)(2)(3)(4)(5)() == 15


def test_negative_numbers():
    """Отрицательные числа"""
    adder = make_adder()
    assert adder(-5)(10)(-3)() == 2


def test_float_numbers():
    """Дробные числа"""
    adder = make_adder()
    assert adder(1.5)(2.25)(0.25)() == 4.0


def test_zero_arguments_in_chain():
    """Нули в цепочке"""
    adder = make_adder()
    assert adder(0)(0)(5)(0)() == 5


# ==================== Тесты независимости ====================

def test_separate_chains_are_independent():
    """Разные цепочки не влияют друг на друга"""
    adder1 = make_adder()
    adder2 = make_adder()

    chain1 = adder1(1)(2)
    chain2 = adder2(10)

    assert chain1() == 3
    assert chain2() == 10
    assert chain1(3)() == 6  # продолжение первой цепочки


def test_branching_from_same_point():
    """Ветвление от одной точки"""
    adder = make_adder()
    base = adder(5)

    branch1 = base(2)
    branch2 = base(3)

    assert branch1() == 7
    assert branch2() == 8
    assert base() == 5  # базовая точка не изменилась


def test_reuse_after_completion():
    """Повторное использование после завершения"""
    adder = make_adder()
    chain = adder(1)(2)

    assert chain() == 3
    # После завершения можно продолжить
    assert chain(3)() == 6
    assert chain() == 3  # но завершённая цепочка сохраняет своё состояние


# ==================== Тесты типизации ====================

def test_returns_callable_for_partial_chain():
    """Незавершённая цепочка возвращает callable"""
    adder = make_adder()
    partial = adder(1)
    assert callable(partial)


def test_returns_int_when_completed():
    """Завершённая цепочка возвращает int"""
    adder = make_adder()
    result = adder(1)()
    assert isinstance(result, int)


def test_type_hints_are_correct():
    """Проверка корректности аннотаций типов"""
    adder = make_adder()
    # Проверяем, что функция возвращает Callable
    assert callable(adder)
    # Проверяем, что результат завершения - число
    result = adder(1)()
    assert isinstance(result, (int, float))


# ==================== Тесты крайних случаев ====================

def test_large_numbers():
    """Большие числа"""
    adder = make_adder()
    assert adder(10**15)(10**15)() == 2 * 10**15


def test_mixed_types():
    """Смешанные типы (int + float)"""
    adder = make_adder()
    assert abs(adder(1)(2.5)(3)() - 6.5 < 0.000001)


def test_zero_length_chain():
    """Пустая цепочка"""
    adder = make_adder()
    assert adder() == 0


def test_single_element_chain():
    """Цепочка из одного элемента"""
    adder = make_adder()
    assert adder(42)() == 42


# ==================== Стресс-тесты ====================

def test_million_arguments():
    """Миллион слагаемых"""
    adder = make_adder()
    chain = adder
    for i in range(1, 1000001):
        chain = chain(i)

    expected = sum(range(1, 1000001))
    assert chain() == expected


def test_million_zeros():
    """Миллион нулей (проверка производительности)"""
    adder = make_adder()
    chain = adder
    for _ in range(1000000):
        chain = chain(0)

    assert chain() == 0


def test_deep_nesting():
    """Глубокая вложенность"""
    adder = make_adder()
    chain = adder
    for i in range(10000):
        chain = chain(i)

    expected = sum(range(10000))
    assert chain() == expected


# ==================== Тесты производительности ====================

def test_million_arguments_time():
    """Время выполнения для миллиона аргументов"""
    adder = make_adder()
    chain = adder
    start = time.time()
    for i in range(1, 1000001):
        chain = chain(i)
    result = chain()
    elapsed = time.time() - start

    assert result == sum(range(1, 1000001))
    # Не должно занимать слишком много времени (обычно < 1 секунды)
    assert elapsed < 5.0


# ==================== Тесты реализации ====================

def test_no_nonlocal_variables():
    """Проверка, что нет nonlocal переменных (по спецификации)"""
    import inspect

    source = inspect.getsource(make_adder)
    assert 'nonlocal' not in source


def test_no_list_accumulation():
    """Проверка, что нет накопления в списке"""
    assert not testlib.is_bytecode_op_used(make_adder, 'BUILD_LIST'), 'Не используйте списки для хранения состояния'
    assert not testlib.is_bytecode_op_used(make_adder, 'LIST_APPEND'), 'Не используйте списки для хранения состояния'
    assert not testlib.is_global_used(make_adder, 'list'), 'Не используйте списки для хранения состояния'


def test_closure_behavior():
    """Проверка поведения замыканий"""
    adder = make_adder()
    chain1 = adder(1)
    chain2 = adder(2)

    # Каждая цепочка имеет своё собственное состояние
    assert chain1() == 1
    assert chain2() == 2

    # Изменение одной не влияет на другую
    chain1(3)
    assert chain2() == 2


# ==================== Дополнительные тесты ====================

def test_chain_continuation_after_completion():
    """Продолжение цепочки после её завершения"""
    adder = make_adder()
    chain = adder(1)(2)

    # Завершаем
    assert chain() == 3

    # Продолжаем с того же места
    continued = chain(4)
    assert continued() == 7
    assert chain() == 3  # оригинал не изменился


def test_multiple_completions():
    """Многократное завершение одной цепочки"""
    adder = make_adder()
    chain = adder(1)(2)

    assert chain() == 3
    assert chain() == 3  # повторный вызов даёт тот же результат
    assert chain() == 3


def test_nested_chains():
    """Вложенные цепочки"""
    adder = make_adder()

    inner = adder(1)(2)  # будет 3
    outer = inner(3)(4)  # будет 10

    assert inner() == 3
    assert outer() == 10


def test_very_large_single_number():
    """Очень большое число в одном вызове"""
    adder = make_adder()
    huge = 10**100
    assert adder(huge)() == huge


def test_combination_of_types():
    """Комбинация различных типов чисел"""
    adder = make_adder()
    assert abs(adder(1)(2.5)(-3)(10**10)() - 10000000000.5) < 0.000001


def test_empty_chain_after_partial():
    """Пустая цепочка после частичной"""
    adder = make_adder()
    chain = adder(5)

    # Вызов без аргументов завершает цепочку
    assert chain() == 5
    # Но можно продолжить
    assert chain(3)() == 8


# ==================== Параметризованные тесты ====================

@pytest.mark.parametrize("args,expected", [
    ((1, 2, 3), 6),
    ((10, 20, 30, 40), 100),
    ((-1, -2, -3), -6),
    ((0, 0, 0), 0),
    ((1.5, 2.5, 3.5), 7.5),
    ((100, -50, 25), 75),
])
def test_parametrized_chains(args, expected):
    """Параметризованные тесты для различных комбинаций"""
    adder = make_adder()
    chain = adder
    for arg in args:
        chain = chain(arg)
    assert chain() == expected


@pytest.mark.parametrize("count,value", [
    (1, 5),
    (10, 3),
    (100, 2),
    (1000, 1),
])
def test_parametrized_repeated_values(count, value):
    """Параметризованные тесты с повторяющимися значениями"""
    adder = make_adder()
    chain = adder
    for _ in range(count):
        chain = chain(value)
    assert chain() == count * value


# ==================== Тесты ошибок ====================

def test_no_arguments_after_completion():
    """Завершённая цепочка не принимает аргументов"""
    adder = make_adder()
    chain = adder(1)(2)
    assert chain() == 3
    # После завершения цепочка остаётся callable
    assert callable(chain)


def test_chain_is_callable():
    """Цепочка всегда callable до завершения"""
    adder = make_adder()
    chain = adder(1)
    assert callable(chain)
    chain = chain(2)
    assert callable(chain)
    chain = chain(3)
    assert callable(chain)


def test_result_is_not_callable():
    """Результат завершения не является callable"""
    adder = make_adder()
    result = adder(1)()
    assert not callable(result)

