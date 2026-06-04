#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, PageBreak, HRFlowable, ListFlowable, ListItem)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import KeepTogether

OUTPUT = "/home/user/General/Documentacion_RealVsPAA.pdf"

# ── Colores corporativos ──────────────────────────────────────────────────────
AZUL      = colors.HexColor("#1F3864")
AZUL_CLARO= colors.HexColor("#2E75B6")
GRIS      = colors.HexColor("#F2F2F2")
GRIS_MED  = colors.HexColor("#D9D9D9")
VERDE     = colors.HexColor("#1F7A1F")
ROJO      = colors.HexColor("#C00000")
BLANCO    = colors.white

# ── Estilos ───────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def estilo(name, parent="Normal", **kw):
    s = ParagraphStyle(name, parent=base[parent], **kw)
    return s

H1  = estilo("H1",  "Heading1", fontSize=20, textColor=AZUL,       spaceAfter=10, spaceBefore=20, leading=24)
H2  = estilo("H2",  "Heading2", fontSize=14, textColor=AZUL_CLARO, spaceAfter=6,  spaceBefore=14, leading=18)
H3  = estilo("H3",  "Heading3", fontSize=11, textColor=AZUL,       spaceAfter=4,  spaceBefore=10, leading=14, fontName="Helvetica-Bold")
H4  = estilo("H4",  "Normal",   fontSize=10, textColor=AZUL_CLARO, spaceAfter=3,  spaceBefore=8,  fontName="Helvetica-Bold")
NOR = estilo("NOR", "Normal",   fontSize=9,  leading=13, spaceAfter=4, alignment=TA_JUSTIFY)
COD = estilo("COD", "Normal",   fontSize=7.5,fontName="Courier", backColor=GRIS, leading=11,
             leftIndent=10, rightIndent=10, spaceAfter=6, spaceBefore=4)
BOX = estilo("BOX", "Normal",   fontSize=9,  leading=13, leftIndent=12, rightIndent=12,
             spaceAfter=6, spaceBefore=4, backColor=colors.HexColor("#EBF3FB"))
ALR = estilo("ALR", "Normal",   fontSize=9,  leading=13, leftIndent=12,
             backColor=colors.HexColor("#FFF2CC"), spaceAfter=6, spaceBefore=4)
TIT_TABLA = estilo("TIT_TABLA","Normal", fontSize=8.5, fontName="Helvetica-Bold",
                    textColor=BLANCO, alignment=TA_CENTER)
CEL = estilo("CEL","Normal", fontSize=8.5, leading=11)
CEL_C = estilo("CEL_C","Normal", fontSize=8.5, leading=11, alignment=TA_CENTER)

def ts_base(col_widths):
    return TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  AZUL),
        ("TEXTCOLOR",    (0,0), (-1,0),  BLANCO),
        ("FONTNAME",     (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,0),  8.5),
        ("ALIGN",        (0,0), (-1,0),  "CENTER"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [BLANCO, GRIS]),
        ("FONTSIZE",     (0,1), (-1,-1), 8.5),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("GRID",         (0,0), (-1,-1), 0.4, GRIS_MED),
        ("LEFTPADDING",  (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING",   (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
    ])

def tabla(data, col_widths, extra_style=None):
    rows = []
    for i, row in enumerate(data):
        r = []
        for cell in row:
            s = TIT_TABLA if i == 0 else CEL
            r.append(Paragraph(str(cell), s))
        rows.append(r)
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    ts = ts_base(col_widths)
    if extra_style:
        ts.add(*extra_style)
    t.setStyle(ts)
    return t

def hr():
    return HRFlowable(width="100%", thickness=1, color=AZUL_CLARO, spaceAfter=6)

def sp(n=6):
    return Spacer(1, n)

def p(txt, style=NOR):
    return Paragraph(txt, style)

def li(items, bullet="•"):
    return ListFlowable(
        [ListItem(p(i), leftIndent=20, bulletColor=AZUL_CLARO) for i in items],
        bulletType="bullet", bulletFontName="Helvetica", bulletFontSize=9,
        leftIndent=10, spaceAfter=2
    )

# ── Portada ───────────────────────────────────────────────────────────────────
def portada():
    PORT = estilo("PORT","Normal",fontSize=28,textColor=BLANCO,alignment=TA_CENTER,
                  fontName="Helvetica-Bold",leading=34)
    SUB  = estilo("SUB","Normal",fontSize=14,textColor=BLANCO,alignment=TA_CENTER,leading=18)
    MET  = estilo("MET","Normal",fontSize=10,textColor=GRIS_MED,alignment=TA_CENTER)

    cover = Table([[""]], colWidths=[19*cm], rowHeights=[27*cm])
    cover.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),AZUL),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))

    inner = [
        sp(60),
        p("Real vs Presupuesto (PAA)", PORT),
        sp(8),
        p("Documentación Funcional y Técnica Completa", SUB),
        sp(4),
        p("Power BI — PBIP Format | Operaciones Complejas", SUB),
        sp(30),
        p("Versión 1.0  |  Junio 2026  |  Uso Interno", MET),
        sp(4),
        p("Preparado por: Área de Datos — Operaciones Complejas", MET),
    ]
    return inner

# ─────────────────────────────────────────────────────────────────────────────
# CONTENIDO
# ─────────────────────────────────────────────────────────────────────────────

def seccion_1():
    out = []
    out += [p("1. RESUMEN EJECUTIVO", H1), hr()]
    out += [p("1.1  ¿Qué es este dashboard?", H2)]
    out += [p("""El dashboard <b>Real vs Presupuesto (PAA)</b> es una solución de Business Intelligence
construida en Power BI que permite comparar, en tiempo real, los gastos operativos reales
de la compañía contra los montos presupuestados (PA — Plan Anual) para el período 2025-2026.
La solución está diseñada para las operaciones del sector de Operaciones Complejas
(exploración de petróleo y minería) y responde a una necesidad crítica de control de gestión:
saber exactamente dónde y cuánto se está gastando respecto de lo planificado.""")]
    out += [sp(), p("1.2  Problema de negocio que resuelve", H2)]
    out += [p("""Antes de esta solución, la comparación entre el gasto real y el presupuesto
requería cruzar manualmente tablas de Excel, proceso propenso a errores, lento y difícil
de mantener. Los usuarios no podían filtrar por vertical de negocio, centro de costos o
período con agilidad, ni detectar desvíos en forma inmediata.""")]
    out += [sp(), p("Beneficios concretos:", H3)]
    out += [li([
        "Reducción del tiempo de análisis de horas a minutos.",
        "Visibilidad inmediata de desvíos entre Real y PA por vertical, cuenta y ceco.",
        "Comparación interanual (2025 vs 2026) automática.",
        "Tabla de auditoría que detecta inconsistencias entre las dos fuentes de datos.",
        "Clasificación CAPEX/OPEX y CO/GT lista para análisis estratégico futuro.",
        "Actualizabilidad simple: basta reemplazar el Excel y hacer Actualizar.",
    ])]
    out += [sp(), p("1.3  Usuarios destinatarios", H2)]
    out += [tabla(
        [["Perfil","Uso principal","Páginas clave"],
         ["Gerente de Operaciones","Ver desvío presupuestario global","Resumen Ejecutivo"],
         ["Controller / Finanzas","Analizar desvíos por cuenta y ceco","Operativa, Detalle Proveedores"],
         ["Área Comercial","Seguimiento por vertical comercial","Comercial"],
         ["Auditor interno","Validar consistencia de datos","Auditoría (interno)"],
         ["Analista de datos","Mantenimiento y evolución","Todas"],
        ],
        [4.5*cm, 8*cm, 5.5*cm]
    )]
    out += [sp(), p("1.4  Principales funcionalidades", H2)]
    out += [li([
        "Segmentador de período (MesAño) sincronizado en todas las páginas.",
        "KPIs de Real Mes, PA Mes y Variación en tarjetas destacadas.",
        "Tabla de detalle por Vertical / Cuenta / Ceco con drill-down.",
        "Evolución mensual en gráfico de líneas o barras.",
        "Acumulado YTD (año hasta la fecha) automático.",
        "Comparación interanual: mismo período año anterior.",
        "Detalle de proveedores con montos reales.",
        "Tabla de auditoría: cruza las dos fuentes e identifica discrepancias.",
        "Clasificación CAPEX_OPEX y CO_GT en tabla DIM_Cuenta.",
        "Página de índice para navegación entre hojas.",
    ])]
    return out

def seccion_2():
    out = []
    out += [p("2. ALCANCE DE LA SOLUCIÓN", H1), hr()]
    out += [p("2.1  Qué cubre", H2)]
    out += [li([
        "Gastos operativos del período enero 2025 — mes más reciente disponible.",
        "Dos fuentes: hoja 'REAL vs PA 2025 2026' (PA y Real consolidado) y hoja 'Base Real' (transaccional SAP).",
        "Dimensiones: Vertical de negocio, Cuenta contable, Centro de costos (Ceco), Proveedor, Calendario.",
        "Medidas: Real mensual, PA mensual, Variación, Variación %, Acumulado YTD, Comparación interanual.",
        "Auditoría automática: detecta qué registros existen en una fuente y no en la otra, o tienen montos distintos.",
    ])]
    out += [sp(), p("2.2  Qué NO cubre (limitaciones actuales)", H2)]
    out += [li([
        "No incluye CAPEX (inversiones de capital) — toda la clasificación actual es OPEX.",
        "No conecta a sistemas SAP/ERP directamente — depende del Excel intermedio.",
        "No incluye forecast ni proyecciones.",
        "La página '5. Entregable Opex' está marcada como '(falta)' — pendiente de construcción.",
        "No tiene alertas automáticas ni envío de reportes por email.",
        "No soporta múltiples archivos Excel simultáneos — un único archivo fuente.",
    ])]
    out += [sp(), p("2.3  Supuestos utilizados", H2)]
    out += [li([
        "El Excel fuente tiene exactamente las hojas 'REAL vs PA 2025 2026' y 'Base Real'.",
        "Las primeras 2 filas de 'REAL vs PA 2025 2026' son encabezados auxiliares y se omiten.",
        "Los campos Vertical, Cuenta, Ceco se normalizan a mayúsculas y sin espacios al importar.",
        "Los montos nulos se reemplazan por 0.",
        "La Base Real filtra solo registros desde enero 2025.",
        "La Variación se interpreta como Real − PA (positivo = gasto mayor al presupuesto).",
        "El color rojo indica gasto mayor al presupuesto; verde, menor.",
    ])]
    return out

