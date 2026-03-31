"""
M4 — Historial Electoral por Sección
Inteligencia Electoral Zacatlán · JCLY Morena 2026
¿Qué tan confiable es ese territorio?
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import os

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="M4 · Historial Electoral · Zacatlán",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Demo mode — no modificar ────────────────────────────────────────────────
from demo_mode import check_demo_mode
check_demo_mode()


# ─── PALETA Y ESTILOS ─────────────────────────────────────────────────────────
COLORES = {
    "rojo":         "#e63946",
    "naranja":      "#f4a261",
    "verde":        "#2a9d8f",
    "azul":         "#457b9d",
    "gris_claro":   "#adb5bd",
    "gris_oscuro":  "#6c757d",
    "fondo_riesgo": "#FDEDEC",
    "fondo_aviso":  "#FEF9E7",
    "fondo_ok":     "#EAF6EF",
    "fondo_info":   "#EBF0FB",
    "fondo_neutro": "#F5F5F5",
    "morena":       "#8B1A1A",
    "pan":          "#003876",
    "pri":          "#006847",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Header principal */
.header-modulo {
    background: linear-gradient(135deg, #1a2744 0%, #2563eb 100%);
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 24px;
    color: white;
}
.header-modulo h1 {
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.header-modulo p {
    font-size: 0.95rem;
    opacity: 0.75;
    margin: 0;
}

/* Tarjetas métricas */
.tarjeta-metrica {
    background: white;
    border-radius: 10px;
    padding: 18px 20px;
    border-left: 4px solid #e63946;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    height: 100%;
}
.tarjeta-metrica.verde  { border-left-color: #2a9d8f; }
.tarjeta-metrica.naranja{ border-left-color: #f4a261; }
.tarjeta-metrica.azul   { border-left-color: #457b9d; }
.tarjeta-metrica .valor { font-size: 2rem; font-weight: 700; line-height: 1; margin: 4px 0; }
.tarjeta-metrica .label { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.5px; color: #6c757d; }
.tarjeta-metrica .contexto { font-size: 0.85rem; color: #444; margin-top: 4px; }

/* Ficha de sección */
.ficha-header {
    background: linear-gradient(135deg, #1a2744 0%, #2563eb 100%);
    border-radius: 12px 12px 0 0;
    padding: 22px 24px;
    color: white;
}
.ficha-header .seccion-num { font-size: 2rem; font-weight: 700; }
.ficha-header .ambito-tag  { font-size: 0.8rem; opacity: 0.7; margin-top: 2px; }
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
}
.badge-alerta  { background: #e63946; color: white; }
.badge-aviso   { background: #f4a261; color: white; }
.badge-solido  { background: #2a9d8f; color: white; }
.badge-parcial { background: #6c757d; color: white; }

/* Caja de instrucción táctica */
.caja-tactica {
    background: #FEF9E7;
    border: 1px solid #f4a261;
    border-radius: 8px;
    padding: 14px 16px;
    margin: 12px 0;
}
.caja-tactica .titulo-tactica { font-weight: 600; font-size: 0.9rem; }
.caja-tactica .desc-tactica   { font-size: 0.85rem; color: #444; margin-top: 4px; }

/* Caja alerta roja */
.caja-alerta-roja {
    background: #FDEDEC;
    border: 1px solid #e63946;
    border-radius: 8px;
    padding: 14px 16px;
    margin: 10px 0;
    font-size: 0.88rem;
}

/* Caja info parcial */
.caja-parcial {
    background: #FEF9E7;
    border: 1px solid #f4a261;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 10px 0;
    font-size: 0.85rem;
    color: #7d4e00;
}

/* Métrica de tendencia */
.tendencia-bloque {
    background: #F5F5F5;
    border-radius: 8px;
    padding: 14px 16px;
    text-align: center;
}
.tendencia-bloque .flecha { font-size: 1.8rem; }
.tendencia-bloque .valor  { font-size: 1.1rem; font-weight: 600; }
.tendencia-bloque .label  { font-size: 0.75rem; color: #6c757d; text-transform: uppercase; }

/* Tabla */
.stDataFrame { border-radius: 8px; overflow: hidden; }

/* Sidebar */
.sidebar-titulo {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #6c757d;
    margin-bottom: 4px;
    font-weight: 600;
}

/* Separador */
.separador { height: 1px; background: #e9ecef; margin: 20px 0; }

    [data-testid="stSidebar"] {
        background-color: #1a2744 !important;
    }
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {
        color: #e8edf5 !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stMultiSelect > div > div {
        background-color: #243058 !important;
        border-color: #3d5a99 !important;
    }
</style>
""", unsafe_allow_html=True)


