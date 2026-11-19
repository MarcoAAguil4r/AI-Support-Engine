from dataclasses import dataclass
from math import ceil

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.schemas import Category

REQUIRED_COLUMNS = {"message", "category"}
VALID_CATEGORIES = {category.value for category in Category}


@dataclass(frozen=True)
class TrainingResult:
    model: Pipeline
    report: str


def load_tickets(csv_path: str) -> pd.DataFrame:
    tickets = pd.read_csv(csv_path)
    missing_columns = REQUIRED_COLUMNS - set(tickets.columns)
    if missing_columns:
        raise ValueError(
            "El CSV debe incluir las columnas message y category; "
            f"faltan: {', '.join(sorted(missing_columns))}."
        )
    return tickets.loc[:, ["message", "category"]].copy()


def _validate_tickets(tickets: pd.DataFrame, test_size: float) -> pd.DataFrame:
    if not 0 < test_size < 1:
        raise ValueError("test_size debe ser mayor que 0 y menor que 1.")
    if tickets.empty:
        raise ValueError("El dataset no contiene tickets.")
    missing_columns = REQUIRED_COLUMNS - set(tickets.columns)
    if missing_columns:
        raise ValueError(
            "El dataset debe incluir las columnas message y category; "
            f"faltan: {', '.join(sorted(missing_columns))}."
        )
    if tickets[["message", "category"]].isna().any().any():
        raise ValueError("message y category no pueden contener valores vacíos.")

    normalized = tickets.loc[:, ["message", "category"]].copy()
    normalized["message"] = normalized["message"].astype(str).str.strip()
    normalized["category"] = normalized["category"].astype(str).str.strip().str.upper()
    if normalized["message"].eq("").any():
        raise ValueError("message no puede estar vacío.")

    categories = set(normalized["category"])
    invalid_categories = categories - VALID_CATEGORIES
    if invalid_categories:
        raise ValueError(
            "Categorías no admitidas: "
            f"{', '.join(sorted(invalid_categories))}. "
            f"Usa: {', '.join(sorted(VALID_CATEGORIES))}."
        )
    if len(categories) < 2:
        raise ValueError("El entrenamiento requiere al menos dos categorías.")

    counts = normalized["category"].value_counts()
    undersampled = counts[counts < 2]
    if not undersampled.empty:
        raise ValueError(
            "Cada categoría necesita al menos dos tickets para dividir los datos; "
            f"insuficientes: {', '.join(undersampled.index)}."
        )

    test_count = ceil(len(normalized) * test_size)
    train_count = len(normalized) - test_count
    if test_count < len(categories) or train_count < len(categories):
        raise ValueError(
            "Hay muy pocos tickets para una división estratificada "
            f"{1 - test_size:.0%}/{test_size:.0%} con {len(categories)} categorías."
        )
    return normalized


def train_and_evaluate(
    tickets: pd.DataFrame,
    *,
    test_size: float = 0.2,
    random_state: int = 42,
) -> TrainingResult:
    validated = _validate_tickets(tickets, test_size)
    x_train, x_test, y_train, y_test = train_test_split(
        validated["message"],
        validated["category"],
        test_size=test_size,
        stratify=validated["category"],
        random_state=random_state,
    )

    model = Pipeline(
        [
            ("vectorizer", TfidfVectorizer(ngram_range=(1, 2))),
            ("classifier", LogisticRegression(max_iter=1000, random_state=random_state)),
        ]
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    report = classification_report(
        y_test,
        predictions,
        labels=sorted(VALID_CATEGORIES),
        zero_division=0,
    )
    return TrainingResult(model=model, report=report)
