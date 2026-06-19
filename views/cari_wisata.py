import streamlit as st
import math
from utils.icons import get_hero_style, get_svg_icon
from utils.helpers import category_color, format_price
from core.data_loader import get_sparql_tourism
from core.recommendation import show_recommendation_dialog

def render_cari_wisata(_g_shared, all_cities, all_categories, min_r, max_r):
    img_style = get_hero_style("public/cari.jpg")
    st.markdown(f"""
    <div class="hero-banner" style="{img_style} padding:2rem 2.5rem;">
        <div class="hero-title" style="font-size:1.8rem;">{get_svg_icon("search")} Cari Tempat Wisata</div>
        <div class="hero-subtitle">Temukan destinasi liburan terbaik di Indonesia menggunakan pencarian cerdas berbasis Semantic Web</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{get_svg_icon("info")} Filter Pencarian Semantic</div>', unsafe_allow_html=True)

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

    # ── Ambil Data dari Semantic Web (Fuseki → rdflib fallback) ──
    with st.spinner("Mengambil data dari Semantic Web (TTL / Fuseki)..."):
        filtered = get_sparql_tourism(search_q, filter_city, filter_cat, filter_rating, _g=_g_shared)

    if not filtered.empty:
        # Sort by rating descending by default
        filtered = filtered.sort_values("Rating", ascending=False).reset_index(drop=True)

        CARDS_PER_PAGE = 12
        total_pages = max(1, math.ceil(len(filtered) / CARDS_PER_PAGE))
        
        if "cari_page" not in st.session_state:
            st.session_state["cari_page"] = 1
            
        if st.session_state["cari_page"] > total_pages:
            st.session_state["cari_page"] = 1
            
        page_num = st.session_state["cari_page"]

        col_res, col_sort, col_prev, col_page, col_next = st.columns([3.5, 2, 0.5, 0.8, 0.5])
        with col_res:
            st.markdown(
                f"<p style='color:var(--text-secondary); font-size:0.9rem; margin:0.5rem 0;'>"
                f"Menampilkan <b>{len(filtered)}</b> tempat wisata</p>",
                unsafe_allow_html=True,
            )
        with col_sort:
            sort_by = st.selectbox(
                "Urutkan",
                ["Rating Tertinggi", "Harga Terendah", "Harga Tertinggi", "A-Z"],
                label_visibility="collapsed",
            )
        with col_prev:
            if st.button(" ", icon=":material/chevron_left:", key="top_prev", use_container_width=True, disabled=(page_num == 1)):
                st.session_state["cari_page"] = page_num - 1
                st.rerun()
        with col_page:
            st.markdown(f"<div style='text-align:center; padding-top:6px; font-size:0.85rem; font-weight:700; color:var(--text-secondary);'>{page_num} / {total_pages}</div>", unsafe_allow_html=True)
        with col_next:
            if st.button(" ", icon=":material/chevron_right:", key="top_next", use_container_width=True, disabled=(page_num == total_pages)):
                st.session_state["cari_page"] = page_num + 1
                st.rerun()

        if sort_by == "Rating Tertinggi":
            filtered = filtered.sort_values("Rating", ascending=False)
        elif sort_by == "Harga Terendah":
            filtered = filtered.sort_values("Price", ascending=True)
        elif sort_by == "Harga Tertinggi":
            filtered = filtered.sort_values("Price", ascending=False)
        elif sort_by == "A-Z":
            filtered = filtered.sort_values("Place_Name", ascending=True)
        
        start_idx = (page_num - 1) * CARDS_PER_PAGE
        page_data = filtered.iloc[start_idx : start_idx + CARDS_PER_PAGE]

        if page_data.empty:
            st.markdown(f"""
            <div class="empty-state">
                <div class="icon">{get_svg_icon("telescope")}</div>
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
                            <span class="badge badge-city">{get_svg_icon("city")} {row['City']}</span>
                            <span class="badge badge-category">{get_svg_icon("category")} {row['Category']}</span>
                            <span class="badge badge-rating">{get_svg_icon("rating")} {row['Rating']}</span>
                            <span class="badge badge-price">{get_svg_icon("price")} {format_price(row['Price'])}</span>
                        </div>
                        <p class="card-desc">{desc_short}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("Lihat Rekomendasi", key=f"btn_{row['Place_Name']}", use_container_width=True):
                        show_recommendation_dialog(row['Place_Name'], filtered)

            st.markdown("<br><br>", unsafe_allow_html=True)
            if total_pages > 1:
                col_pad1, col_prev, col_info, col_next, col_pad2 = st.columns([2, 1.5, 2, 1.5, 2])
                with col_prev:
                    if st.button("Prev", icon=":material/chevron_left:", use_container_width=True, disabled=(page_num == 1)):
                        st.session_state["cari_page"] = page_num - 1
                        st.rerun()
                with col_info:
                    st.markdown(
                        f"<div style='text-align:center; padding-top:8px; font-weight:600; color:var(--text-primary);'>"
                        f"Halaman {page_num} dari {total_pages} <br>"
                        f"<span style='font-size:0.8em; font-weight:400; color:var(--text-secondary);'>Total {len(filtered)} wisata</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                with col_next:
                    if st.button("Next", icon=":material/chevron_right:", use_container_width=True, disabled=(page_num == total_pages)):
                        st.session_state["cari_page"] = page_num + 1
                        st.rerun()
            else:
                st.markdown(
                    f"<div style='text-align:center; margin-top:2rem; font-size:0.9rem; color:var(--text-secondary);'>"
                    f"Menampilkan semua {len(filtered)} wisata"
                    f"</div>",
                    unsafe_allow_html=True
                )
    else:
        st.markdown(f"""
        <div class="empty-state">
            <div class="icon">{get_svg_icon("telescope")}</div>
            <p>Tidak ada data ditemukan yang sesuai filter. Coba ubah kriteria pencarian.</p>
        </div>
        """, unsafe_allow_html=True)