def seccion_3():
    out = []
    out += [p("3. ARQUITECTURA GENERAL", H1), hr()]
    out += [p("""La solución sigue una arquitectura de BI en capas, donde cada capa tiene una
responsabilidad específica y los datos fluyen de forma unidireccional desde la fuente
hasta el usuario final.""")]
    out += [sp()]

    arq = Table([
        [p("FUENTE DE DATOS", TIT_TABLA)],
        [p("Excel: Real_y_pa_2026v2.xlsx\nHojas: REAL vs PA 2025 2026 | Base Real", CEL_C)],
        [p("▼", CEL_C)],
        [p("POWER QUERY (ETL)", TIT_TABLA)],
        [p("Parámetro de ruta → stgOrigen → stgRealPA / stgBaseRealCruda\nNormalización, filtrado, renombrado, unión de fuentes", CEL_C)],
        [p("▼", CEL_C)],
        [p("MODELO STAR SCHEMA", TIT_TABLA)],
        [p("5 Tablas DIM + 2 Tablas FACT + 1 Tabla AUDIT\n9 relaciones activas", CEL_C)],
        [p("▼", CEL_C)],
        [p("MEDIDAS DAX", TIT_TABLA)],
        [p("12 medidas: Real Mes, PA Mes, Variación, %, YTD, Interanual, Color, Formato", CEL_C)],
        [p("▼", CEL_C)],
        [p("VISUALIZACIONES (6 páginas)", TIT_TABLA)],
        [p("Índice · Resumen Ejecutivo · Comercial · Operativa · Detalle Proveedores · Auditoría", CEL_C)],
    ], colWidths=[15*cm])
    arq.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,0), AZUL),
        ("BACKGROUND",(0,3),(0,3), AZUL),
        ("BACKGROUND",(0,6),(0,6), AZUL),
        ("BACKGROUND",(0,9),(0,9), AZUL),
        ("BACKGROUND",(0,12),(0,12), AZUL),
        ("BACKGROUND",(0,1),(0,1), colors.HexColor("#EBF3FB")),
        ("BACKGROUND",(0,4),(0,4), colors.HexColor("#EBF3FB")),
        ("BACKGROUND",(0,7),(0,7), colors.HexColor("#EBF3FB")),
        ("BACKGROUND",(0,10),(0,10), colors.HexColor("#EBF3FB")),
        ("BACKGROUND",(0,13),(0,13), colors.HexColor("#EBF3FB")),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("GRID",(0,0),(-1,-1),0.5,GRIS_MED),
        ("TOPPADDING",(0,0),(-1,-1),5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("FONTSIZE",(0,2),(0,2),14),
        ("FONTSIZE",(0,5),(0,5),14),
        ("FONTSIZE",(0,8),(0,8),14),
        ("FONTSIZE",(0,11),(0,11),14),
    ]))

    out += [arq, sp(12)]
    out += [p("Explicación de cada capa:", H3)]
    out += [tabla(
        [["Capa","Tecnología","Responsabilidad"],
         ["Fuente","Excel .xlsx","Datos crudos tal como los genera el sistema operativo (SAP exportado a Excel)."],
         ["Power Query","M Language","Limpieza, normalización, transformación y carga de datos al modelo."],
         ["Modelo","TMDL / AS Tabular","Estructura relacional (star schema) que optimiza consultas DAX."],
         ["DAX","DAX","Cálculos de negocio: acumulados, comparaciones, formatos condicionales."],
         ["Visualizaciones","Power BI Desktop","Presentación interactiva para usuarios finales."],
        ],
        [3*cm, 3*cm, 12*cm]
    )]
    return out

def seccion_4():
    out = []
    out += [p("4. ESTRUCTURA DEL PROYECTO", H1), hr()]
    out += [p("""El proyecto usa el formato <b>PBIP (Power BI Project)</b>, que almacena todo como
archivos de texto legibles (no binarios). Esto permite versionarlo con Git y editarlo
con cualquier editor de texto.""")]
    out += [sp(), p("4.1  Árbol de carpetas y archivos", H2)]
    out += [p("""<pre>
RealVsPAA/
├── RealVsPAA.pbip                    ← Punto de entrada. Abrir esto en Power BI Desktop.
│
├── RealVsPAA.SemanticModel/          ← Todo el modelo de datos
│   ├── definition.pbism              ← Metadatos del modelo (formato JSON)
│   ├── .platform                     ← ID único del modelo
│   ├── diagramLayout.json            ← Posición de tablas en la vista de modelo
│   └── definition/
│       ├── model.tmdl                ← Configuración global (cultura es-ES)
│       ├── database.tmdl             ← Nivel de compatibilidad (1567)
│       ├── expressions.tmdl          ← Parámetro + 4 consultas Power Query
│       ├── relationships.tmdl        ← 9 relaciones entre tablas
│       └── tables/
│           ├── DIM_Vertical.tmdl
│           ├── DIM_Cuenta.tmdl
│           ├── DIM_Ceco.tmdl
│           ├── DIM_Proveedor.tmdl
│           ├── DIM_Calendario.tmdl
│           ├── FACT_Presupuesto.tmdl ← 11 medidas DAX aquí
│           ├── FACT_RealDetalle.tmdl ←  1 medida DAX aquí
│           └── AUDIT_Diferencias.tmdl
│
├── RealVsPAA.Report/                 ← Todo el informe visual
│   ├── definition.pbir               ← Apunta al SemanticModel
│   ├── .platform                     ← ID único del informe
│   └── report.json                   ← Definición completa de páginas y visuales
│
└── Datos/
    └── Real_y_pa_2026v2.xlsx         ← Fuente de datos (actualizable)
</pre>""", COD)]
    out += [sp(), p("4.2  Descripción de cada archivo", H2)]
    out += [tabla(
        [["Archivo","Función","¿Se edita manualmente?"],
         ["RealVsPAA.pbip","Punto de entrada del proyecto. Contiene referencia al Report.","Solo si cambia la estructura de carpetas."],
         ["definition.pbism","Declara el tipo de artefacto (SemanticModel) y versión.","No."],
         ["model.tmdl","Cultura regional, orden de consultas, configuración global.","No habitualmente."],
         ["database.tmdl","Nivel de compatibilidad del motor tabular (1567 = Power BI Premium).","No."],
         ["expressions.tmdl","Parámetro pRutaArchivo y las 4 consultas staging (stgOrigen, stgRealPA, stgBaseRealCruda, BASE_PLANA_RealvsPA).","Sí: para cambiar la ruta del Excel."],
         ["relationships.tmdl","Define las 9 relaciones entre tablas con sus UUID.","No (se gestiona desde Power BI Desktop)."],
         ["tables/*.tmdl","Definición de cada tabla: columnas, tipos, medidas DAX y código M de la partición.","Solo para correcciones avanzadas."],
         ["report.json","Definición completa del informe: páginas, visuales, filtros, configuraciones.","No (se gestiona desde Power BI Desktop)."],
         ["Real_y_pa_2026v2.xlsx","Fuente de datos. Contiene las hojas Base Real y REAL vs PA 2025 2026.","Sí: se reemplaza mensualmente."],
        ],
        [4*cm, 8.5*cm, 5.5*cm]
    )]
    return out

