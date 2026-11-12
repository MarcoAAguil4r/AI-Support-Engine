import pytest
from fastapi import HTTPException

import app.main as api
from app.generative import ModelProviderError
from app.schemas import AnalyzeRequest, AnalyzeResponse, Category, Mode, Priority


EXPECTED_RESPONSE_FIELDS = {
    "category",
    "priority",
    "response",
    "requiresHumanReview",
    "mode",
}


def test_traditional_endpoint_returns_shared_response_contract() -> None:
    response = api.analyze(
        AnalyzeRequest(message="No puedo iniciar sesión", mode=Mode.traditional)
    )

    assert set(response.model_dump(mode="json")) == EXPECTED_RESPONSE_FIELDS
    assert response.category == Category.ACCESS
    assert response.priority == Priority.MEDIUM
    assert response.response
    assert response.requiresHumanReview is False
    assert response.mode == Mode.traditional


def test_endpoint_dispatches_generative_mode_with_same_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = AnalyzeResponse(
        category=Category.FEATURE,
        priority=Priority.LOW,
        response="Gracias por la sugerencia.",
        requiresHumanReview=False,
        mode=Mode.generative,
    )
    received_messages: list[str] = []

    def fake_generative_engine(message: str) -> AnalyzeResponse:
        received_messages.append(message)
        return expected

    monkeypatch.setattr(api, "analyze_generatively", fake_generative_engine)
    response = api.analyze(
        AnalyzeRequest(message="Agregar exportación", mode=Mode.generative)
    )

    assert received_messages == ["Agregar exportación"]
    assert response == expected
    assert set(response.model_dump(mode="json")) == EXPECTED_RESPONSE_FIELDS


def test_endpoint_maps_provider_failure_to_gateway_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def failing_generative_engine(message: str) -> AnalyzeResponse:
        raise ModelProviderError("Proveedor no disponible.")

    monkeypatch.setattr(api, "analyze_generatively", failing_generative_engine)

    with pytest.raises(HTTPException) as error:
        api.analyze(AnalyzeRequest(message="No puedo entrar", mode=Mode.generative))

    assert error.value.status_code == 502
    assert error.value.detail == "Proveedor no disponible."
