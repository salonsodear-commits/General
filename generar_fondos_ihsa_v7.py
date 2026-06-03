#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grupo IHSA — Dashboard Premium v7
Base: v2 (el favorito — full dark mode, glassmorphism, geometría premium)
Añade: ambulancia IHSA real con color grading corporativo adaptado al dark mode.
La ambulancia respeta los colores de la foto (naranja/rojo del checkerboard,
tracks oscuros, logo IHSA) integrándola con el fondo navy de v2.
"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np
import math, os

OUT = "/home/user/General/assets_ihsa_v7"
AMB = "/home/user/General/ambulancia_ihsa.png"
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720

# ── Paleta IHSA v2 exacta ─────────────────────────────────────────────────────
C_NAVY      = ( 10,  20,  50)
C_NAVY2     = ( 15,  30,  72)
C_BLUE_CORP = ( 50, 103, 184)   # #3267B8
C_BLUE_MID  = ( 35,  80, 155)
C_BLUE_LT   = ( 82, 148, 218)   # #5294DA
C_CYAN      = ( 90, 195, 230)
C_WHITE     = (255, 255, 255)
C_OFF_WHITE = (230, 238, 252)
C_SILVER    = (180, 195, 220)
C_GOLD      = (210, 175,  80)
C_TEAL      = ( 32, 178, 170)
C_RED_SOFT  = (220,  70,  70)
C_PANEL_BG  = ( 18,  28,  65)
C_CARD_BG   = ( 22,  38,  85)
C_CONTENT   = ( 14,  22,  52)

PANEL_W  = 245
HEADER_H = 62


