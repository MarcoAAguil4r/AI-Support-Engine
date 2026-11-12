# AI Support Engine

Prototipo del reto práctico: clasifica solicitudes de soporte con un motor de
reglas y un motor generativo real, ambos detrás del contrato `POST /api/analyze`.
La API y los mensajes de respuesta están en español; los valores de categoría,
prioridad y modo siguen el contrato del reto.

## Requisitos

- Python 3.10 o superior
- Git
- Para el modo generativo: Ollama local con un modelo descargado, o un proveedor
  compatible con la API OpenAI Chat Completions

## Preparación y ejecución

Desde la carpeta del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

La aplicación carga las variables de `.env` al iniciar. Edita ese archivo para
ajustar el proveedor; también puedes definir las variables en la terminal que
ejecutará Uvicorn (estas tienen precedencia sobre `.env`):

```powershell
$env:LLM_BASE_URL = "http://localhost:11434/v1"
$env:LLM_MODEL = "llama3.1:8b"
# Para proveedores en la nube: $env:LLM_API_KEY = "..."
uvicorn app.main:app --reload
```

Para Ollama, inicia el servicio y descarga el modelo antes de probar el modo
generativo:

```powershell
ollama pull llama3.1:8b
```

La aplicación no inventa respuestas cuando el modelo no está disponible:
`generative` devuelve HTTP 502 con un error explícito. Para un proveedor en la
nube configura `LLM_BASE_URL`, `LLM_MODEL` y `LLM_API_KEY` como variables de
entorno. No incluyas claves en el código ni en Git.

Verifica el servicio en `http://127.0.0.1:8000/health` y abre la documentación
interactiva en `http://127.0.0.1:8000/docs`.

Ejemplo de petición:

```json
{
  "message": "No puedo iniciar sesión",
  "mode": "traditional"
}
```

`mode` solo acepta `traditional` o `generative`. La respuesta contiene siempre
`category`, `priority`, `response`, `requiresHumanReview` y `mode`.
Todas las solicitudes clasificadas como `SECURITY` requieren revisión humana.
El motor tradicional no usa modelos generativos; el generativo llama al
proveedor configurado y valida el JSON antes de responder.

## Pruebas y comparación

Ejecuta las pruebas unitarias:

```powershell
python -m pytest -q
```

Las pruebas cubren la clasificación y sus prioridades, el contrato de respuesta
compartido por ambos modos y el despacho/los errores del endpoint.

Con el servidor activo y el proveedor generativo configurado, corre la batería
de 10 solicitudes (incluye mensajes ambiguos y dos intentos de inyección de
instrucciones):

```powershell
python scripts/run_evaluation.py
```

El script llama a ambos motores para cada caso, verifica la forma de respuesta,
compara categoría y prioridad con una referencia definida en el código y calcula
el porcentaje de aciertos sobre los 10 casos. Crea evidencia CSV y JSON en
`results/`; revisa los errores y la conclusión automática antes de entregar. La
conclusión debe mantenerse en un máximo de 150 palabras. Los resultados pueden
variar entre proveedores/modelos.

## Repartición para tres integrantes

| Integrante | Responsabilidades | Entregables / aceptación |
|---|---|---|
| 1 Marco — Motor tradicional y contrato | Mantener `app/schemas.py`, `app/traditional.py` y el endpoint compartido en `app/main.py`; acordar categorías, prioridades y respuestas predeterminadas. | Reglas para las cuatro categorías; prioridad y respuesta en cada caso; revisión humana para `SECURITY`; pruebas unitarias. |
| 2 — Integración generativa y seguridad | Implementar y probar `app/generative.py`; configurar Ollama o proveedor compatible; manejar indisponibilidad/salidas inválidas y cuidar secretos e intentos de inyección. | Llamada real al modelo; salida JSON validada contra el contrato; errores explícitos; ninguna credencial en el repositorio. |
| 3 — Comparación, integración y entrega | Mantener `scripts/run_evaluation.py`, ejecutar pruebas de ambos modos, revisar los resultados y actualizar este README con evidencia e instrucciones comprobadas. | Al menos 10 casos; incluye ambigüedad y dos intentos de confundir el sistema; CSV/JSON; porcentajes y conclusión técnica de hasta 150 palabras. |

