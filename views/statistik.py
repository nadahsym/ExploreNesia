import streamlit as st
from utils.icons import get_hero_style, get_svg_icon

def render_statistik(df_tourism, df_packages):
    img_style = get_hero_style("public/statistik.png", bg_position="center top", overlay_opacity=0.45)
    st.markdown(f"""
    <div class="hero-banner" style="{img_style} padding:2rem 2.5rem;">
        <div class="hero-title" style="font-size:1.8rem;">{get_svg_icon("stats")} Statistik Dataset</div>
        <div class="hero-subtitle">Gambaran umum dataset wisata Indonesia</div>
    </div>
    """, unsafe_allow_html=True)

    if df_tourism.empty:
        st.warning("Data wisata tidak tersedia.")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="stat-card blue">
            <div class="stat-number">{len(df_tourism)}</div>
            <div class="stat-label">{get_svg_icon("city")} Total Wisata</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card green">
            <div class="stat-number">{df_tourism['City'].nunique()}</div>
            <div class="stat-label">{get_svg_icon("city")} Jumlah Kota</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card orange">
            <div class="stat-number">{df_tourism['Category'].nunique()}</div>
            <div class="stat-label">{get_svg_icon("category")} Kategori</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="stat-card purple">
            <div class="stat-number">{len(df_packages)}</div>
            <div class="stat-label">{get_svg_icon("package")} Paket Wisata</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(f"#### {get_svg_icon('city', 'svg-icon inline-icon')} Wisata per Kota", unsafe_allow_html=True)
        city_counts = df_tourism["City"].value_counts().reset_index()
        city_counts.columns = ["Kota", "Jumlah Wisata"]
        st.bar_chart(city_counts.set_index("Kota"))

        st.dataframe(
            city_counts,
            use_container_width=True,
            hide_index=True,
        )

    with col_right:
        st.markdown(f"#### {get_svg_icon('category', 'svg-icon inline-icon')} Wisata per Kategori", unsafe_allow_html=True)
        cat_counts = df_tourism["Category"].value_counts().reset_index()
        cat_counts.columns = ["Kategori", "Jumlah Wisata"]
        st.bar_chart(cat_counts.set_index("Kategori"))

        st.dataframe(
            cat_counts,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown(f"#### {get_svg_icon('rating', 'svg-icon inline-icon')} Distribusi Rating", unsafe_allow_html=True)
    rating_dist = df_tourism["Rating"].value_counts().sort_index()
    st.bar_chart(rating_dist)

    st.markdown(f"#### {get_svg_icon('info', 'svg-icon inline-icon')} Data Tempat Wisata (dari tourism_ontology.ttl)", unsafe_allow_html=True)
    display_cols = ["Place_Id", "Place_Name", "City", "Category", "Rating", "Price", "Description"]
    available = [c for c in display_cols if c in df_tourism.columns]
    st.dataframe(
        df_tourism[available].head(50),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(f"#### {get_svg_icon('package', 'svg-icon inline-icon')} Data Paket Wisata (dari tourism_ontology.ttl)", unsafe_allow_html=True)
    st.dataframe(df_packages.head(30), use_container_width=True, hide_index=True)
