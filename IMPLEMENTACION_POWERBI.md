# IMPLEMENTACION_POWERBI.md — Registro de lo ejecutado

## Nota sobre el entorno
La construcción se hizo en un **contenedor Linux headless** (sin Power BI Desktop ni GUI).
Por eso el artefacto se entregó como **proyecto Power BI (PBIP / TMDL)** — formato oficial de
Microsoft, basado en texto — en lugar de manipular la interfaz de Desktop. El PBIP se abre en
Power BI Desktop y materializa el modelo completo; desde ahí se hace *Guardar como → .pbix*.

## Cómo abrir
1. Power BI Desktop actualizado, con *Archivo → Opciones → Características de vista previa →
   "Power BI Project (.pbip) save option"* activado (en versiones recientes ya viene activo).
2. Abrir `RealVsPAA.pbip`.
3. Ajustar el parámetro `pRutaArchivo` a la ruta real del `.xlsx` (*Transformar datos →
   Administrar parámetros*) y *Actualizar*.
4. *Archivo → Guardar como* → genera el `.pbix`.

## Estructura de archivos generada
```
RealVsPAA.pbip                         (envoltorio del proyecto)
RealVsPAA.SemanticModel/
  definition.pbism
  .platform
  diagramLayout.json
  definition/
    database.tmdl                      (compatibilityLevel 1567)
    model.tmdl                         (cultura es-ES, orden de consultas)
    expressions.tmdl                   (pRutaArchivo + 3 staging + BASE_PLANA, no cargadas)
    relationships.tmdl                 (9 relaciones)
    tables/
      DIM_Vertical.tmdl  DIM_Cuenta.tmdl  DIM_Ceco.tmdl
      DIM_Proveedor.tmdl  DIM_Calendario.tmdl
      FACT_Presupuesto.tmdl  FACT_RealDetalle.tmdl
RealVsPAA.Report/
  .platform
  definition.pbir
  report.json                          (5 páginas con visuales)
```

## ETAPA 1 — Carga de datos
- 3 consultas staging (`stgOrigen`, `stgRealPA`, `stgBaseRealCruda`) como *expressions* no
  cargadas, con el código M exacto de `CONSULTAS_PowerQuery.md`.
- Parámetro `pRutaArchivo` creado (tipo Texto).
- Calendario generado con M (mensual continuo 2025-01 → último mes).
- `BASE_PLANA_RealvsPA` incluida como alternativa, **no cargada**.

## ETAPA 2 — Modelo
- 5 dimensiones + 2 hechos cargados.
- 9 relaciones 1:* dirección única (ver `MODELO_RELACIONAL.md`).
- `DIM_Calendario` preparada como tabla de fechas; `MesAño` ordenada por `AñoMesOrden`.

## ETAPA 3 — DAX
- 12 medidas implementadas (ver `MODELO_POWERBI.md`), con formato y carpetas de visualización.
- Definiciones idénticas a `MEDIDAS_DAX.md`.

## ETAPA 4 — Reportes
- 5 páginas (ver `PAGINAS_REPORTE.md`).
- Drill-through configurado en la página 4 por `Cuenta` + `Ceco`.

## ETAPA 5 — Validación
- Ver `VALIDACIONES_POWERBI.md`.

## Decisiones técnicas tomadas
- Medidas hospedadas en `FACT_Presupuesto` (salvo `Real Detalle` en `FACT_RealDetalle`).
- `FACT_RealDetalle` filtrada a `>= 2025-01` (decisión validada previamente).
- Formato numérico `#,0` para montos y `0.0%` para porcentajes.
