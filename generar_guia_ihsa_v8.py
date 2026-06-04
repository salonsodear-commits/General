"""
Genera guía PDF paso a paso — IHSA Dashboard v8
Requiere: reportlab, Pillow
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import PageBreak
from PIL import Image as PILImage
import io, os

# ── Paleta ──────────────────────────────────────────────────────────────────
NAVY       = colors.HexColor("#080E23")
BLUE_CORP  = colors.HexColor("#3267B8")
BLUE_LT    = colors.HexColor("#5294DA")
GOLD       = colors.HexColor("#D2AF50")
WHITE      = colors.white
GRAY_LT    = colors.HexColor("#E8EDF5")
GRAY_MID   = colors.HexColor("#B0BDD0")
DARK_PANEL = colors.HexColor("#12213F")

OUTPUT = "/home/user/General/assets_ihsa_v8/Guia_PowerBI_IHSA_v8.pdf"
ASSETS = "/home/user/General/assets_ihsa_v8"

# ── Estilos ──────────────────────────────────────────────────────────────────
ss = getSampleStyleSheet()

def sty(name, **kw):
    return ParagraphStyle(name, **kw)

S_TITLE   = sty("Title2",   fontSize=26, textColor=WHITE,     leading=32, spaceAfter=4,
                fontName="Helvetica-Bold", alignment=TA_CENTER)
S_SUB     = sty("Sub",      fontSize=12, textColor=BLUE_LT,   leading=16, spaceAfter=2,
                fontName="Helvetica", alignment=TA_CENTER)
S_STEP    = sty("Step",     fontSize=13, textColor=WHITE,      leading=18, spaceBefore=14,
                spaceAfter=4, fontName="Helvetica-Bold")
S_BODY    = sty("Body",     fontSize=9.5, textColor=GRAY_LT,  leading=14, spaceAfter=3,
                fontName="Helvetica")
S_BULLET  = sty("Bullet",   fontSize=9.5, textColor=GRAY_LT,  leading=14, spaceAfter=2,
                fontName="Helvetica", leftIndent=14, bulletIndent=0)
S_NOTE    = sty("Note",     fontSize=8.5, textColor=GOLD,     leading=13, spaceAfter=4,
                fontName="Helvetica-Oblique", leftIndent=10)
S_HEAD2   = sty("Head2",    fontSize=10, textColor=BLUE_LT,   leading=14, spaceBefore=8,
                spaceAfter=2, fontName="Helvetica-Bold")
S_FOOTER  = sty("Footer",   fontSize=7.5, textColor=GRAY_MID, leading=10,
                fontName="Helvetica", alignment=TA_CENTER)

def b(txt): return f"<b>{txt}</b>"
def gold(txt): return f'<font color="#D2AF50">{txt}</font>'
def lt(txt): return f'<font color="#5294DA">{txt}</font>'

# ── Fondo de página ──────────────────────────────────────────────────────────
def on_page(canvas, doc):
    w, h = A4
    canvas.saveState()
    # fondo navy
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    # banda lateral izquierda
    canvas.setFillColor(DARK_PANEL)
    canvas.rect(0, 0, 0.55*cm, h, fill=1, stroke=0)
    # banda lateral azul corp
    canvas.setFillColor(BLUE_CORP)
    canvas.rect(0.55*cm, 0, 0.18*cm, h, fill=1, stroke=0)
    # línea dorada en footer
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.5)
    canvas.line(1.8*cm, 1.3*cm, w-1.8*cm, 1.3*cm)
    # footer texto
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(GRAY_MID)
    canvas.drawCentredString(w/2, 0.85*cm, f"Grupo IHSA — Dashboard Power BI v8   |   Guía de implementación")
    canvas.drawRightString(w-1.8*cm, 0.85*cm, f"Página {doc.page}")
    canvas.restoreState()

# ── Tabla de archivos ─────────────────────────────────────────────────────────
def tabla_archivos():
    data = [
        [Paragraph(b("Archivo PNG"), S_HEAD2), Paragraph(b("Página en Power BI"), S_HEAD2)],
        [Paragraph("fondo_00_indice.png", S_BODY),    Paragraph("Índice / Portada", S_BODY)],
        [Paragraph("fondo_01_resumen.png", S_BODY),   Paragraph("Resumen Ejecutivo", S_BODY)],
        [Paragraph("fondo_02_comercial.png", S_BODY), Paragraph("Comercial", S_BODY)],
        [Paragraph("fondo_03_operativa.png", S_BODY), Paragraph("Operativa", S_BODY)],
        [Paragraph("fondo_04_proveedores.png", S_BODY),Paragraph("Proveedores", S_BODY)],
        [Paragraph("fondo_05_opex.png", S_BODY),      Paragraph("OPEX", S_BODY)],
        [Paragraph("fondo_06_auditoria.png", S_BODY), Paragraph("Auditoría", S_BODY)],
    ]
    t = Table(data, colWidths=[9*cm, 8*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0),  DARK_PANEL),
        ("BACKGROUND",  (0,1), (-1,-1), colors.HexColor("#0D1A3A")),
        ("ROWBACKGROUNDS",(0,2),(-1,-1),[colors.HexColor("#0D1A3A"), colors.HexColor("#101F45")]),
        ("TEXTCOLOR",   (0,0), (-1,0),  BLUE_LT),
        ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#1E3060")),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    return t

def tabla_slicers():
    data = [
        [Paragraph(b("Slicer"), S_HEAD2), Paragraph(b("X"), S_HEAD2),
         Paragraph(b("Y"), S_HEAD2), Paragraph(b("Ancho"), S_HEAD2), Paragraph(b("Alto"), S_HEAD2)],
        [Paragraph("Período / Mes",      S_BODY), Paragraph("8",S_BODY), Paragraph("72",S_BODY),  Paragraph("229",S_BODY), Paragraph("52",S_BODY)],
        [Paragraph("Vertical / Negocio", S_BODY), Paragraph("8",S_BODY), Paragraph("132",S_BODY), Paragraph("229",S_BODY), Paragraph("52",S_BODY)],
        [Paragraph("Cliente / Contable", S_BODY), Paragraph("8",S_BODY), Paragraph("192",S_BODY), Paragraph("229",S_BODY), Paragraph("52",S_BODY)],
        [Paragraph("OCC / Centro costo", S_BODY), Paragraph("8",S_BODY), Paragraph("252",S_BODY), Paragraph("229",S_BODY), Paragraph("52",S_BODY)],
    ]
    t = Table(data, colWidths=[7.5*cm, 2*cm, 2*cm, 2.5*cm, 2.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  DARK_PANEL),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#0D1A3A"), colors.HexColor("#101F45")]),
        ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#1E3060")),
        ("ALIGN",        (1,0), (-1,-1), "CENTER"),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
    ]))
    return t

def tabla_botones():
    data = [
        [Paragraph(b("Botón"), S_HEAD2), Paragraph(b("X"), S_HEAD2),
         Paragraph(b("Y"), S_HEAD2), Paragraph(b("Ancho"), S_HEAD2),
         Paragraph(b("Alto"), S_HEAD2), Paragraph(b("Navega a"), S_HEAD2)],
        [Paragraph("Resumen Ejecutivo", S_BODY), Paragraph("310",S_BODY), Paragraph("100",S_BODY), Paragraph("230",S_BODY), Paragraph("120",S_BODY), Paragraph("Página 2",S_BODY)],
        [Paragraph("Comercial",         S_BODY), Paragraph("570",S_BODY), Paragraph("100",S_BODY), Paragraph("230",S_BODY), Paragraph("120",S_BODY), Paragraph("Página 3",S_BODY)],
        [Paragraph("Operativa",         S_BODY), Paragraph("830",S_BODY), Paragraph("100",S_BODY), Paragraph("230",S_BODY), Paragraph("120",S_BODY), Paragraph("Página 4",S_BODY)],
        [Paragraph("Proveedores",       S_BODY), Paragraph("310",S_BODY), Paragraph("250",S_BODY), Paragraph("230",S_BODY), Paragraph("120",S_BODY), Paragraph("Página 5",S_BODY)],
        [Paragraph("OPEX",              S_BODY), Paragraph("570",S_BODY), Paragraph("250",S_BODY), Paragraph("230",S_BODY), Paragraph("120",S_BODY), Paragraph("Página 6",S_BODY)],
        [Paragraph("Auditoría",         S_BODY), Paragraph("830",S_BODY), Paragraph("250",S_BODY), Paragraph("230",S_BODY), Paragraph("120",S_BODY), Paragraph("Página 7",S_BODY)],
    ]
    t = Table(data, colWidths=[4.5*cm, 1.5*cm, 1.5*cm, 2*cm, 1.5*cm, 2.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  DARK_PANEL),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#0D1A3A"), colors.HexColor("#101F45")]),
        ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#1E3060")),
        ("ALIGN",        (1,0), (-1,-1), "CENTER"),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
    ]))
    return t

def sep(): return HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#1E3060"), spaceAfter=6, spaceBefore=6)

def step_header(n, txt):
    return Paragraph(f'{gold(f"0{n}.")}  {txt}', S_STEP)

def bullet(txt):
    return Paragraph(f"▸  {txt}", S_BULLET)

# ── Preview imágenes ──────────────────────────────────────────────────────────
def preview_img(path, max_w_cm=16.5, max_h_cm=5.5):
    if not os.path.exists(path):
        return Spacer(1, 0.3*cm)
    with PILImage.open(path) as im:
        iw, ih = im.size
    ratio = iw / ih
    w = max_w_cm * cm
    h = w / ratio
    if h > max_h_cm * cm:
        h = max_h_cm * cm
        w = h * ratio
    return RLImage(path, width=w, height=h)

# ── Contenido ────────────────────────────────────────────────────────────────
def build_story():
    story = []
    M = lambda s: Spacer(1, s*cm)

    # ── PORTADA ──────────────────────────────────────────────────────────────
    story.append(M(3.5))
    story.append(Paragraph("GRUPO IHSA", S_TITLE))
    story.append(Paragraph("Operaciones Complejas", S_SUB))
    story.append(M(0.4))
    story.append(HRFlowable(width="60%", thickness=1.5, color=GOLD, spaceAfter=10, hAlign="CENTER"))
    story.append(Paragraph("Dashboard Power BI — Guía de Implementación", S_TITLE))
    story.append(M(0.3))
    story.append(Paragraph("Versión 8  ·  Dark Mode Premium  ·  Ambulancia IHSA integrada", S_SUB))
    story.append(M(1.5))

    # preview portada
    img_path = os.path.join(ASSETS, "fondo_00_indice.png")
    story.append(preview_img(img_path, max_h_cm=6))
    story.append(M(0.5))
    story.append(Paragraph("Vista previa — Página Índice con ambulancia IHSA como hero visual", S_FOOTER))
    story.append(PageBreak())

    # ── SECCIÓN 1: Archivos ───────────────────────────────────────────────────
    story.append(step_header(1, "Copiar archivos a tu disco"))
    story.append(sep())
    story.append(Paragraph(
        "Copiá la carpeta completa <b>assets_ihsa_v8</b> desde el repositorio a tu disco O::", S_BODY))
    story.append(M(0.3))
    story.append(Paragraph(
        '<font color="#5294DA"><b>O:\\IHSA\\PowerBI\\assets_ihsa_v8\\</b></font>', S_BODY))
    story.append(M(0.4))
    story.append(tabla_archivos())
    story.append(M(0.3))
    story.append(Paragraph(
        f'{gold("★")}  El archivo <b>tema_GrupoIHSA_Premium.json</b> contiene todos los estilos corporativos.', S_NOTE))

    story.append(M(0.6))
    story.append(step_header(2, "Importar el tema JSON"))
    story.append(sep())
    for t in [
        "Abrí el archivo <b>.pbip</b> del dashboard en Power BI Desktop.",
        "En la cinta superior: <b>Ver → Temas → Examinar temas</b>.",
        "Seleccioná: <b>assets_ihsa_v8\\tema_GrupoIHSA_Premium.json</b>.",
        'Click <b>Aplicar</b> en el cuadro de confirmación que aparece.',
    ]:
        story.append(bullet(t))
    story.append(Paragraph(
        f'{gold("★")}  El tema aplica colores corporativos automáticamente a todos los gráficos (barras, líneas, dona, matriz).', S_NOTE))

    story.append(M(0.6))
    story.append(step_header(3, "Configurar tamaño de página"))
    story.append(sep())
    story.append(Paragraph("Hacé esto <b>en cada una de las 7 páginas</b>:", S_BODY))
    for t in [
        "Click en área vacía del canvas (sin seleccionar ningún visual).",
        "Panel <b>Formato</b> (ícono pincel) → <b>Configuración de página</b>.",
        "Tipo: <b>Personalizado</b> → Ancho: <b>1280 px</b> → Alto: <b>720 px</b>.",
    ]:
        story.append(bullet(t))

    story.append(PageBreak())

    # ── SECCIÓN 2: Fondos ────────────────────────────────────────────────────
    story.append(step_header(4, "Aplicar fondo PNG en cada página"))
    story.append(sep())
    story.append(Paragraph("Para <b>cada una de las 7 páginas</b> seguí estos pasos:", S_BODY))
    story.append(M(0.2))
    for t in [
        "Click en área vacía del canvas.",
        "Panel <b>Formato</b> → <b>Fondo del lienzo</b>.",
        "Click <b>Examinar imagen</b> → seleccioná el PNG de la tabla según la página.",
        "<b>Ajuste de imagen</b>: elegí <b>Normal</b> (nunca Ajustar ni Rellenar).",
        "<b>Transparencia</b>: <b>0%</b>.",
    ]:
        story.append(bullet(t))
    story.append(M(0.4))
    story.append(tabla_archivos())

    story.append(M(0.6))
    story.append(step_header(5, "Configurar fondo del informe"))
    story.append(sep())
    story.append(Paragraph(
        "Este es el color que se ve detrás del canvas y en los bordes de la pantalla.", S_BODY))
    for t in [
        "Click en área vacía → <b>Formato</b> → <b>Fondo del informe</b>.",
        'Color: <b><font color="#5294DA">#080E23</font></b> (navy oscuro — mismo del panel lateral).',
        "Transparencia: <b>0%</b>.",
    ]:
        story.append(bullet(t))

    story.append(M(0.6))

    # preview resumen
    img2 = os.path.join(ASSETS, "fondo_01_resumen.png")
    story.append(preview_img(img2, max_h_cm=5))
    story.append(Paragraph("Vista previa — Resumen Ejecutivo con ambulancia en panel lateral", S_FOOTER))

    story.append(PageBreak())

    # ── SECCIÓN 3: Slicers ───────────────────────────────────────────────────
    story.append(step_header(6, "Posicionar los slicers en el panel lateral"))
    story.append(sep())
    story.append(Paragraph(
        "Los slicers van en el panel izquierdo oscuro (<b>245 px de ancho</b>). "
        "Usá las coordenadas exactas para que queden sobre las zonas del fondo.", S_BODY))
    story.append(M(0.3))
    story.append(tabla_slicers())
    story.append(M(0.3))
    story.append(Paragraph(b("Formato para cada slicer:"), S_HEAD2))
    for t in [
        "Fondo: <b>Transparente</b> (sin color de relleno).",
        "Borde: <b>Ninguno</b>.",
        "Título: <b>Desactivado</b> (el texto ya está en el fondo PNG).",
        'Texto de ítem: blanco <b><font color="#5294DA">#FFFFFF</font></b>, tamaño <b>10 pt</b>, fuente Segoe UI.',
        "Contorno del elemento: color <b>#5294DA</b> (azul claro) al seleccionar.",
    ]:
        story.append(bullet(t))

    story.append(M(0.6))
    story.append(step_header(7, "Zona segura para visuals de contenido"))
    story.append(sep())
    story.append(Paragraph(
        "La ambulancia ocupa el panel lateral. El área para KPIs y gráficos empieza en:", S_BODY))
    story.append(M(0.3))

    zona = [
        [Paragraph(b("Límite"), S_HEAD2), Paragraph(b("Valor"), S_HEAD2)],
        [Paragraph("Borde izquierdo (X)", S_BODY), Paragraph("258 px", S_BODY)],
        [Paragraph("Borde superior (Y)", S_BODY), Paragraph("72 px", S_BODY)],
        [Paragraph("Ancho disponible",  S_BODY), Paragraph("1022 px", S_BODY)],
        [Paragraph("Alto disponible",   S_BODY), Paragraph("648 px", S_BODY)],
    ]
    tz = Table(zona, colWidths=[9*cm, 8*cm])
    tz.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  DARK_PANEL),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#0D1A3A"), colors.HexColor("#101F45")]),
        ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#1E3060")),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
    ]))
    story.append(tz)
    story.append(M(0.3))
    story.append(Paragraph(
        f'{gold("★")}  Nunca ubiques visuals con X < 245 px para no tapar la ambulancia ni los slicers.', S_NOTE))

    story.append(PageBreak())

    # ── SECCIÓN 4: Botones ───────────────────────────────────────────────────
    story.append(step_header(8, "Botones de navegación — Página Índice"))
    story.append(sep())
    story.append(Paragraph(
        "En la página Índice agregá 6 botones transparentes sobre las tarjetas del canvas:", S_BODY))
    story.append(M(0.2))
    for t in [
        "<b>Insertar → Botones → Vacío</b>.",
        "Posicioná cada botón según la tabla de coordenadas.",
        "Para cada botón: Fondo <b>transparente</b> → <b>Acción: activada</b>.",
        "Tipo de acción: <b>Navegación de página</b> → elegí la página destino.",
    ]:
        story.append(bullet(t))
    story.append(M(0.4))
    story.append(tabla_botones())

    story.append(M(0.6))
    story.append(step_header(9, 'Botón "Volver al Índice" (páginas 2–7)'))
    story.append(sep())
    for t in [
        "<b>Insertar → Botones → Atrás</b> (o Vacío con ícono de casa).",
        "Posición: X = <b>258</b> px, Y = <b>6</b> px, Ancho = <b>120</b> px, Alto = <b>50</b> px.",
        "Acción: <b>Navegación de página → Índice</b>.",
        "Fondo: transparente. Ícono/texto: blanco.",
        "Copiá el botón y pegalo en cada página (Ctrl+C / Ctrl+V entre páginas).",
    ]:
        story.append(bullet(t))
    story.append(Paragraph(
        f'{gold("★")}  Probá la navegación con Ctrl+Click en Power BI Desktop antes de publicar.', S_NOTE))

    story.append(PageBreak())

    # ── SECCIÓN 5: Formato visuals ───────────────────────────────────────────
    story.append(step_header(10, "Formato de visuals (tarjetas, matrices, gráficos)"))
    story.append(sep())
    story.append(Paragraph(
        "El tema JSON ya aplica los colores corporativos automáticamente. "
        "Para ajuste fino de cada visual:", S_BODY))
    story.append(M(0.2))

    fmt = [
        [Paragraph(b("Propiedad"), S_HEAD2), Paragraph(b("Valor recomendado"), S_HEAD2)],
        [Paragraph("Fondo del visual",  S_BODY), Paragraph("Transparente (0% opacidad)", S_BODY)],
        [Paragraph("Borde",             S_BODY), Paragraph("#5294DA · 1 px · redondeo 4 px  (opcional)", S_BODY)],
        [Paragraph("Título del visual", S_BODY), Paragraph("Texto blanco #FFFFFF · fondo transparente", S_BODY)],
        [Paragraph("Fuente",            S_BODY), Paragraph("Segoe UI · 10–12 pt", S_BODY)],
        [Paragraph("Etiquetas de datos",S_BODY), Paragraph("Blanco o #5294DA según contraste", S_BODY)],
        [Paragraph("Ejes (X / Y)",      S_BODY), Paragraph("Título desactivado · línea #1E3060", S_BODY)],
    ]
    tf = Table(fmt, colWidths=[5.5*cm, 12*cm])
    tf.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  DARK_PANEL),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#0D1A3A"), colors.HexColor("#101F45")]),
        ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#1E3060")),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
    ]))
    story.append(tf)

    story.append(M(0.6))
    story.append(step_header(11, "Formato condicional (opcional avanzado)"))
    story.append(sep())
    story.append(Paragraph(
        "Para tarjetas KPI con semáforo (verde/rojo según desvío vs presupuesto):", S_BODY))
    for t in [
        "Seleccioná la tarjeta → <b>Formato condicional</b> en el panel de campos.",
        "Reglas: <b>≤ -10%</b> → color <b>#D94F3D</b> (rojo) · <b>≥ 0%</b> → color <b>#3DAD5E</b> (verde).",
        "Aplicá en <b>Color de fuente</b> o <b>Fondo de la tarjeta</b> según el tipo de KPI.",
    ]:
        story.append(bullet(t))

    story.append(M(0.6))

    # preview auditoría
    img3 = os.path.join(ASSETS, "fondo_06_auditoria.png")
    story.append(preview_img(img3, max_h_cm=5))
    story.append(Paragraph("Vista previa — Auditoría (fondo diferenciado con ambulancia integrada)", S_FOOTER))

    story.append(PageBreak())

    # ── SECCIÓN 6: Checklist ────────────────────────────────────────────────
    story.append(step_header(12, "Checklist final antes de publicar"))
    story.append(sep())
    story.append(M(0.2))

    checks = [
        ("Tamaño de página",    "1280 × 720 px en las 7 páginas"),
        ("Fondo del informe",   "#080E23 navy oscuro"),
        ("Fondo del lienzo",    "PNG aplicado en Normal, 0% transparencia, en cada página"),
        ("Tema JSON",           "tema_GrupoIHSA_Premium.json importado y activo"),
        ("Slicers",             "Posicionados en coordenadas correctas, fondo transparente"),
        ("Zona segura",         "Ningún visual con X < 245 px"),
        ("Botones Índice",      "6 botones navegación + 1 botón Volver en páginas 2–7"),
        ("Navegación",          "Probada con Ctrl+Click en Power BI Desktop"),
        ("Publicación",         "Publicar en workspace IHSA, verificar en Power BI Service"),
    ]

    for label, desc in checks:
        story.append(Paragraph(
            f'<font color="#D2AF50">☐</font>  <b>{label}:</b>  {desc}', S_BULLET))
        story.append(M(0.1))

    story.append(M(0.8))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GOLD, spaceAfter=10))
    story.append(Paragraph(
        "Grupo IHSA  ·  Operaciones Complejas  ·  Dashboard Power BI v8  ·  Generado automáticamente",
        S_FOOTER))

    return story

# ── Build PDF ─────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=1.8*cm, rightMargin=1.8*cm,
    topMargin=1.6*cm,  bottomMargin=1.8*cm,
)
doc.build(build_story(), onFirstPage=on_page, onLaterPages=on_page)
print(f"  ✓  PDF generado: {OUTPUT}")
