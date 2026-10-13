from decimal import Decimal

import pytest

from app.tools.calc import CalcError, evaluate, round_to


def test_exact_decimal_arithmetic():
    assert evaluate("0.1 + 0.2") == Decimal("0.3")
    assert evaluate("(3*12500000 + 2*8750000) * 1.1") == Decimal("60500000.0")
    assert evaluate("-(2 - 5) / 3") == Decimal("1")


def test_budget_rounding_to_thousand():
    total = evaluate("(2*3*1800000 + 2*149*26180*1.08 + 1250000) * 1.1")
    assert round_to(total, 1000) == Decimal("22523000")


@pytest.mark.parametrize("expression", [
    "__import__('os').system('dir')", "open('x')", "a + 1", "2 ** 10", "'1' + '2'", "True + 1", "[1, 2]",
    "0x10", "0o17", "0b101", "1e999999 * 10", 5, None,
])
def test_rejects_anything_but_arithmetic(expression):
    with pytest.raises(CalcError):
        evaluate(expression)


def test_division_by_zero_is_calc_error():
    with pytest.raises(CalcError):
        evaluate("1 / 0")


def test_literals_keep_full_precision_and_no_negative_zero():
    assert evaluate("10000000000000001.5") == Decimal("10000000000000001.5")
    assert evaluate("12345678901234567890.25 - 12345678901234567890") == Decimal("0.25")
    assert str(evaluate("0 * -5")) == "0"
    assert evaluate("1_000 + 1e3") == Decimal("2000")
