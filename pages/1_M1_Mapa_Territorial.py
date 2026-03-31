"""
M1 — Mapa de Prioridad Territorial v2
Inteligencia Electoral Zacatlán | JCLY Morena 2026
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json, os

# ── Configuración ────────────────────────────────────────────────────
st.set_page_config(
    page_title="M1 · Mapa Territorial · Zacatlán 2026",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Demo mode — no modificar ────────────────────────────────────────────────
from demo_mode import check_demo_mode
check_demo_mode()


# ── Estilos ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

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
        background-color: #243058 !important;
        border-color: #3d5a99 !important;
    }

    .zona-card {
        border-radius: 12px; padding: 14px 18px; margin: 6px 0;
        border-left: 6px solid #ccc;
    }
    .zona-card.prioritaria   { background:#fde8ea; border-color:#e63946; }
    .zona-card.consolidacion { background:#fef3e8; border-color:#f4a261; }
    .zona-card.mantenimiento { background:#e8f5f3; border-color:#2a9d8f; }
    .zona-title { font-size:13px; font-weight:700; color:#1a1a2e; }
    .zona-num   { font-size:26px; font-weight:800; }
    .zona-label { font-size:11px; color:#777; }
    .zona-sub   { font-size:11px; color:#555; margin-top:4px; line-height:1.4; }

    .ficha-header {
        background: linear-gradient(135deg,#004a6e,#007cab);
        color:white; padding:16px 20px; border-radius:12px; margin-bottom:10px;
    }
    .badge { display:inline-block; padding:3px 10px; border-radius:20px;
             font-size:11px; font-weight:700; margin:2px; }
    .badge-prioritaria   { background:#e63946; color:white; }
    .badge-consolidacion { background:#f4a261; color:white; }
    .badge-mantenimiento { background:#2a9d8f; color:white; }
    .badge-encuesta      { background:#457b9d; color:white; }
    .badge-proyectado    { background:#adb5bd; color:white; }
    .badge-parcial       { background:#e9c46a; color:#333; }

    .bar-label { font-size:12px; color:#333; display:flex;
                 justify-content:space-between; margin-bottom:2px; }
    .bar-hint  { font-size:10px; color:#888; margin-bottom:8px; }
    .bar-bg    { background:#e9ecef; border-radius:4px; height:10px; }
    .bar-fill  { height:10px; border-radius:4px; }

    .tactics-box {
        background:#fff3cd; border:1px solid #ffc107; border-radius:8px;
        padding:10px 14px; font-size:13px; font-weight:600;
        color:#856404; margin:8px 0;
    }
    .alert-box { border-radius:8px; padding:9px 13px; font-size:12px; margin:5px 0; }
    .alert-warn { background:#fff3cd; border-left:4px solid #ffc107; color:#856404; }
    .alert-tip  { background:#d4edda; border-left:4px solid #28a745; color:#155724; }

    .arq-card {
        background:white; border-radius:10px; padding:12px 14px;
        border-top:4px solid #ccc; box-shadow:0 1px 4px rgba(0,0,0,0.08); height:100%;
    }
    .arq-code { font-size:18px; font-weight:800; }
    .arq-name { font-size:12px; font-weight:600; color:#444; margin:2px 0; }
    .arq-size { font-size:11px; color:#888; }
    .arq-pri  { font-size:10px; font-weight:700; margin-top:4px; }
    .arq-msg  { font-size:11px; color:#555; margin-top:6px; line-height:1.4;
                border-top:1px solid #eee; padding-top:6px; }

    .section-title {
        font-size:16px; font-weight:700; color:#1a1a2e;
        border-left:4px solid #e63946; padding-left:10px; margin:16px 0 10px;
    }
    .comp-row { display:flex; justify-content:space-between; font-size:12px;
                padding:3px 0; border-bottom:1px solid #f0f0f0; }
    .comp-label { color:#555; }
    .comp-val   { font-weight:700; color:#1a1a2e; }
</style>
""", unsafe_allow_html=True)

# ── Constantes ───────────────────────────────────────────────────────
COLOR_MAP = {
    "Prioritaria":   "#e63946",
    "Consolidacion": "#f4a261",
    "Mantenimiento": "#2a9d8f",
}

ZONA_INFO = {
    "Prioritaria": {
        "emoji": "🔴", "rango": "SPT > 70",
        "titulo": "Zona de máxima atención",
        "desc": "Aquí están los votos que faltan. Brigadas presenciales, visitas del candidato y pauta digital. Monitoreo semanal.",
    },
    "Consolidacion": {
        "emoji": "🟡", "rango": "SPT 40–70",
        "titulo": "Zona de trabajo activo",
        "desc": "Terreno en disputa. Requiere presencia constante, activación de la base sólida y mensajes segmentados.",
    },
    "Mantenimiento": {
        "emoji": "🟢", "rango": "SPT < 40",
        "titulo": "Zona de base sólida",
        "desc": "Votos seguros. Activar únicamente la base existente. No desperdiciar recursos de persuasión aquí.",
    },
}

AMBITO_LABEL = {
    "urbano":         "🏙️ Urbano",
    "rural_media":    "🌾 Rural Media",
    "rural_marginal": "🏔️ Rural Marginal",
}

TACTICA_INFO = {
    "Brigadas de primer contacto urgentes":              {"emoji":"🚶","desc":"La mayoría no nos conoce. Hay que llegar puerta a puerta con nombre y cara del candidato."},
    "Activacion y cierre de voto":                       {"emoji":"🤝","desc":"Ya nos conocen pero no han decidido. El trabajo es convencer, no presentarse."},
    "Brigadas primer contacto + cierre":                 {"emoji":"🔄","desc":"Mezcla de los dos perfiles. Combinar presentación con activación de indecisos."},
    "Presencia regular y activacion de multiplicadores": {"emoji":"📣","desc":"La base sólida ya está. Convertir a esos votantes en promotores de su red."},
    "Activar base solida unicamente":                    {"emoji":"🛡️","desc":"No es momento de persuadir. Solo asegurar que quienes ya nos apoyan lleguen a votar."},
}

