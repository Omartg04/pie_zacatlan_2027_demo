"""
demo_mode.py — Control de acceso para versión vitrina
Inteligencia Electoral Zacatlán · JCLY Morena 2026

USO en cada módulo (2 líneas al inicio, después de st.set_page_config):
    from demo_mode import check_demo_mode
    check_demo_mode()
"""

import streamlit as st

# ── Número de WhatsApp para agendar reunión ────────────────────────────────────
# Formato internacional sin espacios ni símbolos
WHATSAPP_NUMBER = "521XXXXXXXXXX"   # ← reemplazar con número real del equipo
WHATSAPP_MSG    = "Hola, vi el sistema PIE Zacatlán y me gustaría agendar una sesión de presentación."

# ── Contraseña para desbloquear modo operativo ────────────────────────────────
# Configurar en Streamlit Cloud → Settings → Secrets como:
#   DEMO_PASSWORD = "tu_contraseña"
def _get_password():
    try:
        return st.secrets["DEMO_PASSWORD"]
    except Exception:
        return None

# ── CSS del banner y blur ─────────────────────────────────────────────────────
DEMO_CSS = """
<style>
/* Banner fijo en la parte superior del contenido */
.demo-banner {
    position: sticky;
    top: 0;
    z-index: 9999;
    background: linear-gradient(135deg, #004a6e 0%, #007cab 100%);
    border-radius: 12px;
    padding: 20px 28px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    box-shadow: 0 4px 20px rgba(0,74,110,0.25);
}
.demo-banner-text h3 {
    color: #ffffff;
    font-size: 1.05rem;
    font-weight: 700;
    margin: 0 0 4px 0;
}
.demo-banner-text p {
    color: #93c5fd;
    font-size: 0.85rem;
    margin: 0;
    line-height: 1.4;
}
.demo-banner-icon {
    font-size: 2rem;
    flex-shrink: 0;
}
.demo-whatsapp-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #25D366;
    color: #ffffff !important;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 10px 18px;
    border-radius: 8px;
    text-decoration: none !important;
    white-space: nowrap;
    flex-shrink: 0;
    transition: background 0.2s;
}
.demo-whatsapp-btn:hover {
    background: #1da851;
    color: #ffffff !important;
}

/* Contenedor con blur para el contenido del módulo */
.demo-blur-wrapper {
    filter: blur(5px);
    pointer-events: none;
    user-select: none;
    opacity: 0.7;
    margin-top: 8px;
}
</style>
"""

# ── Banner HTML ───────────────────────────────────────────────────────────────
def _build_banner():
    import urllib.parse
    msg_encoded = urllib.parse.quote(WHATSAPP_MSG)
    wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={msg_encoded}"
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

# ── Función principal — llamar al inicio de cada módulo ───────────────────────
def check_demo_mode():
    """
    Si modo_demo está activo:
      1. Inyecta el CSS de blur
      2. Renderiza el banner de bloqueo
      3. Abre el div con blur — el módulo renderiza sus datos debajo (difuminados)

    El módulo NO necesita cambiar nada más en su lógica. Todo su contenido
    queda envuelto en el blur automáticamente por el CSS.

    Para desbloquear: ingresar contraseña en el sidebar.
    """

    # ── Control de desbloqueo en sidebar ──────────────────────────────────────
    pwd_correcta = _get_password()
    if pwd_correcta:
        with st.sidebar:
            st.markdown("---")
            pwd_input = st.text_input(
                "🔑 Acceso equipo",
                type="password",
                key="demo_pwd_input",
                placeholder="Contraseña"
            )
            if pwd_input and pwd_input == pwd_correcta:
                st.session_state["modo_demo"] = False
                st.success("✅ Acceso habilitado")
            elif pwd_input:
                st.error("Contraseña incorrecta")

    # ── Evaluar si estamos en modo demo ───────────────────────────────────────
    # Por defecto siempre demo=True a menos que se haya desbloqueado
    if "modo_demo" not in st.session_state:
        st.session_state["modo_demo"] = True

    if not st.session_state["modo_demo"]:
        return  # acceso completo — salir sin hacer nada

    # ── Modo demo activo: inyectar CSS + banner + abrir div blur ──────────────
    st.markdown(DEMO_CSS, unsafe_allow_html=True)
    st.markdown(_build_banner(), unsafe_allow_html=True)
    st.markdown('<div class="demo-blur-wrapper">', unsafe_allow_html=True)
    # NOTA: el div se cierra automáticamente al final del render de Streamlit.
    # No es HTML estricto pero funciona en el renderer de Streamlit.
