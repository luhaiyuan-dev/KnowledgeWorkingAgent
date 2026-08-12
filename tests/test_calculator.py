import pytest

from app.tools.builtin import SafeCalculator


def test_safe_calculator_handles_arithmetic() -> None:
    calculator = SafeCalculator()
    assert calculator.calculate("(1250 + 860) * 0.13") == pytest.approx(274.3)


@pytest.mark.parametrize(
    "expression", ["__import__('os').system('dir')", "open('a.txt')", "2 ** 1000"]
)
def test_safe_calculator_rejects_unsafe_expressions(expression: str) -> None:
    calculator = SafeCalculator()
    with pytest.raises((ValueError, SyntaxError)):
        calculator.calculate(expression)
