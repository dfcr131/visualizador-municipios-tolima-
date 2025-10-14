from pathlib import Path
import streamlit as st
import pandas as pd
import base64
import plotly.express as px
import os
import math
import folium
from streamlit_folium import st_folium
# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(page_title="Observatorio Turístico del Tolima", layout="wide")

# =========================================================
# ESTILO PERSONALIZADO (igual que antes)
# =========================================================
st.markdown("""
<style>
/* Fondo principal */
html, body, [class*="stAppViewContainer"], [class*="main"], .stApp {
    background-color: #fdf6ed !important;  /* beige cálido */
    color: #3a2e1f !important;            /* marrón oscuro para textos generales */
}

/* Encabezados (h1, h2, h3) con más contraste y sombra ligera */
h1, h2, h3 {
    color: #1c2a35 !important; /* azul muy oscuro */
    text-shadow: 1px 1px 2px rgba(0,0,0,0.15);
}

/* Captions y textos pequeños */
.stCaption, p {
    color: #3a2e1f !important;
}

/* Selectboxes cálidos */
div[data-baseweb="select"], div[role="combobox"], div[role="combobox"] > div {
    background-color: #fffaf3 !important;
    color: #3a2e1f !important;
    border: 1px solid #deb887 !important;
    border-radius: 10px !important;
    box-shadow: 0 3px 8px rgba(200, 150, 100, 0.15) !important;
}

/* Popovers y opciones */
div[data-baseweb="popover"], div[role="listbox"], div[role="option"] {
    background-color: #fff7eb !important;
    color: #3a2e1f !important;
    border-radius: 10px !important;
}

/* Hover y selección */
div[role="option"]:hover, li[role="option"]:hover {
    background-color: #fae0b9 !important;
}
div[role="option"][aria-selected="true"], li[role="option"][aria-selected="true"] {
    background-color: #e8b168 !important;
    color: #ffffff !important;
}

/* Botones */
button, div.stButton > button {
    background-color: #f4d19b !important;
    color: #3a2e1f !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    box-shadow: 0 3px 6px rgba(180, 130, 80, 0.15) !important;
    transition: all 0.3s ease-in-out !important;
}
button:hover, div.stButton > button:hover {
    background-color: #e8b168 !important;
    color: #ffffff !important;
    transform: scale(1.02);
}

/* Tarjetas indicadores */
.indicator-section {
    display: flex;
    justify-content: space-between;
    align-items: stretch;
    margin-top: 10px;
    gap: 25px;
}

.indicator-card {
    flex: 1;
    position: relative;
    background: #fffaf3;
    border-radius: 18px;
    padding: 25px;
    box-shadow: 0 6px 16px rgba(120, 90, 50, 0.15);
    text-align: left;
    overflow: hidden;
    transition: all 0.3s ease;
    transform: translateY(-25px); /* <- sube la tarjeta 25px */
}


.indicator-card:hover {
    transform: translateY(-30px); /* sube un poco más al pasar mouse */
    box-shadow: 0 10px 20px rgba(120, 90, 50, 0.25);
}


.indicator-bg-icon {
    position: absolute;
    right: 10px;
    bottom: -10px;
    font-size: 4rem;           /* <-- Tamaño del icono de fondo */
    color: rgba(180, 120, 60, 0.15);  /* <-- Color y transparencia del icono */
}

.indicator-card h3 {
    color: #7b3f00;            /* <-- Color del número principal */
    font-size: 2.2rem;         /* <-- Tamaño del número */
    margin-bottom: 6px;
    font-weight: 700;
}

.indicator-card p {
    color: #4b3621;            /* <-- Color del texto descriptivo */
    font-weight: 500;
    font-size: 1rem;
}


/* Imagen centrada */
.img-centered { text-align:center; }
.img-centered img { border-radius:18px; box-shadow:0 4px 12px rgba(0,0,0,0.15); margin-top:10px; }
.img-centered p { font-size:14px; color:#3a2e1f !important; font-style:italic; margin-top:4px; }

</style>
""", unsafe_allow_html=True)


# =========================================================
# ENCABEZADO
# =========================================================
st.markdown("<h1 style='text-align:center;'>🌿 Observatorio Turístico del Tolima 🌿</h1>", unsafe_allow_html=True)


