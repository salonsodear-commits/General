#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grupo IHSA — Dashboard Premium v4
Panel lateral: zona de imagen vehicular (ambulancia) como Mercedes-Benz.
Shapes orgánicos exactos de los templates IHSA.
Colores: #3267B8 exacto + sistema completo.
"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, os

OUT = "/home/user/General/assets_ihsa_v4"
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720

# ── Paleta IHSA exacta (extraída de los templates corporativos) ───────────────
BLUE        = ( 50, 103, 184)   # #3267B8 — azul IHSA exacto
BLUE_DARK   = ( 23,  55, 115)   # #173773 — variante oscura
BLUE_LIGHT  = ( 82, 148, 218)   # #5294DA — hover / highlight
BLUE_PALE   = (200, 220, 245)   # para bordes de tarjetas
NAVY        = ( 13,  24,  64)   # fondo oscuro panel
NAVY2       = ( 18,  33,  82)   # gradiente panel
WHITE       = (255, 255, 255)
CONTENT_BG  = (246, 249, 254)   # blanco azulado muy sutil (área contenido)
CARD        = (255, 255, 255)
CARD_BORDER = (218, 230, 248)
TEXT_H      = ( 18,  32,  72)   # texto heading
TEXT_B      = ( 60,  85, 135)   # texto body
TEXT_S      = (140, 165, 200)   # texto secundario/placeholder
GOLD        = (200, 160,  40)   # acento dorado
ORANGE      = (230, 100,  30)   # naranja emergencias (de la ambulancia)
GREEN       = ( 25, 155, 110)   # positivo
RED         = (200,  45,  50)   # alerta

PW = 258   # panel width
HH = 66    # header height

# ── Helpers ───────────────────────────────────────────────────────────────────
def font(sz, bold=False):
    for p in [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        try: return ImageFont.truetype(p, sz)
        except: pass
    return ImageFont.load_default()

def lerp(a, b, t):
    return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

def grad_v(draw, x0,y0,x1,y1, top,bot, n=120):
    s = (y1-y0)/n
    for i in range(n):
        draw.rectangle([x0,y0+i*s,x1,y0+(i+1)*s+1], fill=(*lerp(top,bot,i/n),255))

def grad_h(draw, x0,y0,x1,y1, l,r, n=160):
    s = (x1-x0)/n
    for i in range(n):
        draw.rectangle([x0+i*s,y0,x0+(i+1)*s+1,y1], fill=(*lerp(l,r,i/n),255))

def shadow(img, x0,y0,x1,y1, r=14, offset=4, blur=12):
    L = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(L).rounded_rectangle(
        [x0+offset,y0+offset,x1+offset,y1+offset],
        radius=r, fill=(*TEXT_H, 35))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(blur)))

def card(img, x0,y0,x1,y1, r=14, accent=None, sh=True):
    if sh: shadow(img, x0,y0,x1,y1, r=r)
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([x0,y0,x1,y1], radius=r, fill=(*CARD,255))
    d.rounded_rectangle([x0,y0,x1,y1], radius=r, outline=(*CARD_BORDER,180), width=1)
    img.alpha_composite(L)
    if accent:
        La = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(La).rounded_rectangle([x0,y0,x1,y0+5], radius=r//2,
                                              fill=(*accent,255))
        img.alpha_composite(La)

