#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera fondos PNG para el dashboard RealVsPAA con identidad visual Grupo IHSA.
Resolución: 1280 x 720 px (16:9, estándar Power BI Desktop)
"""

from PIL import Image, ImageDraw, ImageFont
import os, math

OUT = "/home/user/General/assets_ihsa"
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720           # Canvas Power BI
PANEL_W = 260              # Ancho panel lateral izquierdo
HEADER_H = 58              # Alto del header en páginas de contenido

# ── Paleta Grupo IHSA ────────────────────────────────────────────────────────
AZUL       = (50, 103, 184)      # #3267B8 — azul corporativo principal
AZUL_OSC   = (32,  72, 140)      # #20488C — azul oscuro para sombras/contraste
AZUL_CLARO = (82, 140, 210)      # #528CD2 — azul claro para acentos
BLANCO     = (255, 255, 255)
GRIS_CLARO = (245, 247, 251)     # fondo área de contenido
GRIS_MED   = (220, 228, 240)     # líneas separadoras
GRIS_TEXT  = (100, 110, 130)     # texto secundario
NEGRO      = (30,  35,  45)      # texto principal

def rgba(rgb, a=255):
    return (*rgb, a)

def draw_rounded_rect(draw, xy, radius, fill, outline=None):
    x0,y0,x1,y1 = xy
    draw.rounded_rectangle([x0,y0,x1,y1], radius=radius, fill=fill, outline=outline)

def draw_logo(draw, x, y, size=1.0, dark=False):
    """Dibuja el logotipo simplificado GRUPO IHSA."""
    color = BLANCO if not dark else AZUL
    try:
        fnt_grupo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(11*size))
        fnt_ihsa  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(28*size))
    except:
        fnt_grupo = ImageFont.load_default()
        fnt_ihsa  = fnt_grupo
    draw.text((x, y),       "GRUPO", font=fnt_grupo, fill=color)
    draw.text((x, y+13*size), "IHSA",  font=fnt_ihsa,  fill=color)

def draw_separator(draw, y, x0=PANEL_W+20, x1=W-20, color=GRIS_MED):
    draw.line([(x0, y), (x1, y)], fill=color, width=1)

# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE A — Panel lateral azul + área contenido blanca
# Usado en: Resumen Ejecutivo, Comercial, Operativa, Detalle Proveedores
# ─────────────────────────────────────────────────────────────────────────────
def template_A(nombre_pagina, titulo, subtitulo=""):
    img  = Image.new("RGBA", (W, H), (*GRIS_CLARO, 255))
    draw = ImageDraw.Draw(img)

    # ── Panel lateral izquierdo ──
    draw.rectangle([0, 0, PANEL_W, H], fill=(*AZUL, 255))

    # Forma curva orgánica en esquina inferior derecha del panel
    # (semicírculo blanco que "muerde" el panel, estilo IHSA Slide 1)
    r = 110
    draw.ellipse([PANEL_W-r, H-r*2, PANEL_W+r, H], fill=(*GRIS_CLARO, 255))

    # Línea de acento en borde derecho del panel
    draw.rectangle([PANEL_W, 0, PANEL_W+3, H], fill=(*AZUL_CLARO, 255))

    # Logo en panel lateral
    draw_logo(draw, 22, H-150, size=1.3)

    # ── Área de contenido (derecha) ──
    # Header strip
    draw.rectangle([PANEL_W+3, 0, W, HEADER_H], fill=(*BLANCO, 255))
    draw_separator(draw, HEADER_H, PANEL_W+20, W-20, GRIS_MED)

    # Logo pequeño arriba a la derecha
    draw_logo(draw, W-85, 8, size=0.75, dark=True)

    # Título de la página
    try:
        fnt_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        fnt_sub    = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except:
        fnt_titulo = ImageFont.load_default()
        fnt_sub    = fnt_titulo

    draw.text((PANEL_W+20, 12), titulo,    font=fnt_titulo, fill=NEGRO)
    if subtitulo:
        draw.text((PANEL_W+20, 37), subtitulo, font=fnt_sub,    fill=GRIS_TEXT)

    # Área zona segmentadores (dentro del panel lateral)
    # Etiquetas de segmentadores
    try:
        fnt_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
    except:
        fnt_label = ImageFont.load_default()

    labels = ["Período", "Vertical", "Cuenta", "Ceco"]
    sy = 80
    for lbl in labels:
        draw.text((18, sy), lbl.upper(), font=fnt_label, fill=(*GRIS_MED, 220))
        # Placeholder segmentador (rectángulo redondeado semitransparente)
        draw_rounded_rect(draw, [12, sy+12, PANEL_W-12, sy+34], 4,
                          fill=(*AZUL_OSC, 180), outline=(*AZUL_CLARO, 100))
        sy += 56

    # Franja inferior decorativa
    draw.rectangle([PANEL_W+3, H-28, W, H], fill=(*AZUL, 40))
    draw.line([(PANEL_W+3, H-28), (W, H-28)], fill=(*AZUL_CLARO, 180), width=1)

    # Nombre de página en panel (esquina superior)
    try:
        fnt_pag = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    except:
        fnt_pag = ImageFont.load_default()
    draw.text((18, 18), nombre_pagina.upper(), font=fnt_pag, fill=(*BLANCO, 200))

    path = f"{OUT}/fondo_{nombre_pagina.replace(' ','_').lower()}.png"
    img.save(path, "PNG")
    print(f"  ✓ {path}")
    return path

# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE B — Índice / Portada
# Estilo Slide 1 IHSA: panel azul dominante izquierda, blob blanco
# ─────────────────────────────────────────────────────────────────────────────
def template_B_indice():
    img  = Image.new("RGBA", (W, H), (*BLANCO, 255))
    draw = ImageDraw.Draw(img)

    # Fondo azul completo lado izquierdo (55% del ancho)
    panel_w2 = int(W * 0.55)
    draw.rectangle([0, 0, panel_w2, H], fill=(*AZUL, 255))

    # Blob/forma orgánica blanca en esquina inferior derecha del panel azul
    # Simula el semicírculo del Slide 1
    r2 = 200
    draw.ellipse([panel_w2 - r2, H - r2*1.8, panel_w2 + r2, H+50],
                 fill=(*BLANCO, 255))

    # Franja de acento azul claro
    draw.rectangle([panel_w2, 0, panel_w2+4, H], fill=(*AZUL_CLARO, 255))

    # Logo grande en área blanca del panel
    draw_logo(draw, panel_w2 - 160, H - 210, size=2.5)

    # Título del dashboard en área blanca izquierda (zona blob)
    try:
        fnt_t = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        fnt_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except:
        fnt_t = ImageFont.load_default()
        fnt_s = fnt_t

    draw.text((panel_w2-190, H-130), "Real vs Presupuesto", font=fnt_t, fill=AZUL)
    draw.text((panel_w2-190, H-110), "Operaciones Complejas · 2025-2026", font=fnt_s, fill=GRIS_TEXT)

    # Área derecha: zona de botones de navegación
    # Header pequeño
    draw.rectangle([panel_w2+4, 0, W, 55], fill=(*BLANCO, 255))
    draw_separator(draw, 55, panel_w2+20, W-20)
    draw_logo(draw, W-85, 8, size=0.75, dark=True)

    # Título "Navegación"
    draw.text((panel_w2+30, 15), "PANEL DE NAVEGACIÓN", font=fnt_t, fill=NEGRO)
    draw.text((panel_w2+30, 36), "Seleccioná la sección que querés analizar", font=fnt_s, fill=GRIS_TEXT)

    # Placeholders para botones de navegación (6 botones)
    botones = [
        "1. Resumen Ejecutivo",
        "2. Comercial",
        "3. Operativa",
        "4. Detalle de Proveedores",
        "5. Entregable Opex",
        "6. Auditoría (interno)",
    ]
    bx0 = panel_w2 + 25
    by  = 80
    bw  = (W - panel_w2 - 50) // 2 - 10
    bh  = 68
    gap = 12

    try:
        fnt_btn = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    except:
        fnt_btn = ImageFont.load_default()

    for i, btn in enumerate(botones):
        col = i % 2
        row = i // 2
        bx = bx0 + col * (bw + gap + 10)
        by2 = by + row * (bh + gap)
        # Fondo del botón
        draw_rounded_rect(draw, [bx, by2, bx+bw, by2+bh], 8,
                          fill=(*AZUL, 255), outline=None)
        # Número
        draw.text((bx+12, by2+10), str(i+1), font=fnt_btn,
                  fill=(*AZUL_CLARO, 255))
        # Texto
        try:
            fnt_btn2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        except:
            fnt_btn2 = fnt_btn
        # Mostrar solo la parte del nombre sin número
        label = btn.split(". ", 1)[1] if ". " in btn else btn
        draw.text((bx+12, by2+28), label, font=fnt_btn2, fill=(*BLANCO, 220))

    path = f"{OUT}/fondo_00_indice.png"
    img.save(path, "PNG")
    print(f"  ✓ {path}")
    return path

# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE C — Auditoría (interno)
# Estilo diferenciado: header azul oscuro, señal visual de "uso interno"
# ─────────────────────────────────────────────────────────────────────────────
def template_C_auditoria():
    img  = Image.new("RGBA", (W, H), (*GRIS_CLARO, 255))
    draw = ImageDraw.Draw(img)

    # Panel lateral más delgado, azul oscuro
    panel_w3 = 200
    draw.rectangle([0, 0, panel_w3, H], fill=(*AZUL_OSC, 255))

    # Forma orgánica inferior
    r3 = 90
    draw.ellipse([panel_w3-r3, H-r3*2, panel_w3+r3, H],
                 fill=(*GRIS_CLARO, 255))

    # Acento lateral
    draw.rectangle([panel_w3, 0, panel_w3+3, H], fill=(*AZUL, 255))

    # Header área de contenido
    draw.rectangle([panel_w3+3, 0, W, HEADER_H], fill=(*AZUL_OSC, 255))
    draw_separator(draw, HEADER_H, panel_w3+3, W, (*AZUL_CLARO, 100))

    # Logo en header
    draw_logo(draw, W-85, 8, size=0.75)

    try:
        fnt_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        fnt_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        fnt_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 9)
    except:
        fnt_h = ImageFont.load_default()
        fnt_s = fnt_h
        fnt_b = fnt_h

    draw.text((panel_w3+20, 12), "Auditoría — Controles y Validaciones", font=fnt_h, fill=BLANCO)
    draw.text((panel_w3+20, 37), "Uso interno  ·  Conciliación entre fuentes de datos", font=fnt_s, fill=(*GRIS_MED, 200))

    # Badge "INTERNO" en header
    draw_rounded_rect(draw, [W-220, 14, W-130, 34], 4,
                      fill=(*AZUL_CLARO, 80))
    draw.text((W-215, 18), "USO INTERNO", font=fnt_b, fill=(*GRIS_MED, 220))

    # Logo en panel lateral
    draw_logo(draw, 18, H-140, size=1.1)

    # Labels panel
    try:
        fnt_l = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
    except:
        fnt_l = ImageFont.load_default()

    for i, lbl in enumerate(["Período", "Vertical"]):
        sy = 80 + i * 60
        draw.text((15, sy), lbl.upper(), font=fnt_l, fill=(*GRIS_MED, 200))
        draw_rounded_rect(draw, [10, sy+12, panel_w3-10, sy+32], 4,
                          fill=(*AZUL, 150))

    # Franja inferior
    draw.rectangle([panel_w3+3, H-24, W, H], fill=(*AZUL_OSC, 40))

    path = f"{OUT}/fondo_06_auditoria.png"
    img.save(path, "PNG")
    print(f"  ✓ {path}")
    return path

# ─────────────────────────────────────────────────────────────────────────────
# TEMA JSON Power BI — Grupo IHSA
# ─────────────────────────────────────────────────────────────────────────────
def generar_tema_json():
    import json
    tema = {
        "name": "GrupoIHSA",
        "dataColors": [
            "#3267B8",  # azul principal
            "#528CD2",  # azul claro
            "#20488C",  # azul oscuro
            "#7AADDF",  # azul muy claro
            "#1A3560",  # azul noche
            "#A8C8EE",  # azul pálido
            "#C00000",  # rojo alerta
            "#1F7A1F",  # verde positivo
        ],
        "background": "#F5F7FB",
        "foreground": "#3267B8",
        "tableAccent": "#3267B8",
        "visualStyles": {
            "*": {
                "*": {
                    "fontFamily": [{"value": "Segoe UI"}],
                    "fontSize": [{"value": 10}]
                }
            },
            "card": {
                "*": {
                    "background": [{"color": {"solid": {"color": "#FFFFFF"}}}],
                    "border": [{"show": True, "color": {"solid": {"color": "#3267B8"}}, "radius": 8}],
                    "calloutValue": [{"fontSize": 20, "fontBold": True, "color": {"solid": {"color": "#3267B8"}}}],
                    "label": [{"fontSize": 9, "color": {"solid": {"color": "#6478A8"}}}]
                }
            },
            "slicer": {
                "*": {
                    "background": [{"color": {"solid": {"color": "#20488C"}}}],
                    "border": [{"show": False}],
                    "header": [{"fontColor": {"solid": {"color": "#FFFFFF"}}, "background": {"solid": {"color": "#3267B8"}}}],
                    "items": [{"fontColor": {"solid": {"color": "#FFFFFF"}}}]
                }
            },
            "tableEx": {
                "*": {
                    "header": [{"fontColor": {"solid": {"color": "#FFFFFF"}}, "background": {"solid": {"color": "#3267B8"}}}],
                    "rowHeaders": [{"fontColor": {"solid": {"color": "#1E2D4A"}}}],
                    "grid": [{"gridVertical": False, "rowPadding": 4}]
                }
            },
            "matrix": {
                "*": {
                    "header": [{"fontColor": {"solid": {"color": "#FFFFFF"}}, "background": {"solid": {"color": "#3267B8"}}}]
                }
            },
            "lineChart": {
                "*": {
                    "lineWidth": [{"value": 2}],
                    "markerSize": [{"value": 5}]
                }
            },
            "barChart": {
                "*": {
                    "dataPoint": [{"defaultColor": {"solid": {"color": "#3267B8"}}}]
                }
            }
        },
        "good": "#1F7A1F",
        "neutral": "#528CD2",
        "bad": "#C00000",
        "maximum": "#3267B8",
        "center": "#7AADDF",
        "minimum": "#A8C8EE",
        "null": "#D9D9D9"
    }
    path = f"{OUT}/tema_GrupoIHSA.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tema, f, indent=2, ensure_ascii=False)
    print(f"  ✓ {path}")
    return path

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n── Generando fondos IHSA ────────────────────────────────")
    template_B_indice()
    template_A("01_resumen", "Resumen Ejecutivo", "Real vs Presupuesto · Operaciones Complejas")
    template_A("02_comercial", "Análisis Comercial", "Desvío presupuestario por Vertical de negocio")
    template_A("03_operativa", "Vista Operativa", "Detalle por Cuenta y Centro de Costos")
    template_A("04_proveedores", "Detalle de Proveedores", "Gasto real por proveedor · Base SAP")
    template_A("05_entregable_opex", "Entregable OPEX", "Resumen operativo mensual")
    template_C_auditoria()

    print("\n── Generando tema Power BI ──────────────────────────────")
    generar_tema_json()

    print("\n── Assets generados en:", OUT, "────────────────────────")
    import os
    for f in sorted(os.listdir(OUT)):
        size = os.path.getsize(f"{OUT}/{f}") // 1024
        print(f"   {f}  ({size} KB)")
