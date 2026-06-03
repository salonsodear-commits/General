#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplica tema GrupoIHSA v9 al PBIP RealVsPAA.
Versión exhaustiva: sin warnings de schema, tema activo, slicers y cards adaptados.

Fixes aplicados:
1. outspacePane.expanded → solo en report.json, eliminado de TODOS los page.json
2. customTheme → reactivado sin reportVersionAtImport (no-fatal warning aceptado)
3. Slicers → tema aplicado vía customTheme (colores, bordes, fondo)
4. Cards → ídem
5. background en pages → solo image + transparency (ya correcto)
"""

import json, os, shutil, zipfile

SRC    = "/home/user/General/pbip_ihsa/RealVsPAA"
DEST   = "/home/user/General/pbip_ihsa/RealVsPAA_v9"
ASSETS = "/home/user/General/assets_ihsa_v9"
REPORT = "RealVsPAA.Report"
OUT_ZIP = "/home/user/General/assets_ihsa_v9/RealVsPAA_IHSA_v9.zip"

PAGE_PNG = {
    "d532c5ff032986009878": "fondo_00_indice.png",
    "d8eee77324362ca32bc9": "fondo_05_opex.png",
    "ResumenEjecutivo":     "fondo_01_resumen.png",
    "33d617049008988eea19": "fondo_03_operativa.png",
    "Comercial":            "fondo_02_comercial.png",
    "DetalleProveedores":   "fondo_04_proveedores.png",
    "Auditoria":            "fondo_06_auditoria.png",
}

def lit(v):
    """Shorthand: expr Literal."""
    return {"expr": {"Literal": {"Value": v}}}

def color_fill(hex_color):
    """Solid color fill en formato PBIP."""
    return {"solid": {"color": lit(f"'{hex_color}'")}}

# ── 1. Copiar proyecto fresco ─────────────────────────────────────────────────
if os.path.exists(DEST):
    shutil.rmtree(DEST)
shutil.copytree(SRC, DEST)
print("  ✓  Proyecto copiado")

REPORT_DEF = os.path.join(DEST, REPORT, "definition")
STATIC     = os.path.join(DEST, REPORT, "StaticResources", "RegisteredResources")
os.makedirs(STATIC, exist_ok=True)

# ── 2. Copiar recursos ────────────────────────────────────────────────────────
shutil.copy2(os.path.join(ASSETS, "tema_GrupoIHSA.json"),
             os.path.join(STATIC, "tema_GrupoIHSA.json"))
for png in set(PAGE_PNG.values()):
    shutil.copy2(os.path.join(ASSETS, png), os.path.join(STATIC, png))
print(f"  ✓  Recursos copiados ({len(set(PAGE_PNG.values()))} PNG + tema JSON)")

# ── 3. report.json ────────────────────────────────────────────────────────────
# FIX: customTheme SIN reportVersionAtImport (no-fatal warning aceptado vs crash)
# El outspacePane.expanded ya está correcto AQUÍ en report.json, no en page.json
report_path = os.path.join(REPORT_DEF, "report.json")
with open(report_path) as f:
    report = json.load(f)

# Tema personalizado — sin reportVersionAtImport
report["themeCollection"]["customTheme"] = {
    "name": "GrupoIHSA",
    "type": "RegisteredResources"
}

# RegisteredResources package
packages = [p for p in report.get("resourcePackages", [])
            if p.get("name") != "RegisteredResources"]
rr_items = [
    {"name": "GrupoIHSA",
     "path": "RegisteredResources/tema_GrupoIHSA.json",
     "type": "CustomTheme"}
]
for png in set(PAGE_PNG.values()):
    rr_items.append({"name": png,
                     "path": f"RegisteredResources/{png}",
                     "type": "Image"})
packages.append({"name": "RegisteredResources",
                 "type": "RegisteredResources",
                 "items": rr_items})
report["resourcePackages"] = packages

with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print("  ✓  report.json — customTheme activo + RegisteredResources")

# ── 4. page.json — FIX DEFINITIVO ────────────────────────────────────────────
# outspacePane con 'expanded' NO PERTENECE en page.json (solo en report.json)
# → se elimina por completo del objects de cada página
for page_name, png_file in PAGE_PNG.items():
    page_path = os.path.join(REPORT_DEF, "pages", page_name, "page.json")
    if not os.path.exists(page_path):
        continue

    with open(page_path) as f:
        page = json.load(f)

    # Construir objects LIMPIO: solo background con image + transparency
    objects = {
        "background": [
            {
                "properties": {
                    "image": {
                        "expr": {
                            "ResourcePackageItem": {
                                "PackageName": "RegisteredResources",
                                "PackageType": 1,
                                "ItemName": png_file
                            }
                        }
                    },
                    "transparency": lit("0D")
                }
            }
        ]
        # outspacePane ELIMINADO — pertenece solo a report.json
    }
    page["objects"] = objects

    with open(page_path, "w", encoding="utf-8") as f:
        json.dump(page, f, indent=2, ensure_ascii=False)

    display = page.get("displayName", page_name)
    print(f"  ✓  [{display}]  fondo={png_file}  outspacePane=eliminado")

# ── 5. Adaptar SLICERS al tema ────────────────────────────────────────────────
# El customTheme ya aplica colores/bordes globalmente.
# Aquí forzamos el fondo transparente para que el fondo PNG del panel sea visible
# y aseguramos que el header esté oculto (ya estaba así) y fontColor sea coherente.
SLICER_IDS = {
    "3be57bbd2a9044e501ec":                  "33d617049008988eea19",
    "bef499422e12475eee73":                  "33d617049008988eea19",
    "2c8bcecc859c49c7bfbf5ead2bfb6662":      "Comercial",
    "3c22559022c34a1a9f61cde4f30c156d":      "Comercial",
    "3b56fb011d3605d7ea37":                  "DetalleProveedores",
    "3cbeba97a7a02126bc05":                  "DetalleProveedores",
    "120442f2881546039016b7290951b5db":      "ResumenEjecutivo",
    "15b2c760c02942c5ab0877d1acda05fe":      "ResumenEjecutivo",
    "724fe8db4abc4264958f037dee8bb0da":      "ResumenEjecutivo",
    "53f43454cac7e5880b1d":                  "d8eee77324362ca32bc9",
}

for vis_id, page_name in SLICER_IDS.items():
    vis_path = os.path.join(REPORT_DEF, "pages", page_name, "visuals", vis_id, "visual.json")
    if not os.path.exists(vis_path):
        continue
    with open(vis_path) as f:
        vis = json.load(f)

    vco = vis["visual"].get("visualContainerObjects", {})

    # Fondo: blanco semi-transparente sobre el panel azul del PNG
    vco["background"] = [{
        "properties": {
            "show":         lit("true"),
            "color":        color_fill("#FFFFFF"),
            "transparency": lit("15D")   # 15% → el panel azul asoma levemente
        }
    }]
    # Borde corporativo suave
    vco["border"] = [{
        "properties": {
            "show":   lit("true"),
            "color":  color_fill("#D2E1F5")
        }
    }]

    vis["visual"]["visualContainerObjects"] = vco

    # Asegurar header oculto y fontColor blanco (texto sobre panel azul)
    objs = vis["visual"].get("objects", {})
    objs.setdefault("header", [{"properties": {}}])[0]["properties"]["show"] = lit("false")
    objs.setdefault("items", [{"properties": {}}])[0]["properties"].update({
        "fontColor": color_fill("#141E3C"),
        "textSize":  lit("10D")
    })
    vis["visual"]["objects"] = objs

    with open(vis_path, "w", encoding="utf-8") as f:
        json.dump(vis, f, indent=2, ensure_ascii=False)

print(f"  ✓  {len(SLICER_IDS)} slicers adaptados al tema (fondo + borde + fontColor)")

# ── 6. Adaptar CARDS al tema ──────────────────────────────────────────────────
CARD_IDS = {
    "750270f120c56545dd30":              "33d617049008988eea19",
    "d3cf0cc739dac7e565be":              "33d617049008988eea19",
    "a35554535ae6b5e32b98":              "33d617049008988eea19",
    "ab5dc53e21712d022237":              "33d617049008988eea19",
    "4656f9f4f0df4e95951a7640d1d1254d":  "Auditoria",
    "41f66892e3984004a02277df15aab212":  "Auditoria",
    "170dffde66a2423792338b48d682539d":  "Auditoria",
    "6d4cfc0d929a464eb0227d52098571af":  "DetalleProveedores",
    "3eb70c0687654cee8968e19aca29a224":  "ResumenEjecutivo",
    "b63947c3600848999c0588dcd874cbb0":  "ResumenEjecutivo",
    "91f3e55407c742c09606ba75e133b39a":  "ResumenEjecutivo",
    "1e82603f497e431a8bdc447069a0d1a3":  "ResumenEjecutivo",
}

for vis_id, page_name in CARD_IDS.items():
    vis_path = os.path.join(REPORT_DEF, "pages", page_name, "visuals", vis_id, "visual.json")
    if not os.path.exists(vis_path):
        continue
    with open(vis_path) as f:
        vis = json.load(f)

    vco = vis["visual"].get("visualContainerObjects", {})

    # Card: fondo blanco, borde azul claro, radio 8px
    vco["background"] = [{
        "properties": {
            "show":         lit("true"),
            "color":        color_fill("#FFFFFF"),
            "transparency": lit("0D")
        }
    }]
    vco["border"] = [{
        "properties": {
            "show":  lit("true"),
            "color": color_fill("#D2E1F5")
        }
    }]
    # Barra superior azul corporativo
    vco["dropShadow"] = [{
        "properties": {
            "show": lit("false")
        }
    }]

    vis["visual"]["visualContainerObjects"] = vco

    # Colores del texto de la card
    objs = vis["visual"].get("objects", {})
    objs["card"] = [{
        "properties": {
            "calloutValue": color_fill("#141E3C"),
            "label":        color_fill("#5070A0")
        }
    }]
    vis["visual"]["objects"] = objs

    with open(vis_path, "w", encoding="utf-8") as f:
        json.dump(vis, f, indent=2, ensure_ascii=False)

print(f"  ✓  {len(CARD_IDS)} cards adaptadas al tema (fondo + borde + colores)")

# ── 7. ZIP ────────────────────────────────────────────────────────────────────
with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(DEST):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, os.path.dirname(DEST))
            zf.write(abs_path, rel_path)

kb = os.path.getsize(OUT_ZIP) // 1024
print(f"\n  ✓  ZIP: {OUT_ZIP}  ({kb} KB)")
print("  ► Descomprimí la carpeta RealVsPAA_v9 y abrí RealVsPAA.pbip")
