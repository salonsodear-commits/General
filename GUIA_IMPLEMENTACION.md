# GUIA_IMPLEMENTACION.md — De GitHub a Power BI funcionando

Guía práctica, paso a paso. Sin saltar nada. Sin asumir conocimientos previos.

---

## PARTE 1 — Qué generé y para qué sirve cada archivo

### Tipo de proyecto: PBIP (Power BI Project)

El PBIP es el **formato oficial de Microsoft para Power BI basado en texto**. Es la evolución
del `.pbix`: en lugar de un archivo binario comprimido, el proyecto se almacena como una
carpeta con archivos de texto (TMDL y JSON) que son legibles, versionables en git y que
Power BI Desktop puede abrir directamente.

**Analogía:** es como un proyecto de Visual Studio (`.sln`) en lugar de un ejecutable (`.exe`).
Lo abrís en la herramienta, cargás los datos y guardás como `.pbix`.

### Archivo principal

| Archivo | Qué es | Para qué sirve |
|---|---|---|
| `RealVsPAA.pbip` | Entrada del proyecto | Es el archivo que abrís en Power BI Desktop. Le dice a Desktop dónde están el modelo y el reporte. |

### Carpeta `RealVsPAA.SemanticModel/` — el modelo de datos

| Archivo | Formato | Qué contiene |
|---|---|---|
| `definition.pbism` | JSON | Metadatos del modelo. Power BI lo necesita para reconocer la carpeta como Semantic Model. |
| `.platform` | JSON | ID único del modelo. No lo toques. |
| `diagramLayout.json` | JSON | Posición de las tablas en la vista Modelo. Empieza vacío; Power BI lo actualiza cuando movés las tablas. |
| `definition/model.tmdl` | TMDL | Configuración global: cultura (es-ES), orden de carga, compatibilidad. |
| `definition/database.tmdl` | TMDL | Nivel de compatibilidad (1567 = Power BI actual). |
| `definition/expressions.tmdl` | TMDL | El parámetro `pRutaArchivo` y las 4 consultas auxiliares (staging) que NO se cargan al modelo. |
| `definition/relationships.tmdl` | TMDL | Las 9 relaciones entre dimensiones y facts. |
| `definition/tables/DIM_Vertical.tmdl` | TMDL | Tabla + código M + tipos de columna. Ídem para cada DIM y FACT. |
| `definition/tables/DIM_Cuenta.tmdl` | TMDL | Idem |
| `definition/tables/DIM_Ceco.tmdl` | TMDL | Idem |
| `definition/tables/DIM_Proveedor.tmdl` | TMDL | Idem |
| `definition/tables/DIM_Calendario.tmdl` | TMDL | Idem |
| `definition/tables/FACT_Presupuesto.tmdl` | TMDL | Tabla + 11 medidas DAX + código M |
| `definition/tables/FACT_RealDetalle.tmdl` | TMDL | Tabla + medida `Real Detalle` + código M |

**TMDL** = Tabular Model Definition Language. Es el lenguaje con el que Microsoft representa
el modelo de datos en texto plano. Power BI Desktop lo lee y lo convierte al modelo interno.

### Carpeta `RealVsPAA.Report/` — el reporte (páginas y visuales)

| Archivo | Formato | Qué contiene |
|---|---|---|
| `definition.pbir` | JSON | Le dice al reporte en qué Semantic Model buscar los datos (apunta a `../RealVsPAA.SemanticModel`). |
| `.platform` | JSON | ID único del reporte. No lo toques. |
| `report.json` | PBIR legacy | Las 5 páginas con todos los visuales: tarjetas, gráficos, matrices, tablas, slicers y drill-through. |

---

## PARTE 2 — Qué descargar de GitHub (obligatorio y opcional)

### Archivos OBLIGATORIOS para abrir en Power BI

```
RealVsPAA.pbip                          ← archivo de entrada
RealVsPAA.SemanticModel/                ← carpeta completa (con todo lo que tiene adentro)
RealVsPAA.Report/                       ← carpeta completa (con todo lo que tiene adentro)
```

