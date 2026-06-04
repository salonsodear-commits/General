#!/usr/bin/env python3
# Genera RealVsPAA.Report (report.json legacy) con 5 paginas y visuales.
import json, os, uuid
ROOT = os.path.dirname(os.path.abspath(__file__))
RP = os.path.join(ROOT, "RealVsPAA.Report")
os.makedirs(RP, exist_ok=True)

def gid(): return str(uuid.uuid4()).replace("-","")

# Alias de entidades en From
ALIAS = {"DIM_Calendario":"c","DIM_Vertical":"v","DIM_Cuenta":"a","DIM_Ceco":"e",
         "DIM_Proveedor":"p","FACT_Presupuesto":"f","FACT_RealDetalle":"r"}

def field(entity, prop, is_measure=False):
    return {"entity":entity, "prop":prop, "measure":is_measure}

def build_proto(fields):
    # fields: lista de dicts field()
    entities = []
    seen = {}
    for fl in fields:
        e = fl["entity"]
        if e not in seen:
            seen[e] = ALIAS[e]
            entities.append({"Name":ALIAS[e], "Entity":e, "Type":0})
    select = []
    for fl in fields:
        src = {"SourceRef":{"Source":ALIAS[fl["entity"]]}}
        if fl["measure"]:
            select.append({"Measure":{"Expression":src,"Property":fl["prop"]},
                           "Name":f"{fl['entity']}.{fl['prop']}"})
        else:
            select.append({"Column":{"Expression":src,"Property":fl["prop"]},
                           "Name":f"{fl['entity']}.{fl['prop']}"})
    return {"Version":2, "From":entities, "Select":select}

def qref(fl): return f"{fl['entity']}.{fl['prop']}"

def visual(vtype, x, y, wd, ht, roles):
    # roles: dict role -> lista de field()
    allf = []
    for r, fs in roles.items():
        allf.extend(fs)
    projections = {r:[{"queryRef":qref(fl)} for fl in fs] for r, fs in roles.items()}
    single = {"visualType":vtype, "projections":projections,
              "prototypeQuery":build_proto(allf), "drillFilterOtherVisuals":True}
    cfg = {"name":gid(),
           "layouts":[{"id":0,"position":{"x":x,"y":y,"z":0,"width":wd,"height":ht,"tabOrder":0}}],
           "singleVisual":single}
    return {"x":x,"y":y,"z":0,"width":wd,"height":ht,
            "config":json.dumps(cfg), "filters":"[]", "query":"", "dataTransforms":""}

def textbox(x,y,wd,ht,text):
    cfg={"name":gid(),
         "layouts":[{"id":0,"position":{"x":x,"y":y,"z":0,"width":wd,"height":ht}}],
         "singleVisual":{"visualType":"textbox","drillFilterOtherVisuals":True,
            "objects":{"general":[{"properties":{"paragraphs":[{"textRuns":[
               {"value":text,"textStyle":{"fontSize":"18pt","fontWeight":"bold"}}]}]}}]}}}
    return {"x":x,"y":y,"z":0,"width":wd,"height":ht,
            "config":json.dumps(cfg),"filters":"[]","query":"","dataTransforms":""}

# Campos reutilizables
F_RealMes = field("FACT_Presupuesto","Real Mes",True)
F_PAMes   = field("FACT_Presupuesto","PA Mes",True)
F_Var     = field("FACT_Presupuesto","Variación",True)
F_VarPct  = field("FACT_Presupuesto","Variación %",True)
F_RealAc  = field("FACT_Presupuesto","Real Acumulado",True)
F_PAAc    = field("FACT_Presupuesto","PA Acumulado",True)
F_RealDet = field("FACT_RealDetalle","Real Detalle",True)
C_MesAno  = field("DIM_Calendario","MesAño")
C_Anio    = field("DIM_Calendario","Año")
C_Vert    = field("DIM_Vertical","Vertical")
C_Rubro   = field("DIM_Cuenta","Rubro")
C_Cuenta  = field("DIM_Cuenta","Cuenta")
C_DenCta  = field("DIM_Cuenta","DenominacionCuenta")
C_Ceco    = field("DIM_Ceco","Ceco")
C_Prov    = field("DIM_Proveedor","Proveedor")
C_Texto   = field("FACT_RealDetalle","Texto")

W, H = 1280, 720
sections = []

def section(name, display, ordinal, visuals, filters="[]"):
    return {"name":name,"displayName":display,"filters":filters,"ordinal":ordinal,
            "visualContainers":visuals,"config":"{}","displayOption":1,"width":W,"height":H}

