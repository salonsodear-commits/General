# VALIDACIONES_POWERBI.md — Resultados

Validación ejecutada replicando en pandas la lógica M del modelo (mismas normalizaciones,
mismo filtro `>= 2025-01`), para verificar antes de abrir en Desktop.

## 1) Conteos de dimensiones
| Dimensión | Valores únicos |
|---|---|
| DIM_Vertical | 3 |
| DIM_Cuenta | 58 |
| DIM_Ceco | 63 |
| DIM_Proveedor | 499 |
| DIM_Calendario | 2025-01 → 2026-12 (24 meses) |

> Proveedores baja de 695 (histórico total) a **499** al filtrar `>= 2025-01`, como
> corresponde a la decisión validada.

## 2) Totales de hechos
| Medida | Valor |
|---|---|
| Real Mes (FACT_Presupuesto) | 4.061.558.881,62 |
| PA Mes | 5.891.242.325,61 |
| **Variación** | **-1.829.683.443,99** |
| Real Detalle (FACT_RealDetalle, ≥2025) | 4.105.843.955,48 (30.070 filas) |

> `Real Mes` (4.061 MM) y `Real Detalle` (4.106 MM) difieren ~44 MM (~1,1%). Es **esperado**:
> son orígenes distintos (agregado conciliado vs transaccional). Documentado en `MEDIDAS_DAX.md`.
> Por eso el comparativo oficial Real vs PA usa `Real Mes`, no `Real Detalle`.

## 3) Integridad referencial (clave del modelo estrella)
| Control | Resultado |
|---|---|
| Cuentas en Base Real sin match en DIM_Cuenta | **0** ✔️ |
| Cecos en Base Real sin match en DIM_Ceco | **0** ✔️ |
| Verticales en Base Real sin match en DIM_Vertical | **0** ✔️ |

Ningún ID huérfano: todas las claves de la fact transaccional resuelven contra las
dimensiones. Las relaciones 1:* no generarán filas en blanco por claves no encontradas.

## 4) Relaciones
9 relaciones declaradas (ver `MODELO_RELACIONAL.md`), todas 1:* dirección única.
`DIM_Proveedor` conectada solo a `FACT_RealDetalle` (correcto: sin presupuesto por proveedor).

## 5) Performance / integridad del modelo
- Fact delgadas (solo IDs + montos) → modelo liviano.
- Staging marcadas como no cargadas → no inflan el modelo.
- `MesAño` ordenada por `AñoMesOrden` → ejes cronológicos correctos.
- Calendario continuo sin huecos → time-intelligence (YTD, interanual) consistente.

## 6) Pendiente manual (1 clic)
Marcar `DIM_Calendario` como tabla de fechas si Desktop no lo hace automáticamente.

**Conclusión:** modelo íntegro y consistente. Sin errores de integridad detectados.
