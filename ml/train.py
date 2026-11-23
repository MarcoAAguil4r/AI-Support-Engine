"""Entrena y prueba un clasificador supervisado de categorías de soporte."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


VALID_CATEGORIES = ("ACCESS", "BUG", "FEATURE", "SECURITY")
TEST_SIZE = 0.2
RANDOM_STATE = 42
DEFAULT_CSV = Path(__file__).resolve().with_name("tickets.csv")


class DatasetValidationError(ValueError):
    """Indica que el CSV no puede utilizarse para entrenar el modelo."""


def load_dataset(csv_path: Path) -> pd.DataFrame:
    """Carga y valida el conjunto de datos antes de dividirlo."""
    try:
        dataset = pd.read_csv(csv_path)
    except FileNotFoundError as exc:
        raise DatasetValidationError(f"No se encontró el archivo CSV: {csv_path}") from exc
    except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise DatasetValidationError(f"No se pudo leer el CSV '{csv_path}': {exc}") from exc

    required_columns = {"message", "category"}
    missing_columns = required_columns.difference(dataset.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise DatasetValidationError(f"El CSV requiere las columnas message y category; falta: {missing}.")

    dataset = dataset.loc[:, ["message", "category"]].copy()
    if dataset["message"].isna().any() or dataset["category"].isna().any():
        raise DatasetValidationError("El CSV contiene mensajes o categorías vacíos.")

    dataset["message"] = dataset["message"].astype(str).str.strip()
    dataset["category"] = dataset["category"].astype(str).str.strip().str.upper()
    if (dataset["message"] == "").any():
        raise DatasetValidationError("El CSV contiene mensajes vacíos o formados solo por espacios.")

    invalid_categories = sorted(set(dataset.loc[~dataset["category"].isin(VALID_CATEGORIES), "category"]))
    if invalid_categories:
        values = ", ".join(invalid_categories)
        raise DatasetValidationError(
            f"El CSV contiene etiquetas inválidas: {values}. "
            f"Use únicamente: {', '.join(VALID_CATEGORIES)}."
        )

    duplicates = dataset.duplicated(subset=["message"], keep=False)
    if duplicates.any():
        examples = "; ".join(dataset.loc[duplicates, "message"].head(3))
        raise DatasetValidationError(f"El CSV contiene mensajes duplicados, por ejemplo: {examples}")

    class_counts = dataset["category"].value_counts()
    missing_categories = [label for label in VALID_CATEGORIES if label not in class_counts]
    if missing_categories:
        raise DatasetValidationError("Faltan categorías para entrenar: " + ", ".join(missing_categories) + ".")
    too_small = class_counts[class_counts < 2]
    if not too_small.empty:
        details = ", ".join(f"{label}={count}" for label, count in too_small.items())
        raise DatasetValidationError(
            "Cada categoría necesita al menos 2 ejemplos para una división estratificada; " + details + "."
        )

    test_count = max(1, int(len(dataset) * TEST_SIZE + 0.999999))
    train_count = len(dataset) - test_count
    category_count = len(class_counts)
    if test_count < category_count or train_count < category_count:
        raise DatasetValidationError(
            "No hay datos suficientes para una división estratificada 80/20: "
            f"entrenamiento={train_count}, prueba={test_count}, categorías={category_count}."
        )
    return dataset


def build_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clasificador TF-IDF de tickets de soporte.")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Ruta al CSV de entrenamiento.")
    parser.add_argument("--message", help="Mensaje que se desea clasificar.")
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    if args.message is not None and not args.message.strip():
        print("Error: --message debe contener texto y no solo espacios.", file=sys.stderr)
        return 2

    try:
        dataset = load_dataset(args.csv)
        x_train, x_test, y_train, y_test = train_test_split(
            dataset["message"],
            dataset["category"],
            test_size=TEST_SIZE,
            stratify=dataset["category"],
            random_state=RANDOM_STATE,
        )
    except DatasetValidationError as exc:
        print(f"Error de datos: {exc}", file=sys.stderr)
        return 2

    model = build_pipeline()
    # El vectorizador y el clasificador se ajustan solo con entrenamiento.
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    print(f"CSV: {args.csv}")
    print(f"Ejemplos de entrenamiento: {len(x_train)}")
    print(f"Ejemplos de prueba: {len(x_test)}")
    print("\nDistribución de entrenamiento:")
    print(y_train.value_counts().reindex(VALID_CATEGORIES, fill_value=0).to_string())
    print("\nDistribución de prueba:")
    print(y_test.value_counts().reindex(VALID_CATEGORIES, fill_value=0).to_string())
    print("\nReporte de clasificación:")
    print(classification_report(y_test, predictions, labels=VALID_CATEGORIES, zero_division=0))
    print(f"Exactitud: {accuracy_score(y_test, predictions):.4f}")
    print("\nMatriz de confusión (filas=real, columnas=predicción):")
    matrix = confusion_matrix(y_test, predictions, labels=VALID_CATEGORIES)
    print(pd.DataFrame(matrix, index=VALID_CATEGORIES, columns=VALID_CATEGORIES).to_string())

    if args.message is not None:
        prediction = model.predict([args.message.strip()])[0]
        print(f"\nPredicción: {prediction}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
