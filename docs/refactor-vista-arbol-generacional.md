# refactor-vista-arbol-generacional

## Resumen

Refactorizar la vista web del arbol genealogico para que deje de renderizar grupos familiares independientes y pase a mostrar una estructura ordenada por generaciones. La prioridad es aprender el problema de modelado y presentacion paso a paso, sin introducir todavia una solucion completa ni librerias frontend externas.

## Tareas Detalladas

### 1. Crear la rama de trabajo

- Crear una rama llamada `refactor-vista-arbol-generacional`.
- Mantener esta rama centrada solo en la evolucion de la vista `/nodes/{uuid}`.
- Evitar mezclar en esta rama formularios web, README, migraciones o cambios grandes de modelo.
- Antes de empezar, ejecutar los tests actuales para confirmar el punto de partida.

### 2. Documentar el contrato esperado de `/nodes/{uuid}`

- Definir por escrito que la persona seleccionada es la referencia visual del arbol.
- Confirmar que `depth` controla la expansion desde esa persona.
- Para esta fase, interpretar `depth` en ambas direcciones:
  - hacia arriba: padres, abuelos;
  - hacia abajo: hijos, nietos.
- Definir que `depth=0` debe mostrar solo la persona seleccionada.
- Definir que no se modelaran parejas, matrimonios ni unidades conyugales completas todavia.
- Anadir esta decision como comentario o nota en el documento de trabajo, no necesariamente en codigo.

### 3. Revisar el view model actual

- Analizar `build_tree_view_model` en `app/web/services/tree_view_service.py`.
- Identificar que datos ya vienen de `get_person_tree_service`.
- Separar mentalmente tres conceptos:
  - datos del grafo: nodos y edges;
  - agrupacion familiar: padres e hijos;
  - layout de presentacion: generaciones.
- Confirmar que tests actuales dependen de `PersonTreeViewResponse.family`.
- No eliminar `FamilyGroup` al inicio; conservarlo hasta comprobar si sigue siendo util.

### 4. Disenar una estructura minima de generaciones

- Anadir un concepto de generacion relativa al view model.
- La estructura debe permitir representar:
  - numero de generacion;
  - personas dentro de esa generacion;
  - persona raiz destacable.
- Mantener el diseno sencillo para soportar primero 2 o 3 generaciones.
- Evitar disenar todavia posiciones exactas, coordenadas, anchuras o conectores complejos.
- El objetivo de esta tarea es que la plantilla reciba filas ya ordenadas, no que calcule parentescos.

### 5. Calcular niveles relativos desde la raiz

- Implementar el calculo de generacion dentro del servicio web, no en la plantilla.
- Asignar generacion `0` a la persona seleccionada.
- Asignar generaciones negativas a ancestros.
- Asignar generaciones positivas a descendientes.
- Usar los edges padre -> hijo para decidir si una persona queda arriba o abajo.
- Mantener una estrategia simple para conflictos si una persona se alcanza por mas de un camino.
- Limitar el resultado al `depth` solicitado.

### 6. Ordenar el resultado de forma predecible

- Ordenar las generaciones de menor a mayor:
  - primero abuelos/padres;
  - luego raiz;
  - luego hijos/nietos.
- Ordenar personas dentro de cada generacion con un criterio estable.
- Evitar depender del orden accidental de SQLAlchemy, sets o diccionarios.
- Mantener la ordenacion suficientemente simple para que sea facil de probar.

### 7. Adaptar progresivamente `PersonTreeViewResponse`

- Anadir el nuevo campo de generaciones sin borrar inmediatamente los campos antiguos.
- Actualizar los tests para reflejar el nuevo contrato.
- Mantener compatibilidad temporal con `family` si facilita una migracion gradual de la plantilla.
- Una vez que `nodes.html` use generaciones, decidir si `family` sigue siendo necesario para conectores simples.

### 8. Refactorizar `nodes.html`

- Cambiar la plantilla para iterar principalmente sobre generaciones.
- Renderizar cada generacion como una fila horizontal.
- Mostrar las tarjetas de persona dentro de su generacion correspondiente.
- Destacar visualmente la persona raiz.
- Mantener los enlaces actuales para navegar a otro arbol desde cualquier persona.
- Evitar resolver aun conectores complejos entre ramas; priorizar orden generacional correcto.

### 9. Ajustar el CSS despues del cambio de modelo

- Anadir clases para:
  - contenedor principal del arbol;
  - fila de generacion;
  - tarjeta de persona;
  - tarjeta raiz;
  - ancestros y descendientes si aporta claridad.
- Mantener un diseno legible con flexbox.
- Anadir separacion vertical clara entre generaciones.
- Permitir scroll horizontal si hay muchas personas.
- No intentar que CSS deduzca relaciones familiares que no esten ya preparadas por el view model.

### 10. Anadir tests del nuevo view model

- Actualizar `tests/test_view_tree.py`.
- Cubrir como minimo:
  - persona sin relaciones;
  - raiz con padres;
  - raiz con hijos;
  - abuelos -> padres -> raiz;
  - raiz -> hijos -> nietos;
  - varios hijos en la misma generacion;
  - orden estable de generaciones.
- Verificar explicitamente los valores de generacion esperados.
- Mantener los tests centrados en datos de presentacion, no en HTML ni CSS.

### 11. Revisar los tests existentes

- Ejecutar la suite completa con `uv run pytest tests`.
- Si fallan tests antiguos por el cambio de contrato, actualizarlos solo cuando el nuevo comportamiento sea intencional.
- No cambiar tests de API o servicios de dominio salvo que el cambio afecte realmente a su contrato.
- Confirmar que el endpoint `/nodes/{uuid}` sigue aceptando `depth`.

### 12. Hacer una revision manual en navegador

- Arrancar la aplicacion con `uv run fastapi dev app/main.py`.
- Probar arboles pequenos antes que casos complejos.
- Validar visualmente:
  - `depth=0`;
  - `depth=1`;
  - `depth=2`;
  - persona raiz con padres;
  - persona raiz con hijos;
  - persona raiz con padres e hijos.
- Tomar nota de problemas visuales para una fase posterior, sin bloquear el refactor principal salvo que impidan entender el arbol.

## Fuera De Alcance En Esta Rama

- Formularios web para crear o editar personas.
- Librerias JS de visualizacion.
- Modelo explicito de parejas o matrimonios.
- Coordenadas exactas de nodos.
- Conectores perfectos para arboles anchos o familias complejas.
- Migraciones de base de datos.
- Reescritura completa del sistema de parentescos.

## Criterios De Aceptacion

- `/nodes/{uuid}` muestra la persona seleccionada como referencia.
- Las generaciones aparecen en orden vertical correcto.
- `depth=0` muestra solo la raiz.
- `depth=1` muestra padres e hijos directos si existen.
- `depth=2` muestra abuelos y nietos si existen.
- La plantilla consume una estructura generacional preparada por backend.
- Los tests relevantes cubren el nuevo contrato.
- `uv run pytest tests` pasa.

## Supuestos

- El proyecto sigue priorizando aprendizaje y cambios pequenos.
- Se mantiene la estructura actual FastAPI + Jinja2 + SQLAlchemy.
- El backend web es responsable de preparar el modelo de presentacion.
- La solucion inicial puede ser imperfecta visualmente si el modelo generacional queda claro y probado.
