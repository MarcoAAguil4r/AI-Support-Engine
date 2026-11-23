import argparse
from pathlib import Path

from app.ml_classifier import load_tickets, train_and_evaluate

DEFAULT_PREDICTION = "Alguien entró a mi cuenta sin autorización"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Entrena y evalúa un clasificador TF-IDF de tickets."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("tickets.csv"),
        help="CSV etiquetado con las columnas message y category (por defecto: tickets.csv).",
    )
    parser.add_argument(
        "--predict",
        default=DEFAULT_PREDICTION,
        help="Texto de ticket que se clasificará después del entrenamiento.",
    )
    args = parser.parse_args()

    try:
        tickets = load_tickets(str(args.data))
        result = train_and_evaluate(tickets)
    except FileNotFoundError:
        parser.error(
            f"No se encontró {args.data}. Proporciona un CSV etiquetado con "
            "las columnas message y category mediante --data."
        )
    except ValueError as exc:
        parser.error(str(exc))

    print(result.report)
    print("Predicción:")
    print(result.model.predict([args.predict])[0])


if __name__ == "__main__":
    main()