# =========================================================
# FUNCIÓN PARA MOSTRAR IMAGEN
# =========================================================
def mostrar_imagen_centrada(ruta_imagen, ancho=600, caption=""):
    try:
        with open(ruta_imagen, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""
            <div class='img-centered'>
                <img src='data:image/jpeg;base64,{b64}' width='{ancho}'>
                <p>{caption}</p>
            </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ Imagen no encontrada en la ruta especificada.")

mostrar_imagen_centrada("./data/imagenes/TOLIMA.jpeg", ancho=600, caption="Paisaje del Tolima")

# =========================================================
# CARGAR DATOS DESDE EXCEL
# =========================================================
FILE_PATH = Path("./data/municipios tolima.xlsx")
try:
    df = pd.read_excel(FILE_PATH)
except FileNotFoundError:
    st.error("⚠️ No se encontró el archivo Excel en la ruta especificada.")
    df = pd.DataFrame(columns=["municipio", "categoría", "nombre", "fuente", "Aporte a la investigaciòn"])

# =========================================================
# BARRA SUPERIOR DE FILTROS SIMPLIFICADA
# =========================================================
st.markdown('<div class="topbar">', unsafe_allow_html=True)
col1, col2 = st.columns([1,1])

with col1:
    municipio_sel = st.selectbox(
        "🏘️ Municipio", 
        options=["Todos"] + sorted(df["municipio"].dropna().unique()) if "municipio" in df.columns else ["Todos"]
    )

with col2:
    categoria_sel = st.selectbox(
        "🏞️ Categoría", 
        options=["Todos"] + sorted(df["categoría"].dropna().unique()) if "categoría" in df.columns else ["Todos"]
    )
st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# FILTRADO SEGÚN MUNICIPIO Y CATEGORÍA
# =========================================================
df_filt = df.copy()

if "municipio" in df.columns and municipio_sel != "Todos":
    df_filt = df_filt[df_filt["municipio"] == municipio_sel]

if "categoría" in df.columns and categoria_sel != "Todos":
    df_filt = df_filt[df_filt["categoría"] == categoria_sel]


# =========================================================
# KPIs
# =========================================================
# =========================================================
# KPIs DINÁMICOS SEGÚN FILTRO
# =========================================================
registros = len(df_filt)
categorias_unicas = df_filt["categoría"].nunique() if "categoría" in df_filt.columns else 0
fuentes_unicas = df_filt["fuente"].nunique() if "fuente" in df_filt.columns else 0

st.markdown(f"""
<style>
.indicator-section {{
    display: flex;
    justify-content: space-between;
    align-items: stretch;
    margin-top: 30px;
    gap: 25px;
}}
.indicator-card {{
    flex: 0.8;
    position: relative;
    background: linear-gradient(135deg, #fffaf0, #ffb86f);
    border-radius: 14px;
    padding: 15px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    text-align: left;
    overflow: hidden;
    transition: all 0.3s ease;
    color: #3a2e1f;
}}
.indicator-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.25);
}}
.indicator-bg-icon {{
    position: absolute;
    right: 10px;
    bottom: -10px;
    font-size: 4rem;
    color: rgba(180,120,60,0.25);
}}
.indicator-card h3 {{
    color: #3a2e1f;
    font-size: 2.2rem;
    margin-bottom: 6px;
    font-weight: 700;
}}
.indicator-card p {{
    color: #5a4028;
    font-weight: 500;
    font-size: 1rem;
}}
</style>

<h3 style="color:#7b3f00; font-weight:700;">📊 Indicadores Generales</h3>

<div class="indicator-section">
    <div class="indicator-card">
        <h3>{registros}</h3>
        <p>Registros encontrados</p>
        <div class="indicator-bg-icon">📘</div>
    </div>
    <div class="indicator-card">
        <h3>{categorias_unicas}</h3>
        <p>Categorías únicas</p>
        <div class="indicator-bg-icon">🏷️</div>
    </div>
    <div class="indicator-card">
        <h3>{fuentes_unicas}</h3>
        <p>Fuentes analizadas</p>
        <div class="indicator-bg-icon">🌐</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# CONFIGURACIÓN CARRUSEL
# =========================================================
# CONFIGURACIÓN
# =========================================================
# Carpeta principal donde están todas las subcarpetas de los municipios
carpeta_principal = "./data/imagenes"

# Seleccionar imágenes según el municipio
if municipio_sel != "Todos":
    carpeta_imagenes = os.path.join(carpeta_principal, municipio_sel)
    if os.path.exists(carpeta_imagenes):
        imagenes = [os.path.join(carpeta_imagenes, f) for f in os.listdir(carpeta_imagenes)
                    if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
    else:
        imagenes = []
        st.warning(f"No se encontró la carpeta para el municipio {municipio_sel}")
else:
    # Si es "Todos", lee todas las imágenes de la carpeta principal
    imagenes = [os.path.join(carpeta_principal, f) for f in os.listdir(carpeta_principal)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]

ANCHO_IMAGEN = 150
ALTO_IMAGEN = 150
COLUMNAS = 8

# =========================================================
# ESTILO CSS PARA ZOOM FRONTAL
# =========================================================
st.markdown(f"""
<style>
.img-box {{
    width: {ANCHO_IMAGEN}px;
    height: {ALTO_IMAGEN}px;
    overflow: hidden;
    border-radius: 12px;
    margin: 6px;
    display: inline-block;
    transition: transform 0.3s ease, z-index 0.3s ease;
    position: relative;
}}
.img-box img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}}
.img-box:hover {{
    transform: scale(1.5);   /* agranda al pasar el cursor */
    z-index: 999;            /* aparece al frente */
}}
.img-row {{
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
}}
</style>
""", unsafe_allow_html=True)

# =========================================================
# MOSTRAR IMAGENES
# =========================================================
if len(imagenes) > 0:
    html = '<div class="img-row">'
    for img_path in imagenes:
        with open(img_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
        html += f'<div class="img-box"><img src="data:image/jpeg;base64,{b64}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
else:
    st.warning("No se encontraron imágenes en la carpeta.")

    # Espaciado visual
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

# =========================================================
# TABS
# =========================================================
tabs = st.tabs(["📋 Registros", "📊 Visualización", "🧠 Investigación"])

# =========================================================
# CONTENIDO DEL TAB "📋 Registros"
# =========================================================
with tabs[0]:
    import math  # lo necesitas para ceil()
    # -----------------------------
    # Configuración del grid
    # -----------------------------
    N_COLS = 3  # Número de columnas (ajusta según ancho de pantalla)
    IMAGES_FOLDER = "./data/imagenes"

    # -----------------------------
    # Mostrar encabezado
    # -----------------------------
    st.subheader("📋 Registros filtrados")

    if df_filt.empty:
        st.info("No hay registros para mostrar.")
    else:
        records = df_filt.reset_index(drop=True)
        total = len(records)
        rows = math.ceil(total / N_COLS)

        # ===============================
        # CSS ELEGANTE CON CAJA INTERNA
        # ===============================
        st.markdown("""
        <style>
        .card {
            background: linear-gradient(145deg, #fffaf5, #ffe1c1, #ffcb91);
            border-radius: 15px;
            border: 1px solid #f0c27b;
            padding: 18px;
            margin-bottom: 18px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: scale(1.03);
            box-shadow: 4px 4px 20px rgba(0,0,0,0.2);
        }
        .card h4 {
            color: #d35400;
            margin-bottom: 12px;
            font-size: 1.15rem;
            text-align: center;
        }
        .info-box {
            background-color: rgba(255, 255, 255, 0.65);
            border: 1px solid rgba(0,0,0,0.1);
            border-radius: 10px;
            padding: 10px 12px;
            margin-top: 10px;
        }
        .info-box p {
            color: #4a4a4a;
            font-size: 0.9rem;
            margin: 6px 0;
        }
        </style>
        """, unsafe_allow_html=True)

        # ===============================
        # GRID DE TARJETAS
        # ===============================
        for r in range(rows):
            start = r * N_COLS
            end = start + N_COLS
            cols = st.columns(N_COLS)

            for i, idx in enumerate(range(start, end)):
                if idx >= total:
                    cols[i].empty()
                    continue

                row = records.loc[idx]
                title = row.get("Nombre", row.get("nombre", "Sin nombre"))

                # 👉 Tomar descripción (soporta variantes) y acortar un poco
                descripcion = row.get("Descripción",
                               row.get("descripción",
                               row.get("Resumen",
                               row.get("resumen", ""))))
                if isinstance(descripcion, str):
                    desc_txt = descripcion.strip()
                    if len(desc_txt) > 220:
                        desc_txt = desc_txt[:217] + "…"
                else:
                    desc_txt = ""

                with cols[i]:
                    st.markdown(f"""
                    <div class="card">
                        <h4>📌 {title}</h4>
                        <div class="info-box">
                            <p><strong>Categoría:</strong> {row.get("Categoría", row.get("categoría", ""))}</p>
                            <p><strong>Fuente:</strong> {row.get("Fuente", row.get("fuente", ""))}</p>
                            {f"<p><strong>Descripción:</strong> {desc_txt}</p>" if desc_txt else ""}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)



