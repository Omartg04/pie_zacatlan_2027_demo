"""
Home.py — Inteligencia Electoral Zacatlán
Sistema de Inteligencia · Juan Carlos Lastiri Yamal · Morena 2026
Sprint 4 · Marzo 2026
"""

import streamlit as st
import pandas as pd
import os

# ── Rutas relativas ───────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

# ── CSS global — se inyecta una sola vez, fuera de main() ────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Header ── */
.home-header {
    background: linear-gradient(135deg, #004a6e 0%, #007cab 60%, #00c0ff 100%);
    border-radius: 16px;
    padding: 36px 40px 28px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.home-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 240px; height: 240px;
    border-radius: 50%;
    background: rgba(255,255,255,0.04);
}
.home-header::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 40%;
    width: 180px; height: 180px;
    border-radius: 50%;
    background: rgba(255,255,255,0.03);
}
.header-tag {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    color: #00c0ff;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.header-title {
    font-size: 2.0rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
    margin-bottom: 6px;
}
.header-sub {
    font-size: 1.0rem;
    color: #bfdbfe;
    margin-bottom: 16px;
}
.header-corte {
    display: inline-block;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    color: #e0f2fe;
    font-weight: 500;
}

/* ── Sección títulos ── */
.section-title {
    font-size: 1.0rem;
    font-weight: 700;
    color: #1e293b;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 8px;
    margin-top: 36px;
    margin-bottom: 18px;
}

