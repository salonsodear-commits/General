# GUÍA POWER BI DESKTOP — Real vs Presupuesto (PAA)

Guía paso a paso para armar el modelo estrella desde cero. Pensada para alguien que sabe
usar Power BI pero nunca armó un modelo estrella. Los clicks van en **negrita**.

Orden de lectura: primero esta guía (sección A→D), después pegás las medidas de
`MEDIDAS_DAX.md`, y al final armás las páginas (sección E).

---

## A) Conectarse al Excel y entrar a Power Query

1. Abrí Power BI Desktop → **Inicio → Obtener datos → Excel**.
2. Elegí `Real_y_pa_2026v2.xlsx`. Se abre el **Navegador** con la lista de hojas.
3. **NO** marques las hojas ni le des "Cargar". En su lugar, hacé clic en **Transformar
   datos** (abajo a la derecha). Eso abre el **Editor de Power Query**, que es donde vamos a
   trabajar.

   > Si por costumbre ya cargaste alguna hoja, no pasa nada: la borrás después. Lo importante
   > es terminar dentro del Editor de Power Query.

### Crear el parámetro `pRutaArchivo`
4. En el Editor de Power Query → **Inicio → Administrar parámetros → Nuevo parámetro**.
5. Completá:
   - **Nombre:** `pRutaArchivo`
   - **Tipo:** Texto
   - **Valor actual:** la ruta completa, ej. `C:\Reportes\PAA\Real_y_pa_2026v2.xlsx`
6. **Aceptar**. Ya tenés el parámetro que usan todas las consultas.

   > Truco para sacar la ruta exacta: en el Explorador de Windows, clic derecho sobre el
   > archivo → *Copiar como ruta de acceso*, y pegás (quitando las comillas).

### Pegar cada consulta M
7. Para cada consulta de `CONSULTAS_PowerQuery.md`: en el Editor de Power Query →
   **Inicio → Nueva consulta → Consulta nula** (o clic derecho en el panel izquierdo
   *Consultas* → **Nueva consulta → Consulta en blanco**).
8. Con la consulta nueva seleccionada → **Inicio → Editor avanzado**.
9. Borrá todo lo que haya y **pegá el bloque de código** completo. **Aceptar**.
10. **Renombrá** la consulta (panel izquierdo, clic derecho → *Cambiar nombre*) con el
    nombre exacto del título (ej. `_Origen`, `DIM_Vertical`, etc.).

---

## B) Orden de carga y qué NO cargar

Pegá las consultas **en este orden** (cada una depende de las anteriores):

1. `_Origen`
2. `_JessiCruda`
3. `_BaseRealCruda`
4. `DIM_Vertical`
5. `DIM_Cuenta`
6. `DIM_Ceco`
7. `DIM_Proveedor`
8. `DIM_Calendario`
9. `FACT_Presupuesto`
10. `FACT_RealDetalle`
11. `BASE_PLANA_RealvsPA` *(solo si querés la versión express; si no, ni la pegues)*

### Marcar las auxiliares como "No cargar"
Las que empiezan con `_` (y `BASE_PLANA_RealvsPA` si no la usás) no deben ir al modelo:
- Clic derecho sobre la consulta → desmarcá **Habilitar carga** (queda en cursiva).

> Esto evita tablas basura en el modelo y acelera el refresco.

### Verificar tipos antes de cerrar
Hacé clic en cada DIM y FACT y revisá el ícono de tipo en cada encabezado de columna:
- **Fecha** → ícono de calendario (tipo *Fecha*).
- **IDs** (`VerticalID`, `CuentaID`, etc.) → tipo *Número entero* (123).
- **Montos** (`MontoReal`, `MontoPA`) → tipo *Número decimal*.

Si algo está como *Texto* o *Cualquiera*, el código M ya fuerza tipos al final; revisá que
pegaste la consulta completa. Cuando esté todo OK → **Inicio → Cerrar y aplicar**.

---

## C) Refresco mensual (cómo actualizar el mes que viene)

El modelo está pensado para que actualizar sea trivial:

1. Conseguí el Excel nuevo del mes.
2. **Reemplazá** el archivo viejo por el nuevo (mismo nombre y misma carpeta, así no tocás
   el parámetro). Si cambia la ruta, actualizá `pRutaArchivo` (*Transformar datos → Administrar
   parámetros*).
3. En Power BI Desktop → **Inicio → Actualizar**. Listo: dimensiones, IDs y calendario se
   regeneran solos.

