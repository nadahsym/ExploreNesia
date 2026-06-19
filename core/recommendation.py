import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.icons import get_svg_icon

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

@st.dialog("Rekomendasi Wisata Serupa")
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
            st.markdown(f"""
            <div style="font-size:0.9rem; font-weight:600; color:var(--text-secondary); margin-bottom:0.5rem; display:flex; align-items:center; gap:12px;">
                <span style="display:flex; align-items:center; gap:4px;">{get_svg_icon("city")} {row['City']}</span>
                <span style="display:flex; align-items:center; gap:4px;">{get_svg_icon("category")} {row['Category']}</span>
                <span style="display:flex; align-items:center; gap:4px;">{get_svg_icon("rating")} {row['Rating']}</span>
            </div>
            """, unsafe_allow_html=True)
            st.caption(row['Description'][:150] + "...")
            st.divider() # Garis pemisah antar rekomendasi
