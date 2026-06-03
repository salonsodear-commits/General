#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grupo IHSA — Dashboard Premium v8
Base: v2 (dark mode, glassmorphism, geometría premium)
Ambulancia: recorte por flood-fill (Magic Wand) desde esquinas → separa
el fondo blanco del cuerpo blanco del vehículo con precisión Photoshop-level.
Resultado: el vehículo conserva sus colores corporativos exactos (blanco,
naranja, rojo checkerboard, azul IHSA) sobre el fondo navy del panel.
"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import numpy as np
import math, os, json
from collections import deque

OUT = "/home/user/General/assets_ihsa_v8"
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
C_RED_SOFT  = (220,  70,  70)
C_PANEL_BG  = ( 18,  28,  65)
C_CARD_BG   = ( 22,  38,  85)
C_CONTENT   = ( 14,  22,  52)

PANEL_W  = 245
HEADER_H = 62


# ═════════════════════════════════════════════════════════════════════════════
# RECORTE PREMIUM: FLOOD-FILL DESDE ESQUINAS (Magic Wand)
# ═════════════════════════════════════════════════════════════════════════════
def flood_fill_bg(arr_rgb, seeds, tolerance=22):
    """
    BFS desde los seeds (esquinas del fondo).
    Marca como fondo todos los píxeles adyacentes cuyo color
    difiere menos de `tolerance` del color del seed de origen.
    Devuelve máscara booleana: True = fondo.
    """
    h, w = arr_rgb.shape[:2]
    visited = np.zeros((h, w), dtype=bool)
    queue   = deque()

    for sy, sx in seeds:
        if not visited[sy, sx]:
            visited[sy, sx] = True
            queue.append((sy, sx, arr_rgb[sy, sx].astype(np.int32)))

    while queue:
        y, x, ref_color = queue.popleft()
        for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
            ny, nx = y+dy, x+dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                pix = arr_rgb[ny, nx].astype(np.int32)
                dist = np.sqrt(np.sum((pix - ref_color)**2))
                if dist < tolerance:
                    visited[ny, nx] = True
                    queue.append((ny, nx, pix))
    return visited


