"""
M7 — Periódico Mente Política y Empresarial
Inteligencia Electoral Zacatlán · JCLY Morena 2026
Sprint 4 · Marzo 2026
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
import os
from io import StringIO

# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, '..', 'data')

# ── Paleta M1 (consistencia visual) ──────────────────────────────────────────
COLOR_MAP = {
    "Prioritaria":   "#e63946",
    "Consolidacion": "#f4a261",
    "Consolidación": "#f4a261",
    "Mantenimiento": "#2a9d8f",
}

COLOR_CANAL = {
    "Brigadas":            "#004a6e",
    "Reunión Multinivel":  "#7c3aed",
    "Acción directa":      "#f4a261",
}

TEMAS_ICONO = {
    "Agua potable":       "💧",
    "Inseguridad":        "🔒",
    "Economía y empleo":  "💼",
    "Calles y pavimento": "🛣️",
    "Alumbrado público":  "💡",
    "Salud y campo":      "🏥",
}

# ── CSS ───────────────────────────────────────────────────────────────────────

# ── Demo mode — no modificar ────────────────────────────────────────────────
from demo_mode import check_demo_mode
check_demo_mode()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

[data-testid="stSidebar"] { background-color: #004a6e !important; }
[data-testid="stSidebar"] * { color: #e8edf5 !important; }
[data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: #004a6e !important;
    border-color: #007cab !important;
}

.pie-header {
    background: linear-gradient(135deg, #004a6e 0%, #007cab 100%);
    padding: 1.4rem 2rem; border-radius: 10px; margin-bottom: 1.2rem;
}
.pie-header h1 { color: #fff; font-size: 1.6rem; font-weight: 700; margin: 0; }
.pie-header p  { color: #93c5fd; font-size: 0.9rem; margin: 0.2rem 0 0; }

.metric-card {
    background: #f8fafc; border-left: 4px solid #007cab;
    border-radius: 8px; padding: 0.9rem 1rem; margin-bottom: 0.5rem;
}
.metric-card.rojo    { border-left-color: #e63946; }
.metric-card.naranja { border-left-color: #f4a261; }
.metric-card.verde   { border-left-color: #2a9d8f; }
.metric-card.morado  { border-left-color: #7c3aed; }
.metric-card .val    { font-size: 1.9rem; font-weight: 700; color: #1e293b; line-height: 1; }
.metric-card .lbl    { font-size: 0.78rem; color: #64748b; margin-top: 0.2rem; }
.metric-card .sub    { font-size: 0.74rem; color: #94a3b8; margin-top: 0.1rem; }

.section-title {
    font-size: 1.05rem; font-weight: 700; color: #1e293b;
    border-left: 4px solid #e63946; padding-left: 10px;
    margin: 1.2rem 0 0.8rem;
}

.alerta-roja {
    background: #fde8ea; border: 1px solid #e63946;
    border-radius: 8px; padding: 0.7rem 1rem; margin-bottom: 0.8rem;
    font-size: 0.88rem; color: #7f1d1d;
}
.alerta-ambar {
    background: #fef3e8; border: 1px solid #f4a261;
    border-radius: 8px; padding: 0.7rem 1rem; margin-bottom: 0.8rem;
    font-size: 0.88rem; color: #78350f;
}
.alerta-verde {
    background: #e8f5f3; border: 1px solid #2a9d8f;
    border-radius: 8px; padding: 0.7rem 1rem; margin-bottom: 0.8rem;
    font-size: 0.88rem; color: #065f46;
}

.sugerencia-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 14px 16px; margin-bottom: 8px;
    border-left: 4px solid #007cab;
}
.sugerencia-card.prioritaria { border-left-color: #e63946; background: #fde8ea10; }
.sugerencia-card.consolidacion { border-left-color: #f4a261; }
.sugerencia-card.mantenimiento { border-left-color: #2a9d8f; }

.pie-footer {
    font-size: 0.72rem; color: #94a3b8; text-align: center;
    margin-top: 2rem; padding-top: 0.8rem; border-top: 1px solid #e2e8f0;
}
</style>
""", unsafe_allow_html=True)