ARQUETIPOS = {
    "U0": {"nombre":"El Indeciso Crítico",    "ambito":"Urbano", "n":"35 (22%)",   "prioridad":"Máxima — cierre",        "color":"#e63946","msg":"Conoce a JCLY. Dividido 45/40 a favor. Sin partido. Mensaje: JCLY no es el gobierno actual, es la alternativa real."},
    "U1": {"nombre":"El Desconectado Urbano", "ambito":"Urbano", "n":"91 (57%)",   "prioridad":"Alta — visibilidad",     "color":"#f4a261","msg":"44% no conoce a JCLY. El grupo urbano más grande. Necesita primera impresión: presencia física en colonia, nombre y cara."},
    "U2": {"nombre":"El Bastión JCLY",        "ambito":"Urbano", "n":"21 (13%)",   "prioridad":"Mantener — multiplicar", "color":"#2a9d8f","msg":"76% evalúa muy bien. 76% votaría. Base sólida Morena. Rol: promotor activo en su red de contactos."},
    "U3": {"nombre":"El Escéptico Mayor",     "ambito":"Urbano", "n":"12 (7.5%)",  "prioridad":"Baja — mínima inversión","color":"#adb5bd","msg":"45–59 años. Desconfía del ayuntamiento. Agenda: corrupción + seguridad. No mover recursos a este segmento."},
    "R0": {"nombre":"El Simpatizante Activo", "ambito":"Rural",  "n":"118 (32.6%)","prioridad":"Alta — volumen",         "color":"#f4a261","msg":"100% conoce a JCLY. 55% votaría. Agenda: agua + servicios. Mensaje: JCLY sabe lo que tu comunidad necesita y lo va a resolver."},
    "R1": {"nombre":"El Campo No Alcanzado",  "ambito":"Rural",  "n":"147 (40.6%)","prioridad":"Máxima — brigadas",      "color":"#e63946","msg":"77% no conoce a JCLY. El cluster más grande del proyecto. Solo brigadas presenciales lo alcanzan. No rechaza — simplemente no sabe quién es."},
    "R2": {"nombre":"El Núcleo Duro Rural",   "ambito":"Rural",  "n":"32 (8.8%)",  "prioridad":"Mantener — brigadistas", "color":"#2a9d8f","msg":"87% evalúa muy bien. 93% votaría. Son los líderes naturales del territorio. Capacitarlos como brigadistas."},
    "R3": {"nombre":"El Opositor Rural",      "ambito":"Rural",  "n":"33 (9.1%)",  "prioridad":"Descartar",              "color":"#6c757d","msg":"69% evaluación negativa. 81% nunca votaría. Rechazo no contagioso. Cada peso aquí es un peso que no llega al Campo No Alcanzado."},
    "R4": {"nombre":"El Indiferente Rural",   "ambito":"Rural",  "n":"32 (8.8%)",  "prioridad":"Baja — contacto tardío", "color":"#adb5bd","msg":"Conoce a JCLY pero 53% sin opinión. Mezcla de jóvenes y mayores de 60. Contacto tardío si hay recursos disponibles."},
}

METRICA_INFO = {
    "pct_no_alcanzados":  {"label":"No nos conocen",                    "hint":"→ Enviar brigadas de primer contacto","color":"#e63946"},
    "pct_persuadibles":   {"label":"Nos conocen pero no han decidido",  "hint":"→ Trabajo de activación y cierre",   "color":"#f4a261"},
    "pct_nucleo_duro":    {"label":"Ya votan con nosotros",             "hint":"→ Convertirlos en multiplicadores",  "color":"#2a9d8f"},
    "pct_no_convertibles":{"label":"No los vamos a convencer",         "hint":"→ No invertir recursos aquí",        "color":"#adb5bd"},
}

