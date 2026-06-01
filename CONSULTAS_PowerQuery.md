# CONSULTAS POWER QUERY (código M) — Real vs Presupuesto (PAA)

> **Fuente única:** `Real_y_pa_2026v2.xlsx`. No se generan archivos intermedios ni CSV.
> Todo se transforma dentro de Power Query con código M.
>
> **Cómo usar este archivo:** en Power BI Desktop vas a *Inicio → Transformar datos*
> para abrir el Editor de Power Query. Ahí, por cada consulta de abajo hacés
> *Inicio → Nueva consulta → Consulta nula* (o clic derecho en el panel izquierdo →
> *Nueva consulta → Consulta en blanco*), abrís *Ver → Editor avanzado* y pegás el
> bloque de código tal cual. Renombrás la consulta con el nombre que figura en el título.
>
> El paso a paso con clicks está en `GUIA_PowerBI.md`.

---

## 0) Parámetro `pRutaArchivo`

Antes de pegar cualquier consulta, creá el parámetro que guarda la ruta del Excel.
Así, el mes que viene cambiás la ruta en un solo lugar y no tocás código.

**Cómo crearlo:** En el Editor de Power Query → *Inicio → Administrar parámetros →
Nuevo parámetro*:
- **Nombre:** `pRutaArchivo`
- **Tipo:** Texto
- **Valor actual:** la ruta completa de tu archivo, por ejemplo
  `C:\Reportes\PAA\Real_y_pa_2026v2.xlsx`

> Si preferís, dejá el archivo siempre con el mismo nombre y en la misma carpeta;
> así el refresco mensual es solo reemplazar el `.xlsx`.

---

## 1) `_Origen` — conexión al libro  *(Habilitar carga = NO)*

Conecta al `.xlsx` y devuelve la lista de hojas. Es la base que reutilizan las demás.

```m
let
    // Lee el archivo binario desde la ruta del parámetro.
    // El tercer argumento "true" promueve la 1ª fila a encabezado solo a nivel libro;
    // igual cada hoja la reprocesamos a mano más abajo.
    Origen = Excel.Workbook(File.Contents(pRutaArchivo), null, true)
in
    Origen
```

**Pasos clave:** `File.Contents(pRutaArchivo)` abre el binario; `Excel.Workbook(...)`
lo interpreta como libro y deja una tabla con todas las hojas.

> Clic derecho sobre `_Origen` → desmarcar **Habilitar carga** (no va al modelo).

---

## 2) `_JessiCruda` — hoja "REAL vs PA 2025 2026"  *(Habilitar carga = NO)*

Toma la hoja de Jessi, que tiene el **encabezado en la fila 3** (filas 1 y 2 vacías),
limpia columnas vacías y renombra sin tildes ni espacios.

```m
let
    Origen = _Origen,
    // Selecciona la hoja por su nombre EXACTO.
    Hoja = Origen{[Item="REAL vs PA 2025 2026", Kind="Sheet"]}[Data],
    // Quita las 2 primeras filas vacías -> la fila de encabezado queda arriba de todo.
    QuitarFilasSup = Table.Skip(Hoja, 2),
    // Promueve la primera fila a nombres de columna.
    Encabezados = Table.PromoteHeaders(QuitarFilasSup, [PromoteAllScalars=true]),
    // Nos quedamos SOLO con las columnas útiles (descarta "Unnamed", "cuenta ceco",
    // "Cuenta Vertical" y la variación a mano).
    Seleccion = Table.SelectColumns(Encabezados, {
        "Vertical", "Cuenta", "Denominación Cuenta", "Ceco",
        "Denominación Rubro", "mes año", "Monto Real", "Monto PA"
    }),
    // Renombra a nombres limpios (sin tildes ni espacios) para DAX.
    Renombrar = Table.RenameColumns(Seleccion, {
        {"Denominación Cuenta", "DenominacionCuenta"},
        {"Denominación Rubro", "Rubro"},
        {"mes año", "Fecha"}
    }),
    // Saca filas totalmente vacías (por si el Excel trae basura al final).
    SinVacias = Table.SelectRows(Renombrar, each [Vertical] <> null and [Vertical] <> ""),
    // Normaliza texto: recorta espacios y pasa a MAYÚSCULAS para no duplicar dimensiones.
    Normalizar = Table.TransformColumns(SinVacias, {
        {"Vertical", each Text.Upper(Text.Trim(_)), type text},
        {"Cuenta", each Text.Trim(Text.From(_)), type text},
        {"Ceco", each Text.Upper(Text.Trim(Text.From(_))), type text},
        {"DenominacionCuenta", each Text.Trim(_), type text},
        {"Rubro", each Text.Upper(Text.Trim(_)), type text}
    }),
    // null en montos -> 0.
    MontosReal = Table.ReplaceValue(Normalizar, null, 0, Replacer.ReplaceValue, {"Monto Real"}),
    MontosPA = Table.ReplaceValue(MontosReal, null, 0, Replacer.ReplaceValue, {"Monto PA"}),
    // Tipos finales.
    Tipos = Table.TransformColumnTypes(MontosPA, {
        {"Fecha", type date},
        {"Monto Real", type number},
        {"Monto PA", type number}
    })
in
    Tipos
```