# ── Carga de datos ────────────────────────────────────────────────────────────
@st.cache_data
def cargar_spt():
    try:
        return pd.read_csv(os.path.join(DATA, 'spt_secciones_1.csv'))
    except Exception:
        return pd.DataFrame()

@st.cache_data
def cargar_clusters():
    try:
        return pd.read_csv(os.path.join(DATA, 'clusters_total.csv'))
    except Exception:
        return pd.DataFrame()

@st.cache_data
def cargar_csv(contenido: bytes, nombre: str) -> pd.DataFrame:
    return pd.read_csv(StringIO(contenido.decode('utf-8-sig')))

spt_df      = cargar_spt()
clusters_df = cargar_clusters()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📰 Periódico")
    st.markdown("*Mente Política y Empresarial*")
    st.markdown("---")

    st.markdown("**📂 Cargar datos del periódico**")
    f_ediciones = st.file_uploader("CSV de ediciones",       type="csv", key="ed")
    f_planeada  = st.file_uploader("CSV distribución planeada", type="csv", key="pl")
    f_real      = st.file_uploader("CSV distribución real",  type="csv", key="re")

    st.markdown("---")
    st.markdown("**📅 Filtros**")

    st.markdown("---")
    with st.expander("ℹ️ ¿Cómo funciona M7?"):
        st.markdown("""
**Periódico Mente Política y Empresarial** convierte los datos del territorio en decisiones editoriales.

- 📍 **Zonas de distribución** — qué secciones priorizar por edición
- 🧠 **Sugerencia de contenidos** — cruza arquetipos, encuesta y necesidades M6
- 📦 **Registro de distribución** — planeado vs entregado
- 📊 **Cobertura combinada** — brigadas + reuniones + periódico

**Periodicidad:** mensual · **Fuente:** Bubble → CSV
        """)

# ── Cargar datos — automático desde data/ o desde uploader ───────────────────
def intentar_cargar(uploader, nombre_auto):
    if uploader is not None:
        return cargar_csv(uploader.read(), uploader.name)
    ruta = os.path.join(DATA, nombre_auto)
    if os.path.exists(ruta):
        return pd.read_csv(ruta)
    return None

df_ed = intentar_cargar(f_ediciones, "m7_ediciones.csv")
df_pl = intentar_cargar(f_planeada,  "m7_dist_planeada.csv")
df_re = intentar_cargar(f_real,      "m7_dist_real.csv")

DEMO = df_ed is None or df_pl is None

# ── Datos mínimos embebidos si no hay archivos ────────────────────────────────
if DEMO:
    df_ed = pd.DataFrame({
        "id_edicion_text":       ["ED-2026-01","ED-2026-02","ED-2026-03"],
        "numero_edicion_number": [1, 2, 3],
        "fecha_edicion_date":    ["2026-02-01","2026-03-01","2026-04-01"],
        "tema_principal_text":   [
            "Acceso al agua: propuesta de redes de distribución en comunidades rurales",
            "Seguridad comunitaria: modelo de vigilancia vecinal y alumbrado",
            "Acceso al agua: propuesta de redes de distribución en comunidades rurales",
        ],
        "mes_edicion_option": ["Febrero 2026","Marzo 2026","Abril 2026"],
    })
    secciones_demo = [2486,2471,2489,2488,2467,2473,2485,2809,2461,2463]
    clasifs_demo   = ["Prioritaria","Prioritaria","Prioritaria","Prioritaria",
                      "Consolidacion","Consolidacion","Consolidacion","Consolidacion",
                      "Mantenimiento","Mantenimiento"]
    rows_pl, rows_re = [], []
    for ed_n in [1,2,3]:
        for sec, clasif in zip(secciones_demo, clasifs_demo):
            ej = 200 if clasif=="Prioritaria" else 120 if clasif=="Consolidacion" else 60
            rows_pl.append({"id_edicion_text":f"ED-2026-0{ed_n}","numero_edicion_number":ed_n,
                             "seccion_electoral_text":sec,"clasificacion_spt":clasif,
                             "ejemplares_planeados_number":ej,
                             "canal_distribucion_option":["Brigadas","Reunión Multinivel","Acción directa"][ed_n%3],
                             "problematica_principal":["Agua potable","Inseguridad","Economía y empleo",
                                                       "Agua potable","Inseguridad","Economía y empleo",
                                                       "Agua potable","Salud y campo","Economía y empleo","Inseguridad"][secciones_demo.index(sec)]})
            if ed_n < 3:
                rows_re.append({"id_edicion_text":f"ED-2026-0{ed_n}","numero_edicion_number":ed_n,
                                 "seccion_electoral_text":sec,
                                 "ejemplares_planeados_number":ej,
                                 "ejemplares_entregados_number":int(ej*0.88),
                                 "tipo_distribuidor_option":"Promotor de brigada",
                                 "fecha_distribucion_date":f"2026-0{ed_n+1}-10"})
    df_pl = pd.DataFrame(rows_pl)
    df_re = pd.DataFrame(rows_re) if rows_re else pd.DataFrame()

