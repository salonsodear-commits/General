# MEDIDAS DAX — Real vs Presupuesto (PAA)

> **Cómo crear una medida:** en la vista *Informe* o *Datos*, clic derecho sobre la tabla
> donde querés guardarla → *Nueva medida* → pegás el código. Recomiendo guardarlas todas en
> `FACT_Presupuesto` (o crear una tabla vacía "_Medidas" para tenerlas juntas).
>
> Ajustá los nombres de columna si los cambiaste al armar las consultas. Acá usan los
> nombres generados en `CONSULTAS_PowerQuery.md`.

---

## Bloque 1 — Real vs PA del mes

**`Real Mes`** — Real agregado del presupuesto (tabla Real vs PA). Es el Real "oficial"
que compara contra PA, al mismo grano.
```dax
Real Mes = SUM(FACT_Presupuesto[MontoReal])
```

**`PA Mes`** — Presupuesto (PAA) del período en contexto.
```dax
PA Mes = SUM(FACT_Presupuesto[MontoPA])
```

**`Variación`** — Desvío absoluto Real − PA. Negativo = gasté menos que lo presupuestado
(si es gasto), positivo = me pasé.
```dax
Variación = [Real Mes] - [PA Mes]
```

**`Variación %`** — Desvío relativo. Uso `DIVIDE` para que si el PA es 0 no tire error,
devuelve en blanco.
```dax
Variación % = DIVIDE([Variación], [PA Mes])
```

---

## Bloque 2 — Acumulados (YTD)

> Requieren que `DIM_Calendario` esté marcada como **tabla de fechas** (ver `GUIA_PowerBI.md`).

**`Real Acumulado`** — Real acumulado del año en curso hasta el mes en contexto.
```dax
Real Acumulado = CALCULATE([Real Mes], DATESYTD(DIM_Calendario[Fecha]))
```

**`PA Acumulado`** — PA acumulado del año en curso.
```dax
PA Acumulado = CALCULATE([PA Mes], DATESYTD(DIM_Calendario[Fecha]))
```

**`Variación Acum`** — Desvío acumulado Real − PA.
```dax
Variación Acum = [Real Acumulado] - [PA Acumulado]
```

---

## Bloque 3 — Comparación interanual

**`Real Año Anterior`** — Mismo período del año anterior. Sirve para ver crecimiento real.
```dax
Real Año Anterior = CALCULATE([Real Mes], SAMEPERIODLASTYEAR(DIM_Calendario[Fecha]))
```
> Nota: como el presupuesto arranca en 2025-01, el "año anterior" de 2025 (=2024) queda en
> blanco. Recién tiene sentido pleno comparando 2026 vs 2025.

**`Var vs Año Anterior`** — Diferencia Real actual − Real del año pasado.
```dax
Var vs Año Anterior = [Real Mes] - [Real Año Anterior]
```

---

## Bloque 4 — Detalle de proveedores

**`Real Detalle`** — Real transaccional desde la Base Real. **Es para la página de
proveedores**, no para el comparativo contra PA.
```dax
Real Detalle = SUM(FACT_RealDetalle[MontoReal])
```

---

## `[Real Mes]` vs `[Real Detalle]` — ¿cuándo uso cada uno?

Son **dos Real distintos**, de dos tablas distintas, y NO tienen por qué dar igual:

- **`[Real Mes]`** sale de `FACT_Presupuesto` (tabla Real vs PA). Es el Real **agregado** y
  conciliado contra el presupuesto, al grano cuenta-ceco-mes. **Usalo siempre que compares
  contra PA** (variaciones, acumulados, páginas Resumen y Aperturas).

- **`[Real Detalle]`** sale de `FACT_RealDetalle` (Base Real). Es el Real **transaccional**,
  con apertura por proveedor. **Usalo solo en la página de Detalle Proveedores**, donde no hay
  PA que comparar.

Pueden diferir por criterios de armado de la tabla Real vs PA (ajustes, exclusiones, reclasificaciones).
Por eso **no mezcles** `[Real Detalle]` con `[PA Mes]` en el mismo visual: el comparativo
oficial Real vs PA es siempre con `[Real Mes]`.

---

## (Opcional) Medidas de formato útiles

**`Variación % fmt`** — para mostrar el % con signo y 1 decimal en tarjetas.
```dax
Variación % fmt =
VAR v = [Variación %]
RETURN IF(ISBLANK(v), "—", FORMAT(v, "+0.0%;-0.0%"))
```

**`Color Variación`** — para formato condicional (rojo si me pasé del presupuesto en gasto).
Conectala en *Formato condicional → Color de fuente → Según campo*.
```dax
Color Variación = IF([Variación] > 0, "#C00000", "#1F7A1F")
```