def glow_line(img, x0,y0,x1,y1, color, w=1, spread=10):
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    for s in range(spread,0,-1):
        d.line([(x0,y0),(x1,y1)], fill=(*color, int(100*(s/spread)**2)), width=s)
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(spread//4)))
    ImageDraw.Draw(img).line([(x0,y0),(x1,y1)], fill=(*color,200), width=w)

def alpha_shape(img, pts, color, alpha):
    L = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(L).polygon(pts, fill=(*color,alpha))
    img.alpha_composite(L)

def rounded_rect_layer(img, x0,y0,x1,y1, r, color, alpha, outline=None):
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([x0,y0,x1,y1], radius=r, fill=(*color,alpha))
    if outline:
        d.rounded_rectangle([x0,y0,x1,y1], radius=r,
                             outline=(*outline[0],outline[1]), width=1)
    img.alpha_composite(L)

# ── Logo IHSA premium ─────────────────────────────────────────────────────────
def logo(img, x, y, scale=1.0, on_dark=True):
    d = ImageDraw.Draw(img)
    fg = WHITE if on_dark else BLUE
    fg2 = BLUE_LIGHT if on_dark else BLUE
    fnt_g = font(int(8*scale))
    fnt_i = font(int(28*scale), bold=True)
    # Barra de acento
    d.rectangle([x, y+2, x+3, y+int(38*scale)], fill=(*fg2,255))
    d.text((x+9, y),              "GRUPO", font=fnt_g, fill=(*fg,170))
    d.text((x+8, y+int(10*scale)), "IHSA", font=fnt_i, fill=(*fg,255))

# ── Slicer slot premium ───────────────────────────────────────────────────────
def slicer(img, draw, x0, y, label, width):
    draw.text((x0, y), label.upper(), font=font(7), fill=(*TEXT_S,180))
    y1, y2 = y+12, y+34
    rounded_rect_layer(img, x0, y1, x0+width, y2, 6, NAVY2, 190)
    rounded_rect_layer(img, x0, y1, x0+width, y2, 6, BLUE_LIGHT, 0,
                       outline=(BLUE_LIGHT, 55))
    d = ImageDraw.Draw(img)
    d.text((x0+10, y1+6), "Todos", font=font(9), fill=(*TEXT_S,110))
    d.text((x0+width-18, y1+5), "▾", font=font(10), fill=(*BLUE_LIGHT,140))

# ══════════════════════════════════════════════════════════════════════════════
# PANEL LATERAL — el corazón del diseño
# Incluye: gradiente, shapes orgánicos IHSA, zona imagen vehicular, logo, slicers
# ══════════════════════════════════════════════════════════════════════════════
def build_panel(img, page_label=""):
    draw = ImageDraw.Draw(img)

    # ── Fondo panel: gradiente navy profundo ──────────────────────────────────
    grad_v(draw, 0, 0, PW, H, NAVY, lerp(NAVY2, NAVY, 0.4))

    # ── Textura diagonal muy sutil (como en slides IHSA) ─────────────────────
    for off in range(-H, W, 52):
        draw.line([(off,0),(off+H,H)], fill=(*BLUE_DARK,12), width=1)

    # ── SHAPE ORGÁNICO IHSA — semicírculo en zona inferior (Slide 1 exacto) ──
    # Círculo grande que "sale" por el borde derecho-inferior del panel
    blob_cx = PW + 15
    blob_cy = H - 10
    for r, alpha in [(200,22),(155,18),(110,14),(72,10)]:
        L = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(L).ellipse(
            [blob_cx-r, blob_cy-r, blob_cx+r, blob_cy+r],
            fill=(*BLUE, alpha))
        img.alpha_composite(L)

    # ── ZONA DE IMAGEN VEHICULAR (ambulancia) — estilo Mercedes-Benz ──────────
    # Área reservada con forma redondeada + indicación visual
    img_zone_y0 = 360
    img_zone_y1 = H - 85
    img_zone_x0 = 8
    img_zone_x1 = PW - 8

    # Fondo de la zona de imagen (oscuro con borde sutil)
    rounded_rect_layer(img, img_zone_x0, img_zone_y0,
                       img_zone_x1, img_zone_y1, 14,
                       BLUE_DARK, 80)
    rounded_rect_layer(img, img_zone_x0, img_zone_y0,
                       img_zone_x1, img_zone_y1, 14,
                       BLUE_LIGHT, 0,
                       outline=(BLUE_LIGHT, 35))

    # Texto indicador (se reemplaza con la imagen real)
    draw = ImageDraw.Draw(img)
    zone_cx = (img_zone_x0 + img_zone_x1) // 2
    zone_cy = (img_zone_y0 + img_zone_y1) // 2
    draw.text((zone_cx-38, zone_cy-18), "[ IMAGEN ]",
              font=font(9, bold=True), fill=(*BLUE_LIGHT, 80))
    draw.text((zone_cx-36, zone_cy-2), "ambulancia",
              font=font(8), fill=(*BLUE_LIGHT, 55))
    draw.text((zone_cx-26, zone_cy+12), "IHSA",
              font=font(9, bold=True), fill=(*BLUE_LIGHT, 55))

    # Gradiente de fade en borde superior e inferior de la zona imagen
    for i in range(28):
        a = int(80 * (1 - i/28))
        draw.rectangle([img_zone_x0, img_zone_y0+i, img_zone_x1, img_zone_y0+i+1],
                        fill=(*NAVY, a))
    for i in range(28):
        a = int(80 * (1 - i/28))
        draw.rectangle([img_zone_x0, img_zone_y1-i-1, img_zone_x1, img_zone_y1-i],
                        fill=(*NAVY, a))

    # ── Separador lateral luminoso (borde derecho del panel) ─────────────────
    glow_line(img, PW, 0, PW, H, BLUE, w=1, spread=14)

    # ── Logo arriba ───────────────────────────────────────────────────────────
    logo(img, 20, 18, scale=1.1)

    # Línea divisoria bajo logo
    draw = ImageDraw.Draw(img)
    draw.line([(16, 72), (PW-16, 72)], fill=(*BLUE_LIGHT, 40), width=1)

    # ── Sección activa ────────────────────────────────────────────────────────
    if page_label:
        draw.text((16, 80), "SECCIÓN", font=font(7), fill=(*TEXT_S, 130))
        draw.text((16, 92), page_label, font=font(10, bold=True),
                  fill=(*WHITE, 200))
        draw.line([(16,110),(PW-16,110)], fill=(*BLUE_DARK,80), width=1)

    # ── Segmentadores ─────────────────────────────────────────────────────────
    sw = PW - 32
    slicers = ["Período (MesAño)", "Vertical", "Cuenta", "Ceco"]
    sy = 120 if page_label else 88
    draw = ImageDraw.Draw(img)
    for lbl in slicers:
        slicer(img, draw, 16, sy, lbl, sw)
        sy += 58

    # ── Pie del panel ─────────────────────────────────────────────────────────
    draw = ImageDraw.Draw(img)
    draw.text((16, H-22), "Operaciones Complejas · 2025–2026",
              font=font(7), fill=(*TEXT_S, 80))


# ══════════════════════════════════════════════════════════════════════════════
# ÁREA DE CONTENIDO
# ══════════════════════════════════════════════════════════════════════════════
def build_content(img, titulo, subtitulo, badge=None, dark_hdr=False):
    draw = ImageDraw.Draw(img)

    # Fondo blanco suave
    draw.rectangle([PW+1, 0, W, H], fill=(*CONTENT_BG,255))

    # Header
    hdr_color = NAVY if dark_hdr else WHITE
    draw.rectangle([PW+1, 0, W, HH], fill=(*hdr_color,255))

    # Línea separadora header
    if dark_hdr:
        glow_line(img, PW+1, HH, W, HH, BLUE, w=1, spread=8)
    else:
        draw = ImageDraw.Draw(img)
        draw.line([(PW+20, HH),(W-20, HH)], fill=(*CARD_BORDER,255), width=1)
        glow_line(img, PW+20, HH, PW+160, HH, GOLD, w=2, spread=7)

    # Títulos
    tc = WHITE if dark_hdr else TEXT_H
    sc = TEXT_S if dark_hdr else TEXT_B
    draw = ImageDraw.Draw(img)
    draw.text((PW+22, 11), titulo,    font=font(18, bold=True), fill=(*tc,255))
    draw.text((PW+22, 38), subtitulo, font=font(10),            fill=(*sc,200))

    # Badge
    if badge:
        bw = len(badge)*7 + 22
        rounded_rect_layer(img, W-bw-105, 15, W-105, 47, 5, BLUE, 210)
        ImageDraw.Draw(img).text((W-bw-97, 23), badge.upper(),
                                  font=font(8, bold=True), fill=(*WHITE,240))

    # Logo pequeño
    logo(img, W-95, 8, scale=0.70, on_dark=dark_hdr)


# ══════════════════════════════════════════════════════════════════════════════
# LAYOUTS DE CONTENIDO
# ══════════════════════════════════════════════════════════════════════════════
def layout_resumen(img):
    """4 KPI cards + gráfico principal + panel lateral."""
    mx0, mw = PW+18, W-PW-36
    # KPI row
    kw = mw//4 - 5
    accents = [BLUE, GREEN, RED, GOLD]
    for i in range(4):
        card(img, mx0+i*(kw+6), HH+14, mx0+i*(kw+6)+kw, HH+92,
             r=12, accent=accents[i])
    # Main chart
    card(img, mx0, HH+106, mx0+int(mw*0.60), H-18, r=14, accent=BLUE)
    # Side panel
    card(img, mx0+int(mw*0.60)+8, HH+106, mx0+mw, H-18, r=14, accent=BLUE_LIGHT)

def layout_table(img, kpis=3):
    mx0, mw = PW+18, W-PW-36
    kw = mw//kpis - 5
    accents = [BLUE, GREEN, RED, GOLD]
    for i in range(kpis):
        card(img, mx0+i*(kw+6), HH+14, mx0+i*(kw+6)+kw, HH+82,
             r=12, accent=accents[i])
    # Tabla grande con header colorido
    ty0 = HH+98
    card(img, mx0, ty0, mx0+mw, H-18, r=14, accent=BLUE)
    # Simular header de tabla
    rounded_rect_layer(img, mx0, ty0, mx0+mw, ty0+5, 14, BLUE, 255)
    L = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(L).rounded_rectangle([mx0, ty0+3, mx0+mw, ty0+36],
                                         radius=0, fill=(*BLUE,255))
    img.alpha_composite(L)
    # Columnas simuladas en header tabla
    d = ImageDraw.Draw(img)
    cols = ["Vertical", "Cuenta", "Denominación", "Ceco", "Real Mes", "PA Mes", "Variación", "Var%"]
    col_w = mw // len(cols)
    for i, col in enumerate(cols):
        d.text((mx0+6+i*col_w, ty0+12), col, font=font(8, bold=True),
               fill=(*WHITE,220))
    # Filas alternadas
    for r in range(7):
        alpha = 15 if r%2==0 else 0
        L2 = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(L2).rectangle(
            [mx0, ty0+36+r*26, mx0+mw, ty0+36+(r+1)*26],
            fill=(*BLUE_PALE, alpha))
        img.alpha_composite(L2)

def layout_comercial(img):
    mx0, mw = PW+18, W-PW-36
    # 3 KPI
    kw = mw//3 - 5
    for i,acc in enumerate([BLUE, GREEN, RED]):
        card(img, mx0+i*(kw+6), HH+14, mx0+i*(kw+6)+kw, HH+82, r=12, accent=acc)
    # Gráfico barras + donut
    card(img, mx0, HH+98, mx0+int(mw*0.65), H-18, r=14, accent=BLUE)
    card(img, mx0+int(mw*0.65)+8, HH+98, mx0+mw, H-18, r=14, accent=GOLD)

def layout_auditoria(img):
    mx0, mw = PW+18, W-PW-36
    for i,acc in enumerate([BLUE, BLUE, RED]):
        kw = mw//3 - 5
        card(img, mx0+i*(kw+6), HH+14, mx0+i*(kw+6)+kw, HH+82, r=12, accent=acc)
    ty0 = HH+98
    card(img, mx0, ty0, mx0+mw, H-18, r=14, accent=RED)
    rounded_rect_layer(img, mx0, ty0, mx0+mw, ty0+5, 14, RED, 255)
    L = Image.new("RGBA",img.size,(0,0,0,0))
    ImageDraw.Draw(L).rounded_rectangle([mx0,ty0+3,mx0+mw,ty0+36],
                                         radius=0, fill=(*RED,255))
    img.alpha_composite(L)
    cols = ["Vertical","Cuenta","Ceco","Fecha","Monto PA","Monto Base","Diferencia","Motivo"]
    col_w = mw//len(cols)
    d = ImageDraw.Draw(img)
    for i,col in enumerate(cols):
        d.text((mx0+5+i*col_w, ty0+11), col, font=font(7,bold=True), fill=(*WHITE,220))


# ══════════════════════════════════════════════════════════════════════════════
# ÍNDICE PREMIUM (panel oscuro izquierda + botones claros derecha + imagen)
# ══════════════════════════════════════════════════════════════════════════════
def page_indice():
    img = Image.new("RGBA", (W,H), (*NAVY,255))
    draw = ImageDraw.Draw(img)

    # ── Lado izquierdo: panel de marca (45% del ancho) ────────────────────────
    lw = int(W*0.44)
    grad_v(draw, 0, 0, lw, H, NAVY, lerp(NAVY2, NAVY, 0.5))

    # Textura diagonal
    for off in range(-H, W, 50):
        draw.line([(off,0),(off+H,H)], fill=(*BLUE_DARK,10), width=1)

    # Shape orgánico IHSA (blob semicircular en esquina inf-der del panel)
    # Reproducción exacta del Slide 1
    cx_blob, cy_blob = lw+10, H+20
    for r, alpha in [(240,20),(185,16),(130,13),(85,10),(50,8)]:
        L = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(L).ellipse([cx_blob-r,cy_blob-r,cx_blob+r,cy_blob+r],
                                   fill=(*BLUE,alpha))
        img.alpha_composite(L)

    # Línea divisora brillante
    glow_line(img, lw, 0, lw, H, BLUE_LIGHT, w=2, spread=18)

    draw = ImageDraw.Draw(img)

    # Eyebrow
    draw.text((48, 58), "GRUPO IHSA  ·  OPERACIONES COMPLEJAS",
              font=font(9), fill=(*BLUE_LIGHT,150))
    glow_line(img, 48, 76, 340, 76, GOLD, w=1, spread=5)

    # Título principal
    draw = ImageDraw.Draw(img)
    draw.text((48,  88), "Real vs",      font=font(22,bold=True), fill=(*WHITE,170))
    draw.text((48, 120), "Presupuesto",  font=font(44,bold=True), fill=(*WHITE,255))

    glow_line(img, 48, 222, 310, 222, BLUE_LIGHT, w=1, spread=8)
    draw = ImageDraw.Draw(img)
    draw.text((48, 232), "Panel de control presupuestario",
              font=font(11), fill=(*WHITE,140))
    draw.text((48, 252), "Período 2025 – 2026  ·  Operaciones Complejas",
              font=font(9), fill=(*BLUE_LIGHT,110))

    # ZONA IMAGEN VEHICULAR (ambulancia) en parte inferior izquierda
    img_y0, img_y1 = 290, H-55
    img_x0, img_x1 = 30, lw-22
    rounded_rect_layer(img, img_x0, img_y0, img_x1, img_y1, 18, BLUE_DARK, 70)
    rounded_rect_layer(img, img_x0, img_y0, img_x1, img_y1, 18, BLUE_LIGHT, 0,
                       outline=(BLUE_LIGHT, 40))

    draw = ImageDraw.Draw(img)
    cx = (img_x0+img_x1)//2
    cy = (img_y0+img_y1)//2
    draw.text((cx-55, cy-18), "[ IMAGEN AMBULANCIA ]", font=font(10,bold=True),
              fill=(*BLUE_LIGHT,70))
    draw.text((cx-50, cy+4), "Insertar → Imagen en Power BI",
              font=font(8), fill=(*BLUE_LIGHT,45))

    # Gradiente fade en bordes zona imagen
    for i in range(32):
        a = int(85*(1-i/32))
        draw.rectangle([img_x0, img_y0+i, img_x1, img_y0+i+1], fill=(*NAVY,a))
        draw.rectangle([img_x0, img_y1-i-1, img_x1, img_y1-i], fill=(*NAVY,a))

    # Logo
    logo(img, 48, H-42, scale=0.85)

    # ── Lado derecho: grid de navegación ─────────────────────────────────────
    rx0 = lw + 25
    rw  = W - rx0 - 25

    draw = ImageDraw.Draw(img)

    # Header derecho
    draw.text((rx0, 22), "PANEL DE NAVEGACIÓN",
              font=font(13,bold=True), fill=(*TEXT_H,220))
    draw.text((rx0, 44), "Seleccioná la sección que querés analizar",
              font=font(10), fill=(*TEXT_B,180))
    draw.line([(rx0, 66),(W-28,66)], fill=(*CARD_BORDER,200), width=1)
    glow_line(img, rx0, 66, rx0+160, 66, GOLD, w=1, spread=5)

    botones = [
        ("01","Resumen Ejecutivo",   "KPIs globales · Real vs PA",         BLUE),
        ("02","Análisis Comercial",  "Desvío por vertical de negocio",     BLUE),
        ("03","Vista Operativa",     "Detalle por cuenta y ceco",          BLUE),
        ("04","Detalle Proveedores", "Gasto real · Base SAP transaccional",BLUE),
        ("05","Entregable OPEX",     "Clasificación CAPEX/OPEX · CO/GT",   lerp(BLUE,GOLD,0.3)),
        ("06","Auditoría Interna",   "Controles y validaciones de datos",  lerp(BLUE_DARK,RED,0.45)),
    ]

    bw = rw//2 - 6
    bh = (H-84)//3 - 8

    for i,(num,lbl,desc,acc) in enumerate(botones):
        col, row = i%2, i//2
        bx = rx0 + col*(bw+10)
        by = 74 + row*(bh+8)

        shadow(img, bx,by,bx+bw,by+bh, r=12, offset=3, blur=10)

        # Fondo tarjeta blanca
        L = Image.new("RGBA",img.size,(0,0,0,0))
        d = ImageDraw.Draw(L)
        d.rounded_rectangle([bx,by,bx+bw,by+bh], radius=12, fill=(*WHITE,255))
        d.rounded_rectangle([bx,by,bx+bw,by+bh], radius=12,
                             outline=(*CARD_BORDER,150), width=1)
        img.alpha_composite(L)

        # Acento lateral
        La = Image.new("RGBA",img.size,(0,0,0,0))
        da = ImageDraw.Draw(La)
        da.rounded_rectangle([bx,by,bx+6,by+bh], radius=12, fill=(*acc,255))
        da.rounded_rectangle([bx+4,by,bx+6,by+bh], radius=0, fill=(*acc,255))
        img.alpha_composite(La)

        # Número decorativo fondo
        draw = ImageDraw.Draw(img)
        draw.text((bx+bw-42, by+bh//2-18), num, font=font(32,bold=True),
                  fill=(*acc,14))
        # Textos
        draw.text((bx+14, by+14), lbl,  font=font(11,bold=True), fill=(*TEXT_H,230))
        draw.text((bx+14, by+34), desc, font=font(9),            fill=(*TEXT_B,170))
        # Flecha
        draw.text((bx+bw-22, by+bh//2-9), "›", font=font(20), fill=(*acc,160))

    path = f"{OUT}/fondo_00_indice.png"
    img.save(path,"PNG")
    print(f"  ✓  {path}")


# ── Generador genérico ────────────────────────────────────────────────────────
def make(slug, titulo, subtitulo, badge, layout_fn, page_lbl, dark=False):
    img = Image.new("RGBA",(W,H),(*CONTENT_BG,255))
    build_panel(img, page_lbl)
    build_content(img, titulo, subtitulo, badge, dark)
    layout_fn(img)
    p = f"{OUT}/fondo_{slug}.png"
    img.save(p,"PNG")
    print(f"  ✓  {p}")


# ── Tema JSON ─────────────────────────────────────────────────────────────────
def tema_json():
    import json
    t = {
        "name": "GrupoIHSA_v4",
        "dataColors": ["#3267B8","#5294DA","#173773","#C8A028",
                       "#19996E","#C82D32","#7AADDF","#A8C8EE"],
        "background":  "#F6F9FE",
        "foreground":  "#3267B8",
        "tableAccent": "#3267B8",
        "visualStyles": {
            "*": {"*": {
                "fontFamily": [{"value":"Segoe UI"}],
                "fontSize":   [{"value":10}]
            }},
            "card": {"*": {
                "background": [{"color":{"solid":{"color":"#FFFFFF"}}}],
                "border":     [{"show":True,"color":{"solid":{"color":"#3267B8"}},
                                "radius":12}],
                "calloutValue": [{"fontSize":22,"fontBold":True,
                                  "color":{"solid":{"color":"#12204A"}}}],
                "label":        [{"fontSize":9,
                                  "color":{"solid":{"color":"#5A73A0"}}}]
            }},
            "slicer": {"*": {
                "background":  [{"color":{"solid":{"color":"#121840"}}}],
                "border":      [{"show":False}],
                "header":      [{"fontColor":{"solid":{"color":"#FFFFFF"}},
                                 "background":{"solid":{"color":"#173773"}}}],
                "items":       [{"fontColor":{"solid":{"color":"#C8D8F0"}}}]
            }},
            "tableEx": {"*": {
                "header":     [{"fontColor":{"solid":{"color":"#FFFFFF"}},
                                "background":{"solid":{"color":"#3267B8"}}}],
                "values":     [{"fontColor":{"solid":{"color":"#12204A"}}}],
                "grid":       [{"gridVertical":False,"rowPadding":5}],
                "rowHeaders": [{"fontColor":{"solid":{"color":"#12204A"}}}]
            }},
            "matrix": {"*": {
                "header":    [{"fontColor":{"solid":{"color":"#FFFFFF"}},
                               "background":{"solid":{"color":"#3267B8"}}}],
                "values":    [{"fontColor":{"solid":{"color":"#12204A"}}}],
                "subTotals": [{"fontColor":{"solid":{"color":"#3267B8"}},
                               "background":{"solid":{"color":"#EBF1FC"}}}]
            }},
            "lineChart":   {"*": {"lineWidth":[{"value":2}],"markerSize":[{"value":5}]}},
            "barChart":    {"*": {"dataPoint":[{"defaultColor":{"solid":{"color":"#3267B8"}}}]}},
            "columnChart": {"*": {"dataPoint":[{"defaultColor":{"solid":{"color":"#3267B8"}}}]}}
        },
        "good":"#19996E","neutral":"#5294DA","bad":"#C82D32",
        "maximum":"#3267B8","center":"#7CC4E8","minimum":"#173773","null":"#D0DAF0"
    }
    p = f"{OUT}/tema_GrupoIHSA_v4.json"
    with open(p,"w",encoding="utf-8") as f:
        json.dump(t,f,indent=2,ensure_ascii=False)
    print(f"  ✓  {p}")


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__=="__main__":
    print("\n── IHSA Premium v4 ─────────────────────────────────────")
    page_indice()
    make("01_resumen",    "Resumen Ejecutivo",
         "Real vs Presupuesto  ·  Operaciones Complejas  ·  2025–2026",
         "GLOBAL", layout_resumen, "Resumen Ejecutivo")
    make("02_comercial",  "Análisis Comercial",
         "Desvío presupuestario por vertical de negocio",
         "COMERCIAL", layout_comercial, "Comercial")
    make("03_operativa",  "Vista Operativa",
         "Detalle por cuenta contable y centro de costos",
         "OPERATIVA", lambda i: layout_table(i,3), "Operativa")
    make("04_proveedores","Detalle de Proveedores",
         "Gasto real por proveedor  ·  Base SAP transaccional",
         "PROVEEDORES", lambda i: layout_table(i,3), "Proveedores")
    make("05_opex",       "Entregable OPEX",
         "Clasificación operativa  ·  CAPEX / OPEX  ·  CO / GT",
         "OPEX", lambda i: layout_table(i,2), "Entregable OPEX")
    make("06_auditoria",  "Auditoría — Controles y Validaciones",
         "Conciliación entre fuentes  ·  Uso interno  ·  Equipo de datos",
         "AUDITORÍA", layout_auditoria, "Auditoría", dark=True)
    print("\n── Tema ─────────────────────────────────────────────────")
    tema_json()
    print("\n── Archivos ─────────────────────────────────────────────")
    for f in sorted(os.listdir(OUT)):
        print(f"   {f:<48} {os.path.getsize(f'{OUT}/{f}')//1024:>4} KB")