# ── Datos SPT ────────────────────────────────────────────────────────
SPT_DATA = [
{"seccion":2486,"ambito_iter":"urbano","activa":True,"SPT":71.48,"clasificacion":"Prioritaria","tactica_recomendada":"Brigadas de primer contacto urgentes","score_electoral_norm":76.09,"score_demografico":37.95,"score_arquetipos":93.85,"score_cobertura":100.0,"pct_no_alcanzados":56.9,"pct_persuadibles":38.4,"pct_nucleo_duro":4.7,"pct_no_convertibles":0.0,"arq_dominante":"R1","entrevistas":0,"fuente_arquetipos":"proyectado","score_electoral_parcial":False},
{"seccion":2471,"ambito_iter":"rural_marginal","activa":True,"SPT":70.99,"clasificacion":"Prioritaria","tactica_recomendada":"Brigadas de primer contacto urgentes","score_electoral_norm":82.13,"score_demografico":67.56,"score_arquetipos":62.86,"score_cobertura":62.64,"pct_no_alcanzados":54.6,"pct_persuadibles":25.4,"pct_nucleo_duro":9.1,"pct_no_convertibles":10.8,"arq_dominante":"R1","entrevistas":23,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2489,"ambito_iter":"rural_marginal","activa":True,"SPT":70.8,"clasificacion":"Prioritaria","tactica_recomendada":"Brigadas primer contacto + cierre","score_electoral_norm":61.7,"score_demografico":79.45,"score_arquetipos":61.47,"score_cobertura":100.0,"pct_no_alcanzados":47.3,"pct_persuadibles":35.6,"pct_nucleo_duro":5.1,"pct_no_convertibles":11.9,"arq_dominante":"R1","entrevistas":0,"fuente_arquetipos":"proyectado","score_electoral_parcial":False},
{"seccion":2488,"ambito_iter":"rural_marginal","activa":True,"SPT":70.72,"clasificacion":"Prioritaria","tactica_recomendada":"Brigadas primer contacto + cierre","score_electoral_norm":100.0,"score_demografico":67.82,"score_arquetipos":61.47,"score_cobertura":0.0,"pct_no_alcanzados":47.3,"pct_persuadibles":35.6,"pct_nucleo_duro":5.1,"pct_no_convertibles":11.9,"arq_dominante":"R1","entrevistas":26,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2483,"ambito_iter":"urbano","activa":True,"SPT":61.72,"clasificacion":"Consolidacion","tactica_recomendada":"Activacion y cierre de voto","score_electoral_norm":61.61,"score_demografico":37.76,"score_arquetipos":75.32,"score_cobertura":100.0,"pct_no_alcanzados":35.9,"pct_persuadibles":60.1,"pct_nucleo_duro":0.0,"pct_no_convertibles":4.0,"arq_dominante":"R0","entrevistas":0,"fuente_arquetipos":"proyectado","score_electoral_parcial":False},
{"seccion":2896,"ambito_iter":"rural_media","activa":True,"SPT":57.97,"clasificacion":"Consolidacion","tactica_recomendada":"Brigadas de primer contacto urgentes","score_electoral_norm":71.94,"score_demografico":40.95,"score_arquetipos":42.04,"score_cobertura":100.0,"pct_no_alcanzados":53.5,"pct_persuadibles":16.2,"pct_nucleo_duro":26.8,"pct_no_convertibles":3.5,"arq_dominante":"U1","entrevistas":0,"fuente_arquetipos":"proyectado","score_electoral_parcial":True},
{"seccion":2809,"ambito_iter":"rural_media","activa":True,"SPT":54.67,"clasificacion":"Consolidacion","tactica_recomendada":"Activacion y cierre de voto","score_electoral_norm":60.56,"score_demografico":40.95,"score_arquetipos":48.89,"score_cobertura":89.62,"pct_no_alcanzados":26.2,"pct_persuadibles":60.7,"pct_nucleo_duro":0.0,"pct_no_convertibles":13.1,"arq_dominante":"R0","entrevistas":9,"fuente_arquetipos":"encuesta","score_electoral_parcial":True},
{"seccion":2464,"ambito_iter":"rural_media","activa":True,"SPT":53.68,"clasificacion":"Consolidacion","tactica_recomendada":"Activacion y cierre de voto","score_electoral_norm":75.33,"score_demografico":22.98,"score_arquetipos":41.66,"score_cobertura":100.0,"pct_no_alcanzados":27.4,"pct_persuadibles":55.0,"pct_nucleo_duro":3.8,"pct_no_convertibles":13.8,"arq_dominante":"R0","entrevistas":0,"fuente_arquetipos":"proyectado","score_electoral_parcial":False},
{"seccion":2473,"ambito_iter":"urbano","activa":True,"SPT":51.91,"clasificacion":"Consolidacion","tactica_recomendada":"Brigadas de primer contacto urgentes","score_electoral_norm":26.09,"score_demografico":40.38,"score_arquetipos":93.85,"score_cobertura":72.06,"pct_no_alcanzados":56.9,"pct_persuadibles":38.4,"pct_nucleo_duro":4.7,"pct_no_convertibles":0.0,"arq_dominante":"R1","entrevistas":28,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2467,"ambito_iter":"urbano","activa":True,"SPT":50.88,"clasificacion":"Consolidacion","tactica_recomendada":"Brigadas de primer contacto urgentes","score_electoral_norm":44.8,"score_demografico":23.34,"score_arquetipos":83.91,"score_cobertura":72.23,"pct_no_alcanzados":68.4,"pct_persuadibles":15.9,"pct_nucleo_duro":15.7,"pct_no_convertibles":0.0,"arq_dominante":"U1","entrevistas":16,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2487,"ambito_iter":"rural_marginal","activa":True,"SPT":50.5,"clasificacion":"Consolidacion","tactica_recomendada":"Brigadas primer contacto + cierre","score_electoral_norm":24.0,"score_demografico":55.75,"score_arquetipos":61.47,"score_cobertura":100.0,"pct_no_alcanzados":47.3,"pct_persuadibles":35.6,"pct_nucleo_duro":5.1,"pct_no_convertibles":11.9,"arq_dominante":"R1","entrevistas":0,"fuente_arquetipos":"proyectado","score_electoral_parcial":False},
{"seccion":2485,"ambito_iter":"rural_media","activa":True,"SPT":49.76,"clasificacion":"Consolidacion","tactica_recomendada":"Activacion y cierre de voto","score_electoral_norm":76.24,"score_demografico":33.65,"score_arquetipos":41.66,"score_cobertura":25.65,"pct_no_alcanzados":27.4,"pct_persuadibles":55.0,"pct_nucleo_duro":3.8,"pct_no_convertibles":13.8,"arq_dominante":"R0","entrevistas":31,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2472,"ambito_iter":"rural_marginal","activa":True,"SPT":49.25,"clasificacion":"Consolidacion","tactica_recomendada":"Brigadas de primer contacto urgentes","score_electoral_norm":0.0,"score_demografico":78.47,"score_arquetipos":62.86,"score_cobertura":100.0,"pct_no_alcanzados":54.6,"pct_persuadibles":25.4,"pct_nucleo_duro":9.1,"pct_no_convertibles":10.8,"arq_dominante":"R1","entrevistas":0,"fuente_arquetipos":"proyectado","score_electoral_parcial":False},
{"seccion":2470,"ambito_iter":"urbano","activa":True,"SPT":49.06,"clasificacion":"Consolidacion","tactica_recomendada":"Brigadas de primer contacto urgentes","score_electoral_norm":11.34,"score_demografico":39.3,"score_arquetipos":100.0,"score_cobertura":83.0,"pct_no_alcanzados":64.9,"pct_persuadibles":29.7,"pct_nucleo_duro":0.0,"pct_no_convertibles":5.4,"arq_dominante":"R1","entrevistas":17,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2478,"ambito_iter":"urbano","activa":True,"SPT":48.86,"clasificacion":"Consolidacion","tactica_recomendada":"Presencia regular y activacion de multiplicadores","score_electoral_norm":67.38,"score_demografico":33.76,"score_arquetipos":28.02,"score_cobertura":81.4,"pct_no_alcanzados":33.3,"pct_persuadibles":39.0,"pct_nucleo_duro":17.2,"pct_no_convertibles":10.5,"arq_dominante":"R1","entrevistas":46,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2475,"ambito_iter":"urbano","activa":True,"SPT":48.45,"clasificacion":"Consolidacion","tactica_recomendada":"Activacion y cierre de voto","score_electoral_norm":29.5,"score_demografico":40.69,"score_arquetipos":75.32,"score_cobertura":70.9,"pct_no_alcanzados":35.9,"pct_persuadibles":60.1,"pct_nucleo_duro":0.0,"pct_no_convertibles":4.0,"arq_dominante":"R0","entrevistas":21,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2808,"ambito_iter":"rural_media","activa":True,"SPT":48.07,"clasificacion":"Consolidacion","tactica_recomendada":"Brigadas de primer contacto urgentes","score_electoral_norm":43.63,"score_demografico":40.95,"score_arquetipos":42.04,"score_cobertura":100.0,"pct_no_alcanzados":53.5,"pct_persuadibles":16.2,"pct_nucleo_duro":26.8,"pct_no_convertibles":3.5,"arq_dominante":"U1","entrevistas":0,"fuente_arquetipos":"proyectado","score_electoral_parcial":True},
{"seccion":2460,"ambito_iter":"urbano","activa":True,"SPT":46.42,"clasificacion":"Consolidacion","tactica_recomendada":"Brigadas de primer contacto urgentes","score_electoral_norm":35.34,"score_demografico":23.28,"score_arquetipos":68.27,"score_cobertura":100.0,"pct_no_alcanzados":56.5,"pct_persuadibles":25.5,"pct_nucleo_duro":11.7,"pct_no_convertibles":6.3,"arq_dominante":"U1","entrevistas":0,"fuente_arquetipos":"proyectado","score_electoral_parcial":False},
{"seccion":2463,"ambito_iter":"urbano","activa":True,"SPT":44.33,"clasificacion":"Consolidacion","tactica_recomendada":"Brigadas de primer contacto urgentes","score_electoral_norm":23.76,"score_demografico":15.8,"score_arquetipos":99.77,"score_cobertura":63.33,"pct_no_alcanzados":63.8,"pct_persuadibles":31.3,"pct_nucleo_duro":0.0,"pct_no_convertibles":5.0,"arq_dominante":"U1","entrevistas":25,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2484,"ambito_iter":"urbano","activa":True,"SPT":42.93,"clasificacion":"Consolidacion","tactica_recomendada":"Presencia regular y activacion de multiplicadores","score_electoral_norm":44.56,"score_demografico":32.17,"score_arquetipos":43.3,"score_cobertura":68.64,"pct_no_alcanzados":33.5,"pct_persuadibles":46.8,"pct_nucleo_duro":9.1,"pct_no_convertibles":10.6,"arq_dominante":"R0","entrevistas":55,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2476,"ambito_iter":"rural_media","activa":True,"SPT":42.93,"clasificacion":"Consolidacion","tactica_recomendada":"Brigadas de primer contacto urgentes","score_electoral_norm":20.04,"score_demografico":51.34,"score_arquetipos":42.04,"score_cobertura":100.0,"pct_no_alcanzados":53.5,"pct_persuadibles":16.2,"pct_nucleo_duro":26.8,"pct_no_convertibles":3.5,"arq_dominante":"U1","entrevistas":0,"fuente_arquetipos":"proyectado","score_electoral_parcial":False},
{"seccion":2727,"ambito_iter":"rural_media","activa":True,"SPT":42.52,"clasificacion":"Consolidacion","tactica_recomendada":"Brigadas de primer contacto urgentes","score_electoral_norm":35.37,"score_demografico":40.95,"score_arquetipos":42.04,"score_cobertura":73.47,"pct_no_alcanzados":53.5,"pct_persuadibles":16.2,"pct_nucleo_duro":26.8,"pct_no_convertibles":3.5,"arq_dominante":"U1","entrevistas":23,"fuente_arquetipos":"encuesta","score_electoral_parcial":True},
{"seccion":2481,"ambito_iter":"urbano","activa":True,"SPT":42.15,"clasificacion":"Consolidacion","tactica_recomendada":"Brigadas de primer contacto urgentes","score_electoral_norm":25.15,"score_demografico":28.47,"score_arquetipos":63.12,"score_cobertura":90.28,"pct_no_alcanzados":55.7,"pct_persuadibles":24.0,"pct_nucleo_duro":3.7,"pct_no_convertibles":16.6,"arq_dominante":"U1","entrevistas":23,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2480,"ambito_iter":"urbano","activa":True,"SPT":42.06,"clasificacion":"Consolidacion","tactica_recomendada":"Brigadas primer contacto + cierre","score_electoral_norm":39.33,"score_demografico":33.98,"score_arquetipos":41.9,"score_cobertura":76.29,"pct_no_alcanzados":36.1,"pct_persuadibles":42.1,"pct_nucleo_duro":15.7,"pct_no_convertibles":6.0,"arq_dominante":"R0","entrevistas":35,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2466,"ambito_iter":"rural_media","activa":True,"SPT":41.96,"clasificacion":"Consolidacion","tactica_recomendada":"Activacion y cierre de voto","score_electoral_norm":40.05,"score_demografico":25.08,"score_arquetipos":41.66,"score_cobertura":100.0,"pct_no_alcanzados":27.4,"pct_persuadibles":55.0,"pct_nucleo_duro":3.8,"pct_no_convertibles":13.8,"arq_dominante":"R0","entrevistas":0,"fuente_arquetipos":"proyectado","score_electoral_parcial":False},
{"seccion":2474,"ambito_iter":"urbano","activa":True,"SPT":41.66,"clasificacion":"Consolidacion","tactica_recomendada":"Brigadas primer contacto + cierre","score_electoral_norm":8.01,"score_demografico":44.61,"score_arquetipos":77.89,"score_cobertura":60.02,"pct_no_alcanzados":46.9,"pct_persuadibles":45.0,"pct_nucleo_duro":4.1,"pct_no_convertibles":4.1,"arq_dominante":"R1","entrevistas":21,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2465,"ambito_iter":"urbano","activa":True,"SPT":41.42,"clasificacion":"Consolidacion","tactica_recomendada":"Brigadas de primer contacto urgentes","score_electoral_norm":35.76,"score_demografico":20.27,"score_arquetipos":68.27,"score_cobertura":57.56,"pct_no_alcanzados":56.5,"pct_persuadibles":25.5,"pct_nucleo_duro":11.7,"pct_no_convertibles":6.3,"arq_dominante":"U1","entrevistas":39,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2895,"ambito_iter":"rural_media","activa":True,"SPT":37.42,"clasificacion":"Mantenimiento","tactica_recomendada":"Activar base solida unicamente","score_electoral_norm":52.13,"score_demografico":40.95,"score_arquetipos":0.0,"score_cobertura":68.85,"pct_no_alcanzados":25.8,"pct_persuadibles":35.4,"pct_nucleo_duro":26.0,"pct_no_convertibles":12.8,"arq_dominante":"R0","entrevistas":27,"fuente_arquetipos":"encuesta","score_electoral_parcial":True},
{"seccion":2477,"ambito_iter":"rural_media","activa":True,"SPT":36.75,"clasificacion":"Mantenimiento","tactica_recomendada":"Activar base solida unicamente","score_electoral_norm":8.01,"score_demografico":45.12,"score_arquetipos":41.66,"score_cobertura":100.0,"pct_no_alcanzados":27.4,"pct_persuadibles":55.0,"pct_nucleo_duro":3.8,"pct_no_convertibles":13.8,"arq_dominante":"R0","entrevistas":0,"fuente_arquetipos":"proyectado","score_electoral_parcial":False},
{"seccion":2482,"ambito_iter":"urbano","activa":True,"SPT":34.62,"clasificacion":"Mantenimiento","tactica_recomendada":"Activar base solida unicamente","score_electoral_norm":17.32,"score_demografico":34.52,"score_arquetipos":45.67,"score_cobertura":67.82,"pct_no_alcanzados":48.3,"pct_persuadibles":25.9,"pct_nucleo_duro":13.8,"pct_no_convertibles":12.0,"arq_dominante":"R1","entrevistas":23,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2461,"ambito_iter":"urbano","activa":True,"SPT":33.96,"clasificacion":"Mantenimiento","tactica_recomendada":"Activar base solida unicamente","score_electoral_norm":40.11,"score_demografico":15.73,"score_arquetipos":40.19,"score_cobertura":51.57,"pct_no_alcanzados":49.9,"pct_persuadibles":20.5,"pct_nucleo_duro":19.3,"pct_no_convertibles":10.3,"arq_dominante":"U1","entrevistas":33,"fuente_arquetipos":"encuesta","score_electoral_parcial":False},
{"seccion":2469,"ambito_iter":"rural_media","activa":True,"SPT":32.37,"clasificacion":"Mantenimiento","tactica_recomendada":"Activar base solida unicamente","score_electoral_norm":20.04,"score_demografico":16.46,"score_arquetipos":41.66,"score_cobertura":100.0,"pct_no_alcanzados":27.4,"pct_persuadibles":55.0,"pct_nucleo_duro":3.8,"pct_no_convertibles":13.8,"arq_dominante":"R0","entrevistas":0,"fuente_arquetipos":"proyectado","score_electoral_parcial":False},
{"seccion":2462,"ambito_iter":"urbano","activa":True,"SPT":30.74,"clasificacion":"Mantenimiento","tactica_recomendada":"Activar base solida unicamente","score_electoral_norm":17.96,"score_demografico":14.69,"score_arquetipos":40.19,"score_cobertura":100.0,"pct_no_alcanzados":49.9,"pct_persuadibles":20.5,"pct_nucleo_duro":19.3,"pct_no_convertibles":10.3,"arq_dominante":"U1","entrevistas":0,"fuente_arquetipos":"proyectado","score_electoral_parcial":False},
]

