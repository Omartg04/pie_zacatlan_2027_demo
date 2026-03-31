"""
M5 — Base de Contactos Segmentada
Inteligencia Electoral Zacatlán · JCLY Morena 2026
v1.1 — Correcciones: sidebar visible, API con st.secrets, GPS link, 3 cards
"""

import streamlit as st
import pandas as pd
import io
import os
import requests
from datetime import datetime

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="M5 · Base de Contactos",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Demo mode — no modificar ────────────────────────────────────────────────
from demo_mode import check_demo_mode
check_demo_mode()


FECHA_CORTE             = "2026-02-14"  # ajustar si el CSV nuevo tiene fecha diferente
SECCIONES_PRIORITARIAS  = [2471, 2486, 2488, 2489]
LAT_MIN, LAT_MAX        = 19.5, 20.5
LON_MIN, LON_MAX        = -98.5, -97.5

COLORES_SEGMENTO = {
    "Multiplicadores":  "#1a7a4a",
    "Nodos Multinivel": "#7c3aed",
    "Activación":       "#007cab",
    "Persuasión":       "#d97706",
    "Primer contacto":  "#475569",
}

ICONOS_SEGMENTO = {
    "Multiplicadores":  "⭐",
    "Nodos Multinivel": "🌐",
    "Activación":       "🎯",
    "Persuasión":       "🤝",
    "Primer contacto":  "👋",
}

INSTRUCCION_SEGMENTO = {
    "Multiplicadores":  "Ya conocen a Juan Carlos y votarían por él. Convertirlos en promotores activos.",
    "Nodos Multinivel": "Multiplicadores en secciones prioritarias o con poca cobertura de reuniones. Contactar para ser anfitriones de reunión por hogar en su colonia.",
    "Activación":       "Votarían por Juan Carlos pero aún no lo conocen bien. Reforzar presencia.",
    "Persuasión":       "Conocen a Juan Carlos pero no han decidido. El trabajo es convencer.",
    "Primer contacto":  "No conocen a Juan Carlos o no han decidido. Presentarlo, no convencer.",
}

PROBLEMÁTICAS_GRUPO = {
    "Inseguridad":            ["Inseguridad"],
    "Calles y pavimentación": ["Calles sin pavimento (terracería)", "Calles en mal estado"],
    "Agua potable":           ["Falta de agua potable"],
    "Economía y empleo":      ["Economía", "Bajos salarios", "Falta de empleos", "Pobreza"],
    "Corrupción":             ["Corrupción"],
    "Alumbrado público":      ["Falta de alumbrado público",
                               "Mantenimiento y reparación del alumbrado público"],
    "Salud y campo":          ["Desabasto de medicamentos", "Falta de apoyos al campo",
                               "Faltan más o mejores servicios de salud"],
    "Otra":                   ["Otra ESPECIFICAR", "Falta de impulso al turismo",
                               "Faltan vías de comunicación (carreteras y caminos)",
                               "Falta de cuidado del medio ambiente", "Recolección de basura",
                               "Narcotráfico", "Migración", "Mala calidad de la educación pública"],
}

