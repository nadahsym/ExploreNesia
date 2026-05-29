"""
Semantic Tourism Search System
================================
Aplikasi pencarian wisata Indonesia berbasis Semantic Web
menggunakan Streamlit + Pandas + SPARQL.
"""

import streamlit as st
import pandas as pd
import math
from SPARQLWrapper import SPARQLWrapper, JSON
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ──────────────────────────────────────────────
# SPARQL ENDPOINT
# ──────────────────────────────────────────────
# Pastikan Apache Jena Fuseki kamu berjalan di port 3030 dan nama datasetnya "tourism"
sparql = SPARQLWrapper("http://localhost:3030/tourism/query")

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
# CUSTOM CSS — Dark/Light Mode Compatible UI
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── CSS Variables: Light Mode ── */
:root {
    --bg-primary:        #f4f6fb;
    --bg-surface:        #ffffff;
    --bg-surface-hover:  #f8faff;
    --bg-subtle:         #eef1f8;
    --border-color:      #e2e8f4;
    --text-primary:      #0f1b2d;
    --text-secondary:    #4a5568;
    --text-muted:        #8896ab;
    --accent-blue:       #3a86ff;
    --accent-green:      #06d6a0;
    --accent-orange:     #ffb703;
    --accent-purple:     #7c3aed;
    --shadow-sm:         0 1px 4px rgba(15,27,45,0.06), 0 2px 12px rgba(15,27,45,0.05);
    --shadow-md:         0 4px 16px rgba(15,27,45,0.10), 0 1px 4px rgba(15,27,45,0.06);
    --shadow-hover:      0 8px 28px rgba(58,134,255,0.16), 0 2px 8px rgba(15,27,45,0.08);
    --badge-city-bg:     #dbeafe;
    --badge-city-fg:     #1d4ed8;
    --badge-cat-bg:      #fef3c7;
    --badge-cat-fg:      #92400e;
    --badge-rating-bg:   #d1fae5;
    --badge-rating-fg:   #065f46;
    --badge-price-bg:    #fce7f3;
    --badge-price-fg:    #9d174d;
}

/* ── CSS Variables: Dark Mode ── */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary:        #0d1117;
        --bg-surface:        #161b27;
        --bg-surface-hover:  #1e2535;
        --bg-subtle:         #1a2030;
        --border-color:      #2a3349;
        --text-primary:      #e8edf5;
        --text-secondary:    #94a3c0;
        --text-muted:        #5a6a85;
        --shadow-sm:         0 1px 4px rgba(0,0,0,0.3), 0 2px 12px rgba(0,0,0,0.2);
        --shadow-md:         0 4px 16px rgba(0,0,0,0.4), 0 1px 4px rgba(0,0,0,0.25);
        --shadow-hover:      0 8px 28px rgba(58,134,255,0.25), 0 2px 8px rgba(0,0,0,0.3);
        --badge-city-bg:     #1e3a5f;
        --badge-city-fg:     #93c5fd;
        --badge-cat-bg:      #3d2e0a;
        --badge-cat-fg:      #fcd34d;
        --badge-rating-bg:   #052e16;
        --badge-rating-fg:   #6ee7b7;
        --badge-price-bg:    #3b0764;
        --badge-price-fg:    #e879f9;
    }
}

/* ── Streamlit Dark Mode Override ── */
[data-theme="dark"] {
    --bg-primary:        #0d1117;
    --bg-surface:        #161b27;
    --bg-surface-hover:  #1e2535;
    --bg-subtle:         #1a2030;
    --border-color:      #2a3349;
    --text-primary:      #e8edf5;
    --text-secondary:    #94a3c0;
    --text-muted:        #5a6a85;
    --shadow-sm:         0 1px 4px rgba(0,0,0,0.3), 0 2px 12px rgba(0,0,0,0.2);
    --shadow-md:         0 4px 16px rgba(0,0,0,0.4), 0 1px 4px rgba(0,0,0,0.25);
    --shadow-hover:      0 8px 28px rgba(58,134,255,0.25), 0 2px 8px rgba(0,0,0,0.3);
    --badge-city-bg:     #1e3a5f;
    --badge-city-fg:     #93c5fd;
    --badge-cat-bg:      #3d2e0a;
    --badge-cat-fg:      #fcd34d;
    --badge-rating-bg:   #052e16;
    --badge-rating-fg:   #6ee7b7;
    --badge-price-bg:    #3b0764;
    --badge-price-fg:    #e879f9;
}