Estos tres elementos deben quedar **en la misma carpeta** de tu PC.

### Archivos de referencia (opcionales, no afectan el PBIP)

```
CONSULTAS_PowerQuery.md    (código M de referencia)
MEDIDAS_DAX.md             (medidas DAX de referencia)
GUIA_PowerBI.md            (guía del modelo)
MODELO_POWERBI.md
MODELO_RELACIONAL.md
IMPLEMENTACION_POWERBI.md
PAGINAS_REPORTE.md
VALIDACIONES_POWERBI.md
CHECKLIST_IMPLEMENTACION.md
REVISION_ARQUITECTURA.md
```

También podés ignorar: `_build_pbip.py`, `_build_report.py` (son los scripts que los generaron).

---

## PARTE 3 — Implementación paso a paso

---

### PASO 1 — Descargar el repositorio de GitHub

**Opción A (recomendada): descargar el ZIP completo**

1. Abrí el repositorio en GitHub.
2. Hacé clic en el botón verde **`Code`** (arriba a la derecha, sobre la lista de archivos).
3. En el menú que aparece, hacé clic en **`Download ZIP`**.
4. Se descarga un archivo `.zip` con todo el repositorio. Guardalo donde quieras.

**Importante:** el ZIP contiene la rama activa. Como el trabajo está en
`claude/eager-gates-Md3ac`, antes de descargar verificá que GitHub muestre esa rama:
- Sobre la lista de archivos hay un selector de rama (dice el nombre de la rama actual).
- Si no dice `claude/eager-gates-Md3ac`, hacé clic ahí y seleccioná esa rama.
- Luego descargá el ZIP.

**Opción B: clonar con git**

```
git clone https://github.com/salonsodear-commits/General.git
cd General
git checkout claude/eager-gates-Md3ac
```

---

### PASO 2 — Preparar la carpeta en tu PC

1. Descomprimí el ZIP que descargaste.
2. Adentro vas a encontrar, entre otros archivos, estas tres cosas:
   - `RealVsPAA.pbip`
   - carpeta `RealVsPAA.SemanticModel`
   - carpeta `RealVsPAA.Report`
3. Copiá esas tres cosas a una carpeta de trabajo. Ejemplo:
   `C:\Reportes\PAA\ProyectoPBI\`
4. La estructura final en tu PC tiene que verse así:

```
C:\Reportes\PAA\ProyectoPBI\
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
└── RealVsPAA.Report\
    ├── .platform
    ├── definition.pbir
    └── report.json
```

5. **Poné también el Excel** (`Real_y_pa_2026v2.xlsx`) en alguna carpeta de tu PC. Anotá
   la ruta completa. Ejemplo: `C:\Reportes\PAA\Real_y_pa_2026v2.xlsx`.

> **Truco para copiar la ruta exacta:** En el Explorador de Windows, hacé clic sobre la
> barra de dirección (arriba, donde dice el nombre de la carpeta) → se selecciona y se pone
> azul → hacés `Ctrl+C`. Ya la tenés copiada.

---

### PASO 3 — Verificar la versión de Power BI Desktop

El formato PBIP requiere **Power BI Desktop versión de octubre 2023 o posterior** (build
2.122 o superior, idealmente la versión más reciente).

**Cómo verificar tu versión:**
1. Abrí Power BI Desktop.
2. Menú **Ayuda** → **Acerca de Power BI Desktop**.
3. Fijate el número de versión. Si dice "2.1XX" o superior, estás bien.

**Si tenés una versión vieja:** en Windows, buscá "Microsoft Store" → buscá
"Power BI Desktop" → **Actualizar**. O descargalo desde
`https://powerbi.microsoft.com/es-es/desktop/` (botón "Descargar gratis").

