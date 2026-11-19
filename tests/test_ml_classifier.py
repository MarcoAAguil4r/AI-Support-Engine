import pandas as pd
import pytest

from app.ml_classifier import load_tickets, train_and_evaluate
from app.schemas import Category


@pytest.fixture
def tickets() -> pd.DataFrame:
    examples = {
        Category.ACCESS.value: [
            "No puedo iniciar sesión en mi cuenta",
            "Olvidé mi contraseña y no puedo acceder",
            "Mi usuario quedó bloqueado al entrar",
            "Falla el inicio de sesión del portal",
            "Necesito restablecer mi password",
        ],
        Category.BUG.value: [
            "La aplicación muestra un error al guardar",
            "El sistema se cierra al abrir reportes",
            "La página carga muy lento",
            "Aparece una excepción al enviar el formulario",
            "El servicio está caído y no funciona",
        ],
        Category.FEATURE.value: [
            "Quisiera agregar exportación de reportes",
            "Solicito una nueva funcionalidad de búsqueda",
            "Me gustaría incorporar filtros al tablero",
            "Sería útil implementar una opción de descarga",
            "Sugiero añadir una vista de calendario",
        ],
        Category.SECURITY.value: [
            "Encontré una vulnerabilidad en el portal",
            "Hay acceso no autorizado a una cuenta",
            "Detecté un exploit en el servicio web",
            "Se filtraron datos de clientes",
            "La cuenta fue comprometida por phishing",
        ],
    }
    return pd.DataFrame(
        [
            {"message": message, "category": category}
            for category, messages in examples.items()
            for message in messages
        ]
    )


def test_training_produces_report_and_predicts_known_categories(
    tickets: pd.DataFrame,
) -> None:
    result = train_and_evaluate(tickets)

    prediction = result.model.predict(
        ["Encontré una vulnerabilidad y acceso no autorizado"]
    )
    assert prediction[0] in {category.value for category in Category}
    assert "precision" in result.report
    assert "accuracy" in result.report


def test_load_tickets_selects_required_columns(tmp_path) -> None:
    path = tmp_path / "tickets.csv"
    pd.DataFrame(
        {
            "message": ["No puedo acceder"],
            "category": ["ACCESS"],
            "extra": ["ignored"],
        }
    ).to_csv(path, index=False)

    loaded = load_tickets(str(path))

    assert list(loaded.columns) == ["message", "category"]


@pytest.mark.parametrize(
    ("data", "error"),
    [
        (pd.DataFrame({"message": ["texto"]}), "debe incluir las columnas"),
        (
            pd.DataFrame({"message": ["texto"], "category": ["OTHER"]}),
            "Categorías no admitidas",
        ),
        (
            pd.DataFrame(
                {"message": ["uno", "dos"], "category": ["ACCESS", "ACCESS"]}
            ),
            "al menos dos categorías",
        ),
        (
            pd.DataFrame(
                {
                    "message": ["uno", "dos", "tres"],
                    "category": ["ACCESS", "ACCESS", "BUG"],
                }
            ),
            "al menos dos tickets",
        ),
        (
            pd.DataFrame(
                {"message": ["", "texto"], "category": ["ACCESS", "BUG"]}
            ),
            "message no puede estar vacío",
        ),
        (
            pd.DataFrame(
                {"message": ["uno", "dos"], "category": ["ACCESS", None]}
            ),
            "no pueden contener valores vacíos",
        ),
    ],
)
def test_training_rejects_invalid_datasets(
    data: pd.DataFrame, error: str
) -> None:
    with pytest.raises(ValueError, match=error):
        train_and_evaluate(data)


def test_training_rejects_invalid_test_size(tickets: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="test_size"):
        train_and_evaluate(tickets, test_size=1)
