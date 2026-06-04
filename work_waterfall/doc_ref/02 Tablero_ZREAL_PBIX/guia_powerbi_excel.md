# Guía paso a paso — Tablero de segmentación ZREAL (Power BI / Excel)

Construcción del tablero de OPEX por Vertical / Unidad de Negocio a partir de
`Real_y_pa_2026v2.xlsx` → hoja `Base Real`, aplicando las reglas de
`reglas_segmentacion.csv`. Dos caminos: **Power BI** (recomendado) y **Excel + Tabla dinámica**.

> La `Base Real` ya trae casi todo decodificado en origen. El trabajo de modelado es:
> (1) validar la decodificación, (2) clasificar directo/indirecto, (3) preparar el prorrateo
> (driver de venta **PENDIENTE DE VALIDAR**), (4) visualizar.

---

## CAMINO A — Power BI Desktop

### Paso 1 — Conectar a los datos
1. `Inicio → Obtener datos → Excel` → elegí `Real_y_pa_2026v2.xlsx`.
2. En el Navegador, tildá la hoja **`Base Real`** → **Transformar datos** (abre Power Query).

### Paso 2 — Decodificar el CECO en Power Query (M)
En el editor de consultas, `Agregar columna → Columna personalizada`. Pegá estas columnas
(una por una, o todo el bloque en el editor avanzado dentro de un `Table.AddColumn`):

```m
// Limpieza del CECO
CECO        = Text.Trim([Centro de coste]),

// Descomposición por posiciones (1 / 2-3 / 4-6 / 7-10)
Letra       = Text.Start([CECO], 1),
NegArea     = Text.Middle([CECO], 1, 2),
ProdSector  = Text.Middle([CECO], 3, 3),
ZonaCECO    = Text.Middle([CECO], 6, 4),

// Tipología inferida del propio código (R03/R04/R05)
Tipologia   = if [NegArea] = "LE" then "Locación"
              else if Text.Select([NegArea], {"0".."9"}) = [NegArea] then "Directo"
              else "Indirecto",

// Banderas de validación (deberían dar todo OK salvo zonas C6)
ChkLargo    = if Text.Length([CECO]) = 10 then "OK" else "REVISAR",
ChkTipo     = if Text.Lower([Tipologia]) = Text.Lower([#"TIPO CECO"])
                 or [Tipologia] = "Locación" then "OK" else "REVISAR"
```

> El editor avanzado equivalente para una sola columna:
> `= Table.AddColumn(PasoAnterior, "Tipologia", each if Text.Middle([Centro de coste],1,2)="LE" then "Locación" else if Text.Select(Text.Middle([Centro de coste],1,2),{"0".."9"})=Text.Middle([Centro de coste],1,2) then "Directo" else "Indirecto", type text)`

### Paso 3 — Marcar zonas huérfanas (chequeo C6)
`Agregar columna → Columna personalizada`:
```m
ZonaHuerfana = if List.Contains(
    {"901C","902B","902C","915E","916E"}, [ZonaCECO]
  ) then "HUÉRFANA (alta V106 pendiente)" else "OK"
```
Esto te deja visible en el tablero las 228 filas ($25,3M) que el diccionario aún no tiene.

### Paso 4 — Tipar columnas y cerrar
1. `Valor/mon.inf.` → tipo **Número decimal**.
2. `mes año` → tipo **Fecha**.
3. `Inicio → Cerrar y aplicar`.

### Paso 5 — (Opcional) Tabla de venta para el prorrateo — **PENDIENTE DE VALIDAR**
Mientras Comercial/DW no entregue la venta por UN×período, creá una tabla **parámetro** vacía
para no romper el modelo (`Inicio → Especificar datos`), con columnas:
`UN (texto) | mes año (fecha) | Venta (decimal)`. Nombrala `Ventas`.
Relación: `Ventas[mes año]` ↔ `Base Real[mes año]` (cardinalidad muchos-a-muchos o vía tabla de fechas).

### Paso 6 — Medidas DAX
`Modelado → Nueva medida`. Pegá una por una:

```dax
OPEX Total = SUM ( 'Base Real'[Valor/mon.inf.] )

OPEX Directo   = CALCULATE ( [OPEX Total], 'Base Real'[TIPO CECO] = "Directo" )
OPEX Indirecto = CALCULATE ( [OPEX Total], 'Base Real'[TIPO CECO] = "Indirecto" )

% Directo   = DIVIDE ( [OPEX Directo],   [OPEX Total] )
% Indirecto = DIVIDE ( [OPEX Indirecto], [OPEX Total] )

-- Indirecto transversal (a prorratear): excluye sectores dedicados a OC (R19)
OPEX Indirecto Transversal =
CALCULATE (
    [OPEX Indirecto],
    NOT ( 'Base Real'[CODIGO PRODUCTO/SECTOR] IN { "N03","N10","N12","N16","C13" } )
)

-- Indirecto dedicado a OC (candidato a tratar como directo a la Vertical)
OPEX Indirecto Dedicado OC =
CALCULATE (
    [OPEX Indirecto],
    'Base Real'[CODIGO PRODUCTO/SECTOR] IN { "N03","N10","N12","N16","C13" }
)
```

