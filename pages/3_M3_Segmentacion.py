"""
M3 — Segmentación de Votantes
Inteligencia Electoral Zacatlán · JCLY Morena 2026
Documento Confidencial
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ── CONFIGURACIÓN ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="M3 · Segmentación de Votantes · Zacatlán",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Demo mode — no modificar ────────────────────────────────────────────────
from demo_mode import check_demo_mode
check_demo_mode()


# ── ESTILOS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
  .metric-card {
    background: #F5F5F5;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 8px;
  }
  .metric-card-red   { background: #FDEDEC; border-left: 4px solid #e63946; }
  .metric-card-orange{ background: #FEF9E7; border-left: 4px solid #f4a261; }
  .metric-card-green { background: #EAF6EF; border-left: 4px solid #2a9d8f; }
  .metric-card-gray  { background: #F5F5F5; border-left: 4px solid #adb5bd; }
  .metric-card-dgray { background: #F5F5F5; border-left: 4px solid #6c757d; }
  .section-header {
    background: linear-gradient(135deg, #1a2744, #2563eb);
    color: white;
    padding: 18px 24px;
    border-radius: 10px;
    margin-bottom: 16px;
  }
  .alert-amber {
    background: #FEF9E7;
    border: 1px solid #f4a261;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
  }
  .alert-green {
    background: #EAF6EF;
    border: 1px solid #2a9d8f;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
  }
  .alert-red {
    background: #FDEDEC;
    border: 1px solid #e63946;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
  }
  .perfil-block {
    border-radius: 8px;
    padding: 14px 18px;
    margin: 6px 0;
  }
  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.82em;
    font-weight: 600;
    margin: 2px 3px;
  }
  .badge-red    { background: #e63946; color: white; }
  .badge-orange { background: #f4a261; color: white; }
  .badge-green  { background: #2a9d8f; color: white; }
  .badge-gray   { background: #adb5bd; color: white; }
  .badge-dgray  { background: #6c757d; color: white; }
  hr.divider { border: none; border-top: 1px solid #e0e0e0; margin: 16px 0; }

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

# ── DATOS EMBEBIDOS: ARQUETIPOS ───────────────────────────────────────────────
ARQUETIPOS = {
    "U0": {
        "nombre": "El Indeciso Crítico",
        "ambito": "Urbano",
        "color": "#e63946",
        "card_class": "metric-card-red",
        "badge_class": "badge-red",
        "prioridad": "🔴 Máxima — target de cierre",
        "prioridad_orden": 1,
        "mensaje": "JCLY no es el gobierno actual — es la alternativa real. Sin corrupción.",
        "descripcion": "Conoce a JCLY, está dividido 45/40 a su favor. Sin partido. Necesita el argumento del cambio sin ruptura.",
        "n": 35,
        "pct_municipal": 10.1,
        "conoce_pct": 100.0,
        "eval_positiva_pct": 53.7,
        "votaria_pct": 53.3,
        "nunca_votaria_pct": 36.8,
        "edad_dominante": "30–44 años (51%)",
        "sexo": "Hombre 63% / Mujer 37%",
        "agenda": "Inseguridad 54% · Corrupción 17% · Calles 6%",
        "alerta": None,
    },
    "U1": {
        "nombre": "El Desconectado Urbano",
        "ambito": "Urbano",
        "color": "#f4a261",
        "card_class": "metric-card-orange",
        "badge_class": "badge-orange",
        "prioridad": "🟠 Alta — target de visibilidad",
        "prioridad_orden": 2,
        "mensaje": "Primera impresión: presencia física en colonia. Nombre y cara.",
        "descripcion": "44% no conoce a JCLY. El grupo urbano más grande. Economía estable. Sin urgencia aparente.",
        "n": 91,
        "pct_municipal": 25.7,
        "conoce_pct": 52.6,
        "eval_positiva_pct": 43.8,
        "votaria_pct": 33.1,
        "nunca_votaria_pct": 40.0,
        "edad_dominante": "18–29 años (31%) y 30–44 años (28%)",
        "sexo": "Hombre 47% / Mujer 53%",
        "agenda": "Inseguridad 57% · Agua 12% · Empleo 5%",
        "alerta": None,
    },
    "U2": {
        "nombre": "El Bastión JCLY",
        "ambito": "Urbano",
        "color": "#2a9d8f",
        "card_class": "metric-card-green",
        "badge_class": "badge-green",
        "prioridad": "🟢 Mantener — multiplicadores",
        "prioridad_orden": 3,
        "mensaje": "Activación. Convocatoria. Rol de promotor en su red.",
        "descripcion": "76% evalúa muy bien a JCLY. 76% votaría. Morena 71%. Base sólida urbana.",
        "n": 21,
        "pct_municipal": 6.0,
        "conoce_pct": 100.0,
        "eval_positiva_pct": 91.3,
        "votaria_pct": 76.8,
        "nunca_votaria_pct": 12.3,
        "edad_dominante": "18–29 años (36%) y 30–44 años (29%)",
        "sexo": "Hombre 42% / Mujer 58%",
        "agenda": "Inseguridad 68% · Calles 12%",
        "alerta": "💡 Son brigadistas naturales. Capacitarlos como promotores de red.",
    },
    "U3": {
        "nombre": "El Escéptico Mayor",
        "ambito": "Urbano",
        "color": "#adb5bd",
        "card_class": "metric-card-gray",
        "badge_class": "badge-gray",
        "prioridad": "⬜ Baja — inversión mínima",
        "prioridad_orden": 4,
        "mensaje": "Mensaje de seguridad si hay recursos disponibles.",
        "descripcion": "45–59 años. Alta desconfianza institucional. Agenda: corrupción y seguridad.",
        "n": 12,
        "pct_municipal": 2.8,
        "conoce_pct": 92.3,
        "eval_positiva_pct": 74.5,
        "votaria_pct": 49.0,
        "nunca_votaria_pct": 20.9,
        "edad_dominante": "30–44 años (53%) y 45–59 años (44%)",
        "sexo": "Hombre 50% / Mujer 50%",
        "agenda": "Inseguridad 47% · Corrupción 38% · Calles 5%",
        "alerta": None,
    },
    "R0": {
        "nombre": "El Simpatizante Activo",
        "ambito": "Rural",
        "color": "#f4a261",
        "card_class": "metric-card-orange",
        "badge_class": "badge-orange",
        "prioridad": "🟠 Alta — volumen de la elección",
        "prioridad_orden": 2,
        "mensaje": "El agua, las calles, los servicios que tu comunidad necesita. JCLY lo sabe y lo va a resolver.",
        "descripcion": "100% conoce a JCLY. 55% votaría. Morena 44%. Agenda: agua y servicios.",
        "n": 118,
        "pct_municipal": 17.3,
        "conoce_pct": 100.0,
        "eval_positiva_pct": 87.3,
        "votaria_pct": 53.1,
        "nunca_votaria_pct": 27.8,
        "edad_dominante": "30–44 años (38%) y 45–59 años (31%)",
        "sexo": "Hombre 49% / Mujer 51%",
        "agenda": "Inseguridad 41% · Agua 12% · Empleo 7%",
        "alerta": None,
    },
    "R1": {
        "nombre": "El Campo No Alcanzado",
        "ambito": "Rural",
        "color": "#e63946",
        "card_class": "metric-card-red",
        "badge_class": "badge-red",
        "prioridad": "🔴 Máxima — brigadas urgentes",
        "prioridad_orden": 1,
        "mensaje": "77% no conoce a JCLY. Solo brigadas presenciales lo alcanzan.",
        "descripcion": "77% no conoce a JCLY. El cluster rural más grande. No rechaza — simplemente no sabe quién es.",
        "n": 147,
        "pct_municipal": 24.3,
        "conoce_pct": 7.0,
        "eval_positiva_pct": 7.0,
        "votaria_pct": 12.8,
        "nunca_votaria_pct": 30.3,
        "edad_dominante": "18–29 años (39%) y 30–44 años (28%)",
        "sexo": "Hombre 45% / Mujer 55%",
        "agenda": "Inseguridad 32% · NS/NR 13%",
        "alerta": "⚠️ Una campaña de medios no llega aquí. Solo brigadas presenciales funcionan.",
    },
    "R2": {
        "nombre": "El Núcleo Duro Rural",
        "ambito": "Rural",
        "color": "#2a9d8f",
        "card_class": "metric-card-green",
        "badge_class": "badge-green",
        "prioridad": "🟢 Mantener — brigadistas",
        "prioridad_orden": 3,
        "mensaje": "Son líderes naturales del territorio. Capacitarlos como brigadistas.",
        "descripcion": "87% evalúa muy bien. 93% votaría. Líderes naturales del territorio rural.",
        "n": 32,
        "pct_municipal": 4.6,
        "conoce_pct": 100.0,
        "eval_positiva_pct": 97.6,
        "votaria_pct": 97.8,
        "nunca_votaria_pct": 1.0,
        "edad_dominante": "18–29 años (33%) y 45–59 años (36%)",
        "sexo": "Hombre 69% / Mujer 31%",
        "agenda": "Inseguridad 40% · Empleo 12%",
        "alerta": "💡 Son brigadistas naturales. Capacitarlos como promotores de red.",
    },
    "R3": {
        "nombre": "El Opositor Rural",
        "ambito": "Rural",
        "color": "#6c757d",
        "card_class": "metric-card-dgray",
        "badge_class": "badge-dgray",
        "prioridad": "❌ Descartar — no invertir",
        "prioridad_orden": 5,
        "mensaje": "Rechazo no contagioso. No invertir recursos de persuasión aquí.",
        "descripcion": "69% evaluación negativa. 81% nunca votaría. 45–59 años dominante. Rechazo consolidado.",
        "n": 33,
        "pct_municipal": 4.4,
        "conoce_pct": 98.7,
        "eval_positiva_pct": 24.5,
        "votaria_pct": 0.0,
        "nunca_votaria_pct": 85.9,
        "edad_dominante": "45–59 años (63%)",
        "sexo": "Hombre 34% / Mujer 66%",
        "agenda": "Inseguridad 24% · Agua 19% · Corrupción 10%",
        "alerta": "❌ No destinar recursos de persuasión. Cada peso aquí es un peso que no llega al Campo No Alcanzado.",
    },
    "R4": {
        "nombre": "El Indiferente Rural",
        "ambito": "Rural",
        "color": "#adb5bd",
        "card_class": "metric-card-gray",
        "badge_class": "badge-gray",
        "prioridad": "⬜ Baja — contacto tardío",
        "prioridad_orden": 4,
        "mensaje": "Conoce a JCLY pero 53% sin opinión. Contacto solo si hay recursos sobrantes.",
        "descripcion": "Conoce a JCLY pero 53% sin opinión formada. Indiferencia recuperable, no rechazo.",
        "n": 32,
        "pct_municipal": 4.7,
        "conoce_pct": 98.2,
        "eval_positiva_pct": 32.5,
        "votaria_pct": 16.9,
        "nunca_votaria_pct": 24.4,
        "edad_dominante": "18–29 años (34%) y 30–44 años (32%)",
        "sexo": "Hombre 42% / Mujer 58%",
        "agenda": "Inseguridad 40%",
        "alerta": None,
    },
}

# Datos SPT embebidos
SPT_DATA = [
    {"seccion":2486,"ambito_iter":"urbano","clasificacion":"Prioritaria","arq_dominante":"R1","pct_no_alcanzados":56.9,"pct_persuadibles":38.4,"pct_nucleo_duro":4.7,"pct_no_convertibles":0.0,"fuente_arquetipos":"proyectado","score_electoral_parcial":False,"SPT":71.48},
    {"seccion":2471,"ambito_iter":"rural_marginal","clasificacion":"Prioritaria","arq_dominante":"R1","pct_no_alcanzados":54.6,"pct_persuadibles":25.4,"pct_nucleo_duro":9.1,"pct_no_convertibles":10.8,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":70.99},
    {"seccion":2489,"ambito_iter":"rural_marginal","clasificacion":"Prioritaria","arq_dominante":"R1","pct_no_alcanzados":47.3,"pct_persuadibles":35.6,"pct_nucleo_duro":5.1,"pct_no_convertibles":11.9,"fuente_arquetipos":"proyectado","score_electoral_parcial":False,"SPT":70.80},
    {"seccion":2488,"ambito_iter":"rural_marginal","clasificacion":"Prioritaria","arq_dominante":"R1","pct_no_alcanzados":47.3,"pct_persuadibles":35.6,"pct_nucleo_duro":5.1,"pct_no_convertibles":11.9,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":70.72},
    {"seccion":2483,"ambito_iter":"urbano","clasificacion":"Consolidacion","arq_dominante":"R0","pct_no_alcanzados":35.9,"pct_persuadibles":60.1,"pct_nucleo_duro":0.0,"pct_no_convertibles":4.0,"fuente_arquetipos":"proyectado","score_electoral_parcial":False,"SPT":61.72},
    {"seccion":2896,"ambito_iter":"rural_media","clasificacion":"Consolidacion","arq_dominante":"U1","pct_no_alcanzados":53.5,"pct_persuadibles":16.2,"pct_nucleo_duro":26.8,"pct_no_convertibles":3.5,"fuente_arquetipos":"proyectado","score_electoral_parcial":True,"SPT":57.97},
    {"seccion":2809,"ambito_iter":"rural_media","clasificacion":"Consolidacion","arq_dominante":"R0","pct_no_alcanzados":26.2,"pct_persuadibles":60.7,"pct_nucleo_duro":0.0,"pct_no_convertibles":13.1,"fuente_arquetipos":"encuesta","score_electoral_parcial":True,"SPT":54.67},
    {"seccion":2464,"ambito_iter":"rural_media","clasificacion":"Consolidacion","arq_dominante":"R0","pct_no_alcanzados":27.4,"pct_persuadibles":55.0,"pct_nucleo_duro":3.8,"pct_no_convertibles":13.8,"fuente_arquetipos":"proyectado","score_electoral_parcial":False,"SPT":53.68},
    {"seccion":2473,"ambito_iter":"urbano","clasificacion":"Consolidacion","arq_dominante":"R1","pct_no_alcanzados":56.9,"pct_persuadibles":38.4,"pct_nucleo_duro":4.7,"pct_no_convertibles":0.0,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":51.91},
    {"seccion":2467,"ambito_iter":"urbano","clasificacion":"Consolidacion","arq_dominante":"U1","pct_no_alcanzados":68.4,"pct_persuadibles":15.9,"pct_nucleo_duro":15.7,"pct_no_convertibles":0.0,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":50.88},
    {"seccion":2487,"ambito_iter":"rural_marginal","clasificacion":"Consolidacion","arq_dominante":"R1","pct_no_alcanzados":47.3,"pct_persuadibles":35.6,"pct_nucleo_duro":5.1,"pct_no_convertibles":11.9,"fuente_arquetipos":"proyectado","score_electoral_parcial":False,"SPT":50.50},
    {"seccion":2485,"ambito_iter":"rural_media","clasificacion":"Consolidacion","arq_dominante":"R0","pct_no_alcanzados":27.4,"pct_persuadibles":55.0,"pct_nucleo_duro":3.8,"pct_no_convertibles":13.8,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":49.76},
    {"seccion":2472,"ambito_iter":"rural_marginal","clasificacion":"Consolidacion","arq_dominante":"R1","pct_no_alcanzados":54.6,"pct_persuadibles":25.4,"pct_nucleo_duro":9.1,"pct_no_convertibles":10.8,"fuente_arquetipos":"proyectado","score_electoral_parcial":False,"SPT":49.25},
    {"seccion":2470,"ambito_iter":"urbano","clasificacion":"Consolidacion","arq_dominante":"R1","pct_no_alcanzados":64.9,"pct_persuadibles":29.7,"pct_nucleo_duro":0.0,"pct_no_convertibles":5.4,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":49.06},
    {"seccion":2478,"ambito_iter":"urbano","clasificacion":"Consolidacion","arq_dominante":"R1","pct_no_alcanzados":33.3,"pct_persuadibles":39.0,"pct_nucleo_duro":17.2,"pct_no_convertibles":10.5,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":48.86},
    {"seccion":2475,"ambito_iter":"urbano","clasificacion":"Consolidacion","arq_dominante":"R0","pct_no_alcanzados":35.9,"pct_persuadibles":60.1,"pct_nucleo_duro":0.0,"pct_no_convertibles":4.0,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":48.45},
    {"seccion":2808,"ambito_iter":"rural_media","clasificacion":"Consolidacion","arq_dominante":"U1","pct_no_alcanzados":53.5,"pct_persuadibles":16.2,"pct_nucleo_duro":26.8,"pct_no_convertibles":3.5,"fuente_arquetipos":"proyectado","score_electoral_parcial":True,"SPT":48.07},
    {"seccion":2460,"ambito_iter":"urbano","clasificacion":"Consolidacion","arq_dominante":"U1","pct_no_alcanzados":56.5,"pct_persuadibles":25.5,"pct_nucleo_duro":11.7,"pct_no_convertibles":6.3,"fuente_arquetipos":"proyectado","score_electoral_parcial":False,"SPT":46.42},
    {"seccion":2463,"ambito_iter":"urbano","clasificacion":"Consolidacion","arq_dominante":"U1","pct_no_alcanzados":63.8,"pct_persuadibles":31.3,"pct_nucleo_duro":0.0,"pct_no_convertibles":5.0,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":44.33},
    {"seccion":2484,"ambito_iter":"urbano","clasificacion":"Consolidacion","arq_dominante":"R0","pct_no_alcanzados":33.5,"pct_persuadibles":46.8,"pct_nucleo_duro":9.1,"pct_no_convertibles":10.6,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":42.93},
    {"seccion":2476,"ambito_iter":"rural_media","clasificacion":"Consolidacion","arq_dominante":"U1","pct_no_alcanzados":53.5,"pct_persuadibles":16.2,"pct_nucleo_duro":26.8,"pct_no_convertibles":3.5,"fuente_arquetipos":"proyectado","score_electoral_parcial":False,"SPT":42.93},
    {"seccion":2727,"ambito_iter":"rural_media","clasificacion":"Consolidacion","arq_dominante":"U1","pct_no_alcanzados":53.5,"pct_persuadibles":16.2,"pct_nucleo_duro":26.8,"pct_no_convertibles":3.5,"fuente_arquetipos":"encuesta","score_electoral_parcial":True,"SPT":42.52},
    {"seccion":2481,"ambito_iter":"urbano","clasificacion":"Consolidacion","arq_dominante":"U1","pct_no_alcanzados":55.7,"pct_persuadibles":24.0,"pct_nucleo_duro":3.7,"pct_no_convertibles":16.6,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":42.15},
    {"seccion":2480,"ambito_iter":"urbano","clasificacion":"Consolidacion","arq_dominante":"R0","pct_no_alcanzados":36.1,"pct_persuadibles":42.1,"pct_nucleo_duro":15.7,"pct_no_convertibles":6.0,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":42.06},
    {"seccion":2466,"ambito_iter":"rural_media","clasificacion":"Consolidacion","arq_dominante":"R0","pct_no_alcanzados":27.4,"pct_persuadibles":55.0,"pct_nucleo_duro":3.8,"pct_no_convertibles":13.8,"fuente_arquetipos":"proyectado","score_electoral_parcial":False,"SPT":41.96},
    {"seccion":2474,"ambito_iter":"urbano","clasificacion":"Consolidacion","arq_dominante":"R1","pct_no_alcanzados":46.9,"pct_persuadibles":45.0,"pct_nucleo_duro":4.1,"pct_no_convertibles":4.1,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":41.66},
    {"seccion":2465,"ambito_iter":"urbano","clasificacion":"Consolidacion","arq_dominante":"U1","pct_no_alcanzados":56.5,"pct_persuadibles":25.5,"pct_nucleo_duro":11.7,"pct_no_convertibles":6.3,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":41.42},
    {"seccion":2895,"ambito_iter":"rural_media","clasificacion":"Mantenimiento","arq_dominante":"R0","pct_no_alcanzados":25.8,"pct_persuadibles":35.4,"pct_nucleo_duro":26.0,"pct_no_convertibles":12.8,"fuente_arquetipos":"encuesta","score_electoral_parcial":True,"SPT":37.42},
    {"seccion":2477,"ambito_iter":"rural_media","clasificacion":"Mantenimiento","arq_dominante":"R0","pct_no_alcanzados":27.4,"pct_persuadibles":55.0,"pct_nucleo_duro":3.8,"pct_no_convertibles":13.8,"fuente_arquetipos":"proyectado","score_electoral_parcial":False,"SPT":36.75},
    {"seccion":2482,"ambito_iter":"urbano","clasificacion":"Mantenimiento","arq_dominante":"R1","pct_no_alcanzados":48.3,"pct_persuadibles":25.9,"pct_nucleo_duro":13.8,"pct_no_convertibles":12.0,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":34.62},
    {"seccion":2461,"ambito_iter":"urbano","clasificacion":"Mantenimiento","arq_dominante":"U1","pct_no_alcanzados":49.9,"pct_persuadibles":20.5,"pct_nucleo_duro":19.3,"pct_no_convertibles":10.3,"fuente_arquetipos":"encuesta","score_electoral_parcial":False,"SPT":33.96},
    {"seccion":2469,"ambito_iter":"rural_media","clasificacion":"Mantenimiento","arq_dominante":"R0","pct_no_alcanzados":27.4,"pct_persuadibles":55.0,"pct_nucleo_duro":3.8,"pct_no_convertibles":13.8,"fuente_arquetipos":"proyectado","score_electoral_parcial":False,"SPT":32.37},
    {"seccion":2462,"ambito_iter":"urbano","clasificacion":"Mantenimiento","arq_dominante":"U1","pct_no_alcanzados":49.9,"pct_persuadibles":20.5,"pct_nucleo_duro":19.3,"pct_no_convertibles":10.3,"fuente_arquetipos":"proyectado","score_electoral_parcial":False,"SPT":30.74},
]

ZONA_LABELS = {
    "Prioritaria":   "🔴 Zona de máxima atención",
    "Consolidacion": "🟡 Zona de trabajo activo",
    "Mantenimiento": "🟢 Zona de base sólida",
}
AMBITO_LABELS = {
    "urbano":          "🏙️ Urbano",
    "rural_media":     "🌾 Rural Media",
    "rural_marginal":  "🏔️ Rural Marginal",
}
FUENTE_LABELS = {
    "encuesta":   "✅ Datos de encuesta real",
    "proyectado": "🔄 Perfil estimado por modelo",
}

ARQ_ORDER = ["R1","U1","R0","U0","R2","U2","R4","U3","R3"]

# ── CARGA DE DATOS ────────────────────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir   = os.path.join(script_dir, "..", "data")
    candidatos = [
        os.path.join(data_dir,   "clusters_total.csv"),
        os.path.join(script_dir, "clusters_total.csv"),
        os.path.join(script_dir, "data", "clusters_total.csv"),
        os.path.join(script_dir, "processed", "clusters_total.csv"),
        os.path.join(os.path.expanduser("~"), "Inteligencia_Zacatlan", "processed", "clusters_total.csv"),
        "clusters_total.csv",
    ]
    for ruta in candidatos:
        if os.path.exists(ruta):
            df = pd.read_csv(ruta)
            requeridas = {"seccion", "cluster_nombre", "factor_final"}
            if not requeridas.issubset(set(df.columns)):
                faltantes = requeridas - set(df.columns)
                raise ValueError(f"clusters_total.csv falta columnas: {faltantes}")
            return df, pd.DataFrame(SPT_DATA), True
    return pd.DataFrame(columns=["seccion","cluster_nombre","factor_final"]), pd.DataFrame(SPT_DATA), False

try:
    df, spt, datos_ok = cargar_datos()
except Exception as e:
    st.error(f"⚠️ Error al cargar clusters_total.csv: {e}")
    df = pd.DataFrame(columns=["seccion","cluster_nombre","factor_final"])
    spt = pd.DataFrame(SPT_DATA)
    datos_ok = False

secciones_disponibles = sorted(df["seccion"].unique().tolist()) if datos_ok and len(df) > 0 else []

# ── HELPERS ───────────────────────────────────────────────────────────────────
def get_arq_code(nombre_completo):
    """Extrae el código (ej. 'R1') del nombre completo del cluster."""
    for code in ARQUETIPOS:
        if code in nombre_completo:
            return code
    return nombre_completo[:2]

def barra_html(pct, color, label, instruccion):
    return f"""
    <div style="margin:8px 0;">
      <div style="display:flex; justify-content:space-between; margin-bottom:3px;">
        <span style="font-weight:600; font-size:0.9em;">{label}</span>
        <span style="font-weight:700; color:{color}; font-size:0.95em;">{pct:.1f}%</span>
      </div>
      <div style="background:#eee; border-radius:4px; height:10px; margin-bottom:3px;">
        <div style="background:{color}; width:{min(pct,100)}%; height:10px; border-radius:4px;"></div>
      </div>
      <div style="font-size:0.78em; color:#555;">→ {instruccion}</div>
    </div>"""

def metrica_html(valor, label, sub="", color="#1a1a2e"):
    return f"""
    <div style="text-align:center; padding:12px 8px;">
      <div style="font-size:1.8em; font-weight:800; color:{color};">{valor}</div>
      <div style="font-size:0.85em; font-weight:600; color:#333;">{label}</div>
      {f'<div style="font-size:0.75em; color:#666;">{sub}</div>' if sub else ''}
    </div>"""

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 👥 Segmentación de Votantes")
    st.markdown("*¿Con quién hablar primero y qué decirle?*")
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    st.markdown("**¿Qué tipo de territorio?**")
    filtro_ambito = st.multiselect(
        label="Tipo de territorio",
        options=["🏙️ Urbano", "🌾 Rural Media", "🏔️ Rural Marginal"],
        default=["🏙️ Urbano", "🌾 Rural Media", "🏔️ Rural Marginal"],
        label_visibility="collapsed"
    )

    st.markdown("**¿Qué perfil de votante?**")
    todas_prioridades = ["🔴 Máxima prioridad", "🟠 Alta prioridad", "🟢 Mantener", "⬜ Baja prioridad", "❌ Descartar"]
    filtro_prioridad = st.multiselect(
        label="Prioridad",
        options=todas_prioridades,
        default=todas_prioridades,
        label_visibility="collapsed"
    )

    st.markdown("**¿Qué sección quieres explorar?**")
    # El selector se actualiza dinámicamente según el filtro de territorio
    # Usamos una clave única para forzar el re-render cuando cambia el filtro
    _opciones_seccion = ["— Municipio completo —"] + [
        str(s["seccion"]) for s in SPT_DATA
        if s["ambito_iter"] in set(v for a in filtro_ambito for v in {
            "🏙️ Urbano": ["urbano"],
            "🌾 Rural Media": ["rural_media"],
            "🏔️ Rural Marginal": ["rural_marginal"],
        }.get(a, []))
    ]
    seccion_sel = st.selectbox(
        label="Sección",
        options=_opciones_seccion,
        label_visibility="collapsed"
    )

    with st.expander("ℹ️ ¿Cómo funciona esto?"):
        st.markdown("""
        **M3 muestra quiénes son los votantes de Zacatlán.**

        Los **9 perfiles** se construyeron con 521 entrevistas cara a cara
        usando técnicas de agrupamiento estadístico.

        Cada perfil tiene un nombre, un tamaño y un mensaje específico.
        Los colores indican la prioridad de inversión de recursos.

        *Fuente: Encuesta 1 · 6–10 feb 2026 · factor_final como peso.*
        """)

# ── FILTRADO ──────────────────────────────────────────────────────────────────
# Mapeo: etiqueta del filtro → ambito_iter en SPT_DATA y ambito_modelo en clusters
AMBITO_ITER_MAP = {
    "🏙️ Urbano":         ["urbano"],
    "🌾 Rural Media":    ["rural_media"],
    "🏔️ Rural Marginal": ["rural_marginal"],
}
AMBITO_MODELO_MAP = {
    "🏙️ Urbano":         ["Urbano"],
    "🌾 Rural Media":    ["Rural"],
    "🏔️ Rural Marginal": ["Rural"],
}
PRIORIDAD_ORDEN_MAP = {
    "🔴 Máxima prioridad": 1,
    "🟠 Alta prioridad": 2,
    "🟢 Mantener": 3,
    "⬜ Baja prioridad": 4,
    "❌ Descartar": 5,
}

# Conjuntos derivados de los filtros
ambitos_iter_sel   = set(v for a in filtro_ambito for v in AMBITO_ITER_MAP[a])
ambitos_modelo_sel = set(v for a in filtro_ambito for v in AMBITO_MODELO_MAP[a])
prioridades_sel    = set(PRIORIDAD_ORDEN_MAP[p] for p in filtro_prioridad)

# Secciones que pasan el filtro de territorio (basado en SPT_DATA)
secciones_filtradas = [
    s["seccion"] for s in SPT_DATA
    if s["ambito_iter"] in ambitos_iter_sel
]

# Actualizar el selector de sección para mostrar solo secciones del territorio seleccionado
# (el selectbox ya se creó en el sidebar, pero filtramos su efecto abajo)

# Arquetipos que pasan el filtro de perfil (para las fichas en tabs)
arq_visibles = {
    code: arq for code, arq in ARQUETIPOS.items()
    if arq["prioridad_orden"] in prioridades_sel
}

# DataFrame filtrado por territorio (para la gráfica municipal)
df_filtrado = df[df["seccion"].isin(secciones_filtradas)] if datos_ok and len(secciones_filtradas) > 0 else df

# ── CUERPO PRINCIPAL ──────────────────────────────────────────────────────────
st.markdown("""
<div class="section-header">
  <h2 style="margin:0; color:white;">👥 M3 · Segmentación de Votantes</h2>
  <p style="margin:4px 0 0 0; color:#ccc; font-size:0.9em;">
    9 perfiles del electorado zacatleco · Con quién hablar y qué decirle
  </p>