# --- Pagina 1: Resumen Ejecutivo ---
v1 = [
 textbox(20,10,800,50,"Resumen Ejecutivo — Real vs Presupuesto (PAA)"),
 visual("card",20,70,290,120,{"Values":[F_RealMes]}),
 visual("card",320,70,290,120,{"Values":[F_PAMes]}),
 visual("card",620,70,290,120,{"Values":[F_Var]}),
 visual("card",920,70,290,120,{"Values":[F_VarPct]}),
 visual("clusteredColumnChart",20,200,760,300,{"Category":[C_MesAno],"Y":[F_RealMes,F_PAMes]}),
 visual("clusteredBarChart",20,510,760,190,{"Category":[C_Vert],"Y":[F_RealMes,F_PAMes]}),
 visual("slicer",800,200,200,160,{"Values":[C_Vert]}),
 visual("slicer",1010,200,200,160,{"Values":[C_Rubro]}),
 visual("slicer",800,370,410,130,{"Values":[C_MesAno]}),
 visual("lineChart",800,510,410,190,{"Category":[C_MesAno],"Y":[F_RealAc,F_PAAc]}),
]
sections.append(section("ResumenEjecutivo","1. Resumen Ejecutivo",0,v1))

# --- Pagina 2: Comercial ---
v2 = [
 textbox(20,10,800,50,"Comercial — Verticales, Rubros y Cuentas"),
 visual("slicer",1020,70,240,120,{"Values":[C_Vert]}),
 visual("slicer",1020,200,240,120,{"Values":[C_MesAno]}),
 visual("matrix",20,70,980,620,{"Rows":[C_Vert,C_Rubro,C_Cuenta],
        "Values":[F_RealMes,F_PAMes,F_Var,F_VarPct]}),
]
sections.append(section("Comercial","2. Comercial",1,v2))

# --- Pagina 3: Operativa (Aperturas hasta Ceco) ---
v3 = [
 textbox(20,10,900,50,"Operativa — Apertura Vertical > Rubro > Cuenta > Ceco"),
 visual("slicer",1020,70,240,120,{"Values":[C_Rubro]}),
 visual("slicer",1020,200,240,120,{"Values":[C_MesAno]}),
 visual("matrix",20,70,980,620,{"Rows":[C_Vert,C_Rubro,C_Cuenta,C_Ceco],
        "Values":[F_RealMes,F_PAMes,F_Var,F_VarPct]}),
]
sections.append(section("Operativa","3. Operativa",2,v3))

# --- Pagina 4: Drill Through Detalle Proveedores ---
# Filtros drillthrough sobre Cuenta y Ceco
dt_filters = json.dumps([
 {"name":gid(),"expression":{"Column":{"Expression":{"SourceRef":{"Entity":"DIM_Cuenta"}},"Property":"Cuenta"}},
  "type":"Drillthrough","howCreated":1,"filter":{"Version":2,"From":[{"Name":"a","Entity":"DIM_Cuenta","Type":0}],"Where":[]}},
 {"name":gid(),"expression":{"Column":{"Expression":{"SourceRef":{"Entity":"DIM_Ceco"}},"Property":"Ceco"}},
  "type":"Drillthrough","howCreated":1,"filter":{"Version":2,"From":[{"Name":"e","Entity":"DIM_Ceco","Type":0}],"Where":[]}}
])
v4 = [
 textbox(20,10,900,50,"Detalle de Proveedores (solo Real) — Drill Through por Cuenta + Ceco"),
 visual("card",20,70,300,120,{"Values":[F_RealDet]}),
 visual("tableEx",20,200,1240,500,{"Values":[C_Prov,C_Cuenta,C_Ceco,F_RealDet,C_Texto]}),
]
sections.append(section("DetalleProveedores","4. Drill Through — Proveedores",3,v4,filters=dt_filters))

# --- Pagina 5: Auditoria ---
v5 = [
 textbox(20,10,900,50,"Auditoría — Controles y validaciones"),
 visual("card",20,70,290,120,{"Values":[F_RealMes]}),
 visual("card",320,70,290,120,{"Values":[F_RealDet]}),
 visual("card",620,70,290,120,{"Values":[F_Var]}),
 visual("tableEx",20,200,1240,500,{"Values":[C_Vert,C_Cuenta,C_Ceco,F_RealMes,F_RealDet,F_Var]}),
]
sections.append(section("Auditoria","5. Auditoría",4,v5))

report = {
 "id":0,
 "resourcePackages":[{"resourcePackage":{"name":"SharedResources","type":2,
    "items":[{"name":"CY24SU10","path":"BaseThemes/CY24SU10.json","type":202}],"disabled":False}}],
 "config":json.dumps({"version":"5.43","activeSectionIndex":0,
    "defaultDrillFilterOtherVisuals":True,
    "settings":{"useStylableVisualContainerHeader":True}}),
 "layoutOptimization":0,
 "sections":sections,
 "pods":[],
 "publicCustomVisuals":[]
}
with open(os.path.join(RP,"report.json"),"w",encoding="utf-8") as fp:
    json.dump(report, fp, ensure_ascii=False, indent=2)

# definition.pbir
with open(os.path.join(RP,"definition.pbir"),"w",encoding="utf-8") as fp:
    json.dump({"version":"1.0","datasetReference":{"byPath":{"path":"../RealVsPAA.SemanticModel"}}}, fp, indent=2)

# .platform
with open(os.path.join(RP,".platform"),"w",encoding="utf-8") as fp:
    json.dump({"$schema":"https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
       "metadata":{"type":"Report","displayName":"RealVsPAA"},
       "config":{"version":"2.0","logicalId":str(uuid.uuid4())}}, fp, indent=2)

print("Report OK -", len(sections), "paginas")
