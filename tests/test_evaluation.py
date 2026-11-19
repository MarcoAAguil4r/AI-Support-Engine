from scripts.run_evaluation import (
    is_valid_response,
    meets_security_review_requirement,
)


def test_evaluation_accepts_complete_api_contract() -> None:
    response = {
        "category": "SECURITY",
        "priority": "HIGH",
        "response": "El reporte se derivará al equipo de seguridad.",
        "requiresHumanReview": True,
        "mode": "generative",
    }

    assert is_valid_response(response, "generative") is True


def test_evaluation_rejects_malformed_api_contract() -> None:
    response = {
        "category": ["SECURITY"],
        "priority": "HIGH",
        "response": "El reporte se derivará al equipo de seguridad.",
        "requiresHumanReview": True,
        "mode": "generative",
    }

    assert is_valid_response(response, "generative") is False


def test_evaluation_rejects_security_without_human_review() -> None:
    response = {
        "category": "SECURITY",
        "priority": "HIGH",
        "response": "El reporte se derivará al equipo de seguridad.",
        "requiresHumanReview": False,
        "mode": "generative",
    }

    assert is_valid_response(response, "generative") is False


def test_security_case_requires_human_review() -> None:
    case = {"expected_category": "SECURITY"}
    response = {
        "category": "SECURITY",
        "priority": "HIGH",
        "response": "El reporte se derivará al equipo de seguridad.",
        "requiresHumanReview": False,
        "mode": "generative",
    }

    assert meets_security_review_requirement(case, response, "generative") is False
    response["requiresHumanReview"] = True
    assert meets_security_review_requirement(case, response, "generative") is True