# ─── DATOS EMBEBIDOS ──────────────────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    _script = os.path.dirname(os.path.abspath(__file__))
    _data   = os.path.join(_script, "..", "data")
    rutas = [
        _data,
        _script,
        os.path.join(_script, "data"),
        os.path.join(_script, "processed"),
        os.path.join(os.path.expanduser("~"), "Inteligencia_Zacatlan", "processed"),
        "."
    ]

    def buscar(nombre):
        for r in rutas:
            p = os.path.join(r, nombre)
            if os.path.exists(p):
                return pd.read_csv(p)
        return None

    hist  = buscar("historico_electoral.csv")
    comp  = buscar("competitividad_secciones.csv")
    spt   = buscar("spt_secciones_1.csv")
    nuevas= buscar("secciones_nuevas_2024.csv")

    if any(df is None for df in [hist, comp, spt, nuevas]):
        faltantes = []
        if hist   is None: faltantes.append("historico_electoral.csv")
        if comp   is None: faltantes.append("competitividad_secciones.csv")
        if spt    is None: faltantes.append("spt_secciones_1.csv")
        if nuevas is None: faltantes.append("secciones_nuevas_2024.csv")
        st.error(f"⚠️ No se encontraron estos archivos en `processed/`:\n\n" +
                 "\n".join(f"- `{f}`" for f in faltantes) +
                 f"\n\nRuta buscada: `{_data}`")
        st.stop()

    # Dataset unificado
    base = spt[['seccion','ambito_iter','SPT','clasificacion','tactica_recomendada',
                'score_electoral_parcial','arq_dominante',
                'pct_no_alcanzados','pct_persuadibles',
                'pct_nucleo_duro','pct_no_convertibles']].copy()

    comp_sel = comp[['SECCION','pct_morena_2018','pct_morena_2021','pct_morena_2024',
                     'pct_pan_2024','ganador_2018','ganador_2021','ganador_2024',
                     'tendencia_morena','volatilidad_morena','margen_2024',
                     'participacion_2021','participacion_prom',
                     'clasificacion_electoral','pct_nulos_2024']
               ].rename(columns={'SECCION':'seccion'})

    merged = base.merge(comp_sel, on='seccion', how='left')

    nuevas_sel = nuevas[['SECCION','pct_morena','pct_pan','ganador']].rename(
        columns={'SECCION':'seccion','pct_morena':'_m24','pct_pan':'_p24','ganador':'_g24'})
    merged = merged.merge(nuevas_sel, on='seccion', how='left')

    mask = merged['score_electoral_parcial'] == True
    merged.loc[mask, 'pct_morena_2024'] = merged.loc[mask, '_m24']
    merged.loc[mask, 'pct_pan_2024']    = merged.loc[mask, '_p24']
    merged.loc[mask, 'ganador_2024']    = merged.loc[mask, '_g24']
    merged = merged.drop(columns=['_m24','_p24','_g24'])

    return merged, hist

df, hist_raw = cargar_datos()

# Geojson
@st.cache_data
def cargar_geojson():
    _script = os.path.dirname(os.path.abspath(__file__))
    _data   = os.path.join(_script, "..", "data")
    rutas = [
        _data,
        _script,
        os.path.join(_script, "data"),
        os.path.join(_script, "processed"),
        os.path.join(os.path.expanduser("~"), "Inteligencia_Zacatlan", "processed"),
        "."
    ]
    for r in rutas:
        p = os.path.join(r, "zacatlan_secciones.geojson")
        if os.path.exists(p):
            with open(p) as f:
                return json.load(f)
    return None

geojson = cargar_geojson()


# ─── HELPERS ──────────────────────────────────────────────────────────────────
AMBITO_LABELS = {
    "urbano":         "🏙️ Urbano",
    "rural_media":    "🌾 Rural Media",
    "rural_marginal": "🏔️ Rural Marginal",
}

SPT_LABELS = {
    "Prioritaria":   "🔴 Zona de máxima atención",
    "Consolidacion": "🟡 Zona de trabajo activo",
    "Mantenimiento": "🟢 Zona de base sólida",
}

CLASIF_HIST_LABELS = {
    "Favorable":  "🟢 Bastión — Morena gana consistentemente por margen amplio",
    "Competida":  "🟡 Zona disputada — Margen ajustado, resultado incierto",
    "Recuperable":"🔵 Recuperable — Perdimos pero la tendencia mejora",
    "En riesgo":  "🔴 En riesgo — Ganamos pero el margen se achica",
}

TACTIAS_LABELS = {
    "Brigadas de primer contacto urgentes":              "🚶 Primer contacto urgente",
    "Activacion y cierre de voto":                       "🤝 Activación y cierre",
    "Brigadas primer contacto + cierre":                 "🔄 Primer contacto + cierre",
    "Presencia regular y activacion de multiplicadores": "📣 Activar multiplicadores",
    "Activar base solida unicamente":                    "🛡️ Solo activar base sólida",
}

def clasif_margen(margen):
    """Asigna clasificación operativa por margen"""
    if pd.isna(margen):
        return "parcial"
    if margen < 5:
        return "riesgo"
    if margen < 15:
        return "disputada"
    if margen < 35:
        return "competida"
    return "solida"

def color_margen(margen):
    c = clasif_margen(margen)
    return {"riesgo": "#e63946", "disputada": "#f4a261",
            "competida": "#f4d35e", "solida": "#2a9d8f", "parcial": "#adb5bd"}[c]