### Condiciones que el archivo nuevo DEBE cumplir (si no, se rompe)
- Las hojas se llaman **exactamente** `REAL vs PA 2025 2026` y `Base Real`.
- En la hoja de Jessi, el **encabezado sigue en la fila 3** (filas 1 y 2 vacías).
- Los **nombres de columna no cambian** (`Vertical`, `Cuenta`, `Denominación Cuenta`, `Ceco`,
  `Denominación Rubro`, `mes año`, `Monto Real`, `Monto PA` en Jessi; y `VERTICAL`,
  `Clase de coste`, `Centro de coste`, `Denominacion cuenta contrapartida`, `Valor/mon.inf.`,
  `mes año`, `cuenta ceco`, `Texto` en Base Real).
- `mes año` sigue siendo una fecha (primer día del mes).

> Si te cambian el nombre de una hoja o columna, Power Query avisa con un error que indica
> exactamente qué consulta y qué paso falló — ahí ajustás el nombre en el código M.

---

## D) Crear las RELACIONES (vista Modelo)

Andá a la vista **Modelo** (ícono del costado izquierdo, tercero). Vas a crear las relaciones
arrastrando una columna de una tabla sobre la otra. Para cada una, doble clic sobre la línea
para verificar cardinalidad y dirección.

> Concepto clave: en un modelo estrella, las **dimensiones filtran a los hechos** (uno a varios,
> dirección **única** desde la dimensión hacia la fact). Nunca al revés.

Creá estas relaciones (de dimensión → hecho):

| # | Desde (dimensión) | Hacia (hecho) | Columnas | Cardinalidad | Dirección |
|---|---|---|---|---|---|
| 1 | `DIM_Calendario[Fecha]` | `FACT_Presupuesto[Fecha]` | Fecha = Fecha | 1:* | Única (de dim a fact) |
| 2 | `DIM_Calendario[Fecha]` | `FACT_RealDetalle[Fecha]` | Fecha = Fecha | 1:* | Única |
| 3 | `DIM_Vertical[VerticalID]` | `FACT_Presupuesto[VerticalID]` | ID = ID | 1:* | Única |
| 4 | `DIM_Vertical[VerticalID]` | `FACT_RealDetalle[VerticalID]` | ID = ID | 1:* | Única |
| 5 | `DIM_Cuenta[CuentaID]` | `FACT_Presupuesto[CuentaID]` | ID = ID | 1:* | Única |
| 6 | `DIM_Cuenta[CuentaID]` | `FACT_RealDetalle[CuentaID]` | ID = ID | 1:* | Única |
| 7 | `DIM_Ceco[CecoID]` | `FACT_Presupuesto[CecoID]` | ID = ID | 1:* | Única |
| 8 | `DIM_Ceco[CecoID]` | `FACT_RealDetalle[CecoID]` | ID = ID | 1:* | Única |
| 9 | `DIM_Proveedor[ProveedorID]` | `FACT_RealDetalle[ProveedorID]` | ID = ID | 1:* | Única |

**Cómo crear cada una:** arrastrá la columna de la dimensión (lado "1") sobre la columna del
mismo nombre en la fact (lado "*"). Doble clic en la línea → verificá que diga
*Cardinalidad: Uno a varios (1:*)* y *Dirección del filtro cruzado: Única*.

### Por qué van así
- La dimensión es única (una fila por vertical/cuenta/ceco/proveedor/mes); la fact repite esos
  valores muchas veces → de ahí el **1 a varios**.
- Dirección **única**: queremos que el slicer de la dimensión filtre la fact, no al revés.
  Dejar "ambas" puede generar ambigüedad y resultados raros.

### Lo importante: `DIM_Proveedor` NO se conecta al presupuesto
Solo existe la relación #9, hacia `FACT_RealDetalle`. **No** hay relación de proveedor con
`FACT_Presupuesto` porque el presupuesto no tiene proveedor.

**Qué pasa visualmente cuando filtrás por proveedor:** las medidas de presupuesto
(`[PA Mes]`, `[Variación]`) **quedan en blanco**, porque el filtro de proveedor no llega a
`FACT_Presupuesto`. **Eso es correcto y esperado**: no inventamos presupuesto por proveedor.
El comparativo Real vs PA se mira sin filtrar proveedor; el proveedor es solo para el drill del
Real.

### Marcar el calendario como tabla de fechas
Seleccioná `DIM_Calendario` → pestaña **Herramientas de tabla → Marcar como tabla de fechas** →
elegí la columna **Fecha** → **Aceptar**.