def seccion_5():
    out = []
    out += [p("5. INVENTARIO COMPLETO DE FUENTES DE DATOS", H1), hr()]
    out += [p("""El modelo consume <b>un único archivo Excel</b> que actúa como fuente maestra.
Este archivo es generado (o actualizado) por el área de Control de Gestión a partir de
exportaciones del sistema SAP.""")]
    out += [sp(), p("5.1  Archivo fuente", H2)]
    out += [tabla(
        [["Atributo","Detalle"],
         ["Nombre","Real_y_pa_2026v2.xlsx"],
         ["Ruta actual (parámetro)","Configurable vía pRutaArchivo. Valor por defecto en el archivo TMDL."],
         ["Ruta recomendada en producción","O:\\Nuevos Negocios\\Juliana\\...\\02 PowerBI\\RealVsPAA\\Datos\\"],
         ["Formato","Microsoft Excel (.xlsx)"],
         ["Responsable de actualización","Área de Control de Gestión / Operaciones Complejas"],
         ["Frecuencia de actualización","Mensual (al cierre de cada período)"],
         ["Hojas utilizadas","REAL vs PA 2025 2026  |  Base Real"],
         ["Hojas ignoradas","Cualquier otra hoja existente en el archivo (ej: tablas dinámicas)"],
        ],
        [5*cm, 13*cm]
    )]
    out += [sp(), p("5.2  Hoja: REAL vs PA 2025 2026", H2)]
    out += [p("""Esta hoja contiene el consolidado mensual de gastos Reales y Presupuestados
preparado por Control de Gestión. Es la fuente principal del modelo.""")]
    out += [sp(4), p("Estructura de la hoja:", H3)]
    out += [p("<b>Importante:</b> las primeras 2 filas son encabezados auxiliares y se omiten automáticamente en Power Query.", ALR)]
    out += [tabla(
        [["Columna en Excel","Columna en modelo","Tipo","Descripción","Ejemplo"],
         ["Vertical","Vertical","Texto","Línea de negocio","MINERIA"],
         ["Cuenta","Cuenta","Texto","Código de cuenta contable","5110004"],
         ["Denominación Cuenta","DenominacionCuenta","Texto","Descripción de la cuenta","CO- UNIFORMES"],
         ["Ceco","Ceco","Texto","Centro de costos","CNON10917A"],
         ["Denominación Rubro","Rubro","Texto","Categoría del gasto","GT- UNIFORMES"],
         ["mes año","Fecha","Fecha","Período del registro","01/06/2025"],
         ["Monto Real","MontoReal","Número","Gasto real del período","448.562"],
         ["Monto PA","MontoPA","Número","Presupuesto del período","1.541.666"],
        ],
        [3.5*cm, 3.5*cm, 2*cm, 5*cm, 4*cm]
    )]
    out += [sp(), p("5.3  Hoja: Base Real", H2)]
    out += [p("""Esta hoja contiene el detalle transaccional del gasto real, exportado directamente
desde SAP. Tiene mayor granularidad que la hoja anterior: incluye proveedor y texto
descriptivo de cada imputación.""")]
    out += [tabla(
        [["Columna en Excel","Columna en modelo","Tipo","Descripción","Ejemplo"],
         ["VERTICAL","Vertical","Texto","Línea de negocio (normalizada a mayúsculas)","MINERIA"],
         ["Clase de coste","Cuenta","Texto","Código de cuenta SAP","5110004"],
         ["Centro de coste","Ceco","Texto","Centro de costos SAP","CNON10917A"],
         ["Denominacion cuenta contrapartida","Proveedor","Texto","Razón social del proveedor","PROVEEDORA S.A."],
         ["Valor/mon.inf.","MontoReal","Número","Monto del movimiento contable","448.562"],
         ["mes año","Fecha","Fecha","Período del movimiento","01/06/2025"],
         ["cuenta ceco","(no usado)","Texto","Concatenación auxiliar, no se importa al modelo","5110004-CNON10917A"],
         ["Texto","Texto","Texto","Descripción libre del movimiento SAP","COMPRA UNIFORMES JUNIO"],
        ],
        [4*cm, 3*cm, 2*cm, 4.5*cm, 4.5*cm]
    )]
    out += [sp(4)]
    out += [p("<b>Filtro aplicado:</b> solo se importan registros con Fecha ≥ 01/01/2025. Registros anteriores son descartados automáticamente.", ALR)]
    out += [sp(), p("5.4  Validaciones recomendadas antes de actualizar", H2)]
    out += [li([
        "Verificar que la hoja 'REAL vs PA 2025 2026' existe con exactamente ese nombre.",
        "Verificar que la hoja 'Base Real' existe con exactamente ese nombre.",
        "Confirmar que las columnas tienen los mismos nombres que en la versión anterior.",
        "Confirmar que la columna 'mes año' contiene fechas válidas (no texto).",
        "Verificar que no hay filas vacías intercaladas entre los datos.",
        "Confirmar que los códigos de Cuenta y Ceco son consistentes entre ambas hojas.",
    ])]
    return out

def seccion_6():
    out = []
    out += [p("6. PROCESO COMPLETO DE ACTUALIZACIÓN", H1), hr()]
    out += [p("""Este es el procedimiento paso a paso para actualizar el dashboard cuando
hay nuevos datos disponibles (cierre mensual).""")]
    out += [sp(), p("6.1  Cuándo actualizar", H2)]
    out += [li([
        "Al cierre de cada mes, cuando Control de Gestión habilita los datos reales.",
        "Cuando se carga un nuevo período de presupuesto (PA).",
        "Cuando se corrigen errores en los datos fuente.",
    ])]
    out += [sp(), p("6.2  ¿Qué hay que actualizar en el Excel?", H2)]
    out += [p("""<b>Solo las hojas de datos:</b> 'Base Real' y 'REAL vs PA 2025 2026'.
<b>No es necesario</b> actualizar las tablas dinámicas ni otras hojas auxiliares del Excel —
Power Query lee directamente las hojas de datos, no las tablas dinámicas.""", BOX)]
    out += [sp(), p("6.3  Procedimiento paso a paso", H2)]
    pasos = [
        ("Paso 1: Obtener los datos nuevos",
         "Recibir de Control de Gestión el Excel actualizado con los nuevos meses de Real y PA."),
        ("Paso 2: Reemplazar el archivo",
         "Copiar el nuevo Excel a la carpeta Datos\\ con el mismo nombre (Real_y_pa_2026v2.xlsx). Si el nombre cambió, ver Paso 2b."),
        ("Paso 2b (opcional): Actualizar la ruta",
         "Si el archivo tiene otro nombre o está en otra carpeta: en Power BI Desktop → Inicio → Transformar datos → Editar parámetros → modificar pRutaArchivo."),
        ("Paso 3: Abrir el proyecto",
         "Abrir RealVsPAA.pbip con Power BI Desktop (doble clic)."),
        ("Paso 4: Actualizar el modelo",
         "Clic en Inicio → Actualizar. Esperar que completen todas las consultas (indicador de progreso en la barra inferior)."),
        ("Paso 5: Validar los datos",
         "Revisar las tarjetas de Real Mes y PA Mes en Resumen Ejecutivo. Comparar con los totales conocidos del período."),
        ("Paso 6: Revisar Auditoría",
         "Ir a la página 'Auditoría (interno)'. Si hay diferencias nuevas, analizarlas. Diferencias menores a $1 son normales (redondeo)."),
        ("Paso 7: Guardar",
         "Ctrl+S. Power BI guarda los cambios en los archivos TMDL (no en el Excel)."),
        ("Paso 8 (opcional): Publicar",
         "Si el informe está publicado en Power BI Service: Inicio → Publicar → seleccionar el workspace."),
    ]
    for titulo, desc in pasos:
        out += [p(f"<b>{titulo}</b>", H4), p(desc), sp(4)]
    return out