/* ── Global ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: var(--bg-primary) !important;
}

[data-testid="stAppViewContainer"] > .main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f1b2d !important;
    border-right: 1px solid rgba(58,134,255,0.15) !important;
}
[data-testid="stSidebar"] * {
    color: #c8d6e8 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #c8d6e8 !important;
    font-size: 0.92rem;
    font-weight: 500;
}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-top: 1.2rem;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.08) !important;
}

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, #0f3460 0%, #1a2744 45%, #0d6e72 100%);
    border-radius: 20px;
    padding: 2.8rem 2.8rem 2.4rem;
    margin-bottom: 2rem;
    box-shadow: 0 8px 40px rgba(0,0,0,0.25), 0 2px 8px rgba(0,0,0,0.15);
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.07);
}
.hero-banner::before {
    content: "🇮🇩";
    position: absolute;
    right: 2.5rem;
    top: 1.5rem;
    font-size: 5.5rem;
    opacity: 0.10;
    pointer-events: none;
}
.hero-banner::after {
    content: "";
    position: absolute;
    top: -40px;
    right: -40px;
    width: 220px;
    height: 220px;
    background: radial-gradient(circle, rgba(58,134,255,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    color: #ffffff;
    font-size: 2.3rem;
    font-weight: 800;
    margin: 0 0 0.5rem;
    letter-spacing: -0.5px;
    line-height: 1.2;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.hero-subtitle {
    color: #a8d0ec;
    font-size: 1rem;
    margin: 0 0 1rem;
    font-weight: 400;
    line-height: 1.5;
    max-width: 560px;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(58,134,255,0.18);
    border: 1px solid rgba(58,134,255,0.35);
    color: #a8d0ec;
    font-size: 0.75rem;
    padding: 5px 14px;
    border-radius: 100px;
    letter-spacing: 0.4px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 0.25rem;
}

/* ── Stat Cards ── */
.stat-card {
    background: var(--bg-surface);
    border-radius: 16px;
    padding: 1.3rem 1.6rem;
    box-shadow: var(--shadow-sm);
    border-left: 3px solid;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border-top: 1px solid var(--border-color);
    border-right: 1px solid var(--border-color);
    border-bottom: 1px solid var(--border-color);
}
.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
}
.stat-card.blue   { border-left-color: #3a86ff; }
.stat-card.green  { border-left-color: #06d6a0; }
.stat-card.orange { border-left-color: #ffb703; }
.stat-card.purple { border-left-color: #7c3aed; }
.stat-number {
    font-size: 2rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1;
    letter-spacing: -1px;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.stat-label {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-top: 5px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    font-weight: 600;
}

/* ── Search Section ── */
.search-section {
    background: var(--bg-surface);
    border-radius: 18px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
}
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    letter-spacing: -0.2px;
}

/* ── Tourism Card ── */
.tourism-card {
    background: var(--bg-surface);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
    border-top: 3px solid #3a86ff;
    transition: box-shadow 0.25s ease, transform 0.25s ease, border-color 0.25s ease;
    height: 100%;
    position: relative;
    overflow: hidden;
}
.tourism-card::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(58,134,255,0.03) 0%, transparent 60%);
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.25s;
}
.tourism-card:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-3px);
    border-color: rgba(58,134,255,0.3);
}
.tourism-card:hover::before { opacity: 1; }
.card-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 0.6rem;
    line-height: 1.35;
    letter-spacing: -0.2px;
}
.card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-bottom: 0.75rem;
}
.badge {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-size: 0.7rem;
    padding: 3px 9px;
    border-radius: 100px;
    font-weight: 600;
    letter-spacing: 0.2px;
    white-space: nowrap;
}
.badge-city     { background: var(--badge-city-bg);   color: var(--badge-city-fg); }
.badge-category { background: var(--badge-cat-bg);    color: var(--badge-cat-fg); }
.badge-rating   { background: var(--badge-rating-bg); color: var(--badge-rating-fg); }
.badge-price    { background: var(--badge-price-bg);  color: var(--badge-price-fg); }
.card-desc {
    font-size: 0.82rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* ── Package Card ── */
.package-card {
    background: linear-gradient(145deg, #0f2744 0%, #142038 50%, #0a3d40 100%);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    color: #fff;
    height: 100%;
    box-shadow: var(--shadow-md);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border: 1px solid rgba(255,255,255,0.06);
    position: relative;
    overflow: hidden;
}
.package-card::after {
    content: "";
    position: absolute;
    top: -30px;
    right: -30px;
    width: 120px;
    height: 120px;
    background: radial-gradient(circle, rgba(13,115,119,0.3) 0%, transparent 70%);
    pointer-events: none;
}
.package-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.35);
}
.package-city {
    font-size: 0.7rem;
    color: #7ec8d8;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.4rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}
.package-places {
    font-size: 0.82rem;
    color: #c8dff0;
    margin-top: 0.6rem;
    line-height: 1.7;
}

/* ── Section Headers ── */
.sec-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 2.5rem 0 1.2rem;
}
.sec-header h2 {
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--text-primary);
    margin: 0;
    white-space: nowrap;
    letter-spacing: -0.3px;
}
.sec-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border-color), transparent);
    border-radius: 2px;
}