**Pasos clave:** `Table.Skip(...,2)` salta las filas vacías; `PromoteHeaders` arma los
nombres; `SelectColumns` tira lo que no sirve; `Text.Upper(Text.Trim(...))` evita que
"Petroleo" y "PETROLEO " cuenten como dos verticales.

---

## 3) `_BaseRealCruda` — hoja "Base Real"  *(Habilitar carga = NO)*

Toma el detalle transaccional (encabezado normal en fila 1) y se queda solo con las
columnas de interés. **Aplica el filtro de fecha `>= 2025-01-01`** para alinear con el
presupuesto (decisión validada).

```m
let
    Origen = _Origen,
    Hoja = Origen{[Item="Base Real", Kind="Sheet"]}[Data],
    // Encabezado normal en la fila 1.
    Encabezados = Table.PromoteHeaders(Hoja, [PromoteAllScalars=true]),
    // Solo las columnas que usamos.
    Seleccion = Table.SelectColumns(Encabezados, {
        "VERTICAL", "Clase de coste", "Centro de coste",
        "Denominacion cuenta contrapartida", "Valor/mon.inf.",
        "mes año", "cuenta ceco", "Texto"
    }),
    // Renombra a nombres limpios y alineados con la tabla de Jessi.
    Renombrar = Table.RenameColumns(Seleccion, {
        {"VERTICAL", "Vertical"},
        {"Clase de coste", "Cuenta"},
        {"Centro de coste", "Ceco"},
        {"Denominacion cuenta contrapartida", "Proveedor"},
        {"Valor/mon.inf.", "MontoReal"},
        {"mes año", "Fecha"}
    }),
    // Normaliza texto igual que en Jessi (clave para que matcheen los IDs).
    Normalizar = Table.TransformColumns(Renombrar, {
        {"Vertical", each Text.Upper(Text.Trim(_)), type text},
        {"Cuenta", each Text.Trim(Text.From(_)), type text},
        {"Ceco", each Text.Upper(Text.Trim(Text.From(_))), type text},
        {"Proveedor", each Text.Upper(Text.Trim(_)), type text}
    }),
    // null en monto -> 0.
    SinNulos = Table.ReplaceValue(Normalizar, null, 0, Replacer.ReplaceValue, {"MontoReal"}),
    // Tipos.
    Tipos = Table.TransformColumnTypes(SinNulos, {
        {"Fecha", type date},
        {"MontoReal", type number}
    }),
    // FILTRO: solo a partir de 2025-01 (alineado con el presupuesto).
    // Si querés ver el histórico completo, comentá/eliminá este paso.
    FiltroFecha = Table.SelectRows(Tipos, each [Fecha] >= #date(2025,1,1))
in
    FiltroFecha
```

**Pasos clave:** misma normalización de texto que Jessi (si no, los IDs no matchearían);
`FiltroFecha` recorta el histórico pre-2025.

---

# DIMENSIONES

> Patrón común: normalizo texto (ya viene de las consultas crudas) → `Table.Distinct`
> para no duplicar → `Table.AddIndexColumn` para el ID entero → tipos finales.

## 4) `DIM_Vertical`

```m
let
    // Junta verticales de ambas fuentes para no perder ninguna.
    Jessi = Table.SelectColumns(_JessiCruda, {"Vertical"}),
    Real = Table.SelectColumns(_BaseRealCruda, {"Vertical"}),
    Union = Table.Combine({Jessi, Real}),
    // Quita duplicados.
    Distinct = Table.Distinct(Union),
    SinNulos = Table.SelectRows(Distinct, each [Vertical] <> null and [Vertical] <> ""),
    Ordenado = Table.Sort(SinNulos, {{"Vertical", Order.Ascending}}),
    // ID entero arrancando en 1.
    ConID = Table.AddIndexColumn(Ordenado, "VerticalID", 1, 1, Int64.Type),
    Tipos = Table.TransformColumnTypes(ConID, {{"VerticalID", Int64.Type}, {"Vertical", type text}})
in
    Tipos
```

