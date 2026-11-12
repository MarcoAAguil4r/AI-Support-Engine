from fastapi import FastAPI, HTTPException

from app.generative import ModelProviderError, analyze_generatively
from app.schemas import AnalyzeRequest, AnalyzeResponse, Mode
from app.traditional import analyze_traditionally

app = FastAPI(
    title="AI Support Engine",
    description="Clasificacion tradicional y generativa de solicitudes de soporte.",
    version="1.0.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    if request.mode == Mode.traditional:
        return analyze_traditionally(request.message)

    try:
        return analyze_generatively(request.message)
    except ModelProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
