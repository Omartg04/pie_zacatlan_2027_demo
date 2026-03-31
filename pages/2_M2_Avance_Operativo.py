"""
M2 — Avance Operativo de Tierra
Inteligencia Electoral Zacatlán · JCLY Morena 2026
Versión 1.1 · Marzo 2026
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster, HeatMap, Fullscreen
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="M2 · Avance Operativo | Zacatlán 2026",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Demo mode — no modificar ────────────────────────────────────────────────
from demo_mode import check_demo_mode
check_demo_mode()


# ─────────────────────────────────────────────
# PALETA DE COLORES (consistente con M1)
# ─────────────────────────────────────────────
COLORES = {
    "Prioritaria":    "#e63946",
    "Consolidacion":  "#f4a261",
    "Mantenimiento":  "#2a9d8f",
    "votaria":        "#2a9d8f",
    "no_sabe":        "#f4a261",
    "nunca":          "#e63946",
    "sin_dato":       "#adb5bd",
    "fondo_riesgo":   "#FDEDEC",
    "fondo_alerta":   "#FEF9E7",
    "fondo_ok":       "#EAF6EF",
    "fondo_info":     "#EBF0FB",
    "header_dark":    "#004a6e",
}

ETIQUETAS_ZONA = {
    "Prioritaria":   "🔴 Zona de máxima atención",
    "Consolidacion": "🟡 Zona de trabajo activo",
    "Mantenimiento": "🟢 Zona de base sólida",
}

ETIQUETAS_AMBITO = {
    "urbano":         "🏙️ Urbano",
    "rural_media":    "🌾 Rural Media",
    "rural_marginal": "🏔️ Rural Marginal",
}

# ─────────────────────────────────────────────
# CSS GLOBAL
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.header-modulo {
    background: linear-gradient(135deg, #004a6e 0%, #007cab 60%, #00c0ff 100%);
    padding: 28px 32px 22px 32px;
    border-radius: 12px;
    margin-bottom: 24px;
    border-left: 5px solid #e63946;
}
.header-modulo h1 {
    color: #ffffff;
    font-size: 1.6rem;
    font-weight: 700;
    margin: 0 0 4px 0;
    letter-spacing: -0.3px;
}
.header-modulo p {
    color: #94a3b8;
    font-size: 0.88rem;
    margin: 0;
    font-weight: 400;
}
.header-modulo .badge-fecha {
    display: inline-block;
    background: rgba(230,57,70,0.2);
    color: #f87171;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-top: 10px;
    font-family: 'IBM Plex Mono', monospace;
}

.metrica-card {
    background: #ffffff;
    border-radius: 10px;
    padding: 16px 20px;
    border: 1px solid #e2e8f0;
    border-top: 4px solid var(--accent);
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.metrica-card .label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #64748b;
    margin-bottom: 6px;
}
.metrica-card .valor {
    font-size: 1.9rem;
    font-weight: 700;
    color: #1e293b;
    line-height: 1;
    font-family: 'IBM Plex Mono', monospace;
}
.metrica-card .contexto {
    font-size: 0.78rem;
    color: #64748b;
    margin-top: 4px;
}

.alerta-critica {
    background: #FDEDEC;
    border: 1px solid #e63946;
    border-left: 5px solid #e63946;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 12px 0;
}
.alerta-critica .titulo {
    font-weight: 700;
    color: #c0392b;
    font-size: 0.85rem;
}
.alerta-critica .detalle {
    color: #7f1d1d;
    font-size: 0.82rem;
    margin-top: 3px;
}

.alerta-info {
    background: #EBF0FB;
    border-left: 4px solid #007cab;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 8px 0;
    font-size: 0.82rem;
    color: #1e40af;
}

.seccion-ficha {
    background: linear-gradient(135deg, #004a6e, #007cab);
    border-radius: 10px;
    padding: 20px;
    color: white;
    margin-bottom: 12px;
}
.seccion-ficha .num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
}
.seccion-ficha .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin: 4px 4px 0 0;
}

.brecha-alta   { background: #FDEDEC; border-left: 4px solid #e63946; border-radius: 6px; padding: 8px 12px; }
.brecha-media  { background: #FEF9E7; border-left: 4px solid #f4a261; border-radius: 6px; padding: 8px 12px; }
.brecha-baja   { background: #EAF6EF; border-left: 4px solid #2a9d8f; border-radius: 6px; padding: 8px 12px; }

.leyenda-puntos {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.8rem;
}
.leyenda-puntos .dot {
    display: inline-block;
    width: 10px; height: 10px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
}

[data-testid="stSidebar"] {
background-color: #004a6e !important;
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
background-color: #004a6e !important;
border-color: #007cab !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATOS SPT (embebidos — no depende de CSV externo)
# ─────────────────────────────────────────────
SPT_DATA = {
    2460: {"clasificacion":"Consolidacion","SPT":46.42,"ambito":"urbano","arq":"U1","tactica":"Brigadas primer contacto + cierre","pct_no_alc":56.5,"pct_pers":25.5,"pct_duro":10.2,"pct_no_conv":7.8},
    2461: {"clasificacion":"Mantenimiento","SPT":33.96,"ambito":"urbano","arq":"U1","tactica":"Activar base sólida únicamente","pct_no_alc":49.9,"pct_pers":20.5,"pct_duro":14.8,"pct_no_conv":14.8},
    2462: {"clasificacion":"Mantenimiento","SPT":30.74,"ambito":"urbano","arq":"U1","tactica":"Activar base sólida únicamente","pct_no_alc":49.9,"pct_pers":20.5,"pct_duro":14.8,"pct_no_conv":14.8},
    2463: {"clasificacion":"Consolidacion","SPT":44.33,"ambito":"urbano","arq":"U1","tactica":"Brigadas de primer contacto urgentes","pct_no_alc":63.8,"pct_pers":31.3,"pct_duro":2.9,"pct_no_conv":2.0},
    2464: {"clasificacion":"Consolidacion","SPT":53.68,"ambito":"rural_media","arq":"R0","tactica":"Activación y cierre de voto","pct_no_alc":27.4,"pct_pers":55.0,"pct_duro":9.2,"pct_no_conv":8.4},
    2465: {"clasificacion":"Consolidacion","SPT":41.42,"ambito":"urbano","arq":"U1","tactica":"Brigadas de primer contacto urgentes","pct_no_alc":56.5,"pct_pers":25.5,"pct_duro":10.2,"pct_no_conv":7.8},
    2466: {"clasificacion":"Consolidacion","SPT":41.96,"ambito":"rural_media","arq":"R0","tactica":"Activación y cierre de voto","pct_no_alc":27.4,"pct_pers":55.0,"pct_duro":9.2,"pct_no_conv":8.4},
    2467: {"clasificacion":"Consolidacion","SPT":50.88,"ambito":"urbano","arq":"U1","tactica":"Brigadas de primer contacto urgentes","pct_no_alc":68.4,"pct_pers":15.9,"pct_duro":8.6,"pct_no_conv":7.1},
    2469: {"clasificacion":"Mantenimiento","SPT":32.37,"ambito":"rural_media","arq":"R0","tactica":"Activar base sólida únicamente","pct_no_alc":27.4,"pct_pers":55.0,"pct_duro":9.2,"pct_no_conv":8.4},
    2470: {"clasificacion":"Consolidacion","SPT":49.06,"ambito":"urbano","arq":"R1","tactica":"Brigadas de primer contacto urgentes","pct_no_alc":64.9,"pct_pers":29.7,"pct_duro":3.1,"pct_no_conv":2.3},
    2471: {"clasificacion":"Prioritaria","SPT":70.99,"ambito":"rural_marginal","arq":"R1","tactica":"Brigadas de primer contacto urgentes","pct_no_alc":54.6,"pct_pers":25.4,"pct_duro":11.2,"pct_no_conv":8.8},
    2472: {"clasificacion":"Consolidacion","SPT":49.25,"ambito":"rural_marginal","arq":"R1","tactica":"Brigadas primer contacto + cierre","pct_no_alc":54.6,"pct_pers":25.4,"pct_duro":11.2,"pct_no_conv":8.8},
    2473: {"clasificacion":"Consolidacion","SPT":51.91,"ambito":"urbano","arq":"R1","tactica":"Brigadas primer contacto + cierre","pct_no_alc":56.9,"pct_pers":38.4,"pct_duro":2.8,"pct_no_conv":1.9},
    2474: {"clasificacion":"Consolidacion","SPT":41.66,"ambito":"urbano","arq":"R1","tactica":"Brigadas primer contacto + cierre","pct_no_alc":46.9,"pct_pers":45.0,"pct_duro":4.8,"pct_no_conv":3.3},
    2475: {"clasificacion":"Consolidacion","SPT":48.45,"ambito":"urbano","arq":"R0","tactica":"Activación y cierre de voto","pct_no_alc":35.9,"pct_pers":60.1,"pct_duro":2.1,"pct_no_conv":1.9},
    2476: {"clasificacion":"Consolidacion","SPT":42.93,"ambito":"rural_media","arq":"U1","tactica":"Brigadas de primer contacto urgentes","pct_no_alc":53.5,"pct_pers":16.2,"pct_duro":18.9,"pct_no_conv":11.4},
    2477: {"clasificacion":"Mantenimiento","SPT":36.75,"ambito":"rural_media","arq":"R0","tactica":"Activar base sólida únicamente","pct_no_alc":27.4,"pct_pers":55.0,"pct_duro":9.2,"pct_no_conv":8.4},
    2478: {"clasificacion":"Consolidacion","SPT":48.86,"ambito":"urbano","arq":"R1","tactica":"Brigadas primer contacto + cierre","pct_no_alc":33.3,"pct_pers":39.0,"pct_duro":17.4,"pct_no_conv":10.3},
    2480: {"clasificacion":"Consolidacion","SPT":42.06,"ambito":"urbano","arq":"R0","tactica":"Presencia regular y activación de multiplicadores","pct_no_alc":36.1,"pct_pers":42.1,"pct_duro":12.8,"pct_no_conv":9.0},
    2481: {"clasificacion":"Consolidacion","SPT":42.15,"ambito":"urbano","arq":"U1","tactica":"Brigadas de primer contacto urgentes","pct_no_alc":55.7,"pct_pers":24.0,"pct_duro":10.8,"pct_no_conv":9.5},
    2482: {"clasificacion":"Mantenimiento","SPT":34.62,"ambito":"urbano","arq":"R1","tactica":"Activar base sólida únicamente","pct_no_alc":48.3,"pct_pers":25.9,"pct_duro":13.2,"pct_no_conv":12.6},
    2483: {"clasificacion":"Consolidacion","SPT":61.72,"ambito":"urbano","arq":"R0","tactica":"Activación y cierre de voto","pct_no_alc":35.9,"pct_pers":60.1,"pct_duro":2.1,"pct_no_conv":1.9},
    2484: {"clasificacion":"Consolidacion","SPT":42.93,"ambito":"urbano","arq":"R0","tactica":"Presencia regular y activación de multiplicadores","pct_no_alc":33.5,"pct_pers":46.8,"pct_duro":11.6,"pct_no_conv":8.1},
    2485: {"clasificacion":"Consolidacion","SPT":49.76,"ambito":"rural_media","arq":"R0","tactica":"Activación y cierre de voto","pct_no_alc":27.4,"pct_pers":55.0,"pct_duro":9.2,"pct_no_conv":8.4},
    2486: {"clasificacion":"Prioritaria","SPT":71.48,"ambito":"urbano","arq":"R1","tactica":"Brigadas de primer contacto urgentes","pct_no_alc":56.9,"pct_pers":38.4,"pct_duro":2.8,"pct_no_conv":1.9},
    2487: {"clasificacion":"Consolidacion","SPT":47.30,"ambito":"rural_marginal","arq":"R1","tactica":"Brigadas primer contacto + cierre","pct_no_alc":47.3,"pct_pers":35.6,"pct_duro":9.4,"pct_no_conv":7.7},
    2488: {"clasificacion":"Prioritaria","SPT":70.72,"ambito":"rural_marginal","arq":"R1","tactica":"Brigadas de primer contacto urgentes","pct_no_alc":47.3,"pct_pers":35.6,"pct_duro":9.4,"pct_no_conv":7.7},
    2489: {"clasificacion":"Prioritaria","SPT":70.80,"ambito":"rural_marginal","arq":"R1","tactica":"Brigadas de primer contacto urgentes","pct_no_alc":47.3,"pct_pers":35.6,"pct_duro":9.4,"pct_no_conv":7.7},
    2727: {"clasificacion":"Consolidacion","SPT":42.52,"ambito":"rural_media","arq":"U1","tactica":"Brigadas de primer contacto urgentes","pct_no_alc":53.5,"pct_pers":16.2,"pct_duro":18.9,"pct_no_conv":11.4},
    2808: {"clasificacion":"Consolidacion","SPT":42.93,"ambito":"rural_media","arq":"U1","tactica":"Brigadas de primer contacto urgentes","pct_no_alc":53.5,"pct_pers":16.2,"pct_duro":18.9,"pct_no_conv":11.4},
    2809: {"clasificacion":"Consolidacion","SPT":54.67,"ambito":"rural_media","arq":"R0","tactica":"Activación y cierre de voto","pct_no_alc":26.2,"pct_pers":60.7,"pct_duro":6.4,"pct_no_conv":6.7},
    2895: {"clasificacion":"Mantenimiento","SPT":37.42,"ambito":"rural_media","arq":"R0","tactica":"Activar base sólida únicamente","pct_no_alc":25.8,"pct_pers":35.4,"pct_duro":26.1,"pct_no_conv":12.7},
    2896: {"clasificacion":"Consolidacion","SPT":57.97,"ambito":"rural_media","arq":"U1","tactica":"Brigadas de primer contacto urgentes","pct_no_alc":53.5,"pct_pers":16.2,"pct_duro":18.9,"pct_no_conv":11.4},
}

SECCIONES_PRIORITARIAS = [s for s, d in SPT_DATA.items() if d["clasificacion"] == "Prioritaria"]

# Flags metodológicos por sección
SECCIONES_ENC_REAL    = {2461,2463,2465,2467,2470,2471,2473,2474,2475,
                          2478,2480,2481,2482,2484,2485,2488,2727,2809,2895}
SECCIONES_HIST_PARCIAL= {2896,2809,2808,2727,2895}
SECCIONES_KNN         = {2486,2489,2483,2896,2464,2487,2472,2808,
                          2460,2476,2466,2477,2469,2462}

# Datos electorales por sección
COMP_DATA = {
    2460: {"margen":49.71,"tendencia":5.30,"pct_morena":63.64,"volatilidad":18.69,"clasif_elect":"Competida"},
    2461: {"margen":48.81,"tendencia":5.77,"pct_morena":63.09,"volatilidad":18.93,"clasif_elect":"Competida"},
    2462: {"margen":34.02,"tendencia":4.77,"pct_morena":57.04,"volatilidad":16.59,"clasif_elect":"Competida"},
    2463: {"margen":37.77,"tendencia":4.79,"pct_morena":58.73,"volatilidad":16.15,"clasif_elect":"Competida"},
    2464: {"margen":55.76,"tendencia":7.96,"pct_morena":67.25,"volatilidad":25.63,"clasif_elect":"Competida"},
    2465: {"margen":44.11,"tendencia":5.13,"pct_morena":61.92,"volatilidad":18.83,"clasif_elect":"Competida"},
    2466: {"margen":43.92,"tendencia":5.86,"pct_morena":61.96,"volatilidad":18.93,"clasif_elect":"Competida"},
    2467: {"margen":50.93,"tendencia":5.77,"pct_morena":64.37,"volatilidad":21.13,"clasif_elect":"Competida"},
    2469: {"margen":31.17,"tendencia":4.79,"pct_morena":55.58,"volatilidad":16.15,"clasif_elect":"Competida"},
    2470: {"margen": 9.20,"tendencia":3.10,"pct_morena":54.60,"volatilidad":12.40,"clasif_elect":"Competida"},
    2471: {"margen":42.10,"tendencia":6.20,"pct_morena":61.05,"volatilidad":19.80,"clasif_elect":"Competida"},
    2472: {"margen": 1.60,"tendencia":2.10,"pct_morena":50.80,"volatilidad":14.20,"clasif_elect":"Competida"},
    2473: {"margen":38.50,"tendencia":5.10,"pct_morena":59.25,"volatilidad":17.30,"clasif_elect":"Competida"},
    2474: {"margen":32.80,"tendencia":4.50,"pct_morena":56.40,"volatilidad":15.90,"clasif_elect":"Competida"},
    2475: {"margen":45.30,"tendencia":6.10,"pct_morena":62.65,"volatilidad":20.10,"clasif_elect":"Competida"},
    2476: {"margen":41.20,"tendencia":5.40,"pct_morena":60.60,"volatilidad":18.50,"clasif_elect":"Competida"},
    2477: {"margen":29.80,"tendencia":4.20,"pct_morena":54.90,"volatilidad":15.60,"clasif_elect":"Competida"},
    2478: {"margen":12.80,"tendencia":3.50,"pct_morena":56.40,"volatilidad":13.10,"clasif_elect":"Competida"},
    2480: {"margen":38.90,"tendencia":5.20,"pct_morena":59.45,"volatilidad":17.60,"clasif_elect":"Competida"},
    2481: {"margen":35.60,"tendencia":4.90,"pct_morena":57.80,"volatilidad":16.80,"clasif_elect":"Competida"},
    2482: {"margen":12.80,"tendencia":3.20,"pct_morena":56.40,"volatilidad":13.50,"clasif_elect":"Competida"},
    2483: {"margen":52.40,"tendencia":7.10,"pct_morena":66.20,"volatilidad":22.80,"clasif_elect":"Competida"},
    2484: {"margen":39.70,"tendencia":5.30,"pct_morena":59.85,"volatilidad":17.90,"clasif_elect":"Competida"},
    2485: {"margen":44.80,"tendencia":6.00,"pct_morena":62.40,"volatilidad":19.60,"clasif_elect":"Competida"},
    2486: {"margen":60.10,"tendencia":8.40,"pct_morena":70.05,"volatilidad":26.10,"clasif_elect":"Competida"},
    2487: {"margen":38.20,"tendencia":5.00,"pct_morena":59.10,"volatilidad":17.20,"clasif_elect":"Competida"},
    2488: {"margen":45.60,"tendencia":6.30,"pct_morena":62.80,"volatilidad":20.30,"clasif_elect":"Competida"},
    2489: {"margen":46.80,"tendencia":6.50,"pct_morena":63.40,"volatilidad":20.70,"clasif_elect":"Competida"},
    2727: {"margen":38.00,"tendencia": None,"pct_morena":59.00,"volatilidad": None,"clasif_elect":"Competida"},
    2808: {"margen":50.20,"tendencia": None,"pct_morena":65.10,"volatilidad": None,"clasif_elect":"Competida"},
    2809: {"margen":69.20,"tendencia": None,"pct_morena":84.60,"volatilidad": None,"clasif_elect":"Favorable"},
    2895: {"margen":30.10,"tendencia": None,"pct_morena":65.05,"volatilidad": None,"clasif_elect":"Competida"},
    2896: {"margen": 8.50,"tendencia": None,"pct_morena":54.25,"volatilidad": None,"clasif_elect":"Adversa"},
}


# ─────────────────────────────────────────────
# FUNCIONES DE CARGA Y PROCESAMIENTO
# ─────────────────────────────────────────────

_M2_BASE = os.path.dirname(os.path.abspath(__file__))
_M2_DATA = os.path.join(_M2_BASE, "..", "data")

RUTA_GEOJSON   = os.path.join(_M2_DATA, "zacatlan_secciones.geojson")
RUTA_INDUCCION = os.path.join(_M2_BASE, "..", "raw", "induccion_032726.csv")

FECHA_CORTE = '2026-02-14'


@st.cache_data(show_spinner=False)
def cargar_geojson():
    rutas = [
        RUTA_GEOJSON,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "zacatlan_secciones.geojson"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "zacatlan_secciones.geojson"),
    ]
    for ruta in rutas:
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
    return None


def generar_semanas(fecha_inicio_str, fecha_max):
    """
    Genera dinámicamente el mapa de semanas desde la fecha de inicio
    hasta la fecha máxima del archivo. No hay hardcoding de fechas.
    """
    fecha_inicio = pd.Timestamp(fecha_inicio_str)
    # Calcular cuántas semanas hay entre inicio y fecha máxima
    num_semanas = int((fecha_max - fecha_inicio).days // 7) + 1

    semana_map = {}
    for i in range(1, num_semanas + 1):
        inicio_sem = fecha_inicio + pd.Timedelta(weeks=i - 1)
        fin_sem    = inicio_sem + pd.Timedelta(days=6)
        # Formato legible: "Sem 1 · 14-20 feb"
        if inicio_sem.month == fin_sem.month:
            label = f"Sem {i} · {inicio_sem.day}-{fin_sem.day} {fin_sem.strftime('%b').lower()}"
        else:
            label = f"Sem {i} · {inicio_sem.day} {inicio_sem.strftime('%b').lower()}-{fin_sem.day} {fin_sem.strftime('%b').lower()}"
        semana_map[i] = label

    return semana_map, fecha_inicio


def procesar_operativo(df_raw):
    """Limpieza y enriquecimiento del CSV del operativo."""
    df = df_raw.copy()

    # Fecha
    df['Created Date'] = pd.to_datetime(df['Created Date'], format='mixed')

    # ── CAMBIO 1: total_raw = conteo igual que el notebook (solo corte de fecha) ──
    df['_incluir_en_total'] = df['Created Date'] >= FECHA_CORTE

    df = df[df['Created Date'] >= FECHA_CORTE].copy()

    # Sección
    df['seccion'] = pd.to_numeric(df['seccion_electoral_text'], errors='coerce').astype('Int64')

    # ── CAMBIO 2: semanas dinámicas — sin fechas hardcodeadas ──
    fecha_max    = df['Created Date'].max()
    semana_map, fecha_inicio = generar_semanas(FECHA_CORTE, fecha_max)

    df['semana_num'] = ((df['Created Date'] - fecha_inicio).dt.days // 7 + 1).clip(lower=1)
    df['semana_label'] = df['semana_num'].map(semana_map).fillna(
        semana_map[max(semana_map.keys())]
    )

    # Disponibilidad de voto — normalizar
    mapa_voto = {
        'Votaría':                'Votaría',
        'No sabe (NO LEER)':      'No sabe',
        'Nunca votaría':          'Nunca votaría',
        'No respondió (NO LEER)': 'Sin dato',
    }
    df['voto'] = df['p16_3_texto_text'].map(mapa_voto).fillna('Sin dato')

    # Conocimiento — normalizar
    mapa_conocimiento = {
        'Mucho': 'Mucho',
        'Algo':  'Algo',
        'Poco':  'Poco',
        'Nada':  'Nada',
        'No sabe (NO LEER)':      'Sin dato',
        'No respondió (NO LEER)': 'Sin dato',
    }
    df['conocimiento'] = df['p10_3_texto_text'].map(mapa_conocimiento).fillna('Sin dato')

    # Celular válido
    df['tiene_celular'] = df['celular_encuestado_number'].notna()

    # Coordenadas — imputar centroide si faltan
    centroides = df.dropna(subset=['latitud_text', 'longitud_text']).groupby('seccion').agg(
        lat_c=('latitud_text', 'mean'),
        lon_c=('longitud_text', 'mean')
    ).reset_index()
    df = df.merge(centroides, on='seccion', how='left')

    df['lat_final'] = df['latitud_text'].combine_first(df['lat_c'])
    df['lon_final'] = df['longitud_text'].combine_first(df['lon_c'])
    df['es_centroide'] = df['latitud_text'].isna() & df['lat_final'].notna()

    # Enriquecer con SPT
    df['spt_info'] = df['seccion'].map(SPT_DATA)
    df['clasificacion_spt'] = df['seccion'].map(lambda s: SPT_DATA.get(s, {}).get('clasificacion', 'Sin datos'))
    df['spt_valor'] = df['seccion'].map(lambda s: SPT_DATA.get(s, {}).get('SPT', None))
    df['ambito'] = df['seccion'].map(lambda s: SPT_DATA.get(s, {}).get('ambito', ''))

    return df, semana_map


def resumen_por_seccion(df):
    """Agrega métricas por sección para tabla y mapa."""
    grp = df.groupby('seccion').agg(
        total=('seccion', 'count'),
        con_celular=('tiene_celular', 'sum'),
        votaria=('voto', lambda x: (x == 'Votaría').sum()),
        no_sabe=('voto', lambda x: (x == 'No sabe').sum()),
        nunca=('voto', lambda x: (x == 'Nunca votaría').sum()),
        conoce_algo_mucho=('conocimiento', lambda x: x.isin(['Algo', 'Mucho']).sum()),
        ultima_fecha=('Created Date', 'max'),
    ).reset_index()

    for col in ['total', 'con_celular', 'votaria', 'no_sabe', 'nunca', 'conoce_algo_mucho']:
        grp[col] = pd.to_numeric(grp[col], errors='coerce').fillna(0).astype(float)

    grp['pct_celular'] = (grp['con_celular'] / grp['total'] * 100).round(1)
    grp['pct_votaria'] = (grp['votaria'] / grp['total'] * 100).round(1)
    grp['pct_conoce']  = (grp['conoce_algo_mucho'] / grp['total'] * 100).round(1)

    grp['clasificacion'] = grp['seccion'].map(lambda s: SPT_DATA.get(int(s) if pd.notna(s) else 0, {}).get('clasificacion', 'Sin datos'))
    grp['SPT']      = grp['seccion'].map(lambda s: SPT_DATA.get(int(s) if pd.notna(s) else 0, {}).get('SPT', 0))
    grp['ambito']   = grp['seccion'].map(lambda s: SPT_DATA.get(int(s) if pd.notna(s) else 0, {}).get('ambito', ''))
    grp['arq']      = grp['seccion'].map(lambda s: SPT_DATA.get(int(s) if pd.notna(s) else 0, {}).get('arq', ''))
    grp['tactica']  = grp['seccion'].map(lambda s: SPT_DATA.get(int(s) if pd.notna(s) else 0, {}).get('tactica', ''))

    spt_max   = grp['SPT'].max() if grp['SPT'].max() > 0 else 1
    total_max = grp['total'].max() if grp['total'].max() > 0 else 1
    grp['spt_norm']      = grp['SPT'] / spt_max
    grp['cobertura_norm']= grp['total'] / total_max
    grp['brecha']        = (grp['spt_norm'] - grp['cobertura_norm']).round(3)

    def clasif_brecha(b):
        if b > 0.3:  return "⚠️ Refuerzo urgente"
        if b > 0.1:  return "📋 Revisar cobertura"
        return "✅ Cobertura adecuada"

    grp['brecha_label'] = grp['brecha'].apply(clasif_brecha)

    return grp.sort_values('SPT', ascending=False)


# ─────────────────────────────────────────────
# CONSTRUCCIÓN DEL MAPA
# ─────────────────────────────────────────────

def color_voto(voto):
    return {
        'Votaría':        '#2a9d8f',
        'No sabe':        '#f4a261',
        'Nunca votaría':  '#e63946',
        'Sin dato':       '#adb5bd',
    }.get(voto, '#adb5bd')


def color_clasificacion(clasif):
    return {
        'Prioritaria':   '#e63946',
        'Consolidacion': '#f4a261',
        'Mantenimiento': '#2a9d8f',
    }.get(clasif, '#94a3b8')


def construir_mapa(df_filtrado, geojson, resumen_sec, mostrar_puntos, mostrar_heatmap,
                   clasif_activas=None, secciones_activas=None):
    if clasif_activas is None:
        clasif_activas = list(ETIQUETAS_ZONA.keys())
    if secciones_activas is None:
        secciones_activas = list(SPT_DATA.keys())

    m = folium.Map(
        location=[19.94, -97.96],
        zoom_start=12,
        tiles='CartoDB positron',
        control_scale=True
    )

    Fullscreen(
        position='topleft',
        title='Pantalla completa',
        title_cancel='Salir de pantalla completa',
        force_separate_button=True,
    ).add_to(m)

    if geojson:
        def estilo_seccion(feature):
            sec   = feature['properties'].get('SECCION', 0)
            datos = SPT_DATA.get(int(sec), {})
            clasif= datos.get('clasificacion', '')
            color = color_clasificacion(clasif)
            spt   = datos.get('SPT', 40)
            fill_opacity = 0.15 + (spt / 100) * 0.35
            return {
                'fillColor':   color,
                'color':       color,
                'weight':      2.5,
                'fillOpacity': fill_opacity,
                'opacity':     0.9,
            }

        folium.GeoJson(
            geojson,
            name="Prioridad Territorial (SPT)",
            style_function=estilo_seccion,
            tooltip=folium.GeoJsonTooltip(
                fields=['SECCION'],
                aliases=['Sección:'],
                localize=True
            ),
            popup=folium.GeoJsonPopup(
                fields=['SECCION'],
                aliases=['Sección'],
            )
        ).add_to(m)

    if mostrar_heatmap:
        coords_heat = df_filtrado.dropna(subset=['lat_final', 'lon_final'])[['lat_final', 'lon_final']].values.tolist()
        if coords_heat:
            HeatMap(
                coords_heat,
                name="Densidad de contactos",
                radius=18,
                blur=15,
                min_opacity=0.3,
                gradient={'0.4': '#007cab', '0.65': '#f4a261', '1': '#e63946'}
            ).add_to(m)

    if mostrar_puntos:
        cluster = MarkerCluster(
            name="Contactos individuales",
            options={'maxClusterRadius': 40, 'spiderfyOnMaxZoom': True}
        )

        df_con_coords = df_filtrado.dropna(subset=['lat_final', 'lon_final'])

        for _, row in df_con_coords.iterrows():
            voto  = row.get('voto', 'Sin dato')
            color = color_voto(voto)
            es_centroide = row.get('es_centroide', False)
            radio    = 6 if not es_centroide else 4
            opacidad = 0.85 if not es_centroide else 0.55
            contorno = '#ffffff' if not es_centroide else '#94a3b8'
            dash     = 'none' if not es_centroide else '4'

            nombre_raw  = row.get('nombre_encuestado_text', '')
            nombre      = str(nombre_raw).strip() if pd.notna(nombre_raw) and str(nombre_raw).strip() else None

            celular_raw = row.get('celular_encuestado_number', '')
            celular     = None
            if pd.notna(celular_raw):
                try:
                    celular = str(int(float(celular_raw)))
                    if len(celular) < 8:
                        celular = None
                except:
                    celular = None

            dir_raw   = row.get('google_address_geographic_address', '')
            direccion = str(dir_raw).strip() if pd.notna(dir_raw) and str(dir_raw).strip() else None

            localidad_raw = row.get('localidad_text', '')
            localidad = str(localidad_raw).strip().title() if pd.notna(localidad_raw) and str(localidad_raw).strip() else None

            sec          = str(row.get('seccion', ''))
            conocimiento = str(row.get('conocimiento', 'Sin dato'))
            fecha_str    = str(row.get('Created Date', ''))[:10]

            nombre_display = nombre if nombre else "Contacto sin nombre"
            inicial        = nombre_display[0].upper() if nombre_display else "?"
            color_ini      = color

            voto_chip = f"<span style='background:{color};color:#fff;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;'>{voto}</span>"

            if celular:
                wa_url       = f"https://wa.me/52{celular}"
                celular_html = (
                    f"<div style='margin:5px 0;'>"
                    f"<span style='color:#64748b;font-size:11px;'>📱 Celular</span><br>"
                    f"<a href='{wa_url}' target='_blank' style='color:#25D366;font-weight:700;"
                    f"text-decoration:none;font-size:13px;'>📲 {celular} · WhatsApp</a>"
                    f"</div>"
                )
            else:
                celular_html = (
                    "<div style='margin:5px 0;'>"
                    "<span style='color:#94a3b8;font-size:11px;'>📱 Sin celular registrado</span>"
                    "</div>"
                )

            if direccion:
                dir_html = f"<div style='margin:5px 0;color:#475569;font-size:11px;'>📍 {direccion}</div>"
            elif localidad:
                dir_html = f"<div style='margin:5px 0;color:#475569;font-size:11px;'>📍 {localidad}</div>"
            else:
                dir_html = ""

            coord_nota = (
                "<div style='color:#94a3b8;font-size:10px;margin-top:4px;'>"
                "⚬ Coordenada estimada (centroide de sección)</div>"
                if es_centroide else ""
            )

            popup_html = f"""
            <div style='font-family:"IBM Plex Sans",sans-serif;min-width:210px;max-width:260px;'>
                <div style='display:flex;align-items:center;gap:10px;
                            background:#f8fafc;border-radius:8px 8px 0 0;
                            padding:10px 12px;border-bottom:1px solid #e2e8f0;'>
                    <div style='width:32px;height:32px;border-radius:50%;
                                background:{color_ini};color:#fff;
                                display:flex;align-items:center;justify-content:center;
                                font-weight:700;font-size:15px;flex-shrink:0;'>{inicial}</div>
                    <div>
                        <div style='font-weight:700;font-size:13px;color:#1e293b;
                                    line-height:1.2;'>{nombre_display}</div>
                        <div style='font-size:11px;color:#64748b;'>Sección {sec}</div>
                    </div>
                </div>
                <div style='padding:10px 12px;'>
                    <div style='margin-bottom:6px;'>{voto_chip}
                        <span style='font-size:11px;color:#64748b;margin-left:6px;'>
                            Conoce: <b>{conocimiento}</b></span>
                    </div>
                    {celular_html}
                    {dir_html}
                    <div style='color:#94a3b8;font-size:10px;margin-top:6px;
                                border-top:1px solid #f1f5f9;padding-top:5px;'>
                        {fecha_str}{coord_nota}
                    </div>
                </div>
            </div>
            """

            folium.CircleMarker(
                location=[row['lat_final'], row['lon_final']],
                radius=radio,
                color=contorno,
                weight=1.5,
                fill=True,
                fill_color=color,
                fill_opacity=opacidad,
                dash_array=dash,
                popup=folium.Popup(popup_html, max_width=270),
                tooltip=f"{nombre_display} · {voto}",
            ).add_to(cluster)

        cluster.add_to(m)

    secciones_cubiertas = set(df_filtrado['seccion'].dropna().astype(int).unique())
    for sec in SECCIONES_PRIORITARIAS:
        if sec not in secciones_cubiertas:
            datos = SPT_DATA.get(sec, {})
            folium.Marker(
                location=[19.94 + (sec - 2480) * 0.01, -97.96],
                icon=folium.Icon(color='red', icon='exclamation-sign', prefix='glyphicon'),
                popup=f"<b>⚠️ Sección {sec}</b><br>Prioritaria · SPT {datos.get('SPT',0):.1f}<br><b>Sin contactos registrados</b>",
                tooltip=f"⚠️ Sección {sec} · Sin cobertura",
            ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    return m


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 8px 0;'>
        <div style='font-size:0.7rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:1px;color:#64748b;margin-bottom:4px;'>
            INTELIGENCIA ELECTORAL
        </div>
        <div style='font-size:1.1rem;font-weight:700;color:#1e293b;'>
            M2 · Operativo de Tierra
        </div>
    </div>
    <hr style='border:none;border-top:1px solid #e2e8f0;margin:8px 0 16px 0;'>
    """, unsafe_allow_html=True)

    st.markdown("**📂 Cargar datos del operativo**")
    archivo = st.file_uploader(
        "Selecciona el CSV del operativo",
        type=["csv"],
        help="Archivo de inducción con registros del campo. Base: induccion_032726.csv"
    )

    if archivo is None:
        if os.path.exists(RUTA_INDUCCION):
            st.info(f"📁 Usando archivo local: `raw/{os.path.basename(RUTA_INDUCCION)}`")

    st.markdown("---")
    st.markdown("**🔍 Filtros**")

    # Los filtros de semana se llenan dinámicamente después de cargar datos
    filtro_semana_placeholder = st.empty()

    filtro_zona = st.multiselect(
        "¿Qué zonas quieres ver?",
        options=["🔴 Zona de máxima atención",
                 "🟡 Zona de trabajo activo",
                 "🟢 Zona de base sólida"],
        default=["🔴 Zona de máxima atención",
                 "🟡 Zona de trabajo activo",
                 "🟢 Zona de base sólida"],
    )

    filtro_voto = st.multiselect(
        "¿Disponibilidad de voto?",
        options=["Votaría", "No sabe", "Nunca votaría", "Sin dato"],
        default=["Votaría", "No sabe", "Nunca votaría", "Sin dato"],
    )

    filtro_seccion_placeholder = st.empty()
    st.caption("💡 'Todas las secciones' muestra el municipio completo")

    st.markdown("---")
    st.markdown("**🗺️ Opciones del mapa**")
    mostrar_puntos  = st.toggle("Mostrar contactos individuales", value=True)
    mostrar_heatmap = st.toggle("Mostrar densidad (heatmap)", value=False)

    st.markdown("---")
    with st.expander("ℹ️ ¿Cómo funciona esto?"):
        st.markdown("""
        **M2 — Avance Operativo de Tierra**

        Muestra dónde están yendo las brigadas y si el esfuerzo
        coincide con las zonas prioritarias del SPT.

        - **Fondo del mapa:** Prioridad territorial (SPT).
          Rojo = máxima atención · Naranja = trabajo activo · Verde = base sólida
        - **Puntos de color:**
          🟢 Verde = Votaría · 🟡 Naranja = No sabe · 🔴 Rojo = Nunca votaría
        - **Círculo hueco:** coordenada estimada (centroide de sección)
        - **Alerta ⚠️:** sección prioritaria sin ningún contacto registrado
        - **Mapa de calor:** densidad de contactos levantados

        *Fecha de corte del operativo: 14 febrero 2026*
        """)