ATRIBUTOS = {
    "honestidad":          ("p10_3_texto_text", "honesto"),
    "cercanía":            ("p11_3_texto_text", "cercano a la gente"),
    "respeto a mujeres":   ("p12_3_texto_text", "respetuoso con las mujeres"),
    "conoce el municipio": ("p13_3_texto_text", "conocedor del municipio"),
    "cumple promesas":     ("p14_3_texto_text", "cumplidor de sus promesas"),
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
[data-testid="stSidebar"] {
    background-color: #004a6e !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label {
    color: #e8edf5 !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background-color: #004a6e !important;
    color: #ffffff !important;
    border-color: #007cab !important;
}
[data-testid="stSidebar"] .stSelectbox svg,
[data-testid="stSidebar"] .stMultiSelect svg {
    fill: #00c0ff !important;
}
[data-testid="stSidebar"] hr {
    border-color: #007cab !important;
}
[data-testid="stSidebar"] .stFileUploader > div {
    background-color: #004a6e !important;
    border-color: #007cab !important;
}
.metric-card {
    background: #f8fafc; border-radius: 10px;
    padding: 16px 20px; border-left: 4px solid #007cab;
}
.metric-card.green  { border-left-color: #1a7a4a; }
.metric-card.orange { border-left-color: #d97706; }
.metric-card.red    { border-left-color: #dc2626; }
.metric-val { font-size: 2rem; font-weight: 800; color: #1e293b; line-height: 1; }
.metric-lbl { font-size: 0.8rem; color: #64748b; margin-top: 4px; }
.alert-red  {
    background: #fef2f2; border: 1px solid #fca5a5;
    border-radius: 8px; padding: 12px 16px; margin: 10px 0;
}
.alert-warn {
    background: #fffbeb; border: 1px solid #fcd34d;
    border-radius: 8px; padding: 12px 16px; margin: 10px 0;
}
.llm-box {
    background: #f0fdf4; border: 1px solid #86efac;
    border-radius: 10px; padding: 14px 18px; margin: 10px 0;
}
.section-hdr {
    font-size: 1.05rem; font-weight: 700; color: #1e293b;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 5px; margin: 18px 0 10px 0;
}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ───────────────────────────────────────────────────────────────────

def prob_grupo(val):
    if pd.isna(val):
        return "Sin dato"
    for grupo, vals in PROBLEMÁTICAS_GRUPO.items():
        if val in vals:
            return grupo
    return "Otra"


def asignar_segmento(row):
    conoce = row.get("p8_3_texto_text")
    voto   = row.get("p16_3_texto_text")
    seccion = row.get("seccion_electoral_text")
    try:
        seccion = int(seccion) if pd.notna(seccion) else None
    except Exception:
        seccion = None

    es_multiplicador = (voto == "Votaría" and conoce == "Sí")
    es_prioritaria   = seccion in SECCIONES_PRIORITARIAS

    # Nodo Multinivel: Multiplicador en sección prioritaria O con celular
    # (se refina después con cobertura de M6 cuando esté disponible)
    if es_multiplicador and es_prioritaria:
        return "Nodos Multinivel"
    if voto == "Votaría" and conoce == "Sí":
        return "Multiplicadores"
    if voto == "Votaría":
        return "Activación"
    if conoce == "Sí" and str(voto) in ["No sabe (NO LEER)", "No respondió (NO LEER)"]:
        return "Persuasión"
    if str(voto) == "Nunca votaría":
        return "Descarte"
    return "Primer contacto"


def semana_label(fecha, corte):
    delta = (fecha - corte).days
    sem   = max(delta // 7 + 1, 1)
    ini   = corte + pd.Timedelta(days=(sem - 1) * 7)
    fin   = ini + pd.Timedelta(days=6)
    return f"Sem {sem} · {ini.strftime('%d %b')}–{fin.strftime('%d %b')}"


def gps_link(lat, lon):
    try:
        la, lo = float(lat), float(lon)
        if LAT_MIN <= la <= LAT_MAX and LON_MIN <= lo <= LON_MAX:
            return f"https://maps.google.com/?q={la},{lo}"
    except Exception:
        pass
    return None


@st.cache_data(show_spinner=False)
def cargar_datos(raw: bytes) -> pd.DataFrame:
    df    = pd.read_csv(io.BytesIO(raw))
    df["Created Date"] = pd.to_datetime(df["Created Date"], format="mixed")
    corte = pd.to_datetime(FECHA_CORTE)
    df    = df[df["Created Date"] >= corte].copy()

    df["segmento"]    = df.apply(asignar_segmento, axis=1)
    df["prob_grupo"]  = df["p2_1_autobinding_option_p2_1_texto"].apply(prob_grupo)
    df["tiene_cel"]   = df["celular_encuestado_number"].notna()
    df["celular_fmt"] = df["celular_encuestado_number"].apply(
        lambda x: str(int(x)) if pd.notna(x) else ""
    )
    df["semana"] = df["Created Date"].apply(lambda d: semana_label(d, corte))
    df["seccion"] = df["seccion_electoral_text"].apply(
        lambda x: int(x) if pd.notna(x) else None
    )
    df["nombre_display"] = df["nombre_encuestado_text"].fillna("Sin nombre").apply(
        lambda x: "Sin nombre"
        if str(x).lower().strip() in ["anonimo", "anónimo", "", "nan"] else str(x)
    )
    df["gps_link"] = df.apply(
        lambda r: gps_link(r.get("latitud_text"), r.get("longitud_text")), axis=1
    )

    def atribs_debiles(row):
        if row.get("p8_3_texto_text") != "Sí":
            return ""
        return ", ".join(
            n for n, (col, _) in ATRIBUTOS.items()
            if row.get(col) == "No sabe (NO LEER)"
        )

    df["atribs_debiles"] = df.apply(atribs_debiles, axis=1)
    return df


def perfil_grupo(df_g: pd.DataFrame) -> dict:
    n     = len(df_g)
    probs = df_g["prob_grupo"].value_counts()
    atribs = []
    for nombre, (col, _) in ATRIBUTOS.items():
        if col in df_g.columns:
            tot = df_g[col].notna().sum()
            ns  = (df_g[col] == "No sabe (NO LEER)").sum()
            if tot > 0 and ns / tot > 0.15:
                atribs.append(f"{nombre} ({ns/tot*100:.0f}% no sabe)")
    return {
        "n":              n,
        "prob_top":       probs.index[0] if len(probs) else "Sin dato",
        "prob_pct":       probs.iloc[0] / n * 100 if len(probs) else 0,
        "probs_top3":     probs.head(3).to_dict(),
        "atribs_debiles": atribs,
    }


# ── API ───────────────────────────────────────────────────────────────────────

def get_api_key() -> str | None:
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        import os
        return os.environ.get("ANTHROPIC_API_KEY")


# Palabras prohibidas — carrier-safe
_PALABRAS_PROHIBIDAS = [
    "vota", "votar", "votación", "candidato", "candidata",
    "campaña", "partido", "elección", "elecciones", "urna", "urnas",
    "Morena", "PAN", "PRI", "ganar", "ganemos", "triunfo",
    "propaganda", "mitin", "sufragio",
]

# Defaults de enfoque por segmento
_ENFOQUE_DEFAULT = {
    "Multiplicadores":  "Híbrido",
    "Nodos Multinivel": "Comunitario",
    "Activación":       "Comunitario",
    "Persuasión":       "Híbrido",
    "Primer contacto":  "Neutro total",
    None:               "Neutro total",   # modo todos
}

# ¿El segmento conoce a JCLY?
_CONOCE = {
    "Multiplicadores": True,
    "Nodos Multinivel": True,
    "Activación":      False,
    "Persuasión":      True,
    "Primer contacto": False,
    None:              False,
}


def _build_system_prompt() -> str:
    prohibidas = ", ".join(f'"{p}"' for p in _PALABRAS_PROHIBIDAS)
    return (
        "Eres un redactor experto en comunicación comunitaria para municipios rurales "
        "y urbanos de Puebla, México.\n"
        "Tu trabajo es redactar mensajes SMS que hablen de problemas reales de la comunidad "
        "y movilicen a los vecinos.\n\n"
        "REGLAS ABSOLUTAS — sin excepciones:\n"
        f"1. Máximo 160 caracteres por mensaje, incluyendo espacios y puntuación.\n"
        f"2. NUNCA uses estas palabras: {prohibidas}.\n"
        "3. El mensaje debe sonar como comunicación vecinal o comunitaria, "
        "NUNCA como propaganda electoral.\n"
        "4. Una sola idea central. Una sola acción al final.\n"
        "5. Sin adjetivos vacíos: nada de 'gran líder', 'mejor futuro', 'cambio real'.\n"
        "6. El mensaje debe poder enviarse por SMS masivo sin activar filtros de "
        "contenido político de los carriers.\n"
        "7. Escribe en español mexicano, informal pero respetuoso.\n"
        "8. Termina siempre con una llamada a la acción concreta: unirse, informarse, "
        "asistir, compartir — NUNCA 'votar'.\n\n"
        "FORMATO DE RESPUESTA — siempre exactamente así, sin texto adicional:\n"
        "VARIANTE 1: [mensaje]\n"
        "VARIANTE 2: [mensaje]\n"
        "VARIANTE 3: [mensaje]"
    )


def _build_user_prompt(
    segmento: str | None,
    enfoque: str,
    tono: str,
    perfil: dict,
    enfasis: str = "",
) -> str:
    conoce    = _CONOCE.get(segmento, False)
    modo_todos = segmento is None

    probs_str  = ", ".join(f"{k} ({v})" for k, v in perfil["probs_top3"].items())
    atribs_str = (
        "Atributos que el grupo aún no le reconoce: " + "; ".join(perfil["atribs_debiles"])
        if perfil["atribs_debiles"] else ""
    )
    enfasis_str = (
        f"\nÉNFASIS ADICIONAL (debe estar presente en el mensaje): {enfasis.strip()}"
        if enfasis and enfasis.strip() else ""
    )

    # ── Regla del nombre según enfoque ──
    if enfoque == "Comunitario":
        if conoce:
            regla_nombre = (
                "Menciona a Juan Carlos Lastiri por nombre completo como un vecino comprometido "
                "que está trabajando en este problema. No lo llames candidato ni le asignes cargo."
            )
        else:
            regla_nombre = (
                "No menciones el nombre de ninguna persona. Habla de "
                "'un grupo de vecinos de Zacatlán' o 'la comunidad organizada'."
            )
        regla_partido = (
            "Puedes mencionar 'la organización comunitaria' como colectivo, "
            "nunca como partido político."
        )
    elif enfoque == "Híbrido":
        if conoce:
            regla_nombre = (
                "Menciona a Juan Carlos solo por su nombre de pila, "
                "como alguien activo en la comunidad. Sin cargo, sin partido."
            )
        else:
            regla_nombre = (
                "No menciones el nombre de ninguna persona. "
                "Habla de la propuesta o de la acción colectiva."
            )
        regla_partido = "No menciones ningún partido político bajo ninguna circunstancia."
    else:  # Neutro total
        regla_nombre = (
            "No menciones el nombre de ninguna persona. "
            "Usa solo 'vecinos de Zacatlán', 'la comunidad' o 'nosotros'."
        )
        regla_partido = "No menciones ningún partido político bajo ninguna circunstancia."

    # ── Regla de tono ──
    if tono == "Motivacional/directo":
        regla_tono = (
            "Tono imperativo y motivacional. Frases cortas y contundentes. "
            "Verbos de acción al inicio o cierre. Sin preguntas retóricas."
        )
    else:
        regla_tono = (
            "Tono cercano y coloquial, como si le escribieras a un conocido. "
            "Segunda persona singular: 'tú', 'tu familia', 'tu colonia'. "
            "Puedes abrir con una pregunta retórica que conecte con su experiencia."
        )

    # ── Contexto de segmento ──
    if modo_todos:
        seg_ctx = (
            "Destinatario: TODOS los contactos del municipio (audiencia mixta).\n"
            "Objetivo: mensaje amplio que funcione para cualquier perfil de vecino."
        )
    elif segmento == "Nodos Multinivel":
        seg_ctx = (
            "Segmento: Nodos Multinivel\n"
            "Objetivo: invitar a esta persona a ser anfitrión de una reunión por hogar "
            "en su colonia para conocer la propuesta de Juan Carlos Lastiri. "
            "Ya nos apoya — el mensaje es una invitación personal a multiplicar el mensaje, "
            "no a convencer. Tono: como si le escribiera alguien de su confianza del equipo."
        )
    else:
        seg_ctx = (
            f"Segmento: {segmento}\n"
            f"Objetivo: {INSTRUCCION_SEGMENTO[segmento]}"
        )

    return (
        f"{seg_ctx}\n"
        f"Tamaño del grupo: {perfil['n']} personas\n"
        f"Problema principal: {perfil['prob_top']} ({perfil['prob_pct']:.0f}%)\n"
        f"Distribución problemáticas: {probs_str}\n"
        f"{atribs_str}"
        f"{enfasis_str}\n\n"
        f"INSTRUCCIONES ESPECÍFICAS:\n"
        f"Regla del nombre: {regla_nombre}\n"
        f"Regla del partido: {regla_partido}\n"
        f"Regla de tono: {regla_tono}\n\n"
        f"Escribe exactamente 3 variantes de SMS. "
        f"Cada una ancla en el problema principal y cierra con acción concreta."
    )


def _parsear_variantes(texto: str) -> list[str]:
    """Extrae las 3 variantes del formato VARIANTE N: [texto]"""
    import re
    patron = re.compile(
        r"VARIANTE\s+\d+:\s*(.+?)(?=VARIANTE\s+\d+:|$)",
        re.DOTALL | re.IGNORECASE,
    )
    variantes = [m.strip() for m in patron.findall(texto)]
    # Fallback: si el parseo falla, el texto completo va al slot 1
    if not variantes:
        variantes = [texto.strip()]
    while len(variantes) < 3:
        variantes.append("")
    return variantes[:3]


def generar_variantes_sms(
    segmento: str | None,
    perfil: dict,
    enfoque: str,
    tono: str,
    enfasis: str = "",
) -> list[str]:
    """
    Genera 3 variantes de SMS carrier-safe para el segmento y configuración dados.
    Retorna lista de 3 strings. En caso de error, el mensaje de error va en [0].

    segmento = None  →  modo municipal (todos los segmentos).
    segmento = str   →  segmento específico (Multiplicadores, Activación, etc.)
    enfoque  = "Comunitario" | "Híbrido" | "Neutro total"
    tono     = "Motivacional/directo" | "Cercano/coloquial"
    """
    api_key = get_api_key()
    if not api_key:
        return [
            "⚙️ Falta la API key. Agrégala en .streamlit/secrets.toml:\n"
            'ANTHROPIC_API_KEY = "sk-ant-..."',
            "", "",
        ]

    system_p = _build_system_prompt()
    user_p   = _build_user_prompt(segmento, enfoque, tono, perfil, enfasis)

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         api_key,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":       "claude-sonnet-4-20250514",
                "max_tokens":  450,
                "temperature": 0.85,
                "top_p":       0.95,
                "system":      system_p,
                "messages":    [{"role": "user", "content": user_p}],
            },
            timeout=30,
        )
        data = resp.json()

        if resp.status_code != 200:
            err = data.get("error", {}).get("message", str(data))
            return [f"[Error API {resp.status_code}: {err}]", "", ""]

        content = data.get("content", [])
        texto   = next((b["text"] for b in content if b.get("type") == "text"), "")
        return _parsear_variantes(texto)

    except requests.exceptions.Timeout:
        return ["[Error: timeout al conectar con la API]", "", ""]
    except Exception as e:
        return [f"[Error inesperado: {e}]", "", ""]


# ══════════════════════════════════════════════════════════════════════════════
# UI PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<p style='font-size:1rem;font-weight:700;color:#ffffff;margin-bottom:4px;'>"
        "📋 M5 · Contactos</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(
        "<p style='font-size:0.82rem;color:#b0c4e8;margin-bottom:6px;'>"
        "📂 Operativo de campo</p>",
        unsafe_allow_html=True,
    )

    # ── Carga automática desde raw/ si existe ────────────────────────────────
    BASE_M5   = os.path.dirname(os.path.abspath(__file__))
    CSV_AUTO  = os.path.join(BASE_M5, "..", "raw", "induccion_032726.csv")
    tiene_auto = os.path.exists(CSV_AUTO)

    if tiene_auto:
        st.markdown(
            "<p style='color:#2a9d8f;font-size:0.82rem;'>✅ <b>induccion_032726.csv</b> "
            "cargado automáticamente.</p>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<p style='color:#f4a261;font-size:0.82rem;'>⚠️ No se encontró "
            "induccion_032726.csv en raw/</p>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<p style='font-size:0.78rem;color:#b0c4e8;margin:6px 0 4px;'>"
        "Subir CSV más reciente (opcional):</p>",
        unsafe_allow_html=True,
    )
    archivo = st.file_uploader("CSV del operativo", type=["csv"],
                               label_visibility="collapsed")

    # ── Determinar fuente de datos ───────────────────────────────────────────
    if archivo is not None:
        raw_bytes = archivo.read()
        fuente_label = archivo.name
    elif tiene_auto:
        with open(CSV_AUTO, "rb") as f:
            raw_bytes = f.read()
        fuente_label = "induccion_032726.csv"
    else:
        st.markdown(
            "<p style='color:#00c0ff;font-size:0.85rem;'>👆 Sube el CSV exportado "
            "desde la plataforma para comenzar.</p>",
            unsafe_allow_html=True,
        )
        st.stop()
        raw_bytes = None
        fuente_label = ""

    df_raw = cargar_datos(raw_bytes)
    df_act = df_raw[df_raw["segmento"] != "Descarte"].copy()

    # ── Guardar Nodos Multinivel en session_state para M6 ─────────────────────
    df_nodos = df_raw[df_raw["segmento"] == "Nodos Multinivel"].copy()
    if len(df_nodos) > 0:
        nodos_resumen = df_nodos.groupby("seccion").agg(
            n_nodos=("segmento", "count"),
            n_con_cel=("tiene_cel", "sum"),
        ).reset_index()
        nodos_resumen["pct_cel"] = (
            nodos_resumen["n_con_cel"] / nodos_resumen["n_nodos"] * 100
        ).round(0)
        st.session_state["nodos_multinivel"] = nodos_resumen.to_dict("records")
    else:
        st.session_state["nodos_multinivel"] = []

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.82rem;color:#b0c4e8;margin:0 0 8px 0;'>🔍 Filtros</p>",
        unsafe_allow_html=True,
    )

    seg_sel = st.selectbox(
        "¿Qué segmento?",
        ["Todos los segmentos"] + list(COLORES_SEGMENTO.keys()),
    )

    secciones_disp = sorted(s for s in df_act["seccion"].dropna().unique())
    sec_sel = st.selectbox(
        "¿Qué sección?",
        ["Todas las secciones"] + [str(int(s)) for s in secciones_disp],
    )

    semanas_disp = sorted(df_act["semana"].unique())
    sem_sel = st.multiselect("¿Qué semanas?", semanas_disp, default=semanas_disp)

    solo_cel = st.checkbox("Solo contactos con celular", value=False)

    st.markdown("<hr>", unsafe_allow_html=True)
    with st.expander("ℹ️ ¿Cómo funciona M5?"):
        st.markdown("""
**M5** segmenta los contactos del operativo por si conocen a Juan Carlos
y si votarían por él.

- ⭐ **Multiplicadores** → ya apoyan, activarlos como promotores
- 🌐 **Nodos Multinivel** → Multiplicadores en secciones prioritarias · candidatos a anfitrión de reunión por hogar
- 🎯 **Activación** → votarían pero aún no lo conocen bien
- 🤝 **Persuasión** → lo conocen pero no han decidido
- 👋 **Primer contacto** → no lo conocen, presentarlo

El Tab **Mensajes** usa IA para sugerir un SMS de 160 caracteres
calibrado para el grupo seleccionado.
        """)

    st.markdown(
        "<p style='font-size:0.75rem;color:#6b82a8;margin-top:8px;'>"
        "API key en <code style='color:#00c0ff;'>.streamlit/secrets.toml</code></p>",
        unsafe_allow_html=True,
    )


# ── APLICAR FILTROS ───────────────────────────────────────────────────────────
df_f = df_act.copy()
if seg_sel != "Todos los segmentos":
    df_f = df_f[df_f["segmento"] == seg_sel]
if sec_sel != "Todas las secciones":
    df_f = df_f[df_f["seccion"] == int(sec_sel)]
if sem_sel:
    df_f = df_f[df_f["semana"].isin(sem_sel)]
if solo_cel:
    df_f = df_f[df_f["tiene_cel"]]

total_base   = len(df_act)
total_filtro = len(df_f)
con_cel      = int(df_f["tiene_cel"].sum())
pct_cel      = con_cel / total_filtro * 100 if total_filtro > 0 else 0

sin_cobertura = [s for s in SECCIONES_PRIORITARIAS
                 if s not in df_raw["seccion"].dropna().unique()]
umbral        = max(int(total_base * 0.05), 1)
baja_cobertura = [s for s in SECCIONES_PRIORITARIAS
                  if s not in sin_cobertura
                  and len(df_raw[df_raw["seccion"] == s]) < umbral]
n_alertas = len(sin_cobertura) + len(baja_cobertura)

# ── HEADER ────────────────────────────────────────────────────────────────────
LOGO_B64_M5 = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAQABAADASIAAhEBAxEB/8QAHAABAQEAAwEBAQAAAAAAAAAAAAECBgcIAwUE/8QASBABAAIBAgMDBwkGBQIEBwEAAAECAwQFBgcREiExFyI1QVFhchMyUlRxgZGS0QgUQqGxwRUjYuHwY4IkMzSDFjdDRVWT8aL/xAAcAQEBAAIDAQEAAAAAAAAAAAAAAgEGBAUHAwj/xAA7EQEAAQMBAwgHBwQDAQEAAAAAAQIDBAUGEXESFSExNEFRUhMyU5GhsdEUFiIjYYHBB0Lh8CQzYnJD/9oADAMBAAIRAxEAPwDxkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH//2Q=="
st.markdown(f"""
<div style='background:linear-gradient(135deg,#004a6e 0%,#007cab 60%,#00c0ff 100%);
     border-radius:16px;padding:24px 32px;margin-bottom:24px;position:relative;overflow:hidden;'>
  <div style='position:absolute;top:-40px;right:-40px;width:140px;height:140px;
       border-radius:50%;background:rgba(255,255,255,0.05);'></div>
  <div style='display:flex;align-items:center;gap:18px;margin-bottom:10px;'>
    <img src="data:image/png;base64,{LOGO_B64_M5}"
         style='width:52px;height:52px;border-radius:10px;mix-blend-mode:lighten;flex-shrink:0;'>
    <div>
      <div style='font-size:0.70rem;font-weight:700;letter-spacing:0.13em;
           color:#00c0ff;text-transform:uppercase;margin-bottom:4px;'>
        Tu operación activada
      </div>
      <div style='font-size:1.45rem;font-weight:800;color:#ffffff;line-height:1.2;'>
        ¿A quién le mando el mensaje?
      </div>
    </div>
  </div>
  <div style='color:rgba(255,255,255,0.70);font-size:0.88rem;margin-left:70px;'>
    Base de contactos segmentada · El mensaje correcto, a la persona correcta · JCLY Morena 2026
  </div>
</div>
""", unsafe_allow_html=True)

# ── 3 TARJETAS ────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)

suffix = f" de {total_base:,}" if (
    seg_sel != "Todos los segmentos" or sec_sel != "Todas las secciones"
) else ""

with c1:
    alcance_estimado_m5 = int(total_filtro * 3.81)
    st.markdown(f"""
    <div class='metric-card'>
      <div class='metric-val'>{total_filtro:,}</div>
      <div class='metric-lbl'>Contactos accionables{suffix}</div>
      <div style='margin-top:8px;padding-top:8px;border-top:1px solid #e2e8f0;
           font-size:0.75rem;color:#0891b2;font-weight:600;'>
        ~{{alcance_estimado_m5:,}} personas · alcance estimado de hogar
      </div>
    </div>""", unsafe_allow_html=True)

with c2:
    col_cel = "green" if pct_cel >= 55 else "orange"
    st.markdown(f"""
    <div class='metric-card {col_cel}'>
      <div class='metric-val'>{con_cel:,}</div>
      <div class='metric-lbl'>Con celular válido · {pct_cel:.0f}%</div>
    </div>""", unsafe_allow_html=True)

with c3:
    col_al = "red" if n_alertas > 0 else "green"
    icono  = "🔴" if n_alertas > 0 else "✅"
    al_txt = f"{n_alertas} alerta{'s' if n_alertas != 1 else ''}" if n_alertas > 0 else "Sin alertas"
    st.markdown(f"""
    <div class='metric-card {col_al}'>
      <div class='metric-val'>{icono}</div>
      <div class='metric-lbl'>Prioritarias · {al_txt}</div>
    </div>""", unsafe_allow_html=True)

if sin_cobertura:
    st.markdown(
        f"<div class='alert-red'>🔴 <strong>Secciones prioritarias sin contactos:</strong> "
        f"{', '.join(str(s) for s in sin_cobertura)}<br>"
        f"<span style='font-size:0.83rem;color:#7f1d1d;'>"
        f"Enviar brigada urgente antes de cualquier campaña SMS.</span></div>",
        unsafe_allow_html=True,
    )
for s in baja_cobertura:
    n_s = len(df_raw[df_raw["seccion"] == s])
    st.markdown(
        f"<div class='alert-warn'>⚠️ <strong>Sección {s} (Prioritaria):</strong> "
        f"{n_s} contactos — mínimo recomendado: {umbral}</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── DISTRIBUCIÓN POR SEGMENTO ─────────────────────────────────────────────────
st.markdown("<div class='section-hdr'>Distribución por segmento</div>",
            unsafe_allow_html=True)

cols_seg = st.columns(5)
for i, (seg, color) in enumerate(COLORES_SEGMENTO.items()):
    n_seg   = len(df_f[df_f["segmento"] == seg])
    pct_seg = n_seg / total_filtro * 100 if total_filtro > 0 else 0
    cel_seg = int(df_f[df_f["segmento"] == seg]["tiene_cel"].sum())
    with cols_seg[i]:
        st.markdown(f"""
        <div style='background:{color}12;border:1px solid {color}40;
             border-radius:10px;padding:14px 16px;text-align:center;'>
          <div style='font-size:1.6rem;font-weight:800;color:{color};'>{n_seg:,}</div>
          <div style='font-size:0.85rem;font-weight:700;color:{color};margin:3px 0;'>
            {ICONOS_SEGMENTO[seg]} {seg}
          </div>
          <div style='font-size:0.75rem;color:#64748b;'>{pct_seg:.0f}% · {cel_seg} con cel.</div>
          <div style='font-size:0.72rem;color:#94a3b8;margin-top:6px;line-height:1.3;'>
            {INSTRUCCION_SEGMENTO[seg]}
          </div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_listas, tab_mensajes = st.tabs(["📋 Listas de contactos", "✉️ Generador de mensajes"])


# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — LISTAS
# ────────────────────────────────────────────────────────────────────────────
with tab_listas:

    if total_filtro == 0:
        st.warning("No hay contactos con los filtros seleccionados.")
    else:
        n_gps = int(df_f["gps_link"].notna().sum())
        st.markdown(
            f"**{total_filtro:,} contactos** · {con_cel:,} con celular "
            f"({pct_cel:.0f}%) · {n_gps:,} con ubicación GPS"
        )

        df_tabla = df_f[[
            "nombre_display", "celular_fmt", "seccion",
            "localidad_text", "segmento", "prob_grupo",
            "semana", "p15_3_texto_text", "atribs_debiles", "gps_link",
        ]].copy()
        df_tabla.columns = [
            "Nombre", "Celular", "Sección",
            "Localidad", "Segmento", "Problema principal",
            "Semana", "¿Buen candidato?", "Atributos a reforzar", "📍 Ubicación",
        ]
        df_tabla["Sección"] = df_tabla["Sección"].apply(
            lambda x: str(int(x)) if pd.notna(x) else "Sin sección"
        )

        st.dataframe(
            df_tabla,
            use_container_width=True,
            height=430,
            hide_index=True,
            column_config={
                "📍 Ubicación": st.column_config.LinkColumn(
                    "📍 Ubicación",
                    help="Abre Google Maps con la ubicación del contacto",
                    display_text="📍 Ver mapa",
                ),
            },
        )

        st.markdown("---")
        col_chk, col_btn = st.columns([2, 1])
        with col_chk:
            incluir_msg = st.checkbox(
                "Incluir 'Mensaje sugerido' en la exportación",
                value=False,
                help="Genera los mensajes en el Tab Mensajes primero.",
            )

        df_export = df_f[[
            "nombre_display", "celular_fmt", "seccion", "localidad_text",
            "segmento", "prob_grupo",
            "p2_1_autobinding_option_p2_1_texto",
            "semana", "p15_3_texto_text", "atribs_debiles", "gps_link",
        ]].copy()
        df_export.columns = [
            "nombre", "celular", "seccion", "localidad",
            "segmento", "problema_grupo", "problema_detalle",
            "semana_contacto", "es_buen_candidato",
            "atributos_a_reforzar", "gps_link",
        ]

        if incluir_msg and "mensajes_generados" in st.session_state:
            df_export["mensaje_sugerido"] = df_f["segmento"].map(
                st.session_state["mensajes_generados"]
            )

        csv_bytes      = df_export.to_csv(index=False).encode("utf-8-sig")
        fecha_hoy      = datetime.today().strftime("%Y%m%d")
        seg_tag        = seg_sel.replace(" ", "_").lower() if seg_sel != "Todos los segmentos" else "todos"
        sec_tag        = sec_sel if sec_sel != "Todas las secciones" else "todas"
        nombre_archivo = f"contactos_m5_{seg_tag}_sec{sec_tag}_{fecha_hoy}.csv"

        with col_btn:
            st.download_button(
                label=f"⬇️ Exportar {total_filtro:,} contactos",
                data=csv_bytes,
                file_name=nombre_archivo,
                mime="text/csv",
                use_container_width=True,
            )


# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — MENSAJES
# ────────────────────────────────────────────────────────────────────────────
with tab_mensajes:

    if "mensajes_generados" not in st.session_state:
        st.session_state["mensajes_generados"] = {}

    # seg_msg = None cuando el sidebar está en "Todos los segmentos"
    seg_msg    = seg_sel if seg_sel != "Todos los segmentos" else None
    modo_todos = seg_msg is None

    if total_filtro == 0:
        st.warning("No hay contactos con los filtros seleccionados.")
    else:
        perfil  = perfil_grupo(df_f)
        sec_txt = f"· Sección {sec_sel}" if sec_sel != "Todas las secciones" else "· Municipio completo"

        # ── Cabecera contextual ──────────────────────────────────────────────
        if modo_todos:
            st.markdown(f"""
            <div style='background:#f1f5f9;border-left:4px solid #64748b;
                 border-radius:8px;padding:14px 20px;margin-bottom:8px;'>
              <div style='font-size:1rem;font-weight:700;color:#334155;'>
                📢 Todos los segmentos · {total_filtro:,} contactos {sec_txt}
              </div>
              <div style='font-size:0.85rem;color:#64748b;margin-top:4px;'>
                Mensaje para audiencia mixta. El énfasis es el elemento clave
                para dar dirección al texto.
              </div>
            </div>""", unsafe_allow_html=True)

            st.markdown("""
            <div style='background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;
                 padding:10px 16px;margin-bottom:14px;'>
              ⚠️ <strong>Estás generando un mensaje para todos los contactos.</strong>
              Un mensaje sin segmentar no puede apelar al perfil de cada persona.
              Úsalo para eventos con fecha y lugar, noticias de último minuto
              o mensajes de cierre de campaña — donde <em>el contenido</em>
              es el protagonista, no el perfil del destinatario.<br>
              <span style='font-size:0.82rem;color:#92400e;'>
              💡 Para mejores resultados, escribe un énfasis concreto abajo.
              </span>
            </div>""", unsafe_allow_html=True)

        else:
            color = COLORES_SEGMENTO[seg_msg]
            icono = ICONOS_SEGMENTO[seg_msg]
            st.markdown(f"""
            <div style='background:{color}12;border-left:4px solid {color};
                 border-radius:8px;padding:14px 20px;margin-bottom:14px;'>
              <div style='font-size:1rem;font-weight:700;color:{color};'>
                {icono} {seg_msg} · {total_filtro:,} contactos {sec_txt}
              </div>
              <div style='font-size:0.85rem;color:#475569;margin-top:4px;'>
                {INSTRUCCION_SEGMENTO[seg_msg]}
              </div>
            </div>""", unsafe_allow_html=True)

        # ── Perfil del grupo ─────────────────────────────────────────────────
        cp1, cp2 = st.columns(2)
        with cp1:
            st.markdown("**🗺️ Problemas que más preocupan a este grupo**")
            probs_df = (
                df_f["prob_grupo"]
                .value_counts()
                .reset_index()
                .rename(columns={"prob_grupo": "Problemática", "count": "Contactos"})
            )
            probs_df["% del grupo"] = (
                probs_df["Contactos"] / total_filtro * 100
            ).round(1).astype(str) + "%"
            st.dataframe(probs_df.head(6), hide_index=True,
                         use_container_width=True, height=220)

        with cp2:
            st.markdown("**💡 Atributos con menor claridad (a reforzar)**")
            atrib_rows = []
            for nombre, (col_a, _) in ATRIBUTOS.items():
                if col_a in df_f.columns:
                    tot = df_f[col_a].notna().sum()
                    ns  = (df_f[col_a] == "No sabe (NO LEER)").sum()
                    pct = ns / tot * 100 if tot > 0 else 0
                    atrib_rows.append({
                        "Atributo": nombre,
                        "No sabe": int(ns),
                        "%": f"{pct:.0f}%",
                    })
            atrib_df = pd.DataFrame(atrib_rows).sort_values("No sabe", ascending=False)
            st.dataframe(atrib_df, hide_index=True,
                         use_container_width=True, height=220)

        # ── Generador ────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("<div class='section-hdr'>✨ Generar mensaje SMS</div>",
                    unsafe_allow_html=True)

        # Clave de sesión: "TODOS" para modo municipal, nombre del segmento para los demás
        key_sesion = seg_msg if seg_msg else "TODOS"
        # Clave corta para widgets (sin espacios ni emojis)
        key_w = (key_sesion.lower().replace(" ", "_")
                 .replace("é", "e").replace("ó", "o").replace("ú", "u"))

        if modo_todos:
            st.markdown("""
            <div style='background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;
                 padding:10px 16px;margin-bottom:12px;'>
              ⚠️ <strong>Mensaje para audiencia mixta.</strong>
              Úsalo para eventos, noticias de último minuto o cierre de campaña.
              <span style='font-size:0.82rem;color:#92400e;'>
              Se recomienda enfoque <strong>Neutro total</strong> para minimizar
              riesgo de bloqueo por carrier.
              </span>
            </div>""", unsafe_allow_html=True)
        else:
            st.caption(
                f"El mensaje se calibra para **{seg_msg}** · "
                f"Problema principal: **{perfil['prob_top']}** ({perfil['prob_pct']:.0f}%) · "
                f"{'Conoce a JCLY' if _CONOCE.get(seg_msg) else 'No conoce a JCLY'}"
            )

        # ── Controles de enfoque y tono ──────────────────────────────────────
        col_enf, col_ton = st.columns(2)

        _enfoques = ["Comunitario", "Híbrido", "Neutro total"]
        _tonos    = ["Motivacional/directo", "Cercano/coloquial"]
        _desc_enf = {
            "Comunitario":  "JCLY como vecino activo · máxima personalización",
            "Híbrido":      "Nombre propio sin cargo ni partido",
            "Neutro total": "Sin nombres · máxima seguridad carrier",
        }

        with col_enf:
            idx_default = _enfoques.index(_ENFOQUE_DEFAULT.get(seg_msg, "Neutro total"))
            enfoque_sel = st.radio(
                "📐 Enfoque",
                options=_enfoques,
                index=idx_default,
                key=f"enfoque_{key_w}",
                help=(
                    "**Comunitario**: JCLY aparece como vecino activo. "
                    "**Híbrido**: nombre propio sin cargo ni partido. "
                    "**Neutro total**: solo problema + acción colectiva, sin nombres ni partido."
                ),
            )
            st.caption(_desc_enf[enfoque_sel])

        with col_ton:
            tono_sel = st.radio(
                "🎙️ Tono",
                options=_tonos,
                index=0,
                key=f"tono_{key_w}",
                help=(
                    "**Motivacional**: imperativo directo, frases contundentes. "
                    "**Cercano/coloquial**: segunda persona, más conversacional."
                ),
            )

        enfasis_input = st.text_input(
            "🎯 Énfasis adicional (opcional)",
            placeholder=(
                "Ej: evento del sábado en la plaza, jornada de agua, "
                "reunión comunitaria este viernes…"
            ),
            key=f"enfasis_{key_w}",
            help="Si lo dejas vacío, el LLM ancla el mensaje en el problema principal del grupo.",
        )

        # ── Botón de generación ──────────────────────────────────────────────
        if st.button("⚡ Generar 3 variantes", type="primary",
                     key=f"btn_gen_{key_w}", use_container_width=True):
            with st.spinner("Generando mensajes…"):
                variantes = generar_variantes_sms(
                    segmento=seg_msg,
                    perfil=perfil,
                    enfoque=enfoque_sel,
                    tono=tono_sel,
                    enfasis=enfasis_input,
                )
                st.session_state[f"variantes_{key_w}"]  = variantes
                # Limpiar selección previa al regenerar
                st.session_state.pop(f"variante_sel_{key_w}", None)
                st.session_state["mensajes_generados"].pop(key_sesion, None)

        # ── Render de variantes ──────────────────────────────────────────────
        variantes_act = st.session_state.get(f"variantes_{key_w}", [])
        variante_conf = st.session_state.get(f"variante_sel_{key_w}", None)

        if variantes_act and variantes_act[0]:
            st.markdown("#### Variantes generadas")

            for i, variante in enumerate(variantes_act, 1):
                if not variante:
                    continue

                n_chars    = len(variante)
                es_sel     = variante_conf == variante
                color_brd  = "#1a7a4a" if es_sel else "#e2e8f0"
                bg_color   = "#f0fdf4" if es_sel else "#ffffff"
                sem_emoji  = "🟢" if n_chars <= 140 else ("🟡" if n_chars <= 160 else "🔴")
                sem_txt    = (
                    f"{n_chars}/160" if n_chars <= 160
                    else f"⚠️ {n_chars}/160 — excede límite"
                )

                st.markdown(f"""
                <div style='border:2px solid {color_brd};background:{bg_color};
                     border-radius:10px;padding:14px 18px;margin:8px 0;'>
                  <div style='font-size:0.78rem;font-weight:700;color:#64748b;
                       margin-bottom:6px;'>
                    {"✅ VARIANTE " + str(i) + " — SELECCIONADA" if es_sel
                     else "VARIANTE " + str(i)}
                  </div>
                  <div style='font-size:0.95rem;color:#1e293b;line-height:1.5;
                       margin-bottom:8px;'>
                    {variante}
                  </div>
                  <div style='font-size:0.75rem;color:#64748b;'>
                    {sem_emoji} {sem_txt} caracteres
                  </div>
                </div>""", unsafe_allow_html=True)

                col_usar, col_vacio = st.columns([1, 3])
                with col_usar:
                    if not es_sel:
                        if st.button(f"Usar variante {i}", key=f"usar_{key_w}_{i}",
                                     use_container_width=True):
                            st.session_state[f"variante_sel_{key_w}"]       = variante
                            st.session_state["mensajes_generados"][key_sesion] = variante
                            st.rerun()
                    else:
                        if st.button("Quitar selección", key=f"quitar_{key_w}_{i}",
                                     use_container_width=True):
                            st.session_state.pop(f"variante_sel_{key_w}", None)
                            st.session_state["mensajes_generados"].pop(key_sesion, None)
                            st.rerun()

            # ── Confirmación y métricas ──────────────────────────────────────
            if variante_conf:
                # Edición manual post-selección
                msg_edit = st.text_area(
                    "✏️ Edita el mensaje seleccionado antes de exportar (máx. 160 caracteres)",
                    value=variante_conf,
                    height=100,
                    max_chars=160,
                    key=f"edit_{key_w}",
                )
                chars_rest = 160 - len(msg_edit)
                col_c      = "#16a34a" if chars_rest >= 0 else "#dc2626"
                st.markdown(
                    f"<span style='color:{col_c};font-size:0.8rem;'>"
                    f"{'✅' if chars_rest >= 0 else '❌'} {len(msg_edit)}/160 caracteres "
                    f"({'quedan' if chars_rest >= 0 else 'excede por'} {abs(chars_rest)})"
                    f"</span>",
                    unsafe_allow_html=True,
                )
                if msg_edit != variante_conf:
                    st.session_state[f"variante_sel_{key_w}"]       = msg_edit
                    st.session_state["mensajes_generados"][key_sesion] = msg_edit

                st.markdown("---")
                ca, cb, cc = st.columns(3)
                with ca:
                    st.metric("Recibirán este SMS", f"{con_cel:,}")
                with cb:
                    st.metric("Audiencia", seg_msg if seg_msg else "Todos los segmentos")
                with cc:
                    st.metric("Problema cubierto", perfil["prob_top"])

                st.info(
                    "💾 Variante guardada. Ve al **Tab Listas** y activa "
                    "*'Incluir Mensaje sugerido en la exportación'* "
                    "para que el CSV incluya este texto para cada contacto."
                )