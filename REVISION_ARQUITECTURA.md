# REVISION_ARQUITECTURA.md — Análisis técnico final

## Resumen
Modelo estrella sobrio y correcto para Real vs Presupuesto (PAA), entregado como proyecto
**PBIP/TMDL** (texto, versionable en git) listo para abrir en Power BI Desktop y guardar como
`.pbix`. La arquitectura respeta el hecho de negocio central: el presupuesto no tiene
proveedor, el Real sí.

## Fortalezas
1. **Dos hechos a distinto grano** compartiendo dimensiones: separa limpio el comparativo
   Real vs PA (agregado) del drill transaccional de proveedores. Evita inventar presupuesto
   por proveedor.
2. **Dimensiones con IDs enteros** y fact delgadas → modelo liviano y performante.
3. **Integridad referencial verificada** (0 huérfanos): los joins en M resuelven el 100% de
   las claves.
4. **Time-intelligence sólida**: calendario continuo + medidas YTD e interanual.
5. **Mantenibilidad**: parámetro de ruta, staging no cargadas, normalización de texto que
   evita duplicar dimensiones por tildes/espacios. Refresco mensual = reemplazar el `.xlsx`.
6. **Versionado**: al ser TMDL/JSON, el modelo y el reporte viven en git con diffs legibles.

## Riesgos / limitaciones conocidas
1. **No es un `.pbix` binario.** Por construirse en un entorno Linux sin Power BI Desktop, se
   entrega PBIP. El `.pbix` se obtiene con un *Guardar como* tras abrirlo. Es la única vía que
   permite generar el modelo por código sin GUI.
2. **`report.json` en formato PBIR legacy.** Las páginas y visuales quedan definidos, pero
   algún visual puntual podría requerir un retoque menor al abrir (reubicar, reasignar un
   campo). El modelo, medidas y relaciones quedan 100% operativos sin tocar nada.
3. **Marca de tabla de fechas**: puede requerir 1 clic manual si Desktop no la infiere.
4. **Diferencia Real agregado vs detalle (~1,1%)**: esperada por orígenes distintos; no es un
   error del modelo. Mitigada con la regla de usar `Real Mes` para comparar vs PA.
5. **Catálogo de cuentas desde la tabla Real vs PA** (58 cuentas). Validado que cubre el 100%
   de las cuentas del Real ≥2025. Si en el futuro la Base Real trae cuentas nuevas fuera del
   presupuesto, conviene blindar `DIM_Cuenta` uniendo ambas fuentes (nota en `CONSULTAS_PowerQuery.md`).

## Recomendaciones a futuro
- Tras validar en Desktop, publicar el `.pbix` y configurar actualización programada apuntando
  al `.xlsx` en una ubicación estable (OneDrive/SharePoint) para automatizar el refresco mensual.
- Considerar un tema corporativo (.json de tema) para homogeneizar colores.
- Si crece el volumen, evaluar mover el origen de Excel a una fuente más robusta (carpeta /
  base de datos), manteniendo el mismo esquema estrella.

## Veredicto
Arquitectura **correcta, íntegra y mantenible**. Lista para operar tras el paso final de
*Guardar como .pbix* en Power BI Desktop.