# ─────────────────────────────────────────────
# CARGA Y PROCESAMIENTO DE DATOS
# ─────────────────────────────────────────────

df_raw = None

if archivo is not None:
    try:
        df_raw = pd.read_csv(archivo)
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
else:
    if os.path.exists(RUTA_INDUCCION):
        df_raw = pd.read_csv(RUTA_INDUCCION)

if df_raw is None:
    LOGO_B64_M2 = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAQABAADASIAAhEBAxEB/8QAHAABAQEAAwEBAQAAAAAAAAAAAAECBgcIAwUE/8QASBABAAIBAgMDBwkGBQIEBwEAAAECAwQFBgcREiExFyI1QVFhchMyUlRxgZGS0QgUQqGxwRUjYuHwY4IkMzSDFjdDRVWT8aL/xAAcAQEBAAIDAQEAAAAAAAAAAAAAAgEGBAUHAwj/xAA7EQEAAQMBAwgHBwQDAQEAAAAAAQIDBAUGEXESFSExNEFRUhMyU5GhsdEUFiIjYYHBB0Lh8CQzYnJD/9oADAMBAAIRAxEAPwDxkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH//2Q=="
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#004a6e 0%,#007cab 60%,#00c0ff 100%);
         border-radius:16px;padding:24px 32px;margin-bottom:24px;position:relative;overflow:hidden;'>
      <div style='display:flex;align-items:center;gap:18px;margin-bottom:10px;'>
        <img src="data:image/png;base64,{LOGO_B64_M2}"
             style='width:52px;height:52px;border-radius:10px;mix-blend-mode:lighten;flex-shrink:0;'>
        <div>
          <div style='font-size:0.70rem;font-weight:700;letter-spacing:0.13em;
               color:#00c0ff;text-transform:uppercase;margin-bottom:4px;'>Tu mapa de decisiones</div>
          <div style='font-size:1.45rem;font-weight:800;color:#ffffff;line-height:1.2;'>
            ¿Cómo vamos en campo?</div>
        </div>
      </div>
      <div style='color:rgba(255,255,255,0.70);font-size:0.88rem;margin-left:70px;'>
        Carga el CSV del operativo para activar el módulo · Zacatlán JCLY 2026
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class='alerta-info'>
        📂 <b>Carga el CSV del operativo</b> en el panel izquierdo para activar el módulo.
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# Procesar datos
with st.spinner("Procesando datos del operativo..."):
    df, semana_map = procesar_operativo(df_raw)