def seccion_7():
    out = []
    out += [p("7. MODELO DE DATOS", H1), hr()]
    out += [p("""El modelo sigue un <b>esquema estrella (star schema)</b>, que es la arquitectura
estándar de Business Intelligence. Consiste en tablas de hechos (datos numéricos)
rodeadas de tablas de dimensiones (datos descriptivos).""")]
    out += [sp(), p("Concepto clave — Star Schema:", H3)]
    out += [p("""<b>Tabla de hechos (FACT):</b> contiene los números que queremos analizar (montos).
<b>Tabla de dimensión (DIM):</b> contiene los atributos por los que queremos filtrar (Cuenta, Ceco, etc.).
Las relaciones van siempre de FACT a DIM, nunca al revés.""", BOX)]
    out += [sp(), p("7.1  Inventario de tablas", H2)]
    out += [tabla(
        [["Tabla","Tipo","Origen","Función principal","Columnas clave"],
         ["DIM_Vertical","Dimensión","stgRealPA + stgBaseRealCruda","Catálogo de verticales de negocio","VerticalID (PK), Vertical"],
         ["DIM_Cuenta","Dimensión","stgRealPA","Catálogo de cuentas contables con clasificación","CuentaID (PK), Cuenta, Rubro, CAPEX_OPEX, CO_GT"],
         ["DIM_Ceco","Dimensión","stgRealPA + stgBaseRealCruda","Catálogo de centros de costos","CecoID (PK), Ceco"],
         ["DIM_Proveedor","Dimensión","stgBaseRealCruda","Catálogo de proveedores","ProveedorID (PK), Proveedor"],
         ["DIM_Calendario","Dimensión","Generada por M","Tabla de fechas para inteligencia temporal","Fecha (PK), Año, MesAño, AñoMesOrden"],
         ["FACT_Presupuesto","Hechos","stgRealPA","Montos Real y PA mensual por Vertical/Cuenta/Ceco","Fecha, VerticalID, CuentaID, CecoID, MontoReal, MontoPA"],
         ["FACT_RealDetalle","Hechos","stgBaseRealCruda","Detalle transaccional SAP con proveedor y texto","Fecha, VerticalID, CuentaID, CecoID, ProveedorID, MontoReal, Texto"],
         ["AUDIT_Diferencias","Auditoría","stgRealPA + stgBaseRealCruda","Cruce de las dos fuentes para detectar discrepancias","Vertical, Cuenta, Ceco, Fecha, Monto_PA, Monto_Base, Diferencia, Motivo"],
        ],
        [3.5*cm, 2.2*cm, 3*cm, 5*cm, 4.3*cm]
    )]
    out += [sp(), p("7.2  Detalle de cada tabla", H2)]

    # DIM_Vertical
    out += [p("DIM_Vertical", H3)]
    out += [p("Contiene una fila por cada vertical de negocio (ej: MINERIA, PETROLEO). Se construye combinando los valores únicos de Vertical de ambas fuentes para garantizar que todas las verticales aparezcan aunque solo existan en una fuente.")]
    out += [tabla(
        [["Columna","Tipo","Clave","Descripción"],
         ["VerticalID","int64","PK","ID numérico autoincremental generado en Power Query."],
         ["Vertical","string","—","Nombre de la vertical en mayúsculas (ej: MINERIA)."],
        ],[3*cm,2.5*cm,1.5*cm,11*cm])]

    # DIM_Cuenta
    out += [sp(6), p("DIM_Cuenta", H3)]
    out += [p("Catálogo de cuentas contables. Incluye dos columnas de clasificación estratégica calculadas en Power Query.")]
    out += [tabla(
        [["Columna","Tipo","Descripción"],
         ["CuentaID","int64 (PK)","ID numérico autoincremental."],
         ["Cuenta","string","Código de cuenta (ej: 5110004)."],
         ["DenominacionCuenta","string","Descripción legible de la cuenta (ej: CO- UNIFORMES)."],
         ["Rubro","string","Categoría contable (ej: GT- UNIFORMES)."],
         ["CAPEX_OPEX","string","Clasificación de la cuenta. Actualmente todas son OPEX."],
         ["CO_GT","string","Clasificación operativa: CO (Corporate) o GT (General) según el Rubro."],
        ],[3*cm,3*cm,12*cm])]
    out += [p("""<b>Lógica CO_GT:</b> los Rubros BENEFICIOS AL PERSONAL, GASTOS DE RODADOS Y EQUIPOS,
HONORARIOS SERVICIOS CC y MANTENIMIENTO clasifican como CO. El resto clasifica como GT.
Esta clasificación es metadata estratégica futura — actualmente no afecta los cálculos principales.""", BOX)]

    # DIM_Ceco
    out += [sp(6), p("DIM_Ceco", H3)]
    out += [p("Catálogo de centros de costos. Se construye igual que DIM_Vertical: union de ambas fuentes.")]
    out += [tabla(
        [["Columna","Tipo","Descripción"],
         ["CecoID","int64 (PK)","ID numérico autoincremental."],
         ["Ceco","string","Código del centro de costos en mayúsculas (ej: CNON10917A)."],
        ],[3*cm,3*cm,12*cm])]

    # DIM_Proveedor
    out += [sp(6), p("DIM_Proveedor", H3)]
    out += [p("Catálogo de proveedores. Solo existe en la Base Real (no en la hoja de PA).")]
    out += [tabla(
        [["Columna","Tipo","Descripción"],
         ["ProveedorID","int64 (PK)","ID numérico autoincremental."],
         ["Proveedor","string","Razón social del proveedor en mayúsculas."],
        ],[3*cm,3*cm,12*cm])]

    # DIM_Calendario
    out += [sp(6), p("DIM_Calendario", H3)]
    out += [p("""Tabla de fechas generada dinámicamente en Power Query. Se calcula automáticamente
el rango desde enero 2025 hasta el mes más reciente disponible en los datos.
Es fundamental para las funciones de inteligencia temporal de DAX (YTD, SAMEPERIODLASTYEAR).""")]
    out += [tabla(
        [["Columna","Tipo","Descripción","Ejemplo"],
         ["Fecha","date (PK)","Primer día de cada mes. Es la clave de unión con las FACT.","2025-06-01"],
         ["Año","int64","Año del período.","2025"],
         ["NroMes","int64","Número del mes (1-12).","6"],
         ["NombreMes","string","Nombre del mes en español.","Junio"],
         ["MesAño","string","Etiqueta de período para segmentadores y ejes.","Jun-25"],
         ["AñoMesOrden","int64","Entero de ordenamiento cronológico (YYYYMM).","202506"],
        ],[2.5*cm,2*cm,9*cm,3.5*cm])]
    out += [p("""<b>¿Por qué MesAño se ordena por AñoMesOrden?</b> El texto 'Jun-25' se ordenaría
alfabéticamente (Abr, Ago, Dic...) en lugar de cronológicamente. La columna AñoMesOrden
(202506) garantiza el orden correcto en gráficos y segmentadores.""", BOX)]

    # FACT_Presupuesto
    out += [sp(6), p("FACT_Presupuesto", H3)]
    out += [p("""Tabla de hechos principal. Contiene una fila por combinación de Fecha + Vertical + Cuenta + Ceco,
con el monto real y el presupuestado. Es la tabla donde viven la mayoría de las medidas DAX.""")]
    out += [tabla(
        [["Columna","Tipo","Descripción"],
         ["Fecha","date","Clave foránea → DIM_Calendario.Fecha."],
         ["VerticalID","int64","Clave foránea → DIM_Vertical.VerticalID."],
         ["CuentaID","int64","Clave foránea → DIM_Cuenta.CuentaID."],
         ["CecoID","int64","Clave foránea → DIM_Ceco.CecoID."],
         ["MontoReal","double","Gasto real del período. Fuente: col 'Monto Real' del Excel."],
         ["MontoPA","double","Presupuesto del período. Fuente: col 'Monto PA' del Excel."],
        ],[3*cm,3*cm,12*cm])]

    # FACT_RealDetalle
    out += [sp(6), p("FACT_RealDetalle", H3)]
    out += [p("""Tabla de hechos de detalle transaccional. Cada fila es un movimiento contable
de SAP. Tiene mayor granularidad que FACT_Presupuesto: incluye Proveedor y Texto descriptivo.
Solo contiene montos reales (no tiene PA).""")]
    out += [tabla(
        [["Columna","Tipo","Descripción"],
         ["Fecha","date","Clave foránea → DIM_Calendario.Fecha."],
         ["VerticalID","int64","Clave foránea → DIM_Vertical.VerticalID."],
         ["CuentaID","int64","Clave foránea → DIM_Cuenta.CuentaID."],
         ["CecoID","int64","Clave foránea → DIM_Ceco.CecoID."],
         ["ProveedorID","int64","Clave foránea → DIM_Proveedor.ProveedorID."],
         ["MontoReal","double","Monto del movimiento contable SAP."],
         ["Texto","string","Descripción libre del movimiento (ej: COMPRA UNIFORMES JUNIO)."],
        ],[3*cm,3*cm,12*cm])]

    # AUDIT_Diferencias
    out += [sp(6), p("AUDIT_Diferencias", H3)]
    out += [p("""Tabla auxiliar de auditoría. No forma parte del análisis principal. Su función es
detectar inconsistencias entre las dos fuentes de datos. Contiene solo las filas donde
existe una diferencia de más de $0.01 entre lo que figura en cada fuente.""")]
    out += [tabla(
        [["Columna","Tipo","Descripción"],
         ["Vertical","string","Vertical del registro en discrepancia."],
         ["Cuenta","string","Cuenta contable del registro."],
         ["Ceco","string","Centro de costos del registro."],
         ["Fecha","date","Período del registro."],
         ["Monto_PA","double","Monto según stgRealPA (hoja REAL vs PA)."],
         ["Monto_Base","double","Monto según stgBaseRealCruda (hoja Base Real)."],
         ["Diferencia","double","Monto_PA − Monto_Base. Distinto de cero para todas las filas."],
         ["Motivo","string","Explicación de la discrepancia (ver valores posibles abajo)."],
        ],[3*cm,2.5*cm,12.5*cm])]
    out += [p("""<b>Valores posibles de Motivo:</b><br/>
• <i>Solo en Base Real (no está en REAL vs PA)</i>: el movimiento existe en SAP pero no en el consolidado de PA.<br/>
• <i>Solo en REAL vs PA (no está en Base Real)</i>: aparece en el consolidado pero no en SAP.<br/>
• <i>Diferencia de importe en ambas fuentes</i>: existe en ambas pero con montos distintos.""", BOX)]
    return out

def seccion_8():
    out = []
    out += [p("8. RELACIONES DEL MODELO", H1), hr()]
    out += [p("""El modelo tiene <b>9 relaciones activas</b>, todas de tipo Muchos a Uno (desde FACT hacia DIM),
con dirección de filtro Simple (las DIM filtran a las FACT, no al revés).
Adicionalmente, AUDIT_Diferencias tiene 3 relaciones directas por texto.""")]
    out += [sp(), p("Diagrama de relaciones:", H3)]

    diagrama = [
        ["","DIM_Calendario","","",""],
        ["","Fecha (PK)","","",""],
        ["","↑  *:1  ↑","","",""],
        ["FACT_Presupuesto","←→","[Centro]","←→","FACT_RealDetalle"],
        ["Fecha","","","","Fecha"],
        ["VerticalID","→ DIM_Vertical ←","","","VerticalID"],
        ["CuentaID","→ DIM_Cuenta ←","","","CuentaID"],
        ["CecoID","→ DIM_Ceco ←","","","CecoID"],
        ["","","","","ProveedorID → DIM_Proveedor"],
    ]

    out += [tabla(
        [["#","Tabla origen","Columna origen","Tabla destino","Columna destino","Cardinalidad","Dirección","Estado"],
         ["1","FACT_Presupuesto","Fecha","DIM_Calendario","Fecha","*:1","Simple","Activa"],
         ["2","FACT_RealDetalle","Fecha","DIM_Calendario","Fecha","*:1","Simple","Activa"],
         ["3","FACT_Presupuesto","VerticalID","DIM_Vertical","VerticalID","*:1","Simple","Activa"],
         ["4","FACT_RealDetalle","VerticalID","DIM_Vertical","VerticalID","*:1","Simple","Activa"],
         ["5","FACT_Presupuesto","CuentaID","DIM_Cuenta","CuentaID","*:1","Simple","Activa"],
         ["6","FACT_RealDetalle","CuentaID","DIM_Cuenta","CuentaID","*:1","Simple","Activa"],
         ["7","FACT_Presupuesto","CecoID","DIM_Ceco","CecoID","*:1","Simple","Activa"],
         ["8","FACT_RealDetalle","CecoID","DIM_Ceco","CecoID","*:1","Simple","Activa"],
         ["9","FACT_RealDetalle","ProveedorID","DIM_Proveedor","ProveedorID","*:1","Simple","Activa"],
         ["10","AUDIT_Diferencias","Cuenta","DIM_Cuenta","Cuenta","*:1","Simple","Activa"],
         ["11","AUDIT_Diferencias","Ceco","DIM_Ceco","Ceco","*:1","Simple","Activa"],
         ["12","AUDIT_Diferencias","Vertical","DIM_Vertical","Vertical","*:1","Simple","Activa"],
        ],
        [0.7*cm,3.5*cm,2.5*cm,3*cm,2.5*cm,1.8*cm,2*cm,1.5*cm]
    )]
    out += [sp(), p("8.1  Justificación y riesgos por relación", H2)]
    rels = [
        ("FACT → DIM_Calendario (rels 1 y 2)",
         "Fundamental para inteligencia temporal. Sin esta relación, DATESYTD y SAMEPERIODLASTYEAR no funcionan.",
         "Sin esta relación, los acumulados YTD y la comparación interanual devuelven BLANK."),
        ("FACT → DIM_Vertical (rels 3 y 4)",
         "Permite filtrar ambas tablas de hechos por vertical de negocio simultáneamente.",
         "Si se elimina, el segmentador de Vertical no filtra los datos."),
        ("FACT → DIM_Cuenta (rels 5 y 6)",
         "Permite filtrar por cuenta contable y usar las clasificaciones CAPEX_OPEX y CO_GT.",
         "Sin esta relación, las columnas de clasificación de DIM_Cuenta no afectan los visuales de FACT."),
        ("FACT → DIM_Ceco (rels 7 y 8)",
         "Permite análisis por centro de costos.",
         "Sin esta relación, el filtro por Ceco no funciona."),
        ("FACT_RealDetalle → DIM_Proveedor (rel 9)",
         "Solo FACT_RealDetalle tiene proveedor (viene de SAP). Permite la página de detalle por proveedor.",
         "Sin esta relación, la página de Detalle de Proveedores no muestra datos."),
        ("AUDIT_Diferencias → DIM_* (rels 10-12)",
         "Permite usar los segmentadores de período y vertical para filtrar también la tabla de auditoría.",
         "Sin estas relaciones, los segmentadores no afectan la página de Auditoría."),
    ]
    for rel, just, riesgo in rels:
        out += [p(f"<b>{rel}</b>", H4),
                p(f"<b>Justificación:</b> {just}"),
                p(f"<b>Riesgo si se elimina:</b> {riesgo}"), sp(6)]
    return out

