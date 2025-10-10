# ==========================================================
# app_topbar_final.py – filtros arriba, sin sidebar
# ==========================================================
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- Configuración general ---
st.set_page_config(page_title="Observatorio Turístico del Tolima", layout="wide")

# --- Estilo visual (Glassmorphism moderno) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

/* Fondo general */
.stApp {
    background: radial-gradient(circle at 25% 25%, rgba(35, 10, 90, 0.9), rgba(10, 5, 40, 0.97)) !important;
    color: #fff !important;
}

/* Barra superior (filtros) */
.topbar {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(18px) saturate(180%);
    -webkit-backdrop-filter: blur(18px) saturate(180%);
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.2);
    padding: 1rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 25px rgba(0,0,0,0.3);
}

/* Tarjetas métricas */
.metric-card {
    background: rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1rem;
    text-align: center;
    border: 1px solid rgba(170,90,255,0.4);
    box-shadow: 0 0 15px rgba(120,50,255,0.3);
    transition: transform 0.25s ease-in-out;
}
.metric-card:hover { transform: translateY(-4px); }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: rgba(255,255,255,0.05) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    padding: 4px !important;
}
</style>
""", unsafe_allow_html=True)

# --- Carga de datos ---
FILE_PATH = Path("data") / "municipios tolima.xlsx"
@st.cache_data
def load_data(file_path):
    return pd.read_excel(file_path)
df = load_data(FILE_PATH)

# --- Encabezado ---
st.markdown("<h1 style='text-align:center;'>💡 Observatorio Turístico del Tolima</h1>", unsafe_allow_html=True)
st.caption("Análisis de información turística y fuentes digitales")

# --- Barra superior de filtros (sin sidebar) ---
st.markdown('<div class="topbar">', unsafe_allow_html=True)
f1, f2, f3 = st.columns([1,1,1])
with f1:
    categoria = st.multiselect("Categoría", sorted(df["categoría"].dropna().unique()))
with f2:
    fuente = st.multiselect("Fuente", sorted(df["fuente"].dropna().unique()))
with f3:
    buscar = st.text_input("🔍 Buscar texto")
st.markdown('</div>', unsafe_allow_html=True)

# --- Filtrado de datos ---
df_filt = df.copy()
if categoria:
    df_filt = df_filt[df_filt["categoría"].isin(categoria)]
if fuente:
    df_filt = df_filt[df_filt["fuente"].isin(fuente)]
if buscar:
    df_filt = df_filt[df_filt.apply(lambda r: r.astype(str).str.contains(buscar, case=False).any(), axis=1)]

# --- KPIs ---
st.subheader("📊 Indicadores Generales")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"<div class='metric-card'><h2>{len(df_filt):,}</h2><p>Registros</p></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='metric-card'><h2>{df_filt['categoría'].nunique():,}</h2><p>Categorías únicas</p></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='metric-card'><h2>{df_filt['fuente'].nunique():,}</h2><p>Fuentes únicas</p></div>", unsafe_allow_html=True)

st.markdown("---")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📋 Resumen", "📊 Visualización", "🧠 Investigación"])

with tab1:
    st.dataframe(df_filt, use_container_width=True)

with tab2:
    st.subheader("📈 Distribución de registros")
    var = st.selectbox("Variable a agrupar", ["categoría", "fuente"])
    conteo = df_filt[var].value_counts().reset_index()
    conteo.columns = [var, "Conteo"]
    fig = px.bar(conteo, x="Conteo", y=var, orientation="h",
                 text="Conteo", color="Conteo", color_continuous_scale="plasma")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=600, margin=dict(l=20,r=20,t=40,b=20),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Aportes a la investigación")
    muestra = df_filt[["nombre","Aporte a la investigaciòn"]].dropna().head(10)
    for _, fila in muestra.iterrows():
        st.markdown(f"**{fila['nombre']}** — {fila['Aporte a la investigaciòn']}")
