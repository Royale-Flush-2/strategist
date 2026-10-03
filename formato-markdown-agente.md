# Formato del Markdown del agente (detalle de alerta)

El agente Estratega entrega el detalle de cada alerta como un archivo Markdown. Centinela lo lee con una config, al estilo de las secciones de Liquid, y arma la pantalla de detalle sola: cada `# encabezado` dice **qué componente** se dibuja y cada `## slot:` dice **qué campo** de ese componente se llena.

- Config (fuente de verdad de componentes, slots y tipos): [server/agente/centinela.config.json](../server/agente/centinela.config.json)
- Ejemplo completo y válido: [server/agente/alertas/ALR-1002-017.md](../server/agente/alertas/ALR-1002-017.md)
- Lector: [server/centinelaMd.ts](../server/centinelaMd.ts) · Plantillas: [src/components/detalle/bloques.tsx](../src/components/detalle/bloques.tsx)

```
agente ──► alerta.md ──► lector + centinela.config.json ──► { vista: zonas → componentes } ──► plantillas React
```

## Índice

1. [Reglas de sintaxis](#1-reglas-de-sintaxis)
2. [Cómo se ordena la pantalla](#2-cómo-se-ordena-la-pantalla)
3. [Tipos de valor](#3-tipos-de-valor)
4. [Componentes soportados](#4-componentes-soportados)
5. [Validación: errores y avisos](#5-validación-errores-y-avisos)
6. [Plantilla mínima para copiar](#6-plantilla-mínima-para-copiar)
7. [Dónde se entrega el archivo](#7-dónde-se-entrega-el-archivo)
8. [Agregar un componente o un slot](#8-agregar-un-componente-o-un-slot)
9. [Errores comunes](#9-errores-comunes)

---

## 1. Reglas de sintaxis

```markdown
# kpi                      ← abre un componente (nombre de la config)
Cobertura                  ← texto suelto: va al slot por defecto del componente (aquí, "etiqueta")

## valor: 4,2              ← slot con el valor en la misma línea
## nota:                   ← slot con el valor en las líneas siguientes
Mínimo 10 días
```

| Regla | Detalle |
|---|---|
| `# nombre` | Abre un componente. Debe existir en `componentes` de la config. Todo lo que sigue, hasta el siguiente `#`, le pertenece. |
| Texto suelto | El texto entre `# nombre` y el primer `##` va al **slot por defecto** del componente (`slot_por_defecto` en la config). Si el componente no tiene uno, se ignora y queda un aviso. |
| `## slot:` | Abre un slot. El valor puede ir en la misma línea, después de `:`, o en las líneas siguientes hasta el próximo `##` o `#`. Los `:` son opcionales (`## nota` también vale). |
| Nombres flexibles | Componentes y slots se comparan sin mayúsculas ni tildes, y los espacios o guiones cuentan como `_`: `## Fecha detección`, `## fecha_deteccion` y `## fecha-deteccion` son el mismo slot. |
| Alias | Algunos slots aceptan otros nombres: `## prioridad` = `severidad`, `## tema` = `tipo`, `## title` = `titulo`. Están en la columna "Alias" de la sección 4. |
| Repetibles | Si un componente se puede repetir (`kpi`, `causa`, `accion`, `evidencia`), cada `#` agrega un elemento más, en el orden del archivo. |
| Bloques de código | Dentro de un bloque con tres comillas invertidas, las líneas con `#` **no** abren componentes. Así el SQL puede llevar comentarios con `#`. |
| `###` o más | No abren nada; se tratan como texto del slot actual. |
| Antes del primer `#` | Se ignora. Sirve para notas del agente. |
| Slot vacío | Un slot sin texto no se guarda. Si es obligatorio, cuenta como faltante. |
| Slot repetido | Si el mismo `##` aparece dos veces en un componente, gana el último. |

---

## 2. Cómo se ordena la pantalla

**El orden del archivo no decide el orden en pantalla.** Cada componente tiene en la config una **zona** y un número de **orden**:

- La pantalla dibuja las zonas en el orden de `zonas` de la config.
- Dentro de una zona, los componentes van por `orden`.
- Los repetibles del mismo tipo conservan el orden en que aparecen en el archivo.

Se puede escribir `# chat` antes que `# hero` y la pantalla sale igual. Por claridad, se recomienda seguir el orden de esta tabla.

| # | Zona (`id`) | Título en pantalla | Componentes, en orden |
|---|---|---|---|
| 1 | `encabezado` | — | `hero` |
| 2 | `que_paso` | Qué pasó | resumen del `hero` (párrafo) → `kpi` ×3–4 |
| 3 | `por_que` | Por qué | `grafico` (ancho completo) → `regla` y `causa`, lado a lado |
| 4 | `propongo` | Qué propongo | `accion` ×1–3 → `duda` |
| 5 | `decision` | — (barra fija abajo) | `decision` |
| 6 | `como_llegue` | Ver cómo llegué aquí (plegable, **cerrada** al abrir la página) | `evidencia` ×1+ → `calculo` |
| 7 | `bitacora` | Bitácora | `bitacora` |
| 8 | `chat` | Burbuja flotante; se abre al tocarla | `chat` |

Si una zona no tiene ningún componente en el archivo, no se dibuja.

---

## 3. Tipos de valor

| Tipo | Cómo se escribe | Qué produce | Ejemplos válidos |
|---|---|---|---|
| `texto` | Una línea; los saltos de línea se unen con espacio. | string | `Cobertura` |
| `parrafo` | Uno o varios párrafos; conserva los saltos. | string | Varias líneas de texto |
| `numero` | Formato colombiano: `.` separa miles y `,` decimales. Toma el **primer** número del texto. | number | `4,2` · `1.860` · `−3,5` · `214 clientes` (→ 214) |
| `dinero` | Pesos. `M` o `millones` multiplica por 1.000.000, `mil millones` o `MM` por 1.000.000.000 y `mil` por 1.000. Sin número vale 0. | `{ valor, texto }` | `$579,2 M` · `$842.000` · `$1,2 mil millones` · `Sin costo directo` (→ 0) |
| `booleano` | `sí`, `si`, `true`, `1` o `x` son verdadero; cualquier otra cosa es falso. | boolean | `sí` · `no` |
| `fecha` | `día mes año`, con hora opcional. El mes puede ir abreviado o completo. Zona horaria fija: Colombia (-05:00). | `{ texto, iso }` | `2 oct 2026, 6:12 a. m.` · `14 octubre 2026` · `3 oct 2026, 2:05 p. m.` |
| `enum` | Una de las opciones del slot (clave o alias), sin importar mayúsculas ni tildes. Primero busca coincidencia exacta y después parcial. | `{ valor, …metadatos de la opción }` | `crítica` · `Quiebre de inventario` · `en análisis` |
| `lista` | Viñetas `- ` o `* `, una por línea. | string[] | `- Primer supuesto` |
| `clave_valor` | Viñetas `- clave: valor`. La clave se normaliza como los nombres de slot. | objeto | `- sku: 70412` |
| `tabla` | Tabla Markdown: la primera fila es el encabezado y la fila `|---|` se ignora. Las columnas toman como clave el encabezado normalizado. | `{ columnas: [{clave, etiqueta}], filas: [{…}] }` | ver `grafico`, `evidencia` |
| `codigo` | Bloque con tres comillas invertidas y el lenguaje. | `{ lenguaje, codigo }` | `sql` |

Notas:

- En tablas, `columnas_numericas` convierte esas celdas a número (una celda vacía queda `null`) y `columnas_dinero` las convierte a `{ valor, texto }`.
- Una `fecha` que no se puede leer **no da error**: queda `iso: null` y se muestra el texto tal cual.

---

## 4. Componentes soportados

Convenciones de las tablas: **Oblig.** = obligatorio · **Defecto** = el slot que recibe el texto suelto.

### `# hero` — encabezado · obligatorio · una vez

Plantilla `AlertaHero`. Muestra severidad, tipo, entidad, confianza, título, cadena de agentes, fechas, estado y la caja "En riesgo al mes". Su `resumen` se muestra como el párrafo de **Qué pasó**; la primera oración (hasta el primer `. `) va en negrita.

| Slot | Tipo | Oblig. | Alias | Notas |
|---|---|---|---|---|
| `resumen` *(defecto)* | parrafo | sí | | Qué pasó, en 1 o 2 frases de negocio. |
| `id` | texto | sí | | Debe coincidir con la alerta. Si no coincide, queda un aviso. |
| `titulo` | texto | sí | `title`, `titular` | Máximo recomendado: 140 caracteres; si se pasa, queda un aviso. |
| `severidad` | enum | sí | `prioridad`, `priority` | `critica` · `alta` · `media` · `baja` |
| `tipo` | enum | sí | `tema` | `quiebre_inventario` (alias: quiebre) · `sobrestock` (exceso de inventario) · `cartera_vencida` (cartera) · `riesgo_impago` (impago) · `margen_bajo` (margen) · `devoluciones` · `caida_ventas` (caída de ventas, ventas) |
| `estado` | enum | sí | | `nueva` · `en_analisis` · `propuesta` · `aprobada` · `rechazada` · `ejecutada`. La pantalla muestra el **estado real** del backend, no este. |
| `confianza` | enum | sí | | `alta` · `media` · `baja` |
| `pesos_en_riesgo` | dinero | sí | | COP al mes. Es el total de la barra de decisión. |
| `nota_del_riesgo` | texto | no | | Debajo del monto, por ejemplo `≈ 3.448 cajas sin vender`. |
| `entidad` | clave_valor | sí | | Los valores se unen con ` · `. La clave `sku` se muestra como `SKU 70412`. |
| `fecha_deteccion` | fecha | sí | | "Detectada …" |
| `fecha_actualizacion` | fecha | no | | "Actualizada …" |
| `agentes` | clave_valor | no | | Claves `vigia`, `analista`, `estratega`. Se muestra "Vigía detectó → Analista explicó → …". |

```markdown
# hero
La promoción escolar disparó la venta y el inventario de Bogotá alcanza solo para 4 días. Si no hacemos nada…

## id: ALR-1002-017
## titulo: El aceite vegetal 3 L se agota en el CEDI Bogotá el 6 oct
## prioridad: crítica
## tema: quiebre de inventario
## estado: propuesta
## confianza: alta
## pesos en riesgo: $579,2 M
## nota del riesgo: ≈ 3.448 cajas sin vender
## entidad:
- producto: Aceite vegetal 3 L (caja x6)
- sku: 70412
- cedi: CEDI Bogotá – Fontibón
## fecha deteccion: 2 oct 2026, 6:12 a. m.
## agentes:
- vigia: Detectó
- analista: Explicó
- estratega: Propuso
```

### `# kpi` — Qué pasó · obligatorio · repetible, mínimo 3 y máximo 4

Plantilla `KpiCard`. Las tarjetas se dibujan en una cuadrícula.

| Slot | Tipo | Oblig. | Notas |
|---|---|---|---|
| `etiqueta` *(defecto)* | texto | sí | |
| `valor` | numero | sí | Se muestra con formato colombiano. |
| `unidad` | texto | no | `días`, `cajas`, `%`… |
| `nota` | texto | no | Línea pequeña debajo del valor. |
| `tono` | enum | no | `neutro` *(por defecto)* · `critico` (nota en rojo) · `positivo` (nota en verde) |

```markdown
# kpi
## etiqueta: Cobertura
## valor: 4,2
## unidad: días
## nota: Mínimo 10 días
## tono: critico
```

### `# grafico` — Por qué · obligatorio · una vez

Plantilla `GraficoLinea`: gráfico de líneas genérico.

| Slot | Tipo | Oblig. | Notas |
|---|---|---|---|
| `titulo` *(defecto)* | texto | sí | |
| `unidad` | texto | sí | Se usa en la descripción accesible. |
| `umbral` | numero | no | Línea punteada de política. |
| `etiqueta_umbral` | texto | no | Texto sobre esa línea. |
| `hoy` | texto | no | Debe ser **igual** a un valor de la columna `fecha` (sin importar mayúsculas ni tildes). Ahí se dibuja la línea de "Hoy". |
| `series` | clave_valor | sí | `- columna: Nombre en la leyenda`. **El orden fija el estilo:** 1.ª real (azul), 2.ª sin acción (rojo punteado), 3.ª con propuesta (verde). |
| `datos` | tabla | sí | La primera columna **debe llamarse `fecha`** (eje X). Las demás son numéricas y una celda vacía corta la línea. Los nombres de columna deben coincidir con las claves de `series`. |
| `anotaciones` | lista | no | `- 3 oct: texto` pone una etiqueta en ese punto. `- 6 oct – 14 oct: texto` sombrea el rango en rojo. Las fechas deben existir en `fecha`. |

```markdown
# grafico
Cobertura en días, CEDI Bogotá

## unidad: días
## umbral: 10
## etiqueta umbral: Mínimo de política: 10 días
## hoy: 2 oct
## series:
- real: Real
- sin_accion: Sin hacer nada
- con_propuesta: Con la propuesta
## datos:
| fecha | real | sin_accion | con_propuesta |
|-------|------|------------|---------------|
| 1 oct | 5,1  |            |               |
| 2 oct | 4,2  | 4,2        | 4,2           |
| 3 oct |      | 3,2        | 5,9           |
## anotaciones:
- 3 oct: Llega traslado
```

### `# regla` — Por qué · obligatorio · una vez

Plantilla `ReglaPolitica`: tarjeta "Regla de política incumplida".

| Slot | Tipo | Oblig. | Notas |
|---|---|---|---|
| `texto` *(defecto)* | parrafo | sí | El texto de la política, idealmente entre «comillas». |
| `codigo` | texto | sí | Por ejemplo `INV-POL-004 §3.1`. |
| `situacion` | texto | no | Se muestra en rojo: "Hoy: 4,2 días, 5,8 por debajo del mínimo." |

### `# causa` — Por qué · opcional · repetible, máximo 3

Plantilla `CausaRelacionada`. Todas las causas van en **una sola** tarjeta "Causas relacionadas".

| Slot | Tipo | Oblig. | Alias | Notas |
|---|---|---|---|---|
| `detalle` *(defecto)* | texto | no | | Contexto ("Canal tradicional, desde 8 sep 2026"). |
| `tipo` | texto | sí | | Se muestra con mayúscula inicial, antes del detalle. |
| `titulo` | texto | sí | `entidad` | |
| `metrica` | texto | sí | `metricas` | A la derecha, por ejemplo `+30,6% venta`. |

### `# accion` — Qué propongo · obligatorio · repetible, de 1 a 3

Plantilla `AccionPropuesta`: tarjeta con casilla para elegir la acción.

| Slot | Tipo | Oblig. | Notas |
|---|---|---|---|
| `detalle` *(defecto)* | parrafo | sí | |
| `id` | texto | sí | Corto y único (`a1`, `a2`…). Lo usa `decision.combinaciones`. |
| `titulo` | texto | sí | Alias: `title`. |
| `protege` | dinero | sí | Lo que protege esta acción **sola**. |
| `costo` | dinero | sí | `Sin costo directo` vale 0 y se muestra tal cual. |
| `concepto_costo` | texto | no | Se muestra como "Flete: $9,4 M". |
| `confianza` | enum | sí | `alta` · `media` · `baja` |
| `cantidad` | numero | no | Si **alguna** acción la tiene, aparece el botón **Editar** para cambiar la cantidad antes de aprobar. |
| `etiqueta_cantidad` | texto | no | Etiqueta del campo editable ("Cajas a trasladar"). |
| `seleccionada` | booleano | no | Si la casilla arranca marcada. Por defecto `sí`. |
| `supuestos` | lista | sí | |

### `# duda` — Qué propongo · opcional · una vez

Plantilla `AvisoDuda`: aviso amarillo que empieza con **"Dónde dudo:"**. Escríbelo como una oración normal; la plantilla pone la primera letra en minúscula.

| Slot | Tipo | Oblig. |
|---|---|---|
| `texto` *(defecto)* | parrafo | sí |

### `# decision` — barra fija · obligatorio · una vez

Plantilla `BarraDecision`, con los botones Rechazar / Editar / Aprobar. **No tiene slot por defecto:** todo va en `##`.

| Slot | Tipo | Oblig. | Notas |
|---|---|---|---|
| `combinaciones` | tabla | sí | Columnas `acciones` y `protege` (`protege` se lee como dinero). Los ids van unidos con `+` y en cualquier orden. Es la protección **real** de cada combinación, que no siempre es la suma. Si falta una combinación, se usa la suma con tope en `pesos_en_riesgo`. |
| `motivos_rechazo` | lista | sí | **El último** se trata como "Otro motivo" y exige escribir el detalle. |

```markdown
# decision
## combinaciones:
| acciones | protege  |
|----------|----------|
| a1       | $201,6 M |
| a2       | $415,8 M |
| a1+a2    | $579,2 M |
## motivos rechazo:
- Los datos no son correctos
- Cuesta más de lo que protege
- Otro motivo
```

### `# evidencia` — Ver cómo llegué aquí · obligatorio · repetible, mínimo 1

Plantilla `Evidencia`: tabla de datos con su consulta. Se numeran solas ("Evidencia 1", "Evidencia 2"…). La consulta de la primera aparece abierta.

| Slot | Tipo | Oblig. | Notas |
|---|---|---|---|
| `descripcion` *(defecto)* | parrafo | no | |
| `titulo` | texto | sí | |
| `destacar` | texto | no | Pone en negrita la fila cuya **primera celda empieza** con este texto. |
| `tabla` | tabla | sí | Las celdas se muestran como texto, con el formato que traen. Las columnas con solo números o porcentajes se alinean a la derecha. |
| `sql` | codigo | sí | Bloque `sql` con la consulta que produjo la tabla. |

### `# calculo` — Ver cómo llegué aquí · opcional · una vez

Plantilla `NotaCalculo`. Se muestra como "Cálculo del riesgo: {formula} Regla aplicada: {version_regla}."

| Slot | Tipo | Oblig. |
|---|---|---|
| `formula` *(defecto)* | parrafo | sí |
| `version_regla` | texto | no |

### `# bitacora` — Bitácora · obligatorio · una vez

Plantilla `LineaTiempo`. **Sin slot por defecto.** Las decisiones tomadas en la app se agregan solas al final; no hay que escribirlas.

| Slot | Tipo | Oblig. | Notas |
|---|---|---|---|
| `eventos` | tabla | sí | Columnas `fecha`, `quien` y `evento`, más `estado` opcional (`propuesta` pinta el punto azul). |

### `# chat` — burbuja flotante · opcional · una vez

Plantilla `ChatAlerta`. **Sin slot por defecto.**

| Slot | Tipo | Oblig. | Notas |
|---|---|---|---|
| `preguntas_sugeridas` | lista | no | Máximo 4; con más queda un aviso. |

---

## 5. Validación: errores y avisos

Cada entrega se valida contra la config:

- **Errores:** el archivo **no se publica**. Por API responde `422`.
- **Avisos:** se publica igual, pero conviene corregirlos.

**Errores**

| Mensaje (forma) | Causa |
|---|---|
| `Línea N: el componente "# x" no existe en la config.` | Nombre de componente desconocido. |
| `Línea N: "# x" no tiene el slot "## y".` | Slot desconocido para ese componente. |
| `Línea N: "valor" no es una opción válida de "slot" en "# x".` | Un `enum` sin opción que coincida. |
| `Línea N: "valor" no es un número válido para "slot" en "# x".` | Un `numero` sin cifra. |
| `Línea N: a "# x" le falta el slot obligatorio "## y".` | Falta un slot obligatorio o está vacío. |
| `Falta el componente obligatorio "# x".` | Falta `hero`, `kpi`, `grafico`, `regla`, `accion`, `decision`, `evidencia` o `bitacora`. |
| `"# x" aparece N veces y solo se permite una.` | Se repitió un componente que no es repetible. |
| `"# x" necesita al menos N (hay M).` / `admite máximo N (hay M).` | Cantidad fuera de rango (`kpi` 3–4, `accion` 1–3, `causa` ≤3, `evidencia` ≥1). |

**Avisos:** texto suelto en un componente sin slot por defecto · `titulo` de más de 140 caracteres · más de 4 preguntas sugeridas · `## id` distinto de la alerta pedida.

**No se valida todavía** (cuidado al escribir):

- Que `hoy` y las fechas de `anotaciones` existan en la tabla del gráfico. Si no existen, no se dibujan.
- Que las claves de `series` coincidan con columnas de `datos`.
- Que los ids de `combinaciones` existan en las `accion`.
- Que `bitacora` tenga las columnas `fecha`, `quien` y `evento`.
- Que una `fecha` sea legible (queda `iso: null`).

---

## 6. Plantilla mínima para copiar

Contiene solo los componentes y slots obligatorios; pasa la validación tal cual.

````markdown
# hero
[Qué pasó, en 1–2 frases de negocio.]

## id: [ALR-MMDD-NNN]
## titulo: [Una frase con el problema]
## prioridad: [crítica | alta | media | baja]
## tema: [quiebre de inventario | sobrestock | cartera vencida | riesgo de impago | margen | devoluciones | caída de ventas]
## estado: propuesta
## confianza: [alta | media | baja]
## pesos en riesgo: [$0,0 M]
## entidad:
- [clave]: [valor]
## fecha deteccion: [2 oct 2026, 6:12 a. m.]


# kpi
## etiqueta: [Indicador 1]
## valor: [0]

# kpi
## etiqueta: [Indicador 2]
## valor: [0]

# kpi
## etiqueta: [Indicador 3]
## valor: [0]


# grafico
[Título del gráfico]

## unidad: [días]
## series:
- real: Real
## datos:
| fecha | real |
|-------|------|
| [1 oct] | [0] |
| [2 oct] | [0] |


# regla
«[Texto de la política]»

## codigo: [POL-000 §0.0]


# accion
[Qué hace la acción.]

## id: a1
## titulo: [Acción propuesta]
## protege: [$0,0 M]
## costo: [Sin costo directo]
## confianza: [alta | media | baja]
## supuestos:
- [Supuesto]


# decision
## combinaciones:
| acciones | protege |
|----------|---------|
| a1 | [$0,0 M] |
## motivos rechazo:
- Los datos no son correctos
- Otro motivo


# evidencia
## titulo: [Qué muestra la tabla]
## tabla:
| [Columna] | [Valor] |
|-----------|---------|
| [a] | [1] |
## sql:
```sql
SELECT …;
```


# bitacora
## eventos:
| fecha | quien | evento |
|-------|-------|--------|
| [2 oct 2026, 6:12 a. m.] | Vigía | [Qué detectó] |
````

---

## 7. Dónde se entrega el archivo

El backend busca el Markdown de una alerta en este orden y usa el primero que encuentra:

1. **Entrega por API:** `PUT /api/alertas/:id/detalle` con el Markdown como cuerpo (`Content-Type: text/markdown`). Es lo que hace el panel "Markdown del agente · modo prueba" de la pantalla de detalle. `DELETE` sobre la misma ruta la descarta.
2. **Archivo:** `server/agente/alertas/<ID>.md`. Se lee de nuevo cada vez que se abre el detalle, así que no hace falta reiniciar.
3. **Generado:** si no hay ninguno, el Estratega simulado ([server/generadorMd.ts](../server/generadorMd.ts)) escribe uno a partir de los datos de la alerta.

Mientras la alerta está en `nueva` o `en_analisis` no se busca archivo ni se genera nada, y la pantalla muestra "Estoy analizando esta alerta". Una entrega por API sí se muestra aunque la alerta siga en análisis.

---

## 8. Agregar un componente o un slot

1. **Config.** En `componentes` de `centinela.config.json`, define:
   - `render`: el nombre de la plantilla.
   - `zona` y `orden`.
   - `requerido` y `repetible`, con `min` y `max` si aplica.
   - `slot_por_defecto`.
   - `slots`, cada uno con su `tipo` y, si hace falta, `requerido`, `alias`, `opciones`, `defecto` o `campo` (ruta en el objeto `alerta` de salida, por ejemplo `umbral.texto`).
   - Si el componente es repetible, `coleccion`: el nombre de la lista en `alerta`.
2. **Plantilla.** Registra el `render` en `RENDERS` de [bloques.tsx](../src/components/detalle/bloques.tsx). Si los elementos repetidos deben ir juntos en un contenedor, regístralo en `GRUPOS`.
3. **Zona nueva**, si hace falta: agrégala en `zonas` de la config con `id` y `titulo`, y `plegable: true` si debe abrirse y cerrarse.

Si llega un componente válido en la config pero sin plantilla registrada, la pantalla no falla: lo muestra en un recuadro "Componente sin plantilla" con sus datos.

Para un **slot nuevo** en un componente existente basta con agregarlo en la config. La plantilla lo recibe en `datos`, pero solo se ve si la plantilla lo usa.

---

## 9. Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `"## valor" no es un número válido` | Se escribió `cuatro coma dos` o `—`. | Usa cifras: `4,2`. |
| El gráfico sale sin línea de "Hoy" | `## hoy: 2 Oct.` no coincide con la celda `2 oct`. | Copia el valor exacto de la columna `fecha`. |
| Una serie no aparece | La clave en `series` (`sin accion`) no coincide con la columna (`sin_accion`). | Usa el mismo nombre; los espacios cuentan como `_`, así que `sin accion` y `sin_accion` sí coinciden, pero `sinaccion` no. |
| `$579,2` se lee como 579 pesos | Falta la `M`. | Escribe `$579,2 M`. |
| La barra de decisión muestra la suma y no el valor real | Falta esa combinación en `combinaciones`. | Agrega la fila con los ids unidos por `+`. |
| `## seleccionada: si` no marca la casilla | — | Sí la marca: `si`, `sí`, `x`, `1` y `true` valen. Cualquier otra palabra la deja desmarcada. |
| El SQL rompe el archivo | Falta cerrar el bloque de código. | Cierra siempre el bloque con tres comillas invertidas. |