</div>
""", unsafe_allow_html=True)

# ── MODO: SECCIÓN ESPECÍFICA vs MUNICIPAL ─────────────────────────────────────
modo_seccion = seccion_sel != "— Municipio completo —" and datos_ok

if modo_seccion:
    # ── VISTA DE SECCIÓN ──────────────────────────────────────────────────────
    seccion_num = int(seccion_sel)
    df_sec = df[df["seccion"] == seccion_num].copy()
    spt_sec = next((s for s in SPT_DATA if s["seccion"] == seccion_num), None)

    # Header de sección
    if spt_sec:
        zona_label  = ZONA_LABELS.get(spt_sec["clasificacion"], spt_sec["clasificacion"])
        ambito_label = AMBITO_LABELS.get(spt_sec["ambito_iter"], spt_sec["ambito_iter"])
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a2744,#2563eb); color:white;
                    border-radius:10px; padding:16px 24px; margin-bottom:14px;
                    display:flex; gap:16px; flex-wrap:wrap; align-items:center;">
          <span style="font-size:1.5em; font-weight:800;">📍 Sección {seccion_num}</span>
          <span style="background:#ffffff22; padding:4px 12px; border-radius:12px; font-size:0.85em;">{ambito_label}</span>
          <span style="background:#ffffff22; padding:4px 12px; border-radius:12px; font-size:0.85em;">{zona_label}</span>
          <span style="background:#ffffff22; padding:4px 12px; border-radius:12px; font-size:0.85em; margin-left:auto;">SPT {spt_sec['SPT']:.1f}</span>
        </div>
        """, unsafe_allow_html=True)

        # Alertas de calidad de datos
        if spt_sec["fuente_arquetipos"] == "proyectado":
            st.markdown("""<div class='alert-amber'>
            ⚠️ <b>Perfil estimado por modelo</b> — No hay encuesta real en esta sección.
            Validar presencialmente antes de desplegar recursos.
            </div>""", unsafe_allow_html=True)
        if spt_sec["score_electoral_parcial"]:
            st.markdown("""<div class='alert-amber'>
            ⚠️ <b>Historial electoral parcial</b> — Solo tenemos datos de 2024 en esta sección.
            </div>""", unsafe_allow_html=True)
        if seccion_num == 2472:
            st.markdown("""<div class='alert-red'>
            🔴 <b>Sección más vulnerable del proyecto</b> — Margen de 1.6 pts en 2024.
            Candidata prioritaria para segunda ola de encuesta.
            </div>""", unsafe_allow_html=True)
        if seccion_num == 2895:
            st.markdown("""<div class='alert-green'>
            💡 <b>Mayor núcleo duro del proyecto (26%)</b> — Sus votantes son brigadistas naturales.
            Activarlos como promotores aunque la sección sea de Mantenimiento.
            </div>""", unsafe_allow_html=True)
        if seccion_num == 2486:
            st.markdown("""<div class='alert-amber'>
            ⚠️ <b>Única Prioritaria urbana con perfil estimado (KNN)</b> — Requiere validación
            presencial antes de desplegar recursos máximos.
            </div>""", unsafe_allow_html=True)

    # Tarjetas de resumen de la sección
    if spt_sec:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label="🔴 No nos conocen",
                value=f"{spt_sec['pct_no_alcanzados']:.1f}%",
                help="R1 + U1 · Enviar brigadas de primer contacto"
            )
        with col2:
            st.metric(
                label="🟠 Nos conocen pero no han decidido",
                value=f"{spt_sec['pct_persuadibles']:.1f}%",
                help="R0 + U0 + R4 · Trabajo de activación y cierre"
            )
        with col3:
            st.metric(
                label="🟢 Ya votan con nosotros",
                value=f"{spt_sec['pct_nucleo_duro']:.1f}%",
                help="R2 + U2 · Convertirlos en multiplicadores"
            )
        with col4:
            st.metric(
                label="⬜ No los vamos a convencer",
                value=f"{spt_sec['pct_no_convertibles']:.1f}%",
                help="R3 + U3 · No invertir recursos aquí"
            )
    else:
        st.info("Esta sección no tiene datos SPT disponibles. Se muestra la composición de perfiles.")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Gráfica comparativa sección vs municipio
    comp_sec = df_sec.groupby("cluster_nombre")["factor_final"].sum()
    comp_sec_pct = (comp_sec / comp_sec.sum() * 100).reset_index()
    comp_sec_pct.columns = ["cluster_nombre", "pct_local"]
    comp_sec_pct["codigo"]        = comp_sec_pct["cluster_nombre"].apply(get_arq_code)
    comp_sec_pct["nombre_display"] = comp_sec_pct["codigo"].apply(
        lambda c: f"{c} · {ARQUETIPOS.get(c,{}).get('nombre', c)}")
    comp_sec_pct["color"]          = comp_sec_pct["codigo"].apply(
        lambda c: ARQUETIPOS.get(c,{}).get("color", "#aaa"))
    comp_sec_pct["pct_municipal"]  = comp_sec_pct["codigo"].apply(
        lambda c: ARQUETIPOS.get(c,{}).get("pct_municipal", 0))
    comp_sec_pct = comp_sec_pct.sort_values("pct_local", ascending=True)

    col_graf, col_ficha = st.columns([1, 1])

    with col_graf:
        st.markdown("**¿Quiénes viven en esta sección? — vs promedio municipal**")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=comp_sec_pct["nombre_display"],
            x=comp_sec_pct["pct_local"],
            name="Esta sección",
            orientation="h",
            marker_color=comp_sec_pct["color"].tolist(),
            text=comp_sec_pct["pct_local"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside",
        ))
        fig.add_trace(go.Bar(
            y=comp_sec_pct["nombre_display"],
            x=comp_sec_pct["pct_municipal"],
            name="Promedio municipal",
            orientation="h",
            marker_color="rgba(0,0,0,0.12)",
            text=comp_sec_pct["pct_municipal"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside",
        ))
        fig.update_layout(
            barmode="group",
            height=380,
            margin=dict(l=10, r=70, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis_title="% del electorado",
            yaxis_title="",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(size=11),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_ficha:
        arq_dom_code = spt_sec["arq_dominante"] if spt_sec else comp_sec_pct.iloc[-1]["codigo"]
        arq_dom = ARQUETIPOS.get(arq_dom_code, {})
        st.markdown("**Perfil dominante en esta sección**")
        color_dom = arq_dom.get("color", "#aaa")
        st.markdown(f"""
        <div class="perfil-block" style="background:{color_dom}18;
             border-left:4px solid {color_dom}; margin-bottom:10px;">
          <div style="font-weight:800; font-size:1.05em;">
            {arq_dom_code} · {arq_dom.get('nombre','')}
          </div>
          <div style="font-size:0.88em; color:#444; margin:6px 0;">
            {arq_dom.get('descripcion','')}
          </div>
          <div style="background:white; border-radius:6px; padding:8px 12px;
               border-left:3px solid {color_dom}; margin-top:8px;
               font-style:italic; font-size:0.88em;">
            💬 {arq_dom.get('mensaje','')}
          </div>
        </div>
        """, unsafe_allow_html=True)
        if arq_dom.get("alerta"):
            tipo_a = "alert-green" if "💡" in arq_dom["alerta"] else "alert-red"
            st.markdown(f"<div class='{tipo_a}'>{arq_dom['alerta']}</div>",
                        unsafe_allow_html=True)

        st.markdown("<br>**Barras operativas**", unsafe_allow_html=True)
        if spt_sec:
            st.markdown(barra_html(spt_sec["pct_no_alcanzados"], "#e63946",
                "No nos conocen", "Enviar brigadas de primer contacto"), unsafe_allow_html=True)
            st.markdown(barra_html(spt_sec["pct_persuadibles"], "#f4a261",
                "Nos conocen pero no han decidido", "Trabajo de activación y cierre"), unsafe_allow_html=True)
            st.markdown(barra_html(spt_sec["pct_nucleo_duro"], "#2a9d8f",
                "Ya votan con nosotros", "Convertirlos en multiplicadores"), unsafe_allow_html=True)
            st.markdown(barra_html(spt_sec["pct_no_convertibles"], "#6c757d",
                "No los vamos a convencer", "No invertir recursos aquí"), unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

else:
    # ── VISTA MUNICIPAL ───────────────────────────────────────────────────────

    # Tarjetas de resumen municipal
    col1, col2, col3, col4 = st.columns(4)
    pct_brigadas  = ARQUETIPOS['R1']['pct_municipal'] + ARQUETIPOS['U1']['pct_municipal']
    pct_activar   = ARQUETIPOS['R0']['pct_municipal'] + ARQUETIPOS['U0']['pct_municipal']
    pct_duro      = ARQUETIPOS['R2']['pct_municipal'] + ARQUETIPOS['U2']['pct_municipal']
    pct_descartar = ARQUETIPOS['R3']['pct_municipal'] + ARQUETIPOS['U3']['pct_municipal']
    with col1:
        st.metric(label="🔴 Requieren brigadas urgentes",
                  value=f"{pct_brigadas:.0f}%",
                  help="R1 + U1 · No nos conocen")
    with col2:
        st.metric(label="🟠 Listos para activación y cierre",
                  value=f"{pct_activar:.0f}%",
                  help="R0 + U0 · Conocen a JCLY, aún indecisos")
    with col3:
        st.metric(label="🟢 Ya votan con nosotros",
                  value=f"{pct_duro:.0f}%",
                  help="R2 + U2 · Núcleo duro")
    with col4:
        st.metric(label="⬜ No los vamos a convencer",
                  value=f"{pct_descartar:.0f}%",
                  help="R3 + U3 · No invertir recursos aquí")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Visualización municipal: dos gráficas lado a lado
    # Recalcular pesos con df_filtrado para que reaccione al filtro de territorio
    if datos_ok and len(df_filtrado) > 0:
        _tot = df_filtrado["factor_final"].sum()
        _pesos_filtrados = {}
        for code in ARQUETIPOS:
            _sub = df_filtrado[df_filtrado["cluster_nombre"].str.contains(code, regex=False)]
            _pesos_filtrados[code] = (_sub["factor_final"].sum() / _tot * 100) if _tot > 0 else 0.0
    else:
        _pesos_filtrados = {code: ARQUETIPOS[code]["pct_municipal"] for code in ARQUETIPOS}

    titulo_territorio = " · ".join(filtro_ambito) if filtro_ambito else "Municipio completo"
    st.markdown(f"### 📊 ¿Cómo está distribuido el electorado? — {titulo_territorio}")
    col_izq, col_der = st.columns([1, 1])

    with col_izq:
        st.markdown("**Peso de cada perfil**")
        arq_orden_graf = ["R1","U1","R0","U0","R2","U2","R4","U3","R3"]
        # Filtrar arquetipos que corresponden al territorio seleccionado
        arq_graf = [c for c in arq_orden_graf if _pesos_filtrados.get(c, 0) > 0]
        nombres = [f"{c} · {ARQUETIPOS[c]['nombre']}" for c in arq_graf]
        valores = [_pesos_filtrados[c] for c in arq_graf]
        colores = [ARQUETIPOS[c]['color'] for c in arq_graf]

        fig_mun = go.Figure(go.Bar(
            x=valores,
            y=nombres,
            orientation="h",
            marker_color=colores,
            text=[f"{v:.1f}%" for v in valores],
            textposition="outside",
        ))
        fig_mun.update_layout(
            height=360,
            margin=dict(l=10, r=60, t=10, b=10),
            xaxis=dict(title="% del municipio", range=[0, max(valores)*1.3]),
            yaxis=dict(autorange="reversed"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False,
            font=dict(size=11),
        )
        st.plotly_chart(fig_mun, use_container_width=True)

    with col_der:
        # Donut: distribución por grupo estratégico
        st.markdown("**Grupos estratégicos**")
        grupos = {
            "🔴 Brigadas urgentes<br>(R1+U1)":  (_pesos_filtrados['R1'] + _pesos_filtrados['U1'], "#e63946"),
            "🟠 Activación y cierre<br>(R0+U0)": (_pesos_filtrados['R0'] + _pesos_filtrados['U0'], "#f4a261"),
            "🟢 Núcleo duro<br>(R2+U2)":         (_pesos_filtrados['R2'] + _pesos_filtrados['U2'], "#2a9d8f"),
            "⬜ Baja prioridad<br>(R4)":          (_pesos_filtrados['R4'], "#adb5bd"),
            "❌ Descartar<br>(R3+U3)":            (_pesos_filtrados['R3'] + _pesos_filtrados['U3'], "#6c757d"),
        }
        # Filtrar grupos con valor 0 (territorio sin ese perfil)
        grupos = {k: v for k, v in grupos.items() if v[0] > 0}
        g_labels = list(grupos.keys())
        g_values = [v[0] for v in grupos.values()]
        g_colors = [v[1] for v in grupos.values()]

        fig_donut = go.Figure(go.Pie(
            labels=g_labels,
            values=g_values,
            marker_colors=g_colors,
            hole=0.55,
            textinfo="percent",
            textfont_size=13,
            hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
        ))
        fig_donut.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(orientation="v", font=dict(size=10)),
            paper_bgcolor="white",
        )
        fig_donut.add_annotation(
            text="521<br>entrevistas",
            x=0.5, y=0.5,
            font=dict(size=13, color="#1a1a2e"),
            showarrow=False,
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    st.caption("Selecciona una sección en el sidebar izquierdo para ver el desglose de esa sección específica.")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ── FICHAS DE ARQUETIPOS ───────────────────────────────────────────────────────
tab_urbano, tab_rural = st.tabs(["🏙️ Perfiles Urbanos (4)", "🌾 Perfiles Rurales (5)"])

def render_ficha_arquetipo(code, arq, df_data=None):
    """Renderiza la ficha completa de un arquetipo."""
    color = arq["color"]

    # Header
    st.markdown(f"""
    <div style="background:{color}18; border-left:5px solid {color};
         border-radius:8px; padding:14px 18px; margin-bottom:10px;">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
        <div>
          <span style="font-size:1.1em; font-weight:800; color:{color};">{code}</span>
          <span style="font-size:1.1em; font-weight:700; margin-left:8px;">{arq['nombre']}</span>
        </div>
        <div>
          <span style="font-size:0.82em; font-weight:600; background:{color}; color:white;
               padding:3px 10px; border-radius:10px;">{arq['prioridad']}</span>
        </div>
      </div>
      <div style="font-size:0.88em; color:#444; margin-top:8px;">{arq['descripcion']}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])

    with c1:
        # Mensaje de activación
        st.markdown(f"""
        <div style="background:white; border:1px solid {color}; border-radius:8px;
             padding:12px 14px; margin-bottom:10px;">
          <div style="font-size:0.8em; font-weight:700; color:{color}; margin-bottom:6px;">
            💬 MENSAJE DE ACTIVACIÓN
          </div>
          <div style="font-style:italic; font-size:0.9em; color:#222;">
            "{arq['mensaje']}"
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Métricas clave
        st.markdown(f"""
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:10px;">
          <div style="background:#F5F5F5; border-radius:6px; padding:10px; text-align:center;">
            <div style="font-size:1.4em; font-weight:800; color:#1a1a2e;">{arq['n']}</div>
            <div style="font-size:0.75em; color:#555;">entrevistados</div>
          </div>
          <div style="background:#F5F5F5; border-radius:6px; padding:10px; text-align:center;">
            <div style="font-size:1.4em; font-weight:800; color:{color};">{arq['pct_municipal']}%</div>
            <div style="font-size:0.75em; color:#555;">del municipio</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Perfil demográfico
        st.markdown(f"""
        <div style="background:#EBF0FB; border-radius:6px; padding:10px 14px; margin-bottom:6px; font-size:0.85em;">
          <b>Edad predominante:</b> {arq['edad_dominante']}<br>
          <b>Sexo:</b> {arq['sexo']}<br>
          <b>Agenda principal:</b> {arq['agenda']}
        </div>
        """, unsafe_allow_html=True)

    with c2:
        # Métricas JCLY
        metricas = [
            ("Conoce a JCLY", arq["conoce_pct"], color),
            ("Evaluación positiva", arq["eval_positiva_pct"], "#2a9d8f"),
            ("Ya votaría por JCLY", arq["votaria_pct"], "#2a9d8f"),
            ("Nunca votaría", arq["nunca_votaria_pct"], "#e63946"),
        ]
        for label, val, col_bar in metricas:
            st.markdown(f"""
            <div style="margin:7px 0;">
              <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                <span style="font-size:0.82em; color:#444;">{label}</span>
                <span style="font-weight:700; font-size:0.88em; color:{col_bar};">{val:.0f}%</span>
              </div>
              <div style="background:#eee; border-radius:4px; height:8px;">
                <div style="background:{col_bar}; width:{min(val,100)}%; height:8px; border-radius:4px;"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Alerta si existe
        if arq.get("alerta"):
            tipo_alerta = "alert-green" if "💡" in arq["alerta"] else "alert-red" if "❌" in arq["alerta"] else "alert-amber"
            st.markdown(f"<div class='{tipo_alerta}' style='margin-top:10px;'>{arq['alerta']}</div>",
                        unsafe_allow_html=True)

    # Distribución geográfica (si hay datos)
    if df_data is not None:
        arq_df = df_data[df_data["cluster_nombre"].str.contains(code)]
        if len(arq_df) > 0:
            dist = arq_df.groupby("seccion")["factor_final"].sum()
            dist_pct = (dist / dist.sum() * 100).sort_values(ascending=False)
            top_secs = dist_pct.head(5)

            with st.expander("📍 ¿Dónde está concentrado este perfil?"):
                fig_sec = go.Figure(go.Bar(
                    x=[str(s) for s in top_secs.index],
                    y=top_secs.values,
                    marker_color=color,
                    text=[f"{v:.1f}%" for v in top_secs.values],
                    textposition="outside",
                ))
                fig_sec.update_layout(
                    height=200,
                    margin=dict(l=5, r=5, t=5, b=30),
                    xaxis_title="Sección",
                    yaxis_title="% de este perfil",
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    showlegend=False,
                    yaxis=dict(range=[0, top_secs.values[0]*1.3]),
                )
                st.plotly_chart(fig_sec, use_container_width=True)
                st.caption("Top 5 secciones con mayor concentración de este perfil (% del total de este arquetipo en el municipio).")


# Urbano — muestra siempre los 4 perfiles urbanos
with tab_urbano:
    urbanos_filtrados = [c for c in ["U0","U1","U2","U3"] if c in arq_visibles]
    if not urbanos_filtrados:
        st.info("No hay perfiles urbanos que coincidan con los filtros seleccionados.")
    for i in range(0, len(urbanos_filtrados), 2):
        par = urbanos_filtrados[i:i+2]
        cols = st.columns(len(par))
        for j, code in enumerate(par):
            with cols[j]:
                render_ficha_arquetipo(code, ARQUETIPOS[code], df_filtrado if datos_ok else None)
                st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# Rural
with tab_rural:
    rurales_filtrados = [c for c in ["R1","R0","R2","R4","R3"] if c in arq_visibles]
    if not rurales_filtrados:
        st.info("No hay perfiles rurales que coincidan con los filtros seleccionados.")
    for i in range(0, len(rurales_filtrados), 2):
        par = rurales_filtrados[i:i+2]
        cols = st.columns(len(par))
        for j, code in enumerate(par):
            with cols[j]:
                render_ficha_arquetipo(code, ARQUETIPOS[code], df_filtrado if datos_ok else None)
                st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── TABLA COMPLETA ────────────────────────────────────────────────────────────
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
with st.expander("📋 Tabla completa de perfiles — ordenada por prioridad"):
    filas = []
    for code in ARQ_ORDER:
        arq = ARQUETIPOS[code]
        filas.append({
            "Perfil": f"{code} · {arq['nombre']}",
            "Ámbito": arq["ambito"],
            "Prioridad": arq["prioridad"],
            "% del municipio": f"{arq['pct_municipal']}%",
            "Conoce a JCLY": f"{arq['conoce_pct']:.0f}%",
            "Evaluación positiva": f"{arq['eval_positiva_pct']:.0f}%",
            "Ya votaría": f"{arq['votaria_pct']:.0f}%",
            "Nunca votaría": f"{arq['nunca_votaria_pct']:.0f}%",
            "Mensaje clave": arq["mensaje"],
        })
    st.dataframe(
        pd.DataFrame(filas),
        use_container_width=True,
        hide_index=True,
    )

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#94a3b8; font-size:0.75rem; margin-top:24px; padding-top:12px;
     border-top:1px solid #e2e8f0;">
    Inteligencia Electoral Zacatlán · JCLY Morena 2026 · Confidencial
</div>
""", unsafe_allow_html=True)