def seccion_9():
    out = []
    out += [p("9. POWER QUERY — CONSULTAS ETL", H1), hr()]
    out += [p("""Power Query es el motor de transformación de datos de Power BI.
Permite conectarse a las fuentes, limpiar los datos y prepararlos antes de cargarlos al modelo.
Cada consulta es un paso secuencial: la salida de un paso es la entrada del siguiente.""")]
    out += [sp(), p("9.1  Parámetro: pRutaArchivo", H2)]
    out += [p("Es el único punto de configuración de ruta. Cambiar este valor es todo lo necesario si el Excel se mueve de carpeta.")]
    out += [p('expression pRutaArchivo = "C:\\\\Reportes\\\\PAA\\\\Real_y_pa_2026v2.xlsx"\n    meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]', COD)]
    out += [p("<b>Cómo modificarlo:</b> Inicio → Transformar datos → Editar parámetros → cambiar el valor de pRutaArchivo.", BOX)]

    out += [sp(), p("9.2  Consulta: stgOrigen", H2)]
    out += [p("Abre el archivo Excel. Devuelve un objeto con todas las hojas disponibles. Ninguna transformación se aplica aquí.")]
    out += [p("Origen = Excel.Workbook(File.Contents(pRutaArchivo), null, true)", COD)]

    out += [sp(), p("9.3  Consulta: stgRealPA (fuente principal PA + Real)", H2)]
    out += [tabla(
        [["Paso M","Nombre","Transformación","Por qué"],
         ["1","Origen","Referencia a stgOrigen.","Reutiliza la conexión al Excel."],
         ["2","Hoja","Selecciona la hoja 'REAL vs PA 2025 2026'.","Es la hoja de consolidado mensual."],
         ["3","QuitarFilasSup","Omite las primeras 2 filas.","Esas filas son encabezados auxiliares, no datos."],
         ["4","Encabezados","Promueve la fila 3 como encabezados.","Establece los nombres de columna correctos."],
         ["5","Seleccion","Selecciona solo 8 columnas relevantes.","Descarta columnas auxiliares del Excel."],
         ["6","Renombrar","Renombra columnas al estándar del modelo.","Consistencia con el resto del modelo."],
         ["7","SinVacias","Filtra filas donde Vertical es null o vacío.","Elimina subtotales y filas en blanco del Excel."],
         ["8","Normalizar","Convierte Vertical/Ceco/Rubro a mayúsculas y trimea espacios.","Garantiza unión correcta con las DIM."],
         ["9","MontosReal/PA","Reemplaza null por 0 en los montos.","Evita errores en sumas DAX."],
         ["10","Tipos","Aplica tipos de dato definitivos.","Garantiza que Fecha es date y montos son number."],
        ],[2.5*cm,3*cm,6*cm,6.5*cm])]

    out += [sp(), p("9.4  Consulta: stgBaseRealCruda (detalle SAP)", H2)]
    out += [tabla(
        [["Paso M","Nombre","Transformación","Por qué"],
         ["1","Origen","Referencia a stgOrigen.","Reutiliza la conexión al Excel."],
         ["2","Hoja","Selecciona la hoja 'Base Real'.","Exportación directa de SAP."],
         ["3","Encabezados","Promueve primera fila como encabezados.","La hoja Base Real no tiene filas auxiliares."],
         ["4","Seleccion","Selecciona 8 columnas relevantes.","Descarta columnas SAP no utilizadas."],
         ["5","Renombrar","Renombra columnas (VERTICAL→Vertical, Clase de coste→Cuenta, etc.).","Estandariza nombres con el modelo."],
         ["6","Normalizar","Mayúsculas y trim en Vertical, Cuenta, Ceco, Proveedor.","Garantiza unión correcta con las DIM."],
         ["7","SinNulos","Reemplaza null por 0 en MontoReal.","Evita errores en sumas DAX."],
         ["8","Tipos","Aplica tipos definitivos.","Fecha como date, MontoReal como number."],
         ["9","FiltroFecha","Filtra solo registros con Fecha ≥ 01/01/2025.","Limita el volumen de datos a períodos relevantes."],
        ],[2.5*cm,3*cm,6*cm,6.5*cm])]

    out += [sp(), p("9.5  Consulta: BASE_PLANA_RealvsPA (tabla alternativa no cargada)", H2)]
    out += [p("""Esta consulta existe como alternativa de diseño (tabla plana desnormalizada).
<b>No está cargada en el modelo</b> (aparece en Power Query pero no genera tabla en el modelo).
Se mantiene como respaldo o para análisis ad-hoc fuera del modelo star schema.""", ALR)]

    out += [sp(), p("9.6  Construcción de las tablas DIM en Power Query", H2)]
    out += [p("Todas las dimensiones usan el mismo patrón:")]
    out += [p("""SelectColumns → (Combine si hay dos fuentes) → Distinct → SelectRows (sin nulos)
→ Sort → AddIndexColumn (genera el ID) → TransformColumnTypes""", COD)]
    out += [p("""<b>AddIndexColumn</b> genera IDs numéricos secuenciales (1, 2, 3...) que se usan
como claves primarias en las relaciones. Cada vez que se actualiza el modelo,
los IDs se regeneran automáticamente.""", BOX)]
    return out