# ── Selector de edición ───────────────────────────────────────────────────────
ediciones_disp = df_ed.sort_values("numero_edicion_number", ascending=False)
opciones_ed = [
    f"Edición {int(r['numero_edicion_number'])} · {r['mes_edicion_option']}"
    for _, r in ediciones_disp.iterrows()
]
with st.sidebar:
    ed_sel_label = st.selectbox("Edición", opciones_ed)
    ed_sel_num   = int(ed_sel_label.split(" ")[1])

ed_actual  = df_ed[df_ed["numero_edicion_number"] == ed_sel_num].iloc[0]
pl_actual  = df_pl[df_pl["numero_edicion_number"] == ed_sel_num].copy()
re_actual  = df_re[df_re["numero_edicion_number"] == ed_sel_num].copy() if df_re is not None and len(df_re) > 0 else pd.DataFrame()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="pie-header">
  <h1>📰 M7 · Periódico Mente Política y Empresarial</h1>
  <p>¿Qué le decimos a cada zona esta edición? · Distribución territorial · Sugerencia de contenidos · Cobertura impresa</p>
</div>
""", unsafe_allow_html=True)

if DEMO:
    st.markdown("""
    <div class="alerta-ambar">
    ⚠️ <strong>Modo demostración</strong> — Sube los CSV de ediciones y distribución desde el panel lateral para ver datos reales.
    </div>
    """, unsafe_allow_html=True)

# ── TARJETA DE EDICIÓN ACTIVA ─────────────────────────────────────────────────
total_planeados  = int(pl_actual["ejemplares_planeados_number"].sum()) if len(pl_actual) > 0 else 0
total_entregados = int(re_actual["ejemplares_entregados_number"].sum()) if len(re_actual) > 0 else 0
secciones_plan   = pl_actual["seccion_electoral_text"].nunique() if len(pl_actual) > 0 else 0
secciones_real   = re_actual["seccion_electoral_text"].nunique() if len(re_actual) > 0 else 0
pct_cobertura    = round(total_entregados / total_planeados * 100, 1) if total_planeados > 0 else 0
es_planeada      = len(re_actual) == 0

st.markdown(f"""
<div style='background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
     padding:16px 20px;margin-bottom:16px;border-left:4px solid #004a6e;'>
  <div style='font-size:0.75rem;color:#64748b;font-weight:600;text-transform:uppercase;
       letter-spacing:0.08em;margin-bottom:6px;'>
    Edición {int(ed_actual['numero_edicion_number'])} · {ed_actual['mes_edicion_option']}
    {"&nbsp; <span style='background:#f4a261;color:white;border-radius:4px;padding:2px 8px;font-size:11px;'>📋 Planeada</span>" if es_planeada else "&nbsp; <span style='background:#2a9d8f;color:white;border-radius:4px;padding:2px 8px;font-size:11px;'>✅ En distribución</span>"}
  </div>
  <div style='font-size:1.05rem;font-weight:700;color:#1e293b;'>
    {ed_actual['tema_principal_text']}
  </div>
</div>
""", unsafe_allow_html=True)

# ── MÉTRICAS ──────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-card">
      <div class="val">{total_planeados:,}</div>
      <div class="lbl">Ejemplares planeados</div>
      <div class="sub">{secciones_plan} secciones · edición {ed_sel_num}</div>
    </div>""", unsafe_allow_html=True)
