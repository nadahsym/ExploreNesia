"""
Semantic Tourism Search System
================================
Aplikasi pencarian wisata Indonesia berbasis Semantic Web
menggunakan Streamlit + Pandas.

Dirancang untuk integrasi mendatang dengan RDF, SPARQL, dan Recommendation System.
"""

import streamlit as st
import pandas as pd
import math

# ──────────────────────────────────────────────
# PAGE CONFIGURATION
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Semantic Tourism Search",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CUSTOM CSS — Clean Modern UI
# ──────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
[data-testid="stAppViewContainer"] {
    background: #f7f8fc;
}
[data-testid="stSidebar"] {
    background: #1a1a2e;
}
[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #e0e0e0 !important;
    font-size: 15px;
}
[data-testid="stSidebar"] h2 {
    color: #ffffff !important;
    font-size: 1.1rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 1.5rem;
}

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, #0f3460 0%, #16213e 50%, #0d7377 100%);
    border-radius: 18px;
    padding: 3rem 2.5rem 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.18);
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: "🇮🇩";
    position: absolute;
    right: 2rem;
    top: 1.5rem;
    font-size: 5rem;
    opacity: 0.15;
}
.hero-title {
    color: #ffffff;
    font-size: 2.4rem;
    font-weight: 800;
    margin: 0 0 0.4rem;
    letter-spacing: -0.5px;
    line-height: 1.2;
}
.hero-subtitle {
    color: #a8d8ea;
    font-size: 1.05rem;
    margin: 0 0 0.6rem;
    font-weight: 400;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    color: #fff;
    font-size: 0.78rem;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 0.5px;
    margin-top: 0.5rem;
}

/* ── Stat Cards ── */
.stat-grid {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.stat-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.2rem 1.6rem;
    flex: 1;
    min-width: 130px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    border-left: 4px solid;
    transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-2px); }
