# Módulo de Machine Learning

Esta herramienta de consola aprende a asignar una categoría a mensajes de soporte:
`ACCESS`, `BUG`, `FEATURE` o `SECURITY`. Usa TF-IDF con unigramas y bigramas y
regresión logística. Es independiente de la API: no modifica `POST /api/analyze`,
sus prioridades ni la revisión humana.

## Archivos

- `tickets.csv`: datos de entrenamiento con las columnas `message` y `category`.
  Contiene 64 ejemplos sintéticos originales en español (16 por categoría); no son
  casos de la evaluación T01–T10.
- `train.py`: valida los datos, divide 80/20 de forma estratificada y entrena el
  pipeline únicamente con el subconjunto de entrenamiento.
- `requirements.txt`: dependencias exclusivas de este módulo.

## Uso en PowerShell

Desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe -m pip install -r ml\requirements.txt
.\.venv\Scripts\python.exe ml\train.py --message "Alguien entró a mi cuenta sin autorización"
```

Para usar otro conjunto de datos, conserve las columnas requeridas y proporcione
su ruta:

```powershell
.\.venv\Scripts\python.exe ml\train.py --csv .\ruta\tickets.csv --message "Quiero modo oscuro"
```

El script muestra cuántos ejemplos quedaron en entrenamiento y prueba, el reporte
de clasificación (precisión, exhaustividad y F1 por categoría), la exactitud y la
matriz de confusión. La matriz usa filas para la categoría real y columnas para la
predicha. Con pocos datos sintéticos, las métricas son una señal de prueba, no una
garantía de rendimiento en producción.

Esta evaluación mide únicamente la categoría. La comparación original en
`scripts/run_evaluation.py` exige que coincidan tanto categoría como prioridad.