/* ── Cards principales ── */
.journey-card {
    border-radius: 16px;
    padding: 28px 26px 24px;
    min-height: 260px;
    position: relative;
    overflow: hidden;
    color: #ffffff;
}
.journey-card.card-1 {
    background:
        radial-gradient(circle at 85% 15%, rgba(96,165,250,0.20) 0%, transparent 55%),
        linear-gradient(145deg, #004a6e 0%, #005f8a 100%);
}
.journey-card.card-2 {
    background:
        radial-gradient(circle at 85% 15%, rgba(52,211,153,0.18) 0%, transparent 55%),
        linear-gradient(145deg, #064e3b 0%, #065f46 100%);
}
.journey-card.card-3 {
    background:
        radial-gradient(circle at 85% 15%, rgba(167,139,250,0.20) 0%, transparent 55%),
        linear-gradient(145deg, #2e1065 0%, #4c1d95 100%);
}
.journey-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: repeating-linear-gradient(
        -45deg,
        rgba(255,255,255,0.028) 0px,
        rgba(255,255,255,0.028) 1px,
        transparent 1px,
        transparent 18px
    );
    pointer-events: none;
}
.journey-card::after {
    content: '';
    position: absolute;
    top: -45px; right: -45px;
    width: 150px; height: 150px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
    pointer-events: none;
}
.card-concept {
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 14px;
    opacity: 0.70;
    color: #ffffff;
    position: relative;
    z-index: 1;
}
.card-icon-bg {
    font-size: 2.6rem;
    margin-bottom: 10px;
    display: block;
    position: relative;
    z-index: 1;
}
.card-title {
    font-size: 1.28rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 10px;
    line-height: 1.25;
    position: relative;
    z-index: 1;
}
.card-body {
    font-size: 0.86rem;
    color: rgba(255,255,255,0.72);
    line-height: 1.6;
    margin-bottom: 0;
    position: relative;
    z-index: 1;
}

/* ── Pulso ── */
.pulso-card {
    background: #f8fafc;
    border-left: 4px solid #007cab;
    border-radius: 0 12px 12px 0;
    padding: 18px 20px;
    height: 100%;
}
.pulso-card.verde   { border-left-color: #1a7a4a; }
.pulso-card.azul    { border-left-color: #007cab; }
.pulso-card.naranja { border-left-color: #d97706; }
.pulso-card.morado  { border-left-color: #7c3aed; }
.pulso-card.teal    { border-left-color: #0891b2; }
.pulso-valor {
    font-size: 1.9rem;
    font-weight: 700;
    color: #1e293b;
    line-height: 1.1;
}
.pulso-label { font-size: 0.80rem; font-weight: 600; color: #1e293b; margin-top: 5px; }
.pulso-ctx   { font-size: 0.74rem; color: #64748b; margin-top: 2px; line-height: 1.35; }

/* ── Zonas ── */
.zona-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: #f8fafc;
    border-radius: 10px;
    margin-bottom: 8px;
    border-left: 4px solid #007cab;
}
.zona-row.alerta { border-left-color: #dc2626; background: #fef2f2; }
.zona-row.fragil { border-left-color: #d97706; background: #fffbeb; }
.zona-seccion { font-size: 1.05rem; font-weight: 700; color: #004a6e; min-width: 52px; }
.zona-spt {
    font-size: 0.75rem; background: #007cab; color: white;
    border-radius: 20px; padding: 2px 9px; font-weight: 600;
    min-width: 52px; text-align: center;
}
.zona-tipo    { font-size: 0.78rem; color: #64748b; min-width: 110px; }
.zona-tactica { font-size: 0.83rem; color: #1e293b; flex: 1; }
.zona-alerta-badge {
    font-size: 0.72rem; background: #dc2626; color: white;
    border-radius: 20px; padding: 2px 9px; font-weight: 600; white-space: nowrap;
}
.zona-fragil-badge {
    font-size: 0.72rem; background: #d97706; color: white;
    border-radius: 20px; padding: 2px 9px; font-weight: 600; white-space: nowrap;
}

/* ── Hallazgos ── */
.hallazgo-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}
.hallazgo-card .h-icon { font-size: 1.4rem; flex-shrink: 0; margin-top: 1px; }
.hallazgo-card .h-dato {
    font-size: 0.92rem; font-weight: 700; color: #1e293b;
    margin-bottom: 3px; line-height: 1.3;
}
.hallazgo-card .h-impl { font-size: 0.82rem; color: #64748b; line-height: 1.45; }

/* ── Cómo lo construimos ── */
.construimos-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 10px;
}
.construimos-title { font-size: 0.92rem; font-weight: 700; color: #1e293b; margin-bottom: 5px; }
.construimos-desc  { font-size: 0.82rem; color: #64748b; line-height: 1.45; }
.construimos-meta  { font-size: 0.72rem; color: #94a3b8; margin-top: 6px; font-weight: 500; }


/* ── Logo en header ── */
.header-top-row {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 14px;
}
.header-logo {
    width: 64px;
    height: 64px;
    border-radius: 12px;
    flex-shrink: 0;
    mix-blend-mode: lighten;
}
.header-text-block {
    flex: 1;
}
.header-text-block .header-sub {
    margin-bottom: 0;
}

/* ── Footer ── */
.footer {
    margin-top: 40px;
    padding-top: 16px;
    border-top: 1px solid #e2e8f0;
    text-align: center;
    font-size: 0.73rem;
    color: #94a3b8;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] { background-color: #004a6e !important; }
[data-testid="stSidebar"] * { color: #e8edf5 !important; }
</style>
"""


# ── Carga de datos (cacheada, fuera de main para no repetir) ─────────────────
@st.cache_data(ttl=300)
def cargar_datos():
    spt = pd.read_csv(os.path.join(DATA, "spt_secciones_1.csv"))
    enc = pd.read_csv(os.path.join(DATA, "encuesta1_clean.csv"))
    return spt, enc


# ════════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL — todo el contenido del Home va aquí
# st.Page la llama una sola vez, evitando el loop de doble render
# ════════════════════════════════════════════════════════════════════════════════
def main():

    st.markdown(CSS, unsafe_allow_html=True)

    # ── Datos ─────────────────────────────────────────────────────────────────
    try:
        spt, enc = cargar_datos()
        datos_ok = True
    except Exception:
        datos_ok = False
        spt = pd.DataFrame()
        enc = pd.DataFrame()

    if datos_ok:
        pct_votaria = (enc[enc["voto_duro_lastiri"] == 1]["factor_final"].sum()
                       / enc["factor_final"].sum() * 100)
        n_enc = len(enc)
    else:
        pct_votaria = 37.5
        n_enc = 521

    N_CONTACTOS           = 3_919
    N_SECCIONES_CUBIERTAS = 28
    PCT_CELULAR           = 60
    TAMANO_HOGAR_ITER     = 3.81
    ALCANCE_ESTIMADO      = int(N_CONTACTOS * TAMANO_HOGAR_ITER)
    FECHA_CORTE_OPERATIVO = "12 mar 2026"
    FECHA_CORTE_ENCUESTA  = "10 feb 2026"

    # ── HEADER ────────────────────────────────────────────────────────────────
    LOGO_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAQABAADASIAAhEBAxEB/8QAHAABAQEAAwEBAQAAAAAAAAAAAAECBgcIAwUE/8QASBABAAIBAgMDBwkGBQIEBwEAAAECAwQFBgcREiExFyI1QVFhchMyUlRxgZGS0QgUQqGxwRUjYuHwY4IkMzSDFjdDRVWT8aL/xAAcAQEBAAIDAQEAAAAAAAAAAAAAAgEGBAUHAwj/xAA7EQEAAQMBAwgHBwQDAQEAAAAAAQIDBAUGEXESFSExNEFRUhMyU5GhsdEUFiIjYYHBB0Lh8CQzYnJD/9oADAMBAAIRAxEAPwDxkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH//2Q=="
    st.markdown(f"""
    <div class="home-header">
        <div class="header-top-row">
            <img src="data:image/png;base64,{LOGO_B64}"
                 class="header-logo" alt="Data & AI Inclusion Tech">
            <div class="header-text-block">
                <div class="header-tag">Data & AI Inclusion Tech · Sistema de Inteligencia Electoral · Zacatlán, Puebla</div>
                <div class="header-title">JCLY · Morena 2027</div>
                <div class="header-sub">De la intuición a la evidencia. Gana la candidatura de tu partido, con datos propios.</div>
            </div>
        </div>
        <span class="header-corte">📅 Encuesta: {FECHA_CORTE_ENCUESTA} &nbsp;·&nbsp; Operativo: {FECHA_CORTE_OPERATIVO}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── CARDS PRINCIPALES ─────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-title">La plataforma genera tus datos, crea inteligencia y activa la operación</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown("""
        <div class="journey-card card-1">
            <div class="card-concept">Tu línea base propia</div>
            <span class="card-icon-bg">🗺️</span>
            <div class="card-title">¿A dónde voy primero?</div>
            <div class="card-body">¿Cuáles son las zonas donde una visita vale más?
            Prioridad territorial sección por sección — combinando encuesta propia,
            historial electoral y perfil demográfico.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(
            "pages/1_M1_Mapa_Territorial.py",
            label="Ver mapa territorial →",
            use_container_width=True,
        )

    with col2:
        st.markdown("""
        <div class="journey-card card-2">
            <div class="card-concept">Tu mapa de decisiones</div>
            <span class="card-icon-bg">📋</span>
            <div class="card-title">¿Cómo vamos en campo?</div>
            <div class="card-body">¿Cuántos contactos llevamos? ¿Qué secciones ya cubrimos
            y cuáles nos faltan? Semana a semana: cobertura, disponibilidad de voto
            y contactos con celular válido.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(
            "pages/2_M2_Avance_Operativo.py",
            label="Ver avance operativo →",
            use_container_width=True,
        )

    with col3:
        st.markdown("""
        <div class="journey-card card-3">
            <div class="card-concept">Tu operación activada</div>
            <span class="card-icon-bg">📱</span>
            <div class="card-title">¿A quién le mando el mensaje?</div>
            <div class="card-body">Base de contactos segmentada con generador de SMS.
            El mensaje correcto, a la persona correcta, en el momento correcto —
            directo a WhatsApp o SMS.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(
            "pages/5_M5_Contactos.py",
            label="Ver base de contactos →",
            use_container_width=True,
        )

    # ── CARDS SPRINT 4 ────────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-title">🆕 Nuevas estrategias</div>',
        unsafe_allow_html=True,
    )

    col_m6, col_m7 = st.columns(2, gap="medium")

    with col_m6:
        st.markdown("""
        <div class="journey-card" style="background:linear-gradient(145deg,#1a3a5c 0%,#1e4d8c 100%);min-height:200px;">
            <div class="card-concept">Estrategia Multinivel</div>
            <span class="card-icon-bg">🏘️</span>
            <div class="card-title">¿Quién está multiplicando el mensaje?</div>
            <div class="card-body">Reuniones por hogar en cada colonia y barrio.
            Registra anfitriones, asistentes y necesidades del territorio.
            El árbol crece — tú lo diriges.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(
            "pages/6_M6_Estrategia_Multinivel.py",
            label="Ver Estrategia Multinivel →",
            use_container_width=True,
        )

    with col_m7:
        st.markdown("""
        <div class="journey-card" style="background:linear-gradient(145deg,#1c1c3a 0%,#2d2d6b 100%);min-height:200px;">
            <div class="card-concept">Períódico territorial</div>
            <span class="card-icon-bg">📰</span>
            <div class="card-title">¿Qué le decimos a cada zona esta edición?</div>
            <div class="card-body">Periódico Mente Política y Empresarial.
            Zonas de distribución basadas en datos, sugerencia de contenidos
            por sección y medición de cobertura impresa.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(
            "pages/7_M7_Periodico.py",
            label="Ver Periódico Mente Política →",
            use_container_width=True,
        )

    st.info(
        "Navega también desde el menú en la **barra lateral izquierda** (ícono ☰ en móvil).",
        icon="💡",
    )

    # ── PULSO OPERATIVO ───────────────────────────────────────────────────────
    st.markdown(
        f'<div class="section-title">⚡ Pulso operativo — corte al {FECHA_CORTE_OPERATIVO}</div>',
        unsafe_allow_html=True,
    )

    p1, p2, p3, p4, p5 = st.columns(5, gap="medium")
    with p1:
        st.markdown(f"""
        <div class="pulso-card verde">
            <div class="pulso-valor">{N_CONTACTOS:,}</div>
            <div class="pulso-label">Personas contactadas</div>
            <div class="pulso-ctx">en campo · desde el 14 de febrero</div>
        </div>
        """, unsafe_allow_html=True)
    with p2:
        st.markdown(f"""
        <div class="pulso-card teal">
            <div class="pulso-valor">~{ALCANCE_ESTIMADO:,}</div>
            <div class="pulso-label">Alcance estimado</div>
            <div class="pulso-ctx">3.81 integrantes promedio por hogar · ITER 2020</div>
        </div>
        """, unsafe_allow_html=True)
    with p3:
        st.markdown(f"""
        <div class="pulso-card azul">
            <div class="pulso-valor">{N_SECCIONES_CUBIERTAS} / 33</div>
            <div class="pulso-label">Secciones con presencia</div>
            <div class="pulso-ctx">5 secciones aún sin operativo activo</div>
        </div>
        """, unsafe_allow_html=True)
    with p4:
        st.markdown(f"""
        <div class="pulso-card naranja">
            <div class="pulso-valor">{pct_votaria:.1f}%</div>
            <div class="pulso-label">Votarían por JCLY</div>
            <div class="pulso-ctx">encuesta · base {n_enc:,} entrevistas</div>
        </div>
        """, unsafe_allow_html=True)
    with p5:
        st.markdown(f"""
        <div class="pulso-card morado">
            <div class="pulso-valor">{PCT_CELULAR}%</div>
            <div class="pulso-label">Con celular válido</div>
            <div class="pulso-ctx">listos para WhatsApp o SMS</div>
        </div>
        """, unsafe_allow_html=True)

    # ── ZONAS DE MÁXIMA ATENCIÓN ──────────────────────────────────────────────
    st.markdown(
        '<div class="section-title">🎯 Zonas de máxima atención — ir primero aquí</div>',
        unsafe_allow_html=True,
    )

    tipo_map = {
        "urbano":         "🏙️ Urbano",
        "rural_marginal": "🏔️ Rural Marginal",
        "rural_media":    "🌾 Rural Media",
    }
    sin_cobertura = {2488}

    if datos_ok:
        prioritarias_df = spt[spt["clasificacion"] == "Prioritaria"].sort_values("SPT", ascending=False)
    else:
        prioritarias_df = pd.DataFrame({
            "seccion":             [2486, 2471, 2489, 2488],
            "SPT":                 [71.48, 70.99, 70.80, 70.72],
            "ambito_iter":         ["urbano", "rural_marginal", "rural_marginal", "rural_marginal"],
            "tactica_recomendada": [
                "Brigadas de primer contacto urgentes",
                "Brigadas de primer contacto urgentes",
                "Brigadas primer contacto + cierre",
                "Brigadas primer contacto + cierre",
            ],
        })

    for _, row in prioritarias_df.iterrows():
        seccion    = int(row["seccion"])
        es_alerta  = seccion in sin_cobertura
        tipo_texto = tipo_map.get(str(row["ambito_iter"]), str(row["ambito_iter"]))
        badge_html = '<span class="zona-alerta-badge">⚠️ Sin contactos</span>' if es_alerta else ""
        clase_row  = "zona-row alerta" if es_alerta else "zona-row"
        st.markdown(f"""
        <div class="{clase_row}">
            <span class="zona-seccion">§ {seccion}</span>
            <span class="zona-spt">SPT {row['SPT']:.1f}</span>
            <span class="zona-tipo">{tipo_texto}</span>
            <span class="zona-tactica">{row['tactica_recomendada']}</span>
            {badge_html}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="zona-row fragil">
        <span class="zona-seccion">§ 2472</span>
        <span class="zona-spt" style="background:#d97706;">Consolidación</span>
        <span class="zona-tipo">🌾 Rural Media</span>
        <span class="zona-tactica">Margen electoral más frágil del municipio — 1.6 pts en 2024. Intervención urgente.</span>
        <span class="zona-fragil-badge">⚡ Margen frágil</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Ver detalle completo en Módulo 1 · Mapa Territorial o Módulo 4 · Historia Electoral.")

    # ── HALLAZGOS ─────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-title">🔍 Lo que cambia la estrategia — hallazgos de encuesta</div>',
        unsafe_allow_html=True,
    )

    hallazgos = [
        ("🚀",
         "Con JCLY en la boleta, Morena casi dobla su intención de voto: de 11% a 21%.",
         "La candidatura es suya, no del partido. El nombre propio es el activo central de campaña."),
        ("🌾",
         "4 de cada 10 personas en el campo rural nunca han escuchado hablar de JCLY.",
         "Son 147 votantes potenciales sin alcanzar. Solo las brigadas presenciales los llegan — la pauta digital no."),
        ("🗳️",
         "El 42.8% del electorado no se identifica con ningún partido.",
         "Votan por persona y por agenda. Activar el voto duro de Morena es necesario, pero no suficiente."),
        ("📡",
         "Facebook (53%) supera a la TV (49%) como medio principal en Zacatlán.",
         "La conectividad real es del 61%, no 26% como reporta el ITER. La pauta digital sí funciona aquí."),
        ("🏔️",
         "3 de las 4 zonas más prioritarias son rurales marginales.",
         "La pauta digital no las alcanza — son 100% operativo de tierra. Brigadas primero."),
        ("💧",
         "La agenda urbana y rural son completamente distintas.",
         "Urbano: economía y corrupción. Rural: infraestructura y agua. Un solo mensaje de campaña no funciona."),
    ]

    col_h1, col_h2 = st.columns(2, gap="medium")
    for i, (icon, dato, impl) in enumerate(hallazgos):
        col = col_h1 if i % 2 == 0 else col_h2
        with col:
            st.markdown(f"""
            <div class="hallazgo-card">
                <span class="h-icon">{icon}</span>
                <div>
                    <div class="h-dato">{dato}</div>
                    <div class="h-impl">{impl}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── CÓMO LO CONSTRUIMOS ───────────────────────────────────────────────────
    with st.expander("🔬 ¿Cómo lo construimos? — la inteligencia detrás del sistema"):
        st.markdown("""
        <div style="font-size:0.85rem; color:#475569; margin-bottom:16px; line-height:1.6;">
            521 entrevistas representativas &nbsp;·&nbsp; 9 arquetipos de votante &nbsp;·&nbsp;
            3 elecciones analizadas &nbsp;·&nbsp; 33 secciones electorales<br>
            <span style="color:#94a3b8;">Metodología equivalente a las principales casas encuestadoras
            nacionales, a una fracción del costo.</span>
        </div>
        """, unsafe_allow_html=True)

        cc1, cc2 = st.columns(2, gap="medium")
        with cc1:
            st.markdown("""
            <div class="construimos-card">
                <div class="construimos-title">👥 Perfiles del Votante Zacatleco</div>
                <div class="construimos-desc">9 perfiles del votante zacatleco — con el mensaje que mueve
                a cada uno. Generados con MCA y clustering K-Means sobre 521 entrevistas.</div>
                <div class="construimos-meta">4 arquetipos urbanos · 5 arquetipos rurales · validación cruzada</div>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/3_M3_Segmentacion.py", label="Ver perfiles de votante →", use_container_width=True)

        with cc2:
            st.markdown("""
            <div class="construimos-card">
                <div class="construimos-title">📊 Historia Electoral por Sección</div>
                <div class="construimos-desc">Historia electoral 2018–2024 — qué tan sólida es cada sección.
                Evolución del voto Morena en las 3 últimas elecciones con clasificación por margen real.</div>
                <div class="construimos-meta">28 secciones activas · Morena ganó las 28 en 2024 · 90% competidas</div>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/4_M4_Historial.py", label="Ver historia electoral →", use_container_width=True)

        st.markdown("""
        <div class="construimos-card" style="margin-top:10px;">
            <div class="construimos-title">🏗️ Generación de Datos Propios</div>
            <div class="construimos-desc">Diseño del cuestionario, muestreo y cuotas demográficas por sección,
            capacitación de encuestadores, infraestructura digital de levantamiento, monitoreo en tiempo real,
            limpieza y activación de datos. Los datos son tuyos — no de Morena, no de ningún consultor.</div>
            <div class="construimos-meta">Encuesta 1: 521 entrevistas · 19/33 secciones con datos reales ·
            14 secciones proyectadas por modelo KNN</div>
        </div>
        """, unsafe_allow_html=True)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="footer">
        Data & AI Inclusion Tech · Inteligencia Electoral Zacatlán · JCLY Morena 2026 · Confidencial<br>
        Uso exclusivo del equipo de campaña
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# NAVEGACIÓN — se declara en el nivel del módulo, fuera de main()
# pg.run() llama a main() una sola vez cuando el usuario está en el Home
# ════════════════════════════════════════════════════════════════════════════════
pg = st.navigation(
    {
        "La Plataforma": [
            st.Page(main, title="🏠  Inicio", default=True),
        ],
        "Tu línea base propia": [
            st.Page("pages/1_M1_Mapa_Territorial.py", title="🗺️  ¿A dónde voy primero?"),
        ],
        "Tu mapa de decisiones": [
            st.Page("pages/2_M2_Avance_Operativo.py", title="📋  ¿Cómo vamos en campo?"),
        ],
        "Tu operación activada": [
            st.Page("pages/5_M5_Contactos.py",              title="📱  ¿A quién le mando el mensaje?"),
            st.Page("pages/6_M6_Estrategia_Multinivel.py",  title="🏘️  Estrategia Multinivel"),
            st.Page("pages/7_M7_Periodico.py",              title="📰  Periódico Mente Política"),
        ],
        "Cómo lo construimos": [
            st.Page("pages/3_M3_Segmentacion.py", title="👥  Perfiles del votante"),
            st.Page("pages/4_M4_Historial.py",    title="📊  Historia electoral"),
        ],
    },
    position="sidebar",
)

st.set_page_config(
    page_title="Inteligencia Electoral · Zacatlán",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

pg.run()