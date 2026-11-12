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

## Crear el repositorio y subir el proyecto

1. Crea un repositorio vacío en GitHub llamado `ai-support-engine`. No agregues
   README, licencia ni `.gitignore` desde GitHub, porque ya están en este
   proyecto.
2. Abre una terminal en esta carpeta y configura Git si aún no lo has hecho:

   ```powershell
   git init
   git branch -M main
   git add .
   git commit -m "Initial AI Support Engine prototype"
   ```

3. Copia la URL HTTPS del repositorio recién creado y enlázala:

   ```powershell
   git remote add origin https://github.com/<organizacion-o-usuario>/ai-support-engine.git
   git push -u origin main
   ```

4. Invita a los otros dos integrantes como colaboradores (o agrégalos al equipo
   de la organización). Cada integrante clona el repositorio y crea una rama
   propia con el formato `feature/<tema>`:

   ```powershell
   git clone https://github.com/<organizacion-o-usuario>/ai-support-engine.git
   cd ai-support-engine
   git switch -c feature/<tema>
   ```

5. Trabajen mediante Pull Requests hacia `main`. Protejan `main` para requerir
   revisión de otro integrante y, si la configuración lo permite, que pasen las
   pruebas. No suban `.env`, claves de API ni datos reales de soporte. Antes de
   entregar, incluyan las evidencias generadas por la evaluación.

## Repartición para tres integrantes

| Integrante | Responsabilidades | Entregables / aceptación |
|---|---|---|
| 1 — Motor tradicional y contrato | Mantener `app/schemas.py`, `app/traditional.py` y el endpoint compartido en `app/main.py`; acordar categorías, prioridades y respuestas predeterminadas. | Reglas para las cuatro categorías; prioridad y respuesta en cada caso; revisión humana para `SECURITY`; pruebas unitarias. |
| 2 — Integración generativa y seguridad | Implementar y probar `app/generative.py`; configurar Ollama o proveedor compatible; manejar indisponibilidad/salidas inválidas y cuidar secretos e intentos de inyección. | Llamada real al modelo; salida JSON validada contra el contrato; errores explícitos; ninguna credencial en el repositorio. |
| 3 — Comparación, integración y entrega | Mantener `scripts/run_evaluation.py`, ejecutar pruebas de ambos modos, revisar los resultados y actualizar este README con evidencia e instrucciones comprobadas. | Al menos 10 casos; incluye ambigüedad y dos intentos de confundir el sistema; CSV/JSON; porcentajes y conclusión técnica de hasta 150 palabras. |

### Coordinación sugerida

- **Inicio (15 min):** los tres revisan el contrato de la API, acuerdan los casos
  de referencia y crean ramas. Integrante 1 comparte pronto los esquemas para que
  2 y 3 puedan avanzar en paralelo.
- **Implementación (60–90 min):** 1 desarrolla las reglas, 2 conecta el modelo y
  3 prepara la batería comparativa, documentación y pruebas de integración.
- **Integración (30–45 min):** revisan Pull Requests, ejecutan `pytest`, inician
  la API y corren la evaluación completa con el modelo real.
- **Cierre (15 min):** confirman que el repositorio no contiene secretos, guardan
  las evidencias solicitadas y cada integrante explica su parte del código.

La persona responsable de integración ayuda a resolver conflictos, pero cada
integrante debe revisar el resultado final y poder explicar el código presentado.