# ── CAMBIO 1: total consistente con notebook (solo corte de fecha, sin filtrar nulos de sección) ──
total_contactos_reporte = len(df)

# Opciones de semana dinámicas
opciones_semana = list(semana_map.values())

with filtro_semana_placeholder:
    filtro_semana = st.multiselect(
        "¿Qué semana del operativo?",
        options=opciones_semana,
        default=opciones_semana,
    )

# Aplicar filtros
mapa_zona_inv  = {v: k for k, v in ETIQUETAS_ZONA.items()}
clasif_sel     = [mapa_zona_inv.get(z, z) for z in filtro_zona]

secciones_disponibles = sorted(df['seccion'].dropna().astype(int).unique().tolist())
opciones_seccion = ["Todas las secciones"] + [
    f"{s} · {ETIQUETAS_ZONA.get(SPT_DATA.get(s,{}).get('clasificacion',''), SPT_DATA.get(s,{}).get('clasificacion',''))}"
    for s in secciones_disponibles
]
with filtro_seccion_placeholder:
    seleccion_seccion = st.selectbox(
        "¿Qué sección quieres ver?",
        options=opciones_seccion,
        index=0,
    )

if seleccion_seccion == "Todas las secciones":
    seccion_activa = secciones_disponibles
else:
    seccion_activa = [int(seleccion_seccion.split(" · ")[0])]

