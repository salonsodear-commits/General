# GUÍA MAESTRA — De GitHub a Power BI funcionando
## Real vs Presupuesto (PAA) — Operaciones Complejas

> Guía práctica y educativa. Cada paso explica qué hacés, dónde hacés clic, qué debería
> ocurrir, cómo validar, qué hacer si algo falla, **y por qué existe cada cosa**.
>
> Punto de partida: tenés GitHub abierto, Power BI Desktop instalado y el Excel de origen.
> Objetivo final: dashboard `.pbix` funcionando y entendido.

---

# ANTES DE EMPEZAR — Entendé qué construimos y por qué

## El problema de negocio

Cada mes necesitás comparar lo que **realmente se gastó** (Real) contra lo que estaba
**presupuestado** (PA/PAA) para las tres verticales de Operaciones Complejas (Petróleo,
Minería, Otras). Además, cuando un desvío te llama la atención, necesitás poder bajar al
detalle y ver **qué proveedor generó ese gasto**.

El Excel fuente (`Real_y_pa_2026v2.xlsx`) tiene dos hojas:
- **"REAL vs PA 2025 2026"**: tabla armada a mano con los montos agregados de Real y PA por
  Vertical + Cuenta + Ceco + Mes. Tiene presupuesto. NO tiene proveedor.
- **"Base Real"**: detalle transaccional de cada asiento contable. Tiene proveedor. NO tiene
  presupuesto.

## Qué generé en el repositorio

Un **proyecto Power BI completo** (formato PBIP — Power BI Project) con:
- El modelo de datos construido (7 tablas, 9 relaciones, 12 medidas).
- 5 páginas de reporte con visuales.
- Todo el código M de Power Query y las fórmulas DAX implementadas.

Solo te falta abrirlo, apuntarle al Excel y actualizar.

## La arquitectura en una imagen

```
Real_y_pa_2026v2.xlsx
│
├── Hoja "REAL vs PA 2025 2026"  ────►  stgRealPA (staging, no cargada)
│                                              │
└── Hoja "Base Real"             ────►  stgBaseRealCruda (staging, no cargada)
                                               │
                      ┌────────────────────────┼──────────────────────────┐
                      ▼                        ▼                          ▼
              DIM_Vertical            DIM_Cuenta                    DIM_Ceco
              DIM_Proveedor           DIM_Calendario
                      │                        │
              ┌───────┴────────┐     ┌─────────┴──────────┐
              ▼                ▼     ▼                     ▼
    FACT_Presupuesto    FACT_RealDetalle
    (Real + PA, sin     (Real con proveedor,
     proveedor)          sin PA)
              │                │
              └───────┬────────┘
                      ▼
              12 medidas DAX
                      │
                      ▼
              5 páginas del reporte
```

---

# APARTADO ESPECIAL — El modelo estrella explicado desde cero

## ¿Qué es un modelo estrella?

Es una forma de organizar los datos en Power BI (y en cualquier herramienta de BI) que
separa **lo que se mide** (tablas de hechos) de **cómo se clasifica** (tablas de dimensiones).

**Tablas de hechos (FACT):** contienen los números que te importan — montos, cantidades.
Tienen muchas filas (una por cada combinación de fecha + cuenta + ceco + etc.).
**Tablas de dimensiones (DIM):** contienen las etiquetas y categorías — nombres de verticales,
cuentas, cecos, proveedores, fechas. Tienen pocas filas (una por cada entidad única).

En lugar de tener una sola tabla gigante con todo mezclado (lo que haría que los cálculos
sean lentos y propensos a errores), el modelo estrella conecta las dimensiones con las facts
a través de IDs numéricos. Los slicers y filtros del reporte actúan sobre las dimensiones, y
Power BI propaga esos filtros automáticamente hacia los hechos.

## Las 7 tablas del modelo y su función

### Tablas de dimensiones (5)

**`DIM_Vertical`** — La lista de las 3 verticales del negocio.
- Columnas: `VerticalID` (número entero, clave), `Vertical` (texto: PETROLEO / MINERIA /
  OTRAS OPERACIONES DEDICADAS).
- Origen: `CONSULTAS_PowerQuery.md` → sección "DIM_Vertical".
- Por qué existe: para que el slicer de "Vertical" en el reporte filtre tanto el presupuesto
  como el real de forma consistente.

