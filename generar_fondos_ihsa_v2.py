#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grupo IHSA — Dashboard Premium v2
Diseño enterprise de alto impacto visual.
Estética: dark navy + azul corporativo + acentos luminosos + geometría premium.
"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, os, random

OUT = "/home/user/General/assets_ihsa_v2"
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720

# ── Paleta IHSA Premium ───────────────────────────────────────────────────────
# Colores extraídos con precisión del branding IHSA
C_NAVY      = ( 10,  20,  50)      # #0A1432 fondo oscuro base
C_NAVY2     = ( 15,  30,  72)      # #0F1E48 variante panel
C_BLUE_CORP = ( 50, 103, 184)      # #3267B8 azul corporativo IHSA exacto
C_BLUE_MID  = ( 35,  80, 155)      # #23509B
C_BLUE_LT   = ( 82, 148, 218)      # #5294DA acento claro
C_CYAN      = ( 90, 195, 230)      # #5AC3E6 brillo/glow
C_WHITE     = (255, 255, 255)
C_OFF_WHITE = (230, 238, 252)      # blanco azulado
C_SILVER    = (180, 195, 220)      # texto secundario
C_GOLD      = (210, 175,  80)      # #D2AF50 acento dorado premium
C_TEAL      = ( 32, 178, 170)      # acento teal para positivos
C_RED_SOFT  = (220,  70,  70)      # alerta suave
C_PANEL_BG  = ( 18,  28,  65)      # fondo panel lateral
C_CARD_BG   = ( 22,  38,  85)      # fondo tarjetas
C_CONTENT   = ( 14,  22,  52)      # fondo área contenido

PANEL_W   = 245
HEADER_H  = 62

# ── Helpers ───────────────────────────────────────────────────────────────────
def px(rgb, a=255): return (*rgb, a)

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def gradient_v(draw, x0, y0, x1, y1, c_top, c_bot, steps=120):
    h_seg = (y1 - y0) / steps
    for i in range(steps):
        t = i / steps
        c = lerp_color(c_top, c_bot, t)
        draw.rectangle([x0, y0+i*h_seg, x1, y0+(i+1)*h_seg+1], fill=(*c, 255))

def gradient_h(draw, x0, y0, x1, y1, c_left, c_right, steps=200):
    w_seg = (x1 - x0) / steps
    for i in range(steps):
        t = i / steps
        c = lerp_color(c_left, c_right, t)
        draw.rectangle([x0+i*w_seg, y0, x0+(i+1)*w_seg+1, y1], fill=(*c, 255))

def glow_line(img, x0, y0, x1, y1, color, width=2, blur=8):
    """Línea con efecto de brillo/glow."""
    layer = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    for w in range(width+blur, 0, -1):
        alpha = int(255 * (w / (width+blur)) ** 2 * 0.6)
        d.line([(x0,y0),(x1,y1)], fill=(*color, alpha), width=w)
    layer_blur = layer.filter(ImageFilter.GaussianBlur(blur//2))
    img.alpha_composite(layer_blur)
    d2 = ImageDraw.Draw(img)
    d2.line([(x0,y0),(x1,y1)], fill=(*color, 230), width=width)

def dot_grid(draw, x0, y0, x1, y1, spacing=28, color=C_BLUE_MID, alpha=40):
    for x in range(x0, x1, spacing):
        for y in range(y0, y1, spacing):
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(*color, alpha))

def diagonal_lines(draw, x0, y0, x1, y1, gap=40, color=C_BLUE_MID, alpha=18):
    for offset in range(-(y1-y0), (x1-x0), gap):
        sx = x0 + offset
        draw.line([(sx, y0), (sx + (y1-y0), y1)], fill=(*color, alpha), width=1)

def hexgrid(draw, cx, cy, radius=60, color=C_BLUE_LT, alpha=25, rings=3):
    """Patrón hexagonal decorativo."""
    def hex_pts(cx, cy, r):
        return [(cx + r*math.cos(math.radians(60*i-30)),
                 cy + r*math.sin(math.radians(60*i-30))) for i in range(6)]
    draw.polygon(hex_pts(cx, cy, radius), outline=(*color, alpha), fill=None)
    for i in range(6):
        nx = cx + radius*1.73*math.cos(math.radians(60*i))
        ny = cy + radius*1.73*math.sin(math.radians(60*i))
        draw.polygon(hex_pts(nx, ny, radius), outline=(*color, alpha//2), fill=None)

def rounded_rect_aa(img, x0, y0, x1, y1, r, fill_color, alpha=255, outline=None, outline_w=1):
    layer = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x0,y0,x1,y1], radius=r, fill=(*fill_color, alpha))
    if outline:
        d.rounded_rectangle([x0,y0,x1,y1], radius=r, outline=(*outline,200), width=outline_w)
    img.alpha_composite(layer)

def glass_panel(img, x0, y0, x1, y1, r=12, tint=C_BLUE_CORP, alpha_fill=35, alpha_border=80):
    """Efecto glassmorphism."""
    rounded_rect_aa(img, x0, y0, x1, y1, r, tint, alpha_fill)
    rounded_rect_aa(img, x0, y0, x1, y1, r, C_BLUE_LT, 0, outline=C_BLUE_LT, outline_w=1)
    # Brillo superior
    layer = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x0+1, y0+1, x1-1, y0+r+8], radius=r,
                         fill=(*C_WHITE, 12))
    img.alpha_composite(layer)

