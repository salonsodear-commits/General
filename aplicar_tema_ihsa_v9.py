#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplica el tema GrupoIHSA v9 y los fondos PNG al PBIP RealVsPAA.
Modifica directamente los archivos de definición PBIP.
Genera un .zip listo para abrir en Power BI Desktop.
"""

import json, base64, os, shutil, zipfile

SRC   = "/home/user/General/pbip_ihsa/RealVsPAA"
DEST  = "/home/user/General/pbip_ihsa/RealVsPAA_v9"
ASSETS = "/home/user/General/assets_ihsa_v9"
REPORT = "RealVsPAA.Report"
OUT_ZIP = "/home/user/General/assets_ihsa_v9/RealVsPAA_IHSA_v9.zip"

# ── Mapeo página → fondo (usando displayName reales) ──────────────────────────
PAGE_PNG = {
    "d532c5ff032986009878": "fondo_00_indice.png",      # 0. Índice
    "d8eee77324362ca32bc9": "fondo_05_opex.png",         # OPEX - 1. Entregable
    "ResumenEjecutivo":     "fondo_01_resumen.png",      # OPEX - 2. Resumen YoY
    "33d617049008988eea19": "fondo_03_operativa.png",    # OPEX - 3. Resumen YTD
    "Comercial":            "fondo_02_comercial.png",    # OPEX - 4. Aperturas
    "DetalleProveedores":   "fondo_04_proveedores.png",  # 4. Drill Proveedores
    "Auditoria":            "fondo_06_auditoria.png",    # 6. Auditoría
}

# ── 1. Copiar proyecto ────────────────────────────────────────────────────────
if os.path.exists(DEST):
    shutil.rmtree(DEST)
shutil.copytree(SRC, DEST)
print(f"  ✓  Proyecto copiado a {DEST}")

REPORT_DEF = os.path.join(DEST, REPORT, "definition")
STATIC     = os.path.join(DEST, REPORT, "StaticResources", "RegisteredResources")
os.makedirs(STATIC, exist_ok=True)

# ── 2. Copiar tema JSON a RegisteredResources ─────────────────────────────────
tema_src = os.path.join(ASSETS, "tema_GrupoIHSA.json")
tema_dst = os.path.join(STATIC, "tema_GrupoIHSA.json")
shutil.copy2(tema_src, tema_dst)
print(f"  ✓  Tema copiado a StaticResources/RegisteredResources/")

# ── 3. Copiar fondos PNG a RegisteredResources ────────────────────────────────
for png in set(PAGE_PNG.values()):
    shutil.copy2(os.path.join(ASSETS, png), os.path.join(STATIC, png))
print(f"  ✓  {len(set(PAGE_PNG.values()))} fondos PNG copiados a RegisteredResources/")

# ── 4. Actualizar report.json: tema + resourcePackages ───────────────────────
report_path = os.path.join(REPORT_DEF, "report.json")
with open(report_path) as f:
    report = json.load(f)

# Añadir tema personalizado
report["themeCollection"]["customTheme"] = {
    "name": "GrupoIHSA",
    "type": "RegisteredResources"
}

# Construir lista de items para RegisteredResources
rr_items = [
    {
        "name": "GrupoIHSA",
        "path": "RegisteredResources/tema_GrupoIHSA.json",
        "type": "CustomTheme"
    }
]
for png in set(PAGE_PNG.values()):
    rr_items.append({
        "name": png,
        "path": f"RegisteredResources/{png}",
        "type": "Image"
    })

# Añadir o reemplazar el paquete RegisteredResources
packages = report.get("resourcePackages", [])
packages = [p for p in packages if p.get("name") != "RegisteredResources"]
packages.append({
    "name": "RegisteredResources",
    "type": "RegisteredResources",
    "items": rr_items
})
report["resourcePackages"] = packages

with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"  ✓  report.json actualizado (tema + resourcePackages)")

# ── 5. Inyectar fondo en cada page.json ──────────────────────────────────────
for page_name, png_file in PAGE_PNG.items():
    page_path = os.path.join(REPORT_DEF, "pages", page_name, "page.json")
    if not os.path.exists(page_path):
        print(f"  ⚠  No encontrada: {page_path}")
        continue

    with open(page_path) as f:
        page = json.load(f)

    # Preservar objects existentes y agregar background
    objects = page.get("objects", {})
    objects["background"] = [
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
                "imageScaling": {
                    "expr": {"Literal": {"Value": "'Normal'"}}
                },
                "transparency": {
                    "expr": {"Literal": {"Value": "0D"}}
                },
                "visibility": {
                    "expr": {"Literal": {"Value": "1D"}}
                }
            }
        }
    ]
    # Fondo del informe: color corporativo blanco
    objects["outspacePane"] = [
        {
            "properties": {
                "background": {
                    "expr": {
                        "Literal": {"Value": "'#F8FAFD'"}
                    }
                }
            }
        }
    ]
    page["objects"] = objects

    with open(page_path, "w", encoding="utf-8") as f:
        json.dump(page, f, indent=2, ensure_ascii=False)

    display = page.get("displayName", page_name)
    print(f"  ✓  [{display}] → {png_file}")

# ── 6. Empaquetar como ZIP ────────────────────────────────────────────────────
with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(DEST):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, os.path.dirname(DEST))
            zf.write(abs_path, rel_path)

kb = os.path.getsize(OUT_ZIP) // 1024
print(f"\n  ✓  ZIP generado: {OUT_ZIP}  ({kb} KB)")
print(f"\n  ► Descomprimí el ZIP y abrí RealVsPAA.pbip en Power BI Desktop")
