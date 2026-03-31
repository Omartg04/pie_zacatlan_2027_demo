import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import os
from io import StringIO


# ── CSS del sistema PIE ───────────────────────────────────────────────────────

# ── Demo mode — no modificar ────────────────────────────────────────────────
from demo_mode import check_demo_mode
check_demo_mode()

st.markdown("""
<style>
  /* Header gradiente */
  .pie-header {
    background: linear-gradient(135deg, #004a6e 0%, #007cab 100%);
    padding: 1.4rem 2rem;
    border-radius: 10px;
    margin-bottom: 1.2rem;
  }
  .pie-header h1 { color: #ffffff; font-size: 1.6rem; font-weight: 700; margin: 0; }
  .pie-header p  { color: #93c5fd; font-size: 0.95rem; margin: 0.2rem 0 0; }

  /* Tarjetas métricas */
  .metric-card {
    background: #f8fafc;
    border-left: 4px solid #2563eb;
    border-radius: 8px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.5rem;
  }
  .metric-card.verde  { border-left-color: #2a9d8f; }
  .metric-card.naranja{ border-left-color: #f4a261; }
  .metric-card.rojo   { border-left-color: #e63946; }
  .metric-card .val   { font-size: 1.9rem; font-weight: 700; color: #1e293b; line-height: 1; }
  .metric-card .lbl   { font-size: 0.78rem; color: #64748b; margin-top: 0.2rem; }
  .metric-card .sub   { font-size: 0.75rem; color: #94a3b8; margin-top: 0.1rem; }

  /* Separadores de sección */
  .sec-title {
    font-size: 1.05rem; font-weight: 700; color: #1e293b;
    border-left: 4px solid #e63946; padding-left: 10px; border-bottom: none;
    padding-bottom: 0.4rem; margin: 1.2rem 0 0.8rem;
  }

  /* Alerta roja */
  .alerta-roja {
    background: #fde8ea; border: 1px solid #e63946;
    border-radius: 8px; padding: 0.7rem 1rem; margin-bottom: 0.8rem;
    font-size: 0.88rem; color: #7f1d1d;
  }
  /* Alerta ámbar */
  .alerta-ambar {
    background: #fef3e8; border: 1px solid #f4a261;
    border-radius: 8px; padding: 0.7rem 1rem; margin-bottom: 0.8rem;
    font-size: 0.88rem; color: #78350f;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background-color: #004a6e !important;
  }
  [data-testid="stSidebar"] * { color: #e8edf5 !important; }
  [data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: #243058 !important;
    border: 1px solid #3d5a99 !important;
  }

  /* Footer */
  .pie-footer {
    font-size: 0.72rem; color: #94a3b8; text-align: center;
    margin-top: 2rem; padding-top: 0.8rem;
    border-top: 1px solid #e2e8f0;
  }

  /* Árbol nodo */
  .nodo-origen { background:#dbeafe; border-radius:6px; padding:4px 8px; font-size:0.8rem; }
  .nodo-hijo   { background:#dcfce7; border-radius:6px; padding:4px 8px; font-size:0.8rem; }
</style>
""", unsafe_allow_html=True)

# ── Carga de datos ────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, '..', 'data')

@st.cache_data
def cargar_spt():
    try:
        return pd.read_csv(os.path.join(DATA, 'spt_secciones_1.csv'))
    except Exception:
        return pd.DataFrame()

@st.cache_data
def cargar_reuniones(contenido):
    return pd.read_csv(StringIO(contenido))

@st.cache_data
def cargar_asistentes(contenido):
    return pd.read_csv(StringIO(contenido))