# ═════════════════════════════════════════════════════════════════════════════
# TRATAMIENTO DE IMAGEN — ambulancia con color grading dark mode
# ═════════════════════════════════════════════════════════════════════════════
def prepare_ambulancia(target_h, extend_w=80):
    """
    Carga la ambulancia IHSA, crop al bbox, escala por altura para que el
    vehículo llene la zona del panel, y aplica color grading adaptado al
    dark mode de v2.
    - El fondo blanco se convierte en navy C_PANEL_BG (idéntico al panel).
    - El cuerpo blanco del vehículo adopta un tono azul oscuro brillante
      (distinguible del fondo, aún reconocible como vehículo).
    - Los detalles de color (checkerboard naranja/rojo, logo IHSA, tracks)
      retienen su saturación y se potencian para que destaquen.
    """
    if not os.path.exists(AMB):
        return None

    src = Image.open(AMB).convert("RGBA")
    arr = np.array(src, dtype=np.float32)

    # ── Crop bbox del vehículo (eliminar márgenes blancos sobrantes) ──────────
    R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    non_white = ~((R > 248) & (G > 248) & (B > 248))
    ys, xs = np.where(non_white)
    pad = 18
    x0 = max(0, int(xs.min()) - pad)
    y0 = max(0, int(ys.min()) - pad)
    x1 = min(src.width,  int(xs.max()) + pad)
    y1 = min(src.height, int(ys.max()) + pad)
    veh = src.crop((x0, y0, x1, y1))

    # ── Escalar por altura (preserva la proporción, llena la zona) ────────────
    vw, vh = veh.size
    scale  = (target_h * 1.08) / vh
    new_w  = int(vw * scale)
    new_h  = int(target_h * 1.08)
    veh = veh.resize((new_w, new_h), Image.LANCZOS)

    # ── COLOR GRADING para dark mode v2 ──────────────────────────────────────
    # Objetivo:
    #   fondo blanco puro          → C_PANEL_BG (navy, invisible contra el panel)
    #   cuerpo blanco del vehículo → azul oscuro brillante (visible, reconocible)
    #   detalles de color          → conservar y potenciar saturación
    #   partes oscuras (tracks)    → conservar, son dramáticas sobre navy
    arr2 = np.array(veh, dtype=np.float32)
    Rv = arr2[:,:,0] / 255.0
    Gv = arr2[:,:,1] / 255.0
    Bv = arr2[:,:,2] / 255.0

    # Luminosidad y saturación por píxel
    lum  = 0.2126*Rv + 0.7152*Gv + 0.0722*Bv
    cmax = np.maximum(np.maximum(Rv,Gv),Bv)
    cmin = np.minimum(np.minimum(Rv,Gv),Bv)
    sat  = np.where(cmax > 0.001, (cmax-cmin)/cmax, 0.0)

    # Color destino para las zonas blancas: navy del panel
    panel_r = C_PANEL_BG[0]/255.0
    panel_g = C_PANEL_BG[1]/255.0
    panel_b = C_PANEL_BG[2]/255.0

    # Color destino para el cuerpo blanco del vehículo: azul brillante oscuro
    # (como si estuviera iluminado con luz azul corporativa desde arriba)
    body_r = C_BLUE_MID[0]/255.0 * 0.55 + C_BLUE_LT[0]/255.0 * 0.20
    body_g = C_BLUE_MID[1]/255.0 * 0.55 + C_BLUE_LT[1]/255.0 * 0.20
    body_b = C_BLUE_MID[2]/255.0 * 0.55 + C_BLUE_LT[2]/255.0 * 0.20

    # Distinguir: fondo blanco puro (muy alta lum, sat≈0) vs cuerpo vehículo (alta lum, algo de sat/detalle)
    is_bg   = np.clip((lum - 0.93) * 14.0, 0, 1) * np.clip(1.0 - sat * 12.0, 0, 1)
    is_body = np.clip((lum - 0.55) * 2.2, 0, 1) * np.clip(1.0 - sat * 4.0, 0, 1) * (1.0 - is_bg)

    # Factor de mezcla con destino navy/body (alto lum+baja sat → mezclar más)
    blend = is_bg * 1.0 + is_body * 0.72

    # Target interpolado: fondo → panel navy; cuerpo → azul brillante
    tgt_r = panel_r * is_bg + body_r * is_body
    tgt_g = panel_g * is_bg + body_g * is_body
    tgt_b = panel_b * is_bg + body_b * is_body

    # Boost de los detalles de color (naranja, rojo, azul IHSA)
    # sat alto → conservar y potenciar color original
    detail = np.clip(sat * 2.0, 0, 1)
    # Los oscuros (tracks, sombras) también conservan su tono original
    dark   = np.clip((0.45 - lum) * 2.5, 0, 1)
    preserve = np.clip(detail + dark * 0.6, 0, 1)

    out_R = Rv * preserve + (Rv*(1-blend) + tgt_r*blend) * (1-preserve)
    out_G = Gv * preserve + (Gv*(1-blend) + tgt_g*blend) * (1-preserve)
    out_B = Bv * preserve + (Bv*(1-blend) + tgt_b*blend) * (1-preserve)

    # Gamma: oscurecer para atmósfera nocturna premium
    gamma = 0.65   # más oscuro — integra mejor con dark mode v2
    out_R = np.power(np.clip(out_R, 0.001, 1), 1.0/gamma)
    out_G = np.power(np.clip(out_G, 0.001, 1), 1.0/gamma)
    out_B = np.power(np.clip(out_B, 0.001, 1), 1.0/gamma)

    # Pequeño boost de saturación de los colores de acento (naranja del checkerboard)
    # para que sean vividos sobre el fondo oscuro
    sat_boost = np.clip(sat * 1.4, 0, 1)
    lum_out = 0.2126*out_R + 0.7152*out_G + 0.0722*out_B
    out_R = lum_out + (out_R - lum_out) * (1 + sat_boost * 0.5)
    out_G = lum_out + (out_G - lum_out) * (1 + sat_boost * 0.5)
    out_B = lum_out + (out_B - lum_out) * (1 + sat_boost * 0.5)

    arr2[:,:,0] = np.clip(out_R * 255, 0, 255)
    arr2[:,:,1] = np.clip(out_G * 255, 0, 255)
    arr2[:,:,2] = np.clip(out_B * 255, 0, 255)
    arr2[:,:,3] = 255.0  # completamente opaca (los fades se hacen con overlays)

    veh = Image.fromarray(arr2.astype(np.uint8), "RGBA")

    # ── Fades de borde con numpy (vectorizado = rápido) ───────────────────────
    arr3 = np.array(veh, dtype=np.float32)
    rows, cols = arr3.shape[:2]

    ft = min(75, rows//3)
    arr3[:ft, :, 3] *= np.array([(i/ft)**2.5 for i in range(ft)])[:, np.newaxis]

    fb = min(45, rows//5)
    arr3[-fb:, :, 3] *= np.array([((fb-i)/fb)**1.8 for i in range(fb)])[:, np.newaxis]

    fl = min(30, cols//7)
    arr3[:, :fl, 3] *= np.array([(i/fl)**2.2 for i in range(fl)])[np.newaxis, :]

    fr = min(20, cols//9)
    arr3[:, -fr:, 3] *= np.array([((fr-i)/fr)**2.0 for i in range(fr)])[np.newaxis, :]

    arr3[:,:,3] = np.clip(arr3[:,:,3], 0, 255)
    return Image.fromarray(arr3.astype(np.uint8), "RGBA")


_AMB_CACHE = {}
def get_amb(target_h):
    if target_h not in _AMB_CACHE:
        _AMB_CACHE[target_h] = prepare_ambulancia(target_h)
    return _AMB_CACHE[target_h]


# ═════════════════════════════════════════════════════════════════════════════
# HELPERS v2 (idénticos a la versión original)
# ═════════════════════════════════════════════════════════════════════════════
def px(rgb, a=255): return (*rgb, a)

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def gradient_v(draw, x0, y0, x1, y1, c_top, c_bot, steps=120):
    h_seg = (y1 - y0) / steps
    for i in range(steps):
        t = i / steps
        c = lerp_color(c_top, c_bot, t)
        draw.rectangle([x0, y0+i*h_seg, x1, y0+(i+1)*h_seg+1], fill=(*c,255))

def gradient_h(draw, x0, y0, x1, y1, c_left, c_right, steps=200):
    w_seg = (x1 - x0) / steps
    for i in range(steps):
        t = i / steps
        c = lerp_color(c_left, c_right, t)
        draw.rectangle([x0+i*w_seg, y0, x0+(i+1)*w_seg+1, y1], fill=(*c,255))

def glow_line(img, x0, y0, x1, y1, color, width=2, blur=8):
    layer = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    for w in range(width+blur, 0, -1):
        alpha = int(255 * (w/(width+blur))**2 * 0.6)
        d.line([(x0,y0),(x1,y1)], fill=(*color,alpha), width=w)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur//2)))
    ImageDraw.Draw(img).line([(x0,y0),(x1,y1)], fill=(*color,230), width=width)

def dot_grid(draw, x0, y0, x1, y1, spacing=28, color=C_BLUE_MID, alpha=40):
    for x in range(x0, x1, spacing):
        for y in range(y0, y1, spacing):
            draw.ellipse([x-1,y-1,x+1,y+1], fill=(*color,alpha))

def diagonal_lines(draw, x0, y0, x1, y1, gap=40, color=C_BLUE_MID, alpha=18):
    for offset in range(-(y1-y0), (x1-x0), gap):
        sx = x0 + offset
        draw.line([(sx,y0),(sx+(y1-y0),y1)], fill=(*color,alpha), width=1)

def hexgrid(draw, cx, cy, radius=60, color=C_BLUE_LT, alpha=25, rings=3):
    def hex_pts(cx, cy, r):
        return [(cx+r*math.cos(math.radians(60*i-30)),
                 cy+r*math.sin(math.radians(60*i-30))) for i in range(6)]
    draw.polygon(hex_pts(cx,cy,radius), outline=(*color,alpha), fill=None)
    for i in range(6):
        nx = cx + radius*1.73*math.cos(math.radians(60*i))
        ny = cy + radius*1.73*math.sin(math.radians(60*i))
        draw.polygon(hex_pts(nx,ny,radius), outline=(*color,alpha//2), fill=None)

def rounded_rect_aa(img, x0, y0, x1, y1, r, fill_color, alpha=255, outline=None, outline_w=1):
    layer = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x0,y0,x1,y1], radius=r, fill=(*fill_color,alpha))
    if outline:
        d.rounded_rectangle([x0,y0,x1,y1], radius=r, outline=(*outline,200), width=outline_w)
    img.alpha_composite(layer)

def glass_panel(img, x0, y0, x1, y1, r=12, tint=C_BLUE_CORP, alpha_fill=35, alpha_border=80):
    rounded_rect_aa(img, x0, y0, x1, y1, r, tint, alpha_fill)
    rounded_rect_aa(img, x0, y0, x1, y1, r, C_BLUE_LT, 0, outline=C_BLUE_LT, outline_w=1)
    layer = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x0+1,y0+1,x1-1,y0+r+8], radius=r, fill=(*C_WHITE,12))
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
    d = ImageDraw.Draw(img)
    fnt_g = get_font(int(9*scale), bold=False)
    fnt_i = get_font(int(30*scale), bold=True)
    lh = int(42*scale)
    d.rectangle([x, y+2, x+3, y+lh], fill=(*C_BLUE_LT,255))
    d.text((x+9,  y),              "GRUPO", font=fnt_g, fill=(*C_SILVER,200))
    d.text((x+8,  y+int(10*scale)),"IHSA",  font=fnt_i, fill=(*C_OFF_WHITE,255))

def accent_arc(draw, cx, cy, r_out, r_in, start_deg, end_deg, color, alpha=160):
    steps = max(30, (end_deg-start_deg))
    for i in range(steps):
        t1 = math.radians(start_deg + i*(end_deg-start_deg)/steps)
        t2 = math.radians(start_deg + (i+1)*(end_deg-start_deg)/steps)
        pts = [
            (cx+r_out*math.cos(t1), cy+r_out*math.sin(t1)),
            (cx+r_out*math.cos(t2), cy+r_out*math.sin(t2)),
            (cx+r_in*math.cos(t2),  cy+r_in*math.sin(t2)),
            (cx+r_in*math.cos(t1),  cy+r_in*math.sin(t1)),
        ]
        draw.polygon(pts, fill=(*color,alpha))

def kpi_zone_label(draw, x, y, label, value_hint="", color=C_SILVER):
    fnt_l = get_font(8)
    fnt_v = get_font(9, bold=True)
    draw.text((x, y),    label.upper(), font=fnt_l, fill=(*color,160))
    if value_hint:
        draw.text((x, y+11), value_hint, font=fnt_v, fill=(*C_OFF_WHITE,120))


# ═════════════════════════════════════════════════════════════════════════════
# COMPOSICIÓN DE AMBULANCIA SOBRE PANEL v2
# ═════════════════════════════════════════════════════════════════════════════
def composite_amb_panel(img, zone_y0, zone_y1, panel_width=PANEL_W,
                        bg_color=None):
    """
    Compone la ambulancia en la zona del panel lateral entre los slicers y el logo.
    zone_y0: y de inicio de la zona (debajo del último slicer)
    zone_y1: y de fin (arriba del logo)
    """
    zone_h = zone_y1 - zone_y0
    amb = get_amb(zone_h)
    if amb is None:
        return

    aw, ah = amb.size
    # Posicionar: margen izquierdo mínimo, el vehículo "sale" hacia la derecha
    paste_x = -6
    paste_y = zone_y1 - ah + 10  # alinear parte inferior con el fondo de la zona

    # Si se sale por arriba de la zona, recortar
    if paste_y < zone_y0 - 20:
        crop_top = (zone_y0 - 20) - paste_y
        amb = amb.crop((0, crop_top, aw, ah))
        paste_y = zone_y0 - 20
        aw, ah = amb.size

    img.alpha_composite(amb, (paste_x, paste_y))

    # Overlay superior: funde la ambulancia con el fondo del panel sobre ella
    fade_top_h = 65
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    for i in range(fade_top_h):
        a = int(255 * (1 - i/fade_top_h)**2.8)
        d.rectangle([0, paste_y+i, panel_width+50, paste_y+i+1],
                    fill=(*C_PANEL_BG, a))
    img.alpha_composite(L)

    # Overlay inferior: funde el pie del vehículo con el panel
    fade_bot_h = 30
    L2 = Image.new("RGBA", img.size, (0,0,0,0))
    d2 = ImageDraw.Draw(L2)
    for i in range(fade_bot_h):
        a = int(240 * ((fade_bot_h-i)/fade_bot_h)**1.8)
        d2.rectangle([0, zone_y1-fade_bot_h+i, panel_width+50, zone_y1-fade_bot_h+i+1],
                     fill=(*C_PANEL_BG, a))
    img.alpha_composite(L2)

    # Clip derecho: tapa completamente la ambulancia más allá del panel
    fill_bg = bg_color if bg_color else C_CONTENT
    clip_x = panel_width
    L3 = Image.new("RGBA", img.size, (0,0,0,0))
    d3 = ImageDraw.Draw(L3)
    d3.rectangle([clip_x+28, 0, W, H], fill=(*fill_bg, 255))
    for i in range(28):
        a = int(255 * ((28-i)/28)**1.4)
        d3.rectangle([clip_x+i, zone_y0-20, clip_x+i+1, zone_y1+10],
                     fill=(*fill_bg, a))
    img.alpha_composite(L3)

    # Línea de suelo (sutil, matches v2 style)
    glow_line(img, 10, zone_y1-8, panel_width-10, zone_y1-8,
              C_BLUE_MID, width=1, blur=4)


# ═════════════════════════════════════════════════════════════════════════════
# BASE: igual a v2 + ambulancia
# ═════════════════════════════════════════════════════════════════════════════
def build_base():
    img = Image.new("RGBA", (W, H), px(C_NAVY))
    draw = ImageDraw.Draw(img)

    gradient_v(draw, 0, 0, W, H, C_NAVY, C_NAVY2, steps=150)
    dot_grid(draw, PANEL_W, HEADER_H, W, H, spacing=32, color=C_BLUE_MID, alpha=28)
    hexgrid(draw, W-160, H-130, radius=55, color=C_BLUE_LT, alpha=18, rings=2)
    hexgrid(draw, W-80,  H-60,  radius=30, color=C_BLUE_LT, alpha=12)

    # Panel lateral
    gradient_h(draw, 0, 0, PANEL_W, H, C_NAVY2, C_PANEL_BG, steps=60)
    diagonal_lines(draw, 0, 0, PANEL_W, H, gap=35, color=C_BLUE_CORP, alpha=14)
    accent_arc(draw, PANEL_W-10, H+30, 180, 120, 150, 210, C_BLUE_CORP, alpha=55)
    accent_arc(draw, PANEL_W-10, H+30, 120,  85, 150, 210, C_BLUE_LT,  alpha=40)
    glow_line(img, PANEL_W, 0, PANEL_W, H, C_BLUE_LT, width=1, blur=10)

    # Header
    gradient_h(draw, PANEL_W, 0, W, HEADER_H, C_NAVY2, C_PANEL_BG, steps=80)
    glow_line(img, PANEL_W, HEADER_H, W, HEADER_H, C_BLUE_CORP, width=1, blur=8)
    accent_x = PANEL_W + int((W-PANEL_W)*0.40)
    glow_line(img, PANEL_W, HEADER_H, accent_x, HEADER_H, C_GOLD, width=1, blur=6)

    # Footer
    gradient_h(draw, PANEL_W, H-26, W, H, C_NAVY2, C_PANEL_BG, steps=60)
    glow_line(img, PANEL_W, H-26, W, H-26, C_BLUE_MID, width=1, blur=6)

    return img


# ═════════════════════════════════════════════════════════════════════════════
# TEMPLATE CONTENT — páginas de análisis (v2 + ambulancia)
# ═════════════════════════════════════════════════════════════════════════════
def template_content(slug, titulo, subtitulo, badge=None):
    img = build_base()
    draw = ImageDraw.Draw(img)

    # ── Segmentadores (igual a v2) ────────────────────────────────────────────
    labels = [("Período","MesAño"), ("Vertical","Negocio"),
              ("Cuenta","Contable"), ("Ceco","Centro costos")]
    sy = 72
    for lbl, hint in labels:
        kpi_zone_label(draw, 18, sy, lbl, hint)
        glass_panel(img, 12, sy+14, PANEL_W-12, sy+38, r=6,
                    tint=C_BLUE_CORP, alpha_fill=28)
        draw = ImageDraw.Draw(img)
        draw.polygon([(PANEL_W-28,sy+22),(PANEL_W-20,sy+22),(PANEL_W-24,sy+30)],
                     fill=(*C_BLUE_LT,120))
        sy += 60

    # ── AMBULANCIA en zona del panel (entre slicers y logo) ───────────────────
    # Slicers terminan en y ≈ sy = 312; logo en y = H-165 = 555
    amb_zone_y0 = sy - 8     # ~304 — justo bajo el último slicer
    amb_zone_y1 = H - 170    # ~550 — encima del logo
    composite_amb_panel(img, amb_zone_y0, amb_zone_y1)

    # ── Logo (igual a v2, conservar posición original) ────────────────────────
    draw_logo_premium(img, 22, H-165, scale=1.15)

    # ── Título en header ──────────────────────────────────────────────────────
    draw = ImageDraw.Draw(img)
    draw.text((PANEL_W+22, 10), titulo,    font=get_font(19,bold=True),
              fill=(*C_OFF_WHITE,255))
    draw.text((PANEL_W+22, 36), subtitulo, font=get_font(10),
              fill=(*C_SILVER,180))

    if badge:
        rounded_rect_aa(img, W-120, 14, W-30, 44, r=5,
                        fill_color=C_BLUE_CORP, alpha=60,
                        outline=C_BLUE_LT, outline_w=1)
        ImageDraw.Draw(img).text((W-114, 22), badge.upper(),
                                  font=get_font(8,bold=True), fill=(*C_CYAN,200))

    draw_logo_premium(img, W-95, 6, scale=0.7)

    # ── Zonas KPI y visuals (igual a v2) ─────────────────────────────────────
    kpi_y0, kpi_y1 = HEADER_H+14, HEADER_H+90
    kpi_x0 = PANEL_W + 20
    slot_w = int((W - kpi_x0 - 20)/4) - 8
    for i in range(4):
        sx = kpi_x0 + i*(slot_w+8)
        glass_panel(img, sx, kpi_y0, sx+slot_w, kpi_y1, r=10,
                    tint=C_CARD_BG, alpha_fill=85, alpha_border=60)
        glow_line(img, sx+12, kpi_y0+1, sx+slot_w-12, kpi_y0+1,
                  C_BLUE_LT, width=1, blur=4)

    main_y0 = HEADER_H + 104
    main_x0 = PANEL_W + 20
    main_w_l = int((W - main_x0 - 28)*0.60)
    glass_panel(img, main_x0, main_y0, main_x0+main_w_l, H-40, r=12,
                tint=C_CARD_BG, alpha_fill=70, alpha_border=50)
    right_x0 = main_x0 + main_w_l + 8
    glass_panel(img, right_x0, main_y0, W-20, H-40, r=12,
                tint=C_CARD_BG, alpha_fill=70, alpha_border=50)
    draw = ImageDraw.Draw(img)
    dot_grid(draw, main_x0+10, main_y0+10, main_x0+main_w_l-10, H-50,
             spacing=40, color=C_BLUE_LT, alpha=12)

    img.save(f"{OUT}/fondo_{slug}.png", "PNG")
    print(f"  ✓  {OUT}/fondo_{slug}.png")


# ═════════════════════════════════════════════════════════════════════════════
# TEMPLATE ÍNDICE — portada (v2 + ambulancia)
# ═════════════════════════════════════════════════════════════════════════════
def template_indice():
    img = Image.new("RGBA", (W, H), px(C_NAVY))
    draw = ImageDraw.Draw(img)

    gradient_v(draw, 0, 0, W, H, C_NAVY, (8,16,42), steps=160)

    div_x = int(W*0.42)   # 537px

    # Forma diagonal izquierda
    pts_diag = [(0,0),(div_x,0),(int(W*0.32),H),(0,H)]
    layer_shape = Image.new("RGBA",(W,H),(0,0,0,0))
    ds = ImageDraw.Draw(layer_shape)
    ds.polygon(pts_diag, fill=(*C_PANEL_BG,255))
    img.alpha_composite(layer_shape)
    draw = ImageDraw.Draw(img)

    diagonal_lines(draw, 0, 0, div_x, H, gap=38, color=C_BLUE_CORP, alpha=18)

    # Arcos decorativos derecha
    accent_arc(draw, W, H, 400, 300, 140, 200, C_BLUE_CORP, alpha=30)
    accent_arc(draw, W, H, 300, 240, 140, 200, C_BLUE_LT,   alpha=25)
    accent_arc(draw, W, H, 240, 200, 140, 200, C_CYAN,      alpha=18)
    dot_grid(draw, div_x, 0, W, H, spacing=30, color=C_BLUE_MID, alpha=30)
    hexgrid(draw, W-200, H-180, radius=70, color=C_BLUE_LT, alpha=16)

    glow_line(img, div_x, 0, div_x, H, C_BLUE_LT, width=1, blur=14)

    draw = ImageDraw.Draw(img)

    # Textos panel izquierdo
    draw.text((48, 64), "OPERACIONES COMPLEJAS · 2025–2026",
              font=get_font(10), fill=(*C_BLUE_LT,180))
    glow_line(img, 48, 82, 48+220, 82, C_GOLD, width=1, blur=5)
    draw = ImageDraw.Draw(img)
    draw.text((48,  95), "Real vs",     font=get_font(22,bold=True), fill=(*C_SILVER,210))
    draw.text((48, 128), "Presupuesto", font=get_font(42,bold=True), fill=(*C_OFF_WHITE,255))
    glow_line(img, 48, 222, 220, 222, C_BLUE_CORP, width=2, blur=8)
    draw = ImageDraw.Draw(img)
    draw.text((48, 234), "Panel de control presupuestario",
              font=get_font(11), fill=(*C_SILVER,160))
    draw.text((48, 252), "Grupo IHSA · Operaciones Complejas",
              font=get_font(11), fill=(*C_BLUE_LT,140))

    # ── AMBULANCIA en portada ─────────────────────────────────────────────────
    # Zona: y=270 → y=590 (entre textos y logo)
    amb_zone_y0_idx = 268
    amb_zone_y1_idx = H - 130    # 590

    zone_h_idx = amb_zone_y1_idx - amb_zone_y0_idx
    amb_idx = get_amb(zone_h_idx)
    if amb_idx:
        aw, ah = amb_idx.size
        paste_x = -12
        paste_y = amb_zone_y1_idx - ah + 8
        if paste_y < amb_zone_y0_idx - 20:
            crop_top = (amb_zone_y0_idx - 20) - paste_y
            amb_idx = amb_idx.crop((0, crop_top, aw, ah))
            paste_y = amb_zone_y0_idx - 20
            aw, ah = amb_idx.size

        img.alpha_composite(amb_idx, (paste_x, paste_y))

        # Fade superior
        L = Image.new("RGBA", img.size, (0,0,0,0))
        d = ImageDraw.Draw(L)
        for i in range(80):
            a = int(255*(1-i/80)**3.0)
            d.rectangle([0, paste_y+i, div_x+60, paste_y+i+1],
                        fill=(*C_PANEL_BG, a))
        img.alpha_composite(L)

        # Fade inferior
        L2 = Image.new("RGBA", img.size, (0,0,0,0))
        d2 = ImageDraw.Draw(L2)
        for i in range(40):
            a = int(240*((40-i)/40)**1.8)
            d2.rectangle([0, amb_zone_y1_idx-40+i, div_x+60, amb_zone_y1_idx-39+i],
                         fill=(*C_PANEL_BG, a))
        img.alpha_composite(L2)

        # Fade lateral derecho (en el borde div_x)
        L3 = Image.new("RGBA", img.size, (0,0,0,0))
        d3 = ImageDraw.Draw(L3)
        for i in range(50):
            a = int(255*((50-i)/50)**1.5)
            d3.rectangle([div_x-10+i, amb_zone_y0_idx-20,
                          div_x-9+i,  amb_zone_y1_idx+10],
                         fill=(*C_CONTENT, a))
        img.alpha_composite(L3)

    # Logo panel izquierdo (v2 original)
    draw_logo_premium(img, 48, H-130, scale=1.8)

    # ── Panel derecho: navegación (igual a v2) ────────────────────────────────
    right_x0 = div_x + 30
    right_w   = W - right_x0 - 30
    draw = ImageDraw.Draw(img)
    draw.text((right_x0, 24), "SELECCIONÁ UNA SECCIÓN",
              font=get_font(11,bold=True), fill=(*C_OFF_WHITE,200))
    draw.text((right_x0, 42), "Panel de navegación rápida",
              font=get_font(9), fill=(*C_SILVER,140))
    glow_line(img, right_x0, 62, W-30, 62, C_BLUE_CORP, width=1, blur=6)

    botones = [
        ("01","Resumen Ejecutivo",   "KPIs globales · Real vs PA",     C_BLUE_CORP),
        ("02","Análisis Comercial",  "Desvío por vertical de negocio", C_BLUE_MID),
        ("03","Vista Operativa",     "Detalle cuenta y ceco",          C_BLUE_MID),
        ("04","Detalle Proveedores", "Gasto real · Base SAP",          C_BLUE_MID),
        ("05","Entregable OPEX",     "Resumen operativo mensual",      C_BLUE_MID),
        ("06","Auditoría Interna",   "Controles y validaciones",       C_NAVY2),
    ]

    btn_w = right_w//2 - 8
    btn_h = (H-90)//3 - 12

    for i, (num, label, desc, color) in enumerate(botones):
        col, row = i%2, i//2
        bx = right_x0 + col*(btn_w+8)
        by = 76 + row*(btn_h+10)

        glass_panel(img, bx, by, bx+btn_w, by+btn_h, r=10,
                    tint=color, alpha_fill=65, alpha_border=70)
        d2 = ImageDraw.Draw(img)
        d2.text((bx+btn_w-38, by+6), num, font=get_font(20,bold=True),
                fill=(*C_BLUE_LT,45))
        glass_panel(img, bx, by, bx+4, by+btn_h, r=4,
                    tint=C_BLUE_LT, alpha_fill=180)
        d2 = ImageDraw.Draw(img)
        d2.text((bx+14, by+14), label, font=get_font(10,bold=True),
                fill=(*C_OFF_WHITE,240))
        d2.text((bx+14, by+32), desc,  font=get_font(8),
                fill=(*C_SILVER,160))
        d2.text((bx+btn_w-20, by+btn_h-22), "›", font=get_font(18),
                fill=(*C_BLUE_LT,160))

    img.save(f"{OUT}/fondo_00_indice.png", "PNG")
    print(f"  ✓  {OUT}/fondo_00_indice.png")


# ═════════════════════════════════════════════════════════════════════════════
# TEMPLATE AUDITORÍA — v2 original + ambulancia (panel angosto 200px)
# ═════════════════════════════════════════════════════════════════════════════
def template_auditoria():
    img = Image.new("RGBA", (W, H), px(C_NAVY))
    draw = ImageDraw.Draw(img)
    PW_AUD = 200

    gradient_v(draw, 0, 0, W, H, (8,14,35), (12,20,50), steps=150)
    dot_grid(draw, 0, 0, W, H, spacing=28, color=C_BLUE_MID, alpha=22)

    gradient_h(draw, 0, 0, PW_AUD, H, (12,22,58), (8,16,42), steps=50)
    diagonal_lines(draw, 0, 0, PW_AUD, H, gap=30, color=C_BLUE_CORP, alpha=16)
    accent_arc(draw, PW_AUD+10, H+20, 150, 100, 150, 210, C_BLUE_CORP, alpha=40)
    glow_line(img, PW_AUD, 0, PW_AUD, H, C_RED_SOFT, width=1, blur=12)

    gradient_h(draw, PW_AUD, 0, W, HEADER_H, (10,18,48), (15,25,60), steps=80)
    glow_line(img, PW_AUD, HEADER_H, W, HEADER_H, C_RED_SOFT, width=1, blur=8)
    glow_line(img, PW_AUD, HEADER_H, PW_AUD+int((W-PW_AUD)*0.35), HEADER_H,
              C_GOLD, width=1, blur=5)

    draw = ImageDraw.Draw(img)

    # Slicers (2 en auditoría, igual a v2)
    sy = 72
    for lbl, hint in [("Período","MesAño"),("Vertical","Negocio")]:
        kpi_zone_label(draw, 14, sy, lbl, hint)
        glass_panel(img, 10, sy+14, PW_AUD-10, sy+38, r=6,
                    tint=C_BLUE_CORP, alpha_fill=30)
        sy += 60

    # Ambulancia en zona del panel de auditoría
    composite_amb_panel(img, sy - 5, H - 135, panel_width=PW_AUD,
                        bg_color=(8, 14, 35))

    draw_logo_premium(img, 16, H-130, scale=1.0)

    draw = ImageDraw.Draw(img)
    draw.text((PW_AUD+20, 12), "Auditoría — Controles y Validaciones",
              font=get_font(17,bold=True), fill=(*C_OFF_WHITE,255))
    draw.text((PW_AUD+20, 36), "Conciliación entre fuentes · Uso interno · Equipo de datos",
              font=get_font(9), fill=(*C_SILVER,170))

    glass_panel(img, W-145, 13, W-20, 40, r=5, tint=(180,40,40), alpha_fill=50)
    ImageDraw.Draw(img).text((W-138, 20), "⚠  USO INTERNO",
                              font=get_font(8,bold=True), fill=(*C_RED_SOFT,220))
    draw_logo_premium(img, W-95, 6, scale=0.68)

    cy0 = HEADER_H + 14
    slot_w2 = int((W-PW_AUD-28)/3) - 6
    for i in range(3):
        sx = PW_AUD+20 + i*(slot_w2+8)
        glass_panel(img, sx, cy0, sx+slot_w2, cy0+72, r=8, tint=C_CARD_BG, alpha_fill=80)
        glow_line(img, sx+10, cy0+1, sx+slot_w2-10, cy0+1, C_RED_SOFT, width=1, blur=4)

    glass_panel(img, PW_AUD+20, cy0+86, W-20, H-36, r=10, tint=C_CARD_BG, alpha_fill=75)
    glow_line(img, PW_AUD+20, cy0+86, W-20, cy0+86, C_BLUE_CORP, width=1, blur=6)

    draw = ImageDraw.Draw(img)
    gradient_h(draw, PW_AUD, H-24, W, H, (10,18,48), (15,25,60), steps=60)
    glow_line(img, PW_AUD, H-24, W, H-24, C_BLUE_MID, width=1, blur=5)

    img.save(f"{OUT}/fondo_06_auditoria.png", "PNG")
    print(f"  ✓  {OUT}/fondo_06_auditoria.png")


# ── Tema JSON (v2 original) ───────────────────────────────────────────────────
def generar_tema_json():
    import json
    tema = {
        "name": "GrupoIHSA_Premium_v7",
        "dataColors": ["#5294DA","#3267B8","#7CC4E8","#20488C","#D2AF50",
                       "#20B2AA","#7AADDF","#A8C8EE"],
        "background":   "#0A1432",
        "foreground":   "#5294DA",
        "tableAccent":  "#3267B8",
        "visualStyles": {
            "*": {"*": {
                "fontFamily": [{"value":"Segoe UI"}],
                "background": [{"color":{"solid":{"color":"#16265580"}}}]
            }},
            "card": {"*": {
                "background":   [{"color":{"solid":{"color":"#162655"}}}],
                "border":       [{"show":True,"color":{"solid":{"color":"#3267B8"}},"radius":10}],
                "calloutValue": [{"fontSize":22,"fontBold":True,
                                  "color":{"solid":{"color":"#E6EEFA"}}}],
                "label":        [{"fontSize":9,"color":{"solid":{"color":"#8AABD4"}}}]
            }},
            "slicer": {"*": {
                "background": [{"color":{"solid":{"color":"#162655"}}}],
                "border":     [{"show":False}],
                "header":     [{"fontColor":{"solid":{"color":"#E6EEFA"}},
                                "background":{"solid":{"color":"#20488C"}}}],
                "items":      [{"fontColor":{"solid":{"color":"#C8D8F0"}}}]
            }},
            "tableEx": {"*": {
                "header":     [{"fontColor":{"solid":{"color":"#FFFFFF"}},
                                "background":{"solid":{"color":"#3267B8"}}}],
                "rowHeaders": [{"fontColor":{"solid":{"color":"#C8D8F0"}}}],
                "values":     [{"fontColor":{"solid":{"color":"#E6EEFA"}}}],
                "grid":       [{"gridVertical":False,"rowPadding":5,
                                "outlineColor":{"solid":{"color":"#20488C"}}}]
            }},
            "matrix": {"*": {
                "header":   [{"fontColor":{"solid":{"color":"#FFFFFF"}},
                              "background":{"solid":{"color":"#3267B8"}}}],
                "values":   [{"fontColor":{"solid":{"color":"#E6EEFA"}}}],
                "subTotals":[{"fontColor":{"solid":{"color":"#5294DA"}},
                              "background":{"solid":{"color":"#0F1E48"}}}]
            }},
            "lineChart": {"*": {"lineWidth":[{"value":2}],"markerSize":[{"value":5}],
                                "dataPoint":[{"defaultColor":{"solid":{"color":"#5294DA"}}}]}},
            "barChart":  {"*": {"dataPoint":[{"defaultColor":{"solid":{"color":"#3267B8"}}}]}}
        },
        "good":"#20B2AA","neutral":"#5294DA","bad":"#DC4646",
        "maximum":"#3267B8","center":"#7CC4E8","minimum":"#20488C","null":"#2A3A6A"
    }
    p = f"{OUT}/tema_GrupoIHSA_Premium_v7.json"
    with open(p,"w",encoding="utf-8") as f:
        json.dump(tema,f,indent=2,ensure_ascii=False)
    print(f"  ✓  {p}")


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if os.path.exists(AMB):
        print(f"\n  ✦  Ambulancia: {AMB}")
    else:
        print(f"\n  ⚠  Sin ambulancia — {AMB}")

    print("\n── IHSA Premium v7 (base v2 + ambulancia) ──────────────")
    template_indice()
    template_content("01_resumen",    "Resumen Ejecutivo",
                     "Real vs Presupuesto  ·  Operaciones Complejas  ·  2025-2026",
                     "GLOBAL")
    template_content("02_comercial",  "Análisis Comercial",
                     "Desvío presupuestario por vertical de negocio",
                     "COMERCIAL")
    template_content("03_operativa",  "Vista Operativa",
                     "Detalle por cuenta contable y centro de costos",
                     "OPERATIVA")
    template_content("04_proveedores","Detalle de Proveedores",
                     "Gasto real por proveedor  ·  Base SAP transaccional",
                     "PROVEEDORES")
    template_content("05_opex",       "Entregable OPEX",
                     "Resumen de gastos operativos  ·  Clasificación CAPEX/OPEX",
                     "OPEX")
    template_auditoria()

    print("\n── Tema ─────────────────────────────────────────────────")
    generar_tema_json()

    print("\n── Archivos ─────────────────────────────────────────────")
    for f in sorted(os.listdir(OUT)):
        print(f"   {f:<48} {os.path.getsize(f'{OUT}/{f}')//1024:>4} KB")
