#!/usr/bin/env python3
# Generador del proyecto Power BI (PBIP) "RealVsPAA" a partir de los .md aprobados.
# No modifica CONSULTAS_PowerQuery.md / MEDIDAS_DAX.md / GUIA_PowerBI.md.
import json, os, uuid, textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))
SM = os.path.join(ROOT, "RealVsPAA.SemanticModel")
RP = os.path.join(ROOT, "RealVsPAA.Report")
DEF = os.path.join(SM, "definition")
TBL = os.path.join(DEF, "tables")
for d in (SM, RP, DEF, TBL, os.path.join(RP, "definition")):
    os.makedirs(d, exist_ok=True)

def gid():
    return str(uuid.uuid4())

def w(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def m_block(m_code, base_indent="\t\t\t"):
    # Indenta cada linea del codigo M para que cuelgue de 'source ='
    lines = m_code.strip("\n").split("\n")
    return "\n".join(base_indent + ln for ln in lines)

# ---------------------------------------------------------------------------
# CODIGO M (copiado fiel de CONSULTAS_PowerQuery.md)
# ---------------------------------------------------------------------------
M = {}
M["stgOrigen"] = '''let
    Origen = Excel.Workbook(File.Contents(pRutaArchivo), null, true)
in
    Origen'''

M["stgRealPA"] = '''let
    Origen = stgOrigen,
    Hoja = Origen{[Item="REAL vs PA 2025 2026", Kind="Sheet"]}[Data],
    QuitarFilasSup = Table.Skip(Hoja, 2),
    Encabezados = Table.PromoteHeaders(QuitarFilasSup, [PromoteAllScalars=true]),
    Seleccion = Table.SelectColumns(Encabezados, {
        "Vertical", "Cuenta", "Denominación Cuenta", "Ceco",
        "Denominación Rubro", "mes año", "Monto Real", "Monto PA"
    }),
    Renombrar = Table.RenameColumns(Seleccion, {
        {"Denominación Cuenta", "DenominacionCuenta"},
        {"Denominación Rubro", "Rubro"},
        {"mes año", "Fecha"}
    }),
    SinVacias = Table.SelectRows(Renombrar, each [Vertical] <> null and [Vertical] <> ""),
    Normalizar = Table.TransformColumns(SinVacias, {
        {"Vertical", each Text.Upper(Text.Trim(_)), type text},
        {"Cuenta", each Text.Trim(Text.From(_)), type text},
        {"Ceco", each Text.Upper(Text.Trim(Text.From(_))), type text},
        {"DenominacionCuenta", each Text.Trim(_), type text},
        {"Rubro", each Text.Upper(Text.Trim(_)), type text}
    }),
    MontosReal = Table.ReplaceValue(Normalizar, null, 0, Replacer.ReplaceValue, {"Monto Real"}),
    MontosPA = Table.ReplaceValue(MontosReal, null, 0, Replacer.ReplaceValue, {"Monto PA"}),
    Tipos = Table.TransformColumnTypes(MontosPA, {
        {"Fecha", type date},
        {"Monto Real", type number},
        {"Monto PA", type number}
    })
in
    Tipos'''

M["stgBaseRealCruda"] = '''let
    Origen = stgOrigen,
    Hoja = Origen{[Item="Base Real", Kind="Sheet"]}[Data],
    Encabezados = Table.PromoteHeaders(Hoja, [PromoteAllScalars=true]),
    Seleccion = Table.SelectColumns(Encabezados, {
        "VERTICAL", "Clase de coste", "Centro de coste",
        "Denominacion cuenta contrapartida", "Valor/mon.inf.",
        "mes año", "cuenta ceco", "Texto"
    }),
    Renombrar = Table.RenameColumns(Seleccion, {
        {"VERTICAL", "Vertical"},
        {"Clase de coste", "Cuenta"},
        {"Centro de coste", "Ceco"},
        {"Denominacion cuenta contrapartida", "Proveedor"},
        {"Valor/mon.inf.", "MontoReal"},
        {"mes año", "Fecha"}
    }),
    Normalizar = Table.TransformColumns(Renombrar, {
        {"Vertical", each Text.Upper(Text.Trim(_)), type text},
        {"Cuenta", each Text.Trim(Text.From(_)), type text},
        {"Ceco", each Text.Upper(Text.Trim(Text.From(_))), type text},
        {"Proveedor", each Text.Upper(Text.Trim(_)), type text}
    }),
    SinNulos = Table.ReplaceValue(Normalizar, null, 0, Replacer.ReplaceValue, {"MontoReal"}),
    Tipos = Table.TransformColumnTypes(SinNulos, {
        {"Fecha", type date},
        {"MontoReal", type number}
    }),
    FiltroFecha = Table.SelectRows(Tipos, each [Fecha] >= #date(2025,1,1))
in
    FiltroFecha'''

M["BASE_PLANA_RealvsPA"] = '''let
    Origen = stgOrigen,
    Hoja = Origen{[Item="REAL vs PA 2025 2026", Kind="Sheet"]}[Data],
    QuitarFilasSup = Table.Skip(Hoja, 2),
    Encabezados = Table.PromoteHeaders(QuitarFilasSup, [PromoteAllScalars=true]),
    Seleccion = Table.SelectColumns(Encabezados, {
        "Vertical", "Cuenta", "Denominación Cuenta", "Ceco",
        "Denominación Rubro", "mes año", "Monto Real", "Monto PA"
    }),
    Renombrar = Table.RenameColumns(Seleccion, {
        {"Denominación Cuenta", "DenominacionCuenta"},
        {"Denominación Rubro", "Rubro"},
        {"mes año", "Fecha"}
    }),
    SinVacias = Table.SelectRows(Renombrar, each [Vertical] <> null and [Vertical] <> ""),
    MontosReal = Table.ReplaceValue(SinVacias, null, 0, Replacer.ReplaceValue, {"Monto Real"}),
    MontosPA = Table.ReplaceValue(MontosReal, null, 0, Replacer.ReplaceValue, {"Monto PA"}),
    Renombrar2 = Table.RenameColumns(MontosPA, {{"Monto Real", "MontoReal"}, {"Monto PA", "MontoPA"}}),
    ConVariacion = Table.AddColumn(Renombrar2, "Variacion", each [MontoReal] - [MontoPA], type number),
    Tipos = Table.TransformColumnTypes(ConVariacion, {
        {"Fecha", type date}, {"MontoReal", type number},
        {"MontoPA", type number}, {"Variacion", type number}
    })
in
    Tipos'''

M["DIM_Vertical"] = '''let
    FuentePA = Table.SelectColumns(stgRealPA, {"Vertical"}),
    Real = Table.SelectColumns(stgBaseRealCruda, {"Vertical"}),
    Union = Table.Combine({FuentePA, Real}),
    Distinct = Table.Distinct(Union),
    SinNulos = Table.SelectRows(Distinct, each [Vertical] <> null and [Vertical] <> ""),
    Ordenado = Table.Sort(SinNulos, {{"Vertical", Order.Ascending}}),
    ConID = Table.AddIndexColumn(Ordenado, "VerticalID", 1, 1, Int64.Type),
    Tipos = Table.TransformColumnTypes(ConID, {{"VerticalID", Int64.Type}, {"Vertical", type text}})
in
    Tipos'''

M["DIM_Cuenta"] = '''let
    Base = Table.SelectColumns(stgRealPA, {"Cuenta", "DenominacionCuenta", "Rubro"}),
    Distinct = Table.Distinct(Base),
    SinNulos = Table.SelectRows(Distinct, each [Cuenta] <> null and [Cuenta] <> ""),
    AgrupadoUnico = Table.Distinct(SinNulos, {"Cuenta"}),
    Ordenado = Table.Sort(AgrupadoUnico, {{"Cuenta", Order.Ascending}}),
    ConID = Table.AddIndexColumn(Ordenado, "CuentaID", 1, 1, Int64.Type),
    Tipos = Table.TransformColumnTypes(ConID, {
        {"CuentaID", Int64.Type}, {"Cuenta", type text},
        {"DenominacionCuenta", type text}, {"Rubro", type text}
    })
in
    Tipos'''

M["DIM_Ceco"] = '''let
    FuentePA = Table.SelectColumns(stgRealPA, {"Ceco"}),
    Real = Table.SelectColumns(stgBaseRealCruda, {"Ceco"}),
    Union = Table.Combine({FuentePA, Real}),
    Distinct = Table.Distinct(Union),
    SinNulos = Table.SelectRows(Distinct, each [Ceco] <> null and [Ceco] <> ""),
    Ordenado = Table.Sort(SinNulos, {{"Ceco", Order.Ascending}}),
    ConID = Table.AddIndexColumn(Ordenado, "CecoID", 1, 1, Int64.Type),
    Tipos = Table.TransformColumnTypes(ConID, {{"CecoID", Int64.Type}, {"Ceco", type text}})
in
    Tipos'''

M["DIM_Proveedor"] = '''let
    Base = Table.SelectColumns(stgBaseRealCruda, {"Proveedor"}),
    Distinct = Table.Distinct(Base),
    SinNulos = Table.SelectRows(Distinct, each [Proveedor] <> null and [Proveedor] <> ""),
    Ordenado = Table.Sort(SinNulos, {{"Proveedor", Order.Ascending}}),
    ConID = Table.AddIndexColumn(Ordenado, "ProveedorID", 1, 1, Int64.Type),
    Tipos = Table.TransformColumnTypes(ConID, {{"ProveedorID", Int64.Type}, {"Proveedor", type text}})
in
    Tipos'''

M["DIM_Calendario"] = '''let
    FechaInicio = #date(2025, 1, 1),
    MaxPA = List.Max(stgRealPA[Fecha]),
    MaxReal = List.Max(stgBaseRealCruda[Fecha]),
    FechaFin = List.Max({MaxPA, MaxReal}),
    MesesTotales = (Date.Year(FechaFin) - Date.Year(FechaInicio)) * 12
                   + (Date.Month(FechaFin) - Date.Month(FechaInicio)) + 1,
    ListaFechas = List.Transform({0..MesesTotales - 1}, each Date.AddMonths(FechaInicio, _)),
    Tabla = Table.FromList(ListaFechas, Splitter.SplitByNothing(), {"Fecha"}),
    TipoFecha = Table.TransformColumnTypes(Tabla, {{"Fecha", type date}}),
    ConAnio = Table.AddColumn(TipoFecha, "Año", each Date.Year([Fecha]), Int64.Type),
    ConNroMes = Table.AddColumn(ConAnio, "NroMes", each Date.Month([Fecha]), Int64.Type),
    ConNombreMes = Table.AddColumn(ConNroMes, "NombreMes", each Text.Proper(Date.MonthName([Fecha], "es-ES")), type text),
    ConMesAnio = Table.AddColumn(ConNombreMes, "MesAño",
        each Text.Proper(Text.Start(Date.MonthName([Fecha], "es-ES"), 3)) & "-" & Text.End(Text.From(Date.Year([Fecha])), 2), type text),
    ConOrden = Table.AddColumn(ConMesAnio, "AñoMesOrden", each Date.Year([Fecha]) * 100 + Date.Month([Fecha]), Int64.Type)
in
    ConOrden'''

M["FACT_Presupuesto"] = '''let
    Base = stgRealPA,
    JoinVert = Table.NestedJoin(Base, {"Vertical"}, DIM_Vertical, {"Vertical"}, "dV", JoinKind.LeftOuter),
    ExpVert = Table.ExpandTableColumn(JoinVert, "dV", {"VerticalID"}),
    JoinCta = Table.NestedJoin(ExpVert, {"Cuenta"}, DIM_Cuenta, {"Cuenta"}, "dC", JoinKind.LeftOuter),
    ExpCta = Table.ExpandTableColumn(JoinCta, "dC", {"CuentaID"}),
    JoinCeco = Table.NestedJoin(ExpCta, {"Ceco"}, DIM_Ceco, {"Ceco"}, "dCe", JoinKind.LeftOuter),
    ExpCeco = Table.ExpandTableColumn(JoinCeco, "dCe", {"CecoID"}),
    Final = Table.SelectColumns(ExpCeco, {"Fecha", "VerticalID", "CuentaID", "CecoID", "Monto Real", "Monto PA"}),
    Renombrar = Table.RenameColumns(Final, {{"Monto Real", "MontoReal"}, {"Monto PA", "MontoPA"}}),
    Tipos = Table.TransformColumnTypes(Renombrar, {
        {"Fecha", type date}, {"VerticalID", Int64.Type},
        {"CuentaID", Int64.Type}, {"CecoID", Int64.Type},
        {"MontoReal", type number}, {"MontoPA", type number}
    })
in
    Tipos'''

M["FACT_RealDetalle"] = '''let
    Base = stgBaseRealCruda,
    JoinVert = Table.NestedJoin(Base, {"Vertical"}, DIM_Vertical, {"Vertical"}, "dV", JoinKind.LeftOuter),
    ExpVert = Table.ExpandTableColumn(JoinVert, "dV", {"VerticalID"}),
    JoinCta = Table.NestedJoin(ExpVert, {"Cuenta"}, DIM_Cuenta, {"Cuenta"}, "dC", JoinKind.LeftOuter),
    ExpCta = Table.ExpandTableColumn(JoinCta, "dC", {"CuentaID"}),
    JoinCeco = Table.NestedJoin(ExpCta, {"Ceco"}, DIM_Ceco, {"Ceco"}, "dCe", JoinKind.LeftOuter),
    ExpCeco = Table.ExpandTableColumn(JoinCeco, "dCe", {"CecoID"}),
    JoinProv = Table.NestedJoin(ExpCeco, {"Proveedor"}, DIM_Proveedor, {"Proveedor"}, "dP", JoinKind.LeftOuter),
    ExpProv = Table.ExpandTableColumn(JoinProv, "dP", {"ProveedorID"}),
    Final = Table.SelectColumns(ExpProv, {"Fecha", "VerticalID", "CuentaID", "CecoID", "ProveedorID", "MontoReal", "Texto"}),
    Tipos = Table.TransformColumnTypes(Final, {
        {"Fecha", type date}, {"VerticalID", Int64.Type}, {"CuentaID", Int64.Type},
        {"CecoID", Int64.Type}, {"ProveedorID", Int64.Type},
        {"MontoReal", type number}, {"Texto", type text}
    })
in
    Tipos'''

# ---------------------------------------------------------------------------
# Definicion de columnas por tabla cargada
# ---------------------------------------------------------------------------
COLS = {
 "DIM_Vertical": [("VerticalID","int64"),("Vertical","string")],
 "DIM_Cuenta": [("CuentaID","int64"),("Cuenta","string"),("DenominacionCuenta","string"),("Rubro","string")],
 "DIM_Ceco": [("CecoID","int64"),("Ceco","string")],
 "DIM_Proveedor": [("ProveedorID","int64"),("Proveedor","string")],
 "DIM_Calendario": [("Fecha","dateTime"),("Año","int64"),("NroMes","int64"),
                    ("NombreMes","string"),("MesAño","string"),("AñoMesOrden","int64")],
 "FACT_Presupuesto": [("Fecha","dateTime"),("VerticalID","int64"),("CuentaID","int64"),
                      ("CecoID","int64"),("MontoReal","double"),("MontoPA","double")],
 "FACT_RealDetalle": [("Fecha","dateTime"),("VerticalID","int64"),("CuentaID","int64"),
                      ("CecoID","int64"),("ProveedorID","int64"),("MontoReal","double"),("Texto","string")],
}
FMT = {"int64":"0","double":"#,0","dateTime":None,"string":None}
SUMMARIZE_NONE = {"int64", }  # IDs no se agregan

# ---------------------------------------------------------------------------
# Medidas (de MEDIDAS_DAX.md). Hospedadas en FACT_Presupuesto salvo Real Detalle.
# ---------------------------------------------------------------------------
MEAS_PRES = [
 ("Real Mes", "SUM(FACT_Presupuesto[MontoReal])", "#,0", "01 Real vs PA"),
 ("PA Mes", "SUM(FACT_Presupuesto[MontoPA])", "#,0", "01 Real vs PA"),
 ("Variación", "[Real Mes] - [PA Mes]", "#,0", "01 Real vs PA"),
 ("Variación %", "DIVIDE([Variación], [PA Mes])", "0.0%", "01 Real vs PA"),
 ("Real Acumulado", "CALCULATE([Real Mes], DATESYTD(DIM_Calendario[Fecha]))", "#,0", "02 Acumulado"),
 ("PA Acumulado", "CALCULATE([PA Mes], DATESYTD(DIM_Calendario[Fecha]))", "#,0", "02 Acumulado"),
 ("Variación Acum", "[Real Acumulado] - [PA Acumulado]", "#,0", "02 Acumulado"),
 ("Real Año Anterior", "CALCULATE([Real Mes], SAMEPERIODLASTYEAR(DIM_Calendario[Fecha]))", "#,0", "03 Interanual"),
 ("Var vs Año Anterior", "[Real Mes] - [Real Año Anterior]", "#,0", "03 Interanual"),
]
MEAS_PRES_ML = [
 ("Variación % fmt", 'VAR v = [Variación %]\nRETURN IF(ISBLANK(v), "—", FORMAT(v, "+0.0%;-0.0%"))', None, "04 Formato"),
 ("Color Variación", 'IF([Variación] > 0, "#C00000", "#1F7A1F")', None, "04 Formato"),
]
MEAS_REAL = [
 ("Real Detalle", "SUM(FACT_RealDetalle[MontoReal])", "#,0", "05 Detalle"),
]

def col_tmdl(name, dt):
    fmt = FMT[dt]
    lines = [f"\tcolumn {q(name)}", f"\t\tdataType: {dt}"]
    if name in ("VerticalID","CuentaID","CecoID","ProveedorID"):
        lines.append("\t\tisKey")
    if dt in SUMMARIZE_NONE:
        lines.append("\t\tsummarizeBy: none")
    elif dt == "double":
        lines.append("\t\tsummarizeBy: sum")
    else:
        lines.append("\t\tsummarizeBy: none")
    if fmt:
        lines.append(f"\t\tformatString: {fmt}")
    if dt == "dateTime":
        lines.append("\t\tformatString: dd/mm/yyyy")
    lines.append(f"\t\tlineageTag: {gid()}")
    lines.append("")
    lines.append(f"\t\tannotation SummarizationSetBy = Automatic")
    return "\n".join(lines)

def q(name):
    # entrecomilla si tiene espacios o caracteres especiales
    if any(c in name for c in " áéíóúñÁÉÍÓÚÑ%"):
        return "'" + name + "'"
    return name

def measure_tmdl(name, expr, fmt, folder, multiline=False):
    if multiline:
        body = "\n".join("\t\t\t" + ln for ln in expr.split("\n"))
        head = f"\tmeasure {q(name)} = ```\n{body}\n\t\t\t```"
    else:
        head = f"\tmeasure {q(name)} = {expr}"
    lines = [head]
    if fmt:
        lines.append(f"\t\tformatString: {fmt}")
    lines.append(f"\t\tdisplayFolder: {folder}")
    lines.append(f"\t\tlineageTag: {gid()}")
    return "\n".join(lines)

def table_tmdl(tname):
    parts = [f"table {tname}", f"\tlineageTag: {gid()}", ""]
    # medidas
    if tname == "FACT_Presupuesto":
        for m in MEAS_PRES:
            parts.append(measure_tmdl(*m)); parts.append("")
        for m in MEAS_PRES_ML:
            parts.append(measure_tmdl(m[0], m[1], m[2], m[3], multiline=True)); parts.append("")
    if tname == "FACT_RealDetalle":
        for m in MEAS_REAL:
            parts.append(measure_tmdl(*m)); parts.append("")
    # columnas
    for cname, dt in COLS[tname]:
        parts.append(col_tmdl(cname, dt)); parts.append("")
    # particion
    parts.append(f"\tpartition {tname} = m")
    parts.append("\t\tmode: import")
    parts.append("\t\tsource =")
    parts.append(m_block(M[tname]))
    parts.append("")
    # ordenar MesAño por AñoMesOrden
    if tname == "DIM_Calendario":
        # se agrega sortByColumn dentro de la columna MesAño -> reescribimos esa columna
        pass
    return "\n".join(parts) + "\n"

# Tabla calendario: agregar sortByColumn a MesAño
def table_calendario():
    txt = table_tmdl("DIM_Calendario")
    txt = txt.replace(
        "\tcolumn 'MesAño'\n\t\tdataType: string\n\t\tsummarizeBy: none",
        "\tcolumn 'MesAño'\n\t\tdataType: string\n\t\tsummarizeBy: none\n\t\tsortByColumn: AñoMesOrden")
    return txt

# ---------------------------------------------------------------------------
# Escribir tablas
# ---------------------------------------------------------------------------
for t in COLS:
    if t == "DIM_Calendario":
        w(os.path.join(TBL, t + ".tmdl"), table_calendario())
    else:
        w(os.path.join(TBL, t + ".tmdl"), table_tmdl(t))

# ---------------------------------------------------------------------------
# expressions.tmdl (parametro + staging no cargadas)
# ---------------------------------------------------------------------------
exprs = []
exprs.append('expression pRutaArchivo = "C:\\\\Reportes\\\\PAA\\\\Real_y_pa_2026v2.xlsx" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]')
exprs.append(f"\tlineageTag: {gid()}")
exprs.append("\tannotation PBI_ResultType = Text")
exprs.append("")
for name in ("stgOrigen","stgRealPA","stgBaseRealCruda","BASE_PLANA_RealvsPA"):
    exprs.append(f"expression {name} =")
    exprs.append(m_block(M[name], "\t\t"))
    exprs.append(f"\tlineageTag: {gid()}")
    exprs.append("\tannotation PBI_ResultType = Table")
    exprs.append("")
w(os.path.join(DEF, "expressions.tmdl"), "\n".join(exprs) + "\n")

# ---------------------------------------------------------------------------
# relationships.tmdl
# ---------------------------------------------------------------------------
rels = []
def rel(fromtab, fromcol, totab, tocol):
    rels.append(f"relationship {gid()}")
    rels.append(f"\tfromColumn: {fromtab}.{q(fromcol)}")
    rels.append(f"\ttoColumn: {totab}.{q(tocol)}")
    rels.append("")
rel("FACT_Presupuesto","Fecha","DIM_Calendario","Fecha")
rel("FACT_RealDetalle","Fecha","DIM_Calendario","Fecha")
rel("FACT_Presupuesto","VerticalID","DIM_Vertical","VerticalID")
rel("FACT_RealDetalle","VerticalID","DIM_Vertical","VerticalID")
rel("FACT_Presupuesto","CuentaID","DIM_Cuenta","CuentaID")
rel("FACT_RealDetalle","CuentaID","DIM_Cuenta","CuentaID")
rel("FACT_Presupuesto","CecoID","DIM_Ceco","CecoID")
rel("FACT_RealDetalle","CecoID","DIM_Ceco","CecoID")
rel("FACT_RealDetalle","ProveedorID","DIM_Proveedor","ProveedorID")
w(os.path.join(DEF, "relationships.tmdl"), "\n".join(rels) + "\n")

# ---------------------------------------------------------------------------
# model.tmdl + database.tmdl
# ---------------------------------------------------------------------------
order = ["pRutaArchivo","stgOrigen","stgRealPA","stgBaseRealCruda","DIM_Vertical",
         "DIM_Cuenta","DIM_Ceco","DIM_Proveedor","DIM_Calendario",
         "FACT_Presupuesto","FACT_RealDetalle","BASE_PLANA_RealvsPA"]
model = f'''model Model
\tculture: es-ES
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: es-ES
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

\tannotation PBI_QueryOrder = {json.dumps(order)}

\tannotation __PBI_TimeIntelligenceEnabled = 0
'''
w(os.path.join(DEF, "model.tmdl"), model)
w(os.path.join(DEF, "database.tmdl"), "database\n\tcompatibilityLevel: 1567\n")

# ---------------------------------------------------------------------------
# definition.pbism + .platform (SemanticModel)
# ---------------------------------------------------------------------------
w(os.path.join(SM, "definition.pbism"), json.dumps({"version":"4.2","settings":{}}, indent=2))
w(os.path.join(SM, ".platform"), json.dumps({
  "$schema":"https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
  "metadata":{"type":"SemanticModel","displayName":"RealVsPAA"},
  "config":{"version":"2.0","logicalId":gid()}}, indent=2))

# diagramLayout
w(os.path.join(SM, "diagramLayout.json"), json.dumps({"version":"1.1.0","diagrams":[]}, indent=2))

print("SemanticModel OK")