with tabs[1]:
    st.subheader("🗺️ Mapa del Tolima - Municipios principales")

    # ===== Imports locales =====
    import os
    import pandas as pd
    import numpy as np
    import math
    import pydeck as pdk

    # 🔹 1) Cargar Excel real (usa tu ruta local)
    ruta_excel = "./data/municipios tolima.xlsx"
    try:
        df_excel = pd.read_excel(ruta_excel)
        # Normalizamos nombres de columnas a minúsculas sin espacios alrededor
        df_excel.columns = [c.strip().lower() for c in df_excel.columns]
        st.success("✅ Archivo 'municipios tolima.xlsx' cargado correctamente.")
    except Exception as e:
        st.error(f"❌ No se pudo cargar el Excel: {e}")
        df_excel = pd.DataFrame()

    # 🔹 2) Datos base para el mapa (puedes ajustar coordenadas si gustas)
    municipios = pd.DataFrame({
        "Municipio": ["Chaparral", "Rioblanco", "Planadas", "Ataco"],
        "Latitud": [3.723, 3.520, 3.147, 3.591],
        "Longitud": [-75.484, -75.901, -75.636, -75.429],
        "Altitud (m)": [850, 1800, 950, 700],
        "Población (hab)": [47000, 21000, 31000, 13000]
    })

    # 🔹 3) Filtro de municipios
    municipios_seleccionados = st.multiselect(
        "Selecciona los municipios a mostrar:",
        options=municipios["Municipio"].tolist(),
        default=municipios["Municipio"].tolist()
    )
    df = municipios[municipios["Municipio"].isin(municipios_seleccionados)].reset_index(drop=True)

    # 🔹 4) Función distancia Haversine
    def distancia(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
            math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    # 🔹 5) Distancias entre municipios seleccionados
    distancias = []
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            d = distancia(df.iloc[i]["Latitud"], df.iloc[i]["Longitud"],
                          df.iloc[j]["Latitud"], df.iloc[j]["Longitud"])
            distancias.append({
                "Desde": df.iloc[i]["Municipio"],
                "Hasta": df.iloc[j]["Municipio"],
                "Distancia (km)": round(d, 1)
            })
    df_distancias = pd.DataFrame(distancias)

    # 🔹 6) Mapa avanzado con pydeck (con basemap asegurado)
    st.markdown("### 🗺️ Vista avanzada")

    # Enriquecemos con nº de registros del Excel por municipio (si existe 'municipio' en el Excel)
    if not df_excel.empty and "municipio" in df_excel.columns:
        conteo_excel = (
            df_excel.assign(municipio=df_excel["municipio"].astype(str).str.strip())
            .groupby("municipio")
            .size()
            .reset_index(name="registros_excel")
        )
        df_map = df.merge(conteo_excel, left_on="Municipio", right_on="municipio", how="left")
        df_map.drop(columns=["municipio"], inplace=True)
    else:
        df_map = df.copy()
        df_map["registros_excel"] = 0

    df_map["registros_excel"] = df_map["registros_excel"].fillna(0).astype(int)

    # ---- Escalado adaptativo del radio (evita círculos gigantes) ----
    reg_max = int(df_map["registros_excel"].max()) if not df_map.empty else 0
    df_map["radius_m"] = np.interp(
        df_map["registros_excel"],
        [0, reg_max if reg_max > 0 else 1],
        [3500, 12000]  # ajusta a [2500, 9000] si aún hay solape
    ).astype(int)

    # ---- Controles UI: opacidad, arcos y estilo ----
    colA, colB, colC = st.columns([1, 1, 2])
    with colA:
        opacidad = st.slider("Opacidad de círculos", 40, 230, 150, step=10)
    with colB:
        ver_arcos = st.checkbox("Mostrar conexiones", value=False)
    with colC:
        estilo = st.selectbox("Estilo del mapa", ["OSM (recomendado)", "Mapbox Light", "Mapbox Streets", "Mapbox Dark", "Mapbox Satellite"], index=0)

    # ---- Color por altitud + alpha controlado ----
    alt_max = float(df_map["Altitud (m)"].max()) if not df_map.empty else 1.0
    alt_max = alt_max if alt_max > 0 else 1.0

    def color_from_alt(alt, alpha):
        base = max(90, min(200, int(90 + (alt / alt_max) * 110)))  # 90–200
        return [base, 130, 90, int(alpha)]  # RGBA

    df_map["fill_color"] = df_map["Altitud (m)"].apply(lambda a: color_from_alt(a, opacidad))

    # ---- Auto-zoom por bounding box ----
    def zoom_from_bounds(lats, lons):
        if len(lats) == 0:
            return 7.8
        lat_span = max(lats) - min(lats)
        lon_span = max(lons) - min(lons)
        span = max(lat_span, lon_span)
        if span < 0.15:   return 9.2
        if span < 0.3:    return 8.6
        if span < 0.6:    return 8.0
        if span < 1.0:    return 7.5
        return 7.0

    center_lat = float(df_map["Latitud"].mean()) if not df_map.empty else 3.4
    center_lon = float(df_map["Longitud"].mean()) if not df_map.empty else -75.7
    zoom_auto  = zoom_from_bounds(df_map["Latitud"].tolist(), df_map["Longitud"].tolist())

    # ====== BASEMAP CONFIG ======
    mapbox_key = os.getenv("MAPBOX_API_KEY", "").strip()
    base_layers = []
    map_style = None  # lo ponemos en None si usamos TileLayer (OSM)

    use_osm = (estilo.startswith("OSM") or not mapbox_key)

    if use_osm:
        # Basemap OpenStreetMap (no requiere token)
        # Puedes cambiar a 'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
        base_layers.append(
            pdk.Layer(
                "TileLayer",
                data="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                min_zoom=0, max_zoom=19, tile_size=256
            )
        )
    else:
        # Mapbox disponible (requiere MAPBOX_API_KEY en el entorno)
        styles = {
            "Mapbox Streets": "mapbox://styles/mapbox/streets-v12",
            "Mapbox Light": "mapbox://styles/mapbox/light-v11",
            "Mapbox Dark": "mapbox://styles/mapbox/dark-v11",
            "Mapbox Satellite": "mapbox://styles/mapbox/satellite-v9",
        }
        map_style = styles.get(estilo, "mapbox://styles/mapbox/light-v11")
        # pydeck lee automáticamente MAPBOX_API_KEY del entorno

    # ====== CAPAS DE DATOS ======
    points = pdk.Layer(
        "ScatterplotLayer",
        data=df_map,
        get_position="[Longitud, Latitud]",
        get_radius="radius_m",
        get_fill_color="fill_color",
        pickable=True,
        stroked=True,
        get_line_color=[20, 20, 20, 140],
        line_width_min_pixels=2,
    )

    labels = pdk.Layer(
        "TextLayer",
        data=df_map,
        get_position="[Longitud, Latitud]",
        get_text="Municipio",
        get_size=12,
        get_color=[30, 30, 30, 240],
        get_angle=0,
        get_alignment_baseline="'bottom'",
        billboard=True,
        pickable=False,
    )

    layers = base_layers + [points, labels]

    # Arcos opcionales
    if ver_arcos and not df_distancias.empty:
        coords = {row["Municipio"]: (row["Longitud"], row["Latitud"]) for _, row in df.iterrows()}
        arcos_data = []
        for _, row in df_distancias.iterrows():
            de = row["Desde"]; hasta = row["Hasta"]
            if de in coords and hasta in coords:
                lon1, lat1 = coords[de]; lon2, lat2 = coords[hasta]
                arcos_data.append({"from": [lon1, lat1], "to": [lon2, lat2], "dist_km": row["Distancia (km)"]})
        arcos = pdk.Layer(
            "ArcLayer",
            data=arcos_data,
            get_source_position="from",
            get_target_position="to",
            get_width=3,
            get_tilt=12,
            get_source_color=[110, 110, 200, 110],
            get_target_color=[200, 110, 110, 110],
            pickable=True,
        )
        layers.append(arcos)

    tooltip = {
        "html": (
            "<b>{Municipio}</b><br/>"
            "Altitud: {Altitud (m)} m<br/>"
            "Población: {Población (hab)} hab<br/>"
            "Registros Excel: {registros_excel}<br/>"
            "Radio: {radius_m} m"
        ),
        "style": {"backgroundColor": "rgba(255,255,255,0.9)", "color": "black"}
    }

    deck = pdk.Deck(
        map_style=map_style,  # None si usamos OSM; estilo Mapbox si hay token
        initial_view_state=pdk.ViewState(
            latitude=center_lat, longitude=center_lon,
            zoom=zoom_auto, pitch=25, bearing=8
        ),
        layers=layers,
        tooltip=tooltip,
    )

    st.pydeck_chart(deck, use_container_width=True)
    st.caption(
        ("Basemap: **OpenStreetMap** (sin token) " if use_osm else "Basemap: **Mapbox** ") +
        "· El **radio** se ajusta al máximo de *registros* del Excel (límite 3.5–12 km). "
        "Ajuste la **opacidad** o desactive **conexiones** si hay solapamiento."
    )

    # 🔹 7) Análisis automático básico (con los datos del mapa)
    st.markdown("### 📊 Análisis automático de los municipios")
    if not df.empty:
        if not df_distancias.empty:
            promedio_dist = df_distancias["Distancia (km)"].mean()
            st.markdown(f"- 📍 **Distancia promedio** entre seleccionados: **{promedio_dist:.1f} km**")

        mayor_pob = df.loc[df["Población (hab)"].idxmax(), "Municipio"]
        mayor_alt = df.loc[df["Altitud (m)"].idxmax(), "Municipio"]
        menor_alt = df.loc[df["Altitud (m)"].idxmin(), "Municipio"]

        st.markdown(
            f"- 🌆 **Más poblado:** **{mayor_pob}** "
            f"({int(df['Población (hab)'].max()):,} hab)"
        )
        st.markdown(
            f"- 🏔️ **Mayor altitud:** **{mayor_alt}** "
            f"({int(df['Altitud (m)'].max())} m)"
        )
        st.markdown(
            f"- 🌄 **Menor altitud:** **{menor_alt}** "
            f"({int(df['Altitud (m)'].min())} m)"
        )

    # 🔹 8) Análisis automático del Excel (alineado al archivo real)
    st.markdown("### 🤖 Análisis automático del archivo Excel")

    if df_excel.empty:
        st.info("⚠️ No hay datos en el archivo Excel para análisis adicional.")
    else:
        # Filtrado por municipios seleccionados si existe la columna 'municipio'
        if "municipio" in df_excel.columns:
            df_excel["municipio_norm"] = df_excel["municipio"].astype(str).str.strip().str.lower()
            sel_norm = [m.strip().lower() for m in municipios_seleccionados]
            df_excel_filtrado = df_excel[df_excel["municipio_norm"].isin(sel_norm)].copy()
        else:
            df_excel_filtrado = df_excel.copy()

        if df_excel_filtrado.empty:
            st.warning("⚠️ No hay registros en el Excel correspondientes a los municipios seleccionados.")
        else:
            # Columnas esperadas según tu archivo
            col_mun = "municipio"
            col_cat = "categoría" if "categoría" in df_excel_filtrado.columns else None
            col_nom = "nombre" if "nombre" in df_excel_filtrado.columns else None
            col_desc = "descripción" if "descripción" in df_excel_filtrado.columns else None
            col_fuente = "fuente" if "fuente" in df_excel_filtrado.columns else None
            col_info = "info_relevante" if "info_relevante" in df_excel_filtrado.columns else None
            col_aporte = "aporte a la investigaciòn" if "aporte a la investigaciòn" in df_excel_filtrado.columns else None

            # — Resumen por municipio y categoría —
            if col_mun and col_cat:
                st.markdown("#### 📊 Registros por **municipio** y **categoría**")
                resumen_mun_cat = (
                    df_excel_filtrado
                    .groupby([col_mun, col_cat], dropna=False)
                    .size()
                    .reset_index(name="registros")
                    .sort_values(["municipio", "registros"], ascending=[True, False])
                )
                st.dataframe(resumen_mun_cat, use_container_width=True)

            # — Top categorías (global y por municipio) —
            if col_cat:
                st.markdown("#### 🧭 Categorías más frecuentes")
                top_global = (
                    df_excel_filtrado[col_cat]
                    .value_counts(dropna=False)
                    .reset_index()
                    .rename(columns={"index": col_cat, col_cat: "registros"})
                )
                st.dataframe(top_global, use_container_width=True)

                if col_mun:
                    st.markdown("#### 🧩 Top categoría por municipio (seleccionados)")
                    top_por_mun = (
                        df_excel_filtrado
                        .groupby(col_mun)[col_cat]
                        .agg(lambda s: s.value_counts().index[0] if len(s.dropna()) else np.nan)
                        .reset_index(name="categoría más frecuente")
                    )
                    st.dataframe(top_por_mun, use_container_width=True)

            # — Muestra de fuentes y elementos clave —
            if col_fuente:
                st.markdown("#### 🔗 Fuentes más utilizadas")
                top_fuentes = (
                    df_excel_filtrado[col_fuente]
                    .value_counts(dropna=False)
                    .head(10)
                    .reset_index()
                    .rename(columns={"index": "fuente", col_fuente: "registros"})
                )
                st.dataframe(top_fuentes, use_container_width=True)

            # — Conclusiones automáticas en texto (estilo fluido) —
            st.markdown("### 📑 Conclusiones automáticas (basadas en el Excel filtrado)")

            conclusiones = []

            # 1) Cobertura por municipio
            if col_mun:
                conteo_mun = (
                    df_excel_filtrado[col_mun]
                    .value_counts()
                    .reindex(municipios_seleccionados, fill_value=0)
                )
                if conteo_mun.sum() > 0:
                    texto_mun = ", ".join([f"**{m}** ({n})" for m, n in conteo_mun.items()])
                    conclusiones.append(
                        f"Se registran **{int(conteo_mun.sum())}** entradas en total para los municipios seleccionados, "
                        f"con distribución por municipio: {texto_mun}."
                    )

            # 2) Tendencia de categorías
            if col_cat and not df_excel_filtrado.empty:
                vc = df_excel_filtrado[col_cat].value_counts()
                if not vc.empty:
                    top_cat = vc.index[0]
                    top_n = int(vc.iloc[0])
                    conclusiones.append(
                        f"La **categoría predominante** en el conjunto filtrado es **{top_cat}** (≈ {top_n} registros), "
                        f"lo que orienta el enfoque de experiencias y datos analizados."
                    )

            # 3) Fuentes (si existen)
            if col_fuente and not df_excel_filtrado.empty:
                vf = df_excel_filtrado[col_fuente].value_counts()
                if not vf.empty:
                    fuente_top = str(vf.index[0])
                    fuente_n = int(vf.iloc[0])
                    conclusiones.append(
                        f"Las **fuentes** con mayor presencia señalan a **{fuente_top}** (≈ {fuente_n} apariciones), "
                        f"aportando consistencia en la procedencia de la información."
                    )

            # 4) Info relevante / aportes (si existen)
            if col_info or col_aporte:
                disponibles = [c for c in [col_info, col_aporte] if c]
                tot_textos = int(
                    sum(df_excel_filtrado[c].notna().sum() for c in disponibles)
                )
                if tot_textos > 0:
                    conclusiones.append(
                        f"Se identifican **{tot_textos}** notas descriptivas entre "
                        + " y ".join([f"**{c}**" for c in disponibles]) +
                        ", útiles para enriquecer fichas y justificaciones."
                    )

            if conclusiones:
                st.markdown(" ".join(conclusiones))
            else:
                st.info("No se encontraron datos suficientes para generar conclusiones textuales.")

with tabs[2]:
    st.subheader("🧠 Aportes a la investigación")

    import re
    import math
    import pandas as pd
    from collections import Counter

    # ===== Comprobación de df_filt =====
    if 'df_filt' not in locals():
        st.error("No se encontró el DataFrame filtrado (df_filt). Asegúrate de crearlo antes.")
    else:
        # ===== 1) Resolver columnas de forma robusta (insensible a mayúsculas/acentos) =====
        def norm(s: str) -> str:
            return str(s).strip().lower()

        cols_norm = {norm(c): c for c in df_filt.columns}

        def find_col(candidates):
            # Búsqueda exacta normalizada
            for k in candidates:
                nk = norm(k)
                if nk in cols_norm:
                    return cols_norm[nk]
            # Búsqueda por "contiene"
            for k in candidates:
                for c in df_filt.columns:
                    if k in norm(c):
                        return c
            return None

        col_aporte = find_col(["aporte a la investigaciòn", "aporte a la investigación", "aporte", "aporte_investigacion", "aportes"])
        col_nombre = find_col(["nombre", "titulo", "título"])
        col_muni   = find_col(["municipio"])
        col_cat    = find_col(["categoría", "categoria"])
        col_fuente = find_col(["fuente"])

        if (col_aporte is None) or df_filt.empty:
            st.info("No hay aportes de investigación en el dataset.")
        else:
            base = df_filt.copy()

            # ===== 2) Filtros UI =====
            colf1, colf2, colf3 = st.columns([1, 1, 2])
            with colf1:
                muni_sel = None
                if col_muni and base[col_muni].notna().any():
                    muni_opts = ["(Todos)"] + sorted(base[col_muni].dropna().astype(str).unique().tolist())
                    muni_sel = st.selectbox("Municipio", muni_opts, index=0)
            with colf2:
                cat_sel = None
                if col_cat and base[col_cat].notna().any():
                    cat_opts = ["(Todas)"] + sorted(base[col_cat].dropna().astype(str).unique().tolist())
                    cat_sel = st.selectbox("Categoría", cat_opts, index=0)
            with colf3:
                q = st.text_input("Buscar palabra clave en los aportes", value="")

            # Aplicar filtros
            dfA = base.copy()
            if col_muni and muni_sel and muni_sel != "(Todos)":
                dfA = dfA[dfA[col_muni].astype(str) == muni_sel]
            if col_cat and cat_sel and cat_sel != "(Todas)":
                dfA = dfA[dfA[col_cat].astype(str) == cat_sel]
            if q.strip():
                patt = re.compile(re.escape(q.strip()), flags=re.IGNORECASE)
                dfA = dfA[dfA[col_aporte].astype(str).str.contains(patt)]

            # ===== 3) KPIs rápidos =====
            total_aportes = dfA[col_aporte].dropna().shape[0]
            prom_long = int(dfA[col_aporte].dropna().astype(str).map(len).mean()) if total_aportes > 0 else 0
            pct_con_fuente = (dfA[col_fuente].notna().mean() * 100) if col_fuente else 0.0

            k1, k2, k3 = st.columns(3)
            k1.metric("Aportes encontrados", f"{total_aportes}")
            k2.metric("Longitud promedio (caracteres)", f"{prom_long}")
            k3.metric("% con fuente", f"{pct_con_fuente:.0f}%")

            # ===== 4) Top términos y bigramas (simple, sin librerías externas) =====
            stop_es = set("""
                a al algo algun alguna algunas alguno algunos ante antes como con contra cual cuales cualquier cualesquiera 
                de del desde donde dos el la las lo los en entre era erais eramos eran eres es esa esas ese eso esos esta 
                estas este esto estos fue fueron fui fuimos ha haber habia habian habiais habiamos han has hasta hay hice 
                hicieron hicimos hizo la las los le les lo me mi mis mucha muchas mucho muchos muy no nos o os otra otras 
                otro otros para pero poco pocas pocos por porque que quien quienes se sin sobre su sus te ti tiene tuve 
                tuvieron tuvimos tuvo un una unas uno unos y ya si sí son ser es fue
            """.split())

            def limpiar(texto):
                t = re.sub(r"[^a-zA-ZáéíóúñÁÉÍÓÚÑ0-9\s]", " ", str(texto))
                return t.lower()

            textos = dfA[col_aporte].dropna().astype(str).tolist()

            tokens, bigrams = [], []
            for tx in textos:
                ws = [w for w in limpiar(tx).split() if len(w) >= 4 and w not in stop_es]
                tokens.extend(ws)
                for i in range(len(ws) - 1):
                    bigrams.append(ws[i] + " " + ws[i + 1])

            top_words = Counter(tokens).most_common(12)
            top_bigrams = Counter(bigrams).most_common(10)

            st.markdown("#### 🔤 Términos más frecuentes")
            st.write(", ".join([f"**{w}** ({n})" for w, n in top_words]) if top_words else "Sin términos destacados para el filtro actual.")
            st.markdown("#### 〰️ Bigramas más frecuentes")
            st.write(", ".join([f"**{b}** ({n})" for b, n in top_bigrams]) if top_bigrams else "Sin bigramas destacados para el filtro actual.")

            st.divider()

            # ===== 5) Lista de aportes (formato original, UNA COLUMNA, sin expander) =====
            def highlight(text, query):
                if not query:
                    return text
                return re.sub(f"({re.escape(query)})", r"<mark>\1</mark>", str(text), flags=re.IGNORECASE)

            cols_show = [c for c in [col_nombre, col_muni, col_cat, col_fuente] if c]
            view = dfA[[c for c in cols_show + [col_aporte] if c in dfA.columns]].dropna(subset=[col_aporte])

            # Paginación (mantener para no renderizar cientos de filas a la vez)
            page_size = st.select_slider("Aportes por página", options=[5, 10, 15, 20, 30, 50], value=15)
            total_rows = view.shape[0]
            total_pages = max(1, math.ceil(total_rows / page_size))
            page = st.number_input("Página", min_value=1, max_value=total_pages, value=1, step=1)
            start, end = (page - 1) * page_size, min(page * page_size, total_rows)
            page_df = view.iloc[start:end]

            if total_rows == 0:
                st.info("No se encontraron aportes con los filtros/búsqueda actuales.")
            else:
                st.caption(f"Mostrando {start+1}–{end} de {total_rows} aportes.")
                for _, fila in page_df.iterrows():
                    titulo = str(fila[col_nombre]) if col_nombre and pd.notna(fila[col_nombre]) else "Sin título"
                    muni_txt = f"{fila[col_muni]}" if col_muni and pd.notna(fila[col_muni]) else "—"
                    cat_txt  = f"{fila[col_cat]}"  if col_cat  and pd.notna(fila[col_cat])  else "—"
                    fuente_txt = f"{fila[col_fuente]}" if col_fuente and pd.notna(fila[col_fuente]) else "—"
                    cuerpo = highlight(fila[col_aporte], q)

                    # Encabezado del aporte
                    st.markdown(f"**{titulo}** · _Municipio:_ {muni_txt} · _Categoría:_ {cat_txt} · _Fuente:_ {fuente_txt}")
                    # Cuerpo del aporte
                    st.markdown(cuerpo, unsafe_allow_html=True)
                    # — División pequeña e indentada entre resultados —
                    st.markdown(
                     """
                     <style>
                    /* Cambia el color del valor de st.metric a negro */
                    div[data-testid="stMetricValue"] {
                        color: black !important;
                    }
                    /* Cambia el color del label de st.metric a negro */
                    div[data-testid="stMetricLabel"] {
                        color: black !important;
                    }
                    </style>
                     <div style="
                     height:4px;  /* grosor */
                     background: linear-gradient(
                     to right,
                        rgba(245, 158, 11, 0.25),  /* amber-500 suave */
                        rgba(249, 115, 22, 0.85),  /* orange-500 intenso */
                        rgba(245, 158, 11, 0.25)
                  );
                     margin:12px 0 18px 16px;  /* separación e indentación */
                     border-radius:3px;
                     max-width:94%;
                    "></div>
           """,
                   unsafe_allow_html=True
     )

            # ===== 6) Descarga =====
            st.download_button(
                label="⬇️ Descargar aportes filtrados (CSV)",
                data=view.to_csv(index=False).encode("utf-8"),
                file_name="aportes_investigacion_filtrados.csv",
                mime="text/csv",
            )


