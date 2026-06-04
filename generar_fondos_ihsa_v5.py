#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grupo IHSA — Dashboard Premium v5
Incorpora imagen real de la ambulancia IHSA en el panel lateral.
Remoción de fondo blanco + composición con fade gradients.
"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import math, os, sys

OUT  = "/home/user/General/assets_ihsa_v5"
IMG_AMBULANCIA = "/home/user/General/ambulancia_ihsa.png"
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720

# ── Paleta IHSA exacta ────────────────────────────────────────────────────────
BLUE        = ( 50, 103, 184)
BLUE_DARK   = ( 23,  55, 115)
BLUE_LIGHT  = ( 82, 148, 218)
BLUE_PALE   = (200, 220, 245)
NAVY        = ( 13,  24,  64)
NAVY2       = ( 18,  33,  82)
WHITE       = (255, 255, 255)
CONTENT_BG  = (246, 249, 254)
CARD        = (255, 255, 255)
CARD_BORDER = (218, 230, 248)
TEXT_H      = ( 18,  32,  72)
TEXT_B      = ( 60,  85, 135)
TEXT_S      = (140, 165, 200)
GOLD        = (200, 160,  40)
ORANGE      = (230, 100,  30)
GREEN       = ( 25, 155, 110)
RED         = (200,  45,  50)

PW = 258
HH = 66