with c2:
    col_c = "verde" if pct_cobertura >= 80 else "naranja" if pct_cobertura >= 50 else "rojo"
    st.markdown(f"""
    <div class="metric-card {col_c}">
      <div class="val">{total_entregados:,}</div>
      <div class="lbl">Ejemplares entregados · {pct_cobertura:.0f}%</div>
      <div class="sub">{'Cobertura completa ✅' if pct_cobertura >= 90 else 'En proceso' if pct_cobertura > 0 else 'Pendiente de distribución'}</div>
    </div>""", unsafe_allow_html=True)
with c3:
    sin_cobertura = secciones_plan - secciones_real
    col_s = "rojo" if sin_cobertura > 0 else "verde"
    st.markdown(f"""
    <div class="metric-card {col_s}">
      <div class="val">{sin_cobertura}</div>
      <div class="lbl">Secciones sin entrega confirmada</div>
      <div class="sub">de {secciones_plan} secciones planeadas</div>
    </div>""", unsafe_allow_html=True)
with c4:
    # Cobertura combinada desde session_state M6
    reuniones_activas = len(st.session_state.get("nodos_multinivel", []))
    st.markdown(f"""
    <div class="metric-card morado">
      <div class="val">{reuniones_activas}</div>
      <div class="lbl">Secciones con Nodos Multinivel (M6)</div>
      <div class="sub">canales adicionales de distribución</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── MAPA DE DISTRIBUCIÓN ──────────────────────────────────────────────────────
st.markdown('<div class="section-title">📍 Mapa de distribución — cobertura por sección</div>',
            unsafe_allow_html=True)

col_mapa, col_detalle = st.columns([2, 1])

with col_mapa:
    m = folium.Map(location=[19.935, -97.960], zoom_start=11, tiles='CartoDB positron')

    # ── Capa 1: Coroplético SPT ───────────────────────────────────────────────
    geojson_path = os.path.join(DATA, 'zacatlan_secciones.geojson')
    if os.path.exists(geojson_path) and len(spt_df) > 0:
        import json
        with open(geojson_path) as f:
            geojson_data = json.load(f)
        spt_lookup = spt_df.set_index('seccion')[['SPT','clasificacion','ambito_iter']].to_dict('index')

        def spt_style(feature):
            sec   = int(feature['properties'].get('SECCION', 0))
            info  = spt_lookup.get(sec, {})
            clasif = str(info.get('clasificacion', ''))
            color = {"Prioritaria":"#e63946","Consolidacion":"#f4a261","Consolidación":"#f4a261","Mantenimiento":"#2a9d8f"}.get(clasif, "#94a3b8")
            return {'fillColor': color, 'color': '#ffffff', 'weight': 1.2, 'fillOpacity': 0.35}

        folium.GeoJson(
            geojson_data,
            style_function=spt_style,
            highlight_function=lambda f: {'weight': 2.5, 'color': '#1e293b', 'fillOpacity': 0.6},
            tooltip=folium.GeoJsonTooltip(fields=['SECCION'], aliases=['Sección:']),
            name='SPT',
        ).add_to(m)

    # ── Capa 2: Círculos de distribución ──────────────────────────────────────
    if len(pl_actual) > 0:
        # Merge con SPT para coordenadas aproximadas
        pl_map = pl_actual.copy()
        if len(spt_df) > 0:
            pl_map = pl_map.merge(
                spt_df[['seccion','clasificacion']],
                left_on='seccion_electoral_text', right_on='seccion', how='left',
                suffixes=('', '_spt')
            )

        # Coordenadas aproximadas por sección
        coords_base = {
            2461:(19.933,-97.961), 2463:(19.935,-97.958), 2465:(19.930,-97.955),
            2467:(19.928,-97.963), 2470:(19.920,-97.950), 2471:(19.980,-97.940),
            2473:(19.940,-97.970), 2474:(19.950,-97.975), 2475:(19.945,-97.945),
            2478:(19.910,-97.935), 2480:(19.960,-97.930), 2481:(19.915,-97.968),
            2482:(19.905,-97.955), 2484:(19.900,-97.940), 2485:(19.895,-97.930),
            2486:(19.925,-97.965), 2488:(19.870,-97.920), 2489:(19.915,-97.970),
            2727:(19.938,-97.953), 2809:(19.875,-97.945), 2895:(19.860,-97.960),
        }

        for _, row in pl_map.iterrows():
            sec    = int(row["seccion_electoral_text"])
            ej_pl  = int(row.get("ejemplares_planeados_number", 0))
            canal  = str(row.get("canal_distribucion_option", "Brigadas"))
            clasif = str(row.get("clasificacion_spt", row.get("clasificacion_spt", "")))
            prob   = str(row.get("problematica_principal", ""))

            # Verificar si ya se entregó
            re_sec = re_actual[re_actual["seccion_electoral_text"] == sec] if len(re_actual) > 0 else pd.DataFrame()
            entregado = len(re_sec) > 0
            ej_re  = int(re_sec["ejemplares_entregados_number"].sum()) if entregado else 0
            pct_re = round(ej_re / ej_pl * 100, 0) if ej_pl > 0 else 0

            lat_b, lon_b = coords_base.get(sec, (19.935, -97.960))
            color_circ = COLOR_MAP.get(clasif, "#007cab")
            radio = 6 + ej_pl // 30

            estado_html = (
                f"<span style='color:#2a9d8f;font-weight:700;'>✅ {ej_re:,} entregados ({pct_re:.0f}%)</span>"
                if entregado
                else "<span style='color:#e63946;font-weight:700;'>⏳ Pendiente</span>"
            )

            popup_html = (
                f"<div style='font-family:sans-serif;font-size:13px;min-width:180px'>"
                f"<b>Sección {sec}</b><br>"
                f"<span style='color:#64748b;font-size:11px;'>{clasif}</span><br><br>"
                f"📦 <b>{ej_pl:,}</b> ejemplares planeados<br>"
                f"📣 Canal: {canal}<br>"
                f"{TEMAS_ICONO.get(prob,'')} {prob}<br><br>"
                f"{estado_html}</div>"
            )

            folium.CircleMarker(
                location=[lat_b, lon_b],
                radius=radio,
                color='#ffffff',
                weight=2,
                fill=True,
                fill_color=color_circ,
                fill_opacity=0.85 if entregado else 0.45,
                popup=folium.Popup(popup_html, max_width=220),
                tooltip=f"§{sec} · {ej_pl:,} ej. · {'✅' if entregado else '⏳'}",
            ).add_to(m)

    # Leyenda
    legend_html = (
        "<div style='position:fixed;bottom:30px;left:30px;z-index:1000;"
        "background:white;padding:12px 16px;border-radius:8px;"
        "border:1px solid #e2e8f0;font-size:12px;font-family:sans-serif;"
        "box-shadow:0 2px 8px rgba(0,0,0,0.08)'>"
        "<b>Clasificación SPT</b><br>"
        "<span style='color:#e63946'>■</span> Prioritaria<br>"
        "<span style='color:#f4a261'>■</span> Consolidación<br>"
        "<span style='color:#2a9d8f'>■</span> Mantenimiento<br><br>"
        "<b>Distribución</b><br>"
        "● Sólido = entregado &nbsp; ○ Tenue = pendiente<br>"
        "<i style='color:#94a3b8'>Tamaño = volumen de ejemplares</i>"
        "</div>"
    )
    m.get_root().html.add_child(folium.Element(legend_html))
    st_folium(m, width=None, height=460, returned_objects=[])

with col_detalle:
    st.markdown("**Distribución por sección**")
    if len(pl_actual) > 0:
        tabla = pl_actual[["seccion_electoral_text","clasificacion_spt",
                            "ejemplares_planeados_number","canal_distribucion_option"]].copy()
        tabla.columns = ["Sección","Clasificación","Planeados","Canal"]

        # Agregar entregados
        if len(re_actual) > 0:
            re_agg = re_actual.groupby("seccion_electoral_text")["ejemplares_entregados_number"].sum().reset_index()
            re_agg.columns = ["Sección","Entregados"]
            tabla = tabla.merge(re_agg, on="Sección", how="left")
            tabla["Entregados"] = tabla["Entregados"].fillna(0).astype(int)
        else:
            tabla["Entregados"] = 0

        tabla = tabla.sort_values("Planeados", ascending=False).reset_index(drop=True)

        def highlight_tabla(row):
            bg = {"Prioritaria":"#fde8ea","Consolidacion":"#fef3e8",
                  "Consolidación":"#fef3e8","Mantenimiento":"#e8f5f3"}.get(row["Clasificación"],"")
            return [f"background-color:{bg}"] * len(row)

        st.dataframe(
            tabla.style.apply(highlight_tabla, axis=1),
            hide_index=True, height=300, use_container_width=True,
            column_config={"Sección": st.column_config.NumberColumn(format="%d")}
        )

    # Alertas secciones sin cobertura
    if len(pl_actual) > 0 and len(spt_df) > 0:
        prioritarias = spt_df[spt_df["SPT"] >= 70]["seccion"].tolist()
        secs_planeadas = set(pl_actual["seccion_electoral_text"].tolist())
        secs_sin_plan  = [s for s in prioritarias if s not in secs_planeadas]
        if secs_sin_plan:
            st.markdown(f"""
            <div class="alerta-roja">
            ⚠️ <b>Secciones PRIORITARIAS sin distribución planeada:</b><br>
            {', '.join([f'§{s}' for s in secs_sin_plan])}
            </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── MOTOR DE SUGERENCIA DE CONTENIDOS ─────────────────────────────────────────
st.markdown('<div class="section-title">🧠 Sugerencia de contenidos — ¿qué poner en esta edición?</div>',
            unsafe_allow_html=True)

st.caption("Cruza el perfil de votante (M3), problemáticas de encuesta y necesidades del territorio (M6) para sugerir los temas más relevantes por zona.")

# ── Construir sugerencias por sección ────────────────────────────────────────
ARQUETIPOS_AGENDA = {
    "U0": "Economía y empleo",    "U1": "Inseguridad",
    "U2": "Economía y empleo",    "U3": "Corrupción",
    "R0": "Agua potable",         "R1": "Agua potable",
    "R2": "Salud y campo",        "R3": None,
    "R4": "Calles y pavimento",
}

sugerencias = []
if len(pl_actual) > 0:
    for _, row in pl_actual.iterrows():
        sec    = int(row["seccion_electoral_text"])
        clasif = str(row.get("clasificacion_spt", ""))
        prob   = str(row.get("problematica_principal", ""))
        arq    = str(row.get("arq_dominante", ""))

        # Fuente 1: problemática de encuesta
        tema_encuesta = prob

        # Fuente 2: agenda del arquetipo
        tema_arq = ARQUETIPOS_AGENDA.get(arq, prob)

        # Fuente 3: cuadro de necesidades M6 (session_state)
        nodos_ss = st.session_state.get("nodos_multinivel", [])
        tema_m6  = None
        for nodo in nodos_ss:
            if nodo.get("seccion") == sec:
                tema_m6 = nodo.get("necesidad_top", None)
                break

        # Consenso: si encuesta y arquetipo coinciden → alta confianza
        confianza = "Alta" if tema_encuesta == tema_arq else "Media"
        tema_final = tema_encuesta  # encuesta tiene prioridad

        sugerencias.append({
            "seccion":     sec,
            "clasificacion": clasif,
            "tema_final":  tema_final,
            "confianza":   confianza,
            "fuentes":     f"Encuesta + Arquetipo {arq}" + (" + M6" if tema_m6 else ""),
            "icono":       TEMAS_ICONO.get(tema_final, "📌"),
        })

# Agrupar por tema para ver cuáles dominan esta edición
if sugerencias:
    df_sug = pd.DataFrame(sugerencias)
    temas_count = df_sug.groupby("tema_final").agg(
        n_secciones=("seccion","count"),
        alta_confianza=("confianza", lambda x: (x=="Alta").sum()),
    ).reset_index().sort_values("n_secciones", ascending=False)

    col_s1, col_s2 = st.columns([1, 2])

    with col_s1:
        st.markdown("**Temas dominantes esta edición**")
        fig_temas = go.Figure(go.Bar(
            x=temas_count["n_secciones"],
            y=[f"{TEMAS_ICONO.get(t,'📌')} {t}" for t in temas_count["tema_final"]],
            orientation="h",
            marker_color=["#e63946" if i==0 else "#f4a261" if i==1 else "#007cab"
                          for i in range(len(temas_count))],
            text=temas_count["n_secciones"],
            textposition="outside",
        ))
        fig_temas.update_layout(
            height=260, margin=dict(l=0,r=30,t=10,b=10),
            xaxis_title="Secciones",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="#e2e8f0"),
            font=dict(family="DM Sans", size=12, color="#1e293b"),
        )
        st.plotly_chart(fig_temas, use_container_width=True)

    with col_s2:
        st.markdown("**Sugerencia por sección prioritaria**")
        df_pri = df_sug[df_sug["clasificacion"].isin(["Prioritaria"])].copy()
        if len(df_pri) == 0:
            df_pri = df_sug.head(6)

        for _, row in df_pri.iterrows():
            color_cls = {"Prioritaria":"prioritaria","Consolidacion":"consolidacion",
                         "Consolidación":"consolidacion","Mantenimiento":"mantenimiento"}.get(row["clasificacion"],"")
            badge_conf = (
                "<span style='background:#2a9d8f;color:white;border-radius:4px;padding:1px 7px;font-size:10px;'>Alta confianza</span>"
                if row["confianza"] == "Alta"
                else "<span style='background:#f4a261;color:white;border-radius:4px;padding:1px 7px;font-size:10px;'>Media confianza</span>"
            )
            st.markdown(f"""
            <div class='sugerencia-card {color_cls}'>
              <div style='display:flex;justify-content:space-between;align-items:center;'>
                <span style='font-weight:700;color:#1e293b;'>§ {row['seccion']}</span>
                {badge_conf}
              </div>
              <div style='margin-top:6px;font-size:0.95rem;'>
                {row['icono']} <b>{row['tema_final']}</b>
              </div>
              <div style='font-size:0.75rem;color:#64748b;margin-top:3px;'>
                Fuentes: {row['fuentes']}
              </div>
            </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── COBERTURA COMBINADA ───────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Cobertura combinada — periódico + brigadas + reuniones</div>',
            unsafe_allow_html=True)

st.caption("Muestra qué canales llegaron a cada sección. El objetivo es que ninguna sección prioritaria quede sin al menos dos canales.")

if len(spt_df) > 0:
    df_cob = spt_df[["seccion","clasificacion","SPT","ambito_iter"]].copy()
    df_cob.columns = ["Sección","Clasificación","SPT","Ámbito"]

    # Canal periódico
    secs_periodico = set(re_actual["seccion_electoral_text"].tolist()) if len(re_actual) > 0 else set()
    secs_plan_set  = set(pl_actual["seccion_electoral_text"].tolist()) if len(pl_actual) > 0 else set()
    df_cob["📰 Periódico"] = df_cob["Sección"].apply(
        lambda s: "✅ Entregado" if s in secs_periodico else ("📋 Planeado" if s in secs_plan_set else "—")
    )

    # Canal brigadas (desde inducción)
    # Simplificado: si SPT > 0 y hay datos de inducción, asumir cobertura
    df_cob["🚶 Brigadas"] = df_cob["Clasificación"].apply(
        lambda c: "✅" if c in ["Prioritaria","Consolidacion","Consolidación"] else "—"
    )

    # Canal reuniones M6
    nodos_ss    = st.session_state.get("nodos_multinivel", [])
    secs_nodos  = {n.get("seccion") for n in nodos_ss}
    df_cob["🏘️ Reuniones"] = df_cob["Sección"].apply(
        lambda s: "✅" if s in secs_nodos else "—"
    )

    # Score de cobertura
    df_cob["Canales"] = (
        (df_cob["📰 Periódico"] != "—").astype(int) +
        (df_cob["🚶 Brigadas"]  == "✅").astype(int) +
        (df_cob["🏘️ Reuniones"] == "✅").astype(int)
    )

    # Colorear por cobertura
    def color_cob(row):
        if row["Clasificación"] in ["Prioritaria"] and row["Canales"] < 2:
            return ["background-color:#fde8ea"] * len(row)
        if row["Canales"] == 3:
            return ["background-color:#e8f5f3"] * len(row)
        return [""] * len(row)

    df_cob["SPT"] = df_cob["SPT"].round(1)
    df_cob = df_cob.sort_values("SPT", ascending=False)

    st.dataframe(
        df_cob.style.apply(color_cob, axis=1),
        hide_index=True,
        height=400,
        use_container_width=True,
        column_config={
            "Sección": st.column_config.NumberColumn(format="%d"),
            "SPT":     st.column_config.NumberColumn(format="%.1f"),
        }
    )

    # Alertas prioritarias sin cobertura completa
    prioritarias_baja = df_cob[
        (df_cob["Clasificación"] == "Prioritaria") & (df_cob["Canales"] < 2)
    ]
    if len(prioritarias_baja) > 0:
        secs_alerta = ", ".join([f"§{int(s)}" for s in prioritarias_baja["Sección"]])
        st.markdown(f"""
        <div class="alerta-roja">
        ⚠️ <b>Secciones PRIORITARIAS con menos de 2 canales de cobertura:</b><br>
        {secs_alerta}<br>
        <span style='font-size:0.82rem;'>Asegura al menos periódico + brigadas en estas zonas antes del cierre de edición.</span>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── REGISTRO DE DISTRIBUCIÓN ──────────────────────────────────────────────────
st.markdown('<div class="section-title">📦 Registro de distribución — avance de entrega</div>',
            unsafe_allow_html=True)

if len(re_actual) > 0:
    # Gráfica planeado vs entregado
    merge_dist = pl_actual[["seccion_electoral_text","ejemplares_planeados_number",
                             "clasificacion_spt"]].copy()
    re_agg = re_actual.groupby("seccion_electoral_text")["ejemplares_entregados_number"].sum().reset_index()
    merge_dist = merge_dist.merge(re_agg, on="seccion_electoral_text", how="left")
    merge_dist["ejemplares_entregados_number"] = merge_dist["ejemplares_entregados_number"].fillna(0)
    merge_dist = merge_dist.sort_values("ejemplares_planeados_number", ascending=True)

    colors_bar = [COLOR_MAP.get(c,"#007cab") for c in merge_dist["clasificacion_spt"]]

    fig_dist = go.Figure()
    fig_dist.add_trace(go.Bar(
        y=[f"§{int(s)}" for s in merge_dist["seccion_electoral_text"]],
        x=merge_dist["ejemplares_planeados_number"],
        name="Planeados",
        orientation="h",
        marker_color="rgba(0,0,0,0.08)",
        marker_line_color="#cbd5e1", marker_line_width=1,
    ))
    fig_dist.add_trace(go.Bar(
        y=[f"§{int(s)}" for s in merge_dist["seccion_electoral_text"]],
        x=merge_dist["ejemplares_entregados_number"],
        name="Entregados",
        orientation="h",
        marker_color=colors_bar,
        opacity=0.85,
    ))
    fig_dist.update_layout(
        barmode="overlay",
        height=max(300, len(merge_dist) * 22),
        margin=dict(l=0, r=30, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#e2e8f0", title="Ejemplares"),
        font=dict(family="DM Sans", size=11, color="#1e293b"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_dist, use_container_width=True)

    # Tabla detalle
    with st.expander("📋 Ver tabla detallada de distribución"):
        cols_re = [c for c in ["seccion_electoral_text","ejemplares_planeados_number",
                                "ejemplares_entregados_number","tipo_distribuidor_option",
                                "fecha_distribucion_date","observaciones_text"]
                   if c in re_actual.columns]
        df_re_show = re_actual[cols_re].copy()
        df_re_show.columns = ["Sección","Planeados","Entregados","Distribuidor",
                               "Fecha","Observaciones"][:len(cols_re)]
        st.dataframe(df_re_show, hide_index=True, use_container_width=True)

        # Exportar
        csv_exp = df_re_show.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Exportar registro de distribución (CSV)",
            data=csv_exp,
            file_name=f"m7_distribucion_ed{ed_sel_num}.csv",
            mime="text/csv",
        )
else:
    st.markdown("""
    <div class="alerta-ambar">
    📋 Esta edición aún no tiene registros de distribución — está en fase de planeación.
    Sube el CSV de distribución real cuando inicie la entrega.
    </div>""", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="pie-footer">
  Inteligencia Electoral Zacatlán · JCLY Morena 2026 · Confidencial · Marzo 2026
</div>
""", unsafe_allow_html=True)
