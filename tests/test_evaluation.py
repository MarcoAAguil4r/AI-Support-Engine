from scripts.run_evaluation import is_valid_response


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
