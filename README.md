# PIE Zacatlán — Versión Demo / Vitrina

Repositorio de demostración del Sistema de Inteligencia Electoral.
**No modificar el repositorio productivo** (`pie_zacatlan_2027`).

## Diferencias con el repo productivo

| | `pie_zacatlan_2027` | `pie_zacatlan_demo` |
|---|---|---|
| Uso | Operativo de campaña | Demo para stakeholders |
| Módulos | Acceso completo | Home libre + módulos bloqueados |
| URL | pie-zacatlan2027.streamlit.app | pie-zacatlan-demo.streamlit.app |
| Actualización | Sprint activo | Manual, controlada |

## Cómo funciona el bloqueo

`demo_mode.py` en la raíz controla todo. Cada módulo lo importa con 2 líneas:

```python
from demo_mode import check_demo_mode
check_demo_mode()
```

- **Sin contraseña** → banner de bloqueo + contenido difuminado
- **Con contraseña correcta** → acceso completo (para presentaciones en vivo)

## Setup

### 1. Clonar y configurar
```bash
git clone https://github.com/Omartg04/pie_zacatlan_demo
cd pie_zacatlan_demo
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Editar secrets.toml con contraseña real y API key
```

### 2. Copiar archivos de datos
```bash
# Copiar desde repo productivo (sin raw/induccion*.csv)
cp ../pie_zacatlan_2027/data/*.csv data/
cp ../pie_zacatlan_2027/data/*.geojson data/
```

### 3. Deploy en Streamlit Cloud
- Repositorio: `pie_zacatlan_demo`
- Rama: `main`
- Archivo principal: `Home.py`
- Secrets: `DEMO_PASSWORD` + `ANTHROPIC_API_KEY`

## Actualizar el demo tras cambios en productivo

```bash
# Copiar solo Home.py si hubo cambios (no toca el bloqueo)
cp ../pie_zacatlan_2027/Home.py Home.py

# Para módulos: copiar y re-insertar las 2 líneas de demo_mode
# Las 2 líneas van siempre después del bloque st.set_page_config()
```

## ⚠️ NO subir al repo
- `raw/` — datos personales de campo
- `.streamlit/secrets.toml` — credenciales reales
