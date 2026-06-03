#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grupo IHSA — Dashboard Premium v6
Composición profesional: ambulancia real en panel lateral con tratamiento
de imagen de nivel enterprise (remoción fondo, shadow, glow, color grading).
"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops, ImageEnhance
import numpy as np
import math, os

OUT  = "/home/user/General/assets_ihsa_v6"
AMB  = "/home/user/General/ambulancia_ihsa.png"
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720

# ── Paleta IHSA exacta ────────────────────────────────────────────────────────
BLUE        = ( 50, 103, 184)    # #3267B8
BLUE_DARK   = ( 23,  55, 115)    # #173773
BLUE_LIGHT  = ( 82, 148, 218)    # #5294DA
BLUE_PALE   = (200, 220, 245)
NAVY        = ( 13,  24,  64)    # panel fondo profundo
NAVY2       = ( 18,  33,  82)
WHITE       = (255, 255, 255)
CONTENT_BG  = (246, 249, 254)    # blanco azulado (área contenido)
CARD        = (255, 255, 255)
CARD_BORDER = (218, 230, 248)
TEXT_H      = ( 18,  32,  72)
TEXT_B      = ( 60,  85, 135)
TEXT_S      = (140, 165, 200)
GOLD        = (200, 160,  40)
ORANGE      = (230, 100,  30)
GREEN       = ( 25, 155, 110)
RED         = (200,  45,  50)

PW = 258   # ancho del panel
HH = 66    # alto del header