## 5) `DIM_Cuenta`

Una fila por **Cuenta** con su denominación y rubro. La cuenta es la clave; tomamos la
descripción de Jessi (que es la "oficial" del presupuesto).

```m
let
    Base = Table.SelectColumns(_JessiCruda, {"Cuenta", "DenominacionCuenta", "Rubro"}),
    Distinct = Table.Distinct(Base),
    SinNulos = Table.SelectRows(Distinct, each [Cuenta] <> null and [Cuenta] <> ""),
    // Si una cuenta apareciera con 2 descripciones, nos quedamos con la primera.
    AgrupadoUnico = Table.Distinct(SinNulos, {"Cuenta"}),
    Ordenado = Table.Sort(AgrupadoUnico, {{"Cuenta", Order.Ascending}}),
    ConID = Table.AddIndexColumn(Ordenado, "CuentaID", 1, 1, Int64.Type),
    Tipos = Table.TransformColumnTypes(ConID, {
        {"CuentaID", Int64.Type}, {"Cuenta", type text},
        {"DenominacionCuenta", type text}, {"Rubro", type text}
    })
in
    Tipos
```

> Nota: si la Base Real tuviera cuentas que no están en Jessi, no aparecerían acá. Como
> filtramos el Real a 2025+ y el presupuesto cubre ese período, en la práctica el catálogo
> de cuentas de Jessi es el correcto. Si querés blindarlo, podés unir cuentas de ambas
> fuentes igual que en `DIM_Vertical`.

## 6) `DIM_Ceco`

```m
let
    Jessi = Table.SelectColumns(_JessiCruda, {"Ceco"}),
    Real = Table.SelectColumns(_BaseRealCruda, {"Ceco"}),
    Union = Table.Combine({Jessi, Real}),
    Distinct = Table.Distinct(Union),
    SinNulos = Table.SelectRows(Distinct, each [Ceco] <> null and [Ceco] <> ""),
    Ordenado = Table.Sort(SinNulos, {{"Ceco", Order.Ascending}}),
    ConID = Table.AddIndexColumn(Ordenado, "CecoID", 1, 1, Int64.Type),
    Tipos = Table.TransformColumnTypes(ConID, {{"CecoID", Int64.Type}, {"Ceco", type text}})
in
    Tipos
```

## 7) `DIM_Proveedor`

Solo existe en la Base Real (el presupuesto no tiene proveedor).

```m
let
    Base = Table.SelectColumns(_BaseRealCruda, {"Proveedor"}),
    Distinct = Table.Distinct(Base),
    SinNulos = Table.SelectRows(Distinct, each [Proveedor] <> null and [Proveedor] <> ""),
    Ordenado = Table.Sort(SinNulos, {{"Proveedor", Order.Ascending}}),
    ConID = Table.AddIndexColumn(Ordenado, "ProveedorID", 1, 1, Int64.Type),
    Tipos = Table.TransformColumnTypes(ConID, {{"ProveedorID", Int64.Type}, {"Proveedor", type text}})
in
    Tipos
```

## 8) `DIM_Calendario`

Calendario **mensual continuo** generado con M (no se importa). Va desde 2025-01 hasta el
último mes con datos de cualquiera de las dos fact.

```m
let
    // Fecha mínima fija (alineada con el presupuesto).
    FechaInicio = #date(2025, 1, 1),
    // Fecha máxima = el mes más grande entre las dos fuentes de hechos.
    MaxJessi = List.Max(_JessiCruda[Fecha]),
    MaxReal = List.Max(_BaseRealCruda[Fecha]),
    FechaFin = List.Max({MaxJessi, MaxReal}),
    // Cantidad de meses entre inicio y fin.
    MesesTotales = (Date.Year(FechaFin) - Date.Year(FechaInicio)) * 12
                   + (Date.Month(FechaFin) - Date.Month(FechaInicio)) + 1,
    // Genera una fecha por mes (primer día de cada mes).
    ListaFechas = List.Transform({0..MesesTotales - 1},
        each Date.AddMonths(FechaInicio, _)),
    Tabla = Table.FromList(ListaFechas, Splitter.SplitByNothing(), {"Fecha"}),
    TipoFecha = Table.TransformColumnTypes(Tabla, {{"Fecha", type date}}),
    // Columnas de calendario.
    ConAnio = Table.AddColumn(TipoFecha, "Año", each Date.Year([Fecha]), Int64.Type),
    ConNroMes = Table.AddColumn(ConAnio, "NroMes", each Date.Month([Fecha]), Int64.Type),
    ConNombreMes = Table.AddColumn(ConNroMes, "NombreMes",
        each Text.Proper(Date.MonthName([Fecha], "es-ES")), type text),
    // "Ene-25" combinando 3 letras del mes + 2 dígitos del año.
    ConMesAnio = Table.AddColumn(ConNombreMes, "MesAño",
        each Text.Proper(Text.Start(Date.MonthName([Fecha], "es-ES"), 3))
             & "-" & Text.End(Text.From(Date.Year([Fecha])), 2), type text),
    // Orden numérico aaaamm para que "Ene-25" se ordene bien (no alfabéticamente).
    ConOrden = Table.AddColumn(ConMesAnio, "AñoMesOrden",
        each Date.Year([Fecha]) * 100 + Date.Month([Fecha]), Int64.Type)
in
    ConOrden
```