def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        try: return ImageFont.truetype(p, size)
        except: pass
    return ImageFont.load_default()

def draw_logo_premium(img, x, y, scale=1.0):
    """Logo IHSA con tipografía premium y acento de color."""
    d = ImageDraw.Draw(img)
    fnt_g = get_font(int(9*scale), bold=False)
    fnt_i = get_font(int(30*scale), bold=True)
    # Acento vertical dorado a la izquierda del logo
    lh = int(42*scale)
    d.rectangle([x, y+2, x+3, y+lh], fill=(*C_BLUE_LT, 255))
    d.text((x+9, y),          "GRUPO", font=fnt_g, fill=(*C_SILVER, 200))
    d.text((x+8, y+int(10*scale)), "IHSA",  font=fnt_i, fill=(*C_OFF_WHITE, 255))

def accent_arc(draw, cx, cy, r_out, r_in, start_deg, end_deg, color, alpha=160):
    """Arco de acento decorativo."""
    steps = max(30, (end_deg - start_deg))
    for i in range(steps):
        t1 = math.radians(start_deg + i*(end_deg-start_deg)/steps)
        t2 = math.radians(start_deg + (i+1)*(end_deg-start_deg)/steps)
        pts = [
            (cx + r_out*math.cos(t1), cy + r_out*math.sin(t1)),
            (cx + r_out*math.cos(t2), cy + r_out*math.sin(t2)),
            (cx + r_in*math.cos(t2),  cy + r_in*math.sin(t2)),
            (cx + r_in*math.cos(t1),  cy + r_in*math.sin(t1)),
        ]
        draw.polygon(pts, fill=(*color, alpha))

def kpi_zone_label(draw, x, y, label, value_hint="", color=C_SILVER):
    fnt_l = get_font(8)
    fnt_v = get_font(9, bold=True)
    draw.text((x, y),   label.upper(),  font=fnt_l, fill=(*color, 160))
    if value_hint:
        draw.text((x, y+11), value_hint, font=fnt_v, fill=(*C_OFF_WHITE, 120))

