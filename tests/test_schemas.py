import pytest
from pydantic import ValidationError

from app.schemas import AnalyzeRequest, Mode


def test_request_trims_message() -> None:
    request = AnalyzeRequest(message="  No puedo iniciar sesión  ", mode=Mode.traditional)

    assert request.message == "No puedo iniciar sesión"


@pytest.mark.parametrize("message", ["", "   "])
def test_request_rejects_empty_or_blank_message(message: str) -> None:
    with pytest.raises(ValidationError):
        AnalyzeRequest(message=message, mode=Mode.traditional)


def test_request_rejects_unsupported_mode() -> None:
    with pytest.raises(ValidationError):
        AnalyzeRequest(message="No puedo acceder", mode="manual")