**Pasos clave:** `List.Transform({0..N}, each Date.AddMonths(...))` arma la serie mensual;
`AñoMesOrden` (aaaamm) sirve para ordenar `MesAño` correctamente en los visuales.

---

# HECHOS (FACT)

> Reemplazo los textos por los IDs de las dimensiones con `Table.NestedJoin` + `ExpandTableColumn`.
> Así las fact quedan **delgadas**: solo fecha, IDs y montos.

## 9) `FACT_Presupuesto`

Real **agregado** + PA, al grano Cuenta+Ceco+Vertical+Mes. No tiene proveedor.

```m
let
    Base = _JessiCruda,
    // --- Vertical -> VerticalID ---
    JoinVert = Table.NestedJoin(Base, {"Vertical"}, DIM_Vertical, {"Vertical"}, "dV", JoinKind.LeftOuter),
    ExpVert = Table.ExpandTableColumn(JoinVert, "dV", {"VerticalID"}),
    // --- Cuenta -> CuentaID ---
    JoinCta = Table.NestedJoin(ExpVert, {"Cuenta"}, DIM_Cuenta, {"Cuenta"}, "dC", JoinKind.LeftOuter),
    ExpCta = Table.ExpandTableColumn(JoinCta, "dC", {"CuentaID"}),
    // --- Ceco -> CecoID ---
    JoinCeco = Table.NestedJoin(ExpCta, {"Ceco"}, DIM_Ceco, {"Ceco"}, "dCe", JoinKind.LeftOuter),
    ExpCeco = Table.ExpandTableColumn(JoinCeco, "dCe", {"CecoID"}),
    // Solo IDs + fecha + montos -> fact delgada.
    Final = Table.SelectColumns(ExpCeco, {
        "Fecha", "VerticalID", "CuentaID", "CecoID", "Monto Real", "Monto PA"
    }),
    Renombrar = Table.RenameColumns(Final, {{"Monto Real", "MontoReal"}, {"Monto PA", "MontoPA"}}),
    Tipos = Table.TransformColumnTypes(Renombrar, {
        {"Fecha", type date}, {"VerticalID", Int64.Type},
        {"CuentaID", Int64.Type}, {"CecoID", Int64.Type},
        {"MontoReal", type number}, {"MontoPA", type number}
    })
in
    Tipos
```

## 10) `FACT_RealDetalle`

Detalle transaccional con proveedor. Grano = asiento. Real solamente (sin PA).

```m
let
    Base = _BaseRealCruda,
    JoinVert = Table.NestedJoin(Base, {"Vertical"}, DIM_Vertical, {"Vertical"}, "dV", JoinKind.LeftOuter),
    ExpVert = Table.ExpandTableColumn(JoinVert, "dV", {"VerticalID"}),
    JoinCta = Table.NestedJoin(ExpVert, {"Cuenta"}, DIM_Cuenta, {"Cuenta"}, "dC", JoinKind.LeftOuter),
    ExpCta = Table.ExpandTableColumn(JoinCta, "dC", {"CuentaID"}),
    JoinCeco = Table.NestedJoin(ExpCta, {"Ceco"}, DIM_Ceco, {"Ceco"}, "dCe", JoinKind.LeftOuter),
    ExpCeco = Table.ExpandTableColumn(JoinCeco, "dCe", {"CecoID"}),
    JoinProv = Table.NestedJoin(ExpCeco, {"Proveedor"}, DIM_Proveedor, {"Proveedor"}, "dP", JoinKind.LeftOuter),
    ExpProv = Table.ExpandTableColumn(JoinProv, "dP", {"ProveedorID"}),
    Final = Table.SelectColumns(ExpProv, {
        "Fecha", "VerticalID", "CuentaID", "CecoID", "ProveedorID", "MontoReal", "Texto"
    }),
    Tipos = Table.TransformColumnTypes(Final, {
        {"Fecha", type date}, {"VerticalID", Int64.Type}, {"CuentaID", Int64.Type},
        {"CecoID", Int64.Type}, {"ProveedorID", Int64.Type},
        {"MontoReal", type number}, {"Texto", type text}
    })
in
    Tipos
```