spt_df = cargar_spt()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏘️ Estrategia Multinivel")
    st.markdown("*¿Quién está multiplicando el mensaje?*")
    st.markdown("---")

    st.markdown("**📂 Cargar datos de campo**")
    f_reuniones = st.file_uploader("CSV de reuniones (Bubble)", type="csv", key="reu")
    f_asistentes = st.file_uploader("CSV de asistentes (Bubble)", type="csv", key="asi")

    st.markdown("---")
    st.markdown("**🔍 Filtros**")

    ambito_opts = ["Todos", "Urbano", "Rural Marginal", "Rural Media"]
    filtro_ambito = st.selectbox("Ámbito territorial", ambito_opts)

    st.markdown("---")
    with st.expander("ℹ️ ¿Cómo funciona esto?"):
        st.markdown("""
**Estrategia Multinivel** convierte a cada simpatizante en un nodo de expansión.

- Cada reunión registra anfitrión, asistentes y necesidades de la colonia
- El sistema muestra cobertura real vs objetivo por sección
- El árbol muestra quién originó cada reunión
- Los asistentes se integran al **M5** como nuevos contactos

**Fuente de datos:** exportación CSV desde Bubble (mismo flujo que encuesta)
        """)

# ── Datos demo si no se carga archivo ────────────────────────────────────────
DEMO_WARNING = False

if f_reuniones is not None:
    df_r = cargar_reuniones(f_reuniones.getvalue().decode('utf-8-sig'))
else:
    try:
        df_r = pd.read_csv(os.path.join(DATA, 'm6_reuniones.csv'))
    except Exception:
        DEMO_WARNING = True
        # Datos mínimos embebidos para que la página no falle
        df_r = pd.DataFrame({
            'id_reunion_text': ['REU-2486-001','REU-2486-002','REU-2471-001','REU-2489-001','REU-2488-001'],
            'fecha_reunion_date': ['2026-02-15 18:00','2026-02-22 19:00','2026-02-18 18:30','2026-02-20 17:00','2026-03-01 18:00'],
            'seccion_electoral_text': [2486,2486,2471,2489,2488],
            'localidad_text': ['ZACATLAN','ZACATLAN','AYEHUALULCO','ZACATLAN','XONOTLA'],
            'colonia_text': ['Centro','Santa Julia','Centro','Centro','Xonotla Centro'],
            'latitud_text': [19.935,19.932,19.980,19.915,19.870],
            'longitud_text': [-97.960,-97.963,-97.940,-97.970,-97.920],
            'nombre_anfitrion_text': ['María García','José Martínez','Ana Pérez','Carlos Hernández','Rosa López'],
            'celular_anfitrion_number': ['7711000001','7711000002','7711000003','7711000004','7711000005'],
            'id_reunion_origen_text': [None, 'REU-2486-001', None, 'REU-2471-001', None],
            'nombre_promotor_text': ['Omar García','Omar García','Daniela Flores','Luis Pérez','Andrea Moreno'],
            'num_asistentes_number': [12,10,11,13,8],
            'material_entregado_boolean': [True,True,True,False,True],
            'necesidad_seguridad_text': ['Robos frecuentes',None,'No hay patrullaje',None,'Inseguridad en caminos'],
            'necesidad_economia_text': ['Falta empleo jóvenes','No hay apoyos','Precios del campo',None,None],
            'necesidad_pavimento_text': ['Baches en la colonia',None,None,'Calle sin pavimentar',None],
            'necesidad_alumbrado_text': [None,'Calles sin luz',None,None,'Postes caídos'],
            'necesidad_salud_text': [None,None,'Centro de salud cierra temprano',None,None],
            'necesidad_educacion_text': [None,None,None,'Sin transporte escolar',None],
            'necesidad_otro_text': [None,None,None,None,'Río se desborda'],
            'ambito': ['Urbano','Urbano','Rural Marginal','Rural Marginal','Rural Marginal'],
            'observaciones_text': ['Muy buena participación',None,'Comunidad interesada','',None],
        })

if f_asistentes is not None:
    df_a = cargar_asistentes(f_asistentes.getvalue().decode('utf-8-sig'))
