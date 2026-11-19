# Seguimiento de actividades por integrante

Este documento separa lo que ya está implementado de lo que todavía debe
integrarse, comprobarse y evidenciarse para entregar el reto. No se debe marcar
como terminada una integración generativa hasta probarla con un proveedor real.

## Integrante 1 — Motor tradicional y contrato

**Estado: implementado; pruebas verificadas.**

- Motor de reglas para `ACCESS`, `BUG`, `FEATURE` y `SECURITY`.
- Prioridad `LOW`, `MEDIUM`, `HIGH` o `CRITICAL` y respuestas predeterminadas.
- Contrato común de respuesta y revisión humana para solicitudes `SECURITY`.
- Pruebas del clasificador, contrato HTTP y despacho de modos.

**Verificación actual:** `python -m pytest -q` pasa con 57 pruebas.

## Integrante 2 — Proveedor generativo y seguridad

**Estado: cliente generativo implementado; integración real y evidencia pendientes.**

- [x] Conectar un proveedor compatible con Chat Completions mediante
  `LLM_BASE_URL`, `LLM_MODEL` y `LLM_API_KEY`; Ollama es la configuración local
  documentada.
- [x] Solicitar JSON al modelo y validar categoría, prioridad y respuesta antes
  de devolver el contrato común.
- [x] Devolver un error explícito ante fallos del proveedor o salidas inválidas;
  mantener las credenciales fuera del código y del repositorio.
- [ ] Elegir e iniciar el proveedor/modelo que se usará en la demostración y
  comprobar que `POST /api/analyze` responde en modo `generative` con el modelo
  ejecutándose realmente.
- [x] Añadir pruebas aisladas de la integración generativa, sin depender de un
  modelo en vivo: respuesta válida, JSON inválido, campos/categorías/prioridades
  inválidos, salida vacía, timeout o proveedor inaccesible y configuración
  incorrecta.
- [x] Verificar en pruebas aisladas que las instrucciones del mensaje se envían
  separadas del prompt del sistema y que las señales de seguridad prevalecen
  sobre la categoría del modelo, con `requiresHumanReview: true`.
- [ ] Confirmar con casos adversariales en un proveedor real que las instrucciones
  del mensaje no controlen la clasificación.
- [ ] Guardar evidencia reproducible de una ejecución generativa real, sin
  incluir claves, tokens ni datos sensibles.

**Aceptación:** una ejecución real de la API produce una respuesta estructurada
válida; las pruebas cubren salidas defectuosas y fallas del proveedor sin revelar
secretos.

## Integrante 3 — Comparación, resultados y entrega

**Estado: script y casos de referencia implementados; comparación real pendiente.**

- [x] Preparar 10 solicitudes con categorías y prioridades de referencia,
  incluyendo mensajes ambiguos y dos intentos de confundir al sistema.
- [x] Implementar un script que llama a ambos modos, valida el contrato, registra
  la categoría/prioridad obtenidas y calcula exactitud contra la referencia.
- [x] Verificar que todos los casos etiquetados como `SECURITY` requieran revisión
  humana; el script falla si ese requisito no se cumple.
- [ ] Ejecutar `python scripts/run_evaluation.py` con la API y el proveedor real
  activos; confirmar que los 20 resultados (10 por modo) no tienen errores de
  transporte o proveedor.
- [ ] Revisar cada fila en los artefactos generados en `results/` y guardar el
  CSV y el JSON como evidencia de la ejecución final.
- [ ] Presentar la tabla comparativa con el porcentaje correcto de cada motor y
  redactar una conclusión técnica basada en esos resultados, de máximo 150
  palabras. Revisar la conclusión automática del script antes de usarla.
- [ ] Confirmar que las evidencias incluidas corresponden a la configuración y
  ejecución finales, y que no contienen datos reales de soporte ni secretos.

**Aceptación:** hay evidencia de ambos motores para los mismos 10 casos, el
formato y acierto se pueden revisar por caso, y la conclusión se deriva de la
ejecución real.

## Criterios de cierre del equipo

- [ ] Los tres integrantes pueden explicar el código y las decisiones de su
  parte.
- [x] `python -m pytest -q` pasa (57 pruebas) y la API inicia sin errores.
- [x] Se comprueba `traditional` sin proveedor.
- [ ] Se comprueba `generative` con el proveedor real configurado.
- [ ] El repositorio no incluye `.env`, claves de API, tokens ni datos sensibles.
- [ ] Se adjuntan las evidencias de ejecución y comparación requeridas por el
  reto.