---

## ¿Por qué DOS tablas de hechos?

El presupuesto (PA/PAA) **solo existe a nivel Cuenta + Ceco + Mes**: nadie presupuesta por
proveedor. El Real, en cambio, sí tiene apertura por proveedor en la Base Real.

Si metiéramos todo en una sola fact, tendríamos que "inventar" proveedor en las filas de
presupuesto (o repetir el PA en cada proveedor, inflando el total). Las dos cosas están mal.

La solución correcta de modelo estrella es **dos fact a distinto grano** compartiendo las
mismas dimensiones (calendario, vertical, cuenta, ceco):

- `FACT_Presupuesto`: grano cuenta-ceco-mes, tiene Real agregado y PA.
- `FACT_RealDetalle`: grano asiento, tiene Real con proveedor.

`DIM_Proveedor` se conecta **solo** a `FACT_RealDetalle`. Cuando filtrás por proveedor, el
PA queda en blanco (correcto: no hay presupuesto a ese nivel). Para el comparativo Real vs PA
usás las medidas sobre `FACT_Presupuesto`; para el drill de proveedores usás las de
`FACT_RealDetalle`. Las dimensiones compartidas hacen que un slicer de Vertical/Cuenta/Ceco/Mes
filtre las dos fact a la vez de forma coherente.

---

# PASO 2 — Versión rápida (alternativa): `BASE_PLANA_RealvsPA`

Tabla única ya limpia, desde la hoja de Jessi. Es la solución express: una sola tabla,
sin modelo. **Limitaciones:** no permite drill a proveedor (no tiene ese dato) y al ser una
sola tabla plana perdés la flexibilidad del modelo estrella (medidas time-intelligence menos
limpias, slicers duplicados, etc.). Si usás el modelo estrella, dejá esta consulta **sin
habilitar carga**.

```m
let
    Origen = _Origen,
    Hoja = Origen{[Item="REAL vs PA 2025 2026", Kind="Sheet"]}[Data],
    QuitarFilasSup = Table.Skip(Hoja, 2),
    Encabezados = Table.PromoteHeaders(QuitarFilasSup, [PromoteAllScalars=true]),
    Seleccion = Table.SelectColumns(Encabezados, {
        "Vertical", "Cuenta", "Denominación Cuenta", "Ceco",
        "Denominación Rubro", "mes año", "Monto Real", "Monto PA"
    }),
    Renombrar = Table.RenameColumns(Seleccion, {
        {"Denominación Cuenta", "DenominacionCuenta"},
        {"Denominación Rubro", "Rubro"},
        {"mes año", "Fecha"}
    }),
    SinVacias = Table.SelectRows(Renombrar, each [Vertical] <> null and [Vertical] <> ""),
    MontosReal = Table.ReplaceValue(SinVacias, null, 0, Replacer.ReplaceValue, {"Monto Real"}),
    MontosPA = Table.ReplaceValue(MontosReal, null, 0, Replacer.ReplaceValue, {"Monto PA"}),
    Renombrar2 = Table.RenameColumns(MontosPA, {{"Monto Real", "MontoReal"}, {"Monto PA", "MontoPA"}}),
    // Variación recalculada como columna (la del Excel la ignoramos).
    ConVariacion = Table.AddColumn(Renombrar2, "Variacion",
        each [MontoReal] - [MontoPA], type number),
    Tipos = Table.TransformColumnTypes(ConVariacion, {
        {"Fecha", type date}, {"MontoReal", type number},
        {"MontoPA", type number}, {"Variacion", type number}
    })
in
    Tipos
```

---

## Resumen de carga al modelo

| Consulta | ¿Carga al modelo? |
|---|---|
| `_Origen`, `_JessiCruda`, `_BaseRealCruda` | **NO** (auxiliares, empiezan con `_`) |
| `DIM_Vertical`, `DIM_Cuenta`, `DIM_Ceco`, `DIM_Proveedor`, `DIM_Calendario` | SÍ |
| `FACT_Presupuesto`, `FACT_RealDetalle` | SÍ |
| `BASE_PLANA_RealvsPA` | NO si usás el modelo estrella (es la alternativa express) |
