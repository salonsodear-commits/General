# MODELO_RELACIONAL.md — Mapa relacional

Esquema **estrella** con dos hechos a distinto grano que comparten dimensiones.

## Diagrama (texto)

```
              DIM_Calendario
                    │ (Fecha)
        ┌───────────┼────────────┐
        │           │            │
   DIM_Vertical  DIM_Cuenta   DIM_Ceco        DIM_Proveedor
        │           │            │                  │
        ├──────┬────┴────┬───────┤                  │
        ▼      ▼         ▼       ▼                  ▼
   ┌─────────────────────────┐   ┌──────────────────────────────┐
   │   FACT_Presupuesto       │   │   FACT_RealDetalle            │
   │  (Real agregado + PA)    │   │  (Real transaccional+Provee.) │
   └─────────────────────────┘   └──────────────────────────────┘
```

## Relaciones implementadas (todas 1:* , dirección única dim → fact)

| # | Desde (1) | Hacia (*) | Columnas |
|---|---|---|---|
| 1 | DIM_Calendario | FACT_Presupuesto | Fecha |
| 2 | DIM_Calendario | FACT_RealDetalle | Fecha |
| 3 | DIM_Vertical | FACT_Presupuesto | VerticalID |
| 4 | DIM_Vertical | FACT_RealDetalle | VerticalID |
| 5 | DIM_Cuenta | FACT_Presupuesto | CuentaID |
| 6 | DIM_Cuenta | FACT_RealDetalle | CuentaID |
| 7 | DIM_Ceco | FACT_Presupuesto | CecoID |
| 8 | DIM_Ceco | FACT_RealDetalle | CecoID |
| 9 | DIM_Proveedor | FACT_RealDetalle | ProveedorID |

> En TMDL la relación se declara `fromColumn` = lado *muchos* (la fact) y `toColumn` =
> lado *uno* (la dimensión); el default es *many-to-one*, filtro cruzado *único*.

## Regla de negocio clave
`DIM_Proveedor` se relaciona **solo** con `FACT_RealDetalle`. No hay relación con
`FACT_Presupuesto` porque el presupuesto no tiene proveedor. Al filtrar por proveedor, las
medidas de PA quedan en blanco — comportamiento correcto y esperado.