voto_activo = filtro_voto if filtro_voto else df['voto'].unique().tolist()

df_f = df[
    df['semana_label'].isin(filtro_semana) &
    df['clasificacion_spt'].isin(clasif_sel) &
    df['seccion'].isin(seccion_activa) &
    df['voto'].isin(voto_activo)
].copy()

if df_f.empty:
    st.warning("⚠️ No hay contactos con los filtros seleccionados. Ajusta los filtros.")
    st.stop()

resumen_sec = resumen_por_seccion(df_f)
geojson     = cargar_geojson()


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
ultima_fecha = df['Created Date'].max()

# ── CAMBIO 3: fecha dinámica en el header ──
fecha_inicio_label = pd.Timestamp(FECHA_CORTE).strftime('%d %b')
fecha_fin_label    = ultima_fecha.strftime('%d %b %Y')

LOGO_B64_M2 = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAQABAADASIAAhEBAxEB/8QAHAABAQEAAwEBAQAAAAAAAAAAAAECBgcIAwUE/8QASBABAAIBAgMDBwkGBQIEBwEAAAECAwQFBgcREiExFyI1QVFhchMyUlRxgZGS0QgUQqGxwRUjYuHwY4IkMzSDFjdDRVWT8aL/xAAcAQEBAAIDAQEAAAAAAAAAAAAAAgEGBAUHAwj/xAA7EQEAAQMBAwgHBwQDAQEAAAAAAQIDBAUGEXESFSExNEFRUhMyU5GhsdEUFiIjYYHBB0Lh8CQzYnJD/9oADAMBAAIRAxEAPwDxkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH//2Q=="
st.markdown(f"""
<div style='background:linear-gradient(135deg,#004a6e 0%,#007cab 60%,#00c0ff 100%);
     border-radius:16px;padding:24px 32px;margin-bottom:24px;position:relative;overflow:hidden;'>
  <div style='position:absolute;top:-40px;right:-40px;width:140px;height:140px;
       border-radius:50%;background:rgba(255,255,255,0.05);'></div>
  <div style='display:flex;align-items:center;gap:18px;margin-bottom:10px;'>
    <img src="data:image/png;base64,{LOGO_B64_M2}"
         style='width:52px;height:52px;border-radius:10px;mix-blend-mode:lighten;flex-shrink:0;'>
    <div>
      <div style='font-size:0.70rem;font-weight:700;letter-spacing:0.13em;
           color:#00c0ff;text-transform:uppercase;margin-bottom:4px;'>
        Tu mapa de decisiones
      </div>
      <div style='font-size:1.45rem;font-weight:800;color:#ffffff;line-height:1.2;'>
        ¿Cómo vamos en campo?
      </div>
    </div>
  </div>
  <div style='color:rgba(255,255,255,0.70);font-size:0.88rem;margin-left:70px;'>
    Actualizado al {ultima_fecha.strftime('%d %b %Y · %H:%M')} · Zacatlán JCLY 2026
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ALERTAS CRÍTICAS
# ─────────────────────────────────────────────
# Definición de secciones activas y cobertura (usada aquí y en tarjeta 2)
SPT_ACTIVAS = {2460,2461,2462,2463,2464,2465,2466,2467,2469,2470,2471,2472,2473,
               2474,2475,2476,2477,2478,2480,2481,2482,2483,2484,2485,2486,2487,
               2488,2489,2727,2808,2809,2895,2896}
conteo_x_seccion       = df['seccion'].dropna().astype(int).value_counts()
top15_secciones        = conteo_x_seccion.head(15)
top15_total            = int(top15_secciones.sum())
top15_pct              = top15_total / max(total_contactos_reporte, 1) * 100
secciones_con_contacto = set(conteo_x_seccion.index) & SPT_ACTIVAS
secciones_sin_contacto = SPT_ACTIVAS - secciones_con_contacto
n_sin_cobertura        = len(secciones_sin_contacto)

# Regla de negocio: umbral de cobertura = 5% del total de cuestionarios levantados
UMBRAL_COBERTURA_PCT = 0.05
umbral_contactos = max(1, round(total_contactos_reporte * UMBRAL_COBERTURA_PCT))

# Contactos por sección (sobre df completo, no filtrado)
contactos_por_seccion = df.groupby('seccion').size().to_dict()

# Clasificar secciones prioritarias en tres estados:
# - sin_cobertura: 0 contactos
# - cobertura_insuficiente: entre 1 y umbral-1
# - cubiertas: umbral o más
secciones_cubiertas        = secciones_con_contacto  # secciones con al menos 1 contacto declarado
prioritarias_sin_cobertura = []
prioritarias_insuficientes = []

for s in SECCIONES_PRIORITARIAS:
    n = contactos_por_seccion.get(s, 0)
    if n == 0:
        prioritarias_sin_cobertura.append((s, n))
    elif n < umbral_contactos:
        prioritarias_insuficientes.append((s, n))

# Alerta roja — sin cobertura
if prioritarias_sin_cobertura:
    detalles = " · ".join([
        f"Sección {s} (SPT {SPT_DATA[s]['SPT']:.0f} · 0 contactos)"
        for s, n in prioritarias_sin_cobertura
    ])
    st.markdown(f"""
    <div class='alerta-critica'>
        <div class='titulo'>⚠️ Secciones prioritarias sin cobertura</div>
        <div class='detalle'>{detalles} — Estas zonas tienen el mayor potencial electoral
        y no han recibido visita de brigadas.</div>
    </div>
    """, unsafe_allow_html=True)

# Alerta roja — cobertura insuficiente (hay contactos pero por debajo del umbral)
if prioritarias_insuficientes:
    detalles_ins = " · ".join([
        f"Sección {s} ({n} de {umbral_contactos} requeridos)"
        for s, n in prioritarias_insuficientes
    ])
    st.markdown(f"""
    <div class='alerta-critica'>
        <div class='titulo'>⚠️ Secciones prioritarias con cobertura insuficiente</div>
        <div class='detalle'>{detalles_ins} — Se requieren al menos {umbral_contactos} contactos
        por sección prioritaria ({int(UMBRAL_COBERTURA_PCT*100)}% de {total_contactos_reporte:,} totales).
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TARJETAS DE RESUMEN
# ─────────────────────────────────────────────
total_filtrado = len(df_f)
pct_celular    = (df_f['tiene_celular'].sum() / max(total_filtrado, 1) * 100)
pct_votaria    = (df_f['voto'].eq('Votaría').sum() / max(total_filtrado, 1) * 100)
pct_no_sabe    = (df_f['voto'].eq('No sabe').sum() / max(total_filtrado, 1) * 100)

# Tarjeta 2 — Top 15 secciones (definido en bloque ALERTAS CRÍTICAS arriba)

# Detectar si hay filtro de voto activo (no todos seleccionados)
hay_filtro_voto = set(filtro_voto) != {'Votaría', 'No sabe', 'Nunca votaría', 'Sin dato'}

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Sin filtro de voto: muestra total_contactos_reporte (igual que notebook)
    if hay_filtro_voto:
        valor_tarjeta   = total_filtrado
        label_total    = "Contactos (filtrado)"
        contexto_total = f"de {total_contactos_reporte:,} totales \u00b7 {fecha_inicio_label} \u2013 {fecha_fin_label}"
    else:
        valor_tarjeta   = total_contactos_reporte
        label_total    = "Total contactos"
        contexto_total = f"{fecha_inicio_label} \u2013 {fecha_fin_label}"

    alcance_estimado_m2 = int(valor_tarjeta * 3.81)
    st.markdown(f"""
    <div class='metrica-card' style='--accent:#007cab;'>
        <div class='label'>{label_total}</div>
        <div class='valor'>{valor_tarjeta:,}</div>
        <div class='contexto'>{contexto_total}</div>
        <div style='margin-top:8px;padding-top:8px;border-top:1px solid #e2e8f0;
             font-size:0.75rem;color:#0891b2;font-weight:600;'>
            ~{alcance_estimado_m2:,} personas · alcance estimado de hogar
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    color_sec = "#2a9d8f" if n_sin_cobertura == 0 else "#f4a261"
    st.markdown(f"""
    <div class='metrica-card' style='--accent:{color_sec};'>
        <div class='label'>Top 15 secciones</div>
        <div class='valor'>{top15_pct:.0f}<span style='font-size:1rem;color:#94a3b8'>%</span></div>
        <div class='contexto'>{top15_total:,} contactos · {n_sin_cobertura} secc. sin cobertura</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    color_cel = "#2a9d8f" if pct_celular >= 55 else "#f4a261"
    st.markdown(f"""
    <div class='metrica-card' style='--accent:{color_cel};'>
        <div class='label'>Con celular válido</div>
        <div class='valor'>{pct_celular:.0f}<span style='font-size:1rem;color:#94a3b8'>%</span></div>
        <div class='contexto'>{int(df_f['tiene_celular'].sum()):,} contactos activables</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    # Sin filtro activo: mostrar distribución completa de los 4 segmentos
    # Con filtro de un solo segmento: mostrar peso de ese segmento sobre el total
    if hay_filtro_voto and len(filtro_voto) == 1:
        etiqueta_voto = {
            'Votaría':        'Apoyan la candidatura',
            'No sabe':        'Indecisos',
            'Nunca votaría':  'Contactos adversos',
            'Sin dato':       'Sin respuesta',
        }.get(filtro_voto[0], filtro_voto[0])
        color_acento = {
            'Votaría':        '#2a9d8f',
            'No sabe':        '#f4a261',
            'Nunca votaría':  '#e63946',
            'Sin dato':       '#94a3b8',
        }.get(filtro_voto[0], '#2a9d8f')
        pct_segmento = total_filtrado / max(total_contactos_reporte, 1) * 100
        st.markdown(f"""
        <div class='metrica-card' style='--accent:{color_acento};'>
            <div class='label'>{etiqueta_voto}</div>
            <div class='valor'>{pct_segmento:.0f}<span style='font-size:1rem;color:#94a3b8'>%</span></div>
            <div class='contexto'>{total_filtrado:,} de {total_contactos_reporte:,} totales</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Calcular distribución completa sobre universo total
        base = max(total_contactos_reporte, 1)
        _n_votaria = df['voto'].eq('Votaría').sum()
        _n_nosabe  = df['voto'].eq('No sabe').sum()
        _n_nunca   = df['voto'].eq('Nunca votaría').sum()
        _n_sindato = df['voto'].eq('Sin dato').sum()
        _p_votaria = _n_votaria / base * 100
        _p_nosabe  = _n_nosabe  / base * 100
        _p_nunca   = _n_nunca   / base * 100
        _p_sindato = _n_sindato / base * 100
        st.markdown(f"""
        <div class='metrica-card' style='--accent:#2a9d8f;'>
            <div class='label'>DISPOSICIÓN DE VOTO</div>
            <div style='margin-top:8px;font-size:0.85rem;line-height:1.8;'>
                <div><span style='color:#2a9d8f;font-weight:700;font-family:"IBM Plex Mono",monospace;'>{_p_votaria:.0f}%</span>
                    <span style='color:#64748b;margin-left:6px;'>✅ Votaría</span></div>
                <div><span style='color:#f4a261;font-weight:700;font-family:"IBM Plex Mono",monospace;'>{_p_nosabe:.0f}%</span>
                    <span style='color:#64748b;margin-left:6px;'>🟡 Por convencer</span></div>
                <div><span style='color:#e63946;font-weight:700;font-family:"IBM Plex Mono",monospace;'>{_p_nunca:.0f}%</span>
                    <span style='color:#64748b;margin-left:6px;'>🔴 Nunca votaría</span></div>
                <div><span style='color:#94a3b8;font-weight:700;font-family:"IBM Plex Mono",monospace;'>{_p_sindato:.0f}%</span>
                    <span style='color:#64748b;margin-left:6px;'>⚬ Sin dato</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── Nota diagnóstica de calidad de captura ────────────────────────────────
with st.expander("🔍 Nota técnica: calidad de captura de sección electoral", expanded=False):
    registros_con_coord = df['latitud_text'].notna().sum()
    registros_con_seccion = df['seccion'].notna().sum()
    secciones_declaradas = df['seccion'].dropna().astype(int).nunique()
    top3 = conteo_x_seccion.head(3)
    top3_pct = top3.sum() / max(total_contactos_reporte, 1) * 100

    st.markdown(f"""
    <div style='font-size:0.85rem;color:#475569;line-height:1.7;'>
        <b>Distribución de contactos por sección declarada</b><br>
        · <b>{secciones_declaradas}</b> secciones distintas registradas en el formulario<br>
        · Las <b>Top 15</b> concentran el <b>{top15_pct:.1f}%</b> de los contactos ({top15_total:,} de {total_contactos_reporte:,})<br>
        · Las <b>Top 3</b> concentran el <b>{top3_pct:.1f}%</b> ({int(top3.sum()):,} contactos)<br>
        · <b>{n_sin_cobertura}</b> secciones activas sin ningún contacto registrado:
        <span style='color:#e63946;font-weight:600;'>
        {', '.join(str(s) for s in sorted(secciones_sin_contacto))}</span><br><br>
        <span style='color:#94a3b8;font-size:0.8rem;'>
        Nota: La sección electoral se captura manualmente en el formulario. La concentración
        observada responde a decisiones operativas del equipo de campo, no a errores de captura.
        Las coordenadas GPS son independientes y reflejan la ubicación física real del encuestador.
        </span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAPA PRINCIPAL
# ─────────────────────────────────────────────
col_mapa, col_leyenda = st.columns([4, 1])

with col_leyenda:
    st.markdown("""
    <div class='leyenda-puntos'>
        <div style='font-weight:700;font-size:0.8rem;margin-bottom:10px;color:#1e293b;'>LEYENDA</div>
        <div style='font-weight:600;font-size:0.72rem;color:#64748b;text-transform:uppercase;
                    letter-spacing:0.5px;margin-bottom:6px;'>Zona (SPT)</div>
        <div style='margin-bottom:4px;font-size:0.8rem;'><span class='dot' style='background:#e63946'></span>Máxima atención</div>
        <div style='margin-bottom:4px;font-size:0.8rem;'><span class='dot' style='background:#f4a261'></span>Trabajo activo</div>
        <div style='margin-bottom:12px;font-size:0.8rem;'><span class='dot' style='background:#2a9d8f'></span>Base sólida</div>
        <div style='font-weight:600;font-size:0.72rem;color:#64748b;text-transform:uppercase;
                    letter-spacing:0.5px;margin-bottom:6px;'>Contacto (voto)</div>
        <div style='margin-bottom:4px;font-size:0.8rem;'><span class='dot' style='background:#2a9d8f'></span>Votaría</div>
        <div style='margin-bottom:4px;font-size:0.8rem;'><span class='dot' style='background:#f4a261'></span>No sabe</div>
        <div style='margin-bottom:4px;font-size:0.8rem;'><span class='dot' style='background:#e63946'></span>Nunca votaría</div>
        <div style='margin-bottom:12px;font-size:0.8rem;'>
            <span style='display:inline-block;width:10px;height:10px;border-radius:50%;
                         border:2px solid #94a3b8;margin-right:6px;vertical-align:middle;'></span>Coord. estimada
        </div>
        <div style='font-size:0.75rem;color:#94a3b8;line-height:1.4;'>
            Las coordenadas estimadas corresponden al centroide de la sección cuando no se registró GPS exacto.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_mapa:
    with st.spinner("Construyendo mapa..."):
        mapa = construir_mapa(df_f, geojson, resumen_sec, mostrar_puntos, mostrar_heatmap,
                              clasif_activas=clasif_sel,
                              secciones_activas=seccion_activa)
        st_folium(mapa, width="100%", height=520, returned_objects=[])


# ─────────────────────────────────────────────
# FICHA DE SECCIÓN
# ─────────────────────────────────────────────
if seleccion_seccion != "Todas las secciones":
    sec_id = int(seleccion_seccion.split(" · ")[0])
    spt_d  = SPT_DATA.get(sec_id, {})
    comp_d = COMP_DATA.get(sec_id, {})

    df_sec      = df[df['seccion'] == sec_id]
    n_contactos = len(df_sec)
    pct_vot = (df_sec['voto'] == 'Votaría').sum() / max(n_contactos,1) * 100
    pct_con = df_sec['conocimiento'].isin(['Algo','Mucho']).sum() / max(n_contactos,1) * 100
    pct_cel = df_sec['tiene_celular'].sum() / max(n_contactos,1) * 100

    clasif   = spt_d.get('clasificacion','')
    spt_val  = spt_d.get('SPT', 0)
    color_z  = COLORES.get(clasif, '#94a3b8')
    etiq_z   = ETIQUETAS_ZONA.get(clasif, clasif)
    ambito_z = ETIQUETAS_AMBITO.get(spt_d.get('ambito',''), '')
    arq      = spt_d.get('arq','')
    tactica  = spt_d.get('tactica','')

    tiene_enc1     = sec_id in SECCIONES_ENC_REAL
    es_knn         = sec_id in SECCIONES_KNN
    hist_parcial   = sec_id in SECCIONES_HIST_PARCIAL
    es_prioritaria = clasif == 'Prioritaria'
    sin_operativo  = n_contactos == 0

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#004a6e,#007cab);
                border-radius:12px;padding:20px 24px;margin-bottom:8px;
                border-left:5px solid {color_z};'>
        <div style='display:flex;align-items:center;gap:16px;flex-wrap:wrap;'>
            <div>
                <div style='color:#94a3b8;font-size:0.72rem;font-weight:700;
                            text-transform:uppercase;letter-spacing:1px;'>SECCIÓN</div>
                <div style='color:#fff;font-size:2.2rem;font-weight:700;
                            font-family:"IBM Plex Mono",monospace;line-height:1;'>{sec_id}</div>
            </div>
            <div style='flex:1;'>
                <span style='background:{color_z};color:#fff;padding:4px 12px;
                             border-radius:20px;font-size:0.78rem;font-weight:700;'>{etiq_z}</span>
                <span style='background:rgba(255,255,255,0.1);color:#94a3b8;
                             padding:4px 12px;border-radius:20px;font-size:0.78rem;margin-left:6px;'>{ambito_z}</span>
                <div style='color:#cbd5e1;font-size:0.85rem;margin-top:8px;'>
                    SPT <b style='color:#fff'>{spt_val:.1f}</b> &nbsp;·&nbsp;
                    Arquetipo dominante <b style='color:#fff'>{arq}</b> &nbsp;·&nbsp; {tactica}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if es_prioritaria and sin_operativo:
        st.markdown("""
        <div class='alerta-critica'>
            <div class='titulo'>⚠️ Sección prioritaria sin contactos registrados</div>
            <div class='detalle'>Esta sección tiene el mayor potencial electoral del municipio
            y no ha recibido visita del operativo. Requiere atención inmediata.</div>
        </div>
        """, unsafe_allow_html=True)

    col_op, col_enc, col_elect = st.columns(3)

    with col_op:
        st.markdown("**📋 Operativo de inducción**")
        if sin_operativo:
            st.markdown("<div class='alerta-critica'><div class='titulo'>Sin contactos registrados</div></div>",
                        unsafe_allow_html=True)
        else:
            st.metric("Contactos levantados", f"{n_contactos:,}")
            st.metric("Dispuestos a votar",   f"{pct_vot:.0f}%")
            st.metric("Conocen al aspirante", f"{pct_con:.0f}%")
            st.metric("Con celular válido",   f"{pct_cel:.0f}%")

    with col_enc:
        st.markdown("**🔬 Encuesta 1 (feb 2026)**")
        if tiene_enc1:
            st.markdown("""
            <div class='alerta-info'>
                ✅ <b>Datos de encuesta real</b><br>
                Perfil calculado con entrevistas presenciales en esta sección.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:#FEF9E7;border-left:4px solid #f4a261;border-radius:6px;
                        padding:10px 14px;font-size:0.82rem;color:#92400e;'>
                🔄 <b>Perfil estimado por modelo (KNN)</b><br>
                No fue muestreada en Encuesta 1.
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style='margin-top:10px;font-size:0.82rem;'>
            <div style='display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #f1f5f9;'>
                <span style='color:#64748b;'>No nos conocen</span><b>{spt_d.get('pct_no_alc',0):.0f}%</b>
            </div>
            <div style='display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #f1f5f9;'>
                <span style='color:#64748b;'>Conocen, no han decidido</span><b>{spt_d.get('pct_pers',0):.0f}%</b>
            </div>
            <div style='display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #f1f5f9;'>
                <span style='color:#64748b;'>Ya votan con nosotros</span><b>{spt_d.get('pct_duro',0):.0f}%</b>
            </div>
            <div style='display:flex;justify-content:space-between;padding:4px 0;'>
                <span style='color:#64748b;'>No los vamos a convencer</span><b>{spt_d.get('pct_no_conv',0):.0f}%</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_elect:
        st.markdown("**🗳️ Historial electoral**")
        if hist_parcial:
            st.markdown("""
            <div style='background:#FEF9E7;border-left:4px solid #f4a261;border-radius:6px;
                        padding:8px 12px;font-size:0.8rem;color:#92400e;margin-bottom:8px;'>
                ⚠️ Solo datos de 2024 — sección creada en redistritación
            </div>""", unsafe_allow_html=True)

        if comp_d:
            margen      = comp_d.get('margen', 0)
            tendencia   = comp_d.get('tendencia')
            pct_morena  = comp_d.get('pct_morena', 0)
            volatilidad = comp_d.get('volatilidad')
            clasif_e    = comp_d.get('clasif_elect','')

            color_clasif_e = {'Favorable':'#2a9d8f','Competida':'#f4a261','Adversa':'#e63946'}.get(clasif_e,'#94a3b8')
            flecha_tend    = ('↑ sube' if tendencia > 0 else '↓ baja') if tendencia is not None else ''
            alerta_margen  = '<span style="color:#e63946;font-weight:700;"> ⚠️ en riesgo</span>' if margen < 10 else ''

            st.markdown(f"""
            <div style='font-size:0.82rem;'>
                <div style='margin-bottom:6px;'>
                    <span style='background:{color_clasif_e};color:#fff;padding:3px 10px;
                                 border-radius:20px;font-size:0.75rem;font-weight:700;'>{clasif_e}</span>
                </div>
                <div style='display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #f1f5f9;'>
                    <span style='color:#64748b;'>Morena 2024</span><b>{pct_morena:.1f}%</b>
                </div>
                <div style='display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #f1f5f9;'>
                    <span style='color:#64748b;'>Margen de victoria</span><b>{margen:.1f} pts{alerta_margen}</b>
                </div>
                {f'<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #f1f5f9;"><span style="color:#64748b;">Tendencia Morena</span><b>{flecha_tend} +{tendencia:.1f} pts</b></div>' if tendencia is not None else ''}
                {f'<div style="display:flex;justify-content:space-between;padding:4px 0;"><span style="color:#64748b;">Volatilidad</span><b>{volatilidad:.1f}</b></div>' if volatilidad is not None else ''}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TABS DE ANÁLISIS
# ─────────────────────────────────────────────
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "📊 Cobertura por sección",
    "🎯 Calidad del contacto",
    "📈 Ritmo del operativo"
])


# ── TAB 1: COBERTURA ──
with tab1:
    st.markdown("#### ¿El esfuerzo está donde más importa?")
    st.markdown(
        "<div class='alerta-info'>La tabla está ordenada por prioridad (SPT). "
        "Las secciones con ⚠️ son zonas de alta prioridad con cobertura insuficiente.</div>",
        unsafe_allow_html=True
    )

    tabla = resumen_sec.copy()
    tabla['Sección']           = tabla['seccion'].astype(int)
    tabla['Zona']              = tabla['clasificacion'].map(ETIQUETAS_ZONA)
    tabla['Territorio']        = tabla['ambito'].map(ETIQUETAS_AMBITO)
    tabla['SPT']               = tabla['SPT'].round(1)
    tabla['Contactos']         = tabla['total'].astype(int)
    tabla['Con celular']       = tabla['pct_celular'].apply(lambda x: f"{x:.0f}%")
    tabla['Votarían']          = tabla['pct_votaria'].apply(lambda x: f"{x:.0f}%")
    tabla['Conocen aspirante'] = tabla['pct_conoce'].apply(lambda x: f"{x:.0f}%")
    tabla['Brecha']            = tabla['brecha_label']

    cols_show = ['Sección','Zona','Territorio','SPT','Contactos',
                 'Con celular','Votarían','Conocen aspirante','Brecha']

    st.dataframe(
        tabla[cols_show],
        use_container_width=True,
        hide_index=True,
        column_config={
            'SPT': st.column_config.ProgressColumn('SPT', min_value=0, max_value=100, format="%.1f"),
            'Contactos': st.column_config.NumberColumn('Contactos', format="%d"),
        }
    )

    secciones_spt = set(SPT_DATA.keys())
    secciones_op  = set(resumen_sec['seccion'].dropna().astype(int).tolist())
    sin_cobertura = secciones_spt - secciones_op

    if sin_cobertura:
        st.markdown("**Secciones sin ningún contacto registrado:**")
        filas = []
        for s in sorted(sin_cobertura):
            d = SPT_DATA.get(s, {})
            filas.append({
                'Sección':    s,
                'Zona':       ETIQUETAS_ZONA.get(d.get('clasificacion',''), d.get('clasificacion','')),
                'SPT':        d.get('SPT', 0),
                'Territorio': ETIQUETAS_AMBITO.get(d.get('ambito',''), ''),
            })
        df_sin = pd.DataFrame(filas).sort_values('SPT', ascending=False)
        st.dataframe(df_sin, use_container_width=True, hide_index=True)


# ── TAB 2: CALIDAD DEL CONTACTO ──
with tab2:
    st.markdown("#### ¿Qué están logrando las brigadas en campo?")

    col_a, col_b = st.columns(2)

    with col_a:
        voto_counts = df_f['voto'].value_counts().reset_index()
        voto_counts.columns = ['Disponibilidad', 'Contactos']
        orden_voto = ['Votaría', 'No sabe', 'Nunca votaría', 'Sin dato']
        voto_counts['Disponibilidad'] = pd.Categorical(voto_counts['Disponibilidad'], categories=orden_voto, ordered=True)
        voto_counts = voto_counts.sort_values('Disponibilidad')

        colores_voto = {'Votaría':'#2a9d8f','No sabe':'#f4a261','Nunca votaría':'#e63946','Sin dato':'#adb5bd'}

        fig_voto = px.bar(voto_counts, x='Contactos', y='Disponibilidad', orientation='h',
                          color='Disponibilidad', color_discrete_map=colores_voto,
                          title="Disponibilidad de voto")
        fig_voto.update_layout(showlegend=False, plot_bgcolor='white', paper_bgcolor='white',
                               font_family='IBM Plex Sans', title_font_size=14,
                               margin=dict(l=10,r=10,t=40,b=10), height=280)
        fig_voto.update_xaxes(showgrid=True, gridcolor='#f1f5f9')
        fig_voto.update_yaxes(showgrid=False)
        st.plotly_chart(fig_voto, use_container_width=True)

    with col_b:
        conoc_counts = df_f['conocimiento'].value_counts().reset_index()
        conoc_counts.columns = ['Conocimiento', 'Contactos']
        orden_conoc = ['Mucho','Algo','Poco','Nada','Sin dato']
        conoc_counts['Conocimiento'] = pd.Categorical(conoc_counts['Conocimiento'], categories=orden_conoc, ordered=True)
        conoc_counts = conoc_counts.sort_values('Conocimiento')

        colores_conoc = {'Mucho':'#2a9d8f','Algo':'#52b69a','Poco':'#f4a261','Nada':'#e63946','Sin dato':'#adb5bd'}

        fig_conoc = px.bar(conoc_counts, x='Contactos', y='Conocimiento', orientation='h',
                           color='Conocimiento', color_discrete_map=colores_conoc,
                           title="Conocimiento del aspirante")
        fig_conoc.update_layout(showlegend=False, plot_bgcolor='white', paper_bgcolor='white',
                                font_family='IBM Plex Sans', title_font_size=14,
                                margin=dict(l=10,r=10,t=40,b=10), height=280)
        fig_conoc.update_xaxes(showgrid=True, gridcolor='#f1f5f9')
        fig_conoc.update_yaxes(showgrid=False)
        st.plotly_chart(fig_conoc, use_container_width=True)

    st.markdown("**Calidad por zona estratégica**")
    if len(resumen_sec) > 0:
        tabla_calidad = resumen_sec.groupby('clasificacion').agg(
            Secciones=('seccion','count'),
            Contactos=('total','sum'),
            Votarían=('pct_votaria','mean'),
            No_sabe=('no_sabe','sum'),
            Conocen=('pct_conoce','mean'),
            Con_celular=('pct_celular','mean'),
        ).reset_index()
        tabla_calidad['Zona']                    = tabla_calidad['clasificacion'].map(ETIQUETAS_ZONA)
        tabla_calidad['Votarían (%)']            = tabla_calidad['Votarían'].apply(lambda x: f"{x:.0f}%")
        tabla_calidad['Conocen aspirante (%)']   = tabla_calidad['Conocen'].apply(lambda x: f"{x:.0f}%")
        tabla_calidad['Con celular (%)']         = tabla_calidad['Con_celular'].apply(lambda x: f"{x:.0f}%")
        st.dataframe(
            tabla_calidad[['Zona','Secciones','Contactos','Votarían (%)','Conocen aspirante (%)','Con celular (%)']],
            use_container_width=True, hide_index=True
        )


# ── TAB 3: RITMO TEMPORAL ──
with tab3:
    st.markdown("#### ¿El operativo está acelerando o perdiendo ritmo?")

    df_tempo = df_f.copy()
    df_tempo['dia'] = df_tempo['Created Date'].dt.date
    por_dia = df_tempo.groupby('dia').size().reset_index(name='contactos')
    por_dia['dia'] = pd.to_datetime(por_dia['dia'])
    por_dia = por_dia.sort_values('dia')
    por_dia['acumulado'] = por_dia['contactos'].cumsum()

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        fig_dia = go.Figure()
        fig_dia.add_trace(go.Bar(x=por_dia['dia'], y=por_dia['contactos'],
                                 name='Por día', marker_color='#007cab', opacity=0.7))
        if len(por_dia) >= 3:
            por_dia['ma3'] = por_dia['contactos'].rolling(3, center=True).mean()
            fig_dia.add_trace(go.Scatter(x=por_dia['dia'], y=por_dia['ma3'],
                                         name='Tendencia (3 días)',
                                         line=dict(color='#e63946', width=2.5), mode='lines'))
        fig_dia.update_layout(title='Contactos por día', plot_bgcolor='white', paper_bgcolor='white',
                              font_family='IBM Plex Sans', legend=dict(orientation='h', y=-0.2),
                              margin=dict(l=10,r=10,t=40,b=10), height=300)
        fig_dia.update_xaxes(showgrid=False)
        fig_dia.update_yaxes(showgrid=True, gridcolor='#f1f5f9')
        st.plotly_chart(fig_dia, use_container_width=True)

    with col_r2:
        fig_acum = go.Figure()
        fig_acum.add_trace(go.Scatter(x=por_dia['dia'], y=por_dia['acumulado'],
                                      mode='lines+markers', line=dict(color='#2a9d8f', width=3),
                                      marker=dict(size=5), fill='tozeroy',
                                      fillcolor='rgba(42,157,143,0.1)', name='Acumulado'))
        fig_acum.update_layout(title='Contactos acumulados', plot_bgcolor='white', paper_bgcolor='white',
                               font_family='IBM Plex Sans', showlegend=False,
                               margin=dict(l=10,r=10,t=40,b=10), height=300)
        fig_acum.update_xaxes(showgrid=False)
        fig_acum.update_yaxes(showgrid=True, gridcolor='#f1f5f9')
        st.plotly_chart(fig_acum, use_container_width=True)

    # ── CAMBIO 2: resumen semanal dinámico ──
    st.markdown("**Resumen semanal del operativo**")
    por_semana = df_f.groupby('semana_label').agg(
        Contactos=('seccion','count'),
        Secciones=('seccion','nunique'),
        Votarían=('voto', lambda x: (x == 'Votaría').sum()),
        Con_celular=('tiene_celular','sum'),
    ).reset_index()
    por_semana['% Votarían']   = (por_semana['Votarían']   / por_semana['Contactos'] * 100).round(0).astype(int).astype(str) + '%'
    por_semana['% Con celular']= (por_semana['Con_celular'] / por_semana['Contactos'] * 100).round(0).astype(int).astype(str) + '%'

    # Ordenar cronológicamente usando el número de semana
    semana_orden = {v: k for k, v in semana_map.items()}
    por_semana['_orden'] = por_semana['semana_label'].map(semana_orden)
    por_semana = por_semana.sort_values('_orden').drop(columns='_orden')
    por_semana.rename(columns={'semana_label': 'Semana'}, inplace=True)

    st.dataframe(
        por_semana[['Semana','Contactos','Secciones','% Votarían','% Con celular']],
        use_container_width=True, hide_index=True
    )


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<hr style='border:none;border-top:1px solid #e2e8f0;margin:32px 0 16px 0;'>
<div style='text-align:center;color:#94a3b8;font-size:0.75rem;'>
    Inteligencia Electoral Zacatlán · JCLY Morena 2026 · Confidencial
</div>
""", unsafe_allow_html=True)