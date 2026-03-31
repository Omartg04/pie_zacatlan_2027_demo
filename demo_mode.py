"""
demo_mode.py — Control de acceso para versión vitrina
Inteligencia Electoral Zacatlán · JCLY Morena 2026

USO en cada módulo (2 líneas al inicio, después de st.set_page_config):
    from demo_mode import check_demo_mode
    check_demo_mode()
"""

import streamlit as st

# ── WhatsApp del equipo ───────────────────────────────────────────────────────
WHATSAPP_NUMBER = "521XXXXXXXXXX"   # ← reemplazar con número real
WHATSAPP_MSG    = "Hola, vi el sistema PIE Zacatlán y me gustaría agendar una sesión de presentación."

# ── Contraseña (Streamlit Cloud → Settings → Secrets: DEMO_PASSWORD) ─────────
def _get_password():
    try:
        return st.secrets["DEMO_PASSWORD"]
    except Exception:
        return None

# ── CSS ───────────────────────────────────────────────────────────────────────
# Estrategia: blur vía CSS sobre los bloques de Streamlit posteriores al banner.
# Streamlit no respeta divs abiertos entre llamadas, por eso usamos selectores
# CSS que excluyen el primer bloque (el banner).
DEMO_CSS = """
<style>
.demo-banner {
    position: relative;
    z-index: 9999;
    background: linear-gradient(135deg, #004a6e 0%, #007cab 100%);
    border-radius: 12px;
    padding: 20px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    box-shadow: 0 4px 20px rgba(0,74,110,0.3);
    filter: none !important;
}
.demo-banner-text h3 { color:#fff; font-size:1.05rem; font-weight:700; margin:0 0 4px; }
.demo-banner-text p  { color:#93c5fd; font-size:0.85rem; margin:0; line-height:1.4; }
.demo-banner-icon    { font-size:2.2rem; flex-shrink:0; }
.demo-whatsapp-btn {
    display:inline-flex; align-items:center; gap:8px;
    background:#25D366; color:#fff !important;
    font-weight:600; font-size:0.88rem;
    padding:10px 20px; border-radius:8px;
    text-decoration:none !important; white-space:nowrap; flex-shrink:0;
}
.demo-whatsapp-btn:hover { background:#1ebe5d; color:#fff !important; }

/* Blur sobre todos los bloques de contenido excepto el primero (el banner) */
section[data-testid="stMain"] [data-testid="stVerticalBlock"] > div:not(:first-child) {
    filter: blur(6px) !important;
    pointer-events: none !important;
    user-select: none !important;
    opacity: 0.85;
}
</style>
"""

def _build_banner():
    import urllib.parse
    wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(WHATSAPP_MSG)}"
    return f"""
<div class="demo-banner">
    <div class="demo-banner-icon">🔒</div>
    <div class="demo-banner-text">
        <h3>Este módulo está disponible en sesión de presentación</h3>
        <p>Los datos contienen inteligencia operativa sensible de la campaña.<br>
        Agenda una sesión con el equipo para acceder al módulo completo.</p>
    </div>
    <a href="{wa_url}" target="_blank" class="demo-whatsapp-btn">
        📅 &nbsp;Agendar sesión
    </a>
</div>
"""

def check_demo_mode():
    # ── Desbloqueo en sidebar ─────────────────────────────────────────────────
    pwd_correcta = _get_password()
    if pwd_correcta:
        with st.sidebar:
            st.markdown("---")
            pwd_input = st.text_input(
                "🔑 Acceso equipo", type="password",
                key="demo_pwd_input", placeholder="Contraseña"
            )
            if pwd_input and pwd_input == pwd_correcta:
                st.session_state["modo_demo"] = False
                st.rerun()
            elif pwd_input:
                st.error("Contraseña incorrecta")

    # ── Estado por defecto: demo activo ──────────────────────────────────────
    if "modo_demo" not in st.session_state:
        st.session_state["modo_demo"] = True

    if not st.session_state["modo_demo"]:
        return  # acceso completo

    # ── Modo demo: CSS + banner como primer bloque ────────────────────────────
    st.markdown(DEMO_CSS, unsafe_allow_html=True)
    st.markdown(_build_banner(), unsafe_allow_html=True)
    # El módulo continúa ejecutándose — su contenido queda difuminado por CSS