> ¿Para qué sirve? Le dice a Power BI que esa es la tabla oficial de tiempo. Sin esto, las
> funciones de time-intelligence (`DATESYTD`, `SAMEPERIODLASTYEAR`) pueden dar mal o avisar
> error. Con esto marcado, los acumulados y comparaciones interanuales funcionan bien.

> **Después de las relaciones**, creá las medidas de `MEDIDAS_DAX.md`.

---

## E) Diseño de las 3 páginas del reporte

### Página 1 — "Resumen"
Visión ejecutiva. Campos y medidas:
- **4 Tarjetas** (visual *Tarjeta*): `[Real Mes]`, `[PA Mes]`, `[Variación]`, `[Variación %]`.
- **Gráfico de columnas agrupadas**: Eje X = `DIM_Calendario[MesAño]` (ordenado por
  `AñoMesOrden`); Valores = `[Real Mes]` y `[PA Mes]`. Es el Real vs PA por mes.
- **Gráfico de barras**: Eje Y = `DIM_Vertical[Vertical]`; Valores = `[Real Mes]` y `[PA Mes]`.
- **Segmentadores (slicers):** `DIM_Vertical[Vertical]`, `DIM_Cuenta[Rubro]`,
  `DIM_Calendario[MesAño]` (o `Año`).

> Para que `MesAño` se ordene cronológico y no alfabético: seleccioná la columna `MesAño` en la
> vista *Datos* → **Herramientas de columna → Ordenar por columna → `AñoMesOrden`**.

### Página 2 — "Aperturas"
Análisis de desvíos con jerarquía drill-down.
- Visual **Matriz**:
  - **Filas (jerarquía, en este orden):** `DIM_Vertical[Vertical]` → `DIM_Cuenta[Rubro]` →
    `DIM_Cuenta[Cuenta]` (con `DenominacionCuenta`) → `DIM_Ceco[Ceco]`.
  - **Valores:** `[Real Mes]`, `[PA Mes]`, `[Variación]`, `[Variación %]`.
- **Formato condicional en `[Variación]`:** clic en la flecha del valor `Variación` →
  *Formato condicional → Color de fuente* → *Según campo* = `[Color Variación]`
  (la medida del bloque opcional de `MEDIDAS_DAX.md`), o usá una escala de color con rojo en
  los negativos.
- Usá los botones de drill-down de la matriz (las flechas arriba) para bajar
  Vertical → Rubro → Cuenta → Ceco.

### Página 3 — "Detalle Proveedores"
Drill del Real, sin presupuesto.
- Visual **Tabla**: columnas `DIM_Proveedor[Proveedor]`, `DIM_Cuenta[Cuenta]`,
  `DIM_Ceco[Ceco]`, `[Real Detalle]`, `FACT_RealDetalle[Texto]`.

> Acá usás `[Real Detalle]` (transaccional), NO `[Real Mes]`. Y no pongas `[PA Mes]`: a nivel
> proveedor no hay presupuesto.

#### Conectar el drill-through desde la página 2
Queremos que, parado en una Cuenta+Ceco de la matriz, puedas ir al detalle de proveedores de
ese cruce.
1. En la **Página 3**, en el panel *Filtros* hay una zona **"Extraer en detalle"**
   (*Drill through*). Arrastrá ahí `DIM_Cuenta[Cuenta]` y `DIM_Ceco[Ceco]`.
2. Power BI agrega solo un botón de "volver" (flecha) en la página 3.
3. En la **Página 2**, clic derecho sobre una fila de la matriz (a nivel Cuenta o Ceco) →
   **Explorar en profundidad / Drill through → Detalle Proveedores**.
4. Te lleva a la página 3 ya filtrada por esa Cuenta+Ceco, mostrando solo sus proveedores.

> Como el filtro de drill-through es por Cuenta y Ceco (que sí existen en las dos fact), el
> detalle de proveedores queda correctamente acotado al cruce que estabas mirando.

---

## Resumen del flujo
1. Obtener datos → Excel → **Transformar datos**.
2. Crear `pRutaArchivo`.
3. Pegar las 10–11 consultas M en orden; marcar las `_` como no cargar; verificar tipos.
4. Cerrar y aplicar.
5. Crear las 9 relaciones (dim → fact, 1:*, dirección única).
6. Marcar `DIM_Calendario` como tabla de fechas.
7. Crear las medidas DAX.
8. Armar las 3 páginas.
