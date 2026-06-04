#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grupo IHSA — Dashboard Power BI v9
Respeta el template corporativo exacto:
  • Fondo blanco
  • Panel lateral azul sólido #3267B8
  • Ambulancia chica y proporcional, colores exactos (flood-fill BFS)
  • Tipografía y layout idéntico a las slides PowerPoint compartidas
"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np
import math, os, json
from collections import deque

OUT = "/home/user/General/assets_ihsa_v9"
AMB = "/home/user/General/ambulancia_ihsa.png"
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720

# ── Paleta — template IHSA exacto ────────────────────────────────────────────
C_WHITE      = (255, 255, 255)
C_BG         = (248, 250, 253)   # blanco ligerísimamente cálido
C_BLUE_CORP  = ( 50, 103, 184)   # #3267B8 — azul panel
C_BLUE_DARK  = ( 32,  72, 140)   # sombra/borde panel
C_BLUE_LT    = ( 82, 148, 218)   # #5294DA — acentos
C_BLUE_PALE  = (210, 225, 245)   # líneas sutiles en área blanca
C_TEXT_DARK  = ( 20,  30,  60)   # texto principal
C_TEXT_MID   = ( 80, 100, 140)   # texto secundario
C_TEXT_LT    = (140, 165, 200)   # labels, hints
C_GOLD       = (210, 175,  80)   # acento dorado
C_RED        = (200,  50,  50)   # alerta

PANEL_W  = 245
HEADER_H = 64


# ═══════════════════════════════════════════════════════════════════════════════
# FLOOD-FILL BFS — recorte de fondo blanco sin tocar el cuerpo del vehículo
# ═══════════════════════════════════════════════════════════════════════════════
def flood_fill_bg(arr_rgb, seeds, tolerance=22):
    h, w = arr_rgb.shape[:2]
    visited = np.zeros((h, w), dtype=bool)
    queue   = deque()
    for sy, sx in seeds:
        if not visited[sy, sx]:
            visited[sy, sx] = True
            queue.append((sy, sx, arr_rgb[sy, sx].astype(np.int32)))
    while queue:
        y, x, ref = queue.popleft()
        for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
            ny, nx = y+dy, x+dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                pix  = arr_rgb[ny, nx].astype(np.int32)
                dist = np.sqrt(np.sum((pix - ref)**2))
                if dist < tolerance:
                    visited[ny, nx] = True
                    queue.append((ny, nx, pix))
    return visited


