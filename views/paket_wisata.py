import streamlit as st
import pandas as pd
from utils.icons import get_hero_style, get_svg_icon
from utils.helpers import category_color, format_price

def render_paket_wisata(df_packages, df_tourism):
    img_style = get_hero_style("public/paket.jpg", bg_position="center bottom")
    st.markdown(f"""
    <div class="hero-banner" style="{img_style} padding:2rem 2.5rem;">
        <div class="hero-title" style="font-size:1.8rem;">{get_svg_icon("package")} Paket Wisata Rekomendasi</div>
        <div class="hero-subtitle">Kumpulan paket perjalanan wisata terkurasi per kota</div>
    </div>
    """, unsafe_allow_html=True)

    if df_packages.empty:
        st.warning("Data paket wisata tidak tersedia.")
        return

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

    place_cols = sorted([c for c in df_packages.columns if c.startswith("Place_Tourism")])

    cols = st.columns(3)
    for i, (_, row) in enumerate(pkg_filtered.iterrows()):
        places = [str(row[c]) for c in place_cols if pd.notna(row[c]) and str(row[c]).strip()]
        places_html = "".join(
            f"<div>▸ {p}</div>" for p in places
        ) if places else "<div style='color:rgba(255,255,255,0.35); font-style:italic;'>Tidak ada detail tempat</div>"

        with cols[i % 3]:
            st.markdown(f"""
            <div class="package-card">
                <div class="package-city">{get_svg_icon("city")} {row['City']}</div>
                <div style="font-size:1rem; font-weight:700; color:#e8f0fa; letter-spacing:-0.2px; margin-bottom:0.2rem;">
                    Paket #{int(row['Package'])}
                </div>
                <div class="package-places">{places_html}</div>
            </div>
            """, unsafe_allow_html=True)

    if selected_city != "Semua Kota" and not df_tourism.empty:
        st.markdown(f"""
        <div class="sec-header">
            <h2>{get_svg_icon("city")} Wisata Populer di Kota Ini</h2>
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
                        <span class="badge badge-category">{get_svg_icon("category")} {row['Category']}</span>
                        <span class="badge badge-rating">{get_svg_icon("rating")} {row['Rating']}</span>
                        <span class="badge badge-price">{get_svg_icon("price")} {format_price(row['Price'])}</span>
                    </div>
                    <p class="card-desc">{row['Description'][:150]}…</p>
                </div>
                """, unsafe_allow_html=True)