# ══════════════════════════════════════════════════════════════════════════════
# BASE: construye el fondo dark premium común a todas las páginas
# ══════════════════════════════════════════════════════════════════════════════
def build_base(tipo="content"):
    img = Image.new("RGBA", (W, H), px(C_NAVY))
    draw = ImageDraw.Draw(img)

    # ── Fondo: gradiente diagonal profundo ──────────────────────────────────
    gradient_v(draw, 0, 0, W, H, C_NAVY, C_NAVY2, steps=150)

    # ── Patrón de puntos en zona contenido ──────────────────────────────────
    dot_grid(draw, PANEL_W, HEADER_H, W, H, spacing=32, color=C_BLUE_MID, alpha=28)

    # ── Hexágonos decorativos sutiles (esquina inferior derecha) ────────────
    hexgrid(draw, W-160, H-130, radius=55, color=C_BLUE_LT, alpha=18, rings=2)
    hexgrid(draw, W-80,  H-60,  radius=30, color=C_BLUE_LT, alpha=12)

    # ── Panel lateral ────────────────────────────────────────────────────────
    gradient_h(draw, 0, 0, PANEL_W, H, C_NAVY2, C_PANEL_BG, steps=60)

    # Líneas diagonales en panel
    diagonal_lines(draw, 0, 0, PANEL_W, H, gap=35, color=C_BLUE_CORP, alpha=14)

    # Arco decorativo en panel (esquina inferior)
    accent_arc(draw, PANEL_W-10, H+30, 180, 120, 150, 210,
               C_BLUE_CORP, alpha=55)
    accent_arc(draw, PANEL_W-10, H+30, 120,  85, 150, 210,
               C_BLUE_LT,  alpha=40)

    # ── Separador panel / contenido (línea luminosa) ──────────────────────
    glow_line(img, PANEL_W, 0, PANEL_W, H, C_BLUE_LT, width=1, blur=10)

    # ── Header área de contenido ─────────────────────────────────────────────
    gradient_h(draw, PANEL_W, 0, W, HEADER_H, C_NAVY2, C_PANEL_BG, steps=80)

    # Línea inferior header (glow)
    glow_line(img, PANEL_W, HEADER_H, W, HEADER_H, C_BLUE_CORP, width=1, blur=8)

    # Línea de acento dorada en header (solo 40% del ancho)
    accent_x = PANEL_W + int((W-PANEL_W)*0.40)
    glow_line(img, PANEL_W, HEADER_H, accent_x, HEADER_H, C_GOLD, width=1, blur=6)

    # ── Franja inferior decorativa ────────────────────────────────────────────
    gradient_h(draw, PANEL_W, H-26, W, H, C_NAVY2, C_PANEL_BG, steps=60)
    glow_line(img, PANEL_W, H-26, W, H-26, C_BLUE_MID, width=1, blur=6)

    return img

# ══════════════════════════════════════════════════════════════════════════════
# TEMPLATE A — Páginas de contenido (Resumen, Comercial, Operativa, etc.)
# ══════════════════════════════════════════════════════════════════════════════
def template_content(slug, titulo, subtitulo, badge=None):
    img = build_base()
    draw = ImageDraw.Draw(img)

    # ── Logo en panel lateral ────────────────────────────────────────────────
    draw_logo_premium(img, 22, H-165, scale=1.15)

    # ── Zona segmentadores en panel ──────────────────────────────────────────
    labels = [("Período","MesAño"), ("Vertical","Negocio"), ("Cuenta","Contable"), ("Ceco","Centro costos")]
    sy = 72
    for lbl, hint in labels:
        kpi_zone_label(draw, 18, sy, lbl, hint)
        # Slot segmentador (glassmorphism)
        glass_panel(img, 12, sy+14, PANEL_W-12, sy+38, r=6,
                    tint=C_BLUE_CORP, alpha_fill=28)
        # Triángulo dropdown hint
        draw.polygon([(PANEL_W-28, sy+22), (PANEL_W-20, sy+22), (PANEL_W-24, sy+30)],
                     fill=(*C_BLUE_LT, 120))
        sy += 60

    # ── Título en header ─────────────────────────────────────────────────────
    fnt_titulo    = get_font(19, bold=True)
    fnt_subtitulo = get_font(10)
    fnt_badge     = get_font(8, bold=True)

    draw.text((PANEL_W+22, 10), titulo,    font=fnt_titulo,    fill=(*C_OFF_WHITE, 255))
    draw.text((PANEL_W+22, 36), subtitulo, font=fnt_subtitulo, fill=(*C_SILVER, 180))

    # Badge de sección (si aplica)
    if badge:
        bw = 90
        rounded_rect_aa(img, W-120, 14, W-120+bw, 44, r=5,
                        fill_color=C_BLUE_CORP, alpha=60,
                        outline=C_BLUE_LT, outline_w=1)
        draw.text((W-114, 22), badge.upper(), font=fnt_badge, fill=(*C_CYAN, 200))

    # Logo pequeño en header (derecha)
    draw_logo_premium(img, W-95, 6, scale=0.7)

    # ── Zona KPI (placeholders visuales para tarjetas) ────────────────────
    # 4 slots de tarjetas en la fila superior del área de contenido
    kpi_y0, kpi_y1 = HEADER_H+14, HEADER_H+90
    kpi_x0 = PANEL_W + 20
    slot_w = int((W - kpi_x0 - 20) / 4) - 8
    for i in range(4):
        sx = kpi_x0 + i*(slot_w+8)
        glass_panel(img, sx, kpi_y0, sx+slot_w, kpi_y1, r=10,
                    tint=C_CARD_BG, alpha_fill=85, alpha_border=60)
        # Línea de acento en borde superior de cada card
        glow_line(img, sx+12, kpi_y0+1, sx+slot_w-12, kpi_y0+1,
                  C_BLUE_LT, width=1, blur=4)

    # ── Zona principal de visuales (área grande) ──────────────────────────
    main_y0 = HEADER_H + 104
    main_x0 = PANEL_W + 20

    # Contenedor izquierdo grande (60%)
    main_w_l = int((W - main_x0 - 28) * 0.60)
    glass_panel(img, main_x0, main_y0, main_x0+main_w_l, H-40, r=12,
                tint=C_CARD_BG, alpha_fill=70, alpha_border=50)

    # Contenedor derecho (40%)
    right_x0 = main_x0 + main_w_l + 8
    glass_panel(img, right_x0, main_y0, W-20, H-40, r=12,
                tint=C_CARD_BG, alpha_fill=70, alpha_border=50)

    # Micro-grid decorativo dentro de los contenedores
    dot_grid(draw, main_x0+10, main_y0+10, main_x0+main_w_l-10, H-50,
             spacing=40, color=C_BLUE_LT, alpha=12)

    path = f"{OUT}/fondo_{slug}.png"
    img.save(path, "PNG")
    print(f"  ✓  {path}")
    return path