**`DIM_Cuenta`** — El catálogo de cuentas contables con su denominación y rubro.
- Columnas: `CuentaID`, `Cuenta` (código ej. 5110002), `DenominacionCuenta` (ej. "CO-
  COMEDOR/REFRI"), `Rubro` (ej. "BENEFICIOS AL PERSONAL"). Son 13 rubros, 58 cuentas.
- Origen: `CONSULTAS_PowerQuery.md` → sección "DIM_Cuenta".
- Por qué existe: agrupa las cuentas por rubro, lo que permite la jerarquía Rubro → Cuenta
  en la matriz de aperturas.

**`DIM_Ceco`** — La lista de centros de costo ("secos").
- Columnas: `CecoID`, `Ceco` (código ej. CNON11901A). Son 63 cecos únicos.
- Origen: `CONSULTAS_PowerQuery.md` → sección "DIM_Ceco".
- Por qué existe: el análisis por ceco es uno de los ejes principales del control de gestión.

**`DIM_Proveedor`** — Los 499 proveedores únicos del período 2025+.
- Columnas: `ProveedorID`, `Proveedor` (nombre en mayúsculas).
- Origen: `CONSULTAS_PowerQuery.md` → sección "DIM_Proveedor".
- Por qué existe: permite el drill-down de gastos por proveedor. **Solo se conecta al Real
  transaccional, nunca al presupuesto** — porque el presupuesto no tiene apertura por
  proveedor.

**`DIM_Calendario`** — El calendario mensual continuo de enero 2025 a diciembre 2026.
- Columnas: `Fecha`, `Año`, `NroMes`, `NombreMes`, `MesAño` (texto "Ene-25"), `AñoMesOrden`
  (número 202501 para ordenar correctamente).
- Origen: `CONSULTAS_PowerQuery.md` → sección "DIM_Calendario". Generada con código M, no
  importada.
- Por qué existe: es la dimensión de tiempo. Las funciones de acumulados (YTD) e
  interanuales (año anterior) en DAX requieren una tabla de fechas dedicada.

### Tablas de hechos (2)

**`FACT_Presupuesto`** — El corazón del comparativo Real vs PA.
- Columnas: `Fecha`, `VerticalID`, `CuentaID`, `CecoID`, `MontoReal`, `MontoPA`.
- Grano: una fila por cada combinación de Vertical + Cuenta + Ceco + Mes. 5.184 filas.
- Origen: hoja "REAL vs PA 2025 2026" del Excel, procesada en `CONSULTAS_PowerQuery.md`.
- Por qué existe: es la única tabla que tiene tanto Real como PA en la misma fila, al mismo
  nivel de detalle. Todas las medidas de comparación (Variación, Var%, Acumulados) se calculan
  sobre esta tabla.
- **No tiene proveedor** — eso es intencional y correcto.

**`FACT_RealDetalle`** — El detalle transaccional para drill de proveedores.
- Columnas: `Fecha`, `VerticalID`, `CuentaID`, `CecoID`, `ProveedorID`, `MontoReal`, `Texto`.
- Grano: una fila por asiento contable. 30.070 filas (filtradas a 2025+).
- Origen: hoja "Base Real" del Excel, procesada en `CONSULTAS_PowerQuery.md`.
- Por qué existe: es la única tabla que tiene el detalle por proveedor. Se usa exclusivamente
  en la página "Drill Through — Proveedores".
- **No tiene PA** — tampoco tiene con qué: el presupuesto no se distribuye por proveedor.

### Por qué DOS tablas de hechos y no una sola

Si mezcláramos todo en una tabla, tendríamos que elegir entre dos opciones malas: (a) poner
el PA en cada fila del detalle transaccional → el total de PA se multiplicaría por la cantidad
de proveedores, dando números incorrectos; o (b) dejar el PA en blanco en las filas de detalle
→ perdemos el comparativo. La solución correcta es **dos hechos a distinto grano**
compartiendo las mismas dimensiones. Definido en `GUIA_PowerBI.md` → sección D y en
`CONSULTAS_PowerQuery.md` → sección "¿Por qué DOS tablas de hechos?".

## Las 9 relaciones

Todas son **uno a varios (1:*)** con **dirección única** (la dimensión filtra al hecho, nunca
al revés). El "1" siempre está en la dimensión (cada valor aparece una sola vez); el "*" en
la fact (cada valor aparece muchas veces).

| # | Dimensión (lado 1) | Hecho (lado *) | ¿Por qué? |
|---|---|---|---|
| 1 | DIM_Calendario[Fecha] | FACT_Presupuesto[Fecha] | Un mes = muchas filas de presupuesto |
| 2 | DIM_Calendario[Fecha] | FACT_RealDetalle[Fecha] | Un mes = muchas transacciones |
| 3 | DIM_Vertical[VerticalID] | FACT_Presupuesto[VerticalID] | Una vertical = muchas cuentas/cecos |
| 4 | DIM_Vertical[VerticalID] | FACT_RealDetalle[VerticalID] | Idem para el real |
| 5 | DIM_Cuenta[CuentaID] | FACT_Presupuesto[CuentaID] | Una cuenta = muchos cecos/meses |
| 6 | DIM_Cuenta[CuentaID] | FACT_RealDetalle[CuentaID] | Idem |
| 7 | DIM_Ceco[CecoID] | FACT_Presupuesto[CecoID] | Un ceco = muchas cuentas/meses |
| 8 | DIM_Ceco[CecoID] | FACT_RealDetalle[CecoID] | Idem |
| 9 | DIM_Proveedor[ProveedorID] | FACT_RealDetalle[ProveedorID] | Solo al detalle, no al presupuesto |

La relación #9 es la clave del modelo: `DIM_Proveedor` **no tiene relación con
`FACT_Presupuesto`**. Cuando filtrás por proveedor, el PA queda en blanco. Eso es correcto:
no existe presupuesto por proveedor.

Definidas en `MODELO_RELACIONAL.md` e implementadas en
`RealVsPAA.SemanticModel/definition/relationships.tmdl`.

## Las 12 medidas DAX

Las medidas son fórmulas que Power BI calcula **en tiempo real** según los filtros activos.
No son columnas; son cálculos dinámicos. Definidas en `MEDIDAS_DAX.md`.

| Medida | Qué calcula | Tabla | Cuándo usarla |
|---|---|---|---|
| Real Mes | SUM de MontoReal de FACT_Presupuesto | FACT_Presupuesto | Comparativo vs PA |
| PA Mes | SUM de MontoPA | FACT_Presupuesto | Comparativo vs Real |
| Variación | Real Mes − PA Mes | FACT_Presupuesto | Ver el desvío |
| Variación % | Variación / PA Mes (con DIVIDE) | FACT_Presupuesto | Ver el desvío relativo |
| Real Acumulado | Real Mes acumulado en el año (YTD) | FACT_Presupuesto | Comparar avance anual |
| PA Acumulado | PA Mes acumulado en el año (YTD) | FACT_Presupuesto | Idem |
| Variación Acum | Real Acum − PA Acum | FACT_Presupuesto | Desvío acumulado |
| Real Año Anterior | Real Mes del mismo período un año atrás | FACT_Presupuesto | Tendencia interanual |
| Var vs Año Anterior | Real Mes − Real Año Anterior | FACT_Presupuesto | Crecimiento vs año pasado |
| Variación % fmt | Variación % formateada como texto (+/-) | FACT_Presupuesto | Tarjetas de KPI |
| Color Variación | "#C00000" (rojo) o "#1F7A1F" (verde) | FACT_Presupuesto | Formato condicional |
| Real Detalle | SUM de MontoReal de FACT_RealDetalle | FACT_RealDetalle | **Solo** página de proveedores |

**Diferencia clave entre Real Mes y Real Detalle:** son dos fuentes distintas del mismo
concepto. `Real Mes` viene de la tabla de control de gestión (agregada, conciliada, oficial
para comparar vs PA). `Real Detalle` viene del detalle transaccional (bruto, con proveedores).
Difieren ~1,1% por criterios de armado. **Nunca mezcles `Real Detalle` con `PA Mes`** en el
mismo visual.

---

# FLUJO COMPLETO DE DATOS

```
Tu PC: Real_y_pa_2026v2.xlsx
         │
         │  pRutaArchivo apunta aquí
         ▼
     stgOrigen (lee el Excel completo)
         │
    ┌────┴────┐
    ▼         ▼
stgRealPA  stgBaseRealCruda
(hoja 1,   (hoja 2,
 header    header
 en fila3) en fila 1,
           filtro ≥2025)
    │         │
    ├─────────┤ (normalizan texto, reemplazan nulos)
    │         │
    ▼         ▼
 5 DIM + DIM_Calendario (generado con M, no del Excel)
    │
    ▼
 2 FACT (solo IDs enteros + montos, sin texto repetido)
    │
    ▼
 12 medidas DAX (cálculos en tiempo real)
    │
    ▼
 5 páginas del reporte → tus dashboards
```

---

# PASOS DE IMPLEMENTACIÓN

---

## PASO 1 — Descargar el repositorio de GitHub

### Qué estás viendo
La página del repositorio en GitHub. Ves una lista de archivos y carpetas.

### Dónde hacer clic

**Importante primero:** verificá que estás en la rama correcta.
- Sobre la lista de archivos hay un botón desplegable con el nombre de la rama actual (puede
  decir "main" u otro nombre).
- Hacé clic en ese botón → buscá **`claude/eager-gates-Md3ac`** → hacé clic para
  seleccionarla.
- La página se recarga mostrando los archivos de esa rama.

**Para descargar:**
1. Hacé clic en el botón verde **`Code`** (arriba a la derecha, sobre la lista de archivos).
2. En el menú que aparece, hacé clic en **`Download ZIP`**.
3. El navegador descarga un archivo `.zip`. Guardalo donde quieras por ahora.

### Qué debería ocurrir
Se descarga un archivo llamado algo como `General-claude-eager-gates-Md3ac.zip` (el nombre
puede variar según GitHub).

### Cómo validar
Revisá que el ZIP pese varios MB (debería ser ~50-100 KB, ya que el Excel no está adentro).

### Qué significa este paso
Estás bajando todo el trabajo ya hecho: el modelo de datos, las consultas M, las medidas DAX,
las páginas del reporte y las guías. Todo vive en archivos de texto dentro de este ZIP.

**Origen:** el repositorio `salonsodear-commits/General`, rama `claude/eager-gates-Md3ac`.

---

## PASO 2 — Preparar la estructura de carpetas en tu PC

### Qué estás viendo
El archivo ZIP descargado en tu PC y el Excel de origen (`Real_y_pa_2026v2.xlsx`).

### Qué hacer

1. Creá una carpeta de trabajo. Recomendación:
   ```
   C:\PowerBI\RealVsPAA\
   ```
   ¿Por qué esta estructura? Porque el proyecto PBIP va a buscar el SemanticModel y el Report
   en rutas relativas. Si los tres elementos están en la misma carpeta raíz, todo funciona
   independientemente de en qué PC estés.

2. Descomprimí el ZIP. Adentro vas a encontrar muchos archivos. Los que te interesan son:
   - `RealVsPAA.pbip`
   - carpeta `RealVsPAA.SemanticModel\`
   - carpeta `RealVsPAA.Report\`

3. Copiá **esas tres cosas** a `C:\PowerBI\RealVsPAA\`. Asegurate de copiar las carpetas
   completas con todo su contenido adentro (no solo los archivos de primer nivel).

4. Copiá también el Excel a alguna carpeta de fácil acceso. Por ejemplo:
   ```
   C:\PowerBI\RealVsPAA\Datos\Real_y_pa_2026v2.xlsx
   ```

### Cómo debe quedar la estructura
```
C:\PowerBI\RealVsPAA\
├── RealVsPAA.pbip
├── RealVsPAA.SemanticModel\
│   ├── definition.pbism
│   ├── .platform
│   ├── diagramLayout.json
│   └── definition\
│       ├── model.tmdl
│       ├── database.tmdl
│       ├── expressions.tmdl
│       ├── relationships.tmdl
│       └── tables\
│           ├── DIM_Calendario.tmdl
│           ├── DIM_Ceco.tmdl
│           ├── DIM_Cuenta.tmdl
│           ├── DIM_Proveedor.tmdl
│           ├── DIM_Vertical.tmdl
│           ├── FACT_Presupuesto.tmdl
│           └── FACT_RealDetalle.tmdl
├── RealVsPAA.Report\
│   ├── .platform
│   ├── definition.pbir
│   └── report.json
└── Datos\
    └── Real_y_pa_2026v2.xlsx
```

### Cómo validar
En el Explorador de Windows, abrí `C:\PowerBI\RealVsPAA\` y verificá que ves el archivo
`.pbip` y las dos carpetas. Si falta alguna, volvé al ZIP y copialá.

### Qué significa este paso
El formato PBIP es un **proyecto basado en carpetas**, igual que un proyecto de código. El
archivo `RealVsPAA.pbip` es solo la entrada; internamente le dice a Power BI Desktop dónde
buscar el modelo (`RealVsPAA.SemanticModel\`) y el reporte (`RealVsPAA.Report\`). Si movés
las carpetas de lugar sin mover el `.pbip`, el proyecto se rompe. Por eso las tres cosas van
juntas en la misma carpeta raíz.

**Origen:** estructura definida por los generadores `_build_pbip.py` y `_build_report.py`, y
documentada en `IMPLEMENTACION_POWERBI.md`.

---

## PASO 3 — Verificar Power BI Desktop

### Qué estás viendo
Power BI Desktop instalado en tu PC.

### Qué hacer
1. Abrí Power BI Desktop.
2. Menú **Ayuda** → **Acerca de Power BI Desktop**.
3. Fijate el número de versión en el cuadro que aparece. Ejemplos:
   - "Version: 2.122.xxx" → OK
   - "Version: 2.135.xxx" → OK
   - Algo anterior a "2.122" → necesitás actualizar.

### Versión mínima requerida
**Octubre 2023 (build 2.122) o posterior.** El formato PBIP/TMDL fue estabilizado en esa
versión. En 2024-2025 ya viene habilitado por defecto.

### Si necesitás actualizar
- Windows: buscá "Microsoft Store" → buscá "Power BI Desktop" → botón "Actualizar".
- O descargalo desde `https://powerbi.microsoft.com` (botón "Descargar gratis").

### Habilitar soporte PBIP (si tu versión es de 2023)
1. Menú **Archivo → Opciones y configuración → Opciones**.
2. Panel izquierdo: **Características de vista previa**.
3. Marcá **"Guardar como Power BI project"**.
4. **Aceptar** → cerrá y reabrí Power BI Desktop.

### Qué significa este paso
El PBIP es un formato relativamente nuevo. Versiones viejas de Power BI Desktop no pueden
abrirlo. Con versiones recientes (2024+) esto ya no es problema.

---

## PASO 4 — Abrir el proyecto PBIP

### Qué estás viendo
Power BI Desktop abierto, probablemente con la pantalla de inicio o un proyecto vacío.

### Dónde hacer clic
1. Menú **Archivo** (arriba a la izquierda).
2. **Abrir informe** → **Examinar este dispositivo...** (o directamente **Ctrl+O**).
3. Se abre el explorador de archivos de Windows.
4. **Importante:** en la parte inferior del cuadro de diálogo hay un selector de tipo de
   archivo. Hacé clic en él y elegí **"Power BI Project (*.pbip)"** o **"Todos los archivos
   (*.*)"**. Si solo ves `*.pbix` en la lista, no vas a poder ver el `.pbip`.
5. Navegá hasta `C:\PowerBI\RealVsPAA\`.
6. Hacé doble clic en **`RealVsPAA.pbip`**.

### Qué debería ocurrir
Power BI Desktop lee los archivos TMDL y el `report.json`, construye el modelo en memoria y
muestra las páginas del reporte. Puede tardar 30-60 segundos. Es normal que aparezca una
barra de progreso y mensajes de carga.

**Si aparece un aviso de seguridad** ("¿Confías en este archivo?") → **Habilitar**.
**Si aparece "Advertencia de privacidad"** → **Continuar** (o "Omitir").

### Qué debería verse cuando termina de abrir
- En la parte inferior: 5 pestañas con nombres de página.
- En el centro: la página "1. Resumen Ejecutivo" con visuales (probablemente vacíos hasta
  que cargues los datos).
- En el panel derecho: lista de tablas y medidas.

### Qué hacer si aparece un error al abrir
| Error | Causa | Solución |
|---|---|---|
| "No se puede abrir el archivo" | Power BI Desktop muy viejo | Actualizá a versión reciente |
| "Formato no reconocido" | PBIP no habilitado | Activá la opción en Características de vista previa (Paso 3) |
| "No se encuentra SemanticModel" | Las carpetas no están en el mismo nivel que el .pbip | Verificá la estructura del Paso 2 |

### Qué significa este paso
Estás abriendo un **proyecto Power BI basado en texto**. El `.pbip` le dice a Desktop:
"el modelo está en `RealVsPAA.SemanticModel\`" y "el reporte está en `RealVsPAA.Report\`".
Desktop lee los archivos `.tmdl` (modelo) y el `report.json` (páginas) y los materializa en
su motor interno.

**Archivos que Desktop usa internamente en este paso:**
- `RealVsPAA.pbip` → punto de entrada.
- `RealVsPAA.SemanticModel\definition\model.tmdl` → configuración general del modelo.
- `RealVsPAA.SemanticModel\definition\database.tmdl` → nivel de compatibilidad.
- `RealVsPAA.SemanticModel\definition\tables\*.tmdl` → cada tabla con sus columnas y medidas.
- `RealVsPAA.SemanticModel\definition\relationships.tmdl` → las 9 relaciones.
- `RealVsPAA.SemanticModel\definition\expressions.tmdl` → el parámetro y las consultas staging.
- `RealVsPAA.Report\report.json` → las 5 páginas y sus visuales.

---

## PASO 5 — Configurar el parámetro `pRutaArchivo`

### Qué estás viendo
Power BI Desktop con el proyecto abierto. Los visuales del reporte probablemente muestran
"Error" o están vacíos porque todavía no apuntaste al Excel correcto.

### Qué es `pRutaArchivo` y por qué existe
Es un **parámetro de texto** que guarda la ruta completa del Excel en tu PC. En lugar de
hardcodear la ruta dentro de cada consulta M (lo cual obligaría a editar múltiples lugares si
el archivo se mueve), la ruta está centralizada en un solo parámetro. Cambiás la ruta una vez
y todas las consultas la recogen automáticamente.

**Definido en:** `CONSULTAS_PowerQuery.md` → sección "0) Parámetro pRutaArchivo".
**Implementado en:** `RealVsPAA.SemanticModel\definition\expressions.tmdl`.

**Consultas que dependen de él:** `stgOrigen` (que a su vez alimenta a `stgRealPA`,
`stgBaseRealCruda`, y a través de ellas a las 5 DIM y las 2 FACT).

**Si está mal configurado:** todas las consultas fallan con "No se encontró el archivo" y el
modelo queda vacío.

### Dónde hacer clic
1. Menú **Inicio** → botón **"Transformar datos"** (el que tiene el ícono de tabla con lápiz,
   en el grupo "Consultas"). Se abre el Editor de Power Query.
2. En el panel izquierdo (lista de consultas), buscá **`pRutaArchivo`**. Debería ser la primera
   de la lista o estar cerca del principio.
3. Hacé clic sobre **`pRutaArchivo`**.

### Qué pantalla debería aparecer
En el área central ves un campo con el valor actual: `C:\Reportes\PAA\Real_y_pa_2026v2.xlsx`
(ese es el valor de ejemplo que puse al generar el proyecto).

### Cómo modificarlo — Método 1 (directo, barra de fórmulas)
1. En la barra de fórmulas (la barra larga que está arriba del área central, empieza con `=`),
   hace clic.
2. Vas a ver algo como: `= "C:\Reportes\PAA\Real_y_pa_2026v2.xlsx"`
3. Borrá todo el texto entre las comillas (sin borrar las comillas).
4. Pegá tu ruta real. Ejemplo: `C:\PowerBI\RealVsPAA\Datos\Real_y_pa_2026v2.xlsx`
5. Presioná **Enter**.

### Cómo modificarlo — Método 2 (menú visual, más fácil)
1. Con `pRutaArchivo` seleccionado en el panel izquierdo.
2. Menú **Inicio → Administrar parámetros → Administrar parámetros**.
3. Se abre una ventana con el parámetro listado.
4. Hacé doble clic sobre **`pRutaArchivo`**.
5. En el campo **"Valor actual"**, borrá el texto y pegá tu ruta.
6. **Aceptar** → **Aceptar**.

### Cómo obtener la ruta exacta
En el Explorador de Windows, navegá hasta el Excel. Hacé clic en la **barra de dirección**
(la barra con la ruta que está arriba de la lista de archivos) → se selecciona todo → `Ctrl+C`.
Eso copia la ruta de la carpeta. Después agregale `\Real_y_pa_2026v2.xlsx` al final.

### Cómo validar que quedó bien
En el panel izquierdo, hacé clic en **`stgOrigen`**. En la vista previa del centro deberías
ver una tabla con las hojas del Excel (columnas Name, Data, etc.) y entre ellas
"REAL vs PA 2025 2026" y "Base Real". Si ves eso, la ruta está bien.

Si ves un error rojo: la ruta está mal. Revisá que no tenga barras invertidas faltantes, que
el archivo exista en esa ubicación y que el nombre sea exactamente `Real_y_pa_2026v2.xlsx`.

---

## PASO 6 — Actualizar los datos (ejecutar todas las consultas)

### Qué estás viendo
El Editor de Power Query con `pRutaArchivo` correctamente configurado.

### Dónde hacer clic
1. En el Editor de Power Query, menú **Inicio** → botón **"Cerrar y aplicar"** (arriba a la
   izquierda, con un ícono de puerta y flecha).
2. Power BI Desktop cierra el Editor y ejecuta todas las consultas.

### Qué debería ocurrir
Aparece una barra de progreso en la parte inferior de Power BI Desktop que va mostrando los
nombres de las tablas a medida que se cargan:
- `DIM_Vertical` → cargando...
- `DIM_Cuenta` → cargando...
- `DIM_Ceco` → cargando...
- `DIM_Proveedor` → cargando...
- `DIM_Calendario` → cargando...
- `FACT_Presupuesto` → cargando...
- `FACT_RealDetalle` → cargando... (esta tarda más, son 30.000 filas)

**Tiempo estimado:** 2-8 minutos, dependiendo de la velocidad de tu PC. El Excel pesa ~23 MB
y tiene dos hojas pesadas.

### Qué consultas se ejecutan y qué transformaciones hacen

| Consulta | Qué hace |
|---|---|
| `stgOrigen` | Abre el binario del Excel y lista las hojas disponibles |
| `stgRealPA` | Toma la hoja "REAL vs PA 2025 2026" (header en fila 3), limpia, normaliza texto a MAYÚSCULAS, reemplaza nulos por 0 |
| `stgBaseRealCruda` | Toma la hoja "Base Real" (header en fila 1), filtra solo registros ≥ 2025-01-01, normaliza texto |
| `DIM_Vertical` | Une verticales de ambas fuentes, elimina duplicados, asigna ID entero |
| `DIM_Cuenta` | Toma cuentas de stgRealPA, elimina duplicados por Cuenta, asigna ID |
| `DIM_Ceco` | Une cecos de ambas fuentes, elimina duplicados, asigna ID |
| `DIM_Proveedor` | Toma proveedores de stgBaseRealCruda, elimina duplicados, asigna ID |
| `DIM_Calendario` | **No lee el Excel** — genera la tabla de fechas con código M puro |
| `FACT_Presupuesto` | Toma stgRealPA y reemplaza los textos por IDs de las dimensiones (joins) |
| `FACT_RealDetalle` | Toma stgBaseRealCruda y reemplaza los textos por IDs (incluido ProveedorID) |

Las consultas staging (`stgOrigen`, `stgRealPA`, `stgBaseRealCruda`, `BASE_PLANA_RealvsPA`)
**no se cargan al modelo** — son pasos intermedios. Solo las 7 tablas cargadas van al motor
de Power BI.

### Errores posibles y solución

| Error | Causa | Solución |
|---|---|---|
| "No se encontró el archivo" | pRutaArchivo incorrecto | Volvé al Paso 5 y corregí la ruta |
| "No se encontró la hoja 'REAL vs PA 2025 2026'" | El Excel no es el correcto o la hoja fue renombrada | Verificá que el Excel sea el original con esas hojas exactas |
| "Error de columna: 'Denominación Cuenta'" | La hoja Real vs PA cambió de nombre en alguna columna | El Excel nuevo debe tener exactamente los mismos encabezados |
| "Expression.Error: The column 'Vertical' of the table wasn't found" | stgRealPA o stgBaseRealCruda fallaron antes | Solucioná el error de la consulta anterior primero |
| Tiempo de carga muy largo (>15 min) | PC lento o Excel muy pesado | Es normal; esperá. No cierres Power BI. |

---

## PASO 7 — Verificar que las consultas cargaron correctamente

### Qué estás viendo
Power BI Desktop después de que terminó la carga. Los visuales del reporte ahora deberían
mostrar números.

### Dónde mirar
1. Menú **Inicio → Transformar datos** (abre el Editor de Power Query).
2. Panel izquierdo: lista de todas las consultas.

### Cuántas y qué nombres deberías ver (12 en total)

**Cargadas al modelo** (ícono de tabla normal, texto normal):
1. `DIM_Vertical` — 3 filas (las 3 verticales)
2. `DIM_Cuenta` — 58 filas (las 58 cuentas contables)
3. `DIM_Ceco` — 63 filas (los 63 centros de costo)
4. `DIM_Proveedor` — 499 filas (los proveedores únicos desde 2025)
5. `DIM_Calendario` — 24 filas (enero 2025 a diciembre 2026)
6. `FACT_Presupuesto` — 5.184 filas
7. `FACT_RealDetalle` — 30.070 filas

**No cargadas** (texto en cursiva, ícono diferente — son las staging):
8. `pRutaArchivo` (parámetro)
9. `stgOrigen`
10. `stgRealPA`
11. `stgBaseRealCruda`
12. `BASE_PLANA_RealvsPA` (alternativa express, no usada en el modelo)

### Cómo verificar el contenido de cada tabla cargada

Hacé clic en `DIM_Calendario` → deberías ver 24 filas con fechas, el año, el número de mes,
el nombre del mes en español y la columna `MesAño` con valores como "Ene-25", "Feb-25", etc.

Hacé clic en `FACT_Presupuesto` → deberías ver columnas: Fecha (fechas), VerticalID
(números 1, 2 o 3), CuentaID (números), CecoID (números), MontoReal (decimales), MontoPA
(decimales). No deberías ver texto — solo IDs y montos.

Si alguna tabla muestra "Error" o está vacía, hacé clic en el nombre de esa tabla y mirá el
mensaje de error en la zona central para diagnosticar.

### Cerrá el editor
Menú **Inicio → Cerrar y aplicar** (o simplemente la **X** del Editor de Power Query en la
barra de título).

---

## PASO 8 — Verificar el modelo (relaciones y tablas)

### Qué estás viendo
Power BI Desktop con las tablas ya cargadas.

### Cómo abrir la vista Modelo
En el panel de la **izquierda** hay tres íconos apilados verticalmente:
- Ícono 1 (gráfico de barras): vista de Informe (las páginas del reporte).
- Ícono 2 (tabla con filas): vista de Tabla (datos crudos de cada tabla).
- Ícono 3 (diagrama con líneas conectadas): vista de **Modelo**.

Hacé clic en el **tercer ícono** (diagrama).

### Qué deberías ver
Un diagrama con 7 rectángulos (las 7 tablas cargadas) conectados con 9 líneas. Si las tablas
están amontonadas en el centro, arrastralas para acomodarlas — eso no afecta nada funcional,
es solo estético.

El diagrama debería verse aproximadamente así:

```
  DIM_Calendario ────── FACT_Presupuesto ────── DIM_Vertical
                     \       │      /                │
                      \      │     /                 │
                  DIM_Cuenta │ DIM_Ceco     FACT_RealDetalle
                             │                       │
                         DIM_Proveedor ──────────────┘
```

### Cómo verificar cada relación
Hacé doble clic sobre cualquier línea de relación. Se abre un diálogo que muestra:
- **Tabla (del lado muchos):** la FACT.
- **Tabla (del lado uno):** la DIM.
- **Cardinalidad:** debe decir "Uno a varios (1:*)".
- **Dirección del filtro cruzado:** debe decir "Única".

→ **Cancelar** (no cambies nada).

Verificá que `DIM_Proveedor` tiene una sola línea, que va hacia `FACT_RealDetalle` y **no**
hacia `FACT_Presupuesto`.

### Marcar DIM_Calendario como tabla de fechas

Este es el único paso que puede requerir acción manual:

1. En la vista Modelo, hacé clic en la tabla **`DIM_Calendario`** (se selecciona, el borde
   se pone azul).
2. En la barra superior aparece la pestaña **"Herramientas de tabla"**. Hacé clic en ella.
3. Hacé clic en el botón **"Marcar como tabla de fechas"**.
4. En el desplegable que aparece, elegí la columna **`Fecha`**.
5. **Aceptar**.

Si el botón ya muestra "Fecha" o si la tabla ya tiene un ícono de calendario en el diagrama,
ya estaba marcada automáticamente — nada que hacer.

**¿Por qué es necesario?** Las funciones de time-intelligence de DAX (`DATESYTD`,
`SAMEPERIODLASTYEAR`) que usan las medidas de Acumulado y Año Anterior requieren que Power BI
sepa cuál es la tabla oficial de fechas. Sin este marcado, esas medidas pueden dar resultados
incorrectos o mostrar advertencias.

**Origen:** `GUIA_PowerBI.md` → sección D "Marcar el calendario como tabla de fechas".
Implementado en `DIM_Calendario.tmdl`.

---

## PASO 9 — Verificar las medidas DAX

### Qué estás viendo
Power BI Desktop con el modelo cargado.

### Dónde encontrar las medidas
1. En el panel de la izquierda, hacé clic en el **segundo ícono** (vista de Tabla).
2. En el panel **derecho** (panel de "Datos"), expandí la tabla **`FACT_Presupuesto`** haciendo
   clic en la flecha a su izquierda.
3. Deberías ver una lista de columnas y, marcadas con un ícono especial (una calculadora o el
   símbolo `Σ`), las medidas.

### Qué medidas deberías ver en `FACT_Presupuesto` (11)
```
∑ Color Variación
∑ PA Acumulado
∑ PA Mes
∑ Real Acumulado
∑ Real Año Anterior
∑ Real Mes
∑ Var vs Año Anterior
∑ Variación
∑ Variación %
∑ Variación % fmt
∑ Variación Acum
```

### Medida en `FACT_RealDetalle` (1)
Expandí `FACT_RealDetalle` → deberías ver:
```
∑ Real Detalle
```

### Cómo probar una medida
1. Andá a la vista de **Informe** (primer ícono izquierdo).
2. En la página "1. Resumen Ejecutivo", las 4 tarjetas de KPI deberían mostrar números.
   - Si muestran un valor numérico (aunque sea 0 o vacío para meses sin datos): la medida
     funciona correctamente.
   - Si muestran "Error": hacé clic en la tarjeta → panel derecho → revisá qué medida tiene
     asignada → compará con la definición en `MEDIDAS_DAX.md`.

---

## PASO 10 — Verificar las páginas del dashboard

### Qué estás viendo
Power BI Desktop en la vista de Informe, con 5 pestañas en la parte inferior.

### Las 5 páginas y qué deberías ver

---

**Página 1 — "1. Resumen Ejecutivo"**

*Objetivo de negocio:* vista rápida para gerencia. ¿Cuánto gasté, cuánto tenía presupuestado,
cuál es el desvío?

*Visuals que deberías ver:*
- 4 tarjetas (KPIs): **Real Mes**, **PA Mes**, **Variación**, **Variación %**.
- Gráfico de columnas agrupadas: Real vs PA **por mes** (eje X = MesAño, barras = Real y PA).
- Gráfico de barras: Real vs PA **por vertical** (PETROLEO, MINERIA, OTRAS).
- Gráfico de líneas: tendencia de **Real Acumulado** vs **PA Acumulado**.
- 3 slicers (segmentadores): Vertical, Rubro, MesAño.

*Cómo probar:* hacé clic en "PETROLEO" en el slicer de Vertical. Todos los visuales deberían
filtrar y mostrar solo los datos de esa vertical.

---

**Página 2 — "2. Comercial"**

*Objetivo de negocio:* análisis de desvíos por vertical, rubro y cuenta. ¿En qué rubros
me estoy pasando?

*Visuals que deberías ver:*
- 1 **Matriz** con jerarquía Vertical > Rubro > Cuenta. Columnas: Real Mes, PA Mes, Variación,
  Variación %.
- 2 slicers: Vertical, MesAño.

*Cómo probar:* en la matriz, buscá el botón de drill-down (flechas hacia abajo arriba del
visual) y expandí un nivel para ver los rubros. Los valores de Variación deberían ser
negativos donde el gasto fue menor al presupuesto.

*Formato condicional (opcional, 2 clics):*
1. Clic en la matriz → panel "Visualizaciones" (derecha) → buscá "Variación" en los Valores.
2. Clic en la flecha junto a "Variación" → **Formato condicional → Color de fuente**.
3. Cambiá "Basado en" a **"Valor de campo"** y seleccioná la medida **`Color Variación`**.
4. Aceptar. Repetí en la Página 3.

---

**Página 3 — "3. Operativa"**

*Objetivo de negocio:* análisis hasta el nivel más bajo: Vertical > Rubro > Cuenta > Ceco.
¿Qué centro de costo específico está generando el desvío?

*Visuals:* igual que Página 2 pero la jerarquía llega hasta Ceco.
*Slicers:* Rubro, MesAño.

---

**Página 4 — "4. Drill Through — Proveedores"**

*Objetivo de negocio:* una vez que identificaste un ceco o cuenta problemática, ver qué
proveedores generaron ese gasto.

*Visuals que deberías ver:*
- 1 tarjeta: **Real Detalle** (total de la selección).
- 1 tabla: columnas Proveedor, Cuenta, Ceco, Real Detalle, Texto.

*Cómo usar el drill-through:*
1. Andá a la **Página 3**.
2. En la matriz, expandí hasta nivel Ceco.
3. Hacé **clic derecho** sobre una fila de Ceco.
4. En el menú contextual: **"Explorar en profundidad"** → **"4. Drill Through — Proveedores"**.
5. Te lleva a la Página 4 ya filtrada por esa Cuenta + Ceco.
6. El botón de volver (flecha ← arriba izquierda del lienzo) te devuelve.

*Por qué existe esta página separada:* el PA no existe a nivel proveedor. Si lo mezclaras en
la misma página que el comparativo, causaría confusión. La separación hace explícito que acá
solo estás mirando el Real. Definido en `GUIA_PowerBI.md` → sección E "Página 3".

---

**Página 5 — "5. Auditoría"**

*Objetivo de negocio:* control de consistencia. Comparar `Real Mes` (agregado oficial) con
`Real Detalle` (transaccional) para detectar diferencias por cuenta/ceco.

*Visuals:*
- 3 tarjetas: Real Mes, Real Detalle, Variación.
- 1 tabla: Vertical, Cuenta, Ceco, Real Mes, Real Detalle, Variación.

*Resultado esperado:* `Real Mes` (~4.061 MM) y `Real Detalle` (~4.105 MM) difieren ~44 MM
(~1,1%). Eso es esperado y está documentado en `VALIDACIONES_POWERBI.md` y `MEDIDAS_DAX.md`.

---

## PASO 11 — Guardar como .pbix

### Qué estás viendo
Power BI Desktop con todo funcionando.

### Dónde hacer clic
1. Menú **Archivo → Guardar una copia** (o **Archivo → Guardar como**).
2. En "Tipo de archivo" del cuadro de diálogo, elegí **"Archivo Power BI (*.pbix)"**.
3. Elegí la carpeta: `C:\PowerBI\RealVsPAA\`.
4. Nombre: `RealVsPAA.pbix`.
5. **Guardar**.

### Para el refresco mensual
El mes que viene, cuando tengas el nuevo Excel:
1. Reemplazá `Real_y_pa_2026v2.xlsx` en la misma carpeta (mismo nombre).
2. Abrí el `.pbip` (no el `.pbix`).
3. Menú **Inicio → Actualizar** (o el botón Actualizar en la cinta).
4. Power BI recarga las dos hojas, regenera todas las tablas y el calendario.
5. Guardá de nuevo como `.pbix`.

**Condiciones que el Excel nuevo DEBE cumplir:**
- Las hojas se llaman exactamente `REAL vs PA 2025 2026` y `Base Real`.
- En "REAL vs PA 2025 2026": encabezado en la fila 3 (filas 1 y 2 vacías).
- Mismas columnas que el original (no cambiar nombres).
- `mes año` sigue siendo una fecha (no texto).

---

# CHECKLIST DE VALIDACIÓN FINAL

| Estado | Validación | Resultado esperado |
|---|---|---|
| ☐ | Descargué el ZIP de la rama `claude/eager-gates-Md3ac` | Archivo ZIP en mi PC |
| ☐ | Copié las 3 cosas obligatorias en la misma carpeta | `RealVsPAA.pbip`, `SemanticModel\`, `Report\` en `C:\PowerBI\RealVsPAA\` |
| ☐ | Tengo el Excel en mi PC y conozco la ruta | `C:\...\Real_y_pa_2026v2.xlsx` |
| ☐ | Power BI Desktop versión oct-2023 o posterior | Menú Ayuda → Acerca de → versión 2.122+ |
| ☐ | Abrí `RealVsPAA.pbip` sin errores | 5 pestañas visibles en el reporte |
| ☐ | Configuré `pRutaArchivo` con la ruta real | stgOrigen muestra las hojas del Excel |
| ☐ | Ejecuté "Cerrar y aplicar" sin errores | Barra de progreso completó sin rojo |
| ☐ | Veo 7 tablas cargadas en Power Query | DIM_* y FACT_* con ícono normal |
| ☐ | Veo 5 consultas en cursiva (no cargadas) | pRutaArchivo, stgOrigen, stgRealPA, stgBaseRealCruda, BASE_PLANA_RealvsPA |
| ☐ | DIM_Calendario tiene 24 filas | Enero 2025 a diciembre 2026 |
| ☐ | FACT_Presupuesto tiene 5.184 filas | Solo IDs y montos, sin texto |
| ☐ | FACT_RealDetalle tiene 30.070 filas | Solo IDs, MontoReal y Texto |
| ☐ | Vista Modelo muestra 7 tablas y 9 líneas | Diagrama completo |
| ☐ | Relaciones: cardinalidad 1:*, dirección única | Verificar doble clic en cada línea |
| ☐ | DIM_Proveedor conecta SOLO a FACT_RealDetalle | Sin línea hacia FACT_Presupuesto |
| ☐ | DIM_Calendario marcada como tabla de fechas | Ícono de calendario en la tabla |
| ☐ | FACT_Presupuesto tiene 11 medidas | Real Mes, PA Mes, Variación, Var%, 3 acumulados, 2 interanual, 2 formato |
| ☐ | FACT_RealDetalle tiene 1 medida | Real Detalle |
| ☐ | Página 1: KPIs muestran valores numéricos | Tarjetas con números (no "Error") |
| ☐ | Página 1: gráfico de columnas muestra barras | Real y PA por mes |
| ☐ | Página 1: slicer de Vertical filtra los visuales | Al hacer clic en PETROLEO, todo cambia |
| ☐ | Página 2: Matriz muestra jerarquía Vertical > Rubro > Cuenta | Filas expandibles |
| ☐ | Página 3: Matriz llega hasta nivel Ceco | Jerarquía de 4 niveles |
| ☐ | Página 4: Drill-through funciona desde Página 3 | Clic derecho → Explorar → filtra correctamente |
| ☐ | Página 5: muestra ambos totales Real Mes y Real Detalle | Difieren ~1,1% (esperado) |
| ☐ | Guardé como `.pbix` | Archivo `RealVsPAA.pbix` en la carpeta |

---

# SI ALGÚN VISUAL APARECE VACÍO O CON CAMPOS SUELTOS

Los visuales están definidos en `report.json` (formato PBIR legacy). Al abrir el PBIP,
Power BI Desktop intenta reconstruirlos, pero en algunos casos puede que un campo quede
"desasignado" (el visual existe pero no tiene datos). Esto NO es un error del modelo ni
de las medidas — es una limitación del formato cuando se genera sin interfaz gráfica.

**Cómo arreglarlo en 1 minuto:**
1. Hacé clic en el visual que está vacío.
2. En el panel **"Visualizaciones"** (derecha), fijate qué "pozos" (Category, Values, Rows,
   etc.) están vacíos.
3. En el panel **"Datos"** (también derecha, más a la derecha), buscá el campo correcto y
   arrastralo al pozo correspondiente.

Todos los campos y medidas ya existen en el modelo. Solo es cuestión de asignarlos a los
pozos correctos del visual.

**Referencia de qué campo va en qué visual:** ver `PAGINAS_REPORTE.md` (tabla completa de
cada visual con sus campos).
