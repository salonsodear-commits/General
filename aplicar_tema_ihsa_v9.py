#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplica tema GrupoIHSA v9 y fondos PNG al PBIP RealVsPAA.
Versión corregida: propiedades validadas contra schema PBIP.
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

# ── 1. Copiar proyecto fresco ─────────────────────────────────────────────────
if os.path.exists(DEST):
    shutil.rmtree(DEST)
shutil.copytree(SRC, DEST)
print(f"  ✓  Proyecto copiado")

REPORT_DEF = os.path.join(DEST, REPORT, "definition")
STATIC     = os.path.join(DEST, REPORT, "StaticResources", "RegisteredResources")
os.makedirs(STATIC, exist_ok=True)

# ── 2. Copiar recursos ────────────────────────────────────────────────────────
shutil.copy2(os.path.join(ASSETS, "tema_GrupoIHSA.json"),
             os.path.join(STATIC, "tema_GrupoIHSA.json"))
for png in set(PAGE_PNG.values()):
    shutil.copy2(os.path.join(ASSETS, png), os.path.join(STATIC, png))
print(f"  ✓  Recursos copiados a RegisteredResources/")

# ── 3. report.json — FIX: reportVersionAtImport en customTheme ───────────────
report_path = os.path.join(REPORT_DEF, "report.json")
with open(report_path) as f:
    report = json.load(f)

# Tomar versiones del baseTheme existente
base_versions = report["themeCollection"]["baseTheme"]["reportVersionAtImport"]

# customTheme sin reportVersionAtImport — esa prop es solo válida en baseTheme
# La incluimos sin ella; el warning anterior era no-fatal; con ella crashea
report["themeCollection"].pop("customTheme", None)  # no incluir customTheme — causa crash

# resourcePackages
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
print(f"  ✓  report.json — RegisteredResources para imágenes y tema")

# ── 4. page.json — FIX: solo image + transparency; sin outspacePane custom ───
for page_name, png_file in PAGE_PNG.items():
    page_path = os.path.join(REPORT_DEF, "pages", page_name, "page.json")
    if not os.path.exists(page_path):
        continue

    with open(page_path) as f:
        page = json.load(f)

    objects = page.get("objects", {})

    # FIX: solo propiedades válidas en background — quitar imageScaling y visibility
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
                "transparency": {
                    "expr": {"Literal": {"Value": "0D"}}
                }
                # imageScaling y visibility removidos — no son propiedades válidas del schema
            }
        }
    ]

    # FIX: outspacePane — solo propiedades válidas (solo 'expanded')
    # Restaurar el original sin agregar 'background'
    objects["outspacePane"] = [
        {
            "properties": {
                "expanded": {
                    "expr": {"Literal": {"Value": "false"}}
                }
            }
        }
    ]

    page["objects"] = objects

    with open(page_path, "w", encoding="utf-8") as f:
        json.dump(page, f, indent=2, ensure_ascii=False)

    print(f"  ✓  [{page.get('displayName', page_name)}] → {png_file}")

# ── 5. ZIP ────────────────────────────────────────────────────────────────────
with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(DEST):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, os.path.dirname(DEST))
            zf.write(abs_path, rel_path)

kb = os.path.getsize(OUT_ZIP) // 1024
print(f"\n  ✓  ZIP: {OUT_ZIP}  ({kb} KB)")
print(f"  ► Descomprimí y abrí RealVsPAA.pbip en Power BI Desktop")