.stat-card.blue  { border-color: #3a86ff; }
.stat-card.green { border-color: #06d6a0; }
.stat-card.orange{ border-color: #ffb703; }
.stat-card.purple{ border-color: #8338ec; }
.stat-number {
    font-size: 2rem;
    font-weight: 800;
    color: #1a1a2e;
    line-height: 1;
}
.stat-label {
    font-size: 0.82rem;
    color: #888;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Search & Filter Bar ── */
.search-section {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
}
.section-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Tourism Card ── */
.tourism-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    border-top: 4px solid #3a86ff;
    transition: box-shadow 0.25s, transform 0.25s;
    height: 100%;
}
.tourism-card:hover {
    box-shadow: 0 6px 24px rgba(58,134,255,0.18);
    transform: translateY(-3px);
}
.card-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1a1a2e;
    margin: 0 0 0.5rem;
    line-height: 1.3;
}
.card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-bottom: 0.7rem;
}
.badge {
    display: inline-block;
    font-size: 0.72rem;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.badge-city     { background: #e8f4ff; color: #3a86ff; }
.badge-category { background: #fff3cd; color: #856404; }
.badge-rating   { background: #d1fae5; color: #065f46; }
.badge-price    { background: #fce7f3; color: #9d174d; }
.card-desc {
    font-size: 0.83rem;
    color: #666;
    line-height: 1.55;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* ── Package Card ── */
.package-card {
    background: linear-gradient(135deg, #0f3460, #16213e);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    color: #fff;
    height: 100%;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    transition: transform 0.2s;
}
.package-card:hover { transform: translateY(-3px); }
.package-city {
    font-size: 0.78rem;
    color: #a8d8ea;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.4rem;
}
.package-places {
    font-size: 0.82rem;
    color: #d0e8f5;
    margin-top: 0.5rem;
    line-height: 1.6;
}

/* ── Section Headers ── */
.sec-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 2rem 0 1rem;
}
.sec-header h2 {
    font-size: 1.35rem;
    font-weight: 800;
    color: #1a1a2e;
    margin: 0;
}
.sec-line {
    flex: 1;
    height: 2px;
    background: linear-gradient(90deg, #3a86ff33, transparent);
    border-radius: 2px;
}

/* ── Pagination ── */
.page-info {
    text-align: center;
    color: #888;
    font-size: 0.85rem;
    margin-top: 0.5rem;
}

/* ── Empty State ── */
.empty-state {
    text-align: center;
    padding: 3rem;
    color: #aaa;
}
.empty-state .icon { font-size: 3rem; }
.empty-state p { font-size: 1rem; margin-top: 0.5rem; }

/* ── Footer ── */
.footer {
    text-align: center;
    color: #bbb;
    font-size: 0.78rem;
    padding: 2rem 0 1rem;
    border-top: 1px solid #e8e8f0;
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# DATA LOADING — cached untuk performa optimal
# ──────────────────────────────────────────────
@st.cache_data
def load_tourism_data(path: str = "data/tourism_with_id.csv") -> pd.DataFrame:
    """Memuat dan membersihkan dataset wisata utama."""
    df = pd.read_csv(path)

    # Normalkan nama kolom: strip spasi, title-case
    df.columns = df.columns.str.strip()

    # Hapus kolom tidak bernama
    unnamed = [c for c in df.columns if c.startswith("Unnamed")]
    df.drop(columns=unnamed, inplace=True, errors="ignore")

    # Bersihkan nilai harga & rating
    df["Price"] = pd.to_numeric(df.get("Price", 0), errors="coerce").fillna(0).astype(int)
    df["Rating"] = pd.to_numeric(df.get("Rating", 0), errors="coerce").fillna(0.0)

    # Pastikan kolom teks tidak NaN
    for col in ["Place_Name", "City", "Category", "Description"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    return df


@st.cache_data
def load_package_data(path: str = "data/package_tourism.csv") -> pd.DataFrame:
    """Memuat dataset paket wisata."""
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def format_price(price: int) -> str:
    """Format harga ke rupiah dengan pemisah ribuan."""
    if price == 0:
        return "Gratis"
    return f"Rp {price:,.0f}".replace(",", ".")


def star_rating(rating: float) -> str:
    """Konversi rating angka ke bintang unicode."""
    full = int(rating)
    half = 1 if (rating - full) >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + "✩" * half + "☆" * empty


CATEGORY_COLORS = {
    "Budaya": "#ff6b6b",
    "Taman Hiburan": "#ffd93d",
    "Cagar Alam": "#6bcb77",
    "Bahari": "#4d96ff",
    "Pusat Perbelanjaan": "#c77dff",
    "Tempat Ibadah": "#ff9f1c",
}

def category_color(cat: str) -> str:
    return CATEGORY_COLORS.get(cat, "#3a86ff")


# ──────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗺️ Semantic Tourism")
    st.markdown("---")

    page = st.radio(
        "Navigasi",
        ["🏠  Beranda", "🔍  Cari Wisata", "📦  Paket Wisata", "📊  Statistik"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("## 🔧 Tentang Sistem")
    st.markdown("""
<div style='font-size:0.82rem; color:#aaa; line-height:1.7;'>
    <b>Stack saat ini:</b><br>
    • Python + Streamlit<br>
    • Pandas (CSV)<br><br>
    <b>Roadmap integrasi:</b><br>
    • RDF / Turtle<br>
    • SPARQL Query Engine<br>
    • Recommendation System<br>
    • Knowledge Graph
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.75rem; color:#666; text-align:center;'>"
        "v1.0 · Semantic Web Project"
        "</div>",
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────
with st.spinner("Memuat dataset wisata Indonesia…"):
    df_tourism  = load_tourism_data()
    df_packages = load_package_data()

# Ambil daftar unik untuk filter
all_cities      = sorted(df_tourism["City"].unique().tolist())
all_categories  = sorted(df_tourism["Category"].unique().tolist())
min_r, max_r    = float(df_tourism["Rating"].min()), float(df_tourism["Rating"].max())

# ══════════════════════════════════════════════
# PAGE: BERANDA
# ══════════════════════════════════════════════
if page == "🏠  Beranda":

    # ── Hero ──
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🗺️ Semantic Tourism Search System</div>
        <div class="hero-subtitle">
            Jelajahi 400+ destinasi wisata Indonesia — Jakarta, Yogyakarta,
            Bandung, Semarang, Surabaya
        </div>
        <span class="hero-badge">⚡ Berbasis Semantic Web · RDF-Ready · SPARQL-Compatible</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Statistik ──
    total_places = len(df_tourism)
    total_cities = df_tourism["City"].nunique()
    total_cats   = df_tourism["Category"].nunique()
    avg_rating   = df_tourism["Rating"].mean()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="stat-card blue">
            <div class="stat-number">{total_places}</div>
            <div class="stat-label">🏛️ Total Wisata</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card green">
            <div class="stat-number">{total_cities}</div>
            <div class="stat-label">🏙️ Kota</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card orange">
            <div class="stat-number">{total_cats}</div>
            <div class="stat-label">🎭 Kategori</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="stat-card purple">
            <div class="stat-number">{avg_rating:.1f}</div>
            <div class="stat-label">⭐ Rata-rata Rating</div>
        </div>""", unsafe_allow_html=True)

    # ── Quick search shortcut ──
    st.markdown("""
    <div class="sec-header">
        <h2>🔍 Pencarian Cepat</h2>
        <div class="sec-line"></div>
    </div>
    """, unsafe_allow_html=True)

    quick_q = st.text_input(
        "Cari tempat wisata…",
        placeholder="Contoh: Borobudur, pantai, museum…",
        label_visibility="collapsed",
    )
    if quick_q:
        mask = df_tourism["Place_Name"].str.contains(quick_q, case=False, na=False)
        results = df_tourism[mask].head(6)
        if results.empty:
            st.info("Tidak ada hasil. Coba kata kunci lain.")
        else:
            cols = st.columns(3)
            for i, (_, row) in enumerate(results.iterrows()):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="tourism-card">
                        <div class="card-title">{row['Place_Name']}</div>
                        <div class="card-meta">
                            <span class="badge badge-city">📍 {row['City']}</span>
                            <span class="badge badge-category">🎭 {row['Category']}</span>
                            <span class="badge badge-rating">⭐ {row['Rating']}</span>
                            <span class="badge badge-price">💰 {format_price(row['Price'])}</span>
                        </div>
                        <p class="card-desc">{row['Description']}</p>
                    </div>
                    """, unsafe_allow_html=True)

    # ── Wisata unggulan (rating tertinggi) ──
    st.markdown("""
    <div class="sec-header">
        <h2>🌟 Wisata Unggulan</h2>
        <div class="sec-line"></div>
    </div>
    """, unsafe_allow_html=True)

    top_places = df_tourism.nlargest(6, "Rating")
    cols = st.columns(3)
    for i, (_, row) in enumerate(top_places.iterrows()):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="tourism-card" style="border-color:{category_color(row['Category'])};">
                <div class="card-title">{row['Place_Name']}</div>
                <div class="card-meta">
                    <span class="badge badge-city">📍 {row['City']}</span>
                    <span class="badge badge-category">🎭 {row['Category']}</span>
                    <span class="badge badge-rating">⭐ {row['Rating']} {star_rating(row['Rating'])}</span>
                    <span class="badge badge-price">💰 {format_price(row['Price'])}</span>
                </div>
                <p class="card-desc">{row['Description']}</p>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# PAGE: CARI WISATA
# ══════════════════════════════════════════════
elif page == "🔍  Cari Wisata":

    st.markdown("""
    <div class="hero-banner" style="padding:2rem 2.5rem;">
        <div class="hero-title" style="font-size:1.8rem;">🔍 Cari Tempat Wisata</div>
        <div class="hero-subtitle">Temukan destinasi impianmu dari 437 tempat wisata</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Filter Panel ──
    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚙️ Filter Pencarian</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1:
        search_q = st.text_input(
            "Nama Wisata",
            placeholder="Cari nama tempat wisata…",
            label_visibility="visible",
        )
    with col2:
        filter_city = st.selectbox(
            "Kota",
            ["Semua Kota"] + all_cities,
        )
    with col3:
        filter_cat = st.selectbox(
            "Kategori",
            ["Semua Kategori"] + all_categories,
        )
    with col4:
        filter_rating = st.slider(
            "Rating Minimum",
            min_value=min_r,
            max_value=max_r,
            value=min_r,
            step=0.1,
            format="%.1f ⭐",
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Apply Filters ──
    filtered = df_tourism.copy()

    if search_q:
        filtered = filtered[
            filtered["Place_Name"].str.contains(search_q, case=False, na=False)
        ]
    if filter_city != "Semua Kota":
        filtered = filtered[filtered["City"] == filter_city]
    if filter_cat != "Semua Kategori":
        filtered = filtered[filtered["Category"] == filter_cat]
    filtered = filtered[filtered["Rating"] >= filter_rating]

    # Sort by rating descending
    filtered = filtered.sort_values("Rating", ascending=False).reset_index(drop=True)

    # ── Result Summary ──
    col_res, col_sort = st.columns([5, 2])
    with col_res:
        st.markdown(
            f"<p style='color:#666; font-size:0.9rem; margin:0.5rem 0;'>"
            f"Menampilkan <b>{len(filtered)}</b> tempat wisata</p>",
            unsafe_allow_html=True,
        )
    with col_sort:
        sort_by = st.selectbox(
            "Urutkan",
            ["Rating Tertinggi", "Harga Terendah", "Harga Tertinggi", "A-Z"],
            label_visibility="collapsed",
        )

    if sort_by == "Rating Tertinggi":
        filtered = filtered.sort_values("Rating", ascending=False)
    elif sort_by == "Harga Terendah":
        filtered = filtered.sort_values("Price", ascending=True)
    elif sort_by == "Harga Tertinggi":
        filtered = filtered.sort_values("Price", ascending=False)
    elif sort_by == "A-Z":
        filtered = filtered.sort_values("Place_Name", ascending=True)

    # ── Pagination ──
    CARDS_PER_PAGE = 12
    total_pages = max(1, math.ceil(len(filtered) / CARDS_PER_PAGE))
    page_num = st.number_input(
        f"Halaman (dari {total_pages})",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1,
        label_visibility="collapsed",
    )
    start_idx = (page_num - 1) * CARDS_PER_PAGE
    page_data = filtered.iloc[start_idx : start_idx + CARDS_PER_PAGE]

    # ── Render Cards ──
    if page_data.empty:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">🔭</div>
            <p>Tidak ada wisata yang sesuai dengan filter yang dipilih.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        cols = st.columns(3)
        for i, (_, row) in enumerate(page_data.iterrows()):
            with cols[i % 3]:
                desc_short = row["Description"][:180] + "…" if len(row["Description"]) > 180 else row["Description"]
                st.markdown(f"""
                <div class="tourism-card" style="border-color:{category_color(row['Category'])};">
                    <div class="card-title">{row['Place_Name']}</div>
                    <div class="card-meta">
                        <span class="badge badge-city">📍 {row['City']}</span>
                        <span class="badge badge-category">🎭 {row['Category']}</span>
                        <span class="badge badge-rating">⭐ {row['Rating']}</span>
                        <span class="badge badge-price">💰 {format_price(row['Price'])}</span>
                    </div>
                    <p class="card-desc">{desc_short}</p>
                </div>
                """, unsafe_allow_html=True)

        # Pagination info + controls
        st.markdown(
            f"<div class='page-info'>Halaman {page_num} dari {total_pages} "
            f"· {len(filtered)} hasil total</div>",
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════
# PAGE: PAKET WISATA
# ══════════════════════════════════════════════
elif page == "📦  Paket Wisata":

    st.markdown("""
    <div class="hero-banner" style="padding:2rem 2.5rem;">
        <div class="hero-title" style="font-size:1.8rem;">📦 Paket Wisata Rekomendasi</div>
        <div class="hero-subtitle">Kumpulan paket perjalanan wisata terkurasi per kota</div>
    </div>
    """, unsafe_allow_html=True)

    # Filter kota paket
    pkg_cities = sorted(df_packages["City"].unique().tolist())
    selected_city = st.selectbox("Filter Kota Paket", ["Semua Kota"] + pkg_cities)

    pkg_filtered = df_packages.copy()
    if selected_city != "Semua Kota":
        pkg_filtered = pkg_filtered[pkg_filtered["City"] == selected_city]

    st.markdown(
        f"<p style='color:#666; font-size:0.9rem; margin:0.5rem 0 1.2rem;'>"
        f"Menampilkan <b>{len(pkg_filtered)}</b> paket wisata</p>",
        unsafe_allow_html=True,
    )

    # Kolom wisata dalam paket
    place_cols = [c for c in df_packages.columns if c.startswith("Place_Tourism")]

    cols = st.columns(3)
    for i, (_, row) in enumerate(pkg_filtered.iterrows()):
        places = [str(row[c]) for c in place_cols if pd.notna(row[c]) and str(row[c]).strip()]
        places_html = "".join(
            f"<div>▸ {p}</div>" for p in places
        ) if places else "<div style='color:#999'>Tidak ada detail tempat</div>"

        with cols[i % 3]:
            st.markdown(f"""
            <div class="package-card">
                <div class="package-city">📍 {row['City']}</div>
                <div style="font-size:1rem; font-weight:700; color:#fff;">
                    Paket #{int(row['Package'])}
                </div>
                <div class="package-places">{places_html}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Rekomendasi Berdasarkan Kota ──
    if selected_city != "Semua Kota":
        st.markdown("""
        <div class="sec-header">
            <h2>🏛️ Wisata Populer di Kota Ini</h2>
            <div class="sec-line"></div>
        </div>
        """, unsafe_allow_html=True)

        city_tourism = (
            df_tourism[df_tourism["City"] == selected_city]
            .nlargest(6, "Rating")
        )
        cols2 = st.columns(3)
        for i, (_, row) in enumerate(city_tourism.iterrows()):
            with cols2[i % 3]:
                st.markdown(f"""
                <div class="tourism-card" style="border-color:{category_color(row['Category'])};">
                    <div class="card-title">{row['Place_Name']}</div>
                    <div class="card-meta">
                        <span class="badge badge-category">🎭 {row['Category']}</span>
                        <span class="badge badge-rating">⭐ {row['Rating']}</span>
                        <span class="badge badge-price">💰 {format_price(row['Price'])}</span>
                    </div>
                    <p class="card-desc">{row['Description'][:150]}…</p>
                </div>
                """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# PAGE: STATISTIK
# ══════════════════════════════════════════════
elif page == "📊  Statistik":

    st.markdown("""
    <div class="hero-banner" style="padding:2rem 2.5rem;">
        <div class="hero-title" style="font-size:1.8rem;">📊 Statistik Dataset</div>
        <div class="hero-subtitle">Gambaran umum dataset wisata Indonesia</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Ringkasan utama ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="stat-card blue">
            <div class="stat-number">{len(df_tourism)}</div>
            <div class="stat-label">🏛️ Total Wisata</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card green">
            <div class="stat-number">{df_tourism['City'].nunique()}</div>
            <div class="stat-label">🏙️ Jumlah Kota</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card orange">
            <div class="stat-number">{df_tourism['Category'].nunique()}</div>
            <div class="stat-label">🎭 Kategori</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="stat-card purple">
            <div class="stat-number">{len(df_packages)}</div>
            <div class="stat-label">📦 Paket Wisata</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)

    # ── Per Kota ──
    with col_left:
        st.markdown("#### 🏙️ Wisata per Kota")
        city_counts = df_tourism["City"].value_counts().reset_index()
        city_counts.columns = ["Kota", "Jumlah Wisata"]
        st.bar_chart(city_counts.set_index("Kota"))

        st.dataframe(
            city_counts,
            use_container_width=True,
            hide_index=True,
        )

    # ── Per Kategori ──
    with col_right:
        st.markdown("#### 🎭 Wisata per Kategori")
        cat_counts = df_tourism["Category"].value_counts().reset_index()
        cat_counts.columns = ["Kategori", "Jumlah Wisata"]
        st.bar_chart(cat_counts.set_index("Kategori"))

        st.dataframe(
            cat_counts,
            use_container_width=True,
            hide_index=True,
        )

    # ── Distribusi Rating ──
    st.markdown("#### ⭐ Distribusi Rating")
    rating_dist = df_tourism["Rating"].value_counts().sort_index()
    st.bar_chart(rating_dist)

    # ── Tabel lengkap ──
    st.markdown("#### 📋 Preview Dataset (tourism_with_id.csv)")
    display_cols = ["Place_Id", "Place_Name", "City", "Category", "Rating", "Price", "Description"]
    available = [c for c in display_cols if c in df_tourism.columns]
    st.dataframe(
        df_tourism[available].head(50),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### 📦 Preview Dataset (package_tourism.csv)")
    st.dataframe(df_packages.head(30), use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("""
<div class="footer">
    🗺️ <b>Semantic Tourism Search System</b> · Powered by Streamlit + Pandas<br>
    Dataset: <i>Indonesia Tourism Dataset</i> · Roadmap: RDF · SPARQL · Knowledge Graph
</div>
""", unsafe_allow_html=True)