def remove_bg_floodfill(path, tolerance=20, feather=2.2):
    src = Image.open(path).convert("RGBA")
    arr = np.array(src)
    rgb = arr[:,:,:3]
    h, w = rgb.shape[:2]

    seeds = []
    for y in range(0, h, 4):
        seeds += [(y, 0), (y, w-1)]
    for x in range(0, w, 4):
        seeds += [(0, x), (h-1, x)]
    for cy in [0, h//4, h//2, 3*h//4, h-1]:
        for cx in [0, w//4, 3*w//4, w-1]:
            seeds.append((cy, cx))

    bg_mask   = flood_fill_bg(rgb, seeds, tolerance=tolerance)
    alpha     = np.where(bg_mask, 0, 255).astype(np.uint8)
    alpha_img = Image.fromarray(alpha, "L")
    if feather > 0:
        alpha_img = alpha_img.filter(ImageFilter.GaussianBlur(feather))
        a = np.array(alpha_img, dtype=np.float32)
        a = np.clip((a - 30) * 1.4, 0, 255)
        alpha_img = Image.fromarray(a.astype(np.uint8), "L")

    result = src.copy()
    result.putalpha(alpha_img)
    return result


_AMB_CACHE = {}

def get_ambulancia(target_h, for_blue_bg=True):
    """
    Recorta la ambulancia y la escala a target_h.
    for_blue_bg=True: se va a pegar sobre fondo azul, no necesita glow.
    """
    key = (target_h, for_blue_bg)
    if key in _AMB_CACHE:
        return _AMB_CACHE[key]
    if not os.path.exists(AMB):
        _AMB_CACHE[key] = None
        return None

    veh = remove_bg_floodfill(AMB, tolerance=20, feather=2.2)

    # Crop al bbox
    alpha_arr = np.array(veh)[:,:,3]
    ys, xs = np.where(alpha_arr > 15)
    pad = 10
    x0 = max(0, int(xs.min()) - pad)
    y0 = max(0, int(ys.min()) - pad)
    x1 = min(veh.width,  int(xs.max()) + pad)
    y1 = min(veh.height, int(ys.max()) + pad)
    veh = veh.crop((x0, y0, x1, y1))

    # Escalar proporcionalmente por altura
    vw, vh = veh.size
    scale  = target_h / vh
    new_w  = int(vw * scale)
    new_h  = int(vh * scale)
    veh    = veh.resize((new_w, new_h), Image.LANCZOS)

    # Sombra de suelo discreta
    sh = Image.new("RGBA", (new_w, new_h + 18), (0,0,0,0))
    for i in range(12):
        a  = int(80 * (1 - i/12)**2)
        sx = int(new_w*0.1) + i*3
        ex = int(new_w*0.9) - i*3
        sy = new_h + 4 + i
        if ex > sx:
            ImageDraw.Draw(sh).ellipse([sx, sy-3, ex, sy+3], fill=(0,0,0,a))
    sh  = sh.filter(ImageFilter.GaussianBlur(5))
    base = Image.new("RGBA", (new_w, new_h + 18), (0,0,0,0))
    base.alpha_composite(sh)
    base.alpha_composite(veh, (0, 0))
    veh = base
    new_h = veh.height

    # Fades de integración suaves (sin aplastar los colores)
    arr = np.array(veh, dtype=np.float32)
    rows, cols = arr.shape[:2]

    # Superior: fade moderado
    ft = min(40, rows//5)
    arr[:ft, :, 3] *= np.linspace(0, 1, ft)[:, np.newaxis] ** 2.0
    # Inferior: muy suave
    fb = min(18, rows//8)
    arr[-fb:, :, 3] *= np.linspace(1, 0.3, fb)[:, np.newaxis]
    # Izquierdo: suave
    fl = min(20, cols//10)
    arr[:, :fl, 3] *= np.linspace(0, 1, fl)[np.newaxis, :] ** 1.5

    arr[:,:,3] = np.clip(arr[:,:,3], 0, 255)
    veh = Image.fromarray(arr.astype(np.uint8), "RGBA")

    _AMB_CACHE[key] = veh
    return veh


def composite_amb_panel(img, zone_y0, zone_y1, pw=PANEL_W):
    """
    Pega la ambulancia centrada horizontalmente en el panel azul.
    Tamaño proporcional: ocupa ~70% de la zona disponible en altura.
    """
    zone_h = zone_y1 - zone_y0
    target = int(zone_h * 0.72)          # 72% de la zona — más chica y proporcional
    veh    = get_ambulancia(target)
    if veh is None:
        return

    vw, vh = veh.size

    # Centrar horizontalmente en el panel
    paste_x = max(0, (pw - vw) // 2)
    # Alinear base de la sombra con el límite inferior de zona
    paste_y = zone_y1 - vh + 4

    # Si sube más arriba de zone_y0, recortar top
    if paste_y < zone_y0:
        crop_top = zone_y0 - paste_y
        veh = veh.crop((0, crop_top, vw, vh))
        paste_y = zone_y0
        vw, vh = veh.size

    img.alpha_composite(veh, (paste_x, paste_y))

    # Fade superior — funde con el panel azul sobre los slicers
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    ft = 50
    for i in range(ft):
        a = int(255 * (1 - i/ft)**2.5)
        d.rectangle([0, paste_y+i, pw, paste_y+i+1], fill=(*C_BLUE_CORP, a))
    img.alpha_composite(L)

    # Garantía: nada del vehículo sale del panel
    L2 = Image.new("RGBA", img.size, (0,0,0,0))
    d2 = ImageDraw.Draw(L2)
    d2.rectangle([pw, 0, W, H], fill=(*C_BG, 255))
    img.alpha_composite(L2)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def px(rgb, a=255): return (*rgb, a)

def get_font(size, bold=False):
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"    if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]:
        try: return ImageFont.truetype(p, size)
        except: pass
    return ImageFont.load_default()

def lerp(c1, c2, t):
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

def gradient_v(draw, x0,y0,x1,y1, c_top,c_bot, steps=80):
    seg = (y1-y0)/steps
    for i in range(steps):
        draw.rectangle([x0, y0+i*seg, x1, y0+(i+1)*seg+1],
                       fill=(*lerp(c_top,c_bot,i/steps),255))

def thin_line(img, x0,y0,x1,y1, color, w=1, alpha=255):
    ImageDraw.Draw(img).line([(x0,y0),(x1,y1)], fill=(*color,alpha), width=w)

def card_box(img, x0,y0,x1,y1, r=8, fill=(255,255,255), border=None, alpha=255):
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([x0,y0,x1,y1], radius=r, fill=(*fill,alpha))
    if border:
        d.rounded_rectangle([x0,y0,x1,y1], radius=r,
                             outline=(*border,180), width=1)
    img.alpha_composite(L)

def draw_logo_ihsa(img, x, y, scale=1.0, dark=False):
    """
    Logo "GRUPO / IHSA" estilo template: texto oscuro o blanco según fondo.
    dark=False → texto blanco (para panel azul)
    dark=True  → texto azul corporativo (para fondo blanco)
    """
    d = ImageDraw.Draw(img)
    txt_small = C_TEXT_LT if dark else (200, 215, 235)
    txt_big   = C_BLUE_CORP if dark else C_WHITE
    bar_color = C_GOLD

    bar_h = int(38*scale)
    d.rectangle([x, y+2, x+3, y+bar_h], fill=(*bar_color, 220))
    d.text((x+8, y),              "GRUPO", font=get_font(int(8*scale)),
           fill=(*txt_small, 200))
    d.text((x+8, y+int(10*scale)),"IHSA",  font=get_font(int(28*scale), bold=True),
           fill=(*txt_big, 255))

def slicer_row(img, x, y, w, label, hint, panel=True):
    """Un slicer en el panel azul."""
    d = ImageDraw.Draw(img)
    text_color = (220, 232, 248)
    hint_color = (180, 205, 235)

    d.text((x, y), label.upper(), font=get_font(7), fill=(*text_color, 170))

    # Caja del slicer: blanco semi-transparente sobre azul
    L = Image.new("RGBA", img.size, (0,0,0,0))
    dl = ImageDraw.Draw(L)
    dl.rounded_rectangle([x, y+12, x+w, y+36], radius=5,
                          fill=(255,255,255,35), outline=(255,255,255,60), width=1)
    img.alpha_composite(L)

    d2 = ImageDraw.Draw(img)
    d2.text((x+8, y+18), hint, font=get_font(9, bold=True), fill=(*hint_color, 180))
    # Chevron
    cx = x+w-16
    cy = y+24
    d2.polygon([(cx,cy-4),(cx+8,cy-4),(cx+4,cy+2)], fill=(*text_color,120))


# ═══════════════════════════════════════════════════════════════════════════════
# PANEL LATERAL AZUL — construcción base
# ═══════════════════════════════════════════════════════════════════════════════
def draw_panel(img):
    """Panel izquierdo azul sólido, ligerísimo degradado vertical."""
    draw = ImageDraw.Draw(img)
    gradient_v(draw, 0, 0, PANEL_W, H, C_BLUE_CORP, C_BLUE_DARK, steps=100)

    # Separador derecho: línea fina + sombra suave
    L = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(L).rectangle([PANEL_W, 0, PANEL_W+3, H],
                                  fill=(0,0,0,0))
    img.alpha_composite(L)
    thin_line(img, PANEL_W, 0, PANEL_W, H, C_BLUE_DARK, w=2, alpha=200)


# ═══════════════════════════════════════════════════════════════════════════════
# HEADER BLANCO
# ═══════════════════════════════════════════════════════════════════════════════
def draw_header(img, titulo, subtitulo, badge=None):
    d = ImageDraw.Draw(img)
    # Fondo blanco header
    d.rectangle([PANEL_W, 0, W, HEADER_H], fill=(*C_WHITE, 255))
    # Línea inferior azul
    thin_line(img, PANEL_W, HEADER_H, W, HEADER_H, C_BLUE_CORP, w=2, alpha=255)
    # Acento dorado corto
    thin_line(img, PANEL_W, HEADER_H, PANEL_W+280, HEADER_H, C_GOLD, w=2, alpha=200)

    d2 = ImageDraw.Draw(img)
    d2.text((PANEL_W+20, 10), titulo, font=get_font(17, bold=True),
            fill=(*C_TEXT_DARK, 255))
    d2.text((PANEL_W+20, 35), subtitulo, font=get_font(9),
            fill=(*C_TEXT_MID, 200))

    if badge:
        bw = max(70, len(badge)*7+16)
        card_box(img, W-bw-20, 14, W-20, 44, r=5,
                 fill=C_BLUE_CORP, border=C_BLUE_LT, alpha=220)
        ImageDraw.Draw(img).text((W-bw-13, 22), badge.upper(),
                                  font=get_font(8, bold=True),
                                  fill=(*C_WHITE, 230))

    # Logo top-right (sobre fondo blanco, versión oscura)
    draw_logo_ihsa(img, W-100, 8, scale=0.75, dark=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ÁREA CONTENIDO (fondo blanco con grilla sutil)
# ═══════════════════════════════════════════════════════════════════════════════
def draw_content_bg(img):
    d = ImageDraw.Draw(img)
    d.rectangle([PANEL_W, HEADER_H, W, H], fill=(*C_BG, 255))

    # Puntos muy sutiles
    for x in range(PANEL_W+30, W-20, 36):
        for y in range(HEADER_H+30, H-20, 36):
            d.ellipse([x-1, y-1, x+1, y+1], fill=(*C_BLUE_PALE, 160))

    # Línea footer
    thin_line(img, PANEL_W, H-28, W, H-28, C_BLUE_PALE, w=1, alpha=200)


# ═══════════════════════════════════════════════════════════════════════════════
# KPI CARDS + CHART AREAS (placeholders)
# ═══════════════════════════════════════════════════════════════════════════════
def draw_kpi_cards(img):
    kw = int((W - PANEL_W - 36) / 4) - 8
    kh = 72
    ky = HEADER_H + 16
    for i in range(4):
        kx = PANEL_W + 18 + i*(kw+8)
        card_box(img, kx, ky, kx+kw, ky+kh, r=8,
                 fill=C_WHITE, border=C_BLUE_PALE, alpha=255)
        # Barra de color en la parte superior de la card
        L = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(L).rounded_rectangle([kx, ky, kx+kw, ky+4],
                                             radius=8, fill=(*C_BLUE_CORP, 255))
        img.alpha_composite(L)

def draw_chart_areas(img):
    cy = HEADER_H + 106
    cw_l = int((W - PANEL_W - 28) * 0.60)
    cx0  = PANEL_W + 18

    card_box(img, cx0,       cy, cx0+cw_l,     H-38, r=10,
             fill=C_WHITE, border=C_BLUE_PALE, alpha=255)
    card_box(img, cx0+cw_l+8, cy, W-18, H-38, r=10,
             fill=C_WHITE, border=C_BLUE_PALE, alpha=255)

    # Puntos dentro
    d = ImageDraw.Draw(img)
    for x in range(cx0+20, cx0+cw_l-10, 38):
        for y in range(cy+20, H-50, 38):
            d.ellipse([x-1,y-1,x+1,y+1], fill=(*C_BLUE_PALE, 180))


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATE — PÁGINAS DE CONTENIDO
# ═══════════════════════════════════════════════════════════════════════════════
def template_content(slug, titulo, subtitulo, badge=None):
    img = Image.new("RGBA", (W, H), (*C_WHITE, 255))

    draw_panel(img)
    draw_content_bg(img)
    draw_header(img, titulo, subtitulo, badge)
    draw_kpi_cards(img)
    draw_chart_areas(img)

    # Slicers en panel azul
    slicers = [("Período","MesAño"), ("Vertical","Negocio"),
               ("Cuenta","Contable"), ("Ceco","Centro costos")]
    sy = 72
    for lbl, hint in slicers:
        slicer_row(img, 14, sy, PANEL_W-28, lbl, hint)
        sy += 60

    # Ambulancia — zona entre último slicer y logo (proporcional)
    amb_y0 = sy
    amb_y1 = H - 130
    composite_amb_panel(img, amb_y0, amb_y1)

    # Logo IHSA (blanco sobre azul, abajo del panel)
    draw_logo_ihsa(img, 20, H-118, scale=1.05, dark=False)

    img.save(f"{OUT}/fondo_{slug}.png", "PNG")
    print(f"  ✓  fondo_{slug}.png")


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATE — PORTADA / ÍNDICE
# ═══════════════════════════════════════════════════════════════════════════════
def template_indice():
    img = Image.new("RGBA", (W, H), (*C_WHITE, 255))
    d   = ImageDraw.Draw(img)

    # Panel izquierdo mayor en portada (~40% ancho)
    div_x = int(W * 0.40)  # 512px
    gradient_v(d, 0, 0, div_x, H, C_BLUE_CORP, C_BLUE_DARK, steps=120)

    # Detalle decorativo: arco/círculo recortado (como en el template slide 1)
    L = Image.new("RGBA", (W, H), (0,0,0,0))
    dl = ImageDraw.Draw(L)
    r_circle = 200
    dl.ellipse([div_x-r_circle-60, H-r_circle*2+40,
                div_x+r_circle-60, H+40],
               fill=(*C_WHITE, 255))
    img.alpha_composite(L)

    # Línea divisoria
    thin_line(img, div_x, 0, div_x, H, C_BLUE_DARK, w=2, alpha=220)

    # Texto portada (lado izquierdo — sobre azul)
    d2 = ImageDraw.Draw(img)
    d2.text((48, 52), "OPERACIONES COMPLEJAS · 2025–2026",
            font=get_font(10), fill=(*C_WHITE, 180))
    thin_line(img, 48, 72, 48+230, 72, C_GOLD, w=2, alpha=200)
    d3 = ImageDraw.Draw(img)
    d3.text((48,  84), "Real vs",     font=get_font(22, bold=True), fill=(*C_WHITE, 220))
    d3.text((48, 116), "Presupuesto", font=get_font(40, bold=True), fill=(*C_WHITE, 255))

    thin_line(img, 48, 210, 240, 210, (255,255,255), w=1, alpha=80)
    d3.text((48, 220), "Panel de control presupuestario",
            font=get_font(10), fill=(*C_WHITE, 160))
    d3.text((48, 238), "Grupo IHSA · Operaciones Complejas",
            font=get_font(10), fill=(210, 225, 248, 150))

    # Ambulancia en portada (izquierda, sobre el azul del panel)
    amb_target = 210
    veh = get_ambulancia(amb_target)
    if veh:
        vw, vh = veh.size
        paste_x = max(0, (div_x - vw) // 2)
        paste_y = H - vh - 95
        if paste_y < 270:
            crop_top = 270 - paste_y
            veh = veh.crop((0, crop_top, vw, vh))
            paste_y = 270
            vw, vh = veh.size

        img.alpha_composite(veh, (paste_x, paste_y))

        # Fade superior sobre la ambulancia
        Lf = Image.new("RGBA", img.size, (0,0,0,0))
        df = ImageDraw.Draw(Lf)
        for i in range(55):
            a = int(255*(1-i/55)**2.5)
            df.rectangle([0, paste_y+i, div_x, paste_y+i+1],
                         fill=(*C_BLUE_CORP, a))
        img.alpha_composite(Lf)

        # Garantía clip al panel
        Lc = Image.new("RGBA", img.size, (0,0,0,0))
        dc = ImageDraw.Draw(Lc)
        dc.rectangle([div_x, 0, W, H], fill=(*C_WHITE, 255))
        img.alpha_composite(Lc)

    # Logo IHSA (blanco) en la parte baja izquierda
    draw_logo_ihsa(img, 48, H-100, scale=1.1, dark=False)

    # Área derecha — fondo blanco
    d4 = ImageDraw.Draw(img)
    d4.rectangle([div_x, 0, W, H], fill=(*C_BG, 255))

    # Grilla sutil derecha
    for x in range(div_x+30, W-20, 36):
        for y in range(30, H-20, 36):
            d4.ellipse([x-1,y-1,x+1,y+1], fill=(*C_BLUE_PALE, 160))

    # Header área derecha
    thin_line(img, div_x, 64, W, 64, C_BLUE_CORP, w=2, alpha=255)
    thin_line(img, div_x, 64, div_x+300, 64, C_GOLD, w=2, alpha=180)
    d5 = ImageDraw.Draw(img)
    d5.text((div_x+24, 14), "SELECCIONÁ UNA SECCIÓN",
            font=get_font(13, bold=True), fill=(*C_TEXT_DARK, 240))
    d5.text((div_x+24, 38), "Panel de navegación rápida",
            font=get_font(9), fill=(*C_TEXT_MID, 200))

    # Logo top-right (versión oscura)
    draw_logo_ihsa(img, W-108, 8, scale=0.78, dark=True)

    # Tarjetas de navegación
    botones = [
        ("01", "Resumen Ejecutivo",    "KPIs globales · Real vs PA"),
        ("02", "Análisis Comercial",   "Desvío por vertical de negocio"),
        ("03", "Vista Operativa",      "Detalle cuenta y centro costos"),
        ("04", "Detalle Proveedores",  "Gasto real · Base SAP"),
        ("05", "Entregable OPEX",      "Resumen operativo mensual"),
        ("06", "Auditoría Interna",    "Controles y validaciones"),
    ]
    nav_x0 = div_x + 22
    nav_w  = (W - nav_x0 - 22) // 2 - 8
    nav_h  = (H - 90) // 3 - 14

    for i, (num, label, desc) in enumerate(botones):
        col = i % 2
        row = i // 2
        bx  = nav_x0 + col*(nav_w+8)
        by  = 80 + row*(nav_h+12)

        card_box(img, bx, by, bx+nav_w, by+nav_h, r=10,
                 fill=C_WHITE, border=C_BLUE_PALE, alpha=255)
        # Barra lateral azul
        L = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(L).rounded_rectangle([bx, by, bx+5, by+nav_h],
                                             radius=8, fill=(*C_BLUE_CORP, 255))
        img.alpha_composite(L)

        d6 = ImageDraw.Draw(img)
        d6.text((bx+nav_w-30, by+8), num,
                font=get_font(18, bold=True), fill=(*C_BLUE_PALE, 200))
        d6.text((bx+14, by+14), label,
                font=get_font(10, bold=True), fill=(*C_TEXT_DARK, 240))
        d6.text((bx+14, by+32), desc,
                font=get_font(8), fill=(*C_TEXT_MID, 180))
        d6.text((bx+nav_w-20, by+nav_h-22), "›",
                font=get_font(16), fill=(*C_BLUE_CORP, 200))

    img.save(f"{OUT}/fondo_00_indice.png", "PNG")
    print(f"  ✓  fondo_00_indice.png")


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATE — AUDITORÍA
# ═══════════════════════════════════════════════════════════════════════════════
def template_auditoria():
    img = Image.new("RGBA", (W, H), (*C_WHITE, 255))
    PW2 = 200

    # Panel izquierdo (más angosto para auditoría)
    d = ImageDraw.Draw(img)
    gradient_v(d, 0, 0, PW2, H, C_BLUE_CORP, (28, 50, 110), steps=100)
    thin_line(img, PW2, 0, PW2, H, C_BLUE_DARK, w=2, alpha=200)

    # Área contenido
    d.rectangle([PW2, 0, W, H], fill=(*C_BG, 255))
    for x in range(PW2+30, W-20, 36):
        for y in range(30, H-20, 36):
            d.ellipse([x-1,y-1,x+1,y+1], fill=(*C_BLUE_PALE, 160))

    # Header
    d.rectangle([PW2, 0, W, HEADER_H], fill=(*C_WHITE, 255))
    thin_line(img, PW2, HEADER_H, W, HEADER_H, C_RED, w=2, alpha=200)
    thin_line(img, PW2, HEADER_H, PW2+250, HEADER_H, C_GOLD, w=2, alpha=180)

    d2 = ImageDraw.Draw(img)
    d2.text((PW2+20, 10), "Auditoría — Controles y Validaciones",
            font=get_font(17, bold=True), fill=(*C_TEXT_DARK, 255))
    d2.text((PW2+20, 35), "Conciliación entre fuentes · Uso interno · Equipo de datos",
            font=get_font(9), fill=(*C_TEXT_MID, 200))

    # Badge alerta
    card_box(img, W-160, 14, W-20, 44, r=5, fill=(220, 50, 50), alpha=220)
    ImageDraw.Draw(img).text((W-153, 22), "⚠  USO INTERNO",
                              font=get_font(8, bold=True), fill=(*C_WHITE, 240))
    draw_logo_ihsa(img, W-108, 8, scale=0.78, dark=True)

    # Slicers
    slicers_aud = [("Período","MesAño"), ("Vertical","Negocio")]
    sy = 72
    for lbl, hint in slicers_aud:
        slicer_row(img, 12, sy, PW2-24, lbl, hint)
        sy += 60

    composite_amb_panel(img, sy, H-118, pw=PW2)
    draw_logo_ihsa(img, 16, H-108, scale=0.95, dark=False)

    # KPI cards (3)
    cy = HEADER_H + 14
    sw = int((W - PW2 - 24) / 3) - 6
    for i in range(3):
        sx = PW2+18 + i*(sw+8)
        card_box(img, sx, cy, sx+sw, cy+76, r=8, fill=C_WHITE, border=C_BLUE_PALE)
        L = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(L).rounded_rectangle([sx, cy, sx+sw, cy+4],
                                             radius=8, fill=(*C_RED, 255))
        img.alpha_composite(L)

    card_box(img, PW2+18, cy+92, W-18, H-36, r=10, fill=C_WHITE, border=C_BLUE_PALE)
    thin_line(img, PW2+18, cy+92, W-18, cy+92, C_RED, w=2, alpha=160)

    d3 = ImageDraw.Draw(img)
    thin_line(img, PW2, H-28, W, H-28, C_BLUE_PALE, w=1, alpha=200)

    img.save(f"{OUT}/fondo_06_auditoria.png", "PNG")
    print(f"  ✓  fondo_06_auditoria.png")


# ═══════════════════════════════════════════════════════════════════════════════
# TEMA JSON — actualizado para modo claro/corporativo
# ═══════════════════════════════════════════════════════════════════════════════
def generar_tema():
    tema = {
        "name": "GrupoIHSA",
        "dataColors": [
            "#3267B8",  # azul IHSA corporativo
            "#5294DA",  # azul IHSA claro
            "#7CC4E8",  # azul cielo
            "#20488C",  # azul oscuro
            "#D2AF50",  # dorado IHSA
            "#20B2AA",  # teal positivo
            "#DC4646",  # rojo alerta
            "#A8C8EE"   # azul pálido
        ],
        "background":  "#F8FAFD",
        "foreground":  "#141E3C",
        "tableAccent": "#3267B8",
        "visualStyles": {
            "*": {"*": {
                "fontFamily": [{"value": "Segoe UI"}],
                "fontSize":   [{"value": 10}],
                "background": [{"color": {"solid": {"color": "#FFFFFF"}}}]
            }},
            "card": {"*": {
                "background": [{"color": {"solid": {"color": "#FFFFFF"}}}],
                "border": [{"show": True,
                            "color": {"solid": {"color": "#D2E1F5"}},
                            "radius": 8}],
                "calloutValue": [{"fontSize": 22, "fontBold": True,
                                  "color": {"solid": {"color": "#141E3C"}}}],
                "label": [{"fontSize": 9,
                           "color": {"solid": {"color": "#5070A0"}}}]
            }},
            "slicer": {"*": {
                "background": [{"color": {"solid": {"color": "#F0F4FA"}}}],
                "border": [{"show": True,
                            "color": {"solid": {"color": "#D2E1F5"}}}],
                "header": [{"fontColor": {"solid": {"color": "#3267B8"}},
                            "background": {"solid": {"color": "#E8EFF9"}}}],
                "items": [{"fontColor": {"solid": {"color": "#141E3C"}}}]
            }},
            "tableEx": {"*": {
                "header": [{"fontColor": {"solid": {"color": "#FFFFFF"}},
                            "background": {"solid": {"color": "#3267B8"}}}],
                "rowHeaders": [{"fontColor": {"solid": {"color": "#141E3C"}}}],
                "values": [{"fontColor": {"solid": {"color": "#2A3A6A"}}}],
                "grid": [{"gridVertical": False, "rowPadding": 5,
                          "outlineColor": {"solid": {"color": "#D2E1F5"}}}]
            }},
            "matrix": {"*": {
                "header": [{"fontColor": {"solid": {"color": "#FFFFFF"}},
                            "background": {"solid": {"color": "#3267B8"}}}],
                "values": [{"fontColor": {"solid": {"color": "#141E3C"}}}],
                "subTotals": [{"fontColor": {"solid": {"color": "#3267B8"}},
                               "background": {"solid": {"color": "#EEF3FB"}}}]
            }},
            "lineChart": {"*": {
                "lineWidth":  [{"value": 2}],
                "markerSize": [{"value": 5}],
                "dataPoint":  [{"defaultColor": {"solid": {"color": "#3267B8"}}}]
            }},
            "barChart": {"*": {
                "dataPoint": [{"defaultColor": {"solid": {"color": "#3267B8"}}}]
            }},
            "columnChart": {"*": {
                "dataPoint": [{"defaultColor": {"solid": {"color": "#3267B8"}}}]
            }},
            "donutChart": {"*": {
                "dataPoint": [{"defaultColor": {"solid": {"color": "#5294DA"}}}]
            }}
        },
        "good":    "#20B2AA",
        "neutral": "#3267B8",
        "bad":     "#DC4646",
        "maximum": "#3267B8",
        "center":  "#7CC4E8",
        "minimum": "#20488C",
        "null":    "#D2E1F5"
    }
    p = f"{OUT}/tema_GrupoIHSA.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(tema, f, indent=2, ensure_ascii=False)
    print(f"  ✓  tema_GrupoIHSA.json")


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n  ✦  Ambulancia: {AMB}")
    print(f"  ✦  Template: blanco + panel azul #3267B8 (estilo PowerPoint IHSA)")
    print(f"  ✦  Ambulancia: proporcional, colores exactos, flood-fill BFS\n")
    print("── IHSA v9 ──────────────────────────────────────────────")

    template_indice()
    template_content("01_resumen",    "Resumen Ejecutivo",
                     "Real vs Presupuesto  ·  Operaciones Complejas  ·  2025–2026", "GLOBAL")
    template_content("02_comercial",  "Análisis Comercial",
                     "Desvío presupuestario por vertical de negocio", "COMERCIAL")
    template_content("03_operativa",  "Vista Operativa",
                     "Detalle por cuenta contable y centro de costos", "OPERATIVA")
    template_content("04_proveedores","Detalle de Proveedores",
                     "Gasto real por proveedor  ·  Base SAP transaccional", "PROVEEDORES")
    template_content("05_opex",       "Entregable OPEX",
                     "Resumen de gastos operativos  ·  Clasificación CAPEX/OPEX", "OPEX")
    template_auditoria()

    print("\n── Tema JSON ────────────────────────────────────────────")
    generar_tema()

    print("\n── Archivos generados ───────────────────────────────────")
    for f in sorted(os.listdir(OUT)):
        kb = os.path.getsize(f"{OUT}/{f}") // 1024
        print(f"   {f:<52} {kb:>4} KB")
