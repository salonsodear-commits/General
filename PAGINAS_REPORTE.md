# PAGINAS_REPORTE.md — Detalle de visuales implementados

Definido en `RealVsPAA.Report/report.json`. 5 páginas (lienzo 1280×720).

## Página 1 — "1. Resumen Ejecutivo"
| Visual | Tipo | Campos / Medidas |
|---|---|---|
| Título | Textbox | "Resumen Ejecutivo — Real vs Presupuesto (PAA)" |
| KPI Real | Card | `Real Mes` |
| KPI PA | Card | `PA Mes` |
| KPI Variación | Card | `Variación` |
| KPI Var % | Card | `Variación %` |
| Real vs PA por mes | Columnas agrupadas | Eje: `MesAño`; Valores: `Real Mes`, `PA Mes` |
| Real vs PA por vertical | Barras agrupadas | Eje: `Vertical`; Valores: `Real Mes`, `PA Mes` |
| Tendencia acumulada | Líneas | Eje: `MesAño`; Valores: `Real Acumulado`, `PA Acumulado` |
| Slicers | Segmentador | `Vertical`, `Rubro`, `MesAño` |

## Página 2 — "2. Comercial"
| Visual | Tipo | Campos / Medidas |
|---|---|---|
| Matriz | Matrix | Filas: `Vertical` > `Rubro` > `Cuenta`; Valores: `Real Mes`, `PA Mes`, `Variación`, `Variación %` |
| Slicers | Segmentador | `Vertical`, `MesAño` |

## Página 3 — "3. Operativa"
| Visual | Tipo | Campos / Medidas |
|---|---|---|
| Matriz de apertura | Matrix | Filas: `Vertical` > `Rubro` > `Cuenta` > `Ceco`; Valores: `Real Mes`, `PA Mes`, `Variación`, `Variación %` |
| Slicers | Segmentador | `Rubro`, `MesAño` |

> Formato condicional en `Variación`: aplicar *Color de fuente → Según campo →
> `Color Variación`* (un clic en Desktop; la medida ya existe).

## Página 4 — "4. Drill Through — Proveedores"
| Visual | Tipo | Campos / Medidas |
|---|---|---|
| Título | Textbox | Detalle de proveedores (solo Real) |
| KPI Real Detalle | Card | `Real Detalle` |
| Tabla de detalle | Table | `Proveedor`, `Cuenta`, `Ceco`, `Real Detalle`, `Texto` |

- **Drill-through** configurado por `Cuenta` + `Ceco`. Desde las matrices de las páginas 2/3,
  clic derecho sobre una Cuenta/Ceco → *Explorar en profundidad → 4. Drill Through — Proveedores*.

## Página 5 — "5. Auditoría"
| Visual | Tipo | Campos / Medidas |
|---|---|---|
| KPI Real (presup.) | Card | `Real Mes` |
| KPI Real (detalle) | Card | `Real Detalle` |
| KPI Variación | Card | `Variación` |
| Tabla de control | Table | `Vertical`, `Cuenta`, `Ceco`, `Real Mes`, `Real Detalle`, `Variación` |

Sirve para comparar `Real Mes` (agregado) vs `Real Detalle` (transaccional) y detectar
inconsistencias por cuenta/ceco.

> Nota: `report.json` está en formato PBIR legacy. Si algún visual necesita un retoque menor
> al abrir (p. ej. reubicar o reasignar un campo), se hace en segundos en Desktop. El modelo,
> las medidas y las relaciones quedan 100% operativos.