**Prorrateo (parametrizado — se activa cuando exista la tabla `Ventas`):**
```dax
Venta Segmento = SUM ( Ventas[Venta] )

% Incidencia UN =
DIVIDE (
    [Venta Segmento],
    CALCULATE ( [Venta Segmento], ALL ( Ventas[UN] ) )
)

Gasto Indirecto Asignado =
[OPEX Indirecto Transversal] * [% Incidencia UN]

-- Control de cuadre: debe dar = [OPEX Indirecto Transversal] (100%)
Chequeo Cuadre Prorrateo =
SUMX ( VALUES ( Ventas[UN] ), [Gasto Indirecto Asignado] )
```
> El **período de referencia** del `% Incidencia` (mismo mes / mes anterior / acumulado) se ajusta
> filtrando `Ventas[mes año]` en `% Incidencia UN`. Queda `PENDIENTE DE VALIDAR`.

### Paso 7 — Armar las visualizaciones
| Visual | Tipo | Campos |
|---|---|---|
| KPIs | 3 Tarjetas | `OPEX Total`, `% Directo`, `% Indirecto` |
| OPEX por Vertical | Barras | Eje `VERTICAL` · Valor `OPEX Total` |
| OPEX por rubro | Barras horizontales | Eje `Denominación de la cuenta` · Valor `OPEX Total` |
| Evolución | Líneas | Eje `mes año` · Valor `OPEX Total` · Leyenda `TIPO CECO` |
| Vertical × Rubro | Matriz | Filas `VERTICAL` · Columnas `RUBRO EBITDA` · Valor `OPEX Total` |
| Zonas huérfanas | Tabla | `ZonaCECO`, `OPEX Total`, filtro `ZonaHuerfana = HUÉRFANA` |
| Segmentadores | Slicers | `VERTICAL`, `mes año`, `TIPO CECO`, `Denominación de la cuenta` |

### Paso 8 — Publicar / refrescar
`Archivo → Guardar` (.pbix). Para actualizar: `Inicio → Actualizar` (relee el .xlsx).

---

## CAMINO B — Excel + Tabla dinámica (sin Power BI)

### Paso 1 — Cargar con Power Query dentro de Excel
`Datos → Obtener datos → Desde un libro` → `Real_y_pa_2026v2.xlsx` → hoja `Base Real` →
**Transformar datos**. Aplicá las mismas columnas M de los Pasos 2-3 de arriba (el lenguaje es idéntico).
`Cerrar y cargar en… → Solo crear conexión` + **Agregar al modelo de datos**.

### Paso 2 — Tabla dinámica
`Insertar → Tabla dinámica → Usar el modelo de datos de este libro`.
- **Filas:** `VERTICAL` → debajo `Denominación de la cuenta`.
- **Columnas:** `TIPO CECO`.
- **Valores:** Suma de `Valor/mon.inf.`.
- **Filtros / Segmentación:** `mes año`, `ZonaHuerfana`.

### Paso 3 — Medidas DAX en Excel (Power Pivot)
`Power Pivot → Medidas → Nueva medida`. Las fórmulas son **las mismas** del Paso 6
(Excel usa el mismo motor DAX). Empezá con `OPEX Total`, `OPEX Directo`, `OPEX Indirecto`.

### Paso 4 — Gráficos dinámicos
`Insertar → Gráfico dinámico` apuntando a la tabla dinámica:
barras por Vertical, barras por rubro, líneas por `mes año`.

---

## Checklist de validación visual (qué tenés que ver)
- [ ] `OPEX Total` ≈ **6.913.254.737** (cuadra con el total de la base).
- [ ] `% Directo` ≈ 7,4% · `% Indirecto` ≈ 92,6% (4.857 / 60.961 filas).
- [ ] Vertical: PETROLEO domina, luego MINERIA, luego OTRAS OP. DEDICADAS.
- [ ] Tabla de zonas huérfanas muestra `902B` (~$21,7M) y `901C` (~$3,7M).
- [ ] `Chequeo Cuadre Prorrateo` = `OPEX Indirecto Transversal` (cuando cargues `Ventas`).

## Bloqueos conocidos (recordatorio)
- **Venta por UN×período** no está en el archivo → el prorrateo queda inactivo hasta cargar `Ventas`.
- **Período de referencia** del % de incidencia → a confirmar con Control de Gestión.
- **Zonas C6** (`901C/902B/902C/915E/916E`) → alta en V106 pendiente (DW).