# ══════════════════════════════════════════════════════════════════════════════
# TEMPLATE B — Índice / Portada
# Full dark premium con jerarquía visual máxima
# ══════════════════════════════════════════════════════════════════════════════
def template_indice():
    img = Image.new("RGBA", (W, H), px(C_NAVY))
    draw = ImageDraw.Draw(img)

    # ── Fondo gradiente profundo ──────────────────────────────────────────────
    gradient_v(draw, 0, 0, W, H, C_NAVY, (8, 16, 42), steps=160)

    # ── Geometría de fondo (formas angulares premium) ─────────────────────────
    # Forma diagonal grande izquierda
    pts_diag = [(0,0), (int(W*0.42),0), (int(W*0.32), H), (0, H)]
    layer_shape = Image.new("RGBA", (W,H), (0,0,0,0))
    ds = ImageDraw.Draw(layer_shape)
    ds.polygon(pts_diag, fill=(*C_PANEL_BG, 255))
    img.alpha_composite(layer_shape)
    draw = ImageDraw.Draw(img)

    # Líneas diagonales en zona izquierda
    diagonal_lines(draw, 0, 0, int(W*0.42), H, gap=38, color=C_BLUE_CORP, alpha=18)

    # Arcos en fondo derecho
    accent_arc(draw, W, H, 400, 300, 140, 200, C_BLUE_CORP, alpha=30)
    accent_arc(draw, W, H, 300, 240, 140, 200, C_BLUE_LT,   alpha=25)
    accent_arc(draw, W, H, 240, 200, 140, 200, C_CYAN,      alpha=18)

    # Dot grid derecha
    dot_grid(draw, int(W*0.42), 0, W, H, spacing=30, color=C_BLUE_MID, alpha=30)
    hexgrid(draw, W-200, H-180, radius=70, color=C_BLUE_LT, alpha=16)

    # ── Línea divisora vertical luminosa ──────────────────────────────────────
    div_x = int(W*0.42)
    glow_line(img, div_x, 0, div_x, H, C_BLUE_LT, width=1, blur=14)

    # ── Panel izquierdo: branding y subtítulo ─────────────────────────────────
    draw = ImageDraw.Draw(img)
    fnt_eyebrow = get_font(10)
    fnt_title   = get_font(42, bold=True)
    fnt_title2  = get_font(22, bold=True)
    fnt_sub     = get_font(11)
    fnt_small   = get_font(9)

    # Eyebrow text
    draw.text((48, 64), "OPERACIONES COMPLEJAS · 2025–2026",
              font=fnt_eyebrow, fill=(*C_BLUE_LT, 180))
    # Línea acento bajo eyebrow
    glow_line(img, 48, 82, 48+220, 82, C_GOLD, width=1, blur=5)

    # Título grande
    draw.text((48, 95),  "Real vs",        font=fnt_title2, fill=(*C_SILVER, 210))
    draw.text((48, 128), "Presupuesto",    font=fnt_title,  fill=(*C_OFF_WHITE, 255))

    # Acento bajo título
    glow_line(img, 48, 222, 220, 222, C_BLUE_CORP, width=2, blur=8)

    draw.text((48, 234), "Panel de control presupuestario",
              font=fnt_sub, fill=(*C_SILVER, 160))
    draw.text((48, 252), "Grupo IHSA · Operaciones Complejas",
              font=fnt_sub, fill=(*C_BLUE_LT, 140))

    # Logo premium grande (parte inferior panel)
    draw_logo_premium(img, 48, H-130, scale=1.8)

    # ── Panel derecho: botones de navegación ─────────────────────────────────
    right_x0 = div_x + 30
    right_w   = W - right_x0 - 30

    # Header zona derecha
    draw.text((right_x0, 24), "SELECCIONÁ UNA SECCIÓN",
              font=get_font(11, bold=True), fill=(*C_OFF_WHITE, 200))
    draw.text((right_x0, 42), "Panel de navegación rápida",
              font=fnt_small, fill=(*C_SILVER, 140))
    glow_line(img, right_x0, 62, W-30, 62, C_BLUE_CORP, width=1, blur=6)

    botones = [
        ("01", "Resumen Ejecutivo",     "KPIs globales · Real vs PA",     C_BLUE_CORP),
        ("02", "Análisis Comercial",    "Desvío por vertical de negocio", C_BLUE_MID),
        ("03", "Vista Operativa",       "Detalle cuenta y ceco",          C_BLUE_MID),
        ("04", "Detalle Proveedores",   "Gasto real · Base SAP",          C_BLUE_MID),
        ("05", "Entregable OPEX",       "Resumen operativo mensual",      C_BLUE_MID),
        ("06", "Auditoría Interna",     "Controles y validaciones",       C_NAVY2),
    ]

    cols, rows = 2, 3
    btn_w = right_w // cols - 8
    btn_h = (H - 90) // rows - 12
    gx, gy = right_x0, 76

    fnt_num  = get_font(20, bold=True)
    fnt_btn  = get_font(10, bold=True)
    fnt_desc = get_font(8)

    for i, (num, label, desc, color) in enumerate(botones):
        col = i % cols
        row = i // cols
        bx = gx + col*(btn_w+8)
        by = gy + row*(btn_h+10)

        # Fondo glass del botón
        glass_panel(img, bx, by, bx+btn_w, by+btn_h, r=10,
                    tint=color, alpha_fill=65, alpha_border=70)

        # Número (grande, semi-transparente, esquina)
        d2 = ImageDraw.Draw(img)
        d2.text((bx+btn_w-38, by+6), num, font=fnt_num,
                fill=(*C_BLUE_LT, 45))

        # Acento de color en borde izquierdo
        glass_panel(img, bx, by, bx+4, by+btn_h, r=4,
                    tint=C_BLUE_LT, alpha_fill=180)

        # Texto
        d2.text((bx+14, by+14), label, font=fnt_btn,  fill=(*C_OFF_WHITE, 240))
        d2.text((bx+14, by+32), desc,  font=fnt_desc, fill=(*C_SILVER,    160))

        # Ícono flecha →
        d2.text((bx+btn_w-20, by+btn_h-22), "›", font=get_font(18),
                fill=(*C_BLUE_LT, 160))

    path = f"{OUT}/fondo_00_indice.png"
    img.save(path, "PNG")
    print(f"  ✓  {path}")
    return path