def seccion_10():
    out = []
    out += [p("10. MEDIDAS DAX", H1), hr()]
    out += [p("""DAX (Data Analysis Expressions) es el lenguaje de fórmulas de Power BI.
Las medidas DAX son cálculos que se evalúan en el contexto de los filtros activos
en cada visual. A diferencia de las columnas calculadas, no almacenan valores
— se calculan al momento de mostrar cada visual.""")]
    out += [sp()]

    medidas = [
        ("Real Mes", "FACT_Presupuesto", "01 Real vs PA", "#,0",
         "SUM(FACT_Presupuesto[MontoReal])",
         "Suma de todos los gastos reales en el período y filtros seleccionados.",
         "Si el usuario filtra Jun-25 y MINERIA, devuelve la suma de MontoReal para ese mes y esa vertical.",
         "Tarjetas de KPI en Resumen Ejecutivo, columnas en matrices.",
         "Cambiar la columna MontoReal de FACT_Presupuesto afectaría esta medida."),

        ("PA Mes", "FACT_Presupuesto", "01 Real vs PA", "#,0",
         "SUM(FACT_Presupuesto[MontoPA])",
         "Suma del presupuesto para el período y filtros seleccionados.",
         "Si el PA de Junio es 60 millones y Real es 47 millones, esta medida devuelve 60.000.000.",
         "Tarjetas de KPI, matrices comparativas.",
         "Depende de que MontoPA no tenga nulos (ya reemplazados por 0 en Power Query)."),

        ("Variación", "FACT_Presupuesto", "01 Real vs PA", "#,0",
         "[Real Mes] - [PA Mes]",
         "Diferencia entre gasto real y presupuesto. Positivo = gastó más de lo planeado.",
         "Real 47M, PA 60M → Variación = -13M (gastó menos, favorable).",
         "Tarjetas, matrices, gráficos de barras.",
         "Depende de Real Mes y PA Mes."),

        ("Variación %", "FACT_Presupuesto", "01 Real vs PA", "0.0%",
         "DIVIDE([Variación], [PA Mes])",
         "Desvío porcentual sobre el presupuesto. DIVIDE evita división por cero (devuelve BLANK si PA=0).",
         "Variación -13M, PA 60M → -21.7%. Se gastó un 21.7% menos que el presupuesto.",
         "Matrices, formato condicional.",
         "Si PA Mes = 0 (sin presupuesto), devuelve BLANK automáticamente."),

        ("Real Acumulado", "FACT_Presupuesto", "02 Acumulado", "#,0",
         "CALCULATE([Real Mes], DATESYTD(DIM_Calendario[Fecha]))",
         "Suma acumulada del gasto real desde el 1° de enero del año en curso hasta el período seleccionado.",
         "Si el filtro está en Jun-25, devuelve la suma de Real de Ene a Jun 2025.",
         "KPIs de acumulado, análisis de cierre de año.",
         "Requiere relación activa entre FACT_Presupuesto y DIM_Calendario."),

        ("PA Acumulado", "FACT_Presupuesto", "02 Acumulado", "#,0",
         "CALCULATE([PA Mes], DATESYTD(DIM_Calendario[Fecha]))",
         "Suma acumulada del presupuesto desde el 1° de enero hasta el período seleccionado.",
         "Permite comparar cuánto se presupuestó acumular vs cuánto se gastó realmente.",
         "KPIs de acumulado.",
         "Requiere relación activa entre FACT_Presupuesto y DIM_Calendario."),

        ("Variación Acum", "FACT_Presupuesto", "02 Acumulado", "#,0",
         "[Real Acumulado] - [PA Acumulado]",
         "Desvío acumulado en el año. Permite ver si el año está en track presupuestario.",
         "Real Acum 280M, PA Acum 360M → Variación Acum -80M (está 80M por debajo del presupuesto anual).",
         "KPIs, gráficos de tendencia.",
         "Depende de Real Acumulado y PA Acumulado."),

        ("Real Año Anterior", "FACT_Presupuesto", "03 Interanual", "#,0",
         "CALCULATE([Real Mes], SAMEPERIODLASTYEAR(DIM_Calendario[Fecha]))",
         "Gasto real del mismo período del año anterior. Útil para análisis de evolución interanual.",
         "Si el filtro es Jun-26, devuelve el Real de Jun-25.",
         "Gráficos comparativos de evolución.",
         "Requiere datos de al menos dos años en el modelo."),

        ("Var vs Año Anterior", "FACT_Presupuesto", "03 Interanual", "#,0",
         "[Real Mes] - [Real Año Anterior]",
         "Diferencia entre el gasto real actual y el del mismo período del año anterior.",
         "Real Jun-26: 50M, Real Jun-25: 47M → Var = +3M (creció 3M vs año anterior).",
         "Análisis de tendencias interanuales.",
         "Si no hay datos del año anterior, devuelve el Real Mes actual."),

        ("Variación % fmt", "FACT_Presupuesto", "04 Formato", "texto",
         'VAR v = [Variación %]\nRETURN IF(ISBLANK(v), "—", FORMAT(v, "+0.0%;-0.0%"))',
         "Versión formateada de Variación %. Muestra + para positivos, - para negativos, y — cuando no hay PA.",
         "PA=0 → muestra '—'. Variación -21.7% → muestra '-21.7%'.",
         "Columnas de texto en matrices donde se necesita formato +/- explícito.",
         "Solo para presentación. No usar en cálculos numéricos."),

        ("Color Variación", "FACT_Presupuesto", "04 Formato", "texto (hex color)",
         'IF([Variación] > 0, "#C00000", "#1F7A1F")',
         "Devuelve un código de color hexadecimal según el signo de la Variación. Rojo si gastó más, verde si gastó menos.",
         "Variación +5M → '#C00000' (rojo). Variación -5M → '#1F7A1F' (verde).",
         "Formato condicional de fondo o fuente en matrices.",
         "El criterio semántico es: gasto mayor al presupuesto = malo = rojo."),

        ("Real Detalle", "FACT_RealDetalle", "05 Detalle", "#,0",
         "SUM(FACT_RealDetalle[MontoReal])",
         "Suma del gasto real desde la tabla de detalle transaccional (SAP). Equivalente a Real Mes pero desde la otra fuente.",
         "Permite cruzar con el proveedor para ver cuánto gastó cada proveedor.",
         "Página Detalle de Proveedores, tabla de auditoría.",
         "Si los valores difieren de Real Mes, la auditoría lo detecta automáticamente."),
    ]

    for nombre, tabla_padre, carpeta, fmt, formula, func, ejemplo, visuales, riesgos in medidas:
        out += [KeepTogether([
            p(f"10.{medidas.index((nombre,tabla_padre,carpeta,fmt,formula,func,ejemplo,visuales,riesgos))+1}  {nombre}", H3),
            tabla(
                [["Atributo","Valor"],
                 ["Tabla","{}".format(tabla_padre)],
                 ["Carpeta (displayFolder)","{}".format(carpeta)],
                 ["Formato","{}".format(fmt)],
                 ["Fórmula","{}".format(formula)],
                 ["Función","{}".format(func)],
                 ["Ejemplo","{}".format(ejemplo)],
                 ["Visuales","{}".format(visuales)],
                 ["Riesgo","{}".format(riesgos)],
                ],[3.5*cm,14.5*cm]),
            sp(8)
        ])]
    return out

def seccion_11():
    out = []
    out += [p("11. PÁGINAS DEL DASHBOARD", H1), hr()]
    pages = [
        ("0. Índice","Página de aterrizaje y navegación. Permite al usuario ir directamente a la sección que le interesa con un clic. Pensada para usuarios no técnicos.","Todos los usuarios","Botones de navegación a cada página."),
        ("1. Resumen Ejecutivo","Vista de alto nivel del desempeño presupuestario global. KPIs destacados y evolución mensual.","Gerentes, Dirección","Tarjetas KPI (Real, PA, Variación), gráfico de evolución, segmentador de período."),
        ("2. Comercial","Análisis del desempeño por vertical de negocio desde la perspectiva comercial.","Área Comercial","Tabla por Vertical, gráfico comparativo, segmentador de período."),
        ("3. Operativa","Análisis detallado por cuenta y centro de costos. Mayor granularidad operativa.","Controllers, Finanzas","Tabla por Cuenta/Ceco, filtros de Vertical y período."),
        ("4. Detalle de Proveedores","Detalle de gasto real por proveedor. Permite identificar los principales proveedores.","Compras, Control de Gestión","Tabla de proveedores con Real Detalle, segmentadores."),
        ("5. Entregable Opex (falta)","Pendiente de construcción. Será una tabla resumen de gastos OPEX en formato entregable.","Por definir","Por definir."),
        ("6. Auditoría (interno)","Cruce automático entre las dos fuentes de datos. Solo para uso interno del equipo de datos.","Analistas de datos, Auditoría interna","Tarjetas comparativas, tabla AUDIT_Diferencias con Motivo, columnas CAPEX/CO_GT."),
    ]
    out += [tabla(
        [["Página","Objetivo","Público","Visuales principales"]] + [[a,b,c,d] for a,b,c,d in pages],
        [3*cm,6*cm,3.5*cm,5.5*cm]
    )]
    out += [sp(), p("11.1  Segmentador de Período (MesAño)", H2)]
    out += [p("""El segmentador de período es el control principal de filtrado. Está presente en
todas las páginas y muestra los períodos disponibles en formato 'Mes-Año' (ej: Jun-25, Jun-26).
<b>Está ordenado cronológicamente</b> gracias a la columna AñoMesOrden de DIM_Calendario.""")]
    out += [p("""Para que el segmentador filtre correctamente todas las páginas simultáneamente,
se debe configurar la <b>sincronización de segmentadores</b>:
Ver → Sincronizar segmentaciones → activar visibilidad y sincronización para todas las páginas.""", BOX)]
    return out

def seccion_12():
    out = []
    out += [p("12. GESTIÓN DE ERRORES Y SOLUCIÓN DE PROBLEMAS", H1), hr()]
    errores = [
        ("No se pudo encontrar el archivo",
         "El archivo Excel no está en la ruta configurada en pRutaArchivo.",
         "Inicio → Transformar datos → Editar parámetros → actualizar pRutaArchivo con la ruta correcta.",
         "Mantener el Excel siempre en la misma carpeta y con el mismo nombre."),
        ("La propiedad 'expression' es desconocida (TMDL)",
         "Se intentó usar columna calculada DAX en un contexto TMDL no soportado.",
         "Mover la lógica de la columna al código M de la partición (Power Query).",
         "En esta versión de PBI Desktop, usar solo columnas Power Query, no DAX calculadas en TMDL."),
        ("calculatedColumn no es una propiedad admitida",
         "La preview PBI_dynamicCalcColumn está deshabilitada en la versión de PBI Desktop.",
         "Mismo que el anterior: implementar en Power Query.",
         "Verificar las previews habilitadas antes de usar sintaxis avanzada de TMDL."),
        ("Columna 'X' no encontrada en Power Query",
         "El Excel fuente cambió el nombre de una columna.",
         "En Power Query → paso 'Seleccion' → actualizar el nombre de la columna afectada.",
         "Pedir a Control de Gestión que mantenga los nombres de columna estables."),
        ("Los valores de Real Mes y Real Detalle difieren",
         "Las dos fuentes (REAL vs PA y Base Real) tienen datos distintos para el mismo período.",
         "Ir a la página Auditoría y revisar el Motivo de cada diferencia.",
         "Pedir conciliación a Control de Gestión antes de actualizar."),
        ("Los períodos aparecen desordenados en el segmentador",
         "La columna MesAño no tiene configurado 'Ordenar por columna' → AñoMesOrden.",
         "Seleccionar la columna MesAño en DIM_Calendario → Herramientas de columna → Ordenar por columna → AñoMesOrden.",
         "Esta configuración se preserva en el modelo; verificar tras actualizaciones mayores."),
        ("El modelo no carga (error genérico al abrir el .pbip)",
         "Algún archivo TMDL tiene un error de sintaxis.",
         "Revisar el mensaje de error: indica documento y número de línea. Corregir el archivo TMDL correspondiente.",
         "No editar archivos TMDL manualmente salvo que sea necesario."),
        ("Variación muestra BLANK en algunos períodos",
         "No hay datos de PA para ese período (MontoPA = 0 o sin registros).",
         "Normal para períodos futuros sin presupuesto cargado. Verificar con Control de Gestión.",
         "Asegurarse de que el PA está cargado para todos los meses del año en el Excel."),
    ]
    out += [tabla(
        [["Error / Síntoma","Causa probable","Solución","Prevención"]] +
        [[a,b,c,d] for a,b,c,d in errores],
        [4*cm,4*cm,5.5*cm,4.5*cm]
    )]
    return out

