# Plan Para Refactorizar La Vista De Arbol Genealogico

Este documento recoge el plan de trabajo para evolucionar la vista web actual desde grupos familiares separados hacia una visualizacion mas parecida a un arbol genealogico real.

## Problema Actual

La vista actual renderiza grupos de familias independientes. Esto provoca que:

- Familias relacionadas aparezcan separadas visualmente.
- Una familia de hijos pueda aparecer por encima de la familia de sus padres.
- El HTML no tenga suficiente informacion para saber que debe ir arriba, abajo o centrado.
- El CSS tenga que intentar resolver un problema que realmente pertenece al modelo de presentacion.

La causa principal no parece ser solo CSS. El problema esta en que el view model actual representa "familias encontradas", pero no representa todavia un "arbol ordenado por generaciones".

## Objetivo

Construir una vista en la que:

- Los ancestros aparezcan arriba.
- La persona seleccionada aparezca como punto de referencia.
- Los descendientes aparezcan abajo.
- Las generaciones esten claramente separadas.
- Las conexiones padre/madre -> hijos sean consistentes.
- El template reciba una estructura ya preparada para pintar el arbol.

## Decision Inicial Recomendada

Antes de refactorizar, definir el comportamiento esperado de `/nodes/{uuid}`:

- La persona seleccionada debe ser la raiz visual o punto central.
- `depth` deberia controlar cuantos niveles familiares se expanden desde esa persona.
- En una primera fase, `depth` puede expandir en ambas direcciones:
  - padres, abuelos, etc.
  - hijos, nietos, etc.
- No conviene modelar conyuges o matrimonios todavia si el dominio solo tiene padre/madre e hijos.

## Plan De Tareas

### 1. Separar Datos Del Arbol Y Layout Del Arbol

Actualmente existen nodos y edges, y despues se agrupan en `FamilyGroup`. Para renderizar un arbol hace falta una capa adicional de presentacion.

Conceptos utiles:

- `TreeNode`: persona.
- `TreeEdge`: conexion padre -> hijo.
- `GenerationLevel`: personas de una misma generacion relativa.
- `FamilyUnit`: progenitores + hijos.

El objetivo es que el backend web no solo diga "estas familias existen", sino tambien "esta persona/grupo va en este nivel".

### 2. Calcular Generaciones Relativas

Asignar a cada persona alcanzable desde la raiz un nivel relativo:

- raiz: `0`
- padres: `-1`
- abuelos: `-2`
- hijos: `+1`
- nietos: `+2`
- hermanos: normalmente `0`
- tios: normalmente `-1`
- sobrinos: normalmente `+1`

Este paso es clave. Sin niveles relativos, el template no puede ordenar correctamente el arbol.

### 3. Evolucionar El View Model

El modelo actual `PersonTreeViewResponse` puede evolucionar desde una lista simple de familias hacia una estructura renderizable por generaciones.

Ideas de datos que puede incluir:

- Persona raiz.
- Lista de generaciones ordenadas.
- Familias con generacion asociada.
- Nodos por id.
- Edges padre -> hijo.

No hace falta definir el modelo perfecto desde el principio. Basta con que ayude a pintar correctamente 2 o 3 generaciones.

### 4. Revisar La Agrupacion Familiar

`FamilyGroup(parents, children)` sigue siendo util, pero necesita contexto:

- generacion de los padres,
- generacion de los hijos,
- relacion con la raiz,
- orden relativo dentro de su nivel.

Esto evita que el orden de iteracion produzca familias visualmente desordenadas.

### 5. Renderizar Por Generaciones En El Template

En lugar de iterar directamente sobre todas las familias, `nodes.html` deberia pintar filas generacionales:

- generacion -2: abuelos,
- generacion -1: padres,
- generacion 0: raiz y/o hermanos,
- generacion +1: hijos,
- generacion +2: nietos.

Cada generacion seria una fila horizontal. Esto ya corregiria gran parte del problema visual.

### 6. Resolver Primero Casos Simples

No intentar resolver todos los casos genealogicos complejos al principio.

Casos iniciales recomendados:

- Persona sin padres ni hijos.
- Dos progenitores y un hijo.
- Dos progenitores y varios hijos.
- Abuelos -> padres -> hijos.
- Persona raiz con hijos y nietos.

Cuando esos casos funcionen, avanzar hacia hermanos, tios, primos y ramas mas anchas.

### 7. Mejorar CSS Despues Del Modelo

Cuando el view model ya tenga generaciones, mejorar la visualizacion:

- filas con `display: flex`,
- tarjetas centradas,
- raiz destacada,
- conectores verticales y horizontales,
- separacion clara entre ramas,
- scroll horizontal si el arbol crece.

El CSS debe encargarse de presentar una estructura correcta, no de inferir el arbol.

### 8. Anadir Tests Del View Model

Priorizar tests sobre la logica que prepara el arbol, no sobre el CSS.

Tests utiles:

- La raiz queda en generacion `0`.
- Padres quedan en `-1`.
- Abuelos quedan en `-2`.
- Hijos quedan en `+1`.
- Nietos quedan en `+2`.
- Familias relacionadas se devuelven en orden predecible.

## Orden Recomendado

1. Definir comportamiento exacto de `depth`.
2. Crear o adaptar un view model orientado a generaciones.
3. Refactorizar `build_tree_view_model` para calcular niveles relativos.
4. Adaptar `nodes.html` para renderizar filas generacionales.
5. Anadir tests del nuevo view model.
6. Mejorar CSS y conectores.
7. Evaluar mas adelante si merece la pena usar una libreria JS.

## Posibles Librerias Futuras

Para aprender frontend mas avanzado, mas adelante se podria comparar la solucion propia con:

- D3.js
- Cytoscape.js
- React Flow

Pero en esta fase es recomendable seguir con HTML/CSS/Jinja para entender bien el problema de layout y el modelo de datos.

## Criterio Principal

El siguiente cambio importante no deberia ser "hacer mejor CSS", sino redisenar el modelo que recibe la plantilla.

La vista necesita pasar de "familias encontradas" a "arbol renderizable por generaciones".