# ══════════════════════════════════════════════════════════════════════════════
# TEMPLATE C — Auditoría (diferenciado: más oscuro, feel técnico)
# ══════════════════════════════════════════════════════════════════════════════
def template_auditoria():
    img = Image.new("RGBA", (W, H), px(C_NAVY))
    draw = ImageDraw.Draw(img)

    gradient_v(draw, 0, 0, W, H, (8,14,35), (12,20,50), steps=150)
    dot_grid(draw, 0, 0, W, H, spacing=28, color=C_BLUE_MID, alpha=22)

    # Panel lateral más angosto
    PW = 200
    gradient_h(draw, 0, 0, PW, H, (12,22,58), (8,16,42), steps=50)
    diagonal_lines(draw, 0, 0, PW, H, gap=30, color=C_BLUE_CORP, alpha=16)
    accent_arc(draw, PW+10, H+20, 150, 100, 150, 210, C_BLUE_CORP, alpha=40)
    glow_line(img, PW, 0, PW, H, C_RED_SOFT, width=1, blur=12)

    # Header oscuro intenso
    gradient_h(draw, PW, 0, W, HEADER_H, (10,18,48), (15,25,60), steps=80)
    glow_line(img, PW, HEADER_H, W, HEADER_H, C_RED_SOFT, width=1, blur=8)
    glow_line(img, PW, HEADER_H, PW+int((W-PW)*0.35), HEADER_H, C_GOLD, width=1, blur=5)

    draw = ImageDraw.Draw(img)

    # Logo
    draw_logo_premium(img, 16, H-130, scale=1.0)

    # Slots segmentadores
    for i, (lbl, hint) in enumerate([("Período","MesAño"),("Vertical","Negocio")]):
        sy = 72 + i*60
        kpi_zone_label(draw, 14, sy, lbl, hint)
        glass_panel(img, 10, sy+14, PW-10, sy+38, r=6, tint=C_BLUE_CORP, alpha_fill=30)

    # Header título
    fnt_t = get_font(17, bold=True)
    fnt_s = get_font(9)
    draw.text((PW+20, 12), "Auditoría — Controles y Validaciones",
              font=fnt_t, fill=(*C_OFF_WHITE, 255))
    draw.text((PW+20, 36), "Conciliación entre fuentes · Uso interno · Equipo de datos",
              font=fnt_s, fill=(*C_SILVER, 170))

    # Badge USO INTERNO
    glass_panel(img, W-145, 13, W-20, 40, r=5, tint=(180,40,40), alpha_fill=50)
    draw.text((W-138, 20), "⚠  USO INTERNO", font=get_font(8, bold=True),
              fill=(*C_RED_SOFT, 220))

    draw_logo_premium(img, W-95, 6, scale=0.68)

    # Zonas de contenido
    cy0 = HEADER_H + 14
    # 3 KPI cards arriba
    slot_w2 = int((W-PW-28)/3) - 6
    for i in range(3):
        sx = PW+20 + i*(slot_w2+8)
        glass_panel(img, sx, cy0, sx+slot_w2, cy0+72, r=8,
                    tint=C_CARD_BG, alpha_fill=80)
        glow_line(img, sx+10, cy0+1, sx+slot_w2-10, cy0+1, C_RED_SOFT, width=1, blur=4)

    # Tabla grande
    glass_panel(img, PW+20, cy0+86, W-20, H-36, r=10,
                tint=C_CARD_BG, alpha_fill=75)
    glow_line(img, PW+20, cy0+86, W-20, cy0+86, C_BLUE_CORP, width=1, blur=6)

    # Franja footer
    gradient_h(draw, PW, H-24, W, H, (10,18,48), (15,25,60), steps=60)
    glow_line(img, PW, H-24, W, H-24, C_BLUE_MID, width=1, blur=5)

    path = f"{OUT}/fondo_06_auditoria.png"
    img.save(path, "PNG")
    print(f"  ✓  {path}")
    return path