def tendencia_texto(val):
    if pd.isna(val): return "—", "⚠️"
    if val >= 6:  return f"+{val:.1f} pts por ciclo", "📈"
    if val >= 4:  return f"+{val:.1f} pts por ciclo", "↗️"
    if val >= 0:  return f"+{val:.1f} pts por ciclo", "➡️"
    return f"{val:.1f} pts por ciclo", "📉"

def volatilidad_texto(val):
    if pd.isna(val): return "Sin dato"
    if val > 25: return "🔴 Alta — esta sección ha cambiado mucho entre elecciones"
    if val > 15: return "🟡 Media — cierta variabilidad histórica"
    return "🟢 Baja — comportamiento estable"

ALERTAS = {
    2472: "⚠️ Sección crítica: ganamos por solo 1.6 puntos en 2024. Un error operativo puede costar esta sección.",
    2486: "💡 Sección ancla: margen más alto del municipio (69.2 pts). Convertir esta base en multiplicadores.",
    2895: "⚠️ Solo tenemos datos de 2024. Alto núcleo duro (26%) — activar como brigadistas.",
}

SECCIONES_PARCIALES = [2727, 2808, 2809, 2895, 2896]



# ─── CLASIFICACIÓN POR MARGEN (calculada antes del sidebar) ───────────────────
def get_clasif_mapa(row):
    if row['score_electoral_parcial']:
        return "⚠️ Dato parcial"
    m = row['margen_2024']
    if pd.isna(m):  return "⚠️ Dato parcial"
    if m < 5:       return "🔴 En riesgo  (margen < 5 pts)"
    if m < 15:      return "🟠 Terreno frágil  (5–15 pts)"
    if m < 35:      return "🟡 Zona disputada  (15–35 pts)"
    return                 "🟢 Base sólida  (> 35 pts)"

df['clasif_mapa'] = df.apply(get_clasif_mapa, axis=1)

ORDEN_CLASIF = [
    "🔴 En riesgo  (margen < 5 pts)",
    "🟠 Terreno frágil  (5–15 pts)",
    "🟡 Zona disputada  (15–35 pts)",
    "🟢 Base sólida  (> 35 pts)",
    "⚠️ Dato parcial",
]
clasif_presentes = [c for c in ORDEN_CLASIF if c in df['clasif_mapa'].values]

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 M4 · Historial Electoral")
    st.markdown("*¿Qué tan confiable es cada territorio?*")
    st.markdown("---")

    st.markdown('<p class="sidebar-titulo">¿Qué secciones mostrar en el mapa?</p>', unsafe_allow_html=True)
    clasif_sel = st.multiselect(
        label="clasificacion_mapa",
        options=clasif_presentes,
        default=clasif_presentes,
        label_visibility="collapsed"
    )

    # Leyenda de categorías — siempre visible junto al filtro
    st.markdown("""
    <div style="font-size:0.78rem; color:#555; line-height:1.9; padding:8px 4px 4px 4px;">
        <div><b>🔴 En riesgo</b> — Ganamos por menos de 5 pts.<br>
             <span style="color:#888; padding-left:18px;">Un error operativo puede costar esta sección.</span></div>
        <div style="margin-top:4px"><b>🟠 Terreno frágil</b> — Margen de 5 a 15 pts.<br>
             <span style="color:#888; padding-left:18px;">Requiere atención activa.</span></div>
        <div style="margin-top:4px"><b>🟡 Zona disputada</b> — Margen de 15 a 35 pts.<br>
             <span style="color:#888; padding-left:18px;">Resultado no garantizado.</span></div>
        <div style="margin-top:4px"><b>🟢 Base sólida</b> — Margen mayor a 35 pts.<br>
             <span style="color:#888; padding-left:18px;">Territorio consolidado.</span></div>
        <div style="margin-top:4px"><b>⚠️ Dato parcial</b> — Solo tenemos resultado 2024.<br>
             <span style="color:#888; padding-left:18px;">Sin historial previo.</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Toggle secciones encuestadas
    st.markdown('<p class="sidebar-titulo">Capa adicional</p>', unsafe_allow_html=True)
    mostrar_encuesta = st.toggle(
        "Marcar secciones con encuesta real",
        value=True,
        help="Resalta con borde blanco las 19 secciones donde se levantó la encuesta. Las demás tienen perfil estimado."
    )

    st.markdown("---")
    st.markdown('<p class="sidebar-titulo">¿Qué sección quieres analizar en detalle?</p>', unsafe_allow_html=True)
    secciones_disp = sorted(df['seccion'].tolist())
    seccion_sel = st.selectbox(
        label="seccion",
        options=secciones_disp,
        index=secciones_disp.index(2472),
        label_visibility="collapsed"
    )

    st.markdown("---")
    with st.expander("ℹ️ ¿Cómo funciona esto?"):
        st.markdown("""
        Este módulo muestra el comportamiento electoral histórico de cada sección.

        **¿Qué es el margen?** La diferencia entre los votos de Morena y el segundo lugar en 2024. Un margen de 1.6 pts significa que casi perdemos.

        **¿Qué es la tendencia?** Cuántos puntos ha ganado Morena en promedio entre cada elección.

        **¿Por qué algunas secciones no tienen 2018 y 2021?** Son secciones redistritadas en 2024 sin historial previo.

        **Fuentes:** Resultados INE 2018, 2021, 2024.
        """)


# ─── FILTRADO — reactivo al sidebar ──────────────────────────────────────────
todos_seleccionados = set(clasif_sel) == set(clasif_presentes)
df_filtrado = df[df['clasif_mapa'].isin(clasif_sel)].copy() if clasif_sel else df.copy()
secciones_visibles = set(df_filtrado['seccion'].tolist())

# Secciones con encuesta real
SECCIONES_ENCUESTA = {2461,2463,2465,2467,2470,2471,2473,2474,2475,
                      2478,2480,2481,2482,2484,2485,2488,2727,2809,2895}

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-modulo">
    <h1>📊 M4 Historial Electoral por Sección</h1>
    <p>¿Qué tan confiable es ese territorio? · Resultados Morena 2018 → 2021 → 2024 · 33 secciones activas</p>
</div>
""", unsafe_allow_html=True)