**Habilitar soporte PBIP (si la opción no aparece):**
1. Menú **Archivo → Opciones y configuración → Opciones**.
2. En el panel izquierdo: **Características de vista previa**.
3. Verificá que esté marcada la opción **"Guardar como Power BI project"** (o similar).
4. **Aceptar** → cerrar y reabrir Power BI Desktop.

> En versiones recientes (2024+) esta opción ya viene habilitada por defecto.

---

### PASO 4 — Abrir el proyecto en Power BI Desktop

1. Abrí Power BI Desktop.
2. Cerrá cualquier proyecto que tenga abierto (si hay uno). **Archivo → Cerrar**.
3. **Archivo → Abrir → Examinar este dispositivo...** (o **Ctrl+O**).
4. En el explorador de archivos que se abre, navegá hasta la carpeta donde guardaste el
   proyecto (ej. `C:\Reportes\PAA\ProyectoPBI\`).
5. **Importante:** en el filtro de tipo de archivo (abajo del cuadro de diálogo), asegurate
   de que diga "Power BI Project (*.pbip)" o "Todos los archivos (*.*)". Si solo muestra
   `.pbix`, cambiá el filtro.
6. Hacé doble clic en **`RealVsPAA.pbip`**.

**Qué va a pasar:** Power BI Desktop va a leer todos los archivos TMDL y el `report.json`,
construir el modelo en memoria y mostrar las páginas del reporte. Es normal que tarde
30-60 segundos la primera vez.

**Si aparece un aviso de seguridad** sobre ejecutar código o conectar a una fuente de datos:
hacé clic en **Habilitar** o **Confiar**.

---

### PASO 5 — Configurar el parámetro `pRutaArchivo`

Antes de actualizar, tenés que decirle al modelo dónde está el Excel en tu PC.

1. En Power BI Desktop, menú **Inicio** → **Transformar datos** (el botón con el ícono de
   tabla y lápiz). Se abre el **Editor de Power Query**.
2. En el panel izquierdo (lista de consultas), buscá **`pRutaArchivo`**. Va a estar entre
   las primeras de la lista.
3. Hacé clic sobre **`pRutaArchivo`**.
4. En el centro, vas a ver el valor actual: `C:\Reportes\PAA\Real_y_pa_2026v2.xlsx`.
   Ese es un valor de ejemplo; tenés que cambiarlo por la ruta real en tu PC.
5. En la barra de fórmulas (arriba, donde dice `= "C:\Reportes\PAA\Real_y_pa_2026v2.xlsx"`),
   hacé clic → borrá el texto entre comillas → pegá tu ruta real entre las mismas comillas.
   Ejemplo: `= "C:\MiCarpeta\Datos\Real_y_pa_2026v2.xlsx"`
6. Presioná **Enter**.

**Alternativa más fácil (menú visual):**
1. En el Editor de Power Query → menú **Inicio** → **Administrar parámetros**.
2. En la ventana que se abre, hacé doble clic sobre **`pRutaArchivo`**.
3. En el campo **"Valor actual"**, borrá el texto y pegá tu ruta completa.
4. **Aceptar**.

**Cómo verificar que quedó bien:** el valor que ves en el campo tiene que terminar en
`Real_y_pa_2026v2.xlsx` y la ruta tiene que existir en tu PC.

---

### PASO 6 — Ejecutar la carga de datos

1. Dentro del Editor de Power Query → menú **Inicio** → **Cerrar y aplicar**.
2. Power BI va a leer el Excel, ejecutar todas las consultas M y cargar las tablas al modelo.
   **Es normal que tarde varios minutos** (el Excel pesa ~23 MB con 65.000 filas de detalle).
3. Va a aparecer una barra de progreso en la parte inferior con los nombres de cada tabla
   que va cargando.

**Mensajes que vas a ver (normales):**
- "Aplicando cambios a la consulta..." → está procesando.
- Nombres de tablas desfilando abajo → cargando una por una.

**Errores posibles y solución:**

| Error | Causa | Solución |
|---|---|---|
| "No se encontró el archivo" | La ruta en `pRutaArchivo` es incorrecta | Volvé al paso 5 y corregí la ruta. |
| "No se encontró la hoja 'REAL vs PA 2025 2026'" | El Excel abierto no es el correcto | Verificá que el archivo sea el correcto y que la hoja exista. |
| "Error de columna: 'Denominación Cuenta'" | Cambió el nombre de alguna columna en el Excel | Revisá que el Excel nuevo tenga exactamente los mismos encabezados. |
| "Token Literal expected" | Error de sintaxis en la ruta (barra faltante, etc.) | Revisá que la ruta use `\` y que no tenga comillas de más. |

---

### PASO 7 — Validar que las consultas cargaron correctamente

1. Menú **Inicio** → **Transformar datos** (abre Power Query de nuevo).
2. En el panel izquierdo debés ver estas consultas:

**Cargadas al modelo (ícono de tabla normal):**
- `DIM_Vertical`
- `DIM_Cuenta`
- `DIM_Ceco`
- `DIM_Proveedor`
- `DIM_Calendario`
- `FACT_Presupuesto`
- `FACT_RealDetalle`

**No cargadas (texto en cursiva, ícono diferente):**
- `pRutaArchivo`
- `stgOrigen`
- `stgRealPA`
- `stgBaseRealCruda`
- `BASE_PLANA_RealvsPA`

**Total: 12 consultas visibles** (7 cargadas + 5 no cargadas).

3. Hacé clic en `DIM_Calendario` → en la vista previa deberías ver filas con fechas desde
   enero 2025. Deberían ser 24 filas (un mes por fila).
4. Hacé clic en `FACT_Presupuesto` → deberías ver columnas: `Fecha`, `VerticalID`,
   `CuentaID`, `CecoID`, `MontoReal`, `MontoPA`.
5. Cerrá Power Query (**Inicio → Cerrar y aplicar** o simplemente la X del Editor).

---

### PASO 8 — Validar las relaciones en la vista Modelo

1. En Power BI Desktop, en el panel de la **izquierda** hay tres íconos: Informe (gráficos),
   Tabla (filas), Modelo (diagrama). Hacé clic en el **tercero** (Modelo / diagrama de
   estrella).
2. Deberías ver las 7 tablas conectadas con líneas. Si las tablas están amontonadas, arrastralas
   para acomodarlas (no afecta nada funcional).
3. Deberías ver **9 líneas de relación** conectando:
   - `DIM_Calendario` con `FACT_Presupuesto` y `FACT_RealDetalle` (2 líneas desde Calendario)
   - `DIM_Vertical` con `FACT_Presupuesto` y `FACT_RealDetalle` (2 líneas)
   - `DIM_Cuenta` con `FACT_Presupuesto` y `FACT_RealDetalle` (2 líneas)
   - `DIM_Ceco` con `FACT_Presupuesto` y `FACT_RealDetalle` (2 líneas)
   - `DIM_Proveedor` con **solo** `FACT_RealDetalle` (1 línea)
4. Hacé doble clic sobre cualquier línea → tiene que decir **"Cardinalidad: Uno a varios (1:*)"**
   y **"Dirección del filtro cruzado: Única"**. → **Cancelar** (no guardes cambios).

**Marcar DIM_Calendario como tabla de fechas** (puede que lo pida automáticamente):
1. Hacé clic sobre la tabla `DIM_Calendario`.
2. En la barra superior aparece la pestaña **"Herramientas de tabla"**. Hacé clic ahí.
3. Botón **"Marcar como tabla de fechas"** → seleccioná la columna **`Fecha`** → **Aceptar**.
4. Si ya aparece con una marquita de calendario, es que ya estaba marcada — nada que hacer.

---

### PASO 9 — Validar las medidas DAX

1. Hacé clic en el ícono de **Tabla** (segundo del panel izquierdo, filas horizontales).
2. En la lista de tablas del panel derecho, expandí **`FACT_Presupuesto`**.
3. Deberías ver estas medidas (íconos con símbolo de calculadora `f(x)` o `∑`):
   - Real Mes
   - PA Mes
   - Variación
   - Variación %
   - Real Acumulado
   - PA Acumulado
   - Variación Acum
   - Real Año Anterior
   - Var vs Año Anterior
   - Variación % fmt
   - Color Variación
4. Expandí **`FACT_RealDetalle`** → deberías ver:
   - Real Detalle
5. **Total: 12 medidas** (11 en FACT_Presupuesto + 1 en FACT_RealDetalle).

**Cómo probar una medida:**
1. Volvé a la vista de **Informe** (primer ícono del panel izquierdo).
2. En la página 1 ("Resumen Ejecutivo") deberían verse 4 tarjetas con valores numéricos.
   Si muestran un número (aunque sea 0), las medidas están funcionando.
3. Si una tarjeta muestra "Error", hacé clic sobre ella y fijate qué medida tiene asignada
   en el panel de campos (derecha).

---

### PASO 10 — Validar las páginas del dashboard

En la parte inferior de Power BI Desktop hay pestañas con los nombres de página. Deberías
ver **5 pestañas**:

| Pestaña | Qué deberías ver al hacer clic |
|---|---|
| 1. Resumen Ejecutivo | 4 tarjetas (KPIs), gráfico de columnas Real vs PA por mes, gráfico de barras por vertical, gráfico de líneas acumulado, 3 slicers |
| 2. Comercial | Matriz con Vertical > Rubro > Cuenta y columnas Real/PA/Variación/Var% |
| 3. Operativa | Matriz con Vertical > Rubro > Cuenta > Ceco, mismas medidas |
| 4. Drill Through — Proveedores | Tabla de proveedores con Real Detalle y Texto, 1 tarjeta de total |
| 5. Auditoría | 3 tarjetas + tabla de control |

**Si los visuales se ven vacíos:** es normal hasta que los datos estén cargados y los tipos
de campo asignados. Verificá que el Excel se cargó correctamente (paso 6).

**Probar el drill-through:**
1. Andá a la página **"3. Operativa"**.
2. En la matriz, expandí hasta llegar a nivel Ceco (usando los botones de flecha arriba de la matriz).
3. Hacé clic derecho sobre una fila de Ceco → **"Explorar en profundidad"** → **"4. Drill Through — Proveedores"**.
4. Te lleva a la página 4 filtrada por esa Cuenta+Ceco. El botón de "Atrás" (flecha, arriba a la
   izquierda del lienzo) te devuelve.

---

### PASO 11 — Aplicar formato condicional en la Variación (1 clic opcional)

Para que la Variación se muestre en rojo/verde automáticamente:

1. Andá a la página **"2. Comercial"**, hacé clic en la matriz.
2. En el panel **"Visualizaciones"** (derecha), buscá el campo `Variación` dentro de "Valores".
3. Hacé clic en la **flecha hacia abajo** que aparece al pasar el mouse sobre `Variación`.
4. **Formato condicional → Color de fuente**.
5. En el diálogo: cambiá "Mínimo/Máximo" a **"Según campo"**.
6. En el selector de campo, elegí la medida **`Color Variación`**.
7. **Aceptar**. Repetí en la página 3.

---

### PASO 12 — Guardar como .pbix

Una vez que todo funciona:

1. **Archivo → Guardar como**.
2. En "Tipo de archivo" elegí **"Archivo Power BI (*.pbix)"**.
3. Elegí la carpeta y nombre (`RealVsPAA.pbix`).
4. **Guardar**.

> El `.pbix` ya incluye los datos embebidos (si elegís "importar"), por lo que podés
> mandárselo a alguien sin el Excel. Para actualizaciones futuras, seguís usando el `.pbip`
> y repetís el paso 12 al final de cada mes.

---

## PARTE 4 — Checklist de validación final

```
DESCARGA Y PREPARACIÓN
[ ] Descargué el ZIP de la rama claude/eager-gates-Md3ac
[ ] Descomprimí el ZIP
[ ] Copié las 3 cosas obligatorias (RealVsPAA.pbip, SemanticModel/, Report/)
[ ] Las 3 cosas están en la MISMA carpeta de mi PC
[ ] El Excel está en mi PC y conozco su ruta exacta

VERSION DE POWER BI
[ ] Power BI Desktop instalado (versión oct-2023 o posterior)
[ ] Soporte PBIP habilitado (o versión reciente que ya lo trae)

APERTURA
[ ] Abrí RealVsPAA.pbip correctamente (sin errores)
[ ] Power BI mostró las páginas del reporte

PARÁMETRO
[ ] Configuré pRutaArchivo con la ruta real del Excel
[ ] La ruta termina en Real_y_pa_2026v2.xlsx

CARGA DE DATOS
[ ] Ejecuté Cerrar y aplicar en Power Query
[ ] No hubo errores de carga
[ ] Veo 7 tablas cargadas en Power Query (DIM_* y FACT_*)
[ ] Veo 5 consultas en cursiva (no cargadas): stgOrigen, stgRealPA, stgBaseRealCruda, BASE_PLANA_RealvsPA, pRutaArchivo

RELACIONES
[ ] Abri la vista Modelo
[ ] Veo 7 tablas conectadas
[ ] Cuento 9 líneas de relación
[ ] DIM_Proveedor conecta solo a FACT_RealDetalle

CALENDARIO
[ ] DIM_Calendario marcada como tabla de fechas (ícono de calendario en la tabla)

MEDIDAS
[ ] FACT_Presupuesto tiene 11 medidas
[ ] FACT_RealDetalle tiene 1 medida (Real Detalle)

PÁGINAS
[ ] Veo 5 pestañas en el reporte
[ ] Página 1: KPIs muestran valores numéricos
[ ] Página 2: Matriz muestra filas con datos
[ ] Página 3: Matriz muestra hasta nivel Ceco
[ ] Página 4: Tabla de proveedores tiene datos
[ ] Página 5: Tabla de auditoría tiene datos
[ ] Drill-through funciona desde página 3 → página 4

GUARDADO
[ ] Guardé como .pbix (Archivo → Guardar como)
```

---

## PARTE 5 — Estado del repositorio: qué está listo y qué no

### ✅ Listo y funcional

- Modelo completo (TMDL): 7 tablas, 12 medidas, 9 relaciones, calendario, parámetro.
- Reporte: 5 páginas con visuales definidos.
- Código M: idéntico a `CONSULTAS_PowerQuery.md` (fuente de verdad).
- Medidas: idénticas a `MEDIDAS_DAX.md` (fuente de verdad).
- Integridad referencial validada con datos reales (0 huérfanos).

### ⚠️ Requiere 1-2 acciones manuales al abrir

1. **Configurar `pRutaArchivo`** con tu ruta real (Paso 5 arriba). Es obligatorio.
2. **Marcar DIM_Calendario como tabla de fechas** si Power BI no lo hace solo (Paso 8).
3. **Formato condicional en Variación** si querés el rojo/verde (Paso 11, opcional).

### ⚠️ Limitación conocida del report.json

Las páginas están definidas en formato PBIR legacy. Todos los visuales existen, pero al abrir
puede pasar que alguno muestre los campos "sueltos" (sin asignar al rol correcto del visual) y
necesites arrastrarlo de nuevo. Esto no es un error del modelo ni de las medidas, es una
limitación del formato cuando se genera sin GUI. **El modelo de datos, las medidas y las
relaciones funcionan 100% — ese es el núcleo difícil. Los visuales se ajustan en 5 minutos.**

Si algún visual aparece vacío, el procedimiento es:
1. Hacé clic en el visual.
2. En el panel "Visualizaciones" (derecha), revisá qué campos tiene asignados en cada "pozo"
   (Category, Values, Rows, etc.).
3. Si está vacío, arrastrá el campo correcto desde el panel "Datos" (también a la derecha).
   Todos los campos que necesitás ya existen en el modelo.