def seccion_13():
    out = []
    out += [p("13. PREGUNTAS FRECUENTES (FAQ)", H1), hr()]
    faq = [
        ("¿Por qué Real Mes y Real Detalle dan valores distintos?",
         "Porque son dos fuentes distintas: Real Mes viene de la hoja REAL vs PA (consolidado) y Real Detalle viene de la hoja Base Real (SAP transaccional). Pequeñas diferencias son normales. Diferencias grandes indican un problema de conciliación."),
        ("¿Cómo actualizo el dashboard cuando hay nuevos datos?",
         "Reemplazá el Excel en la carpeta Datos\\ por el actualizado (mismo nombre). Abrí el .pbip y hacé clic en Actualizar. Listo."),
        ("¿Tengo que actualizar las tablas dinámicas del Excel?",
         "No. Power Query lee directamente las hojas de datos (Base Real y REAL vs PA 2025 2026). Las tablas dinámicas son ignoradas."),
        ("¿Qué significa que la Variación sea positiva?",
         "Que se gastó más de lo presupuestado (Real > PA). El color rojo lo indica. Variación negativa (verde) significa que se gastó menos que el presupuesto."),
        ("¿Por qué en algunos meses no hay Real?",
         "Porque los datos de la hoja Base Real solo existen hasta el mes que Control de Gestión haya cerrado. Los meses futuros no tienen real."),
        ("¿Por qué mayo 2025 Real = PA?",
         "Posiblemente porque en ese período el consolidado (hoja REAL vs PA) cargó el Real con el mismo valor que el PA. Verificar con Control de Gestión."),
        ("¿Qué es CAPEX_OPEX?",
         "Es una clasificación de la cuenta contable. CAPEX = inversiones de capital. OPEX = gastos operativos. Actualmente todas las cuentas son OPEX."),
        ("¿Qué es CO_GT?",
         "Es una clasificación interna de las cuentas: CO (Corporate) para cuentas de personal, rodados, honorarios y mantenimiento; GT (General) para el resto. Es metadata para análisis futuro, no afecta los cálculos actuales."),
        ("¿Puedo agregar un nuevo vertical de negocio?",
         "Sí. Solo hay que agregar registros con el nuevo valor de Vertical en el Excel. Al actualizar, DIM_Vertical lo detecta automáticamente."),
        ("¿Puedo cambiar la ruta del Excel?",
         "Sí. Inicio → Transformar datos → Editar parámetros → modificar pRutaArchivo."),
        ("¿El dashboard funciona sin conexión a internet?",
         "Sí. El modelo es local (Import Mode). No requiere internet para funcionar una vez publicado. Solo necesita internet para publicar en Power BI Service."),
        ("¿Por qué hay filas con Diferencia = 0 en la tabla de Auditoría?",
         "Porque el visual agrupa por Vertical/Cuenta/Ceco sin incluir Fecha. Si para un Ceco/Cuenta hay +1000 en un mes y -1000 en otro, se cancelan. Agregar Fecha al visual muestra las diferencias reales."),
        ("¿Cómo agrego una nueva cuenta contable?",
         "Solo hay que agregar registros con la nueva cuenta en el Excel. DIM_Cuenta la incorpora automáticamente al actualizar. Si es necesario clasificarla en CO_GT, verificar si su Rubro ya está en la lógica."),
        ("¿Qué es el archivo .pbip?",
         "Es el punto de entrada del proyecto Power BI en formato de texto (no binario). Al abrirlo en Power BI Desktop, carga el modelo y el informe automáticamente."),
        ("¿Puedo convertirlo a .pbix?",
         "Sí. Desde Power BI Desktop: Archivo → Guardar una copia → formato .pbix. Sin embargo, el .pbip es recomendable para versionado con Git."),
        ("¿Por qué los meses aparecen en orden correcto en el segmentador?",
         "Porque MesAño está configurada para ordenarse por AñoMesOrden (número entero YYYYMM). Sin esta configuración, se ordenaría alfabéticamente."),
        ("¿Qué pasa si el Excel tiene más hojas que las esperadas?",
         "Nada. Power Query solo lee las hojas 'Base Real' y 'REAL vs PA 2025 2026'. Las demás son ignoradas."),
        ("¿Cómo sé si la actualización fue exitosa?",
         "Verificar los totales en la tarjeta Real Mes del Resumen Ejecutivo y compararlos con los valores conocidos del período recién cargado."),
        ("¿Puedo filtrar por múltiples períodos simultáneamente?",
         "Sí. El segmentador de MesAño permite selección múltiple (Ctrl+Clic). También se puede usar el tipo de segmentador 'Entre' para rangos de fechas."),
        ("¿Cómo agrego una nueva página al informe?",
         "En Power BI Desktop: clic en el botón + al pie de la pantalla → se crea una nueva página. Luego agregar visuales desde el panel Visualizaciones."),
        ("¿Qué significa 'Solo en REAL vs PA (no está en Base Real)'?",
         "Que ese Vertical/Cuenta/Ceco/Fecha tiene monto en la hoja de consolidado pero no tiene ningún movimiento en la exportación SAP de la hoja Base Real. Puede indicar una imputación manual."),
        ("¿Cómo se calcula el Acumulado YTD?",
         "Con la función DAX DATESYTD que suma desde el 1° de enero del año en curso hasta el mes seleccionado. Si el filtro es Jun-26, suma Ene+Feb+Mar+Abr+May+Jun de 2026."),
        ("¿Puedo publicar el dashboard en Power BI Service?",
         "Sí. Inicio → Publicar → seleccionar el workspace. Se requiere licencia Power BI Pro o Premium."),
        ("¿Cuántos registros tiene aproximadamente el modelo?",
         "Depende del período cubierto. Para 18 meses (Ene 2025 - Jun 2026) con ~50 cuentas y ~20 cecos por vertical, FACT_Presupuesto puede tener ~50.000 filas y FACT_RealDetalle ~200.000 filas (detalle transaccional SAP)."),
        ("¿El modelo funciona si hay un año nuevo (2027)?",
         "Sí. DIM_Calendario se genera dinámicamente hasta el mes más reciente disponible en los datos. Si se agrega 2027, el calendario se extiende automáticamente."),
        ("¿Cómo puedo saber qué versión de Power BI Desktop se usó?",
         "El error log indica v2.154.1260.0 (May 2026). Se recomienda usar esta versión o posterior para garantizar compatibilidad con el formato PBIP."),
        ("¿Qué es TMDL?",
         "Tabular Model Definition Language. Es el formato de texto que usa el PBIP para definir el modelo de datos. Cada tabla, columna, medida y relación se define en archivos .tmdl."),
        ("¿Puedo modificar las medidas DAX directamente en los archivos .tmdl?",
         "Técnicamente sí, pero es riesgoso. Es más seguro modificarlas desde Power BI Desktop (vista de Modelo → seleccionar la medida → editar fórmula)."),
        ("¿La tabla AUDIT_Diferencias siempre debería tener cero filas?",
         "En un escenario ideal sí, pero en la práctica siempre hay pequeñas diferencias por redondeo o timing de cierre. Lo importante es que no haya diferencias sistemáticas grandes."),
        ("¿Cómo puedo agregar una nueva dimensión (ej: Región)?",
         "1) Agregar la columna Región en el Excel. 2) Incluirla en los pasos de stgRealPA y stgBaseRealCruda en Power Query. 3) Crear DIM_Region como tabla nueva. 4) Agregar la columna RegionID a las FACT. 5) Crear la relación. 6) Crear medidas si es necesario."),
    ]
    for i, (pregunta, respuesta) in enumerate(faq, 1):
        out += [p(f"<b>P{i}. {pregunta}</b>"), p(respuesta), sp(5)]
    return out