# ── Tema JSON v2 ──────────────────────────────────────────────────────────────
def generar_tema_json():
    import json
    tema = {
        "name": "GrupoIHSA_Premium",
        "dataColors": ["#5294DA","#3267B8","#7CC4E8","#20488C","#D2AF50",
                       "#20B2AA","#7AADDF","#A8C8EE"],
        "background":   "#0A1432",
        "foreground":   "#5294DA",
        "tableAccent":  "#3267B8",
        "visualStyles": {
            "*": {"*": {
                "fontFamily": [{"value": "Segoe UI"}],
                "background": [{"color": {"solid": {"color": "#16265580"}}}]
            }},
            "card": {"*": {
                "background":  [{"color": {"solid": {"color": "#162655"}}}],
                "border":      [{"show": True, "color": {"solid": {"color": "#3267B8"}}, "radius": 10}],
                "calloutValue":[{"fontSize": 22, "fontBold": True,
                                 "color": {"solid": {"color": "#E6EEFA"}}}],
                "label":       [{"fontSize": 9, "color": {"solid": {"color": "#8AABD4"}}}]
            }},
            "slicer": {"*": {
                "background": [{"color": {"solid": {"color": "#162655"}}}],
                "border":     [{"show": False}],
                "header":     [{"fontColor": {"solid": {"color": "#E6EEFA"}},
                                "background": {"solid": {"color": "#20488C"}}}],
                "items":      [{"fontColor": {"solid": {"color": "#C8D8F0"}}}]
            }},
            "tableEx": {"*": {
                "header":     [{"fontColor": {"solid": {"color": "#FFFFFF"}},
                                "background": {"solid": {"color": "#3267B8"}}}],
                "rowHeaders": [{"fontColor": {"solid": {"color": "#C8D8F0"}}}],
                "values":     [{"fontColor": {"solid": {"color": "#E6EEFA"}}}],
                "grid":       [{"gridVertical": False, "rowPadding": 5,
                                "outlineColor": {"solid": {"color": "#20488C"}}}]
            }},
            "matrix": {"*": {
                "header":  [{"fontColor": {"solid": {"color": "#FFFFFF"}},
                             "background": {"solid": {"color": "#3267B8"}}}],
                "values":  [{"fontColor": {"solid": {"color": "#E6EEFA"}}}],
                "subTotals":[{"fontColor": {"solid": {"color": "#5294DA"}},
                              "background": {"solid": {"color": "#0F1E48"}}}]
            }},
            "lineChart": {"*": {
                "lineWidth":  [{"value": 2}],
                "markerSize": [{"value": 5}],
                "dataPoint":  [{"defaultColor": {"solid": {"color": "#5294DA"}}}]
            }},
            "barChart":  {"*": {
                "dataPoint": [{"defaultColor": {"solid": {"color": "#3267B8"}}}]
            }}
        },
        "good":    "#20B2AA",
        "neutral": "#5294DA",
        "bad":     "#DC4646",
        "maximum": "#3267B8",
        "center":  "#7CC4E8",
        "minimum": "#20488C",
        "null":    "#2A3A6A"
    }
    path = f"{OUT}/tema_GrupoIHSA_Premium.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tema, f, indent=2, ensure_ascii=False)
    print(f"  ✓  {path}")

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n── Generando fondos IHSA Premium v2 ────────────────────")
    template_indice()
    template_content("01_resumen",   "Resumen Ejecutivo",
                     "Real vs Presupuesto  ·  Operaciones Complejas  ·  2025-2026",
                     "GLOBAL")
    template_content("02_comercial", "Análisis Comercial",
                     "Desvío presupuestario por vertical de negocio",
                     "COMERCIAL")
    template_content("03_operativa", "Vista Operativa",
                     "Detalle por cuenta contable y centro de costos",
                     "OPERATIVA")
    template_content("04_proveedores","Detalle de Proveedores",
                     "Gasto real por proveedor  ·  Base SAP transaccional",
                     "PROVEEDORES")
    template_content("05_opex",      "Entregable OPEX",
                     "Resumen de gastos operativos  ·  Clasificación CAPEX/OPEX",
                     "OPEX")
    template_auditoria()

    print("\n── Generando tema Power BI Premium ─────────────────────")
    generar_tema_json()

    print("\n── Assets finales ───────────────────────────────────────")
    for f in sorted(os.listdir(OUT)):
        kb = os.path.getsize(f"{OUT}/{f}") // 1024
        print(f"   {f:<45} {kb:>4} KB")
    print()