/* ── Pagination ── */
.page-info {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.82rem;
    margin-top: 1rem;
    font-weight: 500;
    letter-spacing: 0.2px;
}

/* ── Empty State ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--text-muted);
    background: var(--bg-surface);
    border-radius: 18px;
    border: 1px dashed var(--border-color);
    margin-top: 1rem;
}
.empty-state .icon {
    font-size: 3.5rem;
    margin-bottom: 0.5rem;
    display: block;
}
.empty-state p {
    font-size: 0.95rem;
    margin-top: 0.5rem;
    color: var(--text-secondary);
    line-height: 1.6;
    max-width: 400px;
    margin-inline: auto;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.78rem;
    padding: 2rem 0 1.5rem;
    border-top: 1px solid var(--border-color);
    margin-top: 3rem;
    line-height: 1.8;
}

/* ── Result count text ── */
[style*="color:#666"] {
    color: var(--text-secondary) !important;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# DATA LOADING (Tetap dipertahankan untuk opsi dropdown & beranda)
# ──────────────────────────────────────────────
@st.cache_data
def load_tourism_data(path: str = "data/tourism_with_id.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    unnamed = [c for c in df.columns if c.startswith("Unnamed")]
    df.drop(columns=unnamed, inplace=True, errors="ignore")
    df["Price"] = pd.to_numeric(df.get("Price", 0), errors="coerce").fillna(0).astype(int)
    df["Rating"] = pd.to_numeric(df.get("Rating", 0), errors="coerce").fillna(0.0)
    for col in ["Place_Name", "City", "Category", "Description"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()
    return df

@st.cache_data
def load_package_data(path: str = "data/package_tourism.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def format_price(price: int) -> str:
    if price == 0:
        return "Gratis"
    return f"Rp {price:,.0f}".replace(",", ".")

def star_rating(rating: float) -> str:
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

# ── FUNGSI SPARQL BARU ──
def get_sparql_tourism(search_q="", city="Semua Kota", category="Semua Kategori", min_rating=0.0):
    query = """
    PREFIX : <http://www.semanticweb.org/tourism-ontology#>
    
    SELECT ?placeName ?cityName ?categoryName ?price ?rating ?desc
    WHERE {
        ?place a :TouristPlace ;
               :hasName ?placeName ;
               :locatedIn ?cityNode ;
               :hasCategory ?categoryNode ;
               :hasPrice ?price ;
               :hasRating ?rating ;
               :hasDescription ?desc .
               
        ?cityNode :hasName ?cityName .
        ?categoryNode :hasName ?categoryName .
    """
    
    if city != "Semua Kota":
        query += f'\n        FILTER(str(?cityName) = "{city}")'
    if category != "Semua Kategori":
        query += f'\n        FILTER(str(?categoryName) = "{category}")'
    
    query += f'\n        FILTER(?rating >= {min_rating})'
    
    if search_q:
        query += f'\n        FILTER(regex(str(?placeName), "{search_q}", "i"))'
        
    query += "\n    }"
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    try:
        results = sparql.query().convert()
    except Exception as e:
        st.error(f"Gagal terhubung ke SPARQL Endpoint. Pastikan Apache Jena Fuseki berjalan di port 3030. Error: {e}")
        return pd.DataFrame()
    
    data = []
    for r in results["results"]["bindings"]:
        data.append({
            "Place_Name": r["placeName"]["value"],
            "City": r["cityName"]["value"],
            "Category": r["categoryName"]["value"],
            "Price": int(float(r["price"]["value"])),
            "Rating": float(r["rating"]["value"]),
            "Description": r["desc"]["value"]
        })
        
    return pd.DataFrame(data)

def get_recommendations(target_place_name, df_sparql, top_n=3):
    # Jika data kosong atau tempat tidak ditemukan, kembalikan dataframe kosong
    if df_sparql.empty or target_place_name not in df_sparql['Place_Name'].values:
        return pd.DataFrame()

    # 1. Gabungkan fitur teks yang akan dianalisis oleh AI
    # Kita menggabungkan Kategori, Kota, dan Deskripsi menjadi satu kalimat panjang
    df_sparql['AI_Features'] = df_sparql['Category'] + " " + df_sparql['City'] + " " + df_sparql['Description']

    # 2. Ubah teks menjadi representasi angka (vektor) menggunakan TF-IDF
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df_sparql['AI_Features'])

    # 3. Hitung skor kemiripan (Cosine Similarity) antar semua tempat wisata
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # 4. Cari index dari tempat wisata yang sedang dipilih user
    idx = df_sparql.index[df_sparql['Place_Name'] == target_place_name].tolist()[0]

    # 5. Ambil skor kemiripan tempat tersebut dengan tempat lainnya
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Urutkan dari skor yang paling tinggi ke rendah
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Ambil top N (kita lewati index ke-0 karena itu adalah tempat itu sendiri yang pasti skornya 100%)
    sim_scores = sim_scores[1:top_n+1]
    
    # Dapatkan index tempat-tempat hasil rekomendasi
    place_indices = [i[0] for i in sim_scores]

    # Kembalikan baris data tempat wisata yang direkomendasikan
    return df_sparql.iloc[place_indices]

@st.dialog("💡 Rekomendasi Wisata Serupa")
def show_recommendation_dialog(place_name, df_sparql):
    st.markdown(f"Tempat yang mirip dengan **{place_name}**:")
    
    with st.spinner("Menganalisis kemiripan konten..."):
        # Panggil fungsi AI kita
        rekomendasi = get_recommendations(place_name, df_sparql, top_n=3)
        
    if rekomendasi.empty:
        st.info("Maaf, belum ada rekomendasi yang cukup mirip.")
    else:
        # Tampilkan hasil rekomendasi dengan gaya yang rapi
        for _, row in rekomendasi.iterrows():
            st.markdown(f"### {row['Place_Name']}")
            st.markdown(f"**📍 {row['City']} | 🎭 {row['Category']} | ⭐ {row['Rating']}**")
            st.caption(row['Description'][:150] + "...")
            st.divider() # Garis pemisah antar rekomendasi

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
    st.markdown(
        "<div style='font-size:0.75rem; color:rgba(200,214,232,0.45); text-align:center; font-family:JetBrains Mono,monospace;'>"
        "v1.1 · Semantic Web Project"
        "</div>",
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────
# LOAD DATA AWAL (Untuk Dropdown UI)
# ──────────────────────────────────────────────
with st.spinner("Memuat sumber daya awal…"):
    df_tourism  = load_tourism_data()
    df_packages = load_package_data()

all_cities      = sorted(df_tourism["City"].unique().tolist())
all_categories  = sorted(df_tourism["Category"].unique().tolist())
min_r, max_r    = float(df_tourism["Rating"].min()), float(df_tourism["Rating"].max())

# ══════════════════════════════════════════════
# PAGE: BERANDA
# ══════════════════════════════════════════════
if page == "🏠  Beranda":

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
# PAGE: CARI WISATA (SUDAH MENGGUNAKAN SPARQL)
# ══════════════════════════════════════════════
elif page == "🔍  Cari Wisata":

    st.markdown("""
    <div class="hero-banner" style="padding:2rem 2.5rem;">
        <div class="hero-title" style="font-size:1.8rem;">🔍 Cari Tempat Wisata (SPARQL Enabled)</div>
        <div class="hero-subtitle">Menarik data langsung dari Knowledge Graph melalui Apache Jena Fuseki</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚙️ Filter Pencarian Semantic</div>', unsafe_allow_html=True)

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

    # ── Ambil Data dari SPARQL Endpoint ──
    with st.spinner("Mengambil data dari Semantic Web (Fuseki)..."):
        filtered = get_sparql_tourism(search_q, filter_city, filter_cat, filter_rating)

    if not filtered.empty:
        # Sort by rating descending by default
        filtered = filtered.sort_values("Rating", ascending=False).reset_index(drop=True)

        col_res, col_sort = st.columns([5, 2])
        with col_res:
            st.markdown(
                f"<p style='color:var(--text-secondary); font-size:0.9rem; margin:0.5rem 0;'>"
                f"Menampilkan <b>{len(filtered)}</b> tempat wisata dari Ontology</p>",
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

                    if st.button("💡 Lihat Rekomendasi", key=f"btn_{row['Place_Name']}", use_container_width=True):
                        show_recommendation_dialog(row['Place_Name'], filtered)

            st.markdown(
                f"<div class='page-info'>Halaman {page_num} dari {total_pages} "
                f"· {len(filtered)} hasil total</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">🔌</div>
            <p>Tidak ada data ditemukan. Pastikan Apache Jena Fuseki menyala dan dataset 'tourism' sudah berisi data dari .ttl!</p>
        </div>
        """, unsafe_allow_html=True)

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

    pkg_cities = sorted(df_packages["City"].unique().tolist())
    selected_city = st.selectbox("Filter Kota Paket", ["Semua Kota"] + pkg_cities)

    pkg_filtered = df_packages.copy()
    if selected_city != "Semua Kota":
        pkg_filtered = pkg_filtered[pkg_filtered["City"] == selected_city]

    st.markdown(
        f"<p style='color:var(--text-secondary); font-size:0.9rem; margin:0.5rem 0 1.2rem;'>"
        f"Menampilkan <b>{len(pkg_filtered)}</b> paket wisata</p>",
        unsafe_allow_html=True,
    )

    place_cols = [c for c in df_packages.columns if c.startswith("Place_Tourism")]

    cols = st.columns(3)
    for i, (_, row) in enumerate(pkg_filtered.iterrows()):
        places = [str(row[c]) for c in place_cols if pd.notna(row[c]) and str(row[c]).strip()]
        places_html = "".join(
            f"<div>▸ {p}</div>" for p in places
        ) if places else "<div style='color:rgba(255,255,255,0.35); font-style:italic;'>Tidak ada detail tempat</div>"

        with cols[i % 3]:
            st.markdown(f"""
            <div class="package-card">
                <div class="package-city">📍 {row['City']}</div>
                <div style="font-size:1rem; font-weight:700; color:#e8f0fa; letter-spacing:-0.2px; margin-bottom:0.2rem;">
                    Paket #{int(row['Package'])}
                </div>
                <div class="package-places">{places_html}</div>
            </div>
            """, unsafe_allow_html=True)

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

    st.markdown("#### ⭐ Distribusi Rating")
    rating_dist = df_tourism["Rating"].value_counts().sort_index()
    st.bar_chart(rating_dist)

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
    🗺️ <b>Semantic Tourism Search System</b> · Powered by Streamlit, SPARQL, and Pandas<br>
    Dataset: <i>Indonesia Tourism Dataset</i> · Roadmap: RDF · SPARQL · Knowledge Graph
</div>
""", unsafe_allow_html=True)