@st.cache_data
def load_data():
    return pd.DataFrame(SPT_DATA)

@st.cache_data
def load_geojson(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

df = load_data()

# ── Ruta relativa: funciona en local y en Streamlit Cloud ────────────
_BASE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(_BASE, "..", "data")

geo = None
for p in [
    os.path.join(_DATA, "zacatlan_secciones.geojson"),
    os.path.join(_BASE, "data", "zacatlan_secciones.geojson"),
    os.path.join(_BASE, "zacatlan_secciones.geojson"),
    "zacatlan_secciones.geojson",
]:
    if os.path.exists(p):
        geo = load_geojson(p)
        break

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗺️ Zacatlán 2026")
    st.markdown("**Mapa de Prioridad Territorial**")
    st.divider()

    st.markdown("### ¿Qué zonas quieres ver?")
    zona_opts = {
        "🔴 Zonas de máxima atención": "Prioritaria",
        "🟡 Zonas de trabajo activo":  "Consolidacion",
        "🟢 Zonas de base sólida":     "Mantenimiento",
    }
    zona_sel = st.multiselect(
        "Prioridad", options=list(zona_opts.keys()),
        default=list(zona_opts.keys()), label_visibility="collapsed",
    )
    filtro_clasificacion = [zona_opts[z] for z in zona_sel]

    st.markdown("### ¿Qué tipo de territorio?")
    ambito_opts = {
        "🏙️ Urbano":         "urbano",
        "🌾 Rural Media":    "rural_media",
        "🏔️ Rural Marginal": "rural_marginal",
    }
    ambito_sel = st.multiselect(
        "Ámbito", options=list(ambito_opts.keys()),
        default=list(ambito_opts.keys()), label_visibility="collapsed",
    )
    filtro_ambito = [ambito_opts[a] for a in ambito_sel]

    st.markdown("### ¿Qué operación necesitan?")
    tactica_opts_map = {
        "🚶 Primer contacto urgente":  "Brigadas de primer contacto urgentes",
        "🤝 Activación y cierre":      "Activacion y cierre de voto",
        "🔄 Primer contacto + cierre": "Brigadas primer contacto + cierre",
        "📣 Activar multiplicadores":  "Presencia regular y activacion de multiplicadores",
        "🛡️ Solo activar base sólida": "Activar base solida unicamente",
    }
    tactica_sel = st.multiselect(
        "Táctica", options=list(tactica_opts_map.keys()),
        default=list(tactica_opts_map.keys()), label_visibility="collapsed",
    )
    filtro_tactica = [tactica_opts_map[t] for t in tactica_sel]

    st.divider()
    with st.expander("ℹ️ ¿Cómo se calcula la prioridad?"):
        st.markdown("""
El **Score SPT (0–100)** combina cuatro fuentes:

- **35%** Competitividad electoral 2018–2024
- **30%** Perfil demográfico del territorio
- **25%** Disposición actual hacia JCLY
- **10%** Cobertura de campo

A mayor score → mayor urgencia de recursos.
        """)

# ── Filtro aplicado ──────────────────────────────────────────────────
df_f = df[
    df["clasificacion"].isin(filtro_clasificacion) &
    df["ambito_iter"].isin(filtro_ambito) &
    df["tactica_recomendada"].isin(filtro_tactica)
].copy()
total = len(df_f)

# ── Encabezado ───────────────────────────────────────────────────────
LOGO_B64_M1 = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAQABAADASIAAhEBAxEB/8QAHAABAQEAAwEBAQAAAAAAAAAAAAECBgcIAwUE/8QASBABAAIBAgMDBwkGBQIEBwEAAAECAwQFBgcREiExFyI1QVFhchMyUlRxgZGS0QgUQqGxwRUjYuHwY4IkMzSDFjdDRVWT8aL/xAAcAQEBAAIDAQEAAAAAAAAAAAAAAgEGBAUHAwj/xAA7EQEAAQMBAwgHBwQDAQEAAAAAAQIDBAUGEXESFSExNEFRUhMyU5GhsdEUFiIjYYHBB0Lh8CQzYnJD/9oADAMBAAIRAxEAPwDxkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH//2Q=="
st.markdown(f"""
<div style='background:linear-gradient(135deg,#004a6e 0%,#007cab 60%,#00c0ff 100%);
     border-radius:16px;padding:24px 32px;margin-bottom:24px;position:relative;overflow:hidden;'>
  <div style='position:absolute;top:-40px;right:-40px;width:140px;height:140px;
       border-radius:50%;background:rgba(255,255,255,0.05);'></div>
  <div style='display:flex;align-items:center;gap:18px;margin-bottom:10px;'>
    <img src="data:image/png;base64,{LOGO_B64_M1}"
         style='width:52px;height:52px;border-radius:10px;mix-blend-mode:lighten;flex-shrink:0;'>
    <div>
      <div style='font-size:0.70rem;font-weight:700;letter-spacing:0.13em;
           color:#00c0ff;text-transform:uppercase;margin-bottom:4px;'>
        Tu línea base propia
      </div>
      <div style='font-size:1.45rem;font-weight:800;color:#ffffff;line-height:1.2;'>
        ¿A dónde voy primero?
      </div>
    </div>
  </div>
  <div style='color:rgba(255,255,255,0.70);font-size:0.88rem;margin-left:70px;'>
    Prioridad territorial sección por sección · Inteligencia Electoral Zacatlán · JCLY Morena 2026
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tarjetas resumen ─────────────────────────────────────────────────
st.markdown('<div class="section-title">Resumen del municipio</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
for col, cls in zip([col1, col2, col3], ["Prioritaria", "Consolidacion", "Mantenimiento"]):
    info = ZONA_INFO[cls]
    n_total = len(df[df["clasificacion"] == cls])
    n_filtro = len(df_f[df_f["clasificacion"] == cls])
    with col:
        st.markdown(f"""
        <div class="zona-card {cls.lower()}">
            <div class="zona-title">{info['emoji']} {info['titulo']}</div>
            <div class="zona-num">{n_filtro}<span style="font-size:13px;color:#888;font-weight:400;"> / {n_total}</span></div>
            <div class="zona-label">secciones visibles · {info['rango']}</div>
            <div class="zona-sub">{info['desc']}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Mapa + Ficha ─────────────────────────────────────────────────────
col_mapa, col_ficha = st.columns([3, 2])

with col_mapa:
    st.markdown('<div class="section-title">Mapa</div>', unsafe_allow_html=True)
    st.caption("Haz clic en una sección para ver su ficha táctica →")

    if geo is None:
        st.warning("⚠️ Coloca `zacatlan_secciones.geojson` en el mismo directorio que este script.")
    else:
        spt_lookup = {r["seccion"]: r for r in SPT_DATA}
        secciones_filtradas = set(df_f["seccion"].tolist())

        m = folium.Map(location=[19.95, -97.96], zoom_start=11, tiles="CartoDB positron")

        folium.GeoJson(
            geo,
            style_function=lambda f: {
                "fillColor": COLOR_MAP.get(spt_lookup.get(f["properties"]["SECCION"], {}).get("clasificacion",""), "#ccc"),
                "color": "#444", "weight": 1,
                "fillOpacity": 0.85 if f["properties"]["SECCION"] in secciones_filtradas else 0.10,
            },
            highlight_function=lambda f: {"weight": 3, "color": "#fff", "fillOpacity": 0.95},
            tooltip=folium.GeoJsonTooltip(fields=["SECCION"], aliases=["Sección:"]),
        ).add_to(m)

        for feature in geo["features"]:
            sec = feature["properties"]["SECCION"]
            if sec not in secciones_filtradas:
                continue
            pts = feature["geometry"]["coordinates"][0]
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            folium.Marker(
                location=[cy, cx],
                icon=folium.DivIcon(
                    html=f'<div style="font-size:8px;font-weight:800;color:#1a1a2e;'
                         f'text-shadow:1px 1px 2px white,-1px -1px 2px white;">{sec}</div>',
                    icon_size=(40,14), icon_anchor=(20,7),
                ),
            ).add_to(m)

        map_data = st_folium(m, height=500, use_container_width=True)
        if map_data and map_data.get("last_object_clicked_tooltip"):
            try:
                sec_clicked = int(map_data["last_object_clicked_tooltip"].split("Sección:")[-1].strip().split()[0])
                st.session_state["seccion_seleccionada"] = sec_clicked
            except:
                pass

# ── Ficha táctica ────────────────────────────────────────────────────
with col_ficha:
    st.markdown('<div class="section-title">Ficha táctica</div>', unsafe_allow_html=True)

    secciones_disponibles = sorted(df_f["seccion"].tolist())
    if not secciones_disponibles:
        st.warning("Sin secciones con los filtros actuales.")
    else:
        default_sec = st.session_state.get("seccion_seleccionada", secciones_disponibles[0])
        if default_sec not in secciones_disponibles:
            default_sec = secciones_disponibles[0]

        sec_sel = st.selectbox(
            "Seleccionar sección",
            options=secciones_disponibles,
            index=secciones_disponibles.index(default_sec),
            format_func=lambda x: f"Sección {x}",
        )
        st.session_state["seccion_seleccionada"] = sec_sel

        row = df[df["seccion"] == sec_sel].iloc[0]
        cls = row["clasificacion"]
        info_zona = ZONA_INFO[cls]
        arq = row["arq_dominante"]
        arq_info = ARQUETIPOS.get(arq, {})
        tactica_info = TACTICA_INFO.get(row["tactica_recomendada"], {})

        # Header
        st.markdown(f"""
        <div class="ficha-header">
            <div style="font-size:24px;font-weight:800;">Sección {sec_sel}</div>
            <div style="font-size:12px;opacity:0.7;margin-top:2px;">
                {AMBITO_LABEL.get(row['ambito_iter'],'')} · {int(row['entrevistas'])} entrevistas
            </div>
            <div style="margin-top:10px;display:flex;align-items:center;gap:12px;">
                <span class="badge badge-{cls.lower()}">{info_zona['emoji']} {info_zona['titulo']}</span>
                <span style="color:white;font-size:22px;font-weight:800;">SPT {row['SPT']:.1f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Táctica
        st.markdown(f"""
        <div class="tactics-box">
            {tactica_info.get('emoji','🎯')} <b>{row['tactica_recomendada']}</b><br>
            <span style="font-weight:400;font-size:12px;">{tactica_info.get('desc','')}</span>
        </div>
        """, unsafe_allow_html=True)

        # Perfil dominante
        arq_color = arq_info.get("color","#ccc")
        st.markdown(f"""
        <div style="background:#f8f9fa;border-radius:8px;padding:10px 14px;
                    border-left:4px solid {arq_color};margin:8px 0;">
            <div style="font-size:11px;color:#777;font-weight:600;text-transform:uppercase;">
                Perfil dominante en esta sección
            </div>
            <div style="font-size:15px;font-weight:700;margin:3px 0;">
                {arq} · {arq_info.get('nombre','')}
            </div>
            <div style="font-size:11px;color:#555;line-height:1.5;">
                {arq_info.get('msg','')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Métricas operativas
        st.markdown("**¿Cómo está el electorado en esta sección?**")
        for key, meta in METRICA_INFO.items():
            val = row[key]
            st.markdown(f"""
            <div style="margin:6px 0;">
                <div class="bar-label">
                    <span>{meta['label']}</span>
                    <span style="font-weight:800;color:{meta['color']};">{val:.1f}%</span>
                </div>
                <div class="bar-bg">
                    <div class="bar-fill" style="width:{val}%;background:{meta['color']};"></div>
                </div>
                <div class="bar-hint">{meta['hint']}</div>
            </div>
            """, unsafe_allow_html=True)

        # Desglose SPT
        with st.expander("Ver cómo se calculó el score SPT"):
            for lbl, val in [
                ("Competitividad electoral (35%)", row["score_electoral_norm"]),
                ("Perfil demográfico (30%)",       row["score_demografico"]),
                ("Disposición hacia JCLY (25%)",   row["score_arquetipos"]),
                ("Cobertura de campo (10%)",        row["score_cobertura"]),
            ]:
                st.markdown(f"""
                <div class="comp-row">
                    <span class="comp-label">{lbl}</span>
                    <span class="comp-val">{val:.1f}</span>
                </div>
                """, unsafe_allow_html=True)

        # Flags
        st.markdown("")
        flags = []
        if row["fuente_arquetipos"] == "encuesta":
            flags.append('<span class="badge badge-encuesta">✅ Datos de encuesta real</span>')
        else:
            flags.append('<span class="badge badge-proyectado">🔄 Perfil estimado por modelo</span>')
        if row["score_electoral_parcial"]:
            flags.append('<span class="badge badge-parcial">⚠️ Historial electoral parcial</span>')
        st.markdown(" ".join(flags), unsafe_allow_html=True)

        # Alertas específicas
        if sec_sel == 2472:
            st.markdown('<div class="alert-box alert-warn">⚠️ La sección más disputada del municipio (margen 1.6 pts en 2024) no tiene encuesta real. Candidata prioritaria para segunda ola.</div>', unsafe_allow_html=True)
        if sec_sel == 2895:
            st.markdown('<div class="alert-box alert-tip">💡 Mayor base sólida del proyecto (26%). Activar estos votantes como brigadistas aunque el score sea bajo.</div>', unsafe_allow_html=True)
        if sec_sel == 2486:
            st.markdown('<div class="alert-box alert-warn">⚠️ Única zona de máxima atención urbana con perfil estimado. Validar presencialmente antes de desplegar recursos completos.</div>', unsafe_allow_html=True)

st.divider()

# ── Panel arquetipos ─────────────────────────────────────────────────
st.markdown('<div class="section-title">¿Quiénes son los votantes de Zacatlán? — Los 9 perfiles</div>', unsafe_allow_html=True)
st.caption("Cada sección tiene una mezcla de estos perfiles. El dominante define la táctica principal.")

tab_urb, tab_rur = st.tabs([
    "🏙️ Perfiles Urbanos — 159 personas (30.5%)",
    "🌾 Perfiles Rurales — 362 personas (69.5%)",
])
for tab, amb in zip([tab_urb, tab_rur], ["Urbano", "Rural"]):
    with tab:
        arqs_tab = {k: v for k, v in ARQUETIPOS.items() if v["ambito"] == amb}
        cols = st.columns(len(arqs_tab))
        for col, (codigo, info) in zip(cols, arqs_tab.items()):
            with col:
                st.markdown(f"""
                <div class="arq-card" style="border-top-color:{info['color']};">
                    <div class="arq-code" style="color:{info['color']};">{codigo}</div>
                    <div class="arq-name">{info['nombre']}</div>
                    <div class="arq-size">{info['n']}</div>
                    <div class="arq-pri" style="color:{info['color']};">{info['prioridad']}</div>
                    <div class="arq-msg">{info['msg']}</div>
                </div>
                """, unsafe_allow_html=True)

st.divider()

# ── Tabla ranking ────────────────────────────────────────────────────
st.markdown('<div class="section-title">Ranking de secciones</div>', unsafe_allow_html=True)

df_tabla = df_f[[
    "seccion","ambito_iter","clasificacion","SPT","tactica_recomendada",
    "pct_no_alcanzados","pct_persuadibles","pct_nucleo_duro",
    "arq_dominante","entrevistas","fuente_arquetipos"
]].sort_values("SPT", ascending=False).copy()

df_tabla.columns = [
    "Sección","Territorio","Prioridad","SPT","Operación",
    "No nos conocen %","Indecisos %","Base sólida %",
    "Perfil dominante","Entrevistas","Fuente"
]
df_tabla["Territorio"] = df_tabla["Territorio"].map({
    "urbano":"🏙️ Urbano","rural_media":"🌾 Rural Media","rural_marginal":"🏔️ Rural Marginal"
})
df_tabla["SPT"] = df_tabla["SPT"].round(1)
for c in ["No nos conocen %","Indecisos %","Base sólida %"]:
    df_tabla[c] = df_tabla[c].round(1)
df_tabla["Fuente"] = df_tabla["Fuente"].map({"encuesta":"✅ Real","proyectado":"🔄 Estimado"})

def color_row(row):
    bg = {"Prioritaria":"#fde8ea","Consolidacion":"#fef3e8","Mantenimiento":"#e8f5f3"}.get(row["Prioridad"],"white")
    return [f"background-color:{bg}"] * len(row)

st.dataframe(
    df_tabla.style.apply(color_row, axis=1),
    use_container_width=True, height=400, hide_index=True,
)

# ── Footer ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#aaa;font-size:11px;'>"
    "Inteligencia Electoral Zacatlán · JCLY Morena 2026 · Documento confidencial"
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("""
<hr style='border:none;border-top:1px solid #e2e8f0;margin:32px 0 16px 0;'>
<div style='text-align:center;color:#94a3b8;font-size:0.75rem;'>
    Inteligencia Electoral Zacatlán · JCLY Morena 2026 · Confidencial
</div>
""", unsafe_allow_html=True)