# ─── TARJETAS RESUMEN ─────────────────────────────────────────────────────────
ganadas_2024 = df['pct_morena_2024'].notna().sum()  # todas las activas ganaron
margen_prom  = df['margen_2024'].mean()
sec_fragil   = df.loc[df['margen_2024'].idxmin(), 'seccion'] if df['margen_2024'].notna().any() else "—"
margen_fragil= df['margen_2024'].min()
sec_solida   = df.loc[df['margen_2024'].idxmax(), 'seccion'] if df['margen_2024'].notna().any() else "—"
margen_solida= df['margen_2024'].max()
en_riesgo    = (df['margen_2024'] < 10).sum()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="tarjeta-metrica verde">
        <div class="label">Secciones ganadas en 2024</div>
        <div class="valor" style="color:#2a9d8f">28 / 33</div>
        <div class="contexto">Morena ganó las 28 con historial completo</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="tarjeta-metrica azul">
        <div class="label">Margen promedio municipal 2024</div>
        <div class="valor" style="color:#457b9d">{margen_prom:.1f} pts</div>
        <div class="contexto">Ventaja sobre el segundo lugar</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="tarjeta-metrica" style="border-left-color:#e63946">
        <div class="label">Sección más frágil</div>
        <div class="valor" style="color:#e63946">{sec_fragil} · {margen_fragil:.1f} pts</div>
        <div class="contexto">⚠️ Margen mínimo — intervención urgente</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="tarjeta-metrica verde">
        <div class="label">Sección más sólida</div>
        <div class="valor" style="color:#2a9d8f">{sec_solida} · {margen_solida:.1f} pts</div>
        <div class="contexto">💡 Base para multiplicar el voto</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)


# ─── MAPA + FICHA ─────────────────────────────────────────────────────────────
col_mapa, col_ficha = st.columns([1.6, 1], gap="large")