# ═════════════════════════════════════════════════════════════════════════════
# TRATAMIENTO PROFESIONAL DE LA AMBULANCIA
# ═════════════════════════════════════════════════════════════════════════════
def prepare_ambulancia(path, target_w, target_h, extend_right=60):
    """
    Tratamiento profesional para vehículo blanco sobre fondo blanco.
    Técnica: color-grading IHSA navy + blend mode para integración total.
    El vehículo adquiere una atmósfera oscura corporativa manteniendo
    los detalles (tracks, logo, checkerboard naranja).
    """
    src = Image.open(path).convert("RGBA")
    arr = np.array(src, dtype=np.float32)

    # ── Crop al bbox del vehículo ─────────────────────────────────────────────
    R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    non_white = ~((R > 248) & (G > 248) & (B > 248))
    ys, xs = np.where(non_white)
    if len(ys) == 0:
        return src
    pad = 20
    x0 = max(0, int(xs.min()) - pad)
    y0 = max(0, int(ys.min()) - pad)
    x1 = min(src.width,  int(xs.max()) + pad)
    y1 = min(src.height, int(ys.max()) + pad)
    veh = src.crop((x0, y0, x1, y1))

    # ── Escalar por altura para que el vehículo sea prominente ───────────────
    # El vehículo tiene aspect ratio ~1.67:1 (horizontal).
    # Escalar para que LLENE la altura disponible → ancho desborda el panel
    # → efecto Mercedes-Benz: vehículo "sale" del panel hacia el contenido.
    vw, vh = veh.size
    scale  = (target_h * 1.05) / vh
    new_w  = int(vw * scale)
    new_h  = int(target_h * 1.05)
    veh = veh.resize((new_w, new_h), Image.LANCZOS)

    # ── COLOR GRADING IHSA premium ────────────────────────────────────────────
    # Técnica: oscurecer + tinte navy, preservando la forma del vehículo.
    # El fondo blanco se convierte en navy oscuro (se integra con el panel).
    # El cuerpo blanco del vehículo queda como tono navy claro (reconocible).
    # Los detalles de color (naranja, rojo, tracks oscuros) retienen identidad.
    veh_arr = np.array(veh, dtype=np.float32)
    Rv = veh_arr[:,:,0] / 255.0
    Gv = veh_arr[:,:,1] / 255.0
    Bv = veh_arr[:,:,2] / 255.0

    # Luminosidad y saturación
    lum = 0.2126 * Rv + 0.7152 * Gv + 0.0722 * Bv
    cmax = np.maximum(np.maximum(Rv, Gv), Bv)
    cmin = np.minimum(np.minimum(Rv, Gv), Bv)
    denom = np.where(cmax > 0.001, cmax, 0.001)
    sat = (cmax - cmin) / denom

    # Color del fondo objetivo: navy oscuro (igual al panel)
    # Color del vehículo blanco objetivo: navy claro (distinguible del fondo)
    # Colores de detalle (naranja, rojo, oscuro): conservar con boost
    navy_r, navy_g, navy_b = NAVY[0]/255.0, NAVY[1]/255.0, NAVY[2]/255.0
    # "Navy claro" para el cuerpo del vehículo
    body_r = (NAVY[0]+30)/255.0
    body_g = (NAVY[1]+45)/255.0
    body_b = (NAVY[2]+90)/255.0

    # factor de mezcla hacia navy:
    # alto cuando lum alto Y sat bajo (fondo blanco / cuerpo blanco)
    # bajo cuando sat alto (colores reales) o lum bajo (sombras/tracks)
    blend = np.clip((lum * 0.85 + 0.15) * (1.0 - sat * 2.5), 0, 1)

    # Los píxeles de fondo puro (muy blancos, muy baja sat) → navy exacto
    # Los del cuerpo del vehículo (blanco moderado) → navy claro
    is_bg_white = np.clip((lum - 0.92) * 12, 0, 1) * np.clip(1 - sat * 10, 0, 1)
    target_r = navy_r * is_bg_white + body_r * (1 - is_bg_white)
    target_g = navy_g * is_bg_white + body_g * (1 - is_bg_white)
    target_b = navy_b * is_bg_white + body_b * (1 - is_bg_white)

    # Boost de los colores de detalle (tracks, checkerboard, logo)
    detail_boost = np.clip(sat * 1.5, 0, 1) + np.clip((0.5 - lum) * 1.2, 0, 1)
    detail_boost = np.clip(detail_boost, 0, 1)

    out_R = Rv * detail_boost + (Rv * (1-blend) + target_r * blend) * (1 - detail_boost)
    out_G = Gv * detail_boost + (Gv * (1-blend) + target_g * blend) * (1 - detail_boost)
    out_B = Bv * detail_boost + (Bv * (1-blend) + target_b * blend) * (1 - detail_boost)

    # Oscurecer ligeramente todo (gamma) para look nocturno/dramático
    gamma = 0.80
    out_R = np.power(np.clip(out_R, 0, 1), 1/gamma)
    out_G = np.power(np.clip(out_G, 0, 1), 1/gamma)
    out_B = np.power(np.clip(out_B, 0, 1), 1/gamma)

    veh_arr[:,:,0] = np.clip(out_R * 255, 0, 255)
    veh_arr[:,:,1] = np.clip(out_G * 255, 0, 255)
    veh_arr[:,:,2] = np.clip(out_B * 255, 0, 255)
    # Alpha uniforme = imagen completa opaca (sin recorte de alpha)
    veh_arr[:,:,3] = 255.0

    # ── Fades de borde para integración con el panel ─────────────────────────
    rows, cols = veh_arr.shape[:2]

    # Superior: desvanece fuertemente para no tapar los slicers
    ft = min(70, rows // 3)
    fade_top = np.array([((i/ft)**2.5) for i in range(ft)] + [1.0]*(rows-ft))
    veh_arr[:, :, 3] *= fade_top[:, np.newaxis]

    # Inferior
    fb = min(50, rows // 5)
    fade_bot = np.array([1.0]*(rows-fb) + [((fb-i)/fb)**1.5 for i in range(fb)])
    veh_arr[:, :, 3] *= fade_bot[:, np.newaxis]

    # Izquierda
    fl = min(35, cols // 6)
    fade_l = np.array([((i/fl)**2.0) for i in range(fl)] + [1.0]*(cols-fl))
    veh_arr[:, :, 3] *= fade_l[np.newaxis, :]

    # Derecha (suave, el vehículo puede salir un poco)
    fr = min(25, cols // 8)
    fade_r = np.array([1.0]*(cols-fr) + [((fr-i)/fr)**2.0 for i in range(fr)])
    veh_arr[:, :, 3] *= fade_r[np.newaxis, :]

    veh_arr[:, :, 3] = np.clip(veh_arr[:, :, 3], 0, 255)
    return Image.fromarray(veh_arr.astype(np.uint8), "RGBA")


# ── Caché global de la ambulancia preparada ───────────────────────────────────
_AMB_CACHE = {}
def get_ambulancia(target_w, target_h, extend_right=50):
    key = (target_w, target_h, extend_right)
    if key not in _AMB_CACHE:
        if os.path.exists(AMB):
            _AMB_CACHE[key] = prepare_ambulancia(AMB, target_w, target_h, extend_right)
        else:
            _AMB_CACHE[key] = None
    return _AMB_CACHE[key]


# ═════════════════════════════════════════════════════════════════════════════
# HELPERS GENERALES
# ═════════════════════════════════════════════════════════════════════════════
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

def grad_v(draw, x0,y0,x1,y1, top,bot, n=200):
    if n < 1: return
    s = (y1-y0)/n
    for i in range(n):
        draw.rectangle([x0,y0+i*s,x1,y0+(i+1)*s+1], fill=(*lerp(top,bot,i/n),255))

def shadow(img, x0,y0,x1,y1, r=14, offset=4, blur=14):
    L = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(L).rounded_rectangle(
        [x0+offset,y0+offset,x1+offset,y1+offset],
        radius=r, fill=(*TEXT_H, 40))
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
        ImageDraw.Draw(La).rounded_rectangle([x0,y0,x1,y0+5],
                                              radius=r//2, fill=(*accent,255))
        img.alpha_composite(La)

def glow_line(img, x0,y0,x1,y1, color, w=1, spread=10):
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    for s in range(spread,0,-1):
        d.line([(x0,y0),(x1,y1)], fill=(*color, int(110*(s/spread)**2)), width=s)
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(spread//4)))
    ImageDraw.Draw(img).line([(x0,y0),(x1,y1)], fill=(*color,210), width=w)

def rounded_rect_layer(img, x0,y0,x1,y1, r, color, alpha, outline=None):
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([x0,y0,x1,y1], radius=r, fill=(*color,alpha))
    if outline:
        d.rounded_rectangle([x0,y0,x1,y1], radius=r,
                             outline=(*outline[0],outline[1]), width=1)
    img.alpha_composite(L)

def logo(img, x, y, scale=1.0, on_dark=True):
    d = ImageDraw.Draw(img)
    fg  = WHITE if on_dark else BLUE
    fg2 = BLUE_LIGHT if on_dark else BLUE
    fnt_g = font(int(8*scale))
    fnt_i = font(int(28*scale), bold=True)
    d.rectangle([x, y+2, x+3, y+int(38*scale)], fill=(*fg2,255))
    d.text((x+9,  y),               "GRUPO", font=fnt_g, fill=(*fg,170))
    d.text((x+8,  y+int(10*scale)), "IHSA",  font=fnt_i, fill=(*fg,255))

def slicer_slot(img, x0, y, label, width):
    d = ImageDraw.Draw(img)
    d.text((x0, y), label.upper(), font=font(7), fill=(*TEXT_S,180))
    y1, y2 = y+12, y+34
    rounded_rect_layer(img, x0, y1, x0+width, y2, 6, NAVY2, 200)
    rounded_rect_layer(img, x0, y1, x0+width, y2, 6, BLUE, 0,
                       outline=(BLUE_LIGHT, 60))
    d = ImageDraw.Draw(img)
    d.text((x0+10, y1+6), "Todos",     font=font(9),  fill=(*TEXT_S,120))
    d.text((x0+width-18, y1+5), "▾",  font=font(10), fill=(*BLUE_LIGHT,160))


# ═════════════════════════════════════════════════════════════════════════════
# PANEL LATERAL PREMIUM
# ═════════════════════════════════════════════════════════════════════════════
def build_panel(img, page_label=""):
    draw = ImageDraw.Draw(img)

    # ── Gradiente navy de fondo — profundo y atmosférico ─────────────────────
    grad_v(draw, 0, 0, PW, H,
           lerp(NAVY, NAVY2, 0.3),
           lerp(NAVY, (8, 15, 45), 0.7))

    # ── Textura de líneas diagonales sutiles ──────────────────────────────────
    for off in range(-H, W, 55):
        draw.line([(off,0),(off+H,H)], fill=(*BLUE_DARK,8), width=1)

    # ── SHAPE ORGÁNICO IHSA — blob en esquina inferior derecha del panel ──────
    # Reproducción exacta de los templates corporativos (slides 1 y 2)
    blob_cx = PW - 20
    blob_cy = H + 25
    for r, alpha in [(230,18),(175,14),(125,11),(82,8),(45,6)]:
        L = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(L).ellipse(
            [blob_cx-r, blob_cy-r, blob_cx+r, blob_cy+r],
            fill=(*BLUE, alpha))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(3)))

    # Blob secundario en esquina superior izquierda (muy sutil)
    for r, alpha in [(160,7),(110,5),(65,4)]:
        L = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(L).ellipse([-r, -r, r, r], fill=(*BLUE_LIGHT, alpha))
        img.alpha_composite(L)

    # ── AMBULANCIA — composición premium ──────────────────────────────────────
    # El vehículo se escala por ALTURA para llenar la zona inferior del panel.
    # Por su proporción horizontal (1.67:1), desborda al área de contenido
    # creando el efecto "Mercedes-Benz": el vehículo emerge del panel.
    amb_zone_y0 = 330
    amb_zone_h  = H - amb_zone_y0 - 15
    amb_zone_w  = PW

    amb = get_ambulancia(amb_zone_w, amb_zone_h, extend_right=0)
    if amb:
        aw, ah = amb.size
        # Alinear: el LADO IZQUIERDO del vehículo desde x=0 del panel
        # La ambulancia desborda a la derecha (hacia el contenido) — efecto dinámico
        paste_x = -8
        paste_y = H - ah - 10

        # Si se sale por arriba, recortar desde arriba (conservar la parte inferior)
        if paste_y < amb_zone_y0 - 15:
            crop_top = (amb_zone_y0 - 15) - paste_y
            amb = amb.crop((0, crop_top, aw, ah - crop_top))
            paste_y = amb_zone_y0 - 15
            aw, ah = amb.size

        img.alpha_composite(amb, (paste_x, paste_y))

        # Overlay superior (blend suave amb → panel sobre los slicers)
        ov_h = 80
        ov_y = paste_y
        L = Image.new("RGBA", img.size, (0,0,0,0))
        d_ov = ImageDraw.Draw(L)
        for i in range(ov_h):
            a = int(245 * (1 - i/ov_h)**2.5)
            d_ov.rectangle([0, ov_y+i, W, ov_y+i+1], fill=(*NAVY, a))
        img.alpha_composite(L)

        # Overlay inferior (pie del vehículo → fondo panel)
        bot_h = 35
        L2 = Image.new("RGBA", img.size, (0,0,0,0))
        d2 = ImageDraw.Draw(L2)
        for i in range(bot_h):
            a = int(230 * ((bot_h-i)/bot_h)**1.5)
            d2.rectangle([0, H-bot_h+i, W, H-bot_h+i+1], fill=(*NAVY, a))
        img.alpha_composite(L2)

        # Máscara de clip derecho: recorta el vehículo en el borde del panel
        # dejando solo 30px de overflow (rueda/frente barely visible)
        clip_x = PW + 30
        L3 = Image.new("RGBA", img.size, (0,0,0,0))
        d3 = ImageDraw.Draw(L3)
        # Fade lateral derecho del vehículo (últimos 40px antes del clip)
        for i in range(40):
            a = int(255 * ((40-i)/40)**1.5)
            d3.rectangle([clip_x+i, 0, clip_x+i+1, H], fill=(*CONTENT_BG, a))
        img.alpha_composite(L3)

        # Línea de suelo decorativa
        glow_line(img, 12, H-24, PW-8, H-24, BLUE_DARK, w=1, spread=4)

    else:
        rounded_rect_layer(img, 8, 330, PW-8, H-28, 12, BLUE_DARK, 60)
        draw = ImageDraw.Draw(img)
        draw.text((18, (330 + H-28)//2 - 8), "[ ambulancia_ihsa.png ]",
                  font=font(8), fill=(*BLUE_LIGHT, 60))

    # ── Separador derecho del panel — glow line premium ───────────────────────
    glow_line(img, PW, 0, PW, H, BLUE, w=1, spread=16)

    # ── LOGO ─────────────────────────────────────────────────────────────────
    logo(img, 20, 16, scale=1.1)

    draw = ImageDraw.Draw(img)
    draw.line([(16, 70), (PW-16, 70)], fill=(*BLUE_LIGHT,35), width=1)

    # ── Etiqueta de sección ───────────────────────────────────────────────────
    if page_label:
        draw.text((16, 78), "SECCIÓN", font=font(7), fill=(*TEXT_S,120))
        draw.text((16, 90), page_label, font=font(10, bold=True),
                  fill=(*WHITE,210))
        draw.line([(16,108),(PW-16,108)], fill=(*BLUE_DARK,80), width=1)

    # ── Segmentadores ─────────────────────────────────────────────────────────
    sw = PW - 32
    sy = 118 if page_label else 86
    for lbl in ["Período (MesAño)", "Vertical", "Cuenta", "Ceco"]:
        slicer_slot(img, 16, sy, lbl, sw)
        sy += 56

    # ── Pie del panel ─────────────────────────────────────────────────────────
    draw = ImageDraw.Draw(img)
    draw.text((16, H-18), "Operaciones Complejas · 2025–2026",
              font=font(7), fill=(*TEXT_S,70))


# ═════════════════════════════════════════════════════════════════════════════
# ÁREA DE CONTENIDO
# ═════════════════════════════════════════════════════════════════════════════
def build_content(img, titulo, subtitulo, badge=None, dark_hdr=False):
    draw = ImageDraw.Draw(img)

    # Fondo blanco azulado (limpio, profesional)
    draw.rectangle([PW+1, 0, W, H], fill=(*CONTENT_BG, 255))

    hdr_color = NAVY if dark_hdr else WHITE
    draw.rectangle([PW+1, 0, W, HH], fill=(*hdr_color, 255))

    if dark_hdr:
        glow_line(img, PW+1, HH, W, HH, BLUE, w=1, spread=10)
    else:
        draw = ImageDraw.Draw(img)
        draw.line([(PW+20, HH),(W-20, HH)], fill=(*CARD_BORDER,255), width=1)
        glow_line(img, PW+20, HH, PW+180, HH, GOLD, w=2, spread=8)

    tc = WHITE if dark_hdr else TEXT_H
    sc = TEXT_S if dark_hdr else TEXT_B
    draw = ImageDraw.Draw(img)
    draw.text((PW+22, 10), titulo,    font=font(18, bold=True), fill=(*tc,255))
    draw.text((PW+22, 37), subtitulo, font=font(10),            fill=(*sc,200))

    if badge:
        bw = len(badge)*7 + 22
        rounded_rect_layer(img, W-bw-110, 14, W-110, 48, 6, BLUE, 215)
        ImageDraw.Draw(img).text((W-bw-102, 22), badge.upper(),
                                  font=font(8, bold=True), fill=(*WHITE,245))

    logo(img, W-93, 7, scale=0.70, on_dark=dark_hdr)


# ═════════════════════════════════════════════════════════════════════════════
# LAYOUTS DE CONTENIDO
# ═════════════════════════════════════════════════════════════════════════════
def layout_resumen(img):
    mx0, mw = PW+18, W-PW-36
    kw = mw//4 - 5
    for i, acc in enumerate([BLUE, GREEN, RED, GOLD]):
        card(img, mx0+i*(kw+6), HH+14, mx0+i*(kw+6)+kw, HH+92, r=12, accent=acc)
    card(img, mx0, HH+106, mx0+int(mw*0.60), H-18, r=14, accent=BLUE)
    card(img, mx0+int(mw*0.60)+8, HH+106, mx0+mw, H-18, r=14, accent=BLUE_LIGHT)

def layout_table(img, kpis=3):
    mx0, mw = PW+18, W-PW-36
    kw = mw//kpis - 5
    for i, acc in enumerate([BLUE, GREEN, RED, GOLD][:kpis]):
        card(img, mx0+i*(kw+6), HH+14, mx0+i*(kw+6)+kw, HH+82, r=12, accent=acc)
    ty0 = HH+98
    card(img, mx0, ty0, mx0+mw, H-18, r=14, accent=BLUE)
    rounded_rect_layer(img, mx0, ty0, mx0+mw, ty0+5,  14, BLUE, 255)
    L = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(L).rounded_rectangle([mx0, ty0+3, mx0+mw, ty0+36],
                                         radius=0, fill=(*BLUE,255))
    img.alpha_composite(L)
    cols = ["Vertical","Cuenta","Denominación","Ceco","Real Mes","PA Mes","Variación","Var%"]
    cw = mw // len(cols)
    d = ImageDraw.Draw(img)
    for i, c in enumerate(cols):
        d.text((mx0+6+i*cw, ty0+12), c, font=font(8, bold=True), fill=(*WHITE,225))
    for r in range(7):
        a = 18 if r%2==0 else 0
        L2 = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(L2).rectangle(
            [mx0, ty0+36+r*26, mx0+mw, ty0+36+(r+1)*26], fill=(*BLUE_PALE, a))
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
                                         radius=0, fill=(*RED,255))
    img.alpha_composite(L)
    cols = ["Vertical","Cuenta","Ceco","Fecha","Monto PA","Monto Base","Diferencia","Motivo"]
    cw = mw//len(cols)
    d = ImageDraw.Draw(img)
    for i, c in enumerate(cols):
        d.text((mx0+5+i*cw, ty0+11), c, font=font(7, bold=True), fill=(*WHITE,225))


# ═════════════════════════════════════════════════════════════════════════════
# ÍNDICE / PORTADA PREMIUM
# ═════════════════════════════════════════════════════════════════════════════
def page_indice():
    img = Image.new("RGBA", (W,H), (*NAVY,255))
    draw = ImageDraw.Draw(img)

    lw = int(W * 0.44)   # ancho del panel izquierdo de portada

    # Gradiente panel izquierdo
    grad_v(draw, 0, 0, lw, H,
           lerp(NAVY2, NAVY, 0.2),
           lerp(NAVY, (8,14,42), 0.9))

    # Textura diagonal
    for off in range(-H, W, 50):
        draw.line([(off,0),(off+H,H)], fill=(*BLUE_DARK,8), width=1)

    # Shape orgánico — blob principal esquina inf-der del panel
    for r, alpha in [(280,16),(215,13),(155,10),(100,8),(58,6)]:
        L = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(L).ellipse(
            [lw-r, H-r, lw+r, H+r], fill=(*BLUE, alpha))
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(4)))

    # Línea divisoria brillante
    glow_line(img, lw, 0, lw, H, BLUE_LIGHT, w=2, spread=20)

    draw = ImageDraw.Draw(img)

    # ── Textos del panel izquierdo ────────────────────────────────────────────
    draw.text((48, 52), "GRUPO IHSA  ·  OPERACIONES COMPLEJAS",
              font=font(9), fill=(*BLUE_LIGHT,155))
    glow_line(img, 48, 72, 355, 72, GOLD, w=1, spread=6)
    draw = ImageDraw.Draw(img)
    draw.text((48,  82), "Real vs",     font=font(22, bold=True), fill=(*WHITE,165))
    draw.text((48, 115), "Presupuesto", font=font(44, bold=True), fill=(*WHITE,255))

    # Línea decorativa bajo título
    glow_line(img, 48, 218, 320, 218, BLUE_LIGHT, w=1, spread=8)
    draw = ImageDraw.Draw(img)
    draw.text((48, 228), "Panel de control presupuestario",
              font=font(11), fill=(*WHITE,145))
    draw.text((48, 248), "Período 2025 – 2026  ·  Operaciones Complejas",
              font=font(9), fill=(*BLUE_LIGHT,115))

    # ── AMBULANCIA en portada ─────────────────────────────────────────────────
    amb_zone_w = lw + 50
    amb_zone_h = H - 258
    amb = get_ambulancia(amb_zone_w, amb_zone_h, extend_right=100)
    if amb:
        aw, ah = amb.size
        paste_x = -15
        paste_y = H - ah - 10
        if paste_y < 258:
            crop_top = 258 - paste_y
            amb = amb.crop((0, crop_top, aw, ah))
            paste_y = 258
            ah = amb.height
        img.alpha_composite(amb, (paste_x, paste_y))

        # Fade superior (blend con títulos/texto del panel)
        for i in range(80):
            a = int(240 * (1 - i/80)**2.2)
            ImageDraw.Draw(img).rectangle(
                [0, paste_y+i, lw+15, paste_y+i+1], fill=(*NAVY, a))

        # Fade inferior
        for i in range(45):
            a = int(250 * ((45-i)/45)**1.5)
            ImageDraw.Draw(img).rectangle(
                [0, H-45+i, lw+15, H-44+i], fill=(*NAVY, a))
    else:
        draw = ImageDraw.Draw(img)
        draw.text((48, H//2+30), "[ ambulancia_ihsa.png ]",
                  font=font(9), fill=(*BLUE_LIGHT,60))

    logo(img, 48, H-40, scale=0.85)

    # ── Lado derecho: grid de navegación ─────────────────────────────────────
    rx0 = lw + 28
    rw  = W - rx0 - 25

    draw = ImageDraw.Draw(img)
    draw.text((rx0, 20), "PANEL DE NAVEGACIÓN",
              font=font(13, bold=True), fill=(*TEXT_H,225))
    draw.text((rx0, 42), "Seleccioná la sección que querés analizar",
              font=font(10), fill=(*TEXT_B,185))
    draw.line([(rx0, 64),(W-28, 64)], fill=(*CARD_BORDER,200), width=1)
    glow_line(img, rx0, 64, rx0+170, 64, GOLD, w=1, spread=6)

    botones = [
        ("01","Resumen Ejecutivo",   "KPIs globales · Real vs PA",          BLUE),
        ("02","Análisis Comercial",  "Desvío por vertical de negocio",      BLUE),
        ("03","Vista Operativa",     "Detalle por cuenta y ceco",           BLUE),
        ("04","Detalle Proveedores", "Gasto real · Base SAP transaccional", BLUE),
        ("05","Entregable OPEX",     "Clasificación CAPEX/OPEX · CO/GT",    lerp(BLUE,GOLD,0.3)),
        ("06","Auditoría Interna",   "Controles y validaciones de datos",   lerp(BLUE_DARK,RED,0.45)),
    ]

    bw = rw//2 - 6
    bh = (H-80)//3 - 8

    for i, (num, lbl, desc, acc) in enumerate(botones):
        col, row = i%2, i//2
        bx = rx0 + col*(bw+10)
        by = 72 + row*(bh+8)

        shadow(img, bx,by,bx+bw,by+bh, r=12, offset=3, blur=10)

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
        draw.text((bx+bw-40, by+bh//2-18), num, font=font(32,bold=True),
                  fill=(*acc,13))
        draw.text((bx+14, by+13), lbl,  font=font(11, bold=True), fill=(*TEXT_H,235))
        draw.text((bx+14, by+32), desc, font=font(9),             fill=(*TEXT_B,175))
        draw.text((bx+bw-22, by+bh//2-9), "›", font=font(20),    fill=(*acc,165))

    path = f"{OUT}/fondo_00_indice.png"
    img.save(path, "PNG")
    print(f"  ✓  {path}")


# ── Generador genérico ────────────────────────────────────────────────────────
def make(slug, titulo, subtitulo, badge, layout_fn, page_lbl, dark=False):
    img = Image.new("RGBA", (W,H), (*CONTENT_BG,255))
    build_panel(img, page_lbl)
    build_content(img, titulo, subtitulo, badge, dark)
    layout_fn(img)
    p = f"{OUT}/fondo_{slug}.png"
    img.save(p, "PNG")
    print(f"  ✓  {p}")


# ── Tema JSON ─────────────────────────────────────────────────────────────────
def tema_json():
    import json
    t = {
        "name": "GrupoIHSA_v6",
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
                "border":     [{"show":True,"color":{"solid":{"color":"#3267B8"}},"radius":12}],
                "calloutValue": [{"fontSize":22,"fontBold":True,
                                  "color":{"solid":{"color":"#12204A"}}}],
                "label": [{"fontSize":9,"color":{"solid":{"color":"#5A73A0"}}}]
            }},
            "slicer": {"*": {
                "background": [{"color":{"solid":{"color":"#121840"}}}],
                "border":     [{"show":False}],
                "header":     [{"fontColor":{"solid":{"color":"#FFFFFF"}},
                                "background":{"solid":{"color":"#173773"}}}],
                "items":      [{"fontColor":{"solid":{"color":"#C8D8F0"}}}]
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
    p = f"{OUT}/tema_GrupoIHSA_v6.json"
    with open(p,"w",encoding="utf-8") as f:
        json.dump(t,f,indent=2,ensure_ascii=False)
    print(f"  ✓  {p}")


# ── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if os.path.exists(AMB):
        print(f"\n  ✦  Ambulancia: {AMB}")
    else:
        print(f"\n  ⚠  Sin ambulancia — usando placeholder")

    print("\n── IHSA Premium v6 ─────────────────────────────────────")
    page_indice()
    make("01_resumen",     "Resumen Ejecutivo",
         "Real vs Presupuesto  ·  Operaciones Complejas  ·  2025–2026",
         "GLOBAL",     layout_resumen,              "Resumen Ejecutivo")
    make("02_comercial",   "Análisis Comercial",
         "Desvío presupuestario por vertical de negocio",
         "COMERCIAL",  layout_comercial,             "Comercial")
    make("03_operativa",   "Vista Operativa",
         "Detalle por cuenta contable y centro de costos",
         "OPERATIVA",  lambda i: layout_table(i,3),  "Operativa")
    make("04_proveedores", "Detalle de Proveedores",
         "Gasto real por proveedor  ·  Base SAP transaccional",
         "PROVEEDORES",lambda i: layout_table(i,3),  "Proveedores")
    make("05_opex",        "Entregable OPEX",
         "Clasificación operativa  ·  CAPEX / OPEX  ·  CO / GT",
         "OPEX",       lambda i: layout_table(i,2),  "Entregable OPEX")
    make("06_auditoria",   "Auditoría — Controles y Validaciones",
         "Conciliación entre fuentes  ·  Uso interno  ·  Equipo de datos",
         "AUDITORÍA",  layout_auditoria,             "Auditoría", dark=True)

    print("\n── Tema ─────────────────────────────────────────────────")
    tema_json()
    print("\n── Archivos ─────────────────────────────────────────────")
    for f in sorted(os.listdir(OUT)):
        print(f"   {f:<48} {os.path.getsize(f'{OUT}/{f}')//1024:>4} KB")
