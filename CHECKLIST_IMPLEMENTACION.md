# CHECKLIST_IMPLEMENTACION.md

## Etapa 1 — Carga de datos
- [x] Parámetro `pRutaArchivo` (Text)
- [x] `stgOrigen` (M exacto, no cargada)
- [x] `stgRealPA` (header fila 3, no cargada)
- [x] `stgBaseRealCruda` (filtro ≥2025, no cargada)
- [x] `BASE_PLANA_RealvsPA` (alternativa, no cargada)
- [x] Tipos de datos forzados (date / int64 / decimal / text)
- [x] Limpieza de nulos en montos → 0
- [x] Joins + expansiones (NestedJoin → IDs)
- [x] `DIM_Calendario` generado con M

## Etapa 2 — Modelo
- [x] 5 dimensiones cargadas
- [x] 2 fact tables cargadas
- [x] 9 relaciones (1:*, dirección única)
- [x] `DIM_Proveedor` solo a `FACT_RealDetalle`
- [x] `MesAño` ordenada por `AñoMesOrden`
- [ ] Marcar `DIM_Calendario` como tabla de fechas *(1 clic en Desktop si no es automático)*

## Etapa 3 — DAX
- [x] 12 medidas implementadas
- [x] Formatos (#,0 y 0.0%)
- [x] Carpetas de visualización (01..05)

## Etapa 4 — Reportes
- [x] Página 1 Resumen Ejecutivo (KPIs, columnas, barras, líneas, slicers)
- [x] Página 2 Comercial (matriz Vertical>Rubro>Cuenta)
- [x] Página 3 Operativa (matriz hasta Ceco)
- [x] Página 4 Drill Through Proveedores
- [x] Página 5 Auditoría
- [x] Drill-through por Cuenta + Ceco
- [ ] Formato condicional en `Variación` con `Color Variación` *(1 clic en Desktop)*

## Etapa 5 — Validación
- [x] Conteos de dimensiones
- [x] Totales Real / PA / Variación
- [x] Integridad referencial (0 huérfanos)
- [x] Rango de calendario

## Entregables documentales
- [x] MODELO_POWERBI.md
- [x] MODELO_RELACIONAL.md
- [x] IMPLEMENTACION_POWERBI.md
- [x] PAGINAS_REPORTE.md
- [x] VALIDACIONES_POWERBI.md
- [x] CHECKLIST_IMPLEMENTACION.md
- [x] REVISION_ARQUITECTURA.md

## Artefacto Power BI
- [x] Proyecto PBIP (`RealVsPAA.pbip` + SemanticModel + Report)
- [ ] `.pbix` final *(se obtiene abriendo el PBIP en Desktop → Guardar como)*

## No modificado (fuentes de verdad)
- [x] CONSULTAS_PowerQuery.md — intacto
- [x] MEDIDAS_DAX.md — intacto
- [x] GUIA_PowerBI.md — intacto