with col_mapa:
    st.markdown("#### 🗺️ Mapa por margen de victoria 2024")
    st.caption("El color muestra qué tan amplia fue nuestra ventaja. Rojo = terreno frágil · Verde = base sólida")

    if geojson:
        import plotly.graph_objects as go_map

        # ── Capa 1: base gris (todas las secciones como referencia) ──────────
        df_base = df.copy()
        df_base['_gris'] = 0.5  # valor constante para color uniforme
        df_base['hover_sec'] = df_base['seccion'].astype(str)

        fig_mapa = go.Figure()

        # Traza base gris — solo visible cuando hay filtro activo
        if not todos_seleccionados:
            fig_mapa.add_trace(go.Choroplethmapbox(
                geojson=geojson,
                locations=df_base['seccion'],
                z=df_base['_gris'],
                featureidkey='properties.SECCION',
                colorscale=[[0, "#d6d6d6"], [1, "#d6d6d6"]],
                showscale=False,
                marker=dict(opacity=0.35, line_width=0.5, line_color='white'),
                hovertemplate='<b>Sección %{location}</b><br>No seleccionada en el filtro<extra></extra>',
                name='Referencia',
            ))

        # ── Capa 2: secciones filtradas coloreadas por margen ─────────────────
        df_mapa = df_filtrado.copy()
        df_mapa['margen_display'] = df_mapa['margen_2024'].fillna(-1)
        df_mapa['hover_margen']   = df_mapa['margen_2024'].apply(
            lambda x: f"{x:.1f} pts" if pd.notna(x) else "Solo dato 2024")
        df_mapa['hover_morena']   = df_mapa['pct_morena_2024'].apply(
            lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
        df_mapa['hover_encuesta'] = df_mapa['seccion'].apply(
            lambda x: "✅ Encuesta real" if x in SECCIONES_ENCUESTA else "🔄 Perfil estimado")
        df_mapa['clasif_display'] = df_mapa['clasif_mapa']

        # Escala de color: -1 (sin dato) → gris, 0→rojo, 15→naranja, 35→amarillo, 70→verde
        color_scale = [
            [0.0,  "#e63946"],
            [0.07, "#f4a261"],
            [0.21, "#f4d35e"],
            [0.50, "#2a9d8f"],
            [1.0,  "#1a6b5e"],
        ]

        fig_mapa.add_trace(go.Choroplethmapbox(
            geojson=geojson,
            locations=df_mapa['seccion'],
            z=df_mapa['margen_display'],
            featureidkey='properties.SECCION',
            colorscale=color_scale,
            zmin=-1, zmax=70,
            colorbar=dict(
                title="Margen<br>(pts)",
                tickvals=[-1, 0, 15, 35, 70],
                ticktext=["Sin dato", "0", "15", "35", "70+"],
                thickness=12, len=0.5,
            ),
            marker=dict(opacity=0.80, line_width=0.8, line_color='white'),
            customdata=df_mapa[['hover_margen','hover_morena','clasif_display',
                                'ambito_iter','hover_encuesta']].values,
            hovertemplate=(
                "<b>Sección %{location}</b><br>"
                "Ventaja 2024: %{customdata[0]}<br>"
                "% Morena 2024: %{customdata[1]}<br>"
                "Clasificación: %{customdata[2]}<br>"
                "Territorio: %{customdata[3]}<br>"
                "Datos: %{customdata[4]}<extra></extra>"
            ),
            name='Secciones',
        ))

        # ── Capa 3: punto + etiqueta en centroides de secciones encuestadas ──
        if mostrar_encuesta:
            centroides = []
            for feature in geojson.get('features', []):
                sec_id = feature['properties'].get('SECCION')
                if sec_id in SECCIONES_ENCUESTA:
                    coords = feature['geometry']['coordinates']
                    geom_type = feature['geometry']['type']
                    if geom_type == 'Polygon':
                        pts = coords[0]
                    elif geom_type == 'MultiPolygon':
                        pts = max(coords, key=lambda p: len(p[0]))[0]
                    else:
                        continue
                    lons = [p[0] for p in pts]
                    lats = [p[1] for p in pts]
                    centroides.append({
                        'seccion': sec_id,
                        'lon': sum(lons) / len(lons),
                        'lat': sum(lats) / len(lats),
                    })

            if centroides:
                df_cent = pd.DataFrame(centroides)
                fig_mapa.add_trace(go.Scattermapbox(
                    lat=df_cent['lat'],
                    lon=df_cent['lon'],
                    mode='markers+text',
                    marker=dict(
                        size=10,
                        color='#FFD166',
                        opacity=0.95,
                    ),
                    text=df_cent['seccion'].astype(str),
                    textposition='top center',
                    textfont=dict(
                        size=9,
                        color='#FFD166',
                        family='monospace',
                    ),
                    hovertemplate='<b>Sección %{text}</b><br>✅ Encuesta real<extra></extra>',
                    name='Con encuesta',
                ))

        fig_mapa.update_layout(
            mapbox=dict(
                style="carto-positron",
                zoom=11,
                center={"lat": 19.953, "lon": -97.958},
            ),
            height=470,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
        )

        st.plotly_chart(fig_mapa, use_container_width=True, config={
            "scrollZoom": True,
            "displayModeBar": True,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        })

        # Leyenda visual debajo del mapa
        enc_txt = " &nbsp;|&nbsp; <span style='color:#FFD166; font-weight:600;'>— Borde amarillo</span> = encuesta real (19 secciones)" if mostrar_encuesta else ""
        gris_txt = " &nbsp;|&nbsp; <b>Gris</b> = fuera del filtro (referencia)" if not todos_seleccionados else ""
        st.markdown(f"""
        <div style="display:flex; gap:12px; flex-wrap:wrap; font-size:0.77rem;
                    padding:6px 4px; color:#555; align-items:center;">
            <span>🔴 En riesgo</span>
            <span>🟠 Terreno frágil</span>
            <span>🟡 Zona disputada</span>
            <span>🟢 Base sólida</span>
            <span>⚪ Sin dato</span>
            {enc_txt}{gris_txt}
        </div>
        """, unsafe_allow_html=True)

    else:
        st.info("ℹ️ GeoJSON no encontrado — mostrando ranking visual")
        df_barras = df_filtrado.dropna(subset=['margen_2024']).sort_values('margen_2024')
        colores_bar = []
        for m in df_barras['margen_2024']:
            if m < 5:   colores_bar.append("#e63946")
            elif m < 15: colores_bar.append("#f4a261")
            elif m < 35: colores_bar.append("#f4d35e")
            else:        colores_bar.append("#2a9d8f")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=df_barras['margen_2024'],
            y=df_barras['seccion'].astype(str),
            orientation='h',
            marker_color=colores_bar,
            text=df_barras['margen_2024'].apply(lambda x: f"{x:.1f} pts"),
            textposition='outside',
        ))
        fig_bar.update_layout(
            height=600, margin=dict(l=0, r=40, t=10, b=10),
            xaxis_title="Ventaja sobre segundo lugar (pts)",
            yaxis_title="", showlegend=False,
            plot_bgcolor='white', xaxis=dict(gridcolor='#f0f0f0'),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.plotly_chart(fig_bar, use_container_width=True)


# ─── FICHA DE DETALLE ─────────────────────────────────────────────────────────
with col_ficha:
    row = df[df['seccion'] == seccion_sel].iloc[0]
    es_parcial  = bool(row['score_electoral_parcial'])
    margen      = row['margen_2024']
    morena_24   = row['pct_morena_2024']
    morena_21   = row.get('pct_morena_2021', None)
    morena_18   = row.get('pct_morena_2018', None)
    tendencia   = row.get('tendencia_morena', None)
    volatilidad = row.get('volatilidad_morena', None)
    ambito      = AMBITO_LABELS.get(row['ambito_iter'], row['ambito_iter'])
    spt_val     = row['SPT']
    spt_label   = SPT_LABELS.get(row['clasificacion'], row['clasificacion'])
    tactica     = TACTIAS_LABELS.get(row['tactica_recomendada'], row['tactica_recomendada'])

    # Badge de estado
    if es_parcial:
        badge = '<span class="badge badge-parcial">⚠️ Dato parcial</span>'
        badge_color = COLORES['gris_oscuro']
    elif pd.notna(margen) and margen < 5:
        badge = '<span class="badge badge-alerta">🔴 Zona en riesgo</span>'
        badge_color = COLORES['rojo']
    elif pd.notna(margen) and margen < 15:
        badge = '<span class="badge badge-aviso">🟡 Zona disputada</span>'
        badge_color = COLORES['naranja']
    elif row.get('clasificacion_electoral') == 'Favorable':
        badge = '<span class="badge badge-solido">🟢 Bastión</span>'
        badge_color = COLORES['verde']
    else:
        badge = '<span class="badge badge-aviso">🟡 Zona disputada</span>'
        badge_color = COLORES['naranja']

    st.markdown(f"""
    <div class="ficha-header">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <div class="seccion-num">Sección {seccion_sel}</div>
                <div class="ambito-tag">{ambito}</div>
            </div>
            <div style="text-align:right">{badge}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Alertas específicas
    if seccion_sel in ALERTAS:
        color_alerta = "#FDEDEC" if "⚠️" in ALERTAS[seccion_sel] else "#EAF6EF"
        border_alerta = "#e63946" if "⚠️" in ALERTAS[seccion_sel] else "#2a9d8f"
        st.markdown(f"""
        <div style="background:{color_alerta}; border:1px solid {border_alerta};
                    border-radius:8px; padding:12px 14px; margin:10px 0;
                    font-size:0.85rem;">
            {ALERTAS[seccion_sel]}
        </div>
        """, unsafe_allow_html=True)

    # Aviso historial parcial
    if es_parcial:
        st.markdown("""
        <div class="caja-parcial">
            ⚠️ Solo tenemos datos de 2024 — la tendencia no es calculable.<br>
            Esta sección fue creada en la redistritación electoral de 2024.
        </div>
        """, unsafe_allow_html=True)

    # Margen y Morena 2024 destacados
    col_a, col_b = st.columns(2)
    with col_a:
        color_v = COLORES['rojo'] if (pd.notna(margen) and margen < 10) else COLORES['verde']
        margen_txt = f"{margen:.1f} pts" if pd.notna(margen) else "—"
        st.markdown(f"""
        <div style="background:#F5F5F5; border-radius:8px; padding:14px; text-align:center; margin-top:10px;">
            <div style="font-size:0.72rem; text-transform:uppercase; color:#6c757d; letter-spacing:0.5px;">
                Ventaja 2024
            </div>
            <div style="font-size:1.9rem; font-weight:700; color:{color_v};">{margen_txt}</div>
            <div style="font-size:0.78rem; color:#666;">sobre el segundo lugar</div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        morena_txt = f"{morena_24:.1f}%" if pd.notna(morena_24) else "—"
        st.markdown(f"""
        <div style="background:#F5F5F5; border-radius:8px; padding:14px; text-align:center; margin-top:10px;">
            <div style="font-size:0.72rem; text-transform:uppercase; color:#6c757d; letter-spacing:0.5px;">
                % Morena 2024
            </div>
            <div style="font-size:1.9rem; font-weight:700; color:{COLORES['morena']};">{morena_txt}</div>
            <div style="font-size:0.78rem; color:#666;">de los votos válidos</div>
        </div>
        """, unsafe_allow_html=True)

    # Gráfica de evolución
    if not es_parcial and pd.notna(morena_18) and pd.notna(morena_21):
        pan_18 = row.get('pct_pan_2024')  # solo tenemos PAN en 2024
        anios  = [2018, 2021, 2024]
        vals_m = [morena_18, morena_21, morena_24]

        fig_ev = go.Figure()
        fig_ev.add_trace(go.Scatter(
            x=anios, y=vals_m,
            mode='lines+markers+text',
            name='Morena',
            line=dict(color=COLORES['morena'], width=3),
            marker=dict(size=9, color=COLORES['morena']),
            text=[f"{v:.0f}%" for v in vals_m],
            textposition='top center',
            textfont=dict(size=11, color=COLORES['morena']),
        ))
        # Línea de referencia 50%
        fig_ev.add_hline(
            y=50, line_dash="dot", line_color="#adb5bd",
            annotation_text="50%", annotation_position="right",
            annotation_font_size=10
        )
        fig_ev.update_layout(
            height=200,
            margin=dict(l=0, r=30, t=20, b=10),
            showlegend=False,
            plot_bgcolor='white',
            yaxis=dict(range=[0, 85], gridcolor='#f0f0f0', ticksuffix='%'),
            xaxis=dict(tickvals=[2018,2021,2024], ticktext=['2018','2021','2024'],
                      showgrid=False),
            title=dict(text="Evolución % Morena", font=dict(size=12), x=0),
        )
        st.plotly_chart(fig_ev, use_container_width=True)
    elif not es_parcial:
        st.markdown(f"""
        <div style="background:#F5F5F5; border-radius:8px; padding:12px; text-align:center; margin-top:8px;">
            <div style="font-size:0.8rem; color:#6c757d;">Morena 2024: <strong>{morena_24:.1f}%</strong></div>
            <div style="font-size:0.75rem; color:#adb5bd; margin-top:4px;">Historial 2018-2021 no disponible</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:#F5F5F5; border-radius:8px; padding:16px; text-align:center; margin-top:8px;">
            <div style="font-size:0.8rem; color:#6c757d;">Morena 2024: <strong>{morena_24:.1f}%</strong></div>
            <div style="font-size:0.75rem; color:#adb5bd; margin-top:4px;">Solo dato 2024 disponible</div>
        </div>
        """, unsafe_allow_html=True)

    # Tendencia y volatilidad
    if not es_parcial and pd.notna(tendencia):
        tend_txt, tend_icono = tendencia_texto(tendencia)
        vol_txt = volatilidad_texto(volatilidad)
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown(f"""
            <div class="tendencia-bloque" style="margin-top:8px;">
                <div class="flecha">{tend_icono}</div>
                <div class="valor">{tend_txt}</div>
                <div class="label">Tendencia Morena</div>
            </div>
            """, unsafe_allow_html=True)
        with col_t2:
            part_txt = f"{row.get('participacion_prom',0):.0f}%" if pd.notna(row.get('participacion_prom')) else "—"
            st.markdown(f"""
            <div class="tendencia-bloque" style="margin-top:8px;">
                <div class="flecha">🗳️</div>
                <div class="valor">{part_txt}</div>
                <div class="label">Participación promedio</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:0.82rem; color:#555; margin-top:8px; padding:8px 12px;
                    background:#F5F5F5; border-radius:6px;">
            📊 Variabilidad histórica: {vol_txt}
        </div>
        """, unsafe_allow_html=True)

    # Instrucción táctica (contexto M1)
    st.markdown(f"""
    <div class="caja-tactica" style="margin-top:12px;">
        <div class="titulo-tactica">{tactica}</div>
        <div class="desc-tactica">
            SPT {spt_val:.1f} · {spt_label}<br>
            <span style="color:#6c757d; font-size:0.78rem;">← Ver detalle operativo en M1</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Expander técnico
    with st.expander("Ver cómo se calculó ↓"):
        st.markdown(f"""
        **Componentes del SPT para sección {seccion_sel}**

        | Componente | Valor | Peso |
        |---|---|---|
        | Score electoral | {row.get('score_electoral_parcial','—')} | 35% |
        | % No nos conocen | {row.get('pct_no_alcanzados','—'):.1f}% | — |
        | % Persuadibles | {row.get('pct_persuadibles','—'):.1f}% | — |
        | % Núcleo duro | {row.get('pct_nucleo_duro','—'):.1f}% | — |
        | SPT final | **{spt_val:.1f}** | — |

        {"⚠️ *Score electoral calculado solo con datos 2024. No incluye tendencia histórica ni volatilidad.*" if es_parcial else "✅ *Score electoral calculado con historial completo 2018-2021-2024.*"}
        """)


# ─── GRÁFICA EVOLUCIÓN COMPARATIVA ────────────────────────────────────────────
st.markdown("<div class='separador'></div>", unsafe_allow_html=True)
st.markdown("#### 📈 Evolución de Morena por sección (2018 → 2021 → 2024)")
st.caption("Selecciona hasta 6 secciones para comparar su trayectoria. Las más frágiles están marcadas.")

secciones_con_hist = df[df['score_electoral_parcial'] == False]['seccion'].tolist()
secciones_comp_default = [2472, 2486, 2471, 2488, 2470]
secciones_comp = st.multiselect(
    "¿Qué secciones quieres comparar?",
    options=sorted(secciones_con_hist),
    default=[s for s in secciones_comp_default if s in secciones_con_hist],
    max_selections=6,
)

if secciones_comp:
    fig_comp = go.Figure()
    paleta_lineas = [
        "#e63946","#f4a261","#2a9d8f","#457b9d","#6c757d","#f4d35e"
    ]
    for i, sec in enumerate(secciones_comp):
        r = df[df['seccion'] == sec].iloc[0]
        vals = [r['pct_morena_2018'], r['pct_morena_2021'], r['pct_morena_2024']]
        es_alerta = sec == 2472

        fig_comp.add_trace(go.Scatter(
            x=[2018, 2021, 2024],
            y=vals,
            mode='lines+markers+text',
            name=f"Sec. {sec}",
            line=dict(
                color=paleta_lineas[i % len(paleta_lineas)],
                width=3 if es_alerta else 2,
                dash='dash' if es_alerta else 'solid',
            ),
            marker=dict(size=8 if es_alerta else 6),
            text=[None, None, f" {sec}"],
            textposition='middle right',
            textfont=dict(size=11),
        ))

    fig_comp.add_hline(y=50, line_dash="dot", line_color="#adb5bd",
                       annotation_text="50%", annotation_position="right",
                       annotation_font_size=10)
    fig_comp.update_layout(
        height=320,
        margin=dict(l=0, r=60, t=10, b=10),
        plot_bgcolor='white',
        yaxis=dict(range=[0, 85], gridcolor='#f0f0f0', ticksuffix='%', title='% Morena'),
        xaxis=dict(tickvals=[2018,2021,2024], showgrid=False, title=''),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
        hovermode='x unified',
    )
    st.plotly_chart(fig_comp, use_container_width=True)
    if 2472 in secciones_comp:
        st.markdown("""
        <div style="font-size:0.82rem; color:#888; padding:4px 8px;">
            - - - Línea punteada = sección 2472 (margen crítico de 1.6 pts)
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Selecciona al menos una sección para ver su evolución.")


# ─── TABLA RANKING ────────────────────────────────────────────────────────────
st.markdown("<div class='separador'></div>", unsafe_allow_html=True)
st.markdown("#### 📋 Ranking completo — de mayor a menor riesgo")
st.caption("Ordenado por margen de victoria: las secciones más frágiles aparecen primero.")

if df_filtrado.empty:
    st.info("No hay secciones que coincidan con los filtros seleccionados.")
else:
    tabla = df_filtrado.reset_index(drop=True).copy()

    # Columnas display
    tabla['⚠️']          = tabla.apply(
        lambda r: "⚠️" if r['score_electoral_parcial'] or
                          (pd.notna(r['margen_2024']) and r['margen_2024'] < 5)
                  else "", axis=1)
    tabla['Sección']      = tabla['seccion'].astype(int)
    tabla['Territorio']   = tabla['ambito_iter'].map(AMBITO_LABELS)
    tabla['Morena 2024']  = tabla['pct_morena_2024'].apply(
        lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
    tabla['Ventaja 2024'] = tabla['margen_2024'].apply(
        lambda x: f"{x:.1f} pts" if pd.notna(x) else "⚠️ Solo 2024")
    tabla['Tendencia']    = tabla['tendencia_morena'].apply(
        lambda x: f"↑ +{x:.1f} pts/ciclo" if pd.notna(x) and x >= 0
                  else (f"↓ {x:.1f} pts/ciclo" if pd.notna(x) else "—"))
    tabla['Variabilidad'] = tabla['volatilidad_morena'].apply(
        lambda x: "🔴 Alta"   if pd.notna(x) and x > 25
             else ("🟡 Media"  if pd.notna(x) and x > 15
             else ("🟢 Baja"   if pd.notna(x) else "—")))
    tabla['SPT']          = tabla['SPT'].apply(lambda x: f"{x:.1f}")
    tabla['Prioridad']    = tabla['clasificacion'].map(SPT_LABELS)

    # Ordenar: frágiles primero (NaN al final)
    tabla['_orden'] = tabla['margen_2024'].fillna(999)
    tabla = tabla.sort_values('_orden').reset_index(drop=True)

    tabla_display = tabla[[
        '⚠️', 'Sección', 'Territorio', 'Morena 2024',
        'Ventaja 2024', 'Tendencia', 'Variabilidad', 'SPT', 'Prioridad'
    ]]

    st.dataframe(
        tabla_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "⚠️":           st.column_config.TextColumn(width="small"),
            "Sección":      st.column_config.NumberColumn(width="small", format="%d"),
            "Territorio":   st.column_config.TextColumn(width="medium"),
            "Morena 2024":  st.column_config.TextColumn(width="small"),
            "Ventaja 2024": st.column_config.TextColumn(width="medium"),
            "Tendencia":    st.column_config.TextColumn(width="medium"),
            "Variabilidad": st.column_config.TextColumn(width="small"),
            "SPT":          st.column_config.TextColumn(width="small"),
            "Prioridad":    st.column_config.TextColumn(width="large"),
        }
    )

# Pie
st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; font-size:0.75rem; color:#94a3b8; padding:16px 0;">
    Inteligencia Electoral Zacatlán · JCLY Morena 2026 · Confidencial
</div>
""", unsafe_allow_html=True)