else:
    try:
        df_a = pd.read_csv(os.path.join(DATA, 'm6_asistentes.csv'))
    except Exception:
        df_a = pd.DataFrame({
            'id_reunion_text': ['REU-2486-001']*12 + ['REU-2486-002']*10 + ['REU-2471-001']*11 + ['REU-2489-001']*13 + ['REU-2488-001']*8,
            'seccion_electoral_text': [2486]*12 + [2486]*10 + [2471]*11 + [2489]*13 + [2488]*8,
            'nombre_asistente_text': [f'Persona {i}' for i in range(54)],
            'celular_asistente_number': [f'771100{i:04d}' for i in range(54)],
            'quiere_ser_anfitrion_boolean': [True,False,True,False,False,True,False,False,True,False,False,False,
                                              True,False,False,True,False,True,False,False,
                                              False,True,False,False,True,False,False,False,False,True,False,
                                              True,False,False,True,False,False,True,False,False,False,False,False,False,
                                              False,True,False,False,False,False,False,False,False,False],
            'fecha_proxima_reunion_date': [None]*54,
        })

# Aplicar filtro de ámbito
if filtro_ambito != "Todos" and 'ambito' in df_r.columns:
    df_r_f = df_r[df_r['ambito'] == filtro_ambito].copy()
else:
    df_r_f = df_r.copy()

df_r['fecha_reunion_date'] = pd.to_datetime(df_r['fecha_reunion_date'], errors='coerce')

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="pie-header">
  <h1>🏘️ M6 · Estrategia Multinivel</h1>
  <p>¿Quién está multiplicando el mensaje? · Cobertura de reuniones por hogar · Red de expansión · Necesidades del territorio</p>
</div>
""", unsafe_allow_html=True)

if DEMO_WARNING:
    st.markdown("""
    <div class="alerta-ambar">
    ⚠️ <strong>Modo demostración</strong> — Sube los CSV de reuniones y asistentes desde el panel lateral para ver datos reales.
    </div>
    """, unsafe_allow_html=True)

# ── MÉTRICAS PRINCIPALES ─────────────────────────────────────────────────────
total_reuniones   = len(df_r_f)
total_personas    = df_r_f['num_asistentes_number'].sum() if 'num_asistentes_number' in df_r_f.columns else 0
secciones_cubiertas = df_r_f['seccion_electoral_text'].nunique() if len(df_r_f) > 0 else 0
secciones_totales = 33
nuevos_anfitriones = df_a[df_a['quiere_ser_anfitrion_boolean'] == True].shape[0] if len(df_a) > 0 else 0
reuniones_en_arbol = df_r['id_reunion_origen_text'].notna().sum() if 'id_reunion_origen_text' in df_r.columns else 0

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""
    <div class="metric-card verde">
      <div class="val">{total_reuniones}</div>
      <div class="lbl">Reuniones realizadas</div>
      <div class="sub">desde inicio de estrategia</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card verde">
      <div class="val">{int(total_personas):,}</div>
      <div class="lbl">Personas alcanzadas</div>
      <div class="sub">sin brigadas presenciales</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-card">
      <div class="val">{secciones_cubiertas} / {secciones_totales}</div>
      <div class="lbl">Secciones con reuniones</div>
      <div class="sub">del total del municipio</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-card naranja">
      <div class="val">{nuevos_anfitriones}</div>
      <div class="lbl">Nuevos anfitriones agendados</div>
      <div class="sub">próximas reuniones confirmadas</div>
    </div>""", unsafe_allow_html=True)
