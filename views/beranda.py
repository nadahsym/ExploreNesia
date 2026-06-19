import streamlit as st
from utils.icons import get_hero_style, get_svg_icon
from utils.helpers import category_color, format_price, star_rating

def render_beranda(df_tourism, df_packages):
    img_style = get_hero_style("public/alam.jpg")

    st.markdown(f"""
    <div class="hero-banner" style="{img_style}">
        <div class="hero-title">{get_svg_icon("compass")} Semantic Tourism Search System</div>
        <div class="hero-subtitle">
            Jelajahi 400+ destinasi wisata Indonesia — Jakarta, Yogyakarta,
            Bandung, Semarang, Surabaya
        </div>
    </div>
    """, unsafe_allow_html=True)

    total_places = len(df_tourism)
    total_cities = df_tourism["City"].nunique() if not df_tourism.empty else 0
    total_cats   = df_tourism["Category"].nunique() if not df_tourism.empty else 0
    avg_rating   = df_tourism["Rating"].mean() if not df_tourism.empty else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="stat-card blue">
            <div class="stat-number">{total_places}</div>
            <div class="stat-label">{get_svg_icon("city")} Total Wisata</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card green">
            <div class="stat-number">{total_cities}</div>
            <div class="stat-label">{get_svg_icon("city")} Kota</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card orange">
            <div class="stat-number">{total_cats}</div>
            <div class="stat-label">{get_svg_icon("category")} Kategori</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="stat-card purple">
            <div class="stat-number">{avg_rating:.1f}</div>
            <div class="stat-label">{get_svg_icon("rating")} Rata-rata Rating</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sec-header">
        <h2>{get_svg_icon("search")} Pencarian Cepat</h2>
        <div class="sec-line"></div>
    </div>
    """, unsafe_allow_html=True)

    quick_q = st.text_input(
        "Cari tempat wisata…",
        placeholder="Contoh: Borobudur, pantai, museum…",
        label_visibility="collapsed",
    )
    if quick_q and not df_tourism.empty:
        mask = df_tourism["Place_Name"].str.contains(quick_q, case=False, na=False)
        results = df_tourism[mask].head(6)
        if results.empty:
            st.info("Tidak ada hasil. Coba kata kunci lain.")
        else:
            cols = st.columns(3)
            for i, (_, row) in enumerate(results.iterrows()):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="tourism-card" style="border-color:{category_color(row['Category'])};">
                        <div class="card-title">{row['Place_Name']}</div>
                        <div class="card-meta">
                            <span class="badge badge-city">{get_svg_icon("city")} {row['City']}</span>
                            <span class="badge badge-category">{get_svg_icon("category")} {row['Category']}</span>
                            <span class="badge badge-rating">{get_svg_icon("rating")} {row['Rating']}</span>
                            <span class="badge badge-price">{get_svg_icon("price")} {format_price(row['Price'])}</span>
                        </div>
                        <p class="card-desc">{row['Description']}</p>
                    </div>
                    """, unsafe_allow_html=True)

    CATEGORY_ICON_COLORS = {
        "Budaya":               "#ff6b6b",
        "Taman Hiburan":        "#ffd93d",
        "Cagar Alam":           "#6bcb77",
        "Bahari":               "#4d96ff",
        "Pusat Perbelanjaan":   "#c77dff",
        "Tempat Ibadah":        "#ff9f1c",
    }

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.85rem; font-weight:700; color:var(--text-primary); margin-bottom:0.5rem;">{get_svg_icon("info")} Legenda Kategori</div>', unsafe_allow_html=True)
    leg_cols = st.columns(len(CATEGORY_ICON_COLORS))
    for i, (cat_name, cat_color) in enumerate(CATEGORY_ICON_COLORS.items()):
        with leg_cols[i]:
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:6px;font-size:0.78rem;color:var(--text-secondary);'>"
                f"<span style='width:12px;height:12px;border-radius:50%;background:{cat_color};display:inline-block;flex-shrink:0;'></span>"
                f"{cat_name}</div>",
                unsafe_allow_html=True,
            )
    
    st.markdown(f"""
    <div class="sec-header">
        <h2>{get_svg_icon("rating")} Wisata Unggulan</h2>
        <div class="sec-line"></div>
    </div>
    """, unsafe_allow_html=True)

    if not df_tourism.empty:
        top_places = df_tourism.nlargest(6, "Rating")
        cols = st.columns(3)
        for i, (_, row) in enumerate(top_places.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="tourism-card" style="border-color:{category_color(row['Category'])};">
                    <div class="card-title">{row['Place_Name']}</div>
                    <div class="card-meta">
                        <span class="badge badge-city">{get_svg_icon("city")} {row['City']}</span>
                        <span class="badge badge-category">{get_svg_icon("category")} {row['Category']}</span>
                        <span class="badge badge-rating">{get_svg_icon("rating")} {row['Rating']} {star_rating(row['Rating'])}</span>
                        <span class="badge badge-price">{get_svg_icon("price")} {format_price(row['Price'])}</span>
                    </div>
                    <p class="card-desc">{row['Description']}</p>
                </div>
                """, unsafe_allow_html=True)
