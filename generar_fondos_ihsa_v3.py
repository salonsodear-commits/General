#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grupo IHSA — Dashboard Premium v3
Filosofía: panel lateral oscuro (dark navy) + contenido claro (blanco/gris suave)
Inspiración directa: Mercedes-Benz, SAP Analytics, Zebra BI premium.
"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, os

OUT = "/home/user/General/assets_ihsa_v3"
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720

# ── Paleta ────────────────────────────────────────────────────────────────────
NAVY        = (13,  26,  70)      # panel lateral — azul noche IHSA
NAVY2       = (18,  36,  90)      # variante más clara del panel
BLUE_CORP   = (50, 103, 184)      # #3267B8 azul corporativo exacto IHSA
BLUE_MED    = (70, 130, 200)      # acento interactivo
BLUE_LT     = (110, 165, 225)     # brillo / highlights
CYAN_GLOW   = ( 80, 190, 230)     # glow especial
WHITE       = (255, 255, 255)
CONTENT_BG  = (247, 249, 253)     # fondo contenido: blanco muy suave azulado
CARD_BG     = (255, 255, 255)     # tarjetas: blanco puro
CARD_BORDER = (220, 232, 248)     # borde tarjetas
HEADER_BG   = (255, 255, 255)     # header claro
DIVIDER     = (210, 225, 245)     # líneas separadoras
TEXT_DARK   = ( 25,  40,  80)     # texto principal
TEXT_MED    = ( 90, 115, 160)     # texto secundario
TEXT_LIGHT  = (160, 185, 220)     # texto terciario / placeholders
GOLD        = (210, 170,  60)     # acento dorado para detalles premium
RED_ALERT   = (200,  50,  50)
GREEN_POS   = ( 32, 160, 120)

PANEL_W  = 252
HEADER_H = 64

# ── Font helper ───────────────────────────────────────────────────────────────
def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        try: return ImageFont.truetype(p, size)
        except: pass
    return ImageFont.load_default()

# ── Color helpers ─────────────────────────────────────────────────────────────
def lerp(c1, c2, t):
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

def grad_v(draw, x0, y0, x1, y1, top, bot, n=100):
    h = (y1-y0)/n
    for i in range(n):
        c = lerp(top, bot, i/n)
        draw.rectangle([x0, y0+i*h, x1, y0+(i+1)*h+1], fill=(*c,255))

def grad_h(draw, x0, y0, x1, y1, left, right, n=200):
    w = (x1-x0)/n
    for i in range(n):
        c = lerp(left, right, i/n)
        draw.rectangle([x0+i*w, y0, x0+(i+1)*w+1, y1], fill=(*c,255))

def alpha_rect(img, x0, y0, x1, y1, color, alpha, radius=0):
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    if radius:
        d.rounded_rectangle([x0,y0,x1,y1], radius=radius, fill=(*color,alpha))
    else:
        d.rectangle([x0,y0,x1,y1], fill=(*color,alpha))
    img.alpha_composite(L)

def glow(img, x0, y0, x1, y1, color, thickness=2, spread=10):
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    for w in range(spread, 0, -1):
        a = int(120*(w/spread)**2)
        d.line([(x0,y0),(x1,y1)], fill=(*color,a), width=w)
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(spread//3)))
    ImageDraw.Draw(img).line([(x0,y0),(x1,y1)], fill=(*color,200), width=thickness)

def drop_shadow(img, x0, y0, x1, y1, radius=14, offset=4, blur=12):
    """Sombra suave bajo las tarjetas (efecto depth)."""
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([x0+offset, y0+offset, x1+offset, y1+offset],
                         radius=radius, fill=(TEXT_DARK[0],TEXT_DARK[1],TEXT_DARK[2],40))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(blur)))

def card(img, x0, y0, x1, y1, r=14, shadow=True, accent_color=None):
    """Tarjeta blanca con sombra y acento de color en borde superior."""
    if shadow:
        drop_shadow(img, x0, y0, x1, y1, radius=r, offset=3, blur=10)
    alpha_rect(img, x0, y0, x1, y1, CARD_BG, 255, radius=r)
    # Borde sutil
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([x0,y0,x1,y1], radius=r, outline=(*CARD_BORDER,180), width=1)
    img.alpha_composite(L)
    # Acento de color en borde superior
    if accent_color:
        L2 = Image.new("RGBA", img.size, (0,0,0,0))
        d2 = ImageDraw.Draw(L2)
        d2.rounded_rectangle([x0,y0,x1,y0+4], radius=r//2, fill=(*accent_color,255))
        img.alpha_composite(L2)

def slicer_slot(img, draw, x0, y, label, w=228):
    """Slot de segmentador premium: label + campo redondeado."""
    fnt_lbl = font(8)
    fnt_val = font(9)
    draw.text((x0, y), label.upper(), font=fnt_lbl, fill=(*TEXT_LIGHT,200))
    # Campo
    slot_y0, slot_y1 = y+12, y+34
    alpha_rect(img, x0, slot_y0, x0+w, slot_y1, NAVY2, 200, radius=6)
    # Borde del campo
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([x0, slot_y0, x0+w, slot_y1], radius=6,
                         outline=(*BLUE_MED, 90), width=1)
    img.alpha_composite(L)
    # Texto placeholder
    draw.text((x0+10, slot_y0+6), "Todos", font=fnt_val, fill=(*TEXT_LIGHT,130))
    # Chevron ▾
    draw.text((x0+w-18, slot_y0+5), "▾", font=font(10), fill=(*BLUE_LT,160))

def ihsa_logo(img, x, y, scale=1.0, light=True):
    """Logo IHSA: línea de acento + GRUPO + IHSA."""
    d = ImageDraw.Draw(img)
    fnt_g = font(int(8*scale))
    fnt_i = font(int(27*scale), bold=True)
    # Barra vertical de acento (azul claro)
    bar_h = int(38*scale)
    color_bar = BLUE_LT if light else BLUE_CORP
    color_txt = WHITE if light else TEXT_DARK
    d.rectangle([x, y+2, x+3, y+2+bar_h], fill=(*color_bar,255))
    d.text((x+8, y),               "GRUPO", font=fnt_g, fill=(*color_txt,180))
    d.text((x+8, y+int(9*scale)),  "IHSA",  font=fnt_i, fill=(*color_txt,255))

def nav_label(draw, x, y, text, active=False):
    fnt = font(9, bold=active)
    color = WHITE if active else TEXT_LIGHT
    draw.text((x, y), text, font=fnt, fill=(*color, 220 if active else 150))
    if active:
        draw.rectangle([x-12, y+1, x-8, y+12], fill=(*BLUE_LT,255))

# ══════════════════════════════════════════════════════════════════════════════
# PANEL LATERAL BASE — común a todas las páginas
# ══════════════════════════════════════════════════════════════════════════════
def build_panel(img, page_name=""):
    draw = ImageDraw.Draw(img)

    # Fondo panel: gradiente vertical navy profundo
    grad_v(draw, 0, 0, PANEL_W, H, NAVY, lerp(NAVY, NAVY2, 0.6))

    # Textura sutil: líneas diagonales muy tenues
    for offset in range(-H, W, 48):
        draw.line([(offset, 0), (offset+H, H)],
                  fill=(*BLUE_MED, 10), width=1)

    # Forma orgánica en esquina inferior derecha del panel
    # (círculo grande que "emerge" — estilo IHSA slides)
    cx, cy = PANEL_W + 20, H + 30
    r_out, r_in = 210, 150
    # Capa exterior difuminada
    alpha_rect(img, 0, H-r_out+20, PANEL_W, H, NAVY2, 0)  # reset
    L = Image.new("RGBA", img.size, (0,0,0,0))
    dL = ImageDraw.Draw(L)
    dL.ellipse([cx-r_out, cy-r_out, cx+r_out, cy+r_out], fill=(*BLUE_CORP, 38))
    img.alpha_composite(L)
    L2 = Image.new("RGBA", img.size, (0,0,0,0))
    dL2 = ImageDraw.Draw(L2)
    dL2.ellipse([cx-r_in, cy-r_in, cx+r_in, cy+r_in], fill=(*BLUE_MED, 28))
    img.alpha_composite(L2)

    # Línea separadora panel/contenido
    glow(img, PANEL_W, 0, PANEL_W, H, BLUE_CORP, thickness=1, spread=12)

    draw = ImageDraw.Draw(img)

    # ── Logo en parte superior del panel ───────────────────────────────────
    ihsa_logo(img, 22, 22, scale=1.1)

    # Línea bajo logo
    draw.line([(18, 74), (PANEL_W-18, 74)], fill=(*BLUE_MED, 50), width=1)

    # ── Título de sección en panel ─────────────────────────────────────────
    if page_name:
        fnt_sec = font(8)
        draw.text((18, 82), "SECCIÓN ACTIVA", font=fnt_sec,
                  fill=(*BLUE_LT, 120))
        fnt_pname = font(10, bold=True)
        draw.text((18, 94), page_name, font=fnt_pname,
                  fill=(*WHITE, 210))

    # ── Slots de segmentadores ─────────────────────────────────────────────
    sy = 128
    for lbl in ["Período (MesAño)", "Vertical", "Cuenta", "Ceco"]:
        slicer_slot(img, draw, 18, sy, lbl, w=PANEL_W-36)
        sy += 60

    # ── Separador ──────────────────────────────────────────────────────────
    draw.line([(18, sy+4), (PANEL_W-18, sy+4)], fill=(*BLUE_MED, 40), width=1)

    # ── Logo en parte inferior del panel ───────────────────────────────────
    ihsa_logo(img, 22, H-100, scale=0.95)

    # Versión / pie
    fnt_v = font(7)
    draw.text((18, H-45), "Real vs Presupuesto · 2025–2026",
              font=fnt_v, fill=(*TEXT_LIGHT, 100))
    draw.text((18, H-32), "Operaciones Complejas",
              font=fnt_v, fill=(*TEXT_LIGHT, 80))

# ══════════════════════════════════════════════════════════════════════════════
# ÁREA DE CONTENIDO BASE — header + zona visual
# ══════════════════════════════════════════════════════════════════════════════
def build_content_area(img, titulo, subtitulo, badge=None, dark_header=False):
    draw = ImageDraw.Draw(img)

    # Fondo contenido: blanco suave
    draw.rectangle([PANEL_W+1, 0, W, H], fill=(*CONTENT_BG, 255))

    # ── Header ────────────────────────────────────────────────────────────
    header_color = NAVY if dark_header else HEADER_BG
    draw.rectangle([PANEL_W+1, 0, W, HEADER_H], fill=(*header_color, 255))

    # Línea inferior header
    if dark_header:
        glow(img, PANEL_W+1, HEADER_H, W, HEADER_H, BLUE_CORP, thickness=1, spread=8)
    else:
        draw.line([(PANEL_W+20, HEADER_H), (W-20, HEADER_H)],
                  fill=(*DIVIDER, 255), width=1)
        # Acento dorado corto bajo el título
        glow(img, PANEL_W+20, HEADER_H, PANEL_W+180, HEADER_H,
             GOLD, thickness=2, spread=6)

    # Título y subtítulo
    txt_color = WHITE if dark_header else TEXT_DARK
    sub_color  = TEXT_LIGHT if dark_header else TEXT_MED

    fnt_t = font(18, bold=True)
    fnt_s = font(10)
    draw = ImageDraw.Draw(img)
    draw.text((PANEL_W+22, 11), titulo,    font=fnt_t, fill=(*txt_color, 255))
    draw.text((PANEL_W+22, 38), subtitulo, font=fnt_s, fill=(*sub_color, 200))

    # Badge sección (esquina derecha header)
    if badge:
        bw = len(badge)*7 + 24
        bx = W - bw - 110
        alpha_rect(img, bx, 16, bx+bw, 46, BLUE_CORP, 220, radius=5)
        draw = ImageDraw.Draw(img)
        draw.text((bx+10, 24), badge.upper(), font=font(8, bold=True),
                  fill=(*WHITE, 230))

    # Logo pequeño arriba derecha
    ihsa_logo(img, W-95, 8, scale=0.72, light=(not dark_header))

# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT DE TARJETAS — Resumen Ejecutivo y páginas de análisis
# ══════════════════════════════════════════════════════════════════════════════
def layout_kpi_plus_charts(img, n_kpi=4, has_right_panel=True):
    """
    Zona superior: n_kpi tarjetas KPI
    Zona inferior: gráfico grande izquierda + panel derecho (opcional)
    """
    mx0 = PANEL_W + 18
    my0 = HEADER_H + 14
    mw  = W - mx0 - 18

    # ── KPI cards ────────────────────────────────────────────────────────────
    kpi_h = 82
    kpi_w = mw // n_kpi - 6
    accent_colors = [BLUE_CORP, BLUE_MED, GOLD, GREEN_POS]
    for i in range(n_kpi):
        kx = mx0 + i*(kpi_w+6)
        card(img, kx, my0, kx+kpi_w, my0+kpi_h, r=12, shadow=True,
             accent_color=accent_colors[i % len(accent_colors)])

    # ── Zona gráficos ─────────────────────────────────────────────────────────
    gy0 = my0 + kpi_h + 12
    gh  = H - gy0 - 18

    if has_right_panel:
        main_w = int(mw * 0.62)
        side_w = mw - main_w - 8
        card(img, mx0, gy0, mx0+main_w, gy0+gh, r=14, shadow=True,
             accent_color=BLUE_CORP)
        card(img, mx0+main_w+8, gy0, mx0+mw, gy0+gh, r=14, shadow=True,
             accent_color=BLUE_MED)
    else:
        card(img, mx0, gy0, mx0+mw, gy0+gh, r=14, shadow=True,
             accent_color=BLUE_CORP)

def layout_table_focus(img, has_top_kpi=True):
    """Página con tabla grande como protagonista."""
    mx0 = PANEL_W + 18
    mw  = W - mx0 - 18

    if has_top_kpi:
        my0 = HEADER_H + 14
        kpi_h = 72
        for i in range(3):
            kx = mx0 + i*((mw//3)-4)
            card(img, kx, my0, kx+(mw//3)-6, my0+kpi_h, r=12,
                 accent_color=[BLUE_CORP, GREEN_POS, RED_ALERT][i])
        table_y0 = my0 + kpi_h + 10
    else:
        table_y0 = HEADER_H + 14

    card(img, mx0, table_y0, mx0+mw, H-18, r=14, shadow=True,
         accent_color=BLUE_CORP)

    # Header de la tabla (simulado)
    alpha_rect(img, mx0, table_y0, mx0+mw, table_y0+34, BLUE_CORP, 255,
               radius=14)
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([mx0, table_y0+18, mx0+mw, table_y0+34],
                         radius=0, fill=(*BLUE_CORP,255))
    img.alpha_composite(L)

def layout_two_charts(img):
    """Dos gráficos principales lado a lado."""
    mx0 = PANEL_W + 18
    my0 = HEADER_H + 14
    mw  = W - mx0 - 18
    half = (mw - 8) // 2
    card(img, mx0,        my0, mx0+half,    H-18, r=14, shadow=True,
         accent_color=BLUE_CORP)
    card(img, mx0+half+8, my0, mx0+mw,      H-18, r=14, shadow=True,
         accent_color=GOLD)

def layout_audit(img):
    """Auditoría: 3 KPI + tabla grande."""
    mx0 = PANEL_W + 18
    my0 = HEADER_H + 14
    mw  = W - mx0 - 18

    kpi_h = 78
    for i in range(3):
        kx = mx0 + i*((mw//3)-4)
        card(img, kx, my0, kx+(mw//3)-6, my0+kpi_h, r=12,
             accent_color=[BLUE_CORP, BLUE_CORP, RED_ALERT][i])

    # Tabla grande
    card(img, mx0, my0+kpi_h+10, mx0+mw, H-18, r=14, shadow=True,
         accent_color=RED_ALERT)
    alpha_rect(img, mx0, my0+kpi_h+10, mx0+mw, my0+kpi_h+44,
               RED_ALERT, 200, radius=14)
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([mx0, my0+kpi_h+24, mx0+mw, my0+kpi_h+44],
                         radius=0, fill=(*RED_ALERT,200))
    img.alpha_composite(L)

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 0: ÍNDICE PREMIUM
# ══════════════════════════════════════════════════════════════════════════════
def page_indice():
    img = Image.new("RGBA", (W,H), (*NAVY,255))
    draw = ImageDraw.Draw(img)

    # Fondo: navy con gradiente sutil
    grad_v(draw, 0, 0, W, H, NAVY, lerp(NAVY, NAVY2, 0.7))

    # ── Forma diagonal divisora: 40% izquierda oscura, 60% clara ────────────
    # Triángulo de transición suave
    for i in range(200):
        t = i/200
        x = int(W*0.38 + i*0.6)
        alpha = int(255 * (1-t))
        draw.line([(x, 0),(x, H)], fill=(*CONTENT_BG, alpha//8), width=1)

    # Fondo derecho: claro
    draw.rectangle([int(W*0.40), 0, W, H], fill=(*CONTENT_BG, 255))

    # Textura sutil izquierda
    for offset in range(-H, W, 44):
        draw.line([(offset, 0),(offset+H, H)], fill=(*BLUE_MED,10), width=1)

    # Forma orgánica IHSA (semicírculo en zona de transición)
    L = Image.new("RGBA",(W,H),(0,0,0,0))
    dL = ImageDraw.Draw(L)
    cx_blob = int(W*0.41)
    dL.ellipse([cx_blob-220, H-260, cx_blob+220, H+180],
               fill=(*BLUE_CORP, 22))
    img.alpha_composite(L)

    # Línea divisora brillante
    div_x = int(W*0.40)
    glow(img, div_x, 0, div_x, H, BLUE_LT, thickness=2, spread=16)

    draw = ImageDraw.Draw(img)

    # ── ZONA IZQUIERDA: branding ─────────────────────────────────────────────
    # Eyebrow
    fnt_eye  = font(9)
    fnt_pre  = font(13, bold=False)
    fnt_big  = font(48, bold=True)
    fnt_big2 = font(26, bold=True)
    fnt_sub  = font(11)
    fnt_sm   = font(9)

    draw.text((48, 60), "GRUPO IHSA  ·  OPERACIONES COMPLEJAS",
              font=fnt_eye, fill=(*BLUE_LT, 160))
    glow(img, 48, 78, 340, 78, GOLD, thickness=1, spread=5)

    draw = ImageDraw.Draw(img)
    draw.text((48,  90), "Real vs",      font=fnt_big2, fill=(*WHITE, 180))
    draw.text((48, 124), "Presupuesto",  font=fnt_big,  fill=(*WHITE, 255))

    # Línea acento bajo título
    glow(img, 48, 228, 300, 228, BLUE_LT, thickness=2, spread=8)
    draw = ImageDraw.Draw(img)
    draw.text((48, 238), "Panel de control presupuestario",
              font=fnt_sub, fill=(*WHITE, 150))
    draw.text((48, 260), "Período 2025 – 2026", font=fnt_sm,
              fill=(*BLUE_LT, 120))

    # Logo grande en parte inferior izquierda
    ihsa_logo(img, 48, H-130, scale=1.7)

    # ── ZONA DERECHA: navegación ─────────────────────────────────────────────
    rx0 = div_x + 28

    draw = ImageDraw.Draw(img)
    draw.text((rx0, 20), "PANEL DE NAVEGACIÓN", font=font(12, bold=True),
              fill=(*TEXT_DARK, 220))
    draw.text((rx0, 42), "Seleccioná la sección que querés analizar",
              font=font(10), fill=(*TEXT_MED, 180))
    draw.line([(rx0, 62), (W-28, 62)], fill=(*DIVIDER,255), width=1)

    botones = [
        ("01", "Resumen Ejecutivo",   "KPIs globales · Real vs PA",          BLUE_CORP),
        ("02", "Análisis Comercial",  "Desvío por vertical de negocio",      BLUE_MED),
        ("03", "Vista Operativa",     "Detalle por cuenta y ceco",           BLUE_MED),
        ("04", "Detalle Proveedores", "Gasto real · Base SAP transaccional", BLUE_MED),
        ("05", "Entregable OPEX",     "Resumen operativo mensual",           lerp(BLUE_MED,GOLD,0.3)),
        ("06", "Auditoría Interna",   "Controles y validaciones de datos",   lerp(NAVY,RED_ALERT,0.4)),
    ]

    btn_cols = 2
    av_w = W - rx0 - 28
    btn_w = av_w // btn_cols - 8
    btn_h = (H - 82) // 3 - 10
    gap   = 8

    for i, (num, label, desc, accent) in enumerate(botones):
        col = i % btn_cols
        row = i // btn_cols
        bx = rx0 + col*(btn_w+gap)
        by = 72 + row*(btn_h+gap)

        drop_shadow(img, bx, by, bx+btn_w, by+btn_h, radius=12, offset=3, blur=10)
        alpha_rect(img, bx, by, bx+btn_w, by+btn_h, CARD_BG, 255, radius=12)

        # Borde
        Lb = Image.new("RGBA",img.size,(0,0,0,0))
        db = ImageDraw.Draw(Lb)
        db.rounded_rectangle([bx,by,bx+btn_w,by+btn_h], radius=12,
                              outline=(*CARD_BORDER,200), width=1)
        img.alpha_composite(Lb)

        # Acento lateral izquierdo
        alpha_rect(img, bx, by, bx+5, by+btn_h, accent, 255, radius=12)
        La = Image.new("RGBA",img.size,(0,0,0,0))
        da = ImageDraw.Draw(La)
        da.rounded_rectangle([bx+3,by,bx+5,by+btn_h], radius=0, fill=(*accent,255))
        img.alpha_composite(La)

        draw = ImageDraw.Draw(img)

        # Número grande (fondo, muy transparente)
        draw.text((bx+btn_w-44, by+btn_h//2-18), num,
                  font=font(36, bold=True), fill=(*accent, 18))

        # Texto
        draw.text((bx+16, by+16), label, font=font(11, bold=True),
                  fill=(*TEXT_DARK, 230))
        draw.text((bx+16, by+36), desc,  font=font(9),
                  fill=(*TEXT_MED, 180))

        # Flecha
        draw.text((bx+btn_w-24, by+btn_h//2-8), "›",
                  font=font(20), fill=(*accent, 180))

    path = f"{OUT}/fondo_00_indice.png"
    img.save(path, "PNG")
    print(f"  ✓  {path}")

# ══════════════════════════════════════════════════════════════════════════════
# GENERADOR GENÉRICO
# ══════════════════════════════════════════════════════════════════════════════
def make_page(slug, titulo, subtitulo, badge, layout_fn, page_name,
              dark_header=False):
    img = Image.new("RGBA", (W,H), (*CONTENT_BG, 255))
    build_panel(img, page_name)
    build_content_area(img, titulo, subtitulo, badge, dark_header)
    layout_fn(img)
    path = f"{OUT}/fondo_{slug}.png"
    img.save(path, "PNG")
    print(f"  ✓  {path}")

def generar_tema():
    import json
    t = {
        "name": "GrupoIHSA_Enterprise",
        "dataColors": ["#3267B8","#5294DA","#20488C","#D2AF3C",
                       "#20B29A","#7AADDF","#6878A8","#A8C8EE"],
        "background":  "#F7F9FD",
        "foreground":  "#3267B8",
        "tableAccent": "#3267B8",
        "visualStyles": {
            "*": {"*": {
                "fontFamily": [{"value":"Segoe UI"}],
                "fontSize":   [{"value": 10}]
            }},
            "card": {"*": {
                "background": [{"color":{"solid":{"color":"#FFFFFF"}}}],
                "border":     [{"show":True,"color":{"solid":{"color":"#3267B8"}},
                                "radius":12}],
                "calloutValue":[{"fontSize":22,"fontBold":True,
                                 "color":{"solid":{"color":"#19284A"}}}],
                "label":       [{"fontSize":9,
                                 "color":{"solid":{"color":"#5A73A0"}}}]
            }},
            "slicer": {"*": {
                "background": [{"color":{"solid":{"color":"#0D1A46"}}}],
                "border":     [{"show":False}],
                "header":     [{"fontColor":{"solid":{"color":"#FFFFFF"}},
                                "background":{"solid":{"color":"#12246E"}}}],
                "items":      [{"fontColor":{"solid":{"color":"#C8D8F0"}}}]
            }},
            "tableEx": {"*": {
                "header":    [{"fontColor":{"solid":{"color":"#FFFFFF"}},
                               "background":{"solid":{"color":"#3267B8"}}}],
                "values":    [{"fontColor":{"solid":{"color":"#19284A"}}}],
                "grid":      [{"gridVertical":False,"rowPadding":5}],
                "rowHeaders":[{"fontColor":{"solid":{"color":"#19284A"}}}]
            }},
            "matrix": {"*": {
                "header":   [{"fontColor":{"solid":{"color":"#FFFFFF"}},
                              "background":{"solid":{"color":"#3267B8"}}}],
                "values":   [{"fontColor":{"solid":{"color":"#19284A"}}}],
                "subTotals":[{"fontColor":{"solid":{"color":"#3267B8"}},
                              "background":{"solid":{"color":"#EEF3FB"}}}]
            }},
            "lineChart": {"*": {
                "lineWidth": [{"value":2}],
                "markerSize":[{"value":5}],
                "dataPoint": [{"defaultColor":{"solid":{"color":"#3267B8"}}}]
            }},
            "barChart": {"*": {
                "dataPoint":[{"defaultColor":{"solid":{"color":"#3267B8"}}}]
            }},
            "columnChart": {"*": {
                "dataPoint":[{"defaultColor":{"solid":{"color":"#3267B8"}}}]
            }}
        },
        "good":    "#20B29A",
        "neutral": "#5294DA",
        "bad":     "#C83232",
        "maximum": "#3267B8",
        "center":  "#7CC4E8",
        "minimum": "#20488C",
        "null":    "#D0DAF0"
    }
    path = f"{OUT}/tema_GrupoIHSA_Enterprise.json"
    with open(path,"w",encoding="utf-8") as f:
        json.dump(t, f, indent=2, ensure_ascii=False)
    print(f"  ✓  {path}")

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n── IHSA Premium v3 ─────────────────────────────────────")

    page_indice()

    make_page("01_resumen",
              "Resumen Ejecutivo",
              "Real vs Presupuesto  ·  Operaciones Complejas  ·  2025–2026",
              "GLOBAL", lambda img: layout_kpi_plus_charts(img, 4, True),
              "Resumen Ejecutivo")

    make_page("02_comercial",
              "Análisis Comercial",
              "Desvío presupuestario por vertical de negocio",
              "COMERCIAL", lambda img: layout_kpi_plus_charts(img, 3, True),
              "Comercial")

    make_page("03_operativa",
              "Vista Operativa",
              "Detalle por cuenta contable y centro de costos",
              "OPERATIVA", layout_table_focus,
              "Operativa")

    make_page("04_proveedores",
              "Detalle de Proveedores",
              "Gasto real por proveedor  ·  Base SAP transaccional",
              "PROVEEDORES", lambda img: layout_table_focus(img, has_top_kpi=True),
              "Proveedores")

    make_page("05_opex",
              "Entregable OPEX",
              "Clasificación operativa  ·  CAPEX / OPEX  ·  CO / GT",
              "OPEX", lambda img: layout_kpi_plus_charts(img, 3, False),
              "Entregable OPEX")

    make_page("06_auditoria",
              "Auditoría — Controles y Validaciones",
              "Conciliación entre fuentes  ·  Uso interno  ·  Equipo de datos",
              "AUDITORÍA", layout_audit,
              "Auditoría", dark_header=True)

    print("\n── Tema Power BI ────────────────────────────────────────")
    generar_tema()

    print("\n── Archivos generados ───────────────────────────────────")
    for f in sorted(os.listdir(OUT)):
        kb = os.path.getsize(f"{OUT}/{f}")//1024
        print(f"   {f:<48} {kb:>4} KB")
    print()
