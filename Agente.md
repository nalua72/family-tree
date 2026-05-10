# Contexto Para El Agente

Este fichero mantiene el contexto operativo del proyecto para futuras interacciones.

## Proyecto

`family-tree-api` es una aplicación FastAPI para gestionar un árbol genealógico.

***Muy importante*** La finalidad final del proyecto es aprender sobre diferentes tecnologías de frontend y backend. Quiero que me sugieras cambios y me ayudes con los problemas que encuentre pero NO ME DES CODIGO EXCEPTO QUE LO PIDA EXPLICITAMENTE y NO ESCRIBAS NINGUN FICHERO EXCEPTO QUE LO PIDA EXPLICITAMENTE

El proyecto está en una fase inicial/prototipo funcional. En esta etapa se prioriza avanzar en funcionalidad y aprendizaje antes que cerrar todas las inconsistencias internas entre modelo, schemas y vistas.

## Stack

- Python 3.13
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Jinja2
- pytest
- uv

## Estructura Principal

- `app/main.py`: crea la app FastAPI, registra routers API/web y monta estáticos.
- `app/db/base.py`: engine SQLite, `Base`, modelo `Person` y creación de tablas.
- `app/db/sessions.py`: dependencia `get_db`.
- `app/api/routes/`: endpoints REST.
- `app/services/`: lógica de negocio.
- `app/repositories/`: acceso a datos.
- `app/schemas/`: modelos Pydantic de entrada/salida.
- `app/web/routes/`: rutas HTML.
- `app/web/services/`: preparación de datos para templates.
- `app/web/templates/`: vistas Jinja.
- `app/web/static/`: CSS y estáticos.
- `tests/`: suite de tests.

## Funcionalidad Actual

- CRUD básico de personas vía API.
- Relaciones padre/madre mediante `father_uuid` y `mother_uuid`.
- Validación de UUID.
- Validación de padres existentes.
- Prevención de ciclos al actualizar progenitores.
- Obtención de ancestros.
- Obtención de descendientes.
- Descendientes agrupados por generación.
- Camino más corto entre dos personas.
- Clasificación básica de parentesco: `SELF`, `PARENT`, `CHILD`, `SIBLING`, `UNCLE`, `NEPHEW`, `COUSIN`, etc.
- Árbol familiar por profundidad.
- Interfaz web inicial:
  - listado de personas,
  - detalle de persona,
  - visualización de árbol/nodos familiares.

## Comandos Útiles

Ejecutar tests:

```bash
uv run pytest tests
```

Arrancar servidor de desarrollo:

```bash
uv run fastapi dev app/main.py
```

Alternativa habitual con uvicorn si está disponible:

```bash
uv run uvicorn app.main:app --reload
```

## Estado Actual

- Los últimos cambios web fueron commiteados.
- El usuario ejecutó `uv run pytest tests` y todos los tests pasaron.
- `README.md` todavía está vacío o pendiente de completar.
- Algunas inconsistencias entre modelo SQLAlchemy y schemas Pydantic son aceptables por ahora porque el proyecto sigue en fase inicial.

## Prioridades Recomendadas

1. Seguir construyendo funcionalidad visible en la interfaz web.
2. Añadir formularios web para crear y editar personas.
3. Mejorar navegación entre detalle de persona y árbol.
4. Completar un README mínimo cuando el flujo principal esté más asentado.
5. Más adelante, alinear modelo/schema, configurar DB por entorno y considerar migraciones.

## Criterios De Trabajo

- Mantener cambios pequeños y fáciles de revisar.
- Respetar la estructura actual del proyecto.
- Preferir servicios para lógica de negocio y rutas delgadas.
- Añadir tests cuando se toque lógica de dominio o contratos HTTP.
- No hacer refactors grandes si no desbloquean una necesidad clara.
