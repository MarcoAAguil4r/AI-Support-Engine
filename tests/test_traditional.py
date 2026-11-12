import pytest

from app.schemas import Category, Mode, Priority
from app.traditional import analyze_traditionally, classify
from scripts.run_evaluation import CASES


@pytest.mark.parametrize(
    ("message", "expected_category", "expected_priority"),
    [
        ("No puedo iniciar sesión en mi cuenta", Category.ACCESS, Priority.MEDIUM),
        ("La aplicación muestra un error", Category.BUG, Priority.MEDIUM),
        ("Me gustaría agregar exportación a CSV", Category.FEATURE, Priority.LOW),
        ("Encontré una vulnerabilidad en el portal", Category.SECURITY, Priority.HIGH),
        (
            "Ransomware activo con datos expuestos en producción",
            Category.SECURITY,
            Priority.CRITICAL,
        ),
    ],
)
def test_classify_returns_expected_category_and_priority(
    message: str, expected_category: Category, expected_priority: Priority
) -> None:
    assert classify(message) == (expected_category, expected_priority)


def test_security_response_requires_human_review() -> None:
    result = analyze_traditionally("Detecté una vulnerabilidad")

    assert result.category == Category.SECURITY
    assert result.requiresHumanReview is True
    assert result.mode == Mode.traditional
    assert result.response


def test_non_security_response_does_not_require_human_review() -> None:
    result = analyze_traditionally("Quisiera solicitar una nueva funcionalidad")

    assert result.category == Category.FEATURE
    assert result.requiresHumanReview is False


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_evaluation_reference_matches_traditional_rules(case: dict[str, str]) -> None:
    assert classify(case["message"]) == (
        Category(case["expected_category"]),
        Priority(case["expected_priority"]),
    )
