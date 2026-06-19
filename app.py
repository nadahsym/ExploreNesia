"""
Semantic Tourism Search System
================================
Aplikasi pencarian wisata Indonesia berbasis Semantic Web
menggunakan Streamlit + Pandas + SPARQL.
(Modularized Version)
"""
import streamlit as st

# 1. Setup Page Config FIRST (Must be the first Streamlit command)
st.set_page_config(
    page_title="ExploreNesia: Semantic Tourism Search",
    page_icon="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%232563eb' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'%3E%3C/circle%3E%3Cpolygon points='16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76'%3E%3C/polygon%3E%3C/svg%3E",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Imports from custom modules
from utils.styles import inject_custom_css
from utils.icons import get_svg_icon
from core.data_loader import load_ontology_graph, load_tourism_data, load_package_data
from views.beranda import render_beranda
from views.cari_wisata import render_cari_wisata
from views.paket_wisata import render_paket_wisata
from views.statistik import render_statistik
from views.peta_wisata import render_peta_wisata
from views.relasi_semantik import render_relasi_semantik

# 3. Inject CSS
inject_custom_css()

# 4. Sidebar Navigation & Global State
with st.sidebar:
    st.markdown(f"""
    <div style="font-size:1.3rem; font-weight:800; color:#ffffff; margin-bottom:0.5rem; display:flex; align-items:center; gap:8px;">
        {get_svg_icon("compass")} ExploreNesia
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navigasi",
        ["Beranda", "Cari Wisata", "Paket Wisata", "Statistik", "Peta Wisata", "Relasi Semantik"],
        label_visibility="collapsed",
    )

    # Graph filter settings (only shown on Relasi Semantik page)
    if page == "Relasi Semantik":
        st.markdown("---")
        st.markdown("<div style='font-size:0.8rem; color:#a8c4e0; font-weight:700; letter-spacing:0.5px; margin-bottom:0.5rem;'>⚙️ PENGATURAN GRAF</div>", unsafe_allow_html=True)
        graph_filter_mode = st.selectbox(
            "Tipe Relasi Semantik:",
            ["Semua Relasi", "Lokasi yang Sama", "Kategori yang Sama", "Paket yang Sama"],
            index=0,
            key="graph_filter_mode"
        )
        graph_sort_by = st.selectbox(
            "Urutkan Tetangga:",
            ["Default", "Rating Tertinggi", "Rating Terendah", "Nama A–Z", "Nama Z–A", "Acak"],
            index=0,
            key="graph_sort_by"
        )
        graph_max_nodes = st.slider(
            "Jumlah Node Tetangga:",
            min_value=2,
            max_value=10,
            value=3,
            key="graph_max_nodes"
        )
    else:
        graph_filter_mode = "Semua Relasi"
        graph_sort_by = "Default"
        graph_max_nodes = 3

# 5. Load Data
with st.spinner("Memuat ontologi wisata dari TTL…"):
    _g_shared    = load_ontology_graph()
    df_tourism   = load_tourism_data(_g_shared)
    df_packages  = load_package_data(_g_shared)

all_cities      = sorted(df_tourism["City"].unique().tolist())      if not df_tourism.empty else []
all_categories  = sorted(df_tourism["Category"].unique().tolist())  if not df_tourism.empty else []
min_r = float(df_tourism["Rating"].min()) if not df_tourism.empty else 0.0
max_r = float(df_tourism["Rating"].max()) if not df_tourism.empty else 5.0

# 6. Page Routing
if page == "Beranda":
    render_beranda(df_tourism, df_packages)

elif page == "Cari Wisata":
    render_cari_wisata(_g_shared, all_cities, all_categories, min_r, max_r)

elif page == "Paket Wisata":
    render_paket_wisata(df_packages, df_tourism)

elif page == "Statistik":
    render_statistik(df_tourism, df_packages)

elif page == "Peta Wisata":
    render_peta_wisata(df_tourism, all_cities, all_categories, min_r, max_r)

elif page == "Relasi Semantik":
    render_relasi_semantik(df_tourism, _g_shared, graph_filter_mode, graph_sort_by, graph_max_nodes)