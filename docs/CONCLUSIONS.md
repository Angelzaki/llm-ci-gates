# Conclusiones

## Cuándo bloquear el merge

Bloquear (exit `2`) cuando ocurra cualquiera de estos casos:

1. **`suite.faithfulness` bajo el umbral.** El sistema está generando afirmaciones no sustentadas por el contexto recuperado. Es el riesgo más caro en producción.
2. **`suite.retrieval` bajo el umbral.** Si el retriever no trae el contexto correcto, el resto de la cadena no se puede salvar.
3. **`suite.abstention` bajo el umbral.** El sistema responde cuando debería negarse a responder.
4. **`overall` bajo el umbral**, aunque cada suite individual pase: indica degradación acumulada.
5. **Métrica ausente.** Si una suite deja de reportarse, el check falla; no se interpreta como "sin problemas".

Permitir el merge solo cuando todos los checks pasan. No hay excepciones por promedio: una suite en rojo bloquea aunque `overall` sea alto.

## No bajar umbrales de faithfulness para "poner el CI en verde"

Si un cambio hace caer `suite.faithfulness`, la respuesta correcta es corregir el cambio, no el umbral. Bajar el mínimo para que pase:

- Convierte el gate en un registro de regresiones aceptadas en vez de un control.
- Es difícil de revertir: el nuevo piso pasa a ser la referencia para el siguiente PR.
- Oculta justamente la clase de fallo (alucinación) que el gate existe para detectar.

Reglas prácticas:

- Los umbrales se versionan en Git y cambian por PR separado, con justificación escrita.
- Un cambio de umbral no debe ir en el mismo PR que el código que lo haría fallar.
- Subir un umbral tras una mejora sostenida es válido; bajarlo requiere explicar qué cambió en el conjunto de evaluación, no en el modelo.
- Si el conjunto de evaluación cambia (más casos, más difíciles), recalibrar en un PR dedicado y dejar las cifras antes/después en el mensaje.

## Límites del enfoque

- El gate es tan bueno como las métricas que recibe: un conjunto de evaluación pequeño produce scores con mucho ruido (p. ej. 0.83 = 5/6 en abstención).
- Un umbral único por suite no distingue entre una caída de 0.01 y una de 0.20 más allá del mínimo; para eso sirve comparar contra un baseline (`rag-eval-platform` ya genera `baseline.json`).
- Umbrales justo en el borde generan CI inestable si la evaluación no es determinista. Conviene fijar semillas y versiones del modelo evaluado.

## Siguientes pasos

- Comparación contra baseline con tolerancia de regresión máxima por suite.
- Umbrales por entorno (PR vs. release).
- Publicar la tabla del gate como comentario del PR.