def remove_bg_floodfill(path, tolerance=20, feather=2.5):
    """
    Carga la imagen y remueve el fondo usando flood-fill BFS desde
    las 4 esquinas + bordes. Conserva el vehículo intacto (incluso
    las partes blancas del cuerpo) porque el flood-fill se detiene
    en los bordes/sombras del vehículo.
    """
    src  = Image.open(path).convert("RGBA")
    arr  = np.array(src)
    rgb  = arr[:,:,:3]
    h, w = rgb.shape[:2]

    # Seeds: píxeles de las esquinas y bordes del canvas (zona de fondo segura)
    seeds = []
    margin = 6
    for y in range(0, h, 4):
        seeds += [(y, 0), (y, w-1)]
    for x in range(0, w, 4):
        seeds += [(0, x), (h-1, x)]
    # Esquinas explícitas
    for cy in [0, h//4, h//2, 3*h//4, h-1]:
        for cx in [0, w//4, 3*w//4, w-1]:
            seeds.append((cy, cx))

    bg_mask = flood_fill_bg(rgb, seeds, tolerance=tolerance)

    # Construir alpha: fondo=0, vehículo=255
    alpha = np.where(bg_mask, 0, 255).astype(np.uint8)

    # Suavizado de borde (feather) para anti-aliasing natural
    alpha_img = Image.fromarray(alpha, "L")
    if feather > 0:
        alpha_img = alpha_img.filter(ImageFilter.GaussianBlur(feather))
        # Re-binarizar ligeramente para evitar halos grises
        alpha_arr = np.array(alpha_img, dtype=np.float32)
        alpha_arr = np.clip((alpha_arr - 40) * 1.35, 0, 255)
        alpha_img = Image.fromarray(alpha_arr.astype(np.uint8), "L")

    result = src.copy()
    result.putalpha(alpha_img)
    return result


# ── Caché de ambulancia procesada ─────────────────────────────────────────────
_AMB_CACHE = {}

def get_ambulancia(target_h, flip=False):
    """
    Devuelve la ambulancia recortada, escalada y lista para compositar.
    Aplica sombra de suelo, glow corporativo sutil y fades de borde.
    """
    key = (target_h, flip)
    if key in _AMB_CACHE:
        return _AMB_CACHE[key]

    if not os.path.exists(AMB):
        _AMB_CACHE[key] = None
        return None

    # 1. Recorte flood-fill
    veh = remove_bg_floodfill(AMB, tolerance=20, feather=2.2)

    # 2. Crop al bbox del vehículo (sin márgenes transparentes)
    alpha_arr = np.array(veh)[:,:,3]
    ys, xs = np.where(alpha_arr > 15)
    pad = 12
    x0 = max(0, int(xs.min()) - pad)
    y0 = max(0, int(ys.min()) - pad)
    x1 = min(veh.width,  int(xs.max()) + pad)
    y1 = min(veh.height, int(ys.max()) + pad)
    veh = veh.crop((x0, y0, x1, y1))

    if flip:
        veh = veh.transpose(Image.FLIP_LEFT_RIGHT)

    # 3. Escalar por altura → vehículo llena la zona
    vw, vh = veh.size
    scale  = (target_h * 1.06) / vh
    new_w  = int(vw * scale)
    new_h  = int(vh * scale)
    veh = veh.resize((new_w, new_h), Image.LANCZOS)

    # 4. Sombra de suelo (ground shadow) — efecto premium
    sh_layer = Image.new("RGBA", (new_w, new_h + 30), (0,0,0,0))
    veh_arr  = np.array(veh)
    alpha_col = veh_arr[:,:,3].astype(np.float32)
    # Proyectar la silueta inferior hacia abajo con ellipse
    bottom_row = alpha_col[-1, :]
    shadow_w = int(new_w * 0.85)
    shadow_x = (new_w - shadow_w) // 2
    shadow_y = new_h + 8
    for i in range(18):
        a = int(120 * (1 - i/18)**2)
        sx0 = shadow_x + i*3
        sx1 = shadow_x + shadow_w - i*3
        sy  = shadow_y + i
        if sx1 > sx0:
            ImageDraw.Draw(sh_layer).ellipse([sx0, sy-4, sx1, sy+4],
                                              fill=(0,0,0,a))
    sh_layer = sh_layer.filter(ImageFilter.GaussianBlur(6))
    # Compositar sombra + vehículo
    base = Image.new("RGBA", (new_w, new_h + 30), (0,0,0,0))
    base.alpha_composite(sh_layer)
    base.alpha_composite(veh, (0, 0))
    veh = base
    new_h = veh.height

    # 5. Glow corporativo azul sutil (rim light desde arriba-derecha)
    glow_layer = Image.new("RGBA", veh.size, (0,0,0,0))
    gw, gh = veh.size
    glow_draw = ImageDraw.Draw(glow_layer)
    # Gradiente radial desde esquina superior-derecha
    for r in range(60, 0, -1):
        a = int(18 * (r/60)**2)
        glow_draw.ellipse([gw-r*2, -r, gw+r, r*2],
                          fill=(*C_BLUE_LT, a))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(18))
    veh.alpha_composite(glow_layer)

    # 6. Fades de borde vectorizados para integrar con el panel
    arr3  = np.array(veh, dtype=np.float32)
    rows, cols = arr3.shape[:2]

    # Superior: fade muy marcado (convive con los slicers)
    ft = min(80, rows//3)
    arr3[:ft, :, 3] *= np.linspace(0, 1, ft)[:, np.newaxis] ** 2.8

    # Inferior: suave (la sombra de suelo ya hace la transición)
    fb = min(35, rows//6)
    arr3[-fb:, :, 3] *= np.linspace(1, 0, fb)[:, np.newaxis] ** 1.5

    # Izquierdo: suave-moderado
    fl = min(28, cols//8)
    arr3[:, :fl, 3] *= np.linspace(0, 1, fl)[np.newaxis, :] ** 2.0

    arr3[:,:,3] = np.clip(arr3[:,:,3], 0, 255)
    veh = Image.fromarray(arr3.astype(np.uint8), "RGBA")

    _AMB_CACHE[key] = veh
    return veh


# ═════════════════════════════════════════════════════════════════════════════
# COMPOSICIÓN EN EL PANEL
# ═════════════════════════════════════════════════════════════════════════════
def composite_amb_panel(img, zone_y0, zone_y1, panel_width=PANEL_W, bg_color=None):
    """
    Compone la ambulancia en la zona del panel entre slicers y logo.
    El vehículo se escala por altura, se alinea a la derecha del panel
    (el frente "entra" desde el panel hacia el dashboard) y se clipea
    con un degradado al borde del panel.
    """
    zone_h = zone_y1 - zone_y0
    veh    = get_ambulancia(zone_h)
    if veh is None:
        return

    vw, vh = veh.size

    # Posicionar: alinear inferior de la zona, el vehículo centrado
    paste_x = max(-15, (panel_width - vw) // 2)
    paste_y = zone_y1 - vh + 15

    # Recortar si sube demasiado
    if paste_y < zone_y0 - 25:
        crop_top = (zone_y0 - 25) - paste_y
        veh = veh.crop((0, crop_top, vw, vh))
        paste_y = zone_y0 - 25
        vw, vh = veh.size

    img.alpha_composite(veh, (paste_x, paste_y))

    # Overlay superior: funde con el fondo del panel sobre el vehículo
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    ft = 75
    for i in range(ft):
        a = int(255 * (1 - i/ft)**3.0)
        d.rectangle([0, paste_y+i, panel_width+40, paste_y+i+1],
                    fill=(*C_PANEL_BG, a))
    img.alpha_composite(L)

    # Clip derecho: el vehículo no pasa del borde del panel
    fill_bg = bg_color if bg_color else C_CONTENT
    clip_x  = panel_width
    L2 = Image.new("RGBA", img.size, (0,0,0,0))
    d2 = ImageDraw.Draw(L2)
    d2.rectangle([clip_x + 32, 0, W, H], fill=(*fill_bg, 255))
    for i in range(32):
        a = int(255 * ((32-i)/32) ** 1.6)
        d2.rectangle([clip_x+i, zone_y0-30, clip_x+i+1, zone_y1+15],
                     fill=(*fill_bg, a))
    img.alpha_composite(L2)

    # Línea de suelo elegante
    glow_line(img, 14, zone_y1 - 6, panel_width - 14, zone_y1 - 6,
              C_BLUE_MID, width=1, blur=4)


# ═════════════════════════════════════════════════════════════════════════════
# HELPERS v2 (idénticos)
# ═════════════════════════════════════════════════════════════════════════════
def px(rgb, a=255): return (*rgb, a)

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def gradient_v(draw, x0, y0, x1, y1, c_top, c_bot, steps=120):
    h_seg = (y1-y0)/steps
    for i in range(steps):
        draw.rectangle([x0, y0+i*h_seg, x1, y0+(i+1)*h_seg+1],
                       fill=(*lerp_color(c_top, c_bot, i/steps), 255))

def gradient_h(draw, x0, y0, x1, y1, c_left, c_right, steps=200):
    w_seg = (x1-x0)/steps
    for i in range(steps):
        draw.rectangle([x0+i*w_seg, y0, x0+(i+1)*w_seg+1, y1],
                       fill=(*lerp_color(c_left, c_right, i/steps), 255))

def glow_line(img, x0, y0, x1, y1, color, width=2, blur=8):
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    for w in range(width+blur, 0, -1):
        a = int(255*(w/(width+blur))**2*0.6)
        d.line([(x0,y0),(x1,y1)], fill=(*color,a), width=w)
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(blur//2)))
    ImageDraw.Draw(img).line([(x0,y0),(x1,y1)], fill=(*color,230), width=width)

def dot_grid(draw, x0, y0, x1, y1, spacing=28, color=C_BLUE_MID, alpha=40):
    for x in range(x0, x1, spacing):
        for y in range(y0, y1, spacing):
            draw.ellipse([x-1,y-1,x+1,y+1], fill=(*color,alpha))

def diagonal_lines(draw, x0, y0, x1, y1, gap=40, color=C_BLUE_MID, alpha=18):
    for off in range(-(y1-y0), (x1-x0), gap):
        sx = x0 + off
        draw.line([(sx,y0),(sx+(y1-y0),y1)], fill=(*color,alpha), width=1)

def hexgrid(draw, cx, cy, radius=60, color=C_BLUE_LT, alpha=25):
    def hex_pts(cx, cy, r):
        return [(cx+r*math.cos(math.radians(60*i-30)),
                 cy+r*math.sin(math.radians(60*i-30))) for i in range(6)]
    draw.polygon(hex_pts(cx,cy,radius), outline=(*color,alpha), fill=None)
    for i in range(6):
        nx = cx + radius*1.73*math.cos(math.radians(60*i))
        ny = cy + radius*1.73*math.sin(math.radians(60*i))
        draw.polygon(hex_pts(nx,ny,radius), outline=(*color,alpha//2), fill=None)

def rounded_rect_aa(img, x0,y0,x1,y1, r, fill_color, alpha=255,
                    outline=None, outline_w=1):
    L = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([x0,y0,x1,y1], radius=r, fill=(*fill_color,alpha))
    if outline:
        d.rounded_rectangle([x0,y0,x1,y1], radius=r,
                             outline=(*outline,200), width=outline_w)
    img.alpha_composite(L)

def glass_panel(img, x0,y0,x1,y1, r=12, tint=C_BLUE_CORP,
                alpha_fill=35, alpha_border=80):
    rounded_rect_aa(img, x0,y0,x1,y1, r, tint, alpha_fill)
    rounded_rect_aa(img, x0,y0,x1,y1, r, C_BLUE_LT, 0,
                    outline=C_BLUE_LT, outline_w=1)
    L = Image.new("RGBA", img.size, (0,0,0,0))
    ImageDraw.Draw(L).rounded_rectangle([x0+1,y0+1,x1-1,y0+r+8],
                                         radius=r, fill=(*C_WHITE,12))
    img.alpha_composite(L)

def get_font(size, bold=False):
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]:
        try: return ImageFont.truetype(p, size)
        except: pass
    return ImageFont.load_default()

def draw_logo(img, x, y, scale=1.0):
    d = ImageDraw.Draw(img)
    lh = int(42*scale)
    d.rectangle([x, y+2, x+3, y+lh], fill=(*C_BLUE_LT,255))
    d.text((x+9, y),               "GRUPO", font=get_font(int(9*scale)), fill=(*C_SILVER,200))
    d.text((x+8, y+int(10*scale)), "IHSA",  font=get_font(int(30*scale),bold=True),
           fill=(*C_OFF_WHITE,255))

def accent_arc(draw, cx, cy, r_out, r_in, start_deg, end_deg, color, alpha=160):
    steps = max(30, end_deg-start_deg)
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


# ═════════════════════════════════════════════════════════════════════════════
# BASE (igual a v2)
# ═════════════════════════════════════════════════════════════════════════════
def build_base():
    img  = Image.new("RGBA", (W,H), px(C_NAVY))
    draw = ImageDraw.Draw(img)
    gradient_v(draw, 0, 0, W, H, C_NAVY, C_NAVY2, steps=150)
    dot_grid(draw, PANEL_W, HEADER_H, W, H, spacing=32, color=C_BLUE_MID, alpha=28)
    hexgrid(draw, W-160, H-130, radius=55, color=C_BLUE_LT, alpha=18)
    hexgrid(draw, W-80,  H-60,  radius=30, color=C_BLUE_LT, alpha=12)
    gradient_h(draw, 0, 0, PANEL_W, H, C_NAVY2, C_PANEL_BG, steps=60)
    diagonal_lines(draw, 0, 0, PANEL_W, H, gap=35, color=C_BLUE_CORP, alpha=14)
    accent_arc(draw, PANEL_W-10, H+30, 180, 120, 150, 210, C_BLUE_CORP, alpha=55)
    accent_arc(draw, PANEL_W-10, H+30, 120,  85, 150, 210, C_BLUE_LT,  alpha=40)
    glow_line(img, PANEL_W, 0, PANEL_W, H, C_BLUE_LT, width=1, blur=10)
    gradient_h(draw, PANEL_W, 0, W, HEADER_H, C_NAVY2, C_PANEL_BG, steps=80)
    glow_line(img, PANEL_W, HEADER_H, W, HEADER_H, C_BLUE_CORP, width=1, blur=8)
    accent_x = PANEL_W + int((W-PANEL_W)*0.40)
    glow_line(img, PANEL_W, HEADER_H, accent_x, HEADER_H, C_GOLD, width=1, blur=6)
    gradient_h(draw, PANEL_W, H-26, W, H, C_NAVY2, C_PANEL_BG, steps=60)
    glow_line(img, PANEL_W, H-26, W, H-26, C_BLUE_MID, width=1, blur=6)
    return img


# ═════════════════════════════════════════════════════════════════════════════
# TEMPLATE PÁGINAS DE CONTENIDO
# ═════════════════════════════════════════════════════════════════════════════
def template_content(slug, titulo, subtitulo, badge=None):
    img  = build_base()
    draw = ImageDraw.Draw(img)

    # Segmentadores
    labels = [("Período","MesAño"),("Vertical","Negocio"),
              ("Cuenta","Contable"),("Ceco","Centro costos")]
    sy = 72
    for lbl, hint in labels:
        draw.text((18, sy), lbl.upper(), font=get_font(8), fill=(*C_SILVER,160))
        if hint:
            draw.text((18, sy+11), hint, font=get_font(9,bold=True),
                      fill=(*C_OFF_WHITE,120))
        glass_panel(img, 12, sy+14, PANEL_W-12, sy+38, r=6,
                    tint=C_BLUE_CORP, alpha_fill=28)
        draw = ImageDraw.Draw(img)
        draw.polygon([(PANEL_W-28,sy+22),(PANEL_W-20,sy+22),(PANEL_W-24,sy+30)],
                     fill=(*C_BLUE_LT,120))
        sy += 60

    # AMBULANCIA — justo debajo del último slicer, encima del logo
    amb_y0 = sy - 10    # ~302
    amb_y1 = H - 170    # ~550
    composite_amb_panel(img, amb_y0, amb_y1)

    # Logo
    draw_logo(img, 22, H-165, scale=1.15)

    # Header
    draw = ImageDraw.Draw(img)
    draw.text((PANEL_W+22, 10), titulo,    font=get_font(19,bold=True),
              fill=(*C_OFF_WHITE,255))
    draw.text((PANEL_W+22, 36), subtitulo, font=get_font(10),
              fill=(*C_SILVER,180))

    if badge:
        bw = max(80, len(badge)*7+16)
        rounded_rect_aa(img, W-bw-25, 14, W-25, 44, r=5,
                        fill_color=C_BLUE_CORP, alpha=60,
                        outline=C_BLUE_LT, outline_w=1)
        ImageDraw.Draw(img).text((W-bw-18, 22), badge.upper(),
                                  font=get_font(8,bold=True), fill=(*C_CYAN,200))

    draw_logo(img, W-95, 6, scale=0.7)

    # Zonas KPI
    kw = int((W - PANEL_W - 40)/4) - 8
    for i in range(4):
        sx = PANEL_W+20 + i*(kw+8)
        glass_panel(img, sx, HEADER_H+14, sx+kw, HEADER_H+90, r=10,
                    tint=C_CARD_BG, alpha_fill=85)
        glow_line(img, sx+12, HEADER_H+15, sx+kw-12, HEADER_H+15,
                  C_BLUE_LT, width=1, blur=4)

    # Panel gráficos
    mx0  = PANEL_W + 20
    my0  = HEADER_H + 104
    mw_l = int((W-mx0-28)*0.60)
    glass_panel(img, mx0, my0, mx0+mw_l, H-40, r=12, tint=C_CARD_BG, alpha_fill=70)
    glass_panel(img, mx0+mw_l+8, my0, W-20, H-40, r=12, tint=C_CARD_BG, alpha_fill=70)
    draw = ImageDraw.Draw(img)
    dot_grid(draw, mx0+10, my0+10, mx0+mw_l-10, H-50, spacing=40,
             color=C_BLUE_LT, alpha=12)

    img.save(f"{OUT}/fondo_{slug}.png", "PNG")
    print(f"  ✓  fondo_{slug}.png")


# ═════════════════════════════════════════════════════════════════════════════
# TEMPLATE ÍNDICE / PORTADA
# ═════════════════════════════════════════════════════════════════════════════
def template_indice():
    img  = Image.new("RGBA", (W,H), px(C_NAVY))
    draw = ImageDraw.Draw(img)

    gradient_v(draw, 0, 0, W, H, C_NAVY, (8,16,42), steps=160)

    div_x = int(W*0.42)   # 537px

    # Panel izquierdo
    pts = [(0,0),(div_x,0),(int(W*0.32),H),(0,H)]
    L = Image.new("RGBA",(W,H),(0,0,0,0))
    ImageDraw.Draw(L).polygon(pts, fill=(*C_PANEL_BG,255))
    img.alpha_composite(L)
    draw = ImageDraw.Draw(img)
    diagonal_lines(draw, 0, 0, div_x, H, gap=38, color=C_BLUE_CORP, alpha=18)

    # Arcos derecha
    accent_arc(draw, W, H, 400, 300, 140, 200, C_BLUE_CORP, alpha=30)
    accent_arc(draw, W, H, 300, 240, 140, 200, C_BLUE_LT,   alpha=25)
    accent_arc(draw, W, H, 240, 200, 140, 200, C_CYAN,      alpha=18)
    dot_grid(draw, div_x, 0, W, H, spacing=30, color=C_BLUE_MID, alpha=30)
    hexgrid(draw, W-200, H-180, radius=70, color=C_BLUE_LT, alpha=16)

    glow_line(img, div_x, 0, div_x, H, C_BLUE_LT, width=1, blur=14)

    draw = ImageDraw.Draw(img)
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

    # AMBULANCIA en portada — zona grande bajo los textos
    amb_zone_h = H - 270 - 120
    veh_idx = get_ambulancia(amb_zone_h)
    if veh_idx:
        vw, vh = veh_idx.size
        paste_x = -12
        paste_y = H - vh - 105
        if paste_y < 268:
            crop_top = 268 - paste_y
            veh_idx = veh_idx.crop((0, crop_top, vw, vh))
            paste_y = 268
            vw, vh = veh_idx.size
        img.alpha_composite(veh_idx, (paste_x, paste_y))

        # Fades
        L = Image.new("RGBA", img.size, (0,0,0,0))
        d = ImageDraw.Draw(L)
        for i in range(85):
            a = int(255*(1-i/85)**3.2)
            d.rectangle([0, paste_y+i, div_x+50, paste_y+i+1],
                        fill=(*C_PANEL_BG, a))
        img.alpha_composite(L)
        L2 = Image.new("RGBA", img.size, (0,0,0,0))
        d2 = ImageDraw.Draw(L2)
        for i in range(45):
            a = int(250*((45-i)/45)**1.8)
            d2.rectangle([0, H-45+i, div_x+50, H-44+i], fill=(*C_PANEL_BG, a))
        img.alpha_composite(L2)
        # Clip en div_x
        L3 = Image.new("RGBA", img.size, (0,0,0,0))
        d3 = ImageDraw.Draw(L3)
        d3.rectangle([div_x+35, 0, W, H], fill=(*C_CONTENT, 255))
        for i in range(35):
            a = int(255*((35-i)/35)**1.5)
            d3.rectangle([div_x+i, 265, div_x+i+1, H], fill=(*C_CONTENT, a))
        img.alpha_composite(L3)

    draw_logo(img, 48, H-130, scale=1.8)

    # Navegación derecha
    rx0 = div_x + 30
    rw  = W - rx0 - 30
    draw = ImageDraw.Draw(img)
    draw.text((rx0, 24), "SELECCIONÁ UNA SECCIÓN",
              font=get_font(11,bold=True), fill=(*C_OFF_WHITE,200))
    draw.text((rx0, 42), "Panel de navegación rápida",
              font=get_font(9), fill=(*C_SILVER,140))
    glow_line(img, rx0, 62, W-30, 62, C_BLUE_CORP, width=1, blur=6)

    botones = [
        ("01","Resumen Ejecutivo",   "KPIs globales · Real vs PA",      C_BLUE_CORP),
        ("02","Análisis Comercial",  "Desvío por vertical de negocio",  C_BLUE_MID),
        ("03","Vista Operativa",     "Detalle cuenta y ceco",           C_BLUE_MID),
        ("04","Detalle Proveedores", "Gasto real · Base SAP",           C_BLUE_MID),
        ("05","Entregable OPEX",     "Resumen operativo mensual",       C_BLUE_MID),
        ("06","Auditoría Interna",   "Controles y validaciones",        C_NAVY2),
    ]
    bw = rw//2 - 8
    bh = (H-90)//3 - 12

    for i, (num, label, desc, color) in enumerate(botones):
        col, row = i%2, i//2
        bx = rx0 + col*(bw+8)
        by = 76 + row*(bh+10)
        glass_panel(img, bx, by, bx+bw, by+bh, r=10, tint=color,
                    alpha_fill=65, alpha_border=70)
        d2 = ImageDraw.Draw(img)
        d2.text((bx+bw-38, by+6), num, font=get_font(20,bold=True),
                fill=(*C_BLUE_LT,45))
        glass_panel(img, bx, by, bx+4, by+bh, r=4, tint=C_BLUE_LT, alpha_fill=180)
        d2 = ImageDraw.Draw(img)
        d2.text((bx+14, by+14), label, font=get_font(10,bold=True),
                fill=(*C_OFF_WHITE,240))
        d2.text((bx+14, by+32), desc,  font=get_font(8),
                fill=(*C_SILVER,160))
        d2.text((bx+bw-20, by+bh-22), "›", font=get_font(18),
                fill=(*C_BLUE_LT,160))

    img.save(f"{OUT}/fondo_00_indice.png", "PNG")
    print(f"  ✓  fondo_00_indice.png")


# ═════════════════════════════════════════════════════════════════════════════
# TEMPLATE AUDITORÍA
# ═════════════════════════════════════════════════════════════════════════════
def template_auditoria():
    img  = Image.new("RGBA", (W,H), px(C_NAVY))
    draw = ImageDraw.Draw(img)
    PW2  = 200

    gradient_v(draw, 0, 0, W, H, (8,14,35), (12,20,50), steps=150)
    dot_grid(draw, 0, 0, W, H, spacing=28, color=C_BLUE_MID, alpha=22)
    gradient_h(draw, 0, 0, PW2, H, (12,22,58), (8,16,42), steps=50)
    diagonal_lines(draw, 0, 0, PW2, H, gap=30, color=C_BLUE_CORP, alpha=16)
    accent_arc(draw, PW2+10, H+20, 150, 100, 150, 210, C_BLUE_CORP, alpha=40)
    glow_line(img, PW2, 0, PW2, H, C_RED_SOFT, width=1, blur=12)

    gradient_h(draw, PW2, 0, W, HEADER_H, (10,18,48), (15,25,60), steps=80)
    glow_line(img, PW2, HEADER_H, W, HEADER_H, C_RED_SOFT, width=1, blur=8)
    glow_line(img, PW2, HEADER_H, PW2+int((W-PW2)*0.35), HEADER_H, C_GOLD, width=1, blur=5)

    draw = ImageDraw.Draw(img)

    sy = 72
    for lbl, hint in [("Período","MesAño"),("Vertical","Negocio")]:
        draw.text((14, sy), lbl.upper(), font=get_font(8), fill=(*C_SILVER,160))
        glass_panel(img, 10, sy+14, PW2-10, sy+38, r=6, tint=C_BLUE_CORP, alpha_fill=30)
        sy += 60

    # Ambulancia en auditoría (panel angosto 200px)
    composite_amb_panel(img, sy-5, H-135, panel_width=PW2, bg_color=(8,14,35))

    draw_logo(img, 16, H-130, scale=1.0)

    draw = ImageDraw.Draw(img)
    draw.text((PW2+20, 12), "Auditoría — Controles y Validaciones",
              font=get_font(17,bold=True), fill=(*C_OFF_WHITE,255))
    draw.text((PW2+20, 36), "Conciliación entre fuentes · Uso interno · Equipo de datos",
              font=get_font(9), fill=(*C_SILVER,170))

    glass_panel(img, W-145, 13, W-20, 40, r=5, tint=(180,40,40), alpha_fill=50)
    ImageDraw.Draw(img).text((W-138,20), "⚠  USO INTERNO",
                              font=get_font(8,bold=True), fill=(*C_RED_SOFT,220))
    draw_logo(img, W-95, 6, scale=0.68)

    cy0 = HEADER_H + 14
    sw2 = int((W-PW2-28)/3) - 6
    for i in range(3):
        sx = PW2+20 + i*(sw2+8)
        glass_panel(img, sx, cy0, sx+sw2, cy0+72, r=8, tint=C_CARD_BG, alpha_fill=80)
        glow_line(img, sx+10, cy0+1, sx+sw2-10, cy0+1, C_RED_SOFT, width=1, blur=4)

    glass_panel(img, PW2+20, cy0+86, W-20, H-36, r=10, tint=C_CARD_BG, alpha_fill=75)
    glow_line(img, PW2+20, cy0+86, W-20, cy0+86, C_BLUE_CORP, width=1, blur=6)

    draw = ImageDraw.Draw(img)
    gradient_h(draw, PW2, H-24, W, H, (10,18,48), (15,25,60), steps=60)
    glow_line(img, PW2, H-24, W, H-24, C_BLUE_MID, width=1, blur=5)

    img.save(f"{OUT}/fondo_06_auditoria.png", "PNG")
    print(f"  ✓  fondo_06_auditoria.png")


# ═════════════════════════════════════════════════════════════════════════════
# TEMA JSON v8 — GrupoIHSA actualizado
# ═════════════════════════════════════════════════════════════════════════════
def generar_tema():
    tema = {
        "name": "GrupoIHSA_Premium",
        "dataColors": [
            "#5294DA",  # azul IHSA claro — principal
            "#3267B8",  # azul IHSA corporativo
            "#7CC4E8",  # azul cielo
            "#20488C",  # azul oscuro
            "#D2AF50",  # dorado IHSA
            "#20B2AA",  # teal positivo
            "#DC4646",  # rojo alerta
            "#A8C8EE"   # azul pálido
        ],
        "background":  "#0A1432",
        "foreground":  "#5294DA",
        "tableAccent": "#3267B8",
        "visualStyles": {
            "*": {"*": {
                "fontFamily": [{"value": "Segoe UI"}],
                "fontSize":   [{"value": 10}],
                "background": [{"color": {"solid": {"color": "#16265580"}}}]
            }},
            "card": {"*": {
                "background":   [{"color": {"solid": {"color": "#162655"}}}],
                "border":       [{"show": True,
                                  "color": {"solid": {"color": "#3267B8"}},
                                  "radius": 10}],
                "calloutValue": [{"fontSize": 22, "fontBold": True,
                                  "color": {"solid": {"color": "#E6EEFA"}}}],
                "label":        [{"fontSize": 9,
                                  "color": {"solid": {"color": "#8AABD4"}}}]
            }},
            "slicer": {"*": {
                "background": [{"color": {"solid": {"color": "#0F1E48"}}}],
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
                "header":    [{"fontColor": {"solid": {"color": "#FFFFFF"}},
                               "background": {"solid": {"color": "#3267B8"}}}],
                "values":    [{"fontColor": {"solid": {"color": "#E6EEFA"}}}],
                "subTotals": [{"fontColor": {"solid": {"color": "#5294DA"}},
                               "background": {"solid": {"color": "#0F1E48"}}}]
            }},
            "lineChart": {"*": {
                "lineWidth":  [{"value": 2}],
                "markerSize": [{"value": 5}],
                "dataPoint":  [{"defaultColor": {"solid": {"color": "#5294DA"}}}]
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
        "neutral": "#5294DA",
        "bad":     "#DC4646",
        "maximum": "#3267B8",
        "center":  "#7CC4E8",
        "minimum": "#20488C",
        "null":    "#2A3A6A"
    }
    p = f"{OUT}/tema_GrupoIHSA_Premium.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(tema, f, indent=2, ensure_ascii=False)
    print(f"  ✓  tema_GrupoIHSA_Premium.json")
    return tema


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n  ✦  Ambulancia: {AMB}")
    print(f"  ✦  Técnica: flood-fill BFS desde esquinas (Magic Wand)\n")
    print("── IHSA Premium v8 ─────────────────────────────────────")

    template_indice()
    template_content("01_resumen",    "Resumen Ejecutivo",
                     "Real vs Presupuesto  ·  Operaciones Complejas  ·  2025–2026",
                     "GLOBAL")
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
        print(f"   {f:<50} {kb:>4} KB")
