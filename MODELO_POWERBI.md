# MODELO_POWERBI.md — Diccionario técnico del modelo

Proyecto: **RealVsPAA** (formato PBIP / TMDL). Generado a partir de
`CONSULTAS_PowerQuery.md` y `MEDIDAS_DAX.md` (fuentes de verdad, no modificadas).

## Tablas

| Tabla | Tipo | Carga | Grano |
|---|---|---|---|
| `DIM_Vertical` | Dimensión | Sí | 1 fila por vertical |
| `DIM_Cuenta` | Dimensión | Sí | 1 fila por cuenta |
| `DIM_Ceco` | Dimensión | Sí | 1 fila por ceco |
| `DIM_Proveedor` | Dimensión | Sí | 1 fila por proveedor |
| `DIM_Calendario` | Dimensión (fechas) | Sí | 1 fila por mes |
| `FACT_Presupuesto` | Hecho | Sí | Vertical+Cuenta+Ceco+Mes |
| `FACT_RealDetalle` | Hecho | Sí | Asiento transaccional |
| `stgOrigen`, `stgRealPA`, `stgBaseRealCruda` | Staging (expression) | **No** | — |
| `BASE_PLANA_RealvsPA` | Alternativa express (expression) | **No** | — |
| `pRutaArchivo` | Parámetro (Text) | n/a | ruta del .xlsx |

## Columnas

**DIM_Vertical:** `VerticalID` (int64, clave), `Vertical` (text).
**DIM_Cuenta:** `CuentaID` (int64, clave), `Cuenta` (text), `DenominacionCuenta` (text), `Rubro` (text).
**DIM_Ceco:** `CecoID` (int64, clave), `Ceco` (text).
**DIM_Proveedor:** `ProveedorID` (int64, clave), `Proveedor` (text).
**DIM_Calendario:** `Fecha` (date), `Año` (int64), `NroMes` (int64), `NombreMes` (text), `MesAño` (text, *ordenada por* `AñoMesOrden`), `AñoMesOrden` (int64).
**FACT_Presupuesto:** `Fecha` (date), `VerticalID`, `CuentaID`, `CecoID` (int64), `MontoReal`, `MontoPA` (decimal).
**FACT_RealDetalle:** `Fecha` (date), `VerticalID`, `CuentaID`, `CecoID`, `ProveedorID` (int64), `MontoReal` (decimal), `Texto` (text).

## Medidas (tabla anfitriona y carpeta)

| Medida | Tabla | Carpeta | Formato |
|---|---|---|---|
| Real Mes | FACT_Presupuesto | 01 Real vs PA | #,0 |
| PA Mes | FACT_Presupuesto | 01 Real vs PA | #,0 |
| Variación | FACT_Presupuesto | 01 Real vs PA | #,0 |
| Variación % | FACT_Presupuesto | 01 Real vs PA | 0.0% |
| Real Acumulado | FACT_Presupuesto | 02 Acumulado | #,0 |
| PA Acumulado | FACT_Presupuesto | 02 Acumulado | #,0 |
| Variación Acum | FACT_Presupuesto | 02 Acumulado | #,0 |
| Real Año Anterior | FACT_Presupuesto | 03 Interanual | #,0 |
| Var vs Año Anterior | FACT_Presupuesto | 03 Interanual | #,0 |
| Variación % fmt | FACT_Presupuesto | 04 Formato | texto |
| Color Variación | FACT_Presupuesto | 04 Formato | texto (hex) |
| Real Detalle | FACT_RealDetalle | 05 Detalle | #,0 |

> Las definiciones DAX son idénticas a `MEDIDAS_DAX.md`.

## Parámetro y refresco
`pRutaArchivo` apunta al `.xlsx`. Para refrescar: reemplazar el archivo (mismo nombre y
estructura) y *Actualizar*. Detalle en `GUIA_PowerBI.md`.

## Calendario como tabla de fechas
`DIM_Calendario` está pensada como tabla de fechas (columna `Fecha`). Tras abrir el PBIP,
si Power BI no la marcó sola, hacé *Herramientas de tabla → Marcar como tabla de fechas →
Fecha*. Es lo único manual del modelo.