# ── Helpers ───────────────────────────────────────────────────────────────────
def font(sz, bold=False):
    for p in [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
         else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
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

def rounded_rect_layer(img, x0,y0,x1,y1, r, color, alpha, outline=None):
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([x0,y0,x1,y1], radius=r, fill=(*color,alpha))
    if outline:
        d.rounded_rectangle([x0,y0,x1,y1], radius=r,
                             outline=(*outline[0],outline[1]), width=1)
    img.alpha_composite(L)

def alpha_shape(img, pts, color, alpha):
    L = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(L).polygon(pts, fill=(*color,alpha))
    img.alpha_composite(L)


# ── Remoción de fondo blanco de la ambulancia ─────────────────────────────────
def remove_white_bg(src_path, threshold=240, feather=18):
    """
    Carga la imagen, convierte fondo blanco a transparente con borde suave.
    threshold: píxeles con R,G,B > threshold se eliminan.
    feather: suavizado del borde en píxeles.
    """
    src = Image.open(src_path).convert("RGBA")
    data = src.load()
    w, h = src.size

    # Paso 1: crear máscara — blanco → transparente
    mask = Image.new("L", (w, h), 0)
    mask_data = mask.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = data[x, y]
            # Umbral: si los 3 canales son altos y la saturación es baja → fondo
            mn = min(r, g, b)
            brightness = (r + g + b) / 3
            if brightness > threshold and mn > threshold - 15:
                mask_data[x, y] = 0   # transparente
            else:
                mask_data[x, y] = 255 # opaco

    # Paso 2: dilatar ligeramente para evitar halos blancos en los bordes
    mask = mask.filter(ImageFilter.MinFilter(3))
    # Paso 3: suavizar el borde
    mask = mask.filter(ImageFilter.GaussianBlur(feather // 3))

    result = src.copy()
    result.putalpha(mask)
    return result


# ── Componer ambulancia en zona del panel ─────────────────────────────────────
def composite_ambulancia(img, x0, y0, x1, y1, src_path, flip=False):
    """
    Carga la ambulancia, remueve fondo blanco, redimensiona para llenar la zona
    manteniendo proporción, y la compone sobre img con fade top/bottom.
    """
    amb = remove_white_bg(src_path)

    if flip:
        amb = amb.transpose(Image.FLIP_LEFT_RIGHT)

    # Fit dentro de la zona preservando aspect ratio
    zone_w = x1 - x0
    zone_h = y1 - y0
    amb_w, amb_h = amb.size
    scale = min(zone_w / amb_w, zone_h / amb_h) * 0.96
    new_w = int(amb_w * scale)
    new_h = int(amb_h * scale)
    amb = amb.resize((new_w, new_h), Image.LANCZOS)

    # Centrar en zona
    paste_x = x0 + (zone_w - new_w) // 2
    paste_y = y0 + (zone_h - new_h) // 2

    # Aplicar fade top (20px) y bottom (35px) sobre el alpha de la imagen
    amb_data = amb.load()
    fade_top = 22
    fade_bot = 40
    for py in range(new_h):
        # Fade superior
        if py < fade_top:
            factor = py / fade_top
        # Fade inferior
        elif py > new_h - fade_bot:
            factor = (new_h - py) / fade_bot
        else:
            factor = 1.0
        if factor < 1.0:
            for px in range(new_w):
                r, g, b, a = amb_data[px, py]
                amb_data[px, py] = (r, g, b, int(a * factor))

    # Fade lateral izquierdo y derecho (10px cada lado)
    fade_side = 12
    for px in range(new_w):
        if px < fade_side:
            fx = px / fade_side
        elif px > new_w - fade_side:
            fx = (new_w - px) / fade_side
        else:
            fx = 1.0
        if fx < 1.0:
            for py in range(new_h):
                r, g, b, a = amb_data[px, py]
                amb_data[px, py] = (r, g, b, int(a * fx))

    img.alpha_composite(amb, (paste_x, paste_y))


# ── Logo IHSA premium ─────────────────────────────────────────────────────────
def logo(img, x, y, scale=1.0, on_dark=True):
    d = ImageDraw.Draw(img)
    fg  = WHITE if on_dark else BLUE
    fg2 = BLUE_LIGHT if on_dark else BLUE
    fnt_g = font(int(8 * scale))
    fnt_i = font(int(28 * scale), bold=True)
    d.rectangle([x, y+2, x+3, y+int(38*scale)], fill=(*fg2, 255))
    d.text((x+9,  y),               "GRUPO", font=fnt_g, fill=(*fg, 170))
    d.text((x+8,  y+int(10*scale)), "IHSA",  font=fnt_i, fill=(*fg, 255))


# ── Slicer slot premium ───────────────────────────────────────────────────────
def slicer(img, draw, x0, y, label, width):
    draw.text((x0, y), label.upper(), font=font(7), fill=(*TEXT_S, 180))
    y1, y2 = y+12, y+34
    rounded_rect_layer(img, x0, y1, x0+width, y2, 6, NAVY2, 190)
    rounded_rect_layer(img, x0, y1, x0+width, y2, 6, BLUE_LIGHT, 0,
                       outline=(BLUE_LIGHT, 55))
    d = ImageDraw.Draw(img)
    d.text((x0+10, y1+6), "Todos",    font=font(9),  fill=(*TEXT_S, 110))
    d.text((x0+width-18, y1+5), "▾", font=font(10), fill=(*BLUE_LIGHT, 140))


# ══════════════════════════════════════════════════════════════════════════════
# PANEL LATERAL
# ══════════════════════════════════════════════════════════════════════════════
def build_panel(img, page_label="", amb_path=None):
    draw = ImageDraw.Draw(img)

    # Gradiente navy profundo
    grad_v(draw, 0, 0, PW, H, NAVY, lerp(NAVY2, NAVY, 0.4))

    # Textura diagonal sutil
    for off in range(-H, W, 52):
        draw.line([(off, 0),(off+H, H)], fill=(*BLUE_DARK, 12), width=1)

    # Shape orgánico IHSA (blob semicircular esquina inferior)
    blob_cx = PW + 15
    blob_cy = H - 10
    for r, alpha in [(200,22),(155,18),(110,14),(72,10)]:
        L = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(L).ellipse(
            [blob_cx-r, blob_cy-r, blob_cx+r, blob_cy+r],
            fill=(*BLUE, alpha))
        img.alpha_composite(L)

    # ── ZONA DE IMAGEN VEHICULAR ──────────────────────────────────────────────
    img_zone_y0 = 350
    img_zone_y1 = H - 70
    img_zone_x0 = 4
    img_zone_x1 = PW - 4

    # Fondo de zona (siempre, da contexto si no hay imagen)
    rounded_rect_layer(img, img_zone_x0, img_zone_y0,
                       img_zone_x1, img_zone_y1, 14, BLUE_DARK, 60)

    if amb_path and os.path.exists(amb_path):
        # Componer imagen real con remoción de fondo blanco
        composite_ambulancia(img,
                             img_zone_x0 + 2, img_zone_y0 + 2,
                             img_zone_x1 - 2, img_zone_y1 - 2,
                             amb_path, flip=False)
        # Overlay de gradiente para integrar con el panel (abajo → navy)
        for i in range(50):
            a = int(160 * (i/50)**2)
            draw2 = ImageDraw.Draw(img)
            draw2.rectangle([img_zone_x0, img_zone_y1-50+i,
                              img_zone_x1, img_zone_y1-49+i],
                             fill=(*NAVY, a))
        # Borde sutil azul
        rounded_rect_layer(img, img_zone_x0, img_zone_y0,
                           img_zone_x1, img_zone_y1, 14, BLUE_LIGHT, 0,
                           outline=(BLUE_LIGHT, 50))
    else:
        # Placeholder si no hay imagen
        rounded_rect_layer(img, img_zone_x0, img_zone_y0,
                           img_zone_x1, img_zone_y1, 14, BLUE_LIGHT, 0,
                           outline=(BLUE_LIGHT, 35))
        draw = ImageDraw.Draw(img)
        cx = (img_zone_x0 + img_zone_x1) // 2
        cy = (img_zone_y0 + img_zone_y1) // 2
        draw.text((cx-55, cy-8), "[ ambulancia_ihsa.png ]",
                  font=font(8, bold=True), fill=(*BLUE_LIGHT, 70))

    # Separador lateral luminoso
    glow_line(img, PW, 0, PW, H, BLUE, w=1, spread=14)

    # Logo
    logo(img, 20, 18, scale=1.1)

    draw = ImageDraw.Draw(img)
    draw.line([(16, 72), (PW-16, 72)], fill=(*BLUE_LIGHT, 40), width=1)

    # Sección activa
    if page_label:
        draw.text((16, 80), "SECCIÓN", font=font(7), fill=(*TEXT_S, 130))
        draw.text((16, 92), page_label, font=font(10, bold=True),
                  fill=(*WHITE, 200))
        draw.line([(16,110),(PW-16,110)], fill=(*BLUE_DARK, 80), width=1)

    # Segmentadores
    sw = PW - 32
    slicers_list = ["Período (MesAño)", "Vertical", "Cuenta", "Ceco"]
    sy = 120 if page_label else 88
    draw = ImageDraw.Draw(img)
    for lbl in slicers_list:
        slicer(img, draw, 16, sy, lbl, sw)
        sy += 58

    # Pie del panel
    draw = ImageDraw.Draw(img)
    draw.text((16, H-22), "Operaciones Complejas · 2025–2026",
              font=font(7), fill=(*TEXT_S, 80))


# ══════════════════════════════════════════════════════════════════════════════
# ÁREA DE CONTENIDO
# ══════════════════════════════════════════════════════════════════════════════
def build_content(img, titulo, subtitulo, badge=None, dark_hdr=False):
    draw = ImageDraw.Draw(img)

    draw.rectangle([PW+1, 0, W, H], fill=(*CONTENT_BG, 255))

    hdr_color = NAVY if dark_hdr else WHITE
    draw.rectangle([PW+1, 0, W, HH], fill=(*hdr_color, 255))

    if dark_hdr:
        glow_line(img, PW+1, HH, W, HH, BLUE, w=1, spread=8)
    else:
        draw = ImageDraw.Draw(img)
        draw.line([(PW+20, HH),(W-20, HH)], fill=(*CARD_BORDER, 255), width=1)
        glow_line(img, PW+20, HH, PW+160, HH, GOLD, w=2, spread=7)

    tc = WHITE if dark_hdr else TEXT_H
    sc = TEXT_S if dark_hdr else TEXT_B
    draw = ImageDraw.Draw(img)
    draw.text((PW+22, 11), titulo,    font=font(18, bold=True), fill=(*tc, 255))
    draw.text((PW+22, 38), subtitulo, font=font(10),            fill=(*sc, 200))

    if badge:
        bw = len(badge)*7 + 22
        rounded_rect_layer(img, W-bw-105, 15, W-105, 47, 5, BLUE, 210)
        ImageDraw.Draw(img).text((W-bw-97, 23), badge.upper(),
                                  font=font(8, bold=True), fill=(*WHITE, 240))

    logo(img, W-95, 8, scale=0.70, on_dark=dark_hdr)


# ══════════════════════════════════════════════════════════════════════════════
# LAYOUTS
# ══════════════════════════════════════════════════════════════════════════════
def layout_resumen(img):
    mx0, mw = PW+18, W-PW-36
    kw = mw//4 - 5
    accents = [BLUE, GREEN, RED, GOLD]
    for i in range(4):
        card(img, mx0+i*(kw+6), HH+14, mx0+i*(kw+6)+kw, HH+92,
             r=12, accent=accents[i])
    card(img, mx0, HH+106, mx0+int(mw*0.60), H-18, r=14, accent=BLUE)
    card(img, mx0+int(mw*0.60)+8, HH+106, mx0+mw, H-18, r=14, accent=BLUE_LIGHT)

def layout_table(img, kpis=3):
    mx0, mw = PW+18, W-PW-36
    kw = mw//kpis - 5
    accents = [BLUE, GREEN, RED, GOLD]
    for i in range(kpis):
        card(img, mx0+i*(kw+6), HH+14, mx0+i*(kw+6)+kw, HH+82,
             r=12, accent=accents[i])
    ty0 = HH+98
    card(img, mx0, ty0, mx0+mw, H-18, r=14, accent=BLUE)
    rounded_rect_layer(img, mx0, ty0, mx0+mw, ty0+5, 14, BLUE, 255)
    L = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(L).rounded_rectangle([mx0, ty0+3, mx0+mw, ty0+36],
                                         radius=0, fill=(*BLUE, 255))
    img.alpha_composite(L)
    cols = ["Vertical","Cuenta","Denominación","Ceco","Real Mes","PA Mes","Variación","Var%"]
    col_w = mw // len(cols)
    d = ImageDraw.Draw(img)
    for i, col in enumerate(cols):
        d.text((mx0+6+i*col_w, ty0+12), col, font=font(8, bold=True),
               fill=(*WHITE, 220))
    for r in range(7):
        alpha = 15 if r%2==0 else 0
        L2 = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(L2).rectangle(
            [mx0, ty0+36+r*26, mx0+mw, ty0+36+(r+1)*26],
            fill=(*BLUE_PALE, alpha))
        img.alpha_composite(L2)

def layout_comercial(img):
    mx0, mw = PW+18, W-PW-36
    kw = mw//3 - 5
    for i, acc in enumerate([BLUE, GREEN, RED]):
        card(img, mx0+i*(kw+6), HH+14, mx0+i*(kw+6)+kw, HH+82, r=12, accent=acc)
    card(img, mx0, HH+98, mx0+int(mw*0.65), H-18, r=14, accent=BLUE)
    card(img, mx0+int(mw*0.65)+8, HH+98, mx0+mw, H-18, r=14, accent=GOLD)

def layout_auditoria(img):
    mx0, mw = PW+18, W-PW-36
    kw = mw//3 - 5
    for i, acc in enumerate([BLUE, BLUE, RED]):
        card(img, mx0+i*(kw+6), HH+14, mx0+i*(kw+6)+kw, HH+82, r=12, accent=acc)
    ty0 = HH+98
    card(img, mx0, ty0, mx0+mw, H-18, r=14, accent=RED)
    rounded_rect_layer(img, mx0, ty0, mx0+mw, ty0+5, 14, RED, 255)
    L = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(L).rounded_rectangle([mx0, ty0+3, mx0+mw, ty0+36],
                                         radius=0, fill=(*RED, 255))
    img.alpha_composite(L)
    cols = ["Vertical","Cuenta","Ceco","Fecha","Monto PA","Monto Base","Diferencia","Motivo"]
    col_w = mw // len(cols)
    d = ImageDraw.Draw(img)
    for i, col in enumerate(cols):
        d.text((mx0+5+i*col_w, ty0+11), col, font=font(7, bold=True), fill=(*WHITE, 220))


# ══════════════════════════════════════════════════════════════════════════════
# ÍNDICE / PORTADA
# ══════════════════════════════════════════════════════════════════════════════
def page_indice(amb_path=None):
    img = Image.new("RGBA", (W, H), (*NAVY, 255))
    draw = ImageDraw.Draw(img)

    lw = int(W * 0.44)
    grad_v(draw, 0, 0, lw, H, NAVY, lerp(NAVY2, NAVY, 0.5))

    # Textura diagonal
    for off in range(-H, W, 50):
        draw.line([(off, 0),(off+H, H)], fill=(*BLUE_DARK, 10), width=1)

    # Shape orgánico blob
    cx_blob, cy_blob = lw+10, H+20
    for r, alpha in [(240,20),(185,16),(130,13),(85,10),(50,8)]:
        L = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(L).ellipse([cx_blob-r, cy_blob-r, cx_blob+r, cy_blob+r],
                                   fill=(*BLUE, alpha))
        img.alpha_composite(L)

    glow_line(img, lw, 0, lw, H, BLUE_LIGHT, w=2, spread=18)
    draw = ImageDraw.Draw(img)

    # Textos izquierda
    draw.text((48, 58), "GRUPO IHSA  ·  OPERACIONES COMPLEJAS",
              font=font(9), fill=(*BLUE_LIGHT, 150))
    glow_line(img, 48, 76, 340, 76, GOLD, w=1, spread=5)
    draw = ImageDraw.Draw(img)
    draw.text((48,  88), "Real vs",     font=font(22, bold=True), fill=(*WHITE, 170))
    draw.text((48, 120), "Presupuesto", font=font(44, bold=True), fill=(*WHITE, 255))
    glow_line(img, 48, 222, 310, 222, BLUE_LIGHT, w=1, spread=8)
    draw = ImageDraw.Draw(img)
    draw.text((48, 232), "Panel de control presupuestario",
              font=font(11), fill=(*WHITE, 140))
    draw.text((48, 252), "Período 2025 – 2026  ·  Operaciones Complejas",
              font=font(9), fill=(*BLUE_LIGHT, 110))

    # ZONA IMAGEN VEHICULAR en portada
    img_y0, img_y1 = 275, H - 48
    img_x0, img_x1 = 22, lw - 18

    rounded_rect_layer(img, img_x0, img_y0, img_x1, img_y1, 18, BLUE_DARK, 60)

    if amb_path and os.path.exists(amb_path):
        composite_ambulancia(img,
                             img_x0 + 4, img_y0 + 4,
                             img_x1 - 4, img_y1 - 4,
                             amb_path, flip=False)
        # Fade inferior para integrar con pie de página
        for i in range(55):
            a = int(180 * (i/55)**1.8)
            ImageDraw.Draw(img).rectangle(
                [img_x0, img_y1-55+i, img_x1, img_y1-54+i],
                fill=(*NAVY, a))
        rounded_rect_layer(img, img_x0, img_y0, img_x1, img_y1, 18, BLUE_LIGHT, 0,
                           outline=(BLUE_LIGHT, 55))
    else:
        rounded_rect_layer(img, img_x0, img_y0, img_x1, img_y1, 18, BLUE_LIGHT, 0,
                           outline=(BLUE_LIGHT, 40))
        draw = ImageDraw.Draw(img)
        cx = (img_x0 + img_x1) // 2
        cy = (img_y0 + img_y1) // 2
        draw.text((cx-60, cy-8), "[ ambulancia_ihsa.png ]",
                  font=font(9, bold=True), fill=(*BLUE_LIGHT, 70))

    logo(img, 48, H-42, scale=0.85)

    # Lado derecho: navegación
    rx0 = lw + 25
    rw  = W - rx0 - 25
    draw = ImageDraw.Draw(img)
    draw.text((rx0, 22), "PANEL DE NAVEGACIÓN",
              font=font(13, bold=True), fill=(*TEXT_H, 220))
    draw.text((rx0, 44), "Seleccioná la sección que querés analizar",
              font=font(10), fill=(*TEXT_B, 180))
    draw.line([(rx0, 66),(W-28, 66)], fill=(*CARD_BORDER, 200), width=1)
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

    for i, (num, lbl, desc, acc) in enumerate(botones):
        col, row = i%2, i//2
        bx = rx0 + col*(bw+10)
        by = 74 + row*(bh+8)

        shadow(img, bx, by, bx+bw, by+bh, r=12, offset=3, blur=10)

        L = Image.new("RGBA", img.size, (0,0,0,0))
        d = ImageDraw.Draw(L)
        d.rounded_rectangle([bx,by,bx+bw,by+bh], radius=12, fill=(*WHITE,255))
        d.rounded_rectangle([bx,by,bx+bw,by+bh], radius=12,
                             outline=(*CARD_BORDER,150), width=1)
        img.alpha_composite(L)

        La = Image.new("RGBA", img.size, (0,0,0,0))
        da = ImageDraw.Draw(La)
        da.rounded_rectangle([bx,by,bx+6,by+bh], radius=12, fill=(*acc,255))
        da.rounded_rectangle([bx+4,by,bx+6,by+bh], radius=0, fill=(*acc,255))
        img.alpha_composite(La)

        draw = ImageDraw.Draw(img)
        draw.text((bx+bw-42, by+bh//2-18), num, font=font(32,bold=True),
                  fill=(*acc, 14))
        draw.text((bx+14, by+14), lbl,  font=font(11, bold=True), fill=(*TEXT_H,230))
        draw.text((bx+14, by+34), desc, font=font(9),             fill=(*TEXT_B,170))
        draw.text((bx+bw-22, by+bh//2-9), "›", font=font(20), fill=(*acc, 160))

    path = f"{OUT}/fondo_00_indice.png"
    img.save(path, "PNG")
    print(f"  ✓  {path}")


# ── Generador genérico ────────────────────────────────────────────────────────
def make(slug, titulo, subtitulo, badge, layout_fn, page_lbl,
         dark=False, amb_path=None):
    img = Image.new("RGBA", (W, H), (*CONTENT_BG, 255))
    build_panel(img, page_lbl, amb_path=amb_path)
    build_content(img, titulo, subtitulo, badge, dark)
    layout_fn(img)
    p = f"{OUT}/fondo_{slug}.png"
    img.save(p, "PNG")
    print(f"  ✓  {p}")


# ── Tema JSON ─────────────────────────────────────────────────────────────────
def tema_json():
    import json
    t = {
        "name": "GrupoIHSA_v5",
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
    p = f"{OUT}/tema_GrupoIHSA_v5.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(t, f, indent=2, ensure_ascii=False)
    print(f"  ✓  {p}")


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Detectar imagen de ambulancia
    amb = IMG_AMBULANCIA if os.path.exists(IMG_AMBULANCIA) else None
    if amb:
        print(f"\n  ✦  Ambulancia encontrada: {amb}")
    else:
        print(f"\n  ⚠  Ambulancia no encontrada en {IMG_AMBULANCIA}")
        print(     "     Guardá la imagen como 'ambulancia_ihsa.png' y re-ejecutá.")
        print(     "     Generando con placeholder...\n")

    print("\n── IHSA Premium v5 ─────────────────────────────────────")
    page_indice(amb_path=amb)
    make("01_resumen",    "Resumen Ejecutivo",
         "Real vs Presupuesto  ·  Operaciones Complejas  ·  2025–2026",
         "GLOBAL",    layout_resumen,  "Resumen Ejecutivo", amb_path=amb)
    make("02_comercial",  "Análisis Comercial",
         "Desvío presupuestario por vertical de negocio",
         "COMERCIAL", layout_comercial,"Comercial",         amb_path=amb)
    make("03_operativa",  "Vista Operativa",
         "Detalle por cuenta contable y centro de costos",
         "OPERATIVA", lambda i: layout_table(i,3), "Operativa",  amb_path=amb)
    make("04_proveedores","Detalle de Proveedores",
         "Gasto real por proveedor  ·  Base SAP transaccional",
         "PROVEEDORES",lambda i: layout_table(i,3),"Proveedores",amb_path=amb)
    make("05_opex",       "Entregable OPEX",
         "Clasificación operativa  ·  CAPEX / OPEX  ·  CO / GT",
         "OPEX",      lambda i: layout_table(i,2),"Entregable OPEX",amb_path=amb)
    make("06_auditoria",  "Auditoría — Controles y Validaciones",
         "Conciliación entre fuentes  ·  Uso interno  ·  Equipo de datos",
         "AUDITORÍA", layout_auditoria,"Auditoría", dark=True, amb_path=amb)

    print("\n── Tema ─────────────────────────────────────────────────")
    tema_json()
    print("\n── Archivos ─────────────────────────────────────────────")
    for f in sorted(os.listdir(OUT)):
        print(f"   {f:<48} {os.path.getsize(f'{OUT}/{f}')//1024:>4} KB")