def seccion_14():
    out = []
    out += [p("14. MANTENIMIENTO Y ADMINISTRACIÓN", H1), hr()]
    out += [p("14.1  Tareas periódicas", H2)]
    out += [tabla(
        [["Frecuencia","Tarea","Responsable","Tiempo estimado"],
         ["Mensual","Reemplazar el Excel con datos del nuevo período.","Control de Gestión","5 min"],
         ["Mensual","Actualizar el modelo (botón Actualizar).","Analista de datos","5-15 min"],
         ["Mensual","Validar los totales contra el cierre mensual.","Controller","10 min"],
         ["Mensual","Revisar la página de Auditoría y resolver discrepancias.","Analista de datos","15-30 min"],
         ["Trimestral","Verificar que las cuentas nuevas tienen clasificación CO_GT correcta.","Analista de datos","15 min"],
         ["Anual","Revisar si hay nuevas verticales o cecos que requieran ajustes en el modelo.","Analista de datos","30 min"],
         ["Anual","Actualizar DIM_Calendario si el rango de años cambia (automático).","—","Automático"],
         ["Anual","Backup del proyecto completo (carpeta RealVsPAA/).","Analista de datos","5 min"],
         ["Eventual","Actualizar Power BI Desktop a nueva versión.","Analista de datos","30 min"],
         ["Eventual","Agregar nuevas páginas o visuales según requerimientos.","Analista de datos","Variable"],
        ],
        [2.5*cm,7*cm,4*cm,3.5*cm]
    )]
    out += [sp(), p("14.2  Backup y versionado", H2)]
    out += [li([
        "El proyecto PBIP es texto plano → compatible con Git para versionado.",
        "El repositorio está en: github.com/salonsodear-commits/General (rama claude/eager-gates-Md3ac).",
        "El Excel fuente NO está en Git (datos sensibles). Mantener backup en SharePoint o carpeta de red.",
        "Ante cualquier cambio importante, hacer un commit descriptivo antes de modificar.",
    ])]
    out += [sp(), p("14.3  Agregar nuevas fuentes de datos", H2)]
    out += [p("Para incorporar una nueva fuente (por ejemplo, datos de RRHH o de otro sistema):")]
    out += [li([
        "Agregar la nueva consulta en expressions.tmdl o desde Power Query en Power BI Desktop.",
        "Crear las tablas DIM necesarias.",
        "Agregar las columnas ID a las tablas FACT correspondientes.",
        "Crear las relaciones en relationships.tmdl.",
        "Crear las medidas DAX necesarias en la tabla FACT correspondiente.",
        "Actualizar el informe con los nuevos visuales.",
    ])]
    return out

def seccion_15():
    out = []
    out += [p("15. GLOSARIO DE TÉRMINOS", H1), hr()]
    terminos = [
        ("Business Intelligence (BI)","Conjunto de tecnologías y procesos que transforman datos en información útil para la toma de decisiones."),
        ("Power BI","Herramienta de Microsoft para crear dashboards e informes interactivos de análisis de datos."),
        ("PBIP (Power BI Project)","Formato de proyecto Power BI basado en archivos de texto. Reemplaza al .pbix y permite versionado con Git."),
        ("TMDL (Tabular Model Definition Language)","Lenguaje de texto para definir el modelo de datos de Power BI en archivos .tmdl legibles."),
        ("Star Schema (Esquema estrella)","Arquitectura de base de datos para BI donde una tabla central (FACT) se rodea de tablas descriptivas (DIM)."),
        ("Tabla de hechos (FACT)","Tabla que contiene los valores numéricos a analizar (ej: montos, cantidades). FACT_Presupuesto, FACT_RealDetalle."),
        ("Tabla de dimensión (DIM)","Tabla que describe los atributos por los que se analiza (ej: Cuenta, Ceco). DIM_Cuenta, DIM_Ceco, etc."),
        ("DAX (Data Analysis Expressions)","Lenguaje de fórmulas de Power BI para crear medidas y columnas calculadas."),
        ("Medida DAX","Cálculo que se evalúa dinámicamente según los filtros activos. No almacena valores."),
        ("Columna calculada","Columna cuyo valor se calcula fila a fila al momento de la carga. Se almacena en el modelo."),
        ("Power Query (M)","Motor de ETL de Power BI. Conecta a fuentes, transforma datos y los carga al modelo."),
        ("ETL (Extract, Transform, Load)","Proceso de extracción, transformación y carga de datos desde la fuente al modelo."),
        ("Cardinalidad","Tipo de relación entre tablas: uno a uno (1:1), uno a muchos (1:*), muchos a muchos (*:*)."),
        ("Relación activa","Relación que propaga filtros automáticamente entre tablas."),
        ("Relación inactiva","Relación que existe pero no propaga filtros salvo cuando se invoca explícitamente con USERELATIONSHIP() en DAX."),
        ("Contexto de filtro","Conjunto de filtros activos en un momento dado (segmentadores, filas de tabla, columnas, etc.). DAX evalúa sus fórmulas dentro de este contexto."),
        ("KPI (Key Performance Indicator)","Indicador clave de rendimiento. Métrica que resume el desempeño en un área específica."),
        ("YTD (Year To Date)","Acumulado desde el inicio del año hasta el período actual."),
        ("SAMEPERIODLASTYEAR","Función DAX que calcula una medida para el mismo período del año anterior."),
        ("DATESYTD","Función DAX que devuelve todas las fechas desde el 1° de enero hasta la fecha de contexto."),
        ("DIVIDE","Función DAX que divide dos valores y devuelve BLANK (en lugar de error) cuando el divisor es cero."),
        ("PA (Plan Anual / Presupuesto)","Monto presupuestado para un período. También llamado 'budget' o 'forecast'."),
        ("Variación","Diferencia entre Real y PA. Positivo = gastó más. Negativo = gastó menos."),
        ("Ceco (Centro de Costos)","Unidad organizacional a la que se imputan gastos. Permite identificar qué área generó el gasto."),
        ("CAPEX","Capital Expenditure. Inversión en activos de largo plazo (equipos, instalaciones). Actualmente no hay cuentas CAPEX en el modelo."),
        ("OPEX","Operational Expenditure. Gasto operativo corriente (sueldos, servicios, mantenimiento). Todas las cuentas actuales son OPEX."),
        ("Import Mode","Modo de carga donde los datos se copian al modelo de Power BI. No requiere conexión continua a la fuente."),
        ("Segmentador (Slicer)","Control visual que permite filtrar los datos del informe de forma interactiva."),
        ("Drill-through","Funcionalidad que permite hacer clic en un valor y navegar a una página de detalle filtrada por ese valor."),
        ("Bookmark","Fotografía del estado del informe (filtros, visibilidad de visuales) que se puede guardar y restaurar."),
    ]
    out += [tabla(
        [["Término","Definición"]] + [[a,b] for a,b in terminos],
        [4.5*cm,13.5*cm]
    )]
    return out

def seccion_cierre():
    out = []
    out += [p("16. CONOCIMIENTO TRANSFERIDO", H1), hr()]
    out += [p("""Esta documentación ha sido diseñada para que una persona sin experiencia previa
en este proyecto pueda, utilizando únicamente este documento:""")]
    out += [li([
        "<b>Entender</b> qué hace la solución y por qué fue construida así.",
        "<b>Actualizar</b> los datos mensualmente siguiendo el procedimiento del Capítulo 6.",
        "<b>Diagnosticar</b> errores usando la tabla de errores del Capítulo 12.",
        "<b>Interpretar</b> todas las medidas DAX usando las definiciones del Capítulo 10.",
        "<b>Comprender</b> el modelo de datos y sus relaciones (Capítulos 7 y 8).",
        "<b>Entender</b> cada consulta Power Query paso a paso (Capítulo 9).",
        "<b>Mantener</b> el proyecto siguiendo el plan de mantenimiento del Capítulo 14.",
        "<b>Responder</b> las dudas más frecuentes usando las FAQ del Capítulo 13.",
        "<b>Evolucionar</b> la solución agregando nuevas fuentes, dimensiones y medidas.",
    ])]
    out += [sp(12)]
    CIERRE = estilo("CIERRE","Normal",fontSize=10,textColor=AZUL,alignment=TA_CENTER,
                    fontName="Helvetica-BoldOblique",leading=16)
    out += [p("Área de Datos — Operaciones Complejas | Junio 2026", CIERRE)]
    out += [p("Real vs Presupuesto (PAA) — Documentación v1.0", CIERRE)]
    return out

# ── Numeración de páginas ─────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(A4[0]/2, 1.5*cm, f"Página {doc.page}")
    canvas.drawString(2*cm, 1.5*cm, "Real vs Presupuesto (PAA) — Documentación Técnica v1.0")
    canvas.drawRightString(A4[0]-2*cm, 1.5*cm, "Confidencial — Uso Interno")
    canvas.restoreState()

# ── Build ─────────────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=2.2*cm,
        title="Real vs Presupuesto (PAA) - Documentación",
        author="Área de Datos - Operaciones Complejas",
    )
    story = []

    # Portada
    story += portada()
    story += [PageBreak()]

    # Índice manual
    story += [p("TABLA DE CONTENIDOS", H1), hr()]
    toc = [
        ("1","Resumen Ejecutivo"),
        ("2","Alcance de la Solución"),
        ("3","Arquitectura General"),
        ("4","Estructura del Proyecto"),
        ("5","Inventario de Fuentes de Datos"),
        ("6","Proceso de Actualización"),
        ("7","Modelo de Datos"),
        ("8","Relaciones del Modelo"),
        ("9","Power Query — Consultas ETL"),
        ("10","Medidas DAX"),
        ("11","Páginas del Dashboard"),
        ("12","Gestión de Errores"),
        ("13","Preguntas Frecuentes (FAQ)"),
        ("14","Mantenimiento y Administración"),
        ("15","Glosario de Términos"),
        ("16","Conocimiento Transferido"),
    ]
    for num, titulo in toc:
        story += [p(f"{num}. &nbsp;&nbsp; {titulo}", NOR)]
    story += [PageBreak()]

    story += seccion_1()  + [PageBreak()]
    story += seccion_2()  + [PageBreak()]
    story += seccion_3()  + [PageBreak()]
    story += seccion_4()  + [PageBreak()]
    story += seccion_5()  + [PageBreak()]
    story += seccion_6()  + [PageBreak()]
    story += seccion_7()  + [PageBreak()]
    story += seccion_8()  + [PageBreak()]
    story += seccion_9()  + [PageBreak()]
    story += seccion_10() + [PageBreak()]
    story += seccion_11() + [PageBreak()]
    story += seccion_12() + [PageBreak()]
    story += seccion_13() + [PageBreak()]
    story += seccion_14() + [PageBreak()]
    story += seccion_15() + [PageBreak()]
    story += seccion_cierre()

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF generado: {OUTPUT}")

if __name__ == "__main__":
    build()