with c5:
    st.markdown(f"""
    <div class="metric-card">
      <div class="val">{reuniones_en_arbol}</div>
      <div class="lbl">Reuniones generadas por la red</div>
      <div class="sub">originadas por otro asistente</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── MAPA DE COBERTURA ─────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">📍 Cobertura de reuniones por sección</div>', unsafe_allow_html=True)

col_mapa, col_detalle = st.columns([2, 1])

with col_mapa:
    # Agregar por sección
    if len(df_r_f) > 0:
        resumen_sec = df_r_f.groupby('seccion_electoral_text').agg(
            reuniones=('id_reunion_text', 'count'),
            personas=('num_asistentes_number', 'sum'),
            lat=('latitud_text', 'mean'),
            lon=('longitud_text', 'mean'),
        ).reset_index()
    else:
        resumen_sec = pd.DataFrame(columns=['seccion_electoral_text','reuniones','personas','lat','lon'])

    # Merge con SPT
    if len(spt_df) > 0:
        resumen_sec = resumen_sec.merge(
            spt_df[['seccion','SPT','clasificacion','ambito_iter']],
            left_on='seccion_electoral_text', right_on='seccion', how='left'
        )
    else:
        resumen_sec['SPT'] = 50
        resumen_sec['clasificacion'] = 'Consolidación'

    m = folium.Map(location=[19.935, -97.960], zoom_start=11,
                   tiles='CartoDB positron')

    # ── Capa 1: Coroplético SPT (base territorial, igual que M1) ────────────
    SPT_COLORES = {
        'Prioritaria':   {'fill': '#e63946', 'label': 'Prioritaria (SPT > 70)'},
        'Consolidacion': {'fill': '#f4a261', 'label': 'Consolidación'},
        'Consolidación': {'fill': '#f4a261', 'label': 'Consolidación'},
        'Mantenimiento': {'fill': '#2a9d8f', 'label': 'Mantenimiento'},
    }

    geojson_path = os.path.join(DATA, 'zacatlan_secciones.geojson')
    if os.path.exists(geojson_path) and len(spt_df) > 0:
        import json
        with open(geojson_path) as f:
            geojson_data = json.load(f)

        # Mapa de sección → clasificación y SPT
        spt_lookup = spt_df.set_index('seccion')[['SPT','clasificacion','tactica_recomendada','ambito_iter']].to_dict('index')

        def spt_style(feature):
            sec = int(feature['properties'].get('SECCION', 0))
            info = spt_lookup.get(sec, {})
            clasif = str(info.get('clasificacion', ''))
            color = SPT_COLORES.get(clasif, {'fill': '#94a3b8'})['fill']
            return {
                'fillColor': color,
                'color':     '#ffffff',
                'weight':    1.2,
                'fillOpacity': 0.45,
            }

        def spt_highlight(feature):
            return {'weight': 2.5, 'color': '#1e293b', 'fillOpacity': 0.65}

        def spt_tooltip(feature):
            sec = int(feature['properties'].get('SECCION', 0))
            info = spt_lookup.get(sec, {})
            spt_val = info.get('SPT', '—')
            clasif  = info.get('clasificacion', '—')
            tactica = info.get('tactica_recomendada', '—')
            ambito  = info.get('ambito_iter', '—')
            # Reuniones en esta sección
            reu_sec = resumen_sec[resumen_sec['seccion_electoral_text'] == sec]
            n_reu   = int(reu_sec['reuniones'].values[0]) if len(reu_sec) > 0 else 0
            n_pers  = int(reu_sec['personas'].values[0])  if len(reu_sec) > 0 else 0
            badge   = f"🏘️ {n_reu} reuniones · {n_pers} personas" if n_reu > 0 else "⬜ Sin reuniones aún"
            return folium.Tooltip(f"""
                <div style='font-family:sans-serif;font-size:13px;min-width:180px'>
                  <b>Sección {sec}</b> &nbsp;
                  <span style='background:{"#e63946" if "Prior" in clasif else "#f4a261" if "Consol" in clasif else "#2a9d8f"};
                        color:white;border-radius:4px;padding:1px 7px;font-size:11px'>{clasif}</span><br>
                  <span style='color:#64748b;font-size:11px'>{ambito}</span><br><br>
                  📊 SPT <b>{spt_val if spt_val == "—" else f"{spt_val:.1f}"}</b><br>
                  🎯 {tactica}<br><br>
                  {badge}
                </div>""", sticky=True)

        folium.GeoJson(
            geojson_data,
            style_function=spt_style,
            highlight_function=spt_highlight,
            tooltip=folium.GeoJsonTooltip(
                fields=['SECCION'],
                aliases=['Sección:'],
                localize=True,
            ),
            name='SPT por sección',
        ).add_to(m)

    # ── Capa 2: Círculos de reuniones (encima del coroplético) ───────────────
    COLOR_MAP = {
        'Prioritaria':   '#e63946',
        'Consolidacion': '#f4a261',
        'Consolidación': '#f4a261',
        'Mantenimiento': '#2a9d8f',
    }

    for _, row in resumen_sec.iterrows():
        if pd.isna(row['lat']): continue
        color = COLOR_MAP.get(str(row.get('clasificacion','')), '#2563eb')
        radio = 9 + row['reuniones'] * 5

        popup_html = f"""
        <div style='font-family:sans-serif;font-size:13px;min-width:170px'>
          <b>Sección {int(row['seccion_electoral_text'])}</b><br>
          <span style='color:#64748b'>{row.get('ambito_iter','')}</span><br><br>
          🏘️ <b>{int(row['reuniones'])}</b> reuniones realizadas<br>
          👥 <b>{int(row['personas'])}</b> personas alcanzadas<br>
          📊 SPT: <b>{row.get('SPT', '—') if row.get('SPT','—') == '—' else f"{row.get('SPT',0):.1f}"}</b>
        </div>"""

        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=radio,
            color='#ffffff',
            weight=2,
            fill=True, fill_color=color, fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=230),
            tooltip=f"§{int(row['seccion_electoral_text'])} · {int(row['reuniones'])} reuniones · {int(row['personas'])} personas",
        ).add_to(m)

    # ── Capa 3: Nodos Multinivel desde session_state (M5) ───────────────────
    nodos_ss    = st.session_state.get("nodos_multinivel", None)
    tiene_nodos = nodos_ss is not None and len(nodos_ss) > 0

    if tiene_nodos:
        for nodo in nodos_ss:
            sec_n = nodo.get("seccion")
            n_n   = nodo.get("n_nodos", 0)
            cel_n = int(nodo.get("n_con_cel", 0))
            pct_n = nodo.get("pct_cel", 0)

            coords = resumen_sec[resumen_sec["seccion_electoral_text"] == sec_n]
            if len(coords) > 0 and not pd.isna(coords.iloc[0]["lat"]):
                lat_n = coords.iloc[0]["lat"] + 0.005
                lon_n = coords.iloc[0]["lon"] + 0.005
            else:
                lat_n = 19.935 + (int(sec_n or 0) % 10) * 0.003
                lon_n = -97.960 + (int(sec_n or 0) % 7) * 0.004

            reu_en_sec = len(df_r_f[df_r_f["seccion_electoral_text"] == sec_n]) if len(df_r_f) > 0 else 0
            estado_txt = (
                f"{reu_en_sec} reunion(es) activa(s)"
                if reu_en_sec > 0
                else "Sin reuniones — potencial no activado"
            )
            estado_color = "#2a9d8f" if reu_en_sec > 0 else "#e63946"

            popup_nodo = (
                "<div style='font-family:sans-serif;font-size:13px;min-width:190px'>"
                f"<b>Nodos Multinivel &middot; &sect;{sec_n}</b><br><br>"
                f"<b>{n_n}</b> nodos disponibles<br>"
                f"<b>{cel_n}</b> con celular ({pct_n:.0f}%)<br><br>"
                f"<span style='color:{estado_color};font-weight:700;'>{estado_txt}</span><br><br>"
                "<span style='font-size:11px;color:#64748b;'>"
                "Multiplicadores en seccion prioritaria.<br>"
                "Contactar para agendar reunion por hogar."
                "</span></div>"
            )

            folium.RegularPolygonMarker(
                location=[lat_n, lon_n],
                number_of_sides=4,
                radius=8,
                color="#ffffff",
                weight=2,
                fill_color="#7c3aed",
                fill_opacity=0.9,
                rotation=45,
                popup=folium.Popup(popup_nodo, max_width=230),
                tooltip=f"Nodos {sec_n}: {n_n} disponibles | {'activo' if reu_en_sec > 0 else 'sin activar'}",
            ).add_to(m)

    # ── Leyenda ──────────────────────────────────────────────────────────────
    nodos_legend_html = (
        "<br><b style='font-size:13px'>Nodos Multinivel (M5)</b><br>"
        "<span style='color:#7c3aed'>&#9670;</span> Nodo disponible para activar"
        if tiene_nodos else
        "<br><span style='color:#94a3b8;font-size:11px;font-style:italic;'>"
        "Carga el operativo en M5 para ver los Nodos Multinivel</span>"
    )

    legend_html = (
        "<div style='position:fixed;bottom:30px;left:30px;z-index:1000;"
        "background:white;padding:12px 16px;border-radius:8px;"
        "border:1px solid #e2e8f0;font-size:12px;font-family:sans-serif;"
        "box-shadow:0 2px 8px rgba(0,0,0,0.08)'>"
        "<b style='font-size:13px'>Clasificacion SPT</b><br>"
        "<span style='color:#e63946'>&#9632;</span> Prioritaria (SPT &gt; 70)<br>"
        "<span style='color:#f4a261'>&#9632;</span> Consolidacion<br>"
        "<span style='color:#2a9d8f'>&#9632;</span> Mantenimiento<br><br>"
        "<b style='font-size:13px'>Reuniones realizadas</b><br>"
        "<span style='color:#1e293b'>&#9679;</span> Circulo = reuniones realizadas<br>"
        "<i style='color:#94a3b8'>Tamano proporcional al numero</i>"
        + nodos_legend_html +
        "</div>"
    )
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=None, height=460, returned_objects=[])

with col_detalle:
    st.markdown("**Reuniones por sección**")
    if len(resumen_sec) > 0:
        tabla = resumen_sec[['seccion_electoral_text','reuniones','personas']].copy()
        tabla.columns = ['Sección','Reuniones','Personas']
        tabla = tabla.sort_values('Reuniones', ascending=False).reset_index(drop=True)

        # Colorear filas
        def highlight(row):
            sec = row['Sección']
            spt_val = spt_df[spt_df['seccion'] == sec]['SPT'].values
            spt_v = spt_val[0] if len(spt_val) > 0 else 50
            clasif = spt_df[spt_df['seccion'] == sec]['clasificacion'].values
            c = clasif[0] if len(clasif) > 0 else ''
            bg = {'Prioritaria':'#fde8ea','Consolidacion':'#fef3e8','Consolidación':'#fef3e8','Mantenimiento':'#e8f5f3'}.get(c,'')
            return [f'background-color:{bg}']*3 if bg else ['']*3

        st.dataframe(
            tabla.style.apply(highlight, axis=1),
            hide_index=True, height=300,
            use_container_width=True
        )
    else:
        st.info("Sube el CSV de reuniones para ver el detalle por sección.")

    # Secciones sin reuniones (prioritarias)
    if len(spt_df) > 0:
        prioritarias = spt_df[spt_df['SPT'] >= 70]['seccion'].tolist()
        cubiertas_set = set(df_r_f['seccion_electoral_text'].tolist()) if len(df_r_f) > 0 else set()
        sin_cobertura = [s for s in prioritarias if s not in cubiertas_set]
        if sin_cobertura:
            st.markdown(f"""
            <div class="alerta-roja">
            ⚠️ <b>Secciones PRIORITARIAS sin reuniones:</b><br>
            {', '.join([f'§{s}' for s in sin_cobertura])}
            </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── RED DE EXPANSIÓN — métricas simplificadas ────────────────────────────────
st.markdown('<div class="sec-title">🌳 Red de expansión — ¿cuánto está creciendo sola la red?</div>',
            unsafe_allow_html=True)

if 'id_reunion_origen_text' in df_r.columns:
    raiz_count = int(df_r['id_reunion_origen_text'].isna().sum())
    gen_count  = int(df_r['id_reunion_origen_text'].notna().sum())
    factor     = round(gen_count / raiz_count, 1) if raiz_count > 0 else 0
    total_red  = raiz_count + gen_count
else:
    raiz_count, gen_count, factor, total_red = 0, 0, 0, 0

re1, re2, re3, re4 = st.columns(4)
with re1:
    st.markdown(f"""
    <div class="metric-card">
      <div class="val">{raiz_count}</div>
      <div class="lbl">Reuniones de primer contacto</div>
      <div class="sub">originadas directamente por el equipo</div>
    </div>""", unsafe_allow_html=True)
with re2:
    st.markdown(f"""
    <div class="metric-card verde">
      <div class="val">{gen_count}</div>
      <div class="lbl">Reuniones generadas por la red</div>
      <div class="sub">originadas por asistentes de otras reuniones</div>
    </div>""", unsafe_allow_html=True)
with re3:
    st.markdown(f"""
    <div class="metric-card naranja">
      <div class="val">{factor}×</div>
      <div class="lbl">Factor de expansión</div>
      <div class="sub">reuniones generadas por cada reunión raíz</div>
    </div>""", unsafe_allow_html=True)
with re4:
    pct_red = round(gen_count / total_red * 100, 1) if total_red > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
      <div class="val">{pct_red}%</div>
      <div class="lbl">Del total generado por la red</div>
      <div class="sub">sin intervención directa del equipo</div>
    </div>""", unsafe_allow_html=True)

# Tabla colapsada con detalle para equipo técnico
if gen_count > 0:
    with st.expander("📋 Ver detalle de reuniones generadas por la red"):
        cols_arbol = [c for c in ['id_reunion_text','id_reunion_origen_text',
                                   'seccion_electoral_text','nombre_anfitrion_text',
                                   'fecha_reunion_date','num_asistentes_number']
                      if c in df_r.columns]
        df_gen = df_r[df_r['id_reunion_origen_text'].notna()][cols_arbol].copy()
        df_gen.columns = ['Reunión','Originada por','Sección','Anfitrión','Fecha','Asistentes'][:len(cols_arbol)]
        st.dataframe(df_gen, hide_index=True, use_container_width=True)

st.markdown("---")

# ── CUADRO DE NECESIDADES ─────────────────────────────────────────────────────
st.markdown('<div class="sec-title">📋 Cuadro de necesidades — ¿qué está pidiendo el territorio?</div>',
            unsafe_allow_html=True)

TEMAS = {
    'necesidad_seguridad_text':  ('🔒 Seguridad',     '#dc2626'),
    'necesidad_economia_text':   ('💼 Economía',       '#d97706'),
    'necesidad_pavimento_text':  ('🛣️ Pavimento',      '#7c3aed'),
    'necesidad_alumbrado_text':  ('💡 Alumbrado',      '#0891b2'),
    'necesidad_salud_text':      ('🏥 Salud',          '#059669'),
    'necesidad_educacion_text':  ('🎓 Educación',      '#2563eb'),
    'necesidad_otro_text':       ('📌 Otro',           '#64748b'),
}

# Conteo de menciones por tema
conteos = {}
for col, (label, color) in TEMAS.items():
    if col in df_r_f.columns:
        conteos[label] = df_r_f[col].notna().sum()
    else:
        conteos[label] = 0

col_nec1, col_nec2 = st.columns([1, 2])

with col_nec1:
    df_nec = pd.DataFrame(list(conteos.items()), columns=['Tema', 'Menciones'])
    df_nec = df_nec.sort_values('Menciones', ascending=True)
    colors = [TEMAS[k][1] for k in TEMAS.keys() if TEMAS[k][0] in df_nec['Tema'].values]

    fig_nec = go.Figure(go.Bar(
        x=df_nec['Menciones'],
        y=df_nec['Tema'],
        orientation='h',
        marker_color=[TEMAS[k][1] for k, (lbl, c) in TEMAS.items() if lbl in df_nec['Tema'].values],
        text=df_nec['Menciones'],
        textposition='outside',
    ))
    fig_nec.update_layout(
        height=280,
        margin=dict(l=0, r=30, t=10, b=10),
        xaxis_title='Reuniones con esta necesidad',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#e2e8f0'),
        font=dict(family='sans-serif', size=12, color='#1e293b'),
    )
    st.plotly_chart(fig_nec, use_container_width=True)

with col_nec2:
    st.markdown("**Necesidades más mencionadas por sección**")

    # Tabla resumen: sección × tema con las necesidades reales
    if len(df_r_f) > 0:
        rows_nec = []
        for _, row in df_r_f.iterrows():
            sec = int(row['seccion_electoral_text'])
            loc = row.get('localidad_text', '')
            for col, (label, color) in TEMAS.items():
                if col in df_r_f.columns and pd.notna(row.get(col)):
                    rows_nec.append({
                        'Sección': sec,
                        'Localidad': loc,
                        'Tema': label,
                        'Necesidad': row[col],
                    })
        if rows_nec:
            df_tabla_nec = pd.DataFrame(rows_nec).drop_duplicates()
            st.dataframe(
                df_tabla_nec.sort_values(['Sección','Tema']),
                hide_index=True,
                height=260,
                use_container_width=True,
                column_config={
                    'Sección': st.column_config.NumberColumn(format="%d"),
                    'Necesidad': st.column_config.TextColumn(width='large'),
                }
            )
        else:
            st.info("Sin necesidades registradas en el filtro actual.")
    else:
        st.info("Sube el CSV de reuniones para ver el cuadro de necesidades.")

st.markdown("---")

# ── PANEL DE SEGUIMIENTO DE ASISTENTES ───────────────────────────────────────
st.markdown('<div class="sec-title">👥 Seguimiento de asistentes — próximos anfitriones</div>',
            unsafe_allow_html=True)

if len(df_a) > 0:
    anfitriones_prox = df_a[df_a['quiere_ser_anfitrion_boolean'] == True].copy()

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown(f"""
        <div class="metric-card verde">
          <div class="val">{len(anfitriones_prox)}</div>
          <div class="lbl">Asistentes que quieren ser anfitriones</div>
          <div class="sub">potencial de expansión inmediato</div>
        </div>""", unsafe_allow_html=True)
    with col_s2:
        con_fecha = anfitriones_prox['fecha_proxima_reunion_date'].notna().sum() if 'fecha_proxima_reunion_date' in anfitriones_prox.columns else 0
        st.markdown(f"""
        <div class="metric-card naranja">
          <div class="val">{con_fecha}</div>
          <div class="lbl">Con fecha agendada</div>
          <div class="sub">reuniones confirmadas en pipeline</div>
        </div>""", unsafe_allow_html=True)
    with col_s3:
        total_asis = len(df_a)
        pct = round(len(anfitriones_prox) / total_asis * 100, 1) if total_asis > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
          <div class="val">{pct}%</div>
          <div class="lbl">Tasa de conversión a anfitrión</div>
          <div class="sub">de asistente a multiplicador</div>
        </div>""", unsafe_allow_html=True)

    with st.expander("📋 Ver lista completa de próximos anfitriones"):
        cols_show = [c for c in ['seccion_electoral_text','nombre_asistente_text',
                                  'celular_asistente_number','fecha_proxima_reunion_date']
                     if c in anfitriones_prox.columns]
        df_show = anfitriones_prox[cols_show].copy()
        df_show.columns = ['Sección','Nombre','Celular','Fecha próxima reunión'][:len(cols_show)]
        st.dataframe(df_show, hide_index=True, use_container_width=True)

        # Botón exportar para M5
        csv_exp = df_show.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "⬇️ Exportar para M5 (CSV)",
            data=csv_exp,
            file_name="m6_proximos_anfitriones.csv",
            mime="text/csv",
        )
else:
    st.info("Sube el CSV de asistentes para ver el seguimiento.")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="pie-footer">
  Inteligencia Electoral Zacatlán · JCLY Morena 2026 · Confidencial · Marzo 2026
</div>
""", unsafe_allow_html=